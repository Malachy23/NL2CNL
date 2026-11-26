from importlib import import_module

_REGISTRY = {
    "inctx": "nl2cnl.strategies.in_context:InContextStrategy",
    "example": "nl2cnl.strategies.example_rag:ExampleRAGStrategy",
}
AVAILABLE_STRATEGIES = list(_REGISTRY)

def get_strategy(name: str):
    module, cls = _REGISTRY[name].split(":")
    return getattr(import_module(module), cls)()

# structuring the imports this way prevents importing unnecessary packages used only by other strategies, thus improving performance