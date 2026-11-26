from json import load

from nl2cnl.arg.arg_checker import AppConfig
from nl2cnl.model import PromptItem, PromptResult


# Processes CLI argument in PromptItem format
def format_input(config : AppConfig) -> list[PromptItem]:
    items: list[PromptItem] = []

    if config.text is not None:
        items.append(PromptItem("cli_01", config.text))

    elif config.input is not None:
        with open(config.input, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if line.strip():
                    items.append(PromptItem(id=f"in_{idx}", nl_input=line.strip()))

    # TODO: Maybe move file opening logic somewhere else. 
    elif config.benchmark is not None:
        with open(config.benchmark, "r", encoding="utf-8") as f:
            data = load(f)
            raw_tests = data["cases"] if isinstance(data, dict) else data
            items = [PromptItem(**row) for row in raw_tests]

    return items