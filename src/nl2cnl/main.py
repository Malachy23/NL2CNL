from dotenv import load_dotenv

from nl2cnl.arg.arg_checker import build_config
from nl2cnl.arg.arg_parser import parse_args
from nl2cnl.benchmark import start_benchmark
from nl2cnl.input_formatter import format_input
from nl2cnl.prompt.prompt_model import prompt_model
from nl2cnl.prompt.sys_prompt.sys_prompt_strategy import get_strategy
from nl2cnl.ui import CliUI


def main():
    load_dotenv()
    args = parse_args()
    config = build_config(args)

    CliUI().header(config.model, config.strategy)

    # --- INPUT FORMATTING
    with CliUI().step("Formatting input"):
        items = format_input(config)

    # --- STRATEGY SETUP
    with CliUI().step(f"Setting up strategy ({config.specification.name})"):
        prompt_strategy = get_strategy(config.strategy)
        prompt_strategy.setup(config.specification, config.examples)

    # --- PROMPTING
    for item in CliUI().iter(items, phase="Prompting"):
        messages = [
            {"role": "system", "content": prompt_strategy.get_system_prompt(item.nl_input)},
            {"role": "user", "content": item.nl_input},
        ]
        item.model_output = prompt_model(config.model, messages)

    # --- BENCHMARK
    if config.benchmark is not None:
        start_benchmark(config, items)

    # --- OUTPUT
    if not config.no_output:
        CliUI().print_results(items)


if __name__ == "__main__":
    main()