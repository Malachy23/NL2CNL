import argparse
from pathlib import Path

AVAILABLE_STRATEGIES = ["raw"]

# Validates that the provided CLI argument points to an existing file
def existing_file(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: '{path_str}'")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="nl2cnl",
        description=(
            "NL2CNL: Translate Natural Language (NL) queries into a Controlled Natural Language (CNL) "
            "guided by a formal YAML grammar specification, and benchmark translation accuracy."
        ),
        epilog=(
            "Examples:\n"
            "  Single query:   uv run src/nl2cnl/main.py -m ollama_chat/qwen3.5:4b -y example.yaml -t \"drugs related to asthma\"\n"
            "  Batch queries:  uv run src/nl2cnl/main.py -m groq/qwen/qwen3-32b -y example.yaml -i queries.txt\n"
            "  Benchmark run:  uv run src/nl2cnl/main.py -m openrouter/meta-llama/llama-3.3-70b-instruct:free -y example.yaml --test data/test_cases.json --no-output"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- REQUIRED ARGUMENTS
    required_group = parser.add_argument_group("Required Configuration")
    required_group.add_argument(
        "-m", "--model",
        type=str,
        required=True,
        help="LiteLLM model identifier (e.g., 'ollama_chat/qwen3.5:4b', 'groq/qwen/qwen3-32b', 'gemini/gemini-2.5-flash-lite').",
    )
    required_group.add_argument(
        "-y", "--yaml",
        type=existing_file,
        required=True,
        help="Path to the .yaml file containing the target CNL grammar specification.",
    )
    # ---

    # --- INPUT ARGUMENTS (mutually exclusive)
    input_group = parser.add_argument_group(
        "Execution Mode (choose one)",
        "Select whether to translate a single string, a plain query file, or run an evaluation dataset.",
    )
    mode = input_group.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "-t", "--text",
        type=str,
        default=None,
        help="Single natural language query to translate into CNL.",
    )
    mode.add_argument(
        "-i", "--input",
        type=existing_file,
        default=None,
        help="Path to a plain text file containing one NL query per line (batch translation without evaluation).",
    )
    mode.add_argument(
        "--test",
        type=existing_file,
        default=None,
        help="Path to a JSON test suite file (with expected CNL ground truth) to run evaluation metrics.",
    )
    # ---

    # --- PIPELINE & OUTPUT OPTIONS
    options_group = parser.add_argument_group("Pipeline & Output Options")
    options_group.add_argument(
        "-s", "--strategy",
        type=str,
        choices=AVAILABLE_STRATEGIES,
        default="raw",
        help=(
            "Grammar injection and retrieval strategy used to build the system prompt "
            f"(available: {', '.join(AVAILABLE_STRATEGIES)}). (default: %(default)s)"
        ),
    )
    options_group.add_argument(
        "--no-output",
        action="store_true",
        default=False,
        help="Suppress printing translated CNL sentences to stdout.",
    )
    # ---

    return parser.parse_args()