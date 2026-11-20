from dataclasses import dataclass

from nl2cnl.prompt.prompt_model import PromptResult


@dataclass
class PromptItem:
    id: str
    nl_input: str
    expected_cnl: list[str] | None = None
    model_output: PromptResult | None = None