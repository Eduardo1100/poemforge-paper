from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LinearRegression


def rank_residualize(y: pd.Series, controls: pd.DataFrame | None = None) -> np.ndarray:
    """Rank-transform y and residualize against rank-transformed controls."""
    y_rank = rankdata(y.to_numpy(), method="average")

    if controls is None or controls.shape[1] == 0:
        return y_rank - np.mean(y_rank)

    x = controls.copy()
    x = x.apply(lambda col: rankdata(col.to_numpy(), method="average"), axis=0, result_type="expand")
    x = np.asarray(x, dtype=float)

    model = LinearRegression()
    model.fit(x, y_rank)
    pred = model.predict(x)
    return y_rank - pred
