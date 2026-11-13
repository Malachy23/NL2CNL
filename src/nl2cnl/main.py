from dotenv import load_dotenv
from prompt.prompt_model import prompt_model

load_dotenv()

model = "ollama_chat/qwen3.5:4b"

messages = [
    {"role": "user", "content": "What is 1+1?"}
]

text = prompt_model(model, messages)

print(text)
