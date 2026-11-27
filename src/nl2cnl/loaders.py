"""All the reading of input files lives here, so the rest of the code works on plain data."""
from json import load
from pathlib import Path
from typing import Any

from yaml import safe_load


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return load(file)


def load_text(path: Path) -> str:
    """Returns the content of the file <path> in string format"""
    with path.open("r", encoding="utf-8") as file:
        return file.read()


def load_yaml(path: Path) -> Any:
    """Returns the content of the .yaml file <path>.
    Usually a dict, but it can be any YAML value (None for an empty file): callers must check it.
    """
    with path.open("r", encoding="utf-8") as file:
        return safe_load(file)


def load_examples(path: Path | None) -> list[dict[str, str]]:
    """Returns examples in format [{"nl_input": "...", "cnl_output": "..."}, ...]
    Accepts both {"examples": [...]} and a bare list. Returns [] when no file is given.
    """
    if path is None:
        return []

    data = _load_json(path)
    return data["examples"] if isinstance(data, dict) else data


def load_test_cases(path: Path) -> list[dict[str, Any]]:
    """Returns test cases in format [{"id": "...", "nl_input": "...", "expected_cnl": [...]}, ...]
    Accepts both {"cases": [...]} and a bare list.
    """
    data = _load_json(path)
    return data["cases"] if isinstance(data, dict) else data
