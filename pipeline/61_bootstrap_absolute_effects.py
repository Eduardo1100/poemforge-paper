from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, rankdata
from sklearn.linear_model import LinearRegression


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
SCORES = ROOT / "results" / "scores" / "phase_a_eval_scores"
PHASE_A_RESULTS = ROOT / "results" / "phase_a_eval_results"
OUT = ROOT / "results" / "analyses"
HASH_OUT = ROOT / "results" / "hashes"

HUMAN_CONTROLS = [
    "target__Aesthetic_Appeal",
    "target__Clarity",
    "target__Creativity",
    "target__Felt_Valence",
]

SURFACE_CONTROLS = [
    "word_len_calc",
    "char_len_calc",
    "line_count",
]

NLL_CONTROLS = [
    "item_nll_bpb__distilgpt2",
    "item_nll_bpb__gpt2",
    "item_nll_bpb__gpt2-medium",
]

FEATURE_SETS = {
    "none": [],
    "other_human_targets": HUMAN_CONTROLS,
    "other_human_plus_surface": HUMAN_CONTROLS + SURFACE_CONTROLS,
    "stacked": HUMAN_CONTROLS + SURFACE_CONTROLS + NLL_CONTROLS,
}

DEFAULT_METRICS = [
    "score_pref_struct",
]

ALL_METRICS = [
    "score_pref_struct",
    "score_pref_raw",
]

DEFAULT_FEATURE_SET_NAMES = [
    "other_human_targets",
    "other_human_plus_surface",
    "stacked",
]

BASELINE_FILES = [
    SCORES / "supervised_similarity_baselines_tfidf_kfold_surface_chaudhuri_Surprise.csv",
    SCORES / "supervised_similarity_baselines_embedding_kfold_surface_chaudhuri_Surprise.csv",
]

BASELINE_METHOD_MAP = {
    "tfidf": "tfidf_contrast",
    "embedding": "embedding_contrast",
}

COMPRESSION_METHOD = "compression_distilgpt2"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def residualize_rank(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    y_rank = rankdata(y)

    if X.shape[1] == 0:
        return y_rank

    X_rank = np.column_stack([rankdata(X[:, j]) for j in range(X.shape[1])])
    model = LinearRegression()
    model.fit(X_rank, y_rank)
    return y_rank - model.predict(X_rank)


def safe_spearman(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if len(x) < 5:
        return np.nan
    if np.nanstd(x) == 0 or np.nanstd(y) == 0:
        return np.nan

    rho, _ = spearmanr(x, y)
    return float(rho) if np.isfinite(rho) else np.nan


def canonicalize_after_merge(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["target__Surprise"] + HUMAN_CONTROLS:
        if col in df.columns:
            continue

        for alt in [f"{col}_base", f"{col}_rating", f"{col}_x", f"{col}_y"]:
            if alt in df.columns:
                df[col] = df[alt]
                break

    if "target__Surprise" not in df.columns and "target_value" in df.columns:
        df["target__Surprise"] = df["target_value"]

    aliases = {
        "v_pref_raw": ["score_pref_raw"],
        "v_pref_struct": ["score_pref_struct"],
        "v_pref_ctrl": ["score_pref_ctrl"],
        "score_pref_raw": ["v_pref_raw"],
        "score_pref_struct": ["v_pref_struct"],
        "score_pref_ctrl": ["v_pref_ctrl"],
    }

    for canonical, alts in aliases.items():
        if canonical in df.columns:
            continue
        for alt in alts:
            if alt in df.columns:
                df[canonical] = df[alt]
                break

    return df


def load_base() -> pd.DataFrame:
    base = pd.read_csv(DATA / "targets_wide.csv")
    base = base[base["dataset"] == "chaudhuri_2024"].copy()

    keep = [
        "item_id",
        "target__Surprise",
        "target__Aesthetic_Appeal",
        "target__Clarity",
        "target__Creativity",
        "target__Felt_Valence",
    ]
    base = base[keep].copy()

    for obs in ["distilgpt2", "gpt2", "gpt2-medium"]:
        path = PHASE_A_RESULTS / f"item_unconditional_nll_{obs}.csv"
        if not path.exists():
            raise SystemExit(f"Missing NLL file: {path}")

        nll = pd.read_csv(path)
        col = f"item_nll_bpb__{obs}"

        if col not in nll.columns:
            candidates = [c for c in nll.columns if "nll" in c.lower() and "bpb" in c.lower()]
            if len(candidates) == 1:
                nll = nll.rename(columns={candidates[0]: col})
            else:
                raise SystemExit(
                    f"Could not identify NLL column for {obs} in {path}. "
                    f"Columns: {nll.columns.tolist()}"
                )

        base = base.merge(nll[["item_id", col]], on="item_id", how="left")

    return base.sort_values("item_id").reset_index(drop=True)


def load_compression(base: pd.DataFrame) -> pd.DataFrame:
    paths = sorted(
        p for p in SCORES.glob(
            "vscore_distilgpt2_prefcontrast_kfold_surface_chaudhuri_Surprise_foldseed*_seed*_dn8.csv"
        )
        if not p.name.endswith(".correlations.csv")
    )

    rows = []
    for path in paths:
        m = re.search(r"foldseed(\d+)_seed(\d+)_dn8\.csv$", path.name)
        if not m:
            continue

        df = pd.read_csv(path)
        df["fold_seed"] = int(m.group(1))
        df["seed"] = int(m.group(2))
        df["method"] = COMPRESSION_METHOD
        df = df.merge(base, on="item_id", how="left", suffixes=("", "_base"))
        df = canonicalize_after_merge(df)
        rows.append(df)

    if not rows:
        raise SystemExit("No compression score files found.")

    out = pd.concat(rows, ignore_index=True)
    require_columns(out, "compression")
    return out


def load_baselines(base: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for path in BASELINE_FILES:
        if not path.exists():
            raise SystemExit(f"Missing baseline file: {path}")

        df = pd.read_csv(path)
        df["method"] = df["method"].map(BASELINE_METHOD_MAP).fillna(df["method"])
        df = df.merge(base, on="item_id", how="left", suffixes=("", "_base"))
        df = canonicalize_after_merge(df)
        rows.append(df)

    out = pd.concat(rows, ignore_index=True)
    require_columns(out, "baselines")
    return out


def require_columns(df: pd.DataFrame, label: str) -> None:
    required = set(
        [
            "item_id",
            "fold_seed",
            "seed",
            "method",
            "target__Surprise",
            "score_pref_raw",
            "score_pref_struct",
        ]
        + HUMAN_CONTROLS
        + SURFACE_CONTROLS
        + NLL_CONTROLS
    )
    missing = sorted(c for c in required if c not in df.columns)
    if missing:
        raise SystemExit(f"{label} missing required columns: {missing}")


def resample_run(run: pd.DataFrame, sample_item_ids: list[str]) -> pd.DataFrame:
    indexed = run.set_index("item_id", drop=False)
    return indexed.loc[sample_item_ids].reset_index(drop=True)


def metric_rho(run: pd.DataFrame, metric_col: str, feature_controls: list[str]) -> float:
    needed = ["target__Surprise", metric_col] + feature_controls
    run = run.dropna(subset=needed).copy()

    if len(run) < 5:
        return np.nan

    if feature_controls:
        X = run[feature_controls].to_numpy(dtype=float)
    else:
        X = np.zeros((len(run), 0), dtype=float)

    y_resid = residualize_rank(run["target__Surprise"].to_numpy(dtype=float), X)
    m_resid = residualize_rank(run[metric_col].to_numpy(dtype=float), X)

    return safe_spearman(m_resid, y_resid)


def observed_absolute_effects(
    all_scores: pd.DataFrame,
    feature_set_names: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    rows = []

    selected_feature_sets = {name: FEATURE_SETS[name] for name in feature_set_names}

    for method, mdf in all_scores.groupby("method"):
        runs = {
            key: run.sort_values("item_id").reset_index(drop=True)
            for key, run in mdf.groupby(["fold_seed", "seed"])
        }

        for feature_set, controls in selected_feature_sets.items():
            for metric in metrics:
                rhos = []
                for run in runs.values():
                    rho = metric_rho(run, metric, controls)
                    if np.isfinite(rho):
                        rhos.append(rho)

                rows.append({
                    "analysis": "absolute_effect",
                    "method": method,
                    "feature_set": feature_set,
                    "metric": metric,
                    "n_runs": len(rhos),
                    "observed_mean_rho": float(np.mean(rhos)) if rhos else np.nan,
                })

    return pd.DataFrame(rows)


def bootstrap_absolute_effects(
    all_scores: pd.DataFrame,
    item_ids: list[str],
    n_boot: int,
    rng: np.random.Generator,
    feature_set_names: list[str],
    metrics: list[str],
) -> pd.DataFrame:
    records = []

    run_maps = {
        method: {
            key: run.sort_values("item_id").reset_index(drop=True)
            for key, run in mdf.groupby(["fold_seed", "seed"])
        }
        for method, mdf in all_scores.groupby("method")
    }

    item_ids = list(item_ids)
    n_items = len(item_ids)
    selected_feature_sets = {name: FEATURE_SETS[name] for name in feature_set_names}

    for b in range(n_boot):
        sample_ids = rng.choice(item_ids, size=n_items, replace=True).tolist()

        for method, runs in run_maps.items():
            for feature_set, controls in selected_feature_sets.items():
                for metric in metrics:
                    rhos = []

                    for run in runs.values():
                        brun = resample_run(run, sample_ids)
                        rho = metric_rho(brun, metric, controls)
                        if np.isfinite(rho):
                            rhos.append(rho)

                    records.append({
                        "bootstrap_id": b,
                        "analysis": "absolute_effect",
                        "method": method,
                        "feature_set": feature_set,
                        "metric": metric,
                        "boot_mean_rho": float(np.mean(rhos)) if rhos else np.nan,
                        "n_runs": len(rhos),
                    })

        if (b + 1) % max(1, n_boot // 10) == 0:
            print(f"  absolute bootstrap {b + 1}/{n_boot}")

    return pd.DataFrame(records)


def summarize_absolute(observed: pd.DataFrame, boot: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key_cols = ["analysis", "method", "feature_set", "metric"]

    for key, obs_row in observed.groupby(key_cols):
        analysis, method, feature_set, metric = key
        sub = boot[
            (boot["analysis"] == analysis)
            & (boot["method"] == method)
            & (boot["feature_set"] == feature_set)
            & (boot["metric"] == metric)
        ]["boot_mean_rho"].dropna().to_numpy(dtype=float)

        if len(sub) == 0:
            continue

        obs = float(obs_row["observed_mean_rho"].iloc[0])
        ci_low, ci_high = np.percentile(sub, [2.5, 97.5])

        rows.append({
            "analysis": analysis,
            "method": method,
            "feature_set": feature_set,
            "metric": metric,
            "n_runs": int(obs_row["n_runs"].iloc[0]),
            "observed_mean_rho": obs,
            "boot_mean": float(np.mean(sub)),
            "boot_std": float(np.std(sub, ddof=1)),
            "ci95_low": float(ci_low),
            "ci95_high": float(ci_high),
            "p_boot_le_zero": float(np.mean(sub <= 0)),
            "p_boot_ge_zero": float(np.mean(sub >= 0)),
            "n_boot": len(sub),
            "ci_excludes_zero": bool(ci_low > 0 or ci_high < 0),
        })

    return pd.DataFrame(rows)


def write_hashes(paths: list[Path]) -> None:
    HASH_OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in paths:
        df = pd.read_csv(path) if path.suffix == ".csv" else None
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "rows": len(df) if df is not None else None,
            "cols": len(df.columns) if df is not None else None,
            "sha256": sha256_file(path),
        })
    pd.DataFrame(rows).to_csv(HASH_OUT / "bootstrap_absolute_effects_hashes.csv", index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument(
        "--feature-set",
        action="append",
        choices=sorted(FEATURE_SETS),
        help="Feature set to include. Repeatable. Defaults to critique-primary feature sets.",
    )
    ap.add_argument(
        "--metric",
        action="append",
        choices=ALL_METRICS,
        help="Metric to include. Repeatable. Defaults to score_pref_struct.",
    )
    args = ap.parse_args()

    feature_set_names = args.feature_set or DEFAULT_FEATURE_SET_NAMES
    metrics = args.metric or DEFAULT_METRICS

    rng = np.random.default_rng(args.seed)

    base = load_base()
    item_ids = base["item_id"].tolist()

    print(f"Items: {len(item_ids)}")
    print(f"Bootstraps: {args.n_boot}")
    print(f"Feature sets: {feature_set_names}")
    print(f"Metrics: {metrics}")

    comp = load_compression(base)
    baselines = load_baselines(base)
    all_scores = pd.concat([comp, baselines], ignore_index=True, sort=False)

    print(f"Compression rows: {len(comp)}")
    print(f"Baseline rows: {len(baselines)}")
    print(f"All score rows: {len(all_scores)}")

    print("\nObserved absolute effects...")
    observed = observed_absolute_effects(all_scores, feature_set_names, metrics)

    print("\nBootstrap absolute effects...")
    boot = bootstrap_absolute_effects(
        all_scores,
        item_ids,
        args.n_boot,
        rng,
        feature_set_names,
        metrics,
    )

    summary = summarize_absolute(observed, boot)

    OUT.mkdir(parents=True, exist_ok=True)

    observed_path = OUT / "bootstrap_absolute_effects_observed.csv"
    boot_path = OUT / "bootstrap_absolute_effects_samples.csv"
    summary_path = OUT / "bootstrap_absolute_effects_summary.csv"
    manifest_path = OUT / "bootstrap_absolute_effects_manifest.json"

    observed.to_csv(observed_path, index=False)
    boot.to_csv(boot_path, index=False)
    summary.to_csv(summary_path, index=False)

    manifest = {
        "analysis": "absolute_effect",
        "n_boot": args.n_boot,
        "seed": args.seed,
        "inputs": {
            "targets_wide": str(DATA / "targets_wide.csv"),
            "scores": str(SCORES),
            "phase_a_results": str(PHASE_A_RESULTS),
        },
        "outputs": {
            "observed": str(observed_path),
            "samples": str(boot_path),
            "summary": str(summary_path),
        },
        "feature_sets": {name: FEATURE_SETS[name] for name in feature_set_names},
        "metrics": metrics,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_hashes([observed_path, boot_path, summary_path])

    print("\nAbsolute effect summary:")
    show = summary[
        (summary["metric"] == "score_pref_struct")
        & (summary["feature_set"].isin(["other_human_targets", "other_human_plus_surface", "stacked"]))
    ].sort_values(["feature_set", "method"])
    print(show.to_string(index=False))

    print(f"\nWrote {observed_path}")
    print(f"Wrote {boot_path}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
