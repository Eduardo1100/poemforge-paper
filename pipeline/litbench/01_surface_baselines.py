from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "results" / "litbench"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_SAMPLE = OUT_DIR / "SAA-Lab__LitBench-Train__train__sample.csv"
TRAIN_CACHE = OUT_DIR / "litbench_train_cached.csv"


WORD_RE = re.compile(r"\b\w+\b", flags=re.UNICODE)


def tokenize(text: str) -> list[str]:
    return WORD_RE.findall(str(text).lower())


def features(text: str) -> dict:
    s = str(text)
    toks = tokenize(s)
    n_words = len(toks)
    n_chars = len(s)
    uniq = len(set(toks))
    return {
        "chars": n_chars,
        "words": n_words,
        "type_token_ratio": uniq / n_words if n_words else np.nan,
        "avg_word_len": float(np.mean([len(t) for t in toks])) if toks else np.nan,
        "punct_count": sum(1 for ch in s if not ch.isalnum() and not ch.isspace()),
        "newline_count": s.count("\n"),
    }


def load_train() -> pd.DataFrame:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: datasets. Install with:\n"
            "  python -m pip install datasets pyarrow\n"
        ) from exc

    if TRAIN_CACHE.exists():
        return pd.read_csv(TRAIN_CACHE)

    ds = load_dataset("SAA-Lab/LitBench-Train")
    split = next(iter(ds.keys()))
    df = ds[split].to_pandas()
    df.to_csv(TRAIN_CACHE, index=False)
    return df


def bootstrap_acc(correct: np.ndarray, n_boot: int = 5000, seed: int = 123) -> dict:
    rng = np.random.default_rng(seed)
    correct = np.asarray(correct, dtype=float)
    n = len(correct)
    samples = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        samples.append(float(np.mean(correct[idx])))
    arr = np.asarray(samples)
    return {
        "accuracy": float(np.mean(correct)),
        "ci95_low": float(np.quantile(arr, 0.025)),
        "ci95_high": float(np.quantile(arr, 0.975)),
        "n": int(n),
        "n_boot": n_boot,
    }


def main() -> None:
    df = load_train()

    required = {"chosen_story", "rejected_story"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    rows = []
    feature_rows = []

    for i, row in df.iterrows():
        ch = features(row["chosen_story"])
        rj = features(row["rejected_story"])

        record = {"row_id": i}
        for k, v in ch.items():
            record[f"chosen_{k}"] = v
        for k, v in rj.items():
            record[f"rejected_{k}"] = v
        if "chosen_upvotes" in df.columns:
            record["chosen_upvotes"] = row["chosen_upvotes"]
        if "rejected_upvotes" in df.columns:
            record["rejected_upvotes"] = row["rejected_upvotes"]
        feature_rows.append(record)

    feat = pd.DataFrame(feature_rows)

    tests = {
        "prefer_more_chars": feat["chosen_chars"] > feat["rejected_chars"],
        "prefer_fewer_chars": feat["chosen_chars"] < feat["rejected_chars"],
        "prefer_more_words": feat["chosen_words"] > feat["rejected_words"],
        "prefer_fewer_words": feat["chosen_words"] < feat["rejected_words"],
        "prefer_higher_ttr": feat["chosen_type_token_ratio"] > feat["rejected_type_token_ratio"],
        "prefer_lower_ttr": feat["chosen_type_token_ratio"] < feat["rejected_type_token_ratio"],
        "prefer_higher_avg_word_len": feat["chosen_avg_word_len"] > feat["rejected_avg_word_len"],
        "prefer_lower_avg_word_len": feat["chosen_avg_word_len"] < feat["rejected_avg_word_len"],
        "prefer_more_punct": feat["chosen_punct_count"] > feat["rejected_punct_count"],
        "prefer_less_punct": feat["chosen_punct_count"] < feat["rejected_punct_count"],
        "prefer_more_newlines": feat["chosen_newline_count"] > feat["rejected_newline_count"],
        "prefer_fewer_newlines": feat["chosen_newline_count"] < feat["rejected_newline_count"],
    }

    if {"chosen_upvotes", "rejected_upvotes"} <= set(feat.columns):
        tests["prefer_more_upvotes_sanity"] = feat["chosen_upvotes"] > feat["rejected_upvotes"]

    for name, pred in tests.items():
        valid = pred.notna().to_numpy()
        correct = pred.to_numpy(dtype=bool)[valid]
        stat = bootstrap_acc(correct)
        rows.append({"baseline": name, **stat})

    out = pd.DataFrame(rows).sort_values("accuracy", ascending=False)
    feat_path = OUT_DIR / "litbench_train_surface_features.csv"
    out_path = OUT_DIR / "litbench_train_surface_baselines.csv"
    manifest_path = OUT_DIR / "litbench_train_surface_baselines_manifest.json"

    feat.to_csv(feat_path, index=False)
    out.to_csv(out_path, index=False)
    manifest_path.write_text(
        json.dumps(
            {
                "dataset": "SAA-Lab/LitBench-Train",
                "analysis": "surface baselines for chosen-vs-rejected pair prediction",
                "outputs": [str(feat_path), str(out_path)],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(out.to_string(index=False))
    print(f"Wrote {feat_path}")
    print(f"Wrote {out_path}")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
