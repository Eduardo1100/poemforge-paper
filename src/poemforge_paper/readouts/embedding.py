from __future__ import annotations

from poemforge_paper.readouts.base import Readout, ScoreResult


class EmbeddingReadout(Readout):
    name = "embedding"

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.pos_emb = None
        self.neg_emb = None

    def fit_domain(self, positive_examples: list[str], negative_examples: list[str], metadata=None) -> "EmbeddingReadout":
        raise NotImplementedError(
            "Port the existing sentence-transformers embedding baseline here. "
            "Keep the same fold/domain semantics as TF-IDF and compression."
        )

    def score_candidate(self, candidate_text: str, candidate_id: str | None = None) -> ScoreResult:
        raise NotImplementedError
