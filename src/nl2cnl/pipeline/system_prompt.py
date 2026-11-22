from abc import ABC, abstractmethod
from json import load
from pathlib import Path

from numpy import argsort

from nl2cnl.templates import EXAMPLE_RETRIEVAL_SYSTEM_PROMPT, RAW_SYSTEM_PROMPT


# I don't yet know how this will look in the future
# It is likely going to change
class SystemPromptStrategy(ABC):
    def __init__(self):
        # Format [{"nl_input": "...", "cnl_output": "..."}, ...]
        self.examples: list[dict[str, str]] = []

    @abstractmethod
    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        pass

    @abstractmethod
    def get_system_prompt(self, user_prompt: str) -> str:
        pass

    # TODO: This should be somewhere else
    def _load_examples(self, examples_path: Path):
        with open(examples_path, "r", encoding="utf-8") as f:
            data = load(f)
            self.examples = data["examples"] if isinstance(data, dict) else data

    # Converts examples' dict format into printable string of the type
    # Input: example[nl_input]
    # Output: example[cnl_output]
    def _format_examples(self, examples: list[dict[str, str]]) -> str:
        if not examples:
            return ""

        blocks = [
            f"Input: {ex['nl_input']}\nOutput: {ex['cnl_output']}"
            for ex in reversed(examples)
        ]
        return "EXAMPLES:\n\n" + "\n\n".join(blocks) + "\n"

# Gives the LLM the raw grammar specification file
class RawStrategy(SystemPromptStrategy):
    def __init__(self):
        self.specification = ""
        super().__init__()

    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        self.specification = grammar_path.read_text() # TODO: Move file open logic somewhere else

        if examples_path is not None:
            self._load_examples(examples_path)


    # It doesn't use user_prompt
    def get_system_prompt(self, user_prompt: str) -> str:
        return RAW_SYSTEM_PROMPT.format(
            examples=self._format_examples(self.examples),
            specification=self.specification
        )


class ExampleRetrievalStrategy(SystemPromptStrategy):
    def __init__(self):
        # Lazy loadings
        from sentence_transformers import SentenceTransformer
        from transformers.utils import logging

        super().__init__()
        self.specification = ""

        logging.disable_progress_bar() # Hides progress bar, which ruined CliUI aesthetic

        name = "paraphrase-multilingual-MiniLM-L12-v2"
        try:
            self.embedding_model = SentenceTransformer(name, device="cpu", local_files_only=True)
        except OSError:  # Downloads it if not previously installed
            self.embedding_model = SentenceTransformer(name, device="cpu")

    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        self.specification = grammar_path.read_text()

        if examples_path is None:
            return
        
        self._load_examples(examples_path)

        # Create embeddings for examples
        self.examples_embedding = self.embedding_model.encode(
            [example["nl_input"] for example in self.examples],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    
    # TODO: Maybe it's better to 
    def get_system_prompt(self, user_prompt: str) -> str:
        user_prompt_embedding = self.embedding_model.encode(user_prompt, normalize_embeddings=True)
        
        scores = self.examples_embedding @ user_prompt_embedding
        
        top_k = 10 #int( len(self.examples) / 3 ) # Takes a third of the example dataset size as K
        # TODO: Check if this is appropriate
        
        best_idx = argsort(scores)[::-1][:top_k]

        chosen_examples = [self.examples[idx] for idx in best_idx]


        return RAW_SYSTEM_PROMPT.format(
            specification=self.specification,
            examples=self._format_examples(chosen_examples)
        )

class SubgrammarRetrievalStrategy(SystemPromptStrategy):
    pass

# Returns the strategy choosen by CLI (default: raw)
def get_strategy(signature: str) -> SystemPromptStrategy:
    strategies = {
        "raw": RawStrategy,
        "example": ExampleRetrievalStrategy,
        "subgrammar": SubgrammarRetrievalStrategy
        # To be added...
    } 

    return strategies[signature]()