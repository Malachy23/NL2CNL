from pathlib import Path

from nl2cnl.prompts import IN_CONTEXT_SYSTEM_PROMPT
from nl2cnl.strategies.base import SystemPromptStrategy


class InContextStrategy(SystemPromptStrategy):
    """This strategy simply copy and pastes the content of the grammar specifications and examples
    directly into the system prompt, without processing any of them.
    As such, once both are provided the system prompt remains the same no matter what the user prompt is.
    """
    def __init__(self):
        self.specification = ""
        super().__init__()

    def setup(self, specification: str, examples: list[dict[str, str]] | None) -> None:
        self.specification = specification # TODO: Move file open logic somewhere else
        if examples is not None:
            self.examples = examples


    def get_system_prompt(self, user_prompt: str) -> str:
        # user_prompt is unused
        return IN_CONTEXT_SYSTEM_PROMPT.format(
            examples=self._format_examples(self.examples),
            specification=self.specification
        )
