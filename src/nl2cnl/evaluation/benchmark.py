# Column definition
import csv
from datetime import datetime
from pathlib import Path

from nl2cnl.evaluation.validator import is_syntax_valid
from nl2cnl.model import PromptItem
from nl2cnl.ui import CliUI

columns = ["id", "model", "strategy", "syntax_valid", "match", "prompt_tokens", "completion_tokens", "total_tokens", "latency_ms", "cost_usd"]

def _evaluate_items(args, processed_items: list[PromptItem]):
    rows = []

    for item in CliUI().iter(processed_items, phase="Benchmarking"):
        model_output = item.model_output
        assert model_output
        assert item.expected_cnl

        row = {
            "id": item.id,
            "model": args.model,
            "strategy": args.strategy,
            "syntax_valid": is_syntax_valid(model_output.text),
            "match": 1 if model_output.text in item.expected_cnl else 0,
            "prompt_tokens": model_output.prompt_tokens,
            "completion_tokens": model_output.completion_tokens,
            "total_tokens": model_output.total_tokens,
            "latency_ms": model_output.latency_ms,
            "cost_usd": model_output.cost_usd
        }
        rows.append(row)

    return rows

# Takes from granted that PromptItems have already been processed by LLM
def start_benchmark(args, processed_items: list[PromptItem]) -> None:
    """Takes a list[PromptItem] processed by an LLM (with PromptItem.PromptResult not None)
    and performes a benchmark on its results, saving it into a <timestamp>.csv file.

    For each <processed_item>, the model_output is parsed by Lark to check whether it respects the grammar,
    and whether it is equal to the <processed_item>.expected_cnl, taken from the benchmark (-b) file provided .
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    Path("./data/results").mkdir(parents=True, exist_ok=True)
    with open(f"./data/results/test-{timestamp}.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        writer.writeheader()

        rows = _evaluate_items(args, processed_items)
        writer.writerows(rows)