from nl2cnl.config import AppConfig
from nl2cnl.loaders import load_test_cases, load_text
from nl2cnl.model import PromptItem


def format_input(config: AppConfig) -> list[PromptItem]:
    """Converts the chosen input source (-t, -i or -b) into a list of PromptItem"""
    if config.text is not None:
        return [PromptItem(id="cli_01", nl_input=config.text)]

    if config.input is not None:
        lines = load_text(config.input).splitlines()
        # idx is the line number in the file, so ids stay stable even with blank lines
        return [PromptItem(id=f"in_{idx}", nl_input=line.strip()) for idx, line in enumerate(lines) if line.strip()]

    if config.benchmark is not None:
        return [PromptItem(**case) for case in load_test_cases(config.benchmark)]

    return []
