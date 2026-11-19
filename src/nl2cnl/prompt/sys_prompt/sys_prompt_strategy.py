from abc import ABC, abstractmethod

from nl2cnl.file_opener import open_file


# I don't yet know how this will look in the future
# It is likely going to change
class SystemPromptStrategy(ABC):
    @abstractmethod
    def signature(self) -> str:
        pass

    @abstractmethod
    def setup(self, file: str) -> None:
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

# Give the LLM the raw grammar specification file
class RawFileStrategy(SystemPromptStrategy):
    def __init__(self):
        self.specification = ""

    def signature(self) -> str:
        return "raw_file"

    def setup(self, file: str) -> None:
        self.specification = open_file(file)

    def get_system_prompt(self) -> str:
        return f"""You are a formal translator that converts natural language input into a Controlled Natural Language (CNL) strictly conforming to the provided YAML grammar specification.

        How to read and apply the grammar specification:
        1. Root rule: Always start expanding from the `start` rule down to terminal tokens.
        2. Literal tokens: Strings enclosed in double quotes (e.g., `"the"`, `"of the"`, `"?."`) are mandatory keywords or punctuation and MUST appear verbatim in the exact positions specified.
        3. Alternatives: YAML lists (`- ...`) and pipes (`|`) represent mutually exclusive production branches; select the branch that best matches the semantic intent of the input.
        4. Lexical terminals: Placeholders such as `string` or `number` must be instantiated with the corresponding words or values extracted from the user input.
        5. Implicit slot resolution: If a production rule requires multiple adjacent slots (e.g., a classifier/type followed by an identifier/instance) and the user input omits one of them, infer the minimal missing grammatical slot from general linguistic context so that every required token of the rule is satisfied.

        Output constraints:
        - Output ONLY the final valid CNL sentence.
        - Do NOT include explanations, parse trees, markdown formatting, or surrounding quotes.

        Grammar specification:
        {self.specification}
        """