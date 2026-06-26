from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

PHASE_A_RESULTS = ROOT / "results" / "phase_a_eval_results"
ANALYSES_DIR = ROOT / "results" / "analyses"
HASH_DIR = ROOT / "results" / "hashes"

BOOTSTRAP_SUMMARY = PHASE_A_RESULTS / "poem_level_bootstrap_summary.csv"
BOOTSTRAP_OBSERVED = PHASE_A_RESULTS / "poem_level_bootstrap_observed.csv"
BOOTSTRAP_SAMPLES = PHASE_A_RESULTS / "poem_level_bootstrap_samples.csv"


KEY_BOOTSTRAP_ROWS = [
    {
        "claim_id": "B1",
        "analysis": "compression_vs_baseline",
        "comparison_contains": "compression_distilgpt2_minus_embedding",
        "feature_set": "other_human_targets",
        "metric": "score_pref_struct",
        "paper_role": "Compression vs embedding, partially controlled structural target.",
    },
    {
        "claim_id": "B2",
        "analysis": "compression_vs_baseline",
        "comparison_contains": "compression_distilgpt2_minus_tfidf",
        "feature_set": "other_human_targets",
        "metric": "score_pref_struct",
        "paper_role": "Compression vs TF-IDF, partially controlled structural target.",
    },
    {
        "claim_id": "B3",
        "analysis": "compression_vs_baseline",
        "comparison_contains": "compression_distilgpt2_minus_embedding",
        "feature_set": "stacked",
        "metric": "score_pref_struct",
        "paper_role": "Compression vs embedding, fully stacked structural target.",
    },
    {
        "claim_id": "B4",
        "analysis": "compression_vs_baseline",
        "comparison_contains": "compression_distilgpt2_minus_tfidf",
        "feature_set": "stacked",
        "metric": "score_pref_struct",
        "paper_role": "Compression vs TF-IDF, fully stacked structural target.",
    },
    {
        "claim_id": "B5",
        "analysis": "matched_other_diagnostic",
        "comparison_contains": "struct_matched_other_minus_raw_plus_ctrl_surface_nll",
        "feature_set": "other_human_targets",
        "metric": "variant_rho",
        "paper_role": "Matched-other vs explicit normalization, partially controlled.",
    },
    {
        "claim_id": "B6",
        "analysis": "matched_other_diagnostic",
        "comparison_contains": "struct_matched_other_minus_raw_plus_ctrl_surface_nll",
        "feature_set": "stacked",
        "metric": "variant_rho",
        "paper_role": "Matched-other vs explicit normalization, fully stacked.",
    },
]


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


def require_files() -> None:
    for path in [BOOTSTRAP_SUMMARY, BOOTSTRAP_OBSERVED, BOOTSTRAP_SAMPLES]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run pipeline/50_permutation.py first."
            )


def ci_interpretation(row: pd.Series) -> str:
    low = float(row["ci95_low"])
    high = float(row["ci95_high"])
    diff = float(row["observed_mean_diff"])

    if low > 0:
        return "CI excludes zero; positive difference resolved."
    if high < 0:
        return "CI excludes zero; negative difference resolved."
    if diff > 0:
        return "Point estimate positive, but CI includes zero; unresolved at item level."
    if diff < 0:
        return "Point estimate negative, but CI includes zero; unresolved at item level."
    return "Point estimate near zero; CI includes zero."


def select_key_rows(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []

    required_cols = {
        "analysis",
        "comparison",
        "feature_set",
        "metric",
        "observed_mean_diff",
        "ci95_low",
        "ci95_high",
    }

    missing = required_cols - set(summary.columns)
    if missing:
        raise ValueError(
            f"Bootstrap summary missing required columns: {sorted(missing)}. "
            f"Available columns: {list(summary.columns)}"
        )

    for spec in KEY_BOOTSTRAP_ROWS:
        mask = (
            (summary["analysis"] == spec["analysis"])
            & summary["comparison"].astype(str).str.contains(spec["comparison_contains"], regex=False)
            & (summary["feature_set"] == spec["feature_set"])
            & (summary["metric"] == spec["metric"])
        )

        sub = summary[mask].copy()

        if len(sub) != 1:
            rows.append(
                {
                    "claim_id": spec["claim_id"],
                    "paper_role": spec["paper_role"],
                    "analysis": spec["analysis"],
                    "comparison_query": spec["comparison_contains"],
                    "feature_set": spec["feature_set"],
                    "metric": spec["metric"],
                    "status": f"selection_error_n={len(sub)}",
                }
            )
            continue

        row = sub.iloc[0].to_dict()
        row["claim_id"] = spec["claim_id"]
        row["paper_role"] = spec["paper_role"]
        row["status"] = "selected"
        row["interpretation"] = ci_interpretation(pd.Series(row))
        rows.append(row)

    out = pd.DataFrame(rows)

    preferred_cols = [
        "claim_id",
        "paper_role",
        "status",
        "analysis",
        "comparison",
        "feature_set",
        "metric",
        "observed_mean_diff",
        "boot_mean",
        "boot_std",
        "ci95_low",
        "ci95_high",
        "p_boot_le_zero",
        "p_boot_ge_zero",
        "n_boot",
        "ci_excludes_zero",
        "interpretation",
    ]

    existing = [c for c in preferred_cols if c in out.columns]
    rest = [c for c in out.columns if c not in existing]
    return out[existing + rest]


def make_manuscript_bootstrap_table(key_rows: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _, r in key_rows.iterrows():
        if r.get("status") != "selected":
            rows.append(
                {
                    "claim_id": r.get("claim_id"),
                    "comparison": r.get("paper_role"),
                    "observed_diff": "",
                    "ci95": "",
                    "n_boot": "",
                    "paper_interpretation": "Selection error; inspect bootstrap source.",
                }
            )
            continue

        rows.append(
            {
                "claim_id": r["claim_id"],
                "comparison": r["paper_role"],
                "observed_diff": round(float(r["observed_mean_diff"]), 6),
                "ci95": f"[{float(r['ci95_low']):+.6f}, {float(r['ci95_high']):+.6f}]",
                "n_boot": int(r["n_boot"]) if pd.notna(r.get("n_boot")) else "",
                "paper_interpretation": r["interpretation"],
            }
        )

    return pd.DataFrame(rows)


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


def write_hash_csv(entries: list[dict]) -> None:
    HASH_DIR.mkdir(parents=True, exist_ok=True)
    out = HASH_DIR / "bootstrap_hashes.csv"

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


def main() -> None:
    require_files()

    ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    summary = pd.read_csv(BOOTSTRAP_SUMMARY)

    key_rows = select_key_rows(summary)
    key_rows_path = ANALYSES_DIR / "bootstrap_key_claims.csv"
    key_rows.to_csv(key_rows_path, index=False)

    manuscript_table = make_manuscript_bootstrap_table(key_rows)
    manuscript_path = ANALYSES_DIR / "bootstrap_manuscript_table.csv"
    manuscript_table.to_csv(manuscript_path, index=False)

    bootstrap_file_summary = pd.DataFrame(
        [
            {
                "artifact": "poem_level_bootstrap_summary",
                "path": str(BOOTSTRAP_SUMMARY),
                "n_rows": csv_shape(BOOTSTRAP_SUMMARY)[0],
                "n_cols": csv_shape(BOOTSTRAP_SUMMARY)[1],
                "sha256": sha256_file(BOOTSTRAP_SUMMARY),
            },
            {
                "artifact": "poem_level_bootstrap_observed",
                "path": str(BOOTSTRAP_OBSERVED),
                "n_rows": csv_shape(BOOTSTRAP_OBSERVED)[0],
                "n_cols": csv_shape(BOOTSTRAP_OBSERVED)[1],
                "sha256": sha256_file(BOOTSTRAP_OBSERVED),
            },
            {
                "artifact": "poem_level_bootstrap_samples",
                "path": str(BOOTSTRAP_SAMPLES),
                "n_rows": csv_shape(BOOTSTRAP_SAMPLES)[0],
                "n_cols": csv_shape(BOOTSTRAP_SAMPLES)[1],
                "sha256": sha256_file(BOOTSTRAP_SAMPLES),
            },
        ]
    )

    file_summary_path = ANALYSES_DIR / "bootstrap_file_summary.csv"
    bootstrap_file_summary.to_csv(file_summary_path, index=False)

    manifest = {
        "stage": "60_bootstrap",
        "source_files": {
            "summary": str(BOOTSTRAP_SUMMARY),
            "observed": str(BOOTSTRAP_OBSERVED),
            "samples": str(BOOTSTRAP_SAMPLES),
        },
        "outputs": {
            "key_claims": str(key_rows_path),
            "manuscript_table": str(manuscript_path),
            "file_summary": str(file_summary_path),
        },
        "important_note": (
            "This stage promotes frozen Phase A poem-level bootstrap outputs into "
            "paper-facing tables. It does not recompute bootstrap samples yet."
        ),
    }

    manifest_path = ANALYSES_DIR / "bootstrap_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    entries = [
        hash_entry(key_rows_path, "Key bootstrap rows for manuscript claims."),
        hash_entry(manuscript_path, "Compact manuscript-facing bootstrap table."),
        hash_entry(file_summary_path, "Hashes and dimensions for frozen bootstrap source files."),
    ]
    write_hash_csv(entries)

    print("Prepared bootstrap artifacts:")
    for e in entries:
        print(f"  {e['destination']} rows={e['n_rows']} cols={e['n_cols']}")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {HASH_DIR / 'bootstrap_hashes.csv'}")

    print("\nBootstrap manuscript table:")
    print(manuscript_table.to_string(index=False))


if __name__ == "__main__":
    main()
