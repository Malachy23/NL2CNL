from atexit import register
from gc import freeze
from os import environ
from sys import exit

from dotenv import load_dotenv

from nl2cnl.cli import parse_args
from nl2cnl.model import FatalLLMError
from nl2cnl.ui import CliUI


def main():
    load_dotenv()
    args = parse_args()

    # To deactivate if wanting to use updated (online) costs
    environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    register(freeze)

    from nl2cnl.config import build_config
    from nl2cnl.formatter import format_input
    from nl2cnl.llm import prompt_model
    from nl2cnl.loaders import load_examples, load_text
    from nl2cnl.strategies import StrategyOptions, get_strategy

    config = build_config(args)

    CliUI().header(config.model, config.strategy)

    # --- INPUT FORMATTING
    with CliUI().step("Formatting input"):
        items = format_input(config)

    # --- STRATEGY SETUP
    with CliUI().step(f"Setting up strategy ({config.specification.name})"):
        prompt_strategy = get_strategy(config.strategy, StrategyOptions(top_k=config.top_k))
        prompt_strategy.setup(
            load_text(config.specification),
            load_examples(config.examples),
        )

    # --- PROMPTING
    try:
        for item in CliUI().iter(items, phase="Prompting"):
            system_prompt = prompt_strategy.get_system_prompt(item.nl_input)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": item.nl_input},
            ]
            item.model_output = prompt_model(config.model, messages)

            # Prints RETRIABLE_ERRORS
            error = item.model_output.error
            if error is not None:
                CliUI().error(error)
    except FatalLLMError as e:
        CliUI().error(str(e))
        exit(2)

    # --- BENCHMARK
    if config.benchmark is not None:
        from nl2cnl.evaluation.benchmark import start_benchmark

        start_benchmark(config, items)

    # --- OUTPUT
    if not config.no_output:
        CliUI().print_results(items)


if __name__ == "__main__":
    main()