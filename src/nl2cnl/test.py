# Column definition
import csv
from datetime import datetime

from lark import Lark, LarkError, UnexpectedInput

from nl2cnl.prompt.prompt_item import PromptItem
from nl2cnl.ui import CliUI

columns = ["id", "model", "strategy", "syntax_valid", "match", "prompt_tokens", "completion_tokens", "total_tokens", "latency_ms", "cost_usd"]

p = Lark.open("grammar.lark", parser="lalr")

# TODO: RENAME
def check_grammar(text: str) -> int:
    try:
        p.parse(text)
        return 1
    except UnexpectedInput:
        return 0
    except LarkError:
        return 0

def method_to_be_named(args, processed_items: list[PromptItem]):
    rows = []

    for item in CliUI().iter(processed_items, phase="Testing"):
        model_output = item.model_output
        assert model_output

        row = {
            "id": item.id,
            "model": args.model,
            "strategy": args.strategy,
            "syntax_valid": check_grammar(model_output.text),
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
def test_output(args, processed_items: list[PromptItem]) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f"./results/test-{timestamp}.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        writer.writeheader()

        rows = method_to_be_named(args, processed_items)
        writer.writerows(rows)