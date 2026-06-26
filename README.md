# PoemForge Paper

Reproducibility repository for **PoemForge Phase A: Domain-Relative Preference Probing with Compression, Similarity, and Human-Rated Poetry**.

This repository contains a reproducible bridge from frozen Phase A artifacts to manuscript-facing tables, figures, and numeric drift checks.

## Core Claim

PoemForge Phase A does **not** support the strong claim that generic compression-progress provides a label-free aesthetic oracle.

The robust result is narrower and cleaner:

> Human-labeled domains induce the value landscape. Generic world-grounded compression fails to recover human poetic appraisal, while preference-shaped contrastive domains recover appraisal structure across multiple readout metrics.

Compression is competitive and often strongest by run-level point estimate, but poem-level bootstrap uncertainty does not establish that compression uniquely outperforms TF-IDF or sentence-embedding contrast at the current item count.

## Repository Status

The pipeline currently reproduces the paper-facing empirical spine:

* normalized item and target data;
* domain artifacts;
* frozen Phase A score artifacts;
* control feature inventories;
* regenerated run-level readout summaries;
* frozen inferential Phase A artifacts;
* bootstrap manuscript claim table;
* manuscript tables;
* manuscript figures;
* scaffold numeric drift checks.

The final scaffold diff checks 39 canonical manuscript values at tolerance `1e-9`.

## Reproduce

From the repository root:

```bash
make reproduce
```

Expected final stage:

```text
=== Running 99_diff_against_scaffold.py ===
Scaffold diff complete:
  total=39 pass=39 fail=0 missing=0
```

## Pipeline Stages

| Stage | Script                                 | Purpose                                                                  |
| ----- | -------------------------------------- | ------------------------------------------------------------------------ |
| 00    | `pipeline/00_prepare_data.py`          | Copy and hash normalized poem/item/target data                           |
| 10    | `pipeline/10_build_domains.py`         | Prepare generic-D, preference-D, and matched-control domain artifacts    |
| 20    | `pipeline/20_score_readouts.py`        | Copy and inventory frozen Phase A score artifacts                        |
| 30    | `pipeline/30_compute_controls.py`      | Extract surface, matched-control, and NLL-like control artifacts         |
| 40    | `pipeline/40_residualize.py`           | Regenerate run-level residualized readout summaries                      |
| 50    | `pipeline/50_permutation.py`           | Copy and inventory frozen Phase A inferential artifacts                  |
| 60    | `pipeline/60_bootstrap.py`             | Promote poem-level bootstrap outputs into manuscript-facing claim tables |
| 90    | `pipeline/90_make_tables.py`           | Generate manuscript tables in CSV, Markdown, and LaTeX                   |
| 91    | `pipeline/91_make_figures.py`          | Generate manuscript figures in PNG and PDF                               |
| 99    | `pipeline/99_diff_against_scaffold.py` | Check generated manuscript numbers against canonical scaffold values     |

## Key Outputs

### Manuscript

* `paper/main.md`

### Tables

* `results/tables/table_1_readout_convergence.*`
* `results/tables/table_2_bootstrap_uncertainty.*`
* `results/tables/table_3_generic_d_summary.*`
* `results/tables/table_4_item_nll_correlations.*`

### Figures

* `results/figures/figure_1_readout_convergence.png`
* `results/figures/figure_1_readout_convergence.pdf`
* `results/figures/figure_2_bootstrap_uncertainty.png`
* `results/figures/figure_2_bootstrap_uncertainty.pdf`

### Drift Checks

* `results/diffs/scaffold_numeric_diff.csv`
* `results/diffs/scaffold_diff_report.md`

## Interpretation Guide

### What the results show

Preference-shaped domains recover human appraisal structure across multiple readout families. Compression has strong run-level point estimates in several settings, especially for structural preference scores, but the evidence is best read as metric convergence induced by the domain.

### What the results do not show

The results do not show that compression alone discovers aesthetic value without supervision. Generic Gutenberg-derived domains fail or anti-align with human poetic ratings. The item-level bootstrap does not resolve a unique compression advantage over TF-IDF or embedding baselines.

### Best Current Framing

PoemForge is best framed as a **domain construction and readout system** for probing creative preference structure, not as a label-free aesthetic evaluator.

## Notes on Frozen Artifacts

Some stages currently promote frozen Phase A artifacts rather than recomputing every expensive analysis from scratch. This is intentional for the current reproducibility bridge. Later archival versions should progressively replace frozen-result promotion with direct regeneration where practical.

## License

TBD.
