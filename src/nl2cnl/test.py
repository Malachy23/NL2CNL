# Column definition
import csv
from datetime import datetime

from nl2cnl.prompt.prompt_item import PromptItem

columns = ["id", "model", "strategy", "pass", "prompt_tokens", "completion_tokens", "total_tokens", "latency_ms", "cost_usd"]

def method_to_be_named(args, processed_items: list[PromptItem]):
    rows = []
    for item in processed_items:
        model_output = item.model_output
        assert model_output

        row = {
            "id": item.id,
            "model": args.model,
            "strategy": args.strategy,
            "pass": 1 if model_output.text == item.expected_cnl else 0,
            "prompt_tokens": model_output.prompt_tokens,
            "completion_tokens": model_output.completion_tokens,
            "total_tokens": model_output.total_tokens,
            "latency_ms": model_output.latency_ms,
            "cost_usd": model_output.cost_usd
        }
        rows.append(row)

    return rows

# Takes from granted that PromptItems have already been processed by LLM
def test_output(args, processed_items: list[PromptItem]) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f"./results/test-{timestamp}.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        writer.writeheader()

        rows = method_to_be_named(args, processed_items)
        writer.writerows(rows)