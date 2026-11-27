from pathlib import Path

import pytest

from nl2cnl.config import InvalidArgumentError, check_file_suffix, validate_and_build

BASE = {
    "model": "ollama_chat/test",  # local provider: no API key needed
    "specification": "data/specifications/bioquery.yaml",
    "strategy": "inctx",
    "no_output": False,
    "top_k": 10,
}


@pytest.mark.parametrize("name", ["config.yaml", "a/b/config.yaml"])
def test_suffix_accepted(name):
    check_file_suffix(Path(name), ".yaml")


@pytest.mark.parametrize("name", ["config", "config.y", "config.yml", "config.yaml.bak"])
def test_suffix_rejected(name):
    with pytest.raises(InvalidArgumentError):
        check_file_suffix(Path(name), ".yaml")


def test_valid_text_config():
    config = validate_and_build({**BASE, "text": "  approved drugs  "})
    assert config.text == "approved drugs"
    assert config.grammar is None  # only needed when benchmarking


def test_benchmark_uses_default_grammar():
    config = validate_and_build({**BASE, "benchmark": "data/tests/test_cases.json"})
    assert config.grammar == Path("grammar.lark")


def test_no_input_rejected():
    with pytest.raises(InvalidArgumentError, match="No input"):
        validate_and_build(BASE)


def test_two_inputs_rejected():
    with pytest.raises(InvalidArgumentError, match="Mutually exclusive"):
        validate_and_build({**BASE, "text": "q", "input": "data/inputs/input.txt"})


def test_example_strategy_requires_examples():
    with pytest.raises(InvalidArgumentError, match="requires examples"):
        validate_and_build({**BASE, "text": "q", "strategy": "example"})


@pytest.mark.parametrize("top_k", [0, -1, "3", True])
def test_invalid_top_k_rejected(top_k):
    with pytest.raises(InvalidArgumentError, match="top_k"):
        validate_and_build({**BASE, "text": "q", "top_k": top_k})


def test_unknown_strategy_rejected():
    with pytest.raises(InvalidArgumentError, match="Invalid strategy"):
        validate_and_build({**BASE, "text": "q", "strategy": "subgrammar"})
