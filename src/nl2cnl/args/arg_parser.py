import argparse

parser = argparse.ArgumentParser(description="Hello")

parser.add_argument(
    "-i", "--input",
    type=str,
    default="",
    help="specify file to extract queries from"
)

parser.add_argument(
    "-o", "--output",
    type=str,
    default="",
    help="specify file to put output to. If unspecified, it prints it in the CL"
)

parser.add_argument(
    "-t", "--text",
    type=str,
    default="",
    help="single query specification"
)

# This requires a check of the .env, there is an option in LiteLLM which does this automatically
#  REMEMBER
parser.add_argument(
    "-m", "--model",
    type=str,
    required=True,
    help="specify the model to be used"
)

parser.add_argument(
    "-y", "--yaml",
    type=str,
    required=True,
    help="specify the location of the .yaml grammar definition file"
)


