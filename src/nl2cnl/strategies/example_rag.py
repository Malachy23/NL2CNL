from pathlib import Path
from numpy import argsort
from sentence_transformers import SentenceTransformer
from transformers.utils import logging

from nl2cnl.prompts import EXAMPLE_RAG_SYSTEM_PROMPT
from nl2cnl.strategies.base import Example, StrategyOptions, SystemPromptStrategy

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class ExampleRAGStrategy(SystemPromptStrategy):
    """This strategy leaves the grammar specification untouched, but produces an embedding of the provided examples
    that are then compared to the user prompt in order to retrieve the top_k most relevant ones to augment the system prompt.
    Providing examples is mandatory to use this strategy.
    """

    def __init__(self, options: StrategyOptions):
        super().__init__(options)

        logging.disable_progress_bar()  # Hides the "Loading weights" bar, which ruined CliUI aesthetic

        try:
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, device="cpu", local_files_only=True)
        except OSError:  # Downloads it if not previously installed
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")


    def setup(self, specification_path: Path, examples_path: Path | None) -> None:
        super().setup(specification_path, examples_path)

        # Embeddings are computed once here, not at every prompt
        self.examples_embedding = self.embedding_model.encode(
            [example["nl_input"] for example in self.examples],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def get_system_prompt(self, user_prompt: str) -> str:
        chosen_examples: list[Example] = []

        if self.examples:
            user_prompt_embedding = self.embedding_model.encode(user_prompt, normalize_embeddings=True)
            scores = self.examples_embedding @ user_prompt_embedding  # Cosine similarity (vectors are normalized)
            best_idx = argsort(scores)[::-1][: self.options.top_k]
            chosen_examples = [self.examples[idx] for idx in best_idx]

        return EXAMPLE_RAG_SYSTEM_PROMPT.format(
            specification=self.specification,
            examples=self._format_examples(chosen_examples),
        )
