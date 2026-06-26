from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from poemforge_paper.readouts.base import Readout, ScoreResult


class TfidfReadout(Readout):
    name = "tfidf"

    def __init__(self, ngram_range=(1, 2), sublinear_tf=True):
        self.vectorizer = TfidfVectorizer(ngram_range=ngram_range, sublinear_tf=sublinear_tf)
        self.pos_vec = None
        self.neg_vec = None

    def fit_domain(self, positive_examples: list[str], negative_examples: list[str], metadata=None) -> "TfidfReadout":
        corpus = positive_examples + negative_examples
        x = self.vectorizer.fit_transform(corpus)
        n_pos = len(positive_examples)
        self.pos_vec = x[:n_pos]
        self.neg_vec = x[n_pos:]
        return self

    def score_candidate(self, candidate_text: str, candidate_id: str | None = None) -> ScoreResult:
        if self.pos_vec is None or self.neg_vec is None:
            raise RuntimeError("TfidfReadout must be fit before scoring.")
        cand = self.vectorizer.transform([candidate_text])
        pos = float(np.mean(cosine_similarity(cand, self.pos_vec)))
        neg = float(np.mean(cosine_similarity(cand, self.neg_vec)))
        return ScoreResult(
            readout=self.name,
            candidate_id=candidate_id,
            score_pref_raw=pos - neg,
            metadata={"pos_similarity": pos, "neg_similarity": neg},
        )
