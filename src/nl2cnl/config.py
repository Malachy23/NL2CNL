import sys
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from litellm import get_llm_provider, validate_environment
from yaml import YAMLError, safe_load

from nl2cnl.strategies import AVAILABLE_STRATEGIES
from nl2cnl.ui import CliUI

LOCAL_PROVIDERS = {"ollama", "ollama_chat", "lm_studio", "llamacpp", "vllm"}
INPUT_KEYS = ("text", "input", "benchmark")
ALLOWED_CONFIG_KEYS = {
    "model",
    "specification",
    "text",
    "input",
    "benchmark",
    "examples",
    "strategy",
    "no_output",
}


class InvalidArgumentError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class AppConfig:
    model: str
    specification: Path
    text: str | None
    input: Path | None
    benchmark: Path | None
    examples: Path | None
    strategy: str
    no_output: bool


def check_file_existence(path_str: str | Path) -> Path:
    path = Path(path_str)
    if not path.is_file():
        raise InvalidArgumentError(f"File not found: '{path_str}'")
    return path


def check_file_suffix(file: Path, expected_suffix: str) -> None:
    if file.suffix not in expected_suffix:
        raise InvalidArgumentError(f"File '{file.name}' has wrong suffix '{file.suffix}': expected {expected_suffix}.")


def check_model_availability(model: str) -> None:
    if not isinstance(model, str) or not model.strip():
        raise InvalidArgumentError("Model identifier cannot be empty.")

    try:
        _, provider, _, _ = get_llm_provider(model=model)
    except Exception as e:
        raise InvalidArgumentError(
            f"Unrecognized provider in '{model}'. Use '<provider>/<model>' "
            "(e.g., 'ollama_chat/qwen3.5:4b', 'groq/qwen/qwen3-32b')."
        ) from e

    if provider in LOCAL_PROVIDERS:
        return

    env_check = validate_environment(model=model)
    if not env_check.get("keys_in_environment", False):
        missing = ", ".join(env_check.get("missing_keys", [])) or f"{provider.upper()}_API_KEY"
        raise InvalidArgumentError(f"Missing API key(s) in .env for provider '{provider}': {missing}")

# Extracts configs from args
# If provided, it first extracts them from config.yaml, and then overrides those that where
# explicitly provided by the user.
def extract_raw_config(args: Namespace) -> dict[str, Any]:
    raw: dict[str, Any] = {}

    if args.config is not None:
        cfg_path = check_file_existence(args.config)
        check_file_suffix(cfg_path, ".yaml")

        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                loaded = safe_load(f) or {}
        except YAMLError as e:
            raise InvalidArgumentError(f"Invalid YAML syntax in '{cfg_path.name}': {e}") from e

        if not isinstance(loaded, dict):
            raise InvalidArgumentError(f"Configuration file '{cfg_path.name}' must define a key-value mapping.")

        unknown_keys = set(loaded.keys()) - ALLOWED_CONFIG_KEYS
        if unknown_keys:
            raise InvalidArgumentError(f"Unknown key(s) in '{cfg_path.name}': {', '.join(sorted(unknown_keys))}")

        raw.update(loaded)

    # Maps CLI flags to AppConfig
    cli_overrides = {
        "model": args.model,
        "specification": args.yaml,
        "text": args.text,
        "input": args.input,
        "benchmark": args.benchmark,
        "examples": args.examples,
        "strategy": args.strategy,
        "no_output": args.no_output,
    }

    # Overrides input modality if user provided it
    if any(cli_overrides[k] is not None for k in INPUT_KEYS):
        for k in INPUT_KEYS:
            raw[k] = None

    for key, value in cli_overrides.items():
        if value is not None:
            raw[key] = value

    # Default values
    raw.setdefault("strategy", "inctx")
    raw.setdefault("no_output", False)

    return raw

# Validates extracted arguments
def validate_and_build(raw: dict[str, Any]) -> AppConfig:
    # Required parameters
    if not raw.get("model"):
        raise InvalidArgumentError("Missing required parameter: 'model' (-m / --model).")
    if not raw.get("specification"):
        raise InvalidArgumentError("Missing required parameter: 'specification' (-y / --yaml).")

    check_model_availability(raw["model"])

    spec_path = check_file_existence(raw["specification"])
    check_file_suffix(spec_path, ".yaml")

    # Checks whether exactly one input modality has been provided 
    provided_inputs = [k for k in INPUT_KEYS if raw.get(k) is not None]
    if len(provided_inputs) == 0:
        raise InvalidArgumentError("No input source provided. Specify one of: 'text' (-t), 'input' (-i), or 'benchmark' (-b).")
    if len(provided_inputs) > 1:
        raise InvalidArgumentError(f"Mutually exclusive inputs specified together: {', '.join(provided_inputs)}.")

    text_val: str | None = None
    input_path: Path | None = None
    benchmark_path: Path | None = None

    if raw.get("text") is not None:
        if not isinstance(raw["text"], str) or not raw["text"].strip():
            raise InvalidArgumentError("Provided prompt 'text' (-t) cannot be empty.")
        text_val = raw["text"].strip()

    elif raw.get("input") is not None:
        input_path = check_file_existence(raw["input"])
        check_file_suffix(input_path, ".txt")

    elif raw.get("benchmark") is not None:
        benchmark_path = check_file_existence(raw["benchmark"])
        check_file_suffix(benchmark_path, ".json")

    # Optionals parameters
    strategy = raw["strategy"]
    if strategy not in AVAILABLE_STRATEGIES:
        raise InvalidArgumentError(
            f"Invalid strategy '{strategy}'. Allowed choices: {', '.join(AVAILABLE_STRATEGIES)}."
        )

    examples_path: Path | None = None
    if raw.get("examples") is not None:
        examples_path = check_file_existence(raw["examples"])
        check_file_suffix(examples_path, ".json")

    if strategy == "example" and examples_path is None:
        raise InvalidArgumentError("Strategy 'example' requires examples to be provided (-e, --examples)")

    return AppConfig(
        model=raw["model"],
        specification=spec_path,
        text=text_val,
        input=input_path,
        benchmark=benchmark_path,
        examples=examples_path,
        strategy=strategy,
        no_output=raw["no_output"],
    )


def build_config(args: Namespace) -> AppConfig:
    try:
        raw = extract_raw_config(args)
        return validate_and_build(raw)
    except InvalidArgumentError as e:
        CliUI().error(str(e))
        sys.exit(2)