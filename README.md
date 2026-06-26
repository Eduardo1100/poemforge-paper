# PoemForge Paper

Clean reproducibility artifact for the domain-relativity paper.

## Core thesis

Generic external domains do not recover human poetic appraisal; human-labeled contrastive domains do. Once such domains are constructed, compression, TF-IDF, and sentence-embedding readouts recover similar signal under full controls. The value signal lives primarily in the domain, not in a uniquely privileged metric.

## Reproduction

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make reproduce
```

## Rules

1. No manuscript number may appear without a generated output file.
2. All generated tables and figures must be reproduced from `pipeline/run_all.py`.
3. All paper claims must appear in `docs/claims_manifest.csv`.
4. Run-level tests are stability evidence, not independent item-level inference.
5. Poem-level bootstrap is the primary uncertainty estimate for method comparisons.
