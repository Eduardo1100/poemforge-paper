from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreResult:
    readout: str
    candidate_id: str | None
    score_pref_raw: float | None = None
    score_pref_ctrl: float | None = None
    score_pref_struct: float | None = None
    metadata: dict[str, Any] | None = None


class Readout(ABC):
    """Shared interface for all domain readouts.

    The paper's methodological claim is that compression, TF-IDF, and embeddings
    are different lenses over the same human-shaped domain D. This interface keeps
    those comparisons fair by construction.
    """

    name: str

    @abstractmethod
    def fit_domain(self, positive_examples: list[str], negative_examples: list[str], metadata=None) -> "Readout":
        raise NotImplementedError

    @abstractmethod
    def score_candidate(self, candidate_text: str, candidate_id: str | None = None) -> ScoreResult:
        raise NotImplementedError

    def score_batch(self, candidates: list[dict[str, str]]) -> list[ScoreResult]:
        return [
            self.score_candidate(c["text"], candidate_id=c.get("item_id"))
            for c in candidates
        ]
