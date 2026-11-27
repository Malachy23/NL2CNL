from pathlib import Path

from nl2cnl.config import AppConfig
from nl2cnl.formatter import format_input
from nl2cnl.strategies import AVAILABLE_STRATEGIES, StrategyOptions, get_strategy


def make_config(**overrides) -> AppConfig:
    values = dict(
        model="ollama_chat/test", specification=Path("data/specifications/bioquery.yaml"),
        text=None, input=None, benchmark=None, examples=None,
        strategy="inctx", no_output=False, grammar=None, top_k=10,
    )
    values.update(overrides)
    return AppConfig(**values)


def test_format_text():
    [item] = format_input(make_config(text="approved drugs"))
    assert (item.id, item.nl_input, item.expected_cnl) == ("cli_01", "approved drugs", None)


def test_format_input_file_skips_blank_lines_and_keeps_line_numbers(tmp_path):
    queries = tmp_path / "queries.txt"
    queries.write_text("first\n\n  second  \n", encoding="utf-8")

    items = format_input(make_config(input=queries))
    assert [(i.id, i.nl_input) for i in items] == [("in_0", "first"), ("in_2", "second")]


def test_format_benchmark():
    items = format_input(make_config(benchmark=Path("data/tests/test_cases.json")))
    assert items and all(item.expected_cnl for item in items)


def test_registry_lists_only_existing_strategies():
    assert AVAILABLE_STRATEGIES == ["inctx", "example"]


def test_in_context_prompt_contains_grammar_and_examples():
    strategy = get_strategy("inctx", StrategyOptions())
    strategy.setup("GRAMMAR-TEXT", [
        {"nl_input": "first nl", "cnl_output": "First?"},
        {"nl_input": "second nl", "cnl_output": "Second?"},
    ])
    prompt = strategy.get_system_prompt("anything")

    assert "GRAMMAR-TEXT" in prompt
    # Reversed order: the first example ends up closest to the user prompt
    assert prompt.index("Input: second nl") < prompt.index("Input: first nl")


def test_in_context_prompt_without_examples():
    strategy = get_strategy("inctx")
    strategy.setup("GRAMMAR-TEXT", [])
    assert "EXAMPLES" not in strategy.get_system_prompt("anything")
