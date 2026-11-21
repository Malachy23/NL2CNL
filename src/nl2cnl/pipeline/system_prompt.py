from abc import ABC, abstractmethod
from pathlib import Path
from json import load


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
        formatted_examples = ""

        for example in examples:
            formatted_examples += f"Input: {example["nl_input"]}\nOutput: {example["cnl_output"]}\n\n"

        return formatted_examples

# Gives the LLM the raw grammar specification file
class RawStrategy(SystemPromptStrategy):
    def __init__(self):
        self.specification = ""
        super().__init__()

    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        self.specification = grammar_path.read_text() # TODO: Move file open logic somewhere else

        if examples_path is not None:
            self._load_examples(examples_path)


    def get_system_prompt(self, user_prompt: str) -> str:
        return f"""You are an expert NL2CNL translator.
        Your task is to translate natural language input into a Controlled Natural Language (CNL) that strictly conforms to the provided YAML grammar specification.

        GRAMMAR INTERPRETATION AND APPLICATION

        1. Always begin derivation from the root rule named `start`.
        2. Expand production rules recursively until all symbols
        are terminal tokens or lexical placeholders.
        3. Strings enclosed in double quotes represent mandatory
        literal tokens and must be reproduced exactly.
        4. YAML lists and pipe-separated expressions represent
        alternative production branches.
        5. Select the branch that best preserves the semantic
        meaning of the input while satisfying the grammar.
        6. Replace lexical placeholders with corresponding values
        extracted from the input.
        7. Infer only the minimum information strictly necessary
        to satisfy required grammatical slots.
        8. Preserve the original meaning and do not invent
        entities, identifiers, values, or relationships.

        {self._format_examples(self.examples)}

        OUTPUT REQUIREMENTS

        - Output exactly one valid CNL sentence.
        - The output must be derivable from the `start` rule.
        - Preserve the semantic intent of the original input.
        - Do not include explanations, reasoning, parse trees,
        markdown, or quotation marks.
        - Output only the final CNL sentence.

        YAML GRAMMAR SPECIFICATION:
        {self.specification}
        """


class ExampleRetrievalStrategy(SystemPromptStrategy):
    def __init__(self):
        self.specification = ""

    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
            with open(grammar_path, "r") as file:
                self.specification = file.read()

    
    def get_system_prompt(self, user_prompt: str) -> str:
        return ""

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