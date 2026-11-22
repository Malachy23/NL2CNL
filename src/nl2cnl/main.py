from atexit import register
from gc import freeze
from os import environ

from dotenv import load_dotenv

from nl2cnl.arg.arg_parser import parse_args
from nl2cnl.ui import CliUI


def main():
    load_dotenv()
    args = parse_args()

    environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    register(freeze)

    from nl2cnl.arg.arg_checker import build_config
    from nl2cnl.pipeline.input_formatter import format_input
    from nl2cnl.pipeline.prompt_model import prompt_model
    from nl2cnl.pipeline.system_prompt import get_strategy


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
        system_prompt = prompt_strategy.get_system_prompt(item.nl_input)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": item.nl_input},
        ]
        item.model_output = prompt_model(config.model, messages)

    # --- BENCHMARK
    if config.benchmark is not None:
        from nl2cnl.pipeline.benchmark import start_benchmark

        start_benchmark(config, items)

    # --- OUTPUT
    if not config.no_output:
        CliUI().print_results(items)


if __name__ == "__main__":
    main()