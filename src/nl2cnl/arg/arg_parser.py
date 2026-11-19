import argparse
from pathlib import Path

AVAILABLE_STRATEGIES = ["raw"]

# Validate that the provided CLI argument points to an existing file
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
            "guided by a formal grammar specification, and run yet-to-be-determined tests."
        ),
        epilog=(
            "Examples:\n"
            "  Single query:   python main.py -m ollama/qwen3.5:4b -y grammars/bioquery.yaml -t \"drugs related to asthma\"\n"
            "  Batch queries:  python main.py -m openai/gpt-4o -y grammars/bioquery.yaml -i queries.txt -o out.jsonl\n"
            "  Benchmark run:  python main.py -m ollama/qwen3.5:4b -y grammars/bioquery.yaml --test datasets/bioquery.json -s raw"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- REQUIRED ARGUMENTS
    required_group = parser.add_argument_group("Required Configuration")
    required_group.add_argument(
        "-m", "--model",
        type=str,
        required=True,
        help="LiteLLM model identifier (e.g., 'ollama/qwen3.5:4b', 'openai/gpt-4o', 'gemini/gemini-2.5-pro').",
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
        help="Path to a JSON test suite file (with expected CNL ground truth) to run full evaluation metrics.",
    )

    # --- 3. OPZIONI PIPELINE E OUTPUT ---
    options_group = parser.add_argument_group("Pipeline & Output Options")
    options_group.add_argument(
        "-s", "--strategy",
        type=str,
        choices=AVAILABLE_STRATEGIES,
        default="raw",
        help=f"IDK how to explain it. Choiches are: {', '.join(AVAILABLE_STRATEGIES)}. (default: raw)",
    )
    options_group.add_argument(
        "--no-output",
        action="store_true",
        default=False,
        help="Suppress printing model outputs to stdout (useful during --test benchmarks).",
    )

    return parser.parse_args()