from arg.arg_checker import check_args
from arg.arg_parser import parse_args
from arg.arg_processer import process_args
from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

from nl2cnl.input_formatter import format_input
from nl2cnl.prompt.sys_prompt.sys_prompt_strategy import get_strategy


def main():
    load_dotenv()

    # --- ARG PHASE
    args = parse_args()
    check_args(args)
    processed = process_args(args)
    # ---

    # --- INPUT FORMAT PHASE
    items = format_input(args)
    # ---

    # --- SYS PROMPT PHASE
    prompt_strategy = get_strategy(processed.strategy)
    prompt_strategy.setup(processed.yaml)
    # ---

    # --- PROMPTING PHASE 
    model = processed.model

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
    if args.output is None:
        for item in items:
            print(item.model_output.text)
    else:
        pass # Writes output in file
    # ---

if __name__ == "__main__":
    main()