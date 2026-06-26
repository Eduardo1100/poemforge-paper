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

SRC_RESULTS_DIR = PHASE_A_ROOT / "eval" / "results"
DST_RESULTS_DIR = ROOT / "results" / "phase_a_eval_results"
ANALYSES_DIR = ROOT / "results" / "analyses"
HASH_DIR = ROOT / "results" / "hashes"

RESULT_EXTENSIONS = {".csv", ".json", ".txt", ".md"}


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


def classify_result_file(path: Path) -> dict[str, str]:
    name = path.name.lower()

    if "bootstrap" in name:
        inference_family = "bootstrap"
    elif "permutation" in name or "perm" in name:
        inference_family = "permutation"
    elif "paired" in name or "compare" in name or "baseline" in name:
        inference_family = "paired_or_baseline_comparison"
    elif "matched_other" in name or "matched" in name:
        inference_family = "matched_other_diagnostic"
    elif "gutenberg" in name or "external_d" in name or "mismatch" in name:
        inference_family = "generic_d"
    elif "nll" in name:
        inference_family = "nll_or_predictability"
    else:
        inference_family = "unknown"

    if "summary" in name:
        artifact_kind = "summary"
    elif "samples" in name:
        artifact_kind = "samples"
    elif "observed" in name:
        artifact_kind = "observed"
    elif "diagnostic" in name:
        artifact_kind = "diagnostic"
    else:
        artifact_kind = "result"

    return {
        "inference_family": inference_family,
        "artifact_kind": artifact_kind,
    }


def collect_result_files() -> list[Path]:
    if not SRC_RESULTS_DIR.exists():
        raise FileNotFoundError(f"Phase A eval/results directory missing: {SRC_RESULTS_DIR}")

    return sorted(
        p for p in SRC_RESULTS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in RESULT_EXTENSIONS
    )


def copy_result_file(src: Path) -> dict:
    dst = DST_RESULTS_DIR / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    rows, cols = csv_shape(dst)
    cls = classify_result_file(dst)

    return {
        "status": "copied",
        "filename": dst.name,
        "source": str(src),
        "destination": str(dst),
        "sha256": sha256_file(dst),
        "n_rows": rows,
        "n_cols": cols,
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

    files = collect_result_files()
    if not files:
        raise RuntimeError(f"No result artifacts found in {SRC_RESULTS_DIR}")

    DST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    entries = [copy_result_file(src) for src in files]

    fieldnames = [
        "status",
        "filename",
        "inference_family",
        "artifact_kind",
        "n_rows",
        "n_cols",
        "sha256",
        "source",
        "destination",
    ]

    inventory_path = ANALYSES_DIR / "phase_a_eval_results_inventory.csv"
    hash_path = HASH_DIR / "phase_a_eval_results_hashes.csv"

    write_csv(inventory_path, entries, fieldnames)
    write_csv(hash_path, entries, fieldnames)

    manifest = {
        "stage": "50_permutation",
        "phase_a_root": str(PHASE_A_ROOT),
        "source_results_dir": str(SRC_RESULTS_DIR),
        "destination_results_dir": str(DST_RESULTS_DIR),
        "n_files": len(entries),
        "outputs": {
            "inventory": str(inventory_path),
            "hashes": str(hash_path),
        },
        "important_note": (
            "This first Stage 50 pass copies and hashes frozen Phase A inferential "
            "artifacts from eval/results. It does not yet recompute permutation tests. "
            "Later versions should regenerate canonical permutation summaries and diff "
            "against these frozen outputs."
        ),
        "entries": entries,
    }

    manifest_path = DST_RESULTS_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Copied {len(entries)} Phase A eval/results artifacts.")
    print(f"Wrote {inventory_path}")
    print(f"Wrote {hash_path}")
    print(f"Wrote {manifest_path}")

    summary: dict[tuple[str, str], int] = {}
    for e in entries:
        key = (e["inference_family"], e["artifact_kind"])
        summary[key] = summary.get(key, 0) + 1

    print("\nInferential artifact inventory:")
    for (family, kind), count in sorted(summary.items()):
        print(f"  {family:34s} {kind:14s} {count}")


if __name__ == "__main__":
    main()
