from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT / "data" / "processed"
SCORE_DIR = ROOT / "results" / "scores" / "phase_a_eval_scores"
CONTROL_DIR = ROOT / "results" / "controls"
HASH_DIR = ROOT / "results" / "hashes"

SURFACE_SOURCE = PROCESSED_DIR / "surface_matched_pools.csv"
TARGETS_WIDE = PROCESSED_DIR / "targets_wide.csv"

SURFACE_PATTERNS = [
    "word",
    "char",
    "len",
    "length",
    "line",
    "stanza",
    "token",
    "syll",
    "rhyme",
    "meter",
    "surface",
    "matched",
    "control",
    "ctrl",
]

NLL_PATTERNS = [
    "nll",
    "bpb",
    "bits_per_byte",
    "perplex",
    "ppl",
    "item_nll",
    "uncond",
    "predictability",
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


def safe_slug(s: str, max_len: int = 80) -> str:
    out = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return out[:max_len] if len(out) > max_len else out


def matches_any(name: str, patterns: list[str]) -> bool:
    low = name.lower()
    return any(p in low for p in patterns)


def write_csv_hash_entry(path: Path, note: str) -> dict:
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
    out = HASH_DIR / "control_hashes.csv"

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


def extract_surface_features() -> tuple[Path, list[dict]]:
    if not SURFACE_SOURCE.exists():
        raise FileNotFoundError(
            f"Missing {SURFACE_SOURCE}. Run pipeline/00_prepare_data.py first."
        )

    df = pd.read_csv(SURFACE_SOURCE)

    if "item_id" not in df.columns:
        raise ValueError(f"{SURFACE_SOURCE} must contain item_id.")

    selected = ["item_id"]
    inventory = []

    for col in df.columns:
        if col == "item_id":
            continue

        if matches_any(col, SURFACE_PATTERNS):
            selected.append(col)
            inventory.append(
                {
                    "feature_source": str(SURFACE_SOURCE),
                    "feature_table": "surface_features",
                    "feature_name": col,
                    "feature_kind": "surface_or_matched_control",
                    "n_nonnull": int(df[col].notna().sum()),
                    "dtype": str(df[col].dtype),
                }
            )

    # Keep item_id plus detected surface/matched-control features.
    out_df = df[selected].copy()

    out_path = CONTROL_DIR / "surface_features.csv"
    out_df.to_csv(out_path, index=False)

    return out_path, inventory


def scan_csv_header(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            return next(reader)
    except Exception:
        return []


def extract_nll_features_from_scores() -> tuple[Path, list[dict]]:
    if not SCORE_DIR.exists():
        raise FileNotFoundError(
            f"Missing {SCORE_DIR}. Run pipeline/20_score_readouts.py first."
        )

    extracted_tables: list[pd.DataFrame] = []
    inventory: list[dict] = []

    for path in sorted(SCORE_DIR.glob("*.csv")):
        header = scan_csv_header(path)
        if not header or "item_id" not in header:
            continue

        nll_cols = [
            c for c in header
            if c != "item_id" and matches_any(c, NLL_PATTERNS)
        ]

        if not nll_cols:
            continue

        try:
            df = pd.read_csv(path, usecols=["item_id", *nll_cols])
        except Exception:
            continue

        # One row per item if possible. If a score artifact has repeated item rows,
        # average numeric NLL-like features by item_id.
        numeric_cols = []
        for col in nll_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if df[col].notna().any():
                numeric_cols.append(col)

        if not numeric_cols:
            continue

        grouped = df.groupby("item_id", as_index=False)[numeric_cols].mean()

        # Long score filenames can collide after slug truncation, so include
        # a short filename hash in the prefix. This keeps wide NLL feature
        # columns unique across fold seeds, pool/eval targets, and runs.
        name_hash = hashlib.sha1(path.name.encode("utf-8")).hexdigest()[:10]
        file_prefix = f"{safe_slug(path.stem, max_len=120)}__{name_hash}"
        rename = {
            col: f"{file_prefix}__{safe_slug(col, max_len=60)}"
            for col in numeric_cols
        }
        grouped = grouped.rename(columns=rename)
        extracted_tables.append(grouped)

        for original_col, renamed_col in rename.items():
            inventory.append(
                {
                    "feature_source": str(path),
                    "feature_table": "nll_features",
                    "feature_name": renamed_col,
                    "original_column": original_col,
                    "feature_kind": "nll_or_predictability",
                    "n_nonnull": int(grouped[renamed_col].notna().sum()),
                    "dtype": str(grouped[renamed_col].dtype),
                }
            )

    if not extracted_tables:
        out = pd.DataFrame(columns=["item_id"])
    else:
        out = extracted_tables[0]
        for table in extracted_tables[1:]:
            out = out.merge(table, on="item_id", how="outer")

    out_path = CONTROL_DIR / "nll_features.csv"
    out.to_csv(out_path, index=False)

    return out_path, inventory


def build_controls_inventory(surface_inventory: list[dict], nll_inventory: list[dict]) -> Path:
    rows = surface_inventory + nll_inventory
    out = CONTROL_DIR / "control_feature_inventory.csv"

    fieldnames = [
        "feature_source",
        "feature_table",
        "feature_name",
        "original_column",
        "feature_kind",
        "n_nonnull",
        "dtype",
    ]

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    return out


def build_control_summary(surface_path: Path, nll_path: Path, inventory_path: Path) -> Path:
    summary_rows = []

    for table_name, path in [
        ("surface_features", surface_path),
        ("nll_features", nll_path),
        ("control_feature_inventory", inventory_path),
    ]:
        rows, cols = csv_shape(path)
        summary_rows.append(
            {
                "table": table_name,
                "path": str(path),
                "n_rows": rows,
                "n_cols": cols,
                "sha256": sha256_file(path),
            }
        )

    out = CONTROL_DIR / "control_summary.csv"
    pd.DataFrame(summary_rows).to_csv(out, index=False)
    return out


def main() -> None:
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    HASH_DIR.mkdir(parents=True, exist_ok=True)

    surface_path, surface_inventory = extract_surface_features()
    nll_path, nll_inventory = extract_nll_features_from_scores()
    inventory_path = build_controls_inventory(surface_inventory, nll_inventory)
    summary_path = build_control_summary(surface_path, nll_path, inventory_path)

    manifest = {
        "stage": "30_compute_controls",
        "surface_source": str(SURFACE_SOURCE),
        "score_source_dir": str(SCORE_DIR),
        "outputs": {
            "surface_features": str(surface_path),
            "nll_features": str(nll_path),
            "control_feature_inventory": str(inventory_path),
            "control_summary": str(summary_path),
        },
        "important_note": (
            "This stage extracts control features already present in frozen Phase A "
            "artifacts. It does not run new language-model NLL computation."
        ),
    }

    manifest_path = CONTROL_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    hash_entries = [
        write_csv_hash_entry(surface_path, "Extracted surface and matched-control features."),
        write_csv_hash_entry(nll_path, "Extracted item-level NLL/predictability-like features from score artifacts, if present."),
        write_csv_hash_entry(inventory_path, "Inventory of extracted control features."),
        write_csv_hash_entry(summary_path, "Summary of control tables."),
    ]
    write_hash_csv(hash_entries)

    print("Prepared control artifacts:")
    for entry in hash_entries:
        print(
            f"  {entry['destination']} rows={entry['n_rows']} "
            f"cols={entry['n_cols']}"
        )
    print(f"Wrote {manifest_path}")
    print(f"Wrote {HASH_DIR / 'control_hashes.csv'}")

    if len(nll_inventory) == 0:
        print(
            "\nNote: no NLL-like columns were extracted from copied score artifacts. "
            "This is okay if item-level NLL features live in a separate Phase A result file; "
            "locate and add that file in a later pass."
        )


if __name__ == "__main__":
    main()
