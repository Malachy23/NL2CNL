from dotenv import load_dotenv
import argparse
from prompt.prompt_model import prompt_model

load_dotenv()

# PARSER DEFINITION (to be moved in future commit)
parser = argparse.ArgumentParser(description="Hello")

parser.add_argument(
    "-i", "--input",
    type=str,
    default="",
    help="Specify file to extract queries from"
)

parser.add_argument(
    "-o", "--output",
    type=str,
    default="",
    help="Specify file to put output to. If unspecified, it prints it in the CL"
)

parser.add_argument(
    "-t", "--text",
    type=str,
    default="",
    help="Single query specification"
)

# This requires a check of the .env, there is an option in LiteLLM which does this automatically
#  REMEMBER
parser.add_argument(
    "-m", "--model",
    type=str,
    required=True,
    help="Specify the model to be used"
)

parser.add_argument(
    "-y", "--yaml",
    type=str,
    required=True,
    help="Specify the location of the .yaml grammar definition file"
)

args = parser.parse_args()

print(args.input)
print(args.output)
print(args.model)
print(args.text)
print(args.yaml)


'''
model = "ollama_chat/qwen3.5:4b"

messages = [
    {"role": "user", "content": "What is 1+1?"}
]

text = prompt_model(model, messages)

print(text)
'''
