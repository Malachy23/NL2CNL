import re
import sys
from dataclasses import dataclass
from time import perf_counter

import litellm
from litellm import completion, completion_cost
from litellm.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
)

from nl2cnl.ui import CliUI

litellm.suppress_debug_info = True
litellm.set_verbose = False
litellm.drop_params = True  # Discards parameters not supported by some models

FATAL_ERRORS = (
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    BadRequestError,
)

RETRYABLE_ERRORS = (
    ServiceUnavailableError,
    RateLimitError,
    Timeout,
    InternalServerError,
    APIConnectionError,
)


@dataclass(frozen=True, slots=True)
class PromptResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    error: str | None = None


@dataclass
class PromptItem:
    id: str
    nl_input: str
    expected_cnl: list[str] | None = None
    model_output: PromptResult | None = None


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

    try:
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            num_ctx=num_ctx,
            reasoning_effort=reasoning_effort,
            stream=False,
            num_retries=3,  # Retries automatically on error 429, 500, 503 and Timeout
        )
    except FATAL_ERRORS as e:
        CliUI().error(f"Fatal model/API error ({getattr(e, 'status_code', 'N/A')}): {e.message}")
        sys.exit(2)
    except (*RETRYABLE_ERRORS, APIError) as e:
        latency_ms = (perf_counter() - start) * 1000
        err_msg = f"Temporary API error ({getattr(e, 'status_code', 'N/A')}): {e.message}"
        CliUI().error(err_msg)
        return PromptResult(
            text="",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=latency_ms,
            cost_usd=0.0,
            error=err_msg,
        )

    latency_ms = (perf_counter() - start) * 1000

    choice = response.choices[0]
    content = choice.message.content

    raw_text = content.strip() if isinstance(content, str) else ""
    # Removes <think>...</think> blocks if the model ignores reasoning_effort="none"
    text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()

    usage = response.usage
    prompt_tokens = usage.prompt_tokens or 0 if usage else 0
    completion_tokens = usage.completion_tokens or 0 if usage else 0
    total_tokens = usage.total_tokens or 0 if usage else 0

    try:
        cost_usd = float(completion_cost(completion_response=response) or 0.0)
    except Exception:
        # Some local models (Ollama) or :free (OpenRouter) are not mapped
        cost_usd = 0.0

    return PromptResult(
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
    )