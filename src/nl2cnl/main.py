from arg.arg_checker import check_args
from arg.arg_parser import parse_args
from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

from nl2cnl.input_formatter import format_input
from nl2cnl.prompt.sys_prompt.sys_prompt_strategy import get_strategy


def main():
    load_dotenv()

    # --- ARG PHASE
    args = parse_args()
    check_args(args)
    # ---

    # --- INPUT FORMATTING PHASE
    items = format_input(args)
    # ---

    # --- SYS PROMPT PHASE
    prompt_strategy = get_strategy(args.strategy)
    prompt_strategy.setup(args.yaml)
    # ---

    # --- PROMPTING PHASE 
    model = args.model

    for item in items:
        system_prompt = prompt_strategy.get_system_prompt(item.nl_input)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": item.nl_input}
        ]

        item.model_output = prompt_model(model, messages)
    # ---

    # --- TEST PHASE

    # ---

    # --- OUTPUT PHASE
    if not args.no_output:
        for item in items:
            print(f"{item.id}: {item.model_output.text}")
    # ---

if __name__ == "__main__":
    main()