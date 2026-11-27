from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter

from nl2cnl.strategies import AVAILABLE_STRATEGIES


def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog="nl2cnl",
        description=(
            "NL2CNL: Translate Natural Language (NL) queries into a Controlled Natural Language (CNL) "
            "guided by a formal YAML grammar specification, and benchmark translation accuracy."
        ),
        epilog=(
            "Examples:\n"
            "  Config file:    uv run nl2cnl -c configs/bioquery_raw.yaml\n"
            "  Config + model: uv run nl2cnl -c configs/bioquery_raw.yaml -m groq/qwen/qwen3-32b\n"
            "  Single query:   uv run nl2cnl -m ollama_chat/qwen3.5:4b -y example.yaml -t \"drugs related to asthma\"\n"
            "  Benchmark run:  uv run nl2cnl -m openrouter/meta-llama/llama-3.3-70b-instruct:free -y example.yaml -b data/test_cases.json --no-output"
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )

    # --- CONFIGURATION FILE
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to a .yaml configuration file (CLI flags override values defined in the file).",
    )

    # --- REQUIRED ARGUMENTS (validated after merging with --config)
    required_group = parser.add_argument_group("Required Configuration")
    required_group.add_argument(
        "-m", "--model",
        type=str,
        default=None,
        help="LiteLLM model identifier (e.g., 'ollama_chat/qwen3.5:4b', 'groq/qwen/qwen3-32b').",
    )
    required_group.add_argument(
        "-y", "--yaml",
        type=str,
        default=None,
        help="Path to the .yaml file containing the target CNL grammar specification.",
    )

    # --- INPUT ARGUMENTS (mutually exclusive)
    input_group = parser.add_argument_group(
        "Execution Mode (choose one)",
        "Select whether to translate a single string, a plain query file, or run an evaluation dataset.",
    )
    mode = input_group.add_mutually_exclusive_group()
    mode.add_argument(
        "-t", "--text",
        type=str,
        default=None,
        help="Single natural language query to translate into CNL.",
    )
    mode.add_argument(
        "-i", "--input",
        type=str,
        default=None,
        help="Path to a plain text file containing one NL query per line.",
    )
    mode.add_argument(
        "-b", "--benchmark",
        type=str,
        default=None,
        help="Path to a JSON test suite file (with expected CNL ground truth).",
    )

    # --- PIPELINE & OUTPUT OPTIONS
    options_group = parser.add_argument_group("Pipeline & Output Options")
    options_group.add_argument(
        "-e", "--examples",
        type=str,
        default=None,
        help="Path to translation examples pool (NL -> CNL) for RAG strategies.",
    )
    options_group.add_argument(
        "-s", "--strategy",
        type=str,
        choices=AVAILABLE_STRATEGIES,
        default=None,
        help=f"Grammar injection strategy: {', '.join(AVAILABLE_STRATEGIES)}. (default: inctx)",
    )
    options_group.add_argument(
        "-k", "--top-k",
        type=int,
        default=None,
        help="Number of examples retrieved by the 'example' strategy. (default: 10)",
    )
    options_group.add_argument(
        "-g", "--grammar",
        type=str,
        default=None,
        help="Path to the .lark grammar used to check benchmark outputs. (default: grammar.lark)",
    )
    options_group.add_argument(
        "--no-output",
        action="store_true",
        default=None,
        help="Suppress printing translated CNL sentences to stdout.",
    )

    return parser.parse_args()