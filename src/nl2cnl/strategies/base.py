from abc import ABC, abstractmethod
from json import load
from pathlib import Path


# I don't yet know how this will look in the future
# It is likely going to change
class SystemPromptStrategy(ABC):
    def __init__(self):
        self.examples: list[dict[str, str]] = [] # Format [{"nl_input": "...", "cnl_output": "..."}, ...]

    @abstractmethod
    def setup(self, grammar_path: Path, examples_path: Path | None) -> None:
        """Used to give the strategy the grammar specification and examples path.
        This should be run before self.get_system_prompt()
        """

    @abstractmethod
    def get_system_prompt(self, user_prompt: str) -> str:
        """Used to get the system prompt. The user_prompt is required in most strategies"""

    # TODO: This should be somewhere else
    def _load_examples(self, examples_path: Path):
        with open(examples_path, "r", encoding="utf-8") as f:
            data = load(f)
            self.examples = data["examples"] if isinstance(data, dict) else data

    def _format_examples(self, examples: list[dict[str, str]]) -> str:
        """Converts examples' dict format into printable string of the type
            Input: example[nl_input]
            Output: example[cnl_output]
        """
        if not examples:
            return ""

        blocks = [
            f"Input: {ex['nl_input']}\nOutput: {ex['cnl_output']}"
            for ex in reversed(examples)
        ]
        return "EXAMPLES:\n\n" + "\n\n".join(blocks) + "\n"