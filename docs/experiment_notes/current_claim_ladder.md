# Current claim ladder

## Strong resolved claims

1. Generic literary compression does not recover contemporary human poetic appraisal as a resolved positive signal.
2. Formal generic compression can anti-align with human ratings, suggesting that generic compression tracks conventionality or canon-likeness rather than contemporary appraisal.
3. Human appraisal is not language-model surprise: higher-rated poems are often more predictable, not less.

## Bounded positive claims

1. Human-shaped contrastive readouts are positive by point estimate.
2. Mixed-form human-vs-generic contrasts often favor human-shaped contrastive construction under matched controls.
3. These mixed-form contrasts should be read as human-shaped `v_pref_struct` versus generic `v_struct`, not as a fully isolated human-label domain effect.

## Explicitly unresolved claims

1. Same-form human Surprise `v_pref_struct` does not significantly outperform the available `Surprise_surfacepool` `v_pref_struct` control at n=36.
2. This same-form result remains unresolved across DistilGPT-2, GPT-2, and GPT-2-medium observer artifacts in the extension branch.
3. Compression-specific advantage over TF-IDF or embedding baselines is not resolved.
4. Broad word-shuffle robustness is not established.
5. Observer-family robustness for full paired generic-vs-human contrast remains incomplete.
6. Cross-target structure is exploratory, not resolved evidence for a shared appraisal manifold.

## Current publication framing

This is a negative-boundary paper.

The clean contribution is not that compression mechanizes poetic value. The clean contribution is that generic compression fails as a label-free aesthetic signal, and that value enters through human-shaped domain construction and contrastive setup. The current evidence supports human-shaped contrastive construction as suggestive, but not isolated from contrastive form at n=36.

## What would strengthen the positive mechanism claim

The decisive next experiment is a same-form domain-control study:

- human-labeled `v_pref_struct`
- versus nonhuman `v_pref_struct`
- with randompool, lengthpool, nllpool, or surface-feature pools
- ideally with both matched-control and word-shuffle variants
- ideally on a second dataset

Until then, the paper should remain framed as a boundary result.
