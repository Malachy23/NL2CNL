from litellm import get_llm_provider, validate_environment
from pathlib import Path
from sys import exit

from nl2cnl.ui import CliUI

LOCAL_PROVIDERS = {"ollama", "ollama_chat", "lm_studio", "llamacpp", "vllm"}

class InvalidArgumentError(Exception):
    pass

# Validate LiteLLM provider syntax and check required API keys for remote models
def check_model_availability(model: str) -> None:
    if not model or not model.strip():
        raise InvalidArgumentError("Model identifier cannot be empty.")

    try:
        _, provider, _, _ = get_llm_provider(model=model)
    except Exception as e:
        raise InvalidArgumentError(
            f"Unrecognized provider in '{model}'. Use '<provider>/<model>' "
            "(e.g., 'ollama_chat/qwen3.5:4b', 'groq/qwen/qwen3-32b', 'openrouter/...:free')."
        ) from e

    if provider in LOCAL_PROVIDERS:
        return

    env_check = validate_environment(model=model)
    if not env_check.get("keys_in_environment", False):
        missing = ", ".join(env_check.get("missing_keys", [])) or f"{provider.upper()}_API_KEY"
        raise InvalidArgumentError(
            f"Missing API key(s) in .env for provider '{provider}': {missing}"
        )

# Checks whether the file has the expected extension
def check_file_suffix(file: Path, expected_suffix: str):
    if file.suffix != expected_suffix:
        raise InvalidArgumentError(f"File {file.name} has wrong suffix: it should be {expected_suffix}")

# Validates the selected input mode (--text, --input, or --test)
def check_input_source(args) -> None:
    if args.input is not None:
        check_file_suffix(args.input, ".txt")
    elif args.text is not None and not args.text.strip():
        raise InvalidArgumentError("Provided prompt text (-t) cannot be empty or whitespace only.")
    elif args.test is not None:
        check_file_suffix(args.test, ".json")

def check_args(args):
    try:
        check_model_availability(args.model)
        check_input_source(args)
        check_file_suffix(args.yaml, ".yaml")

    except InvalidArgumentError as e:
        CliUI().error(f"Error: {e}")
        exit(2)
