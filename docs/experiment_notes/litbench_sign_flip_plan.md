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

