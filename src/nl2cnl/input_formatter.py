from json import load

from nl2cnl.prompt.prompt_item import PromptItem


# Processes CLI argument in PromptItem format
def format_input(args) -> list[PromptItem]:
    items: list[PromptItem] = []

    if args.text is not None:
        items.append(PromptItem("cli_01", args.text))

    elif args.input is not None:
        with open(args.input, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if line.strip():
                    items.append(PromptItem(id=f"in_{idx}", nl_input=line.strip()))

    elif args.test is not None:
        with open(args.test, "r", encoding="utf-8") as f:
            raw_tests = load(f)
            items = [PromptItem(**row) for row in raw_tests]

    return items