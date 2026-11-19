
from dataclasses import dataclass
from time import perf_counter

from litellm import completion, completion_cost


@dataclass(frozen=True, slots=True)
class PromptResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float


def prompt_model(
    model: str,
    messages: list[dict],
    *,
    temperature: float = 0.1,
    max_tokens: int = 2048,
    num_ctx: int = 8192,
    reasoning_effort: str = "none",
) -> PromptResult:

    start = perf_counter()

    response = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        num_ctx=num_ctx,
        reasoning_effort=reasoning_effort,
        stream=False,
    )

    latency_ms = (perf_counter() - start) * 1000

    choice = response.choices[0]
    content = choice.message.content

    text = content.strip() if isinstance(content, str) else ""

    usage = response.usage

    prompt_tokens = usage.prompt_tokens or 0 if usage else 0
    completion_tokens = usage.completion_tokens or 0 if usage else 0
    total_tokens = usage.total_tokens or 0 if usage else 0

    cost_usd = completion_cost(completion_response=response)

    return PromptResult(
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_usd=float(cost_usd or 0.0),
    )
