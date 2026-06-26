from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PHASE_A_ROOT = Path(os.environ.get("PHASE_A_REPO", ROOT.parent / "poemforge")).resolve()

DOMAINS_DIR = ROOT / "results" / "domains"
HASH_DIR = ROOT / "results" / "hashes"
PROCESSED_DIR = ROOT / "data" / "processed"

POOL_FRAC = 0.33

GENERIC_DOMAIN_FILES = [
    (
        "eval/domain/d_gutenberg_accessible_v0.csv",
        "results/domains/d_gutenberg_accessible_v0.csv",
        "Generic-D accessible Gutenberg contrast domain.",
    ),
    (
        "eval/domain/d_gutenberg_accessible_v0_manifest.json",
        "results/domains/d_gutenberg_accessible_v0_manifest.json",
        "Manifest for accessible Gutenberg contrast domain.",
    ),
    (
        "eval/domain/d_gutenberg_formal_v0.csv",
        "results/domains/d_gutenberg_formal_v0.csv",
        "Generic-D formal Gutenberg contrast domain.",
    ),
    (
        "eval/domain/d_gutenberg_formal_v0_manifest.json",
        "results/domains/d_gutenberg_formal_v0_manifest.json",
        "Manifest for formal Gutenberg contrast domain.",
    ),
    (
        "eval/domain/d_gutenberg_poetry_samples.csv",
        "results/domains/d_gutenberg_poetry_samples.csv",
        "Generic Gutenberg poetry samples used by Phase A.",
    ),
    (
        "eval/domain/d_gutenberg_poetry_manifest.json",
        "results/domains/d_gutenberg_poetry_manifest.json",
        "Manifest for generic Gutenberg poetry samples.",
    ),
]

CONTROL_FILES = [
    (
        "eval/poemset/eval_targets_surface_matched_pools.csv",
        "results/domains/matched_other_controls.csv",
        "Surface-matched control metadata used by matched-other analyses.",
    ),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_shape(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() != ".csv":
        return None, None
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0
        return sum(1 for _ in reader), len(header)


def copy_artifact(src_rel: str, dst_rel: str, note: str, required: bool = True) -> dict:
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

    rows, cols = file_shape(dst)
    return {
        "status": "copied",
        "source": str(src),
        "destination": str(dst),
        "sha256": sha256_file(dst),
        "n_rows": rows,
        "n_cols": cols,
        "note": note,
    }


def semicolon_join(values: list[str]) -> str:
    return ";".join(str(v) for v in values)


def build_preference_domains() -> dict:
    """Build transparent high/low pool manifests from normalized target table.

    This stage does not score readouts. It records the label-induced domain pools
    that later readout stages must use or reproduce fold-wise.

    For the final held-out K-fold scoring protocol, `20_score_readouts.py` should
    rebuild train-fold-specific pools using the same ranking semantics.
    """

    targets_path = PROCESSED_DIR / "targets_wide.csv"
    if not targets_path.exists():
        raise FileNotFoundError(
            f"Missing {targets_path}. Run pipeline/00_prepare_data.py first."
        )

    df = pd.read_csv(targets_path)

    if "dataset" not in df.columns:
        raise ValueError("targets_wide.csv must contain a `dataset` column.")

    # Current main analysis uses Chaudhuri human poems.
    main = df[df["dataset"] == "chaudhuri_2024"].copy()
    if main.empty:
        raise ValueError("No rows with dataset == 'chaudhuri_2024' found.")

    target_cols = [
        c for c in main.columns
        if c.startswith("target__") and main[c].notna().sum() >= 10
    ]

    rows = []
    for target_col in target_cols:
        sub = main[["item_id", "text", target_col]].dropna().copy()
        sub = sub.sort_values(target_col, ascending=True)

        n_items = len(sub)
        pool_size = max(1, int(math.floor(n_items * POOL_FRAC)))

        low = sub.head(pool_size)
        high = sub.tail(pool_size).sort_values(target_col, ascending=False)

        rows.append(
            {
                "domain_id": f"chaudhuri_2024__{target_col}__poolfrac_{POOL_FRAC}",
                "dataset": "chaudhuri_2024",
                "target_col": target_col,
                "n_items": n_items,
                "pool_frac": POOL_FRAC,
                "pool_size": pool_size,
                "low_item_ids": semicolon_join(low["item_id"].tolist()),
                "high_item_ids": semicolon_join(high["item_id"].tolist()),
                "low_min": float(low[target_col].min()),
                "low_max": float(low[target_col].max()),
                "high_min": float(high[target_col].min()),
                "high_max": float(high[target_col].max()),
                "note": (
                    "Global high/low pool manifest. Held-out readout scoring must "
                    "rebuild pools inside each train fold to avoid leakage."
                ),
            }
        )

    out = DOMAINS_DIR / "preference_domains_manifest.csv"
    pd.DataFrame(rows).to_csv(out, index=False)

    return {
        "status": "generated",
        "source": str(targets_path),
        "destination": str(out),
        "sha256": sha256_file(out),
        "n_rows": len(rows),
        "n_cols": len(pd.DataFrame(rows).columns) if rows else 0,
        "note": (
            "Human-labeled global high/low preference-domain pool manifest. "
            "Used for audit and paper documentation; K-fold scoring must rebuild "
            "train-fold domains."
        ),
    }


def write_hash_csv(entries: list[dict]) -> None:
    HASH_DIR.mkdir(parents=True, exist_ok=True)
    out = HASH_DIR / "domain_hashes.csv"

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

    DOMAINS_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []

    for src_rel, dst_rel, note in GENERIC_DOMAIN_FILES:
        entries.append(copy_artifact(src_rel, dst_rel, note, required=True))

    for src_rel, dst_rel, note in CONTROL_FILES:
        entries.append(copy_artifact(src_rel, dst_rel, note, required=True))

    entries.append(build_preference_domains())

    manifest = {
        "stage": "10_build_domains",
        "phase_a_root": str(PHASE_A_ROOT),
        "pool_frac": POOL_FRAC,
        "entries": entries,
        "important_note": (
            "This stage records generic-D artifacts, matched-control metadata, "
            "and global preference-domain pool manifests. Final held-out scoring "
            "must rebuild preference pools inside each train fold."
        ),
    }

    manifest_path = DOMAINS_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_hash_csv(entries)

    print("Prepared domain artifacts:")
    for e in entries:
        status = e["status"]
        dst = e["destination"]
        rows = e.get("n_rows")
        cols = e.get("n_cols")
        print(f"  [{status}] {dst} rows={rows} cols={cols}")

    print(f"Wrote {manifest_path}")
    print(f"Wrote {HASH_DIR / 'domain_hashes.csv'}")


if __name__ == "__main__":
    main()
