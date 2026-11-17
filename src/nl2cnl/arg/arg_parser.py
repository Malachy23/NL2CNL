import argparse
from pathlib import Path


# TODO: Add trivial comment
def existing_file(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {path_str}")
    return path

def parse_args():
    parser = argparse.ArgumentParser(description="Hello")

    parser.add_argument(
        "-i", "--input",
        type=existing_file,
        default=None,
        help="specify file to extract queries from"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="specify file to put output to. If unspecified, it prints it in the CL"
    )

    parser.add_argument(
        "-t", "--text",
        type=str,
        default=None,
        help="single query specification"
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        required=True,
        help="specify the model to be used"
    )

    parser.add_argument(
        "-y", "--yaml",
        type=existing_file,
        required=True,
        help="specify the location of the .yaml grammar definition file"
    )

    return parser.parse_args()

