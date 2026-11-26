from pathlib import Path

from numpy import argsort
from sentence_transformers import SentenceTransformer
from transformers.utils import logging

from nl2cnl.prompts import EXAMPLE_RAG_SYSTEM_PROMPT
from nl2cnl.strategies.base import SystemPromptStrategy


class ExampleRAGStrategy(SystemPromptStrategy):
    """This strategy leaves the grammar specification untouched, but produces an embedding of the provided examples
    that are then compared to the user prompt in order to retrieve the most relevant ones to augment the system prompt.
    Providing examples is mandatory to use this strategy.
    """
    def __init__(self):
        super().__init__()
        self.specification = ""

        logging.disable_progress_bar() # Hides progress bar, which ruined CliUI aesthetic

        name = "paraphrase-multilingual-MiniLM-L12-v2"
        try:
            self.embedding_model = SentenceTransformer(name, device="cpu", local_files_only=True)
        except OSError:  # Downloads it if not previously installed
            self.embedding_model = SentenceTransformer(name, device="cpu")

    def setup(self, specification: str, examples: list[dict[str, str]] | None) -> None:
        self.specification = specification

        if examples is None:
            return

        self.examples = examples

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


        return EXAMPLE_RAG_SYSTEM_PROMPT.format(
            specification=self.specification,
            examples=self._format_examples(chosen_examples)
        )