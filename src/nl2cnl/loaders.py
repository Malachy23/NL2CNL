from pathlib import Path

from yaml import safe_load


def load_examples(examples_path: Path | None):
    """Returns examples in format
    [{"nl_input": "...", "cnl_output": "..."}, ...]
    """
    if examples_path is None:
        return []

    with examples_path.open("r", encoding="utf-8") as file:
        data = safe_load(file)
        return data["examples"] if isinstance(data, dict) else data

def load_text(path: Path) -> str:
    """Returns the content of the file <path> in string format"""
    with path.open("r", encoding="utf-8") as file:
        return file.read()