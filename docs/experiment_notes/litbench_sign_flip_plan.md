# LitBench sign-flip experiment plan

## Motivation

The poetry results now support a negative-boundary interpretation:

- generic literary compression does not recover human poetic appraisal as a resolved positive signal;
- formal generic compression can anti-align with ratings;
- human-shaped contrastive construction is positive but not isolated from contrastive form;
- same-form human Surprise vs Surprise_surfacepool is positive but unresolved across DistilGPT-2, GPT-2, and GPT-2-medium.

The critic's key point is that the high surfacepool score is itself mechanistically informative. A nonhuman surface-feature contrast recovered almost as much held-out Surprise structure as the human-labeled contrast. This suggests that the positive signal may be mediated by surface-correlated contrastive structure rather than uniquely human aesthetic semantics.

LitBench lets us test a broader and more falsifiable hypothesis:

> Compression/predictability measures conventionality, fluency, accessibility, or typicality. Whether that signal aligns or anti-aligns with human preference depends on the evaluation population and task.

## Core sign-flip hypothesis

In the current poetry-aesthetic setting:

- contemporary raters may penalize conventionality;
- generic compression therefore fails or anti-aligns;
- higher-rated poems can be more predictable, showing that human appraisal is not simple LM surprise.

In LitBench:

- labels are pairwise creative-writing preferences derived from Reddit upvotes;
- crowd preference may reward accessibility, fluency, readability, and conventionality more than expert-ish poetry appraisal does;
- therefore generic compression/predictability may flip sign and positively align with preference.

## Dataset

Primary dataset:

- SAA-Lab/LitBench-Test
- SAA-Lab/LitBench-Train

LitBench provides a paired creative-writing preference benchmark. The paper reports:

- 43,827-pair training corpus;
- held-out debiased human-labeled test set;
- Claude-3.7-Sonnet as strongest off-the-shelf judge at 73%;
- trained Bradley-Terry and generative reward models at 78%.

## First-stage tests

### Test 1: Dataset ingest

Load LitBench test and train splits.

Record:

- column schema;
- number of pairs;
- available IDs;
- whether full story text is included or whether only comment IDs are included;
- average story length if text is available.

### Test 2: Pairwise generic predictability baseline

For each pair:

- compute LM negative log-likelihood or average token NLL for chosen and rejected texts;
- convert to a pairwise prediction:
  - prefer lower NLL / more predictable text;
  - optionally prefer higher NLL / more surprising text;
- report pairwise agreement with LitBench labels.

This directly tests whether crowd preference rewards predictability/accessibility.

### Test 3: Length and surface baselines

For each pair:

- prefer longer text;
- prefer shorter text;
- prefer lower type-token ratio;
- prefer higher type-token ratio;
- prefer simpler readability / surface fluency if cheaply available.

This tests whether any compression signal is just length or surface structure.

### Test 4: Contrastive domain construction

Generate same-form nonhuman controls:

- randompool v_pref_struct;
- lengthpool v_pref_struct;
- nllpool v_pref_struct;
- surface-feature-pool v_pref_struct.

Then compare against any human/preference-shaped domain construction:

- same score form;
- same observer;
- same pairwise evaluation;
- bootstrap over pairs or prompts.

## Evaluation metrics

Primary:

- pairwise accuracy against human preference labels.

Secondary:

- bootstrap confidence interval over pairwise accuracy;
- prompt-clustered bootstrap if prompt IDs are available;
- difference from 50%;
- difference from length baseline;
- difference from published judge/reward baselines when comparable.

## Interpretation rule

If generic predictability/compression positively predicts LitBench crowd preference while anti-aligning with poetry-aesthetic ratings, this supports the sign-flip theory:

> compression tracks conventionality / fluency / typicality, and the evaluative setting determines whether that signal is rewarded or penalized.

If generic predictability fails on both poetry and LitBench, then the generic compression result is a narrower negative finding.

If contrastive human/preference-shaped domains beat same-form nonhuman controls, then domain construction becomes stronger.

If they do not, the mechanism remains surface/contrastive rather than human-semantic.

## Guardrails

Do not claim this is a direct poetry replication. LitBench is a generalization/stress-test dataset:

- construct: creative-writing preference, not lab-rated poetic appraisal;
- labels: Reddit-derived preference, not expert aesthetic ratings;
- genre: stories, not poems;
- advantage: scale, pairwise labels, published baselines, longer texts.

## Immediate success criterion

The first checkpoint is not to beat LitBench reward models. The first checkpoint is to determine whether simple predictability/compression has a stable and interpretable directional relationship with LitBench preference.


## First held-out LitBench baselines

We scored the complete held-out LitBench test artifact:

- dataset: SAA-Lab/LitBench-Test-IDs-Complete
- n = 2,480 chosen/rejected pairs
- full prompt, chosen_story, rejected_story, metadata, comment IDs, and post IDs are available.

### Surface baselines

The strongest non-upvote surface baselines were:

- prefer_more_paragraphs: 58.87%, CI [56.93%, 60.77%]
- prefer_more_newlines: 58.02%, CI [56.13%, 59.92%]
- prefer_more_punct: 55.60%, CI [53.67%, 57.50%]

Raw length was near chance:

- prefer_more_words: 50.93%, CI [49.03%, 52.82%]
- prefer_more_chars: 50.93%, CI [48.99%, 52.78%]

Interpretation:
LitBench preference is not simply a preference for longer stories. It is more strongly associated with formatting and structural organization: paragraphs, line breaks, and punctuation.

### DistilGPT-2 average NLL baseline

We scored each chosen/rejected story with DistilGPT-2 using sliding-window average token negative log-likelihood.

Results:

- prefer_lower_avg_nll: 54.27%, CI [52.34%, 56.21%]
- prefer_higher_avg_nll: 45.73%, CI [43.79%, 47.66%]
- prefer_higher_total_nll: 51.33%, CI [49.35%, 53.23%]
- prefer_lower_total_nll: 48.67%, CI [46.77%, 50.65%]

Interpretation:
Preferred LitBench stories are more predictable / fluent under DistilGPT-2 by average token NLL. This signal is modest but resolved, and it is stronger than raw length. The total-NLL direction is not clean because total NLL is heavily entangled with length.

This supports the emerging cross-domain mechanism:

> Compression or predictability does not measure literary value directly. It measures fluency, accessibility, conventionality, or typicality. Whether that signal helps or hurts depends on the evaluative population and task.

For Reddit creative-writing preference, predictability/fluency appears mildly rewarded. In the poetry setting, generic formal compression can anti-align with contemporary appraisal, suggesting that raters may penalize conventionality in that domain.

## Combined surface + NLL model

We trained simple cross-validated logistic pairwise models on the held-out complete LitBench test set using pairwise feature differences.

Results:

- surface_format: 60.60%, CI [58.67%, 62.46%]
- nll_avg_only: 55.12%, CI [53.15%, 57.06%]
- surface_plus_avg_nll: 61.29%, CI [59.31%, 63.23%]
- surface_plus_avg_and_total_nll: 61.37%, CI [59.44%, 63.27%]

Paired bootstrap deltas:

- surface_plus_avg_nll - surface_format: +0.69 points, CI [-0.65,+2.02], unresolved.
- surface_plus_avg_and_total_nll - surface_format: +0.77 points, CI [-0.52,+2.10], unresolved.
- surface_format - nll_avg_only: +5.48 points, CI [+3.06,+7.94], resolved.

Interpretation:
Average NLL predicts held-out LitBench preference above chance, but its incremental value beyond formatting/surface organization is not resolved. Formatting and surface organization are the stronger predictors. The sign-flip hypothesis should therefore be softened: LitBench preference rewards readable organization and modestly rewards LM fluency/predictability, rather than being primarily explained by predictability.

## Interpretation correction after critic review

The first LitBench results should be interpreted more conservatively.

The held-out test result confirms a sign-flip for raw average predictability:

- preferred stories have lower DistilGPT-2 average NLL than rejected stories;
- prefer_lower_avg_nll reaches 54.27%, CI [52.34%, 56.21%].

However, this is not yet a test of the paper's central compression-progress quantity V. It is a test of unconditional fluency / typicality.

The combined model also shows that NLL does not add a resolved increment beyond surface formatting:

- surface_format: 60.60%, CI [58.67%, 62.46%]
- surface_plus_avg_nll: 61.29%, CI [59.31%, 63.23%]
- delta: +0.69 points, CI [-0.65,+2.02], unresolved.

Therefore, the honest current LitBench claim is:

> LitBench preference is primarily captured by readable formatting / surface organization among the simple features tested. Raw average predictability is above chance, but its incremental value beyond formatting is unresolved.

The framework-relevant test remains to be run:

> Does compression-progress V predict LitBench preference, especially after residualizing or controlling for formatting?

Next priority:
1. inventory repeated prompts / post IDs / possible domain construction;
2. implement global compression-progress V;
3. implement prompt-conditioned V if the data support it;
4. evaluate V raw and net of formatting;
5. repeat with GPT-2-family observers if feasible.
