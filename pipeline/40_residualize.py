from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
from sklearn.linear_model import LinearRegression


ROOT = Path(__file__).resolve().parents[1]

SCORE_DIR = ROOT / "results" / "scores" / "phase_a_eval_scores"
ANALYSES_DIR = ROOT / "results" / "analyses"
HASH_DIR = ROOT / "results" / "hashes"

TARGETS_WIDE = ROOT / "data" / "processed" / "targets_wide.csv"
SURFACE_FEATURES = ROOT / "results" / "controls" / "surface_features.csv"

TARGET_COL = "target__Surprise"

OTHER_HUMAN_CONTROLS = [
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

COMPRESSION_SURPRISE_PATTERN = (
    "vscore_distilgpt2_prefcontrast_kfold_surface_chaudhuri_Surprise_"
    "foldseed*_seed*_dn8.csv"
)

BASELINE_FILES = {
    "embedding": "supervised_similarity_baselines_embedding_kfold_surface_chaudhuri_Surprise.csv",
    "tfidf": "supervised_similarity_baselines_tfidf_kfold_surface_chaudhuri_Surprise.csv",
}

SCORE_COLUMNS_BY_READOUT = {
    "compression": ["v_pref_raw", "v_pref_struct"],
    "embedding": ["score_pref_raw", "score_pref_struct"],
    "tfidf": ["score_pref_raw", "score_pref_struct"],
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_shape(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() != ".csv":
        return None, None
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0
        return sum(1 for _ in reader), len(header)


def rank_residualize(y: pd.Series, controls: pd.DataFrame | None = None) -> np.ndarray:
    mask = y.notna().to_numpy()

    if controls is not None and controls.shape[1] > 0:
        mask = mask & controls.notna().all(axis=1).to_numpy()

    y_valid = y.to_numpy()[mask]
    y_rank = rankdata(y_valid, method="average").astype(float)

    out = np.full(len(y), np.nan, dtype=float)

    if controls is None or controls.shape[1] == 0:
        out[mask] = y_rank - np.mean(y_rank)
        return out

    x_valid = controls.loc[mask].copy()
    x_rank_cols = []
    for col in x_valid.columns:
        x_rank_cols.append(rankdata(x_valid[col].to_numpy(), method="average"))

    x_rank = np.vstack(x_rank_cols).T.astype(float)

    model = LinearRegression()
    model.fit(x_rank, y_rank)
    pred = model.predict(x_rank)

    out[mask] = y_rank - pred
    return out


def residual_spearman(df: pd.DataFrame, score_col: str, controls: list[str]) -> tuple[float, float, int]:
    needed = ["item_id", TARGET_COL, score_col] + controls
    sub = df[[c for c in needed if c in df.columns]].copy()

    missing = [c for c in [TARGET_COL, score_col] + controls if c not in sub.columns]
    if missing:
        return np.nan, np.nan, 0

    control_df = sub[controls] if controls else None

    y_resid = rank_residualize(sub[TARGET_COL], control_df)
    s_resid = rank_residualize(sub[score_col], control_df)

    mask = np.isfinite(y_resid) & np.isfinite(s_resid)
    if mask.sum() < 4:
        return np.nan, np.nan, int(mask.sum())

    rho, p = spearmanr(y_resid[mask], s_resid[mask])
    return float(rho), float(p), int(mask.sum())


def parse_run_from_filename(filename: str) -> tuple[int | None, int | None]:
    fold = re.search(r"foldseed(\d+)", filename)
    seed = re.search(r"_seed(\d+)_", filename)
    fold_seed = int(fold.group(1)) if fold else None
    sampling_seed = int(seed.group(1)) if seed else None
    return fold_seed, sampling_seed


def load_targets_and_controls() -> pd.DataFrame:
    if not TARGETS_WIDE.exists():
        raise FileNotFoundError(f"Missing {TARGETS_WIDE}. Run Stage 00 first.")

    targets = pd.read_csv(TARGETS_WIDE)
    targets = targets[targets["dataset"] == "chaudhuri_2024"].copy()

    cols = ["item_id", TARGET_COL] + OTHER_HUMAN_CONTROLS
    keep = [c for c in cols if c in targets.columns]
    out = targets[keep].copy()

    if SURFACE_FEATURES.exists():
        surface = pd.read_csv(SURFACE_FEATURES)
        surface_keep = ["item_id"] + [c for c in SURFACE_CONTROLS if c in surface.columns]
        out = out.merge(surface[surface_keep], on="item_id", how="left")

    return out


def canonical_score_col(readout: str, score_col: str) -> str:
    if readout == "compression":
        return score_col.replace("v_", "score_")
    return score_col


def analyze_one_run(
    readout: str,
    run_df: pd.DataFrame,
    target_controls: pd.DataFrame,
    fold_seed: int | None,
    sampling_seed: int | None,
    source_file: str,
) -> list[dict]:
    df = run_df.merge(target_controls, on="item_id", how="left")

    feature_sets = {
        "none": [],
        "other_human_targets": OTHER_HUMAN_CONTROLS,
        "other_human_plus_surface": OTHER_HUMAN_CONTROLS + SURFACE_CONTROLS,
    }

    rows: list[dict] = []
    for raw_score_col in SCORE_COLUMNS_BY_READOUT[readout]:
        if raw_score_col not in df.columns:
            continue

        metric = canonical_score_col(readout, raw_score_col)

        for feature_set, controls in feature_sets.items():
            available_controls = [c for c in controls if c in df.columns]
            rho, p, n = residual_spearman(df, raw_score_col, available_controls)
            rows.append(
                {
                    "readout": readout,
                    "metric": metric,
                    "source_score_col": raw_score_col,
                    "feature_set": feature_set,
                    "rho": rho,
                    "p_value": p,
                    "n_items": n,
                    "fold_seed": fold_seed,
                    "seed": sampling_seed,
                    "source_file": source_file,
                }
            )

    return rows


def analyze_compression_runs(target_controls: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []

    files = sorted(SCORE_DIR.glob(COMPRESSION_SURPRISE_PATTERN))
    if not files:
        raise FileNotFoundError(
            f"No compression Surprise K-fold score files matching {COMPRESSION_SURPRISE_PATTERN}"
        )

    for path in files:
        if ".correlations." in path.name:
            continue

        fold_seed, seed = parse_run_from_filename(path.name)
        df = pd.read_csv(path)

        if "item_id" not in df.columns:
            continue

        rows.extend(
            analyze_one_run(
                readout="compression",
                run_df=df,
                target_controls=target_controls,
                fold_seed=fold_seed,
                sampling_seed=seed,
                source_file=path.name,
            )
        )

    return rows


def infer_baseline_run_cols(df: pd.DataFrame) -> tuple[str, str]:
    fold_candidates = ["fold_seed", "foldseed", "cv_fold_seed"]
    seed_candidates = ["seed", "sampling_seed", "run_seed"]

    fold_col = next((c for c in fold_candidates if c in df.columns), None)
    seed_col = next((c for c in seed_candidates if c in df.columns), None)

    if fold_col is None:
        for c in df.columns:
            if "fold" in c.lower() and "seed" in c.lower():
                fold_col = c
                break

    if seed_col is None:
        for c in df.columns:
            low = c.lower()
            if low == "seed" or "sampling_seed" in low or "run_seed" in low:
                seed_col = c
                break

    if fold_col is None or seed_col is None:
        raise ValueError(
            "Could not infer baseline run columns. "
            f"Columns: {list(df.columns)}"
        )

    return fold_col, seed_col


def analyze_baseline_runs(target_controls: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []

    for readout, filename in BASELINE_FILES.items():
        path = SCORE_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing baseline score file: {path}")

        df = pd.read_csv(path)

        if "item_id" not in df.columns:
            raise ValueError(f"{path} must contain item_id.")

        fold_col, seed_col = infer_baseline_run_cols(df)

        for (fold_seed, seed), run_df in df.groupby([fold_col, seed_col], dropna=False):
            rows.extend(
                analyze_one_run(
                    readout=readout,
                    run_df=run_df,
                    target_controls=target_controls,
                    fold_seed=int(fold_seed) if pd.notna(fold_seed) else None,
                    sampling_seed=int(seed) if pd.notna(seed) else None,
                    source_file=path.name,
                )
            )

    return rows


def summarize_runlevel(long_df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["readout", "metric", "feature_set"]

    rows = []
    for key, sub in long_df.groupby(group_cols, dropna=False):
        vals = sub["rho"].dropna().to_numpy()

        if len(vals) == 0:
            mean_rho = std_rho = min_rho = max_rho = np.nan
            sig_05 = 0
        else:
            mean_rho = float(np.mean(vals))
            std_rho = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            min_rho = float(np.min(vals))
            max_rho = float(np.max(vals))
            sig_05 = int(((sub["p_value"] < 0.05) & sub["rho"].notna()).sum())

        rows.append(
            {
                "readout": key[0],
                "metric": key[1],
                "feature_set": key[2],
                "n_runs": int(sub["rho"].notna().sum()),
                "mean_rho": mean_rho,
                "std_rho": std_rho,
                "min_rho": min_rho,
                "max_rho": max_rho,
                "sig_05": sig_05,
            }
        )

    return pd.DataFrame(rows).sort_values(["feature_set", "metric", "readout"])


def make_readout_convergence(summary: pd.DataFrame) -> pd.DataFrame:
    sub = summary[
        (summary["metric"] == "score_pref_struct")
        & (summary["feature_set"].isin(["none", "other_human_targets", "other_human_plus_surface"]))
    ].copy()

    pivot = sub.pivot_table(
        index=["feature_set", "metric"],
        columns="readout",
        values="mean_rho",
        aggfunc="first",
    ).reset_index()

    for col in ["compression", "embedding", "tfidf"]:
        if col not in pivot.columns:
            pivot[col] = np.nan

    pivot["compression_minus_embedding"] = pivot["compression"] - pivot["embedding"]
    pivot["compression_minus_tfidf"] = pivot["compression"] - pivot["tfidf"]

    return pivot[
        [
            "feature_set",
            "metric",
            "compression",
            "embedding",
            "tfidf",
            "compression_minus_embedding",
            "compression_minus_tfidf",
        ]
    ]


def collect_generic_d_correlation_summaries() -> pd.DataFrame:
    files = sorted(
        list(SCORE_DIR.glob("*gutenberg_accessible*.correlations.csv"))
        + list(SCORE_DIR.glob("*gutenberg_formal*.correlations.csv"))
    )

    rows = []
    for path in files:
        try:
            df = pd.read_csv(path)
        except Exception:
            continue

        # Preserve original columns while adding provenance.
        for _, row in df.iterrows():
            out = row.to_dict()
            out["source_file"] = path.name
            out["domain_variant"] = (
                "accessible" if "accessible" in path.name.lower()
                else "formal" if "formal" in path.name.lower()
                else "unknown"
            )
            out["control_variant"] = (
                "matchedctrl" if "matchedctrl" in path.name.lower()
                else "wordctrl" if "wordctrl" in path.name.lower()
                else "unknown"
            )
            fold_seed, seed = parse_run_from_filename(path.name)
            out["seed"] = seed
            rows.append(out)

    return pd.DataFrame(rows)


def write_hash_csv(entries: list[dict]) -> None:
    HASH_DIR.mkdir(parents=True, exist_ok=True)
    out = HASH_DIR / "analysis_hashes.csv"

    fieldnames = [
        "status",
        "destination",
        "sha256",
        "n_rows",
        "n_cols",
        "note",
    ]

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            writer.writerow({k: e.get(k, "") for k in fieldnames})


def hash_entry(path: Path, note: str) -> dict:
    rows, cols = csv_shape(path)
    return {
        "status": "generated",
        "destination": str(path),
        "sha256": sha256_file(path),
        "n_rows": rows,
        "n_cols": cols,
        "note": note,
    }


def main() -> None:
    ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    target_controls = load_targets_and_controls()

    long_rows = []
    long_rows.extend(analyze_compression_runs(target_controls))
    long_rows.extend(analyze_baseline_runs(target_controls))

    long_df = pd.DataFrame(long_rows)
    long_path = ANALYSES_DIR / "runlevel_readout_correlations_long.csv"
    long_df.to_csv(long_path, index=False)

    summary = summarize_runlevel(long_df)
    summary_path = ANALYSES_DIR / "runlevel_readout_summary.csv"
    summary.to_csv(summary_path, index=False)

    convergence = make_readout_convergence(summary)
    convergence_path = ANALYSES_DIR / "readout_convergence_summary.csv"
    convergence.to_csv(convergence_path, index=False)

    generic = collect_generic_d_correlation_summaries()
    generic_path = ANALYSES_DIR / "generic_d_correlation_summaries.csv"
    generic.to_csv(generic_path, index=False)

    manifest = {
        "stage": "40_residualize",
        "target_col": TARGET_COL,
        "score_source_dir": str(SCORE_DIR),
        "outputs": {
            "runlevel_long": str(long_path),
            "runlevel_summary": str(summary_path),
            "readout_convergence_summary": str(convergence_path),
            "generic_d_correlation_summaries": str(generic_path),
        },
        "important_note": (
            "This stage recomputes run-level residualized Spearman summaries from "
            "frozen score artifacts. It currently includes none, other-human, and "
            "other-human-plus-surface controls. Full stacked NLL-controlled analyses "
            "and poem-level bootstrap are handled in later stages."
        ),
    }

    manifest_path = ANALYSES_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    entries = [
        hash_entry(long_path, "Long-form run-level residualized correlations."),
        hash_entry(summary_path, "Summary of run-level residualized correlations."),
        hash_entry(convergence_path, "Readout convergence summary across compression, TF-IDF, and embeddings."),
        hash_entry(generic_path, "Copied/combined generic-D correlation summaries from Phase A artifacts."),
    ]

    write_hash_csv(entries)

    print("Prepared analysis artifacts:")
    for e in entries:
        print(f"  {e['destination']} rows={e['n_rows']} cols={e['n_cols']}")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {HASH_DIR / 'analysis_hashes.csv'}")

    print("\nReadout convergence preview:")
    print(convergence.to_string(index=False))


if __name__ == "__main__":
    main()
