from litellm import completion


def prompt_model(model: str, messages: list[dict], temperature: float = 0.1) -> str:
    response = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=2048,
        extra_body={
            "think": False,
            "options": {"num_ctx": 8192},
        },
    )
    # print("Raw response:", response.model_dump_json(indent=2))

    return (response.choices[0].message.content or "").strip()