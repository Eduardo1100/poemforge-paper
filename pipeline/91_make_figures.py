from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

TABLE_DIR = ROOT / "results" / "tables"
FIG_DIR = ROOT / "results" / "figures"
HASH_DIR = ROOT / "results" / "hashes"

READOUT_TABLE = TABLE_DIR / "table_1_readout_convergence.csv"
BOOTSTRAP_TABLE = TABLE_DIR / "table_2_bootstrap_uncertainty.csv"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_size(path: Path) -> int:
    return path.stat().st_size


def parse_ci(ci: str) -> tuple[float, float]:
    nums = re.findall(r"[-+]?\d+\.\d+", str(ci))
    if len(nums) != 2:
        raise ValueError(f"Could not parse CI: {ci}")
    return float(nums[0]), float(nums[1])


def save_both(fig, stem: str) -> list[Path]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png = FIG_DIR / f"{stem}.png"
    pdf = FIG_DIR / f"{stem}.pdf"

    # Keep figure artifacts byte-stable across repeated `make reproduce` runs.
    # Matplotlib PDFs otherwise may include timestamp-like metadata.
    pdf_metadata = {
        "Creator": "poemforge-paper pipeline/91_make_figures.py",
        "Producer": "Matplotlib",
        "CreationDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
        "ModDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
    }

    fig.savefig(png, bbox_inches="tight", dpi=200)
    fig.savefig(pdf, bbox_inches="tight", metadata=pdf_metadata)
    plt.close(fig)
    return [png, pdf]


def make_readout_convergence_figure() -> list[Path]:
    df = pd.read_csv(READOUT_TABLE)

    labels = df["Controls"].tolist()
    readouts = ["Compression", "Embedding", "TF-IDF"]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 4.8))

    for i, readout in enumerate(readouts):
        offsets = x + (i - 1) * width
        vals = pd.to_numeric(df[readout], errors="coerce").to_numpy()
        ax.bar(offsets, vals, width, label=readout)

    ax.set_ylabel("Mean Spearman ρ")
    ax.set_title("Structural preference readouts converge under controls")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.legend(frameon=False)
    ax.axhline(0, linewidth=1)
    fig.tight_layout()

    return save_both(fig, "figure_1_readout_convergence")


def make_bootstrap_ci_figure() -> list[Path]:
    df = pd.read_csv(BOOTSTRAP_TABLE)

    observed = pd.to_numeric(df["Observed Δ"], errors="coerce").to_numpy()
    ci = df["95% CI"].map(parse_ci)
    low = np.array([a for a, _ in ci])
    high = np.array([b for _, b in ci])

    xerr = np.vstack([observed - low, high - observed])
    y = np.arange(len(df))

    labels = [
        f"{claim}: {comparison}"
        for claim, comparison in zip(df["Claim"], df["Comparison"])
    ]

    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.errorbar(observed, y, xerr=xerr, fmt="o", capsize=4)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Observed difference in mean run-level ρ")
    ax.set_title("Poem-level bootstrap intervals cross zero")
    fig.tight_layout()

    return save_both(fig, "figure_2_bootstrap_uncertainty")


def write_hash_csv(paths: list[Path]) -> Path:
    HASH_DIR.mkdir(parents=True, exist_ok=True)
    out = HASH_DIR / "figure_hashes.csv"

    fieldnames = [
        "status",
        "destination",
        "sha256",
        "size_bytes",
        "note",
    ]

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for path in paths:
            writer.writerow(
                {
                    "status": "generated",
                    "destination": str(path),
                    "sha256": sha256_file(path),
                    "size_bytes": file_size(path),
                    "note": "Generated manuscript figure.",
                }
            )

    return out


def main() -> None:
    for path in [READOUT_TABLE, BOOTSTRAP_TABLE]:
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run pipeline/90_make_tables.py first.")

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    generated.extend(make_readout_convergence_figure())
    generated.extend(make_bootstrap_ci_figure())

    manifest = {
        "stage": "91_make_figures",
        "outputs": [str(p) for p in generated],
        "important_note": (
            "This stage formats existing table outputs into manuscript figures. "
            "It does not alter empirical values."
        ),
    }

    manifest_path = FIG_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    hash_path = write_hash_csv(generated)

    print("Generated paper figures:")
    for p in generated:
        print(f"  {p} size={file_size(p)} bytes")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {hash_path}")


if __name__ == "__main__":
    main()
