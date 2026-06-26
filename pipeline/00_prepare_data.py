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

PROCESSED_DIR = ROOT / "data" / "processed"
HASH_DIR = ROOT / "results" / "hashes"

REQUIRED_FILES = [
    (
        "eval/poemset/eval_items_all_text.csv",
        "data/processed/items.csv",
        "Primary normalized item table used for current paper analyses.",
    ),
    (
        "eval/poemset/eval_targets_all_text_long.csv",
        "data/processed/targets_long.csv",
        "Long-form normalized target/rating table.",
    ),
    (
        "eval/poemset/eval_targets_per_dimension_wide.csv",
        "data/processed/targets_wide.csv",
        "Wide-form normalized target/rating table.",
    ),
]

OPTIONAL_FILES = [
    (
        "eval/poemset/eval_items_porter_s2.csv",
        "data/processed/porter_items_s2.csv",
        "Porter Study 2 item table, supporting/contextual.",
    ),
    (
        "eval/poemset/eval_targets_porter_s2_long.csv",
        "data/processed/porter_targets_s2_long.csv",
        "Porter Study 2 target table, supporting/contextual.",
    ),
    (
        "eval/poemset/eval_targets_surface_matched_pools.csv",
        "data/processed/surface_matched_pools.csv",
        "Surface-matched pool metadata used by matched-control analyses.",
    ),
    (
        "eval/poemset/VERSION.txt",
        "data/processed/phase_a_poemset_VERSION.txt",
        "Phase A poemset version/provenance note.",
    ),
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


def copy_with_manifest(src_rel: str, dst_rel: str, note: str, required: bool) -> dict:
    src = PHASE_A_ROOT / src_rel
    dst = ROOT / dst_rel

    if not src.exists():
        if required:
            raise FileNotFoundError(f"Required source file missing: {src}")
        return {
            "status": "missing_optional",
            "source": str(src),
            "destination": str(dst),
            "note": note,
        }

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    n_rows, n_cols = csv_shape(dst)
    return {
        "status": "copied",
        "source": str(src),
        "destination": str(dst),
        "sha256": sha256_file(dst),
        "n_rows": n_rows,
        "n_cols": n_cols,
        "note": note,
    }


def write_hash_csv(entries: list[dict]) -> None:
    HASH_DIR.mkdir(parents=True, exist_ok=True)
    out = HASH_DIR / "data_hashes.csv"

    fieldnames = [
        "status",
        "destination",
        "sha256",
        "n_rows",
        "n_cols",
        "source",
        "note",
    ]

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in entries:
            writer.writerow({k: e.get(k, "") for k in fieldnames})


def main() -> None:
    if not PHASE_A_ROOT.exists():
        print(f"Phase A repo not found: {PHASE_A_ROOT}", file=sys.stderr)
        print("Set PHASE_A_REPO=/path/to/poemforge if needed.", file=sys.stderr)
        raise SystemExit(1)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for src_rel, dst_rel, note in REQUIRED_FILES:
        entries.append(copy_with_manifest(src_rel, dst_rel, note, required=True))

    for src_rel, dst_rel, note in OPTIONAL_FILES:
        entries.append(copy_with_manifest(src_rel, dst_rel, note, required=False))

    manifest = {
        "stage": "00_prepare_data",
        "phase_a_root": str(PHASE_A_ROOT),
        "entries": entries,
        "important_note": (
            "This first paper-pipeline stage copies frozen normalized Phase A files. "
            "A later pass should regenerate these from raw source data where feasible."
        ),
    }

    manifest_path = PROCESSED_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_hash_csv(entries)

    print("Prepared normalized data files:")
    for e in entries:
        status = e["status"]
        dst = e["destination"]
        rows = e.get("n_rows")
        cols = e.get("n_cols")
        print(f"  [{status}] {dst} rows={rows} cols={cols}")

    print(f"Wrote {manifest_path}")
    print(f"Wrote {HASH_DIR / 'data_hashes.csv'}")


if __name__ == "__main__":
    main()
