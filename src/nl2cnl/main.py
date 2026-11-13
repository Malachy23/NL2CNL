from dotenv import load_dotenv
from litellm import completion

load_dotenv()

m = [
    {"role": "user", "content": "What is 1+1?"}
]

answer = completion(
    model="ollama_chat/qwen3.5:4b",
    messages=m,
    temperature=0
)

text = answer.choices[0].message.content
print(text)
