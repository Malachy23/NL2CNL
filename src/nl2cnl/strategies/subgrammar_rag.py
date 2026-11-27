from pathlib import Path

from nl2cnl.loaders import load_yaml
from nl2cnl.strategies.base import SystemPromptStrategy


class SubgrammarRAGStrategy(SystemPromptStrategy):
    def __init__(self, options):
        super().__init__(options)

    def _load_specification(self, specification_path: Path) -> None:
        spec_data = load_yaml(specification_path)
        print(spec_data)

    def _load_examples(self, examples_path):
        super()._load_examples(examples_path)

    def setup(self, specification_path, examples_path):
        super().setup(specification_path, examples_path)

    def get_system_prompt(self, user_prompt):
        return "ciao"