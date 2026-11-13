from litellm import completion

# Takes model, an array of messages and temperature, and returns the text produced by the LLM
def prompt_model(model: str, messages, temperature=0):
    answer = completion(
        model=model,
        messages=messages,
        temperature=temperature
    )

    return answer.choices[0].message.content
