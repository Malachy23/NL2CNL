from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptResult:
    """
    Encapsules the response of a model (text) and various technical details. In particular, the number of tokens used (*_tokens),
    the time it took to generate an answer (latency_ms), the cost of the call (cost_usd, set to 0 when running local models), and
    the error message if something went wrong. 
    """
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    error: str | None = None


@dataclass
class PromptItem:
    """ 
    Used to transform input from any source (-t, -i, -b) into a universal format that the pipeline can
    treat uniformly.

    - id: string identification of the query
    - nl_input: user query
    - expected_cnl: expected translation (used only when run with -b)
    - model_output: answer from the chosen model and some technical values  
    """
    id: str
    nl_input: str
    expected_cnl: list[str] | None = None
    model_output: PromptResult | None = None