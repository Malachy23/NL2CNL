from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from nl2cnl.loaders import load_examples, load_text

type Example = dict[str, str]  # {"nl_input": "...", "cnl_output": "..."}


@dataclass(frozen=True, slots=True)
class StrategyOptions:
    """Settings shared by all strategies. Each strategy reads only the ones it needs."""
    top_k: int = 10  # Number of examples retrieved by "example"


class SystemPromptStrategy(ABC):
    def __init__(self, options: StrategyOptions):
        self.options = options
        self.specification = ""
        self.examples: list[Example] = []

    @abstractmethod
    def _load_specification(self, specification_path: Path) -> None:
        self.specification = load_text(specification_path)

    @abstractmethod
    def _load_examples(self, examples_path: Path) -> None:
        self.examples = load_examples(examples_path)

    @abstractmethod
    def setup(self, specification_path: Path, examples_path: Path | None) -> None:
        """Gives the strategy the grammar specification and the examples (already loaded).
        Must be called before get_system_prompt().
        """
        self._load_specification(specification_path)
        if examples_path is not None:
            self._load_examples(examples_path)

    @abstractmethod
    def get_system_prompt(self, user_prompt: str) -> str:
        """Returns the system prompt. Some strategies use user_prompt to adapt it."""

    def _format_examples(self, examples: list[Example]) -> str:
        """Converts examples into a printable block of the type
            Input: example[nl_input]
            Output: example[cnl_output]
        The order is reversed, so the most relevant example ends up closest to the user prompt.
        """
        if not examples:
            return ""

        blocks = [
            f"Input: {ex['nl_input']}\nOutput: {ex['cnl_output']}"
            for ex in reversed(examples)
        ]
        return "EXAMPLES:\n\n" + "\n\n".join(blocks) + "\n"
