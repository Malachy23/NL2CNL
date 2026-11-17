from dotenv import load_dotenv
from args.arg_parser import parser
from prompt.prompt_model import prompt_model

load_dotenv()

args = parser.parse_args()
print(args.model)

model = "ollama_chat/qwen3.5:4b"

messages = [
    {"role": "user", "content": "What is 1+1?"}
]

text = prompt_model(model, messages)

print(text)
