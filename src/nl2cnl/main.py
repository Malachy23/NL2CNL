from arg.arg_checker import check_args
from arg.arg_parser import parse_args
from arg.arg_processer import process_args
from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

from nl2cnl.prompt.prompt_model import PromptResult
from nl2cnl.prompt.sys_prompt.sys_prompt_strategy import choose_strategy


def main():
    load_dotenv()

    # --- ARG PHASE
    args = parse_args()
    check_args(args)
    processed = process_args(args)
    # ---

    # --- SYS PROMPT PHASE
    prompt_strategy = choose_strategy(processed.strategy)
    prompt_strategy.setup(processed.yaml)
    system_prompt = prompt_strategy.get_system_prompt(processed.text)
    # ---

    # --- PROMPT PHASE 

    model = processed.model

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": processed.text}
    ]

    response: PromptResult = prompt_model(model, messages)
    # ---

    # --- TEST PHASE


    # ---

    print(response)

if __name__ == "__main__":
    main()