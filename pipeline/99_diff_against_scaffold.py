from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

ANALYSES_DIR = ROOT / "results" / "analyses"
DIFF_DIR = ROOT / "results" / "diffs"
HASH_DIR = ROOT / "results" / "hashes"

READOUT_CONVERGENCE = ANALYSES_DIR / "readout_convergence_summary.csv"
BOOTSTRAP_KEY_CLAIMS = ANALYSES_DIR / "bootstrap_key_claims.csv"

TOL = 1e-9


EXPECTED_READOUT_VALUES = [
    # feature_set, metric, column, expected_value
    ("none", "score_pref_struct", "compression", 0.4091842809236345),
    ("none", "score_pref_struct", "embedding", 0.2113708422631655),
    ("none", "score_pref_struct", "tfidf", 0.11476919060474207),
    ("none", "score_pref_struct", "compression_minus_embedding", 0.19781343866046902),
    ("none", "score_pref_struct", "compression_minus_tfidf", 0.29441509031889246),

    ("other_human_targets", "score_pref_struct", "compression", 0.2665431145431146),
    ("other_human_targets", "score_pref_struct", "embedding", 0.13817245817245818),
    ("other_human_targets", "score_pref_struct", "tfidf", 0.09637065637065638),
    ("other_human_targets", "score_pref_struct", "compression_minus_embedding", 0.1283706563706564),
    ("other_human_targets", "score_pref_struct", "compression_minus_tfidf", 0.17017245817245819),

    # This is a regenerated surface-control value, not the final stacked-NLL value.
    ("other_human_plus_surface", "score_pref_struct", "compression", 0.20897812097812105),
    ("other_human_plus_surface", "score_pref_struct", "embedding", 0.18947747747747748),
    ("other_human_plus_surface", "score_pref_struct", "tfidf", 0.13953153153153156),
    ("other_human_plus_surface", "score_pref_struct", "compression_minus_embedding", 0.019500643500643566),
    ("other_human_plus_surface", "score_pref_struct", "compression_minus_tfidf", 0.06944658944658949),
]


EXPECTED_BOOTSTRAP_VALUES = [
    # claim_id, column, expected_value
    ("B1", "observed_mean_diff", 0.1283706563706563),
    ("B1", "ci95_low", -0.2290724083829605),
    ("B1", "ci95_high", 0.433378526565762),
    ("B1", "n_boot", 5000),

    ("B2", "observed_mean_diff", 0.1701724581724582),
    ("B2", "ci95_low", -0.2285897266476315),
    ("B2", "ci95_high", 0.5269217731001804),
    ("B2", "n_boot", 5000),

    ("B3", "observed_mean_diff", 0.0125714285714285),
    ("B3", "ci95_low", -0.4074154144767005),
    ("B3", "ci95_high", 0.454174626586573),
    ("B3", "n_boot", 5000),

    ("B4", "observed_mean_diff", 0.0387129987129987),
    ("B4", "ci95_low", -0.3420982968842635),
    ("B4", "ci95_high", 0.4510032262227383),
    ("B4", "n_boot", 5000),

    ("B5", "observed_mean_diff", 0.0737400257400257),
    ("B5", "ci95_low", -0.1021451303272442),
    ("B5", "ci95_high", 0.3168722717293037),
    ("B5", "n_boot", 5000),

    ("B6", "observed_mean_diff", 0.0543320463320463),
    ("B6", "ci95_low", -0.0711492358318032),
    ("B6", "ci95_high", 0.1878295434085269),
    ("B6", "n_boot", 5000),
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


def diff_status(actual: float | None, expected: float, tol: float = TOL) -> tuple[str, float | None]:
    if actual is None or pd.isna(actual):
        return "missing", None

    delta = float(actual) - float(expected)
    if abs(delta) <= tol:
        return "pass", delta
    return "fail", delta


def add_readout_diffs(rows: list[dict]) -> None:
    df = pd.read_csv(READOUT_CONVERGENCE)

    for feature_set, metric, column, expected in EXPECTED_READOUT_VALUES:
        sub = df[
            (df["feature_set"] == feature_set)
            & (df["metric"] == metric)
        ]

        if len(sub) != 1 or column not in df.columns:
            actual = None
        else:
            actual = sub.iloc[0][column]

        status, delta = diff_status(actual, expected)

        rows.append(
            {
                "section": "readout_convergence",
                "key": f"{feature_set}/{metric}/{column}",
                "expected": expected,
                "actual": actual,
                "delta": delta,
                "tol": TOL,
                "status": status,
            }
        )


def add_bootstrap_diffs(rows: list[dict]) -> None:
    df = pd.read_csv(BOOTSTRAP_KEY_CLAIMS)

    for claim_id, column, expected in EXPECTED_BOOTSTRAP_VALUES:
        sub = df[df["claim_id"] == claim_id]

        if len(sub) != 1 or column not in df.columns:
            actual = None
        else:
            actual = sub.iloc[0][column]

        status, delta = diff_status(actual, expected)

        rows.append(
            {
                "section": "bootstrap_key_claims",
                "key": f"{claim_id}/{column}",
                "expected": expected,
                "actual": actual,
                "delta": delta,
                "tol": TOL,
                "status": status,
            }
        )


def write_markdown_report(diff_df: pd.DataFrame, path: Path) -> None:
    n_total = len(diff_df)
    n_pass = int((diff_df["status"] == "pass").sum())
    n_fail = int((diff_df["status"] == "fail").sum())
    n_missing = int((diff_df["status"] == "missing").sum())

    lines = []
    lines.append("# Scaffold Numeric Diff Report")
    lines.append("")
    lines.append(f"- Total checks: {n_total}")
    lines.append(f"- Passed: {n_pass}")
    lines.append(f"- Failed: {n_fail}")
    lines.append(f"- Missing: {n_missing}")
    lines.append(f"- Tolerance: {TOL}")
    lines.append("")

    if n_fail == 0 and n_missing == 0:
        lines.append("All scaffold checks passed.")
    else:
        lines.append("Some scaffold checks failed or were missing.")
        lines.append("")
        bad = diff_df[diff_df["status"] != "pass"].copy()
        lines.append("| section | key | expected | actual | delta | status |")
        lines.append("|---|---|---:|---:|---:|---|")
        for _, r in bad.iterrows():
            lines.append(
                f"| {r['section']} | {r['key']} | {r['expected']} | "
                f"{r['actual']} | {r['delta']} | {r['status']} |"
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_hash_csv(paths: list[Path]) -> Path:
    HASH_DIR.mkdir(parents=True, exist_ok=True)
    out = HASH_DIR / "scaffold_diff_hashes.csv"

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
        for path in paths:
            rows, cols = csv_shape(path)
            writer.writerow(
                {
                    "status": "generated",
                    "destination": str(path),
                    "sha256": sha256_file(path),
                    "n_rows": rows,
                    "n_cols": cols,
                    "note": "Generated scaffold numeric diff artifact.",
                }
            )

    return out


def main() -> None:
    for path in [READOUT_CONVERGENCE, BOOTSTRAP_KEY_CLAIMS]:
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run earlier pipeline stages first.")

    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    add_readout_diffs(rows)
    add_bootstrap_diffs(rows)

    diff_df = pd.DataFrame(rows)
    diff_path = DIFF_DIR / "scaffold_numeric_diff.csv"
    diff_df.to_csv(diff_path, index=False)

    report_path = DIFF_DIR / "scaffold_diff_report.md"
    write_markdown_report(diff_df, report_path)

    manifest = {
        "stage": "99_diff_against_scaffold",
        "tolerance": TOL,
        "outputs": {
            "numeric_diff": str(diff_path),
            "report": str(report_path),
        },
        "important_note": (
            "This stage checks selected regenerated manuscript numbers against "
            "canonical scaffold values. It is a drift detector, not a statistical test."
        ),
    }

    manifest_path = DIFF_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    hash_path = write_hash_csv([diff_path, report_path])

    n_total = len(diff_df)
    n_pass = int((diff_df["status"] == "pass").sum())
    n_fail = int((diff_df["status"] == "fail").sum())
    n_missing = int((diff_df["status"] == "missing").sum())

    print("Scaffold diff complete:")
    print(f"  total={n_total} pass={n_pass} fail={n_fail} missing={n_missing}")
    print(f"Wrote {diff_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {hash_path}")

    if n_fail or n_missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
