from dotenv import load_dotenv

from nl2cnl.arg.arg_checker import check_args
from nl2cnl.arg.arg_parser import parse_args
from nl2cnl.input_formatter import format_input
from nl2cnl.prompt.prompt_model import prompt_model
from nl2cnl.prompt.sys_prompt.sys_prompt_strategy import get_strategy
from nl2cnl.benchmark import test_output
from nl2cnl.ui import CliUI


def main():
    load_dotenv()
    args = parse_args()
    check_args(args)

    CliUI().header(args.model, args.strategy)

    # --- INPUT FORMATTING
    with CliUI().step("Formatting input"):
        items = format_input(args)

    # --- STRATEGY SETUP
    with CliUI().step(f"Setting up strategy ({args.yaml.name})"):
        prompt_strategy = get_strategy(args.strategy)
        prompt_strategy.setup(args.yaml, args.examples)

    # --- PROMPTING
    for item in CliUI().iter(items, phase="Prompting"):
        messages = [
            {"role": "system", "content": prompt_strategy.get_system_prompt(item.nl_input)},
            {"role": "user", "content": item.nl_input},
        ]
        item.model_output = prompt_model(args.model, messages)

    # --- BENCHMARK
    if args.benchmark is not None:
        start_benchmark(args, items)

    # --- OUTPUT
    if not args.no_output:
        CliUI().print_results(items)


if __name__ == "__main__":
    main()