"""Registry of the available strategies.

Each strategy is referenced by "module:Class" and imported only when chosen, so that
heavy dependencies (e.g. sentence-transformers for "ExampleRAGStrategy") are loaded only if needed.
"""
from importlib import import_module

from nl2cnl.strategies.base import StrategyOptions, SystemPromptStrategy

_REGISTRY = {
    "inctx": "nl2cnl.strategies.in_context:InContextStrategy",
    "example": "nl2cnl.strategies.example_rag:ExampleRAGStrategy",
    "subg": "nl2cnl.strategies.subgrammar_rag:SubgrammarRAGStrategy"
}
AVAILABLE_STRATEGIES = list(_REGISTRY)

__all__ = ["AVAILABLE_STRATEGIES", "StrategyOptions", "SystemPromptStrategy", "get_strategy"]


def get_strategy(name: str, options: StrategyOptions | None = None) -> SystemPromptStrategy:
    module, cls = _REGISTRY[name].split(":")
    return getattr(import_module(module), cls)(options or StrategyOptions())
