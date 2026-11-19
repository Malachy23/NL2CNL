from pathlib import Path
from sys import exit, stderr


class InvalidArgumentError(Exception):
    pass

# TODO: This needs to check whether the user-chosed model actually exists (from LiteLLM perspective)
# and if not local it should check whether the user imported the appropriate API-KEYS in the .env
def check_model_availability(model: str):
    pass

# Checks whether the file has the expected extension
def check_file_suffix(file: Path, expected_suffix: str):
    if file.suffix != expected_suffix:
        raise InvalidArgumentError(f"File {file.name} has wrong suffix: it should be {expected_suffix}")

# TODO: Change this name
def check_input(args):
    input = args.input
    text = args.text
    test = args.test

    if input is not None:
        check_file_suffix(input, ".txt")
    elif text is not None and text == "":
        raise InvalidArgumentError("Provided prompt is empty")
    elif test is not None:
        check_file_suffix(test, ".json")

def check_args(args):
    try:
        check_model_availability(args.model)
        check_input(args)
        check_file_suffix(args.yaml, ".yaml")

    except InvalidArgumentError as e:
        print(f"Error: {e}", file=stderr)
        exit(2)
