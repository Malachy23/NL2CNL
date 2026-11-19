from arg.arg_checker import check_args
from arg.arg_parser import parse_args
from arg.arg_processer import process_args
from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

from nl2cnl.prompt.prompt_model import PromptResult
from nl2cnl.prompt.sys_prompt.sys_prompt_strategy import get_strategy


def main():
    load_dotenv()

    user_prompts: list[str] = []
    model_output: list[PromptResult] = []

    # --- ARG PHASE
    args = parse_args()
    check_args(args)
    processed = process_args(args)
    # ---

    # --- USER PROMPT PHASE
    if args.text is not None:
        user_prompts.append(args.text)
    elif args.input is not None:
        pass
    elif args.test is not None:
        print("£Ciao")

    # ---

    # --- SYS PROMPT PHASE
    prompt_strategy = get_strategy(processed.strategy)
    prompt_strategy.setup(processed.yaml)
    # ---

    # --- PROMPT PHASE 

    model = processed.model

    for user_prompt in user_prompts:
        system_prompt = prompt_strategy.get_system_prompt(processed.text)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        model_output.append(prompt_model(model, messages))
    # ---

    # --- TEST PHASE


    # ---

    # --- OUTPUT PHASE
    if args.output is None:
        for out in model_output:
            print(out.text)
    else:
        pass # Writes output in file
    # ---

if __name__ == "__main__":
    main()