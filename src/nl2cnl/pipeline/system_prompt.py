from abc import ABC, abstractmethod
from pathlib import Path


# I don't yet know how this will look in the future
# It is likely going to change
class SystemPromptStrategy(ABC):
    @abstractmethod
    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        pass

    @abstractmethod
    def get_system_prompt(self, user_prompt: str) -> str:
        pass

# Gives the LLM the raw grammar specification file
class RawStrategy(SystemPromptStrategy):
    def __init__(self):
        self.specification = ""

    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        with open(grammar_path, "r") as file:
            self.specification = file.read()
            
        self.examples = ""
        if examples_path is not None:
            with open(examples_path, "r") as file:
                self.examples = file.read()


    def get_system_prompt(self, user_prompt: str) -> str:
        return f"""You are an expert NL2CNL translator.

        Your task is to translate natural language input into a
        Controlled Natural Language (CNL) that strictly conforms
        to the provided YAML grammar specification.

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

        {self.examples}

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
    pass

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