from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_A_ROOT = Path(os.environ.get("PHASE_A_REPO", ROOT.parent / "poemforge")).resolve()

SRC_SCORE_DIR = PHASE_A_ROOT / "eval" / "scores"
DST_SCORE_DIR = ROOT / "results" / "scores" / "phase_a_eval_scores"
HASH_DIR = ROOT / "results" / "hashes"

SCORE_GLOBS = [
    "*.csv",
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
        n_cols = len(header)
        n_rows = sum(1 for _ in reader)
    return n_rows, n_cols


def classify_score_file(path: Path) -> dict[str, str]:
    name = path.name.lower()

    if "tfidf" in name:
        readout_family = "tfidf"
    elif "embedding" in name or "minilm" in name or "sentence" in name:
        readout_family = "embedding"
    elif name.startswith("vscore") or "distilgpt2" in name or "gpt2" in name:
        readout_family = "compression_or_lm"
    else:
        readout_family = "unknown"

    if "gutenberg" in name:
        experiment_family = "generic_d"
    elif "preference" in name or "kfold" in name or "surprise" in name or "chaudhuri" in name:
        experiment_family = "preference_d"
    else:
        experiment_family = "unknown"

    if ".correlations." in name or name.endswith(".correlations.csv"):
        artifact_kind = "correlation_summary"
    elif "baseline" in name or "supervised_similarity" in name:
        artifact_kind = "baseline_score"
    elif "nll" in name:
        artifact_kind = "nll_or_predictability"
    else:
        artifact_kind = "score_table"

    return {
        "readout_family": readout_family,
        "experiment_family": experiment_family,
        "artifact_kind": artifact_kind,
    }


def collect_score_files() -> list[Path]:
    if not SRC_SCORE_DIR.exists():
        raise FileNotFoundError(f"Phase A score directory missing: {SRC_SCORE_DIR}")

    files: list[Path] = []
    for pattern in SCORE_GLOBS:
        files.extend(SRC_SCORE_DIR.glob(pattern))

    return sorted(set(p for p in files if p.is_file()))


def copy_score_file(src: Path) -> dict:
    rel = src.relative_to(SRC_SCORE_DIR)
    dst = DST_SCORE_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    n_rows, n_cols = csv_shape(dst)
    cls = classify_score_file(dst)

    return {
        "status": "copied",
        "source": str(src),
        "destination": str(dst),
        "filename": dst.name,
        "sha256": sha256_file(dst),
        "n_rows": n_rows,
        "n_cols": n_cols,
        **cls,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def main() -> None:
    if not PHASE_A_ROOT.exists():
        print(f"Phase A repo not found: {PHASE_A_ROOT}", file=sys.stderr)
        print("Set PHASE_A_REPO=/path/to/poemforge if needed.", file=sys.stderr)
        raise SystemExit(1)

    files = collect_score_files()
    if not files:
        raise RuntimeError(f"No score CSV files found in {SRC_SCORE_DIR}")

    DST_SCORE_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    entries = [copy_score_file(src) for src in files]

    manifest = {
        "stage": "20_score_readouts",
        "phase_a_root": str(PHASE_A_ROOT),
        "source_score_dir": str(SRC_SCORE_DIR),
        "destination_score_dir": str(DST_SCORE_DIR),
        "n_files": len(entries),
        "important_note": (
            "This stage copies frozen Phase A score artifacts. It does not yet "
            "regenerate scores from readout implementations. Later versions should "
            "port canonical scoring code and diff regenerated scores against these "
            "frozen artifacts."
        ),
        "entries": entries,
    }

    manifest_path = ROOT / "results" / "scores" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    fieldnames = [
        "status",
        "filename",
        "readout_family",
        "experiment_family",
        "artifact_kind",
        "n_rows",
        "n_cols",
        "sha256",
        "source",
        "destination",
    ]

    write_csv(ROOT / "results" / "scores" / "score_inventory.csv", entries, fieldnames)
    write_csv(HASH_DIR / "score_hashes.csv", entries, fieldnames)

    print(f"Copied {len(entries)} Phase A score artifacts.")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {ROOT / 'results' / 'scores' / 'score_inventory.csv'}")
    print(f"Wrote {HASH_DIR / 'score_hashes.csv'}")

    # Compact summary for terminal review.
    summary: dict[tuple[str, str, str], int] = {}
    for e in entries:
        key = (e["readout_family"], e["experiment_family"], e["artifact_kind"])
        summary[key] = summary.get(key, 0) + 1

    print("\nInventory summary:")
    for (readout, experiment, kind), count in sorted(summary.items()):
        print(f"  {readout:18s} {experiment:14s} {kind:24s} {count}")


if __name__ == "__main__":
    main()
