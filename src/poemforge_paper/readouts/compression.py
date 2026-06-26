from __future__ import annotations

from poemforge_paper.readouts.base import Readout, ScoreResult


class CompressionReadout(Readout):
    name = "compression"

    def __init__(self, model_name: str = "distilgpt2"):
        self.model_name = model_name

    def fit_domain(self, positive_examples: list[str], negative_examples: list[str], metadata=None) -> "CompressionReadout":
        raise NotImplementedError(
            "Port the final canonical compression scoring code here. "
            "Invariant: score held-out D, not the candidate itself."
        )

    def score_candidate(self, candidate_text: str, candidate_id: str | None = None) -> ScoreResult:
        raise NotImplementedError
