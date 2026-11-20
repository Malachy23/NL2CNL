from abc import ABC, abstractmethod


# I don't yet know how this will look in the future
# It is likely going to change
class SystemPromptStrategy(ABC):
    @abstractmethod
    def setup(self, path: str) -> None:
        pass

    @abstractmethod
    def get_system_prompt(self, user_prompt: str) -> str:
        pass

# Gives the LLM the raw grammar specification file
class RawStrategy(SystemPromptStrategy):
    def __init__(self):
        self.specification = ""

    def setup(self, path: str) -> None:
        with open(path, "r") as file:
            self.specification = file.read()

    def get_system_prompt(self, user_prompt: str) -> str:
        return f"""You are an expert NL2CNL translator. Your task is to translate
        natural language input into a Controlled Natural Language (CNL) that
        strictly conforms to the provided YAML grammar specification.

        GRAMMAR INTERPRETATION AND APPLICATION

        1. Grammar entry point:
        - Always begin derivation from the root rule named `start`.
        - Expand production rules recursively until all symbols are terminal
            tokens or lexical placeholders.

        2. Terminal symbols:
        - Strings enclosed in double quotes (e.g., `"the"`, `"of the"`,
            `"?."`) represent literal terminal tokens.
        - These tokens are mandatory and must appear exactly as specified,
            including capitalization, spacing, and punctuation.

        3. Production alternatives:
        - YAML lists and pipe-separated expressions represent alternative
            production branches.
        - Select the branch that most accurately preserves the semantic
            meaning of the input while satisfying the grammar.

        4. Lexical placeholders:
        - Replace placeholders such as `string`, `number`, or other
            lexical terminals with the corresponding values extracted
            from the input.
        - Preserve entity names, identifiers, numbers, and relevant
            semantic information from the original input.

        5. Missing grammatical information:
        - If a required grammatical slot is omitted from the input,
            infer only the minimum information strictly necessary to
            construct a valid grammatical expression.
        - Prefer grammatically required defaults over speculative
            assumptions.
        - Never invent entities, identifiers, numerical values, or
            semantic relationships.
        - If a required slot cannot be inferred reliably, use the
            most conservative grammatically valid interpretation.

        6. Semantic preservation:
        - Preserve the original intent and meaning of the input.
        - Do not introduce, remove, or modify semantic constraints.
        - Do not add information that is not explicitly stated or
            strictly required by the grammar.

        OUTPUT REQUIREMENTS

        - Output exactly one valid CNL sentence.
        - The output must be derivable from the `start` rule.
        - Every terminal token must conform exactly to the grammar.
        - Do not output explanations, comments, reasoning, parse trees,
        markdown, or surrounding quotation marks.
        - Do not include any text before or after the CNL sentence.

        YAML GRAMMAR SPECIFICATION:
        {self.specification}
        """


# Returns the strategy choosen by CLI (default: raw)
def get_strategy(signature: str) -> SystemPromptStrategy:
    strategies = {
        "raw": RawStrategy
        # To be added...
    } 

    return strategies[signature]()