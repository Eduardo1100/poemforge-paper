# Phase A Findings, Current Checkpoint

## Setup

- Eval set: 46 rated poems from Porter/Machery Study 2 and Chaudhuri 2024.
- External D: 512 Gutenberg Poetry Corpus chunks, sampled at D_N=32 or D_N=128.
- Observer: distilgpt2.
- Score: bits-per-byte NLL gain on held-out D.
- Controls tested: line-shuffle and word-shuffle.

## Main observations

1. Raw compression gain is stable but negatively correlated with human aesthetic ratings.
2. Line-shuffle control removes almost all residual signal.
3. Word-shuffle control produces a positive structural residual on the synthetic ladder.
4. Word-shuffle structural residual does not predict the 46-item human target.
5. The strongest human-target baseline remains is_ai, reflecting dataset composition rather than a general aesthetic law.

## Interpretation

The current V-score detects coarse coherence or poetic-language compatibility, but does not yet track fine-grained human aesthetic preference.

## Consequence

Next work should prioritize:
- stratified analysis by dataset/authorship,
- improved eval ladder with unique bad/weak/strong tiers,
- human or pairwise labels for generated weak/strong poems,
- additional observers only after the target set is less confounded.
