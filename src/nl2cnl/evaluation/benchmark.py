import csv
from datetime import datetime
from pathlib import Path

from nl2cnl.config import AppConfig
from nl2cnl.evaluation.validator import is_syntax_valid
from nl2cnl.model import PromptItem
from nl2cnl.ui import CliUI

RESULTS_DIR = Path("data/results")

COLUMNS = [
    "id", "model", "strategy", "top_k", "syntax_valid", "match",
    "prompt_tokens", "completion_tokens", "total_tokens", "latency_ms", "cost_usd", "error",
]


def _evaluate_items(config: AppConfig, processed_items: list[PromptItem]) -> list[dict]:
    assert config.grammar is not None  # Always set by build_config() when benchmarking
    rows = []

    for item in CliUI().iter(processed_items, phase="Benchmarking"):
        model_output = item.model_output
        assert model_output is not None
        assert item.expected_cnl is not None

        rows.append({
            "id": item.id,
            "model": config.model,
            "strategy": config.strategy,
            "top_k": config.top_k if config.strategy == "example" else "",
            "syntax_valid": int(is_syntax_valid(model_output.text, config.grammar)),
            "match": int(model_output.text in item.expected_cnl),
            "prompt_tokens": model_output.prompt_tokens,
            "completion_tokens": model_output.completion_tokens,
            "total_tokens": model_output.total_tokens,
            "latency_ms": model_output.latency_ms,
            "cost_usd": model_output.cost_usd,
            "error": model_output.error or "",
        })

    return rows


def start_benchmark(config: AppConfig, processed_items: list[PromptItem]) -> Path:
    """Takes a list[PromptItem] already processed by an LLM (model_output not None)
    and saves the evaluation of each one into data/results/test-<timestamp>.csv.

    For each item, model_output is parsed by Lark to check whether it respects the grammar,
    and compared with item.expected_cnl, taken from the benchmark (-b) file.
    Returns the path of the CSV file.
    """
    rows = _evaluate_items(config, processed_items)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = RESULTS_DIR / f"test-{timestamp}.csv"

    with out_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return out_path
