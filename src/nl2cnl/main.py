from arg.arg_checker import check_args
from arg.arg_parser import parse_args
from arg.arg_processer import process_args
from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

load_dotenv()

# ARG PHASE
args = parse_args()
check_args(args)
processed = process_args(args)


model = "ollama_chat/qwen3.5:4b"

messages = [
    {"role": "user", "content": "What is 1+1?"}
]

text = prompt_model(model, messages)

print(text)
