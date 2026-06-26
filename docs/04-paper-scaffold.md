# Paper Scaffold: The Domain Chooses the Value Function

## Working title

**The Domain Chooses the Value Function: Supervised Contrastive Probes for Human Poetic Appraisal**

Alternative titles:

1. **Domain-Relative Supervised Probes for Human Poetic Appraisal**
2. **When Compression Fails as Value: Human-Labeled Domains Induce Aesthetic Appraisal**
3. **Contrastive Domains, Not Metrics, Carry Human Poetic Value**
4. **The Domain Chooses the Value Function**

---

# One-sentence thesis

Generic compression-progress over external literary domains does not recover human poetic appraisal; human-labeled contrastive domains do, and once such domains are constructed, compression, TF-IDF, and sentence embeddings recover similar fully controlled signal, showing that the value signal lives primarily in the domain rather than in any uniquely privileged readout metric.

---

# Core claim hierarchy

## Claim 1: Generic D fails

Generic external literary domains do not recover contemporary human poetic appraisal and can anti-align with human ratings.

Interpretation:

> Frozen compression over a generic world/literary domain is not a label-free aesthetic value function.

## Claim 2: Preference-shaped D works

When D is constructed from human high/low preference labels, contrastive probes recover human appraisal structure.

Interpretation:

> Human-labeled domains induce a value landscape.

## Claim 3: The metric is secondary

Compression, TF-IDF contrast, and sentence-embedding contrast all recover signal from human-labeled D under full controls.

Interpretation:

> The value-bearing object is D, not the readout metric.

## Claim 4: Compression is competitive, not uniquely established

Compression is often higher by mean, especially in matched-control structural form, but poem-level bootstrap uncertainty does not establish a stable advantage over simpler baselines at n = 36.

Interpretation:

> Compression is a useful supervised readout, not demonstrated label-free value discovery.

## Claim 5: Matched-other is the open mechanism

Matched-other subtraction strongly improves compression at run level, but poem-level uncertainty cannot resolve whether this reflects a stable compression-specific mechanism or normalization.

Interpretation:

> If there is residual compression-specific structure, it lives in the matched-other interaction.

---

# Abstract draft

We test whether compression-progress can serve as a label-free value functional for poetry. In the proposed framework, an action or candidate is valuable when it improves compression of a target domain D under an observer model. We evaluate this idea on human poetry ratings by comparing generic external literary domains against human-labeled contrastive domains. Generic domains fail to recover contemporary human appraisal and can anti-align with human ratings, suggesting that frozen compression over broad literary data is not a universal aesthetic value signal. In contrast, domains constructed from human high/low preference labels recover appraisal structure. However, this positive signal is not unique to compression: TF-IDF contrast, sentence-embedding contrast, and compression all read out aspects of the supervised domain. Under full controls, including other human rating dimensions, surface features, and item-level language-model predictability, the three readouts converge within item-level bootstrap uncertainty. Compression is competitive and often strongest by mean in matched-control structural form, but the current sample does not establish a unique compression advantage. These results support a domain-relative supervised-probe view: D induces the value landscape, human labels are load-bearing, and compression is one possible readout rather than a label-free mechanism for aesthetic value.

---

# Introduction structure

## Paragraph 1: The motivating problem

Open-ended creative systems require selectors. Generators can produce many candidates, but without a value signal, generation alone does not explain curation, preference, or improvement. A natural hypothesis is that value can be modeled as compression-progress: a candidate is valuable if adding it to context improves compression of some target domain.

## Paragraph 2: The compression-progress hypothesis

Define the value functional:

```text
V(a | H) = Σ_i q_i [L(D | O_i ⊕ H) - L(D | O_i ⊕ H ⊕ a)] - cost(a)
```

where D is the target domain, O_i are observers, H is history/context, and a is the candidate action or artifact.

The key question:

> Can a frozen observer plus a generic target domain recover aesthetic value without human labels?

## Paragraph 3: Why poetry is a useful testbed

Poetry is a strong test case because aesthetic appraisal is subjective, culturally situated, and difficult to reduce to surface quality alone. If generic compression-progress can recover aesthetic value, it should show some alignment with human poetry ratings. If it cannot, poetry exposes the boundary of label-free value discovery.

## Paragraph 4: The experimental arc

We test three possibilities:

1. Generic D recovers human appraisal.
2. Preference-shaped D recovers human appraisal.
3. Compression is uniquely better than simpler supervised readouts.

The experiments support the second but not the first or third.

## Paragraph 5: Main result

Generic D fails. Preference-shaped D works. Compression is competitive but not uniquely established. Therefore, the central finding is domain-relativity:

> D chooses the value function.

---

# Methods structure

## 1. Data

### Chaudhuri 2024 poetry ratings

Use the 36 human poems and human rating dimensions:

```text
Clarity
Aesthetic_Appeal
Felt_Valence
Felt_Arousal
Surprise
Creativity
Open
Intellect
Awe
Curio
```

Primary target for the latest tests:

```text
target__Surprise
```

Main controlled dimensions:

```text
target__Aesthetic_Appeal
target__Clarity
target__Creativity
target__Felt_Valence
```

### Porter & Machery 2024

Use as supporting context for human/AI poetry rating structure and authorship confounds.

### Gutenberg / external literary D

Use as generic external D for the negative branch.

---

## 2. Compression-progress scoring

For candidate poem a and target domain D, compute compression gain as reduction in held-out domain loss:

```text
v_raw = L(D | O ⊕ H) - L(D | O ⊕ H ⊕ a)
```

Scores are normalized as bits per byte.

Important invariant:

> Score held-out D, not the candidate itself.

---

## 3. Preference-shaped contrastive domains

Construct high/low domains from human rating labels.

For Surprise:

```text
high_pool = poems in top Surprise region
low_pool  = poems in bottom Surprise region
```

Held-out K-fold protocol:

```text
dataset = Chaudhuri 2024 human poems
n_items = 36
folds = 6
fold_seeds = 101, 123, 202, 303, 404
sampling_seeds = 17, 18, 19, 20, 21
D_N = 8
pool_frac = 0.33
low_candidate_frac = 0.50
```

For each held-out item, build high/low pools only from train-fold items.

---

## 4. Matched-other structural control

For each candidate item, select a matched-other real poem control, matched primarily on surface features.

Compute:

```text
v_pref_raw = v_high_raw - v_low_raw
v_pref_ctrl = v_high_ctrl - v_low_ctrl
v_pref_struct = v_pref_raw - v_pref_ctrl
```

Interpretation:

```text
v_pref_raw:
  raw contrastive compression toward high vs low domains

v_pref_ctrl:
  same score for matched-other control poem

v_pref_struct:
  matched-control residual
```

Caution:

> The matched-other operation is not a routine nuisance control. It is load-bearing for compression’s apparent advantage and should be analyzed directly.

---

## 5. Supervised baseline readouts

Compare compression against two supervised contrastive readouts using the same high/low pools, folds, labels, and matched-other controls.

### TF-IDF contrast

```text
TfidfVectorizer
ngram_range = (1, 2)
sublinear_tf = True
cosine similarity
```

Score:

```text
score_pref_raw =
  mean_cosine(candidate, high_pool) - mean_cosine(candidate, low_pool)
```

Structural version:

```text
score_pref_struct =
  score_pref_raw(candidate) - score_pref_raw(matched_other_control)
```

### Sentence-embedding contrast

```text
model = sentence-transformers/all-MiniLM-L6-v2
normalized embeddings
cosine similarity
```

Same raw and structural scores as TF-IDF.

---

## 6. Controls and residualization

Feature sets:

```text
none:
  no residual controls

other_human_targets:
  Aesthetic_Appeal
  Clarity
  Creativity
  Felt_Valence

stacked:
  Aesthetic_Appeal
  Clarity
  Creativity
  Felt_Valence
  word_len_calc
  char_len_calc
  line_count
  item_nll_bpb__distilgpt2
  item_nll_bpb__gpt2
  item_nll_bpb__gpt2-medium
```

Residualization uses rank residualization:

```text
residualize rank(target) against controls
residualize rank(score) against controls
Spearman correlation between residuals
```

---

## 7. Inference and uncertainty

Run-level paired tests:

```text
unit = fold_seed × sampling_seed run
n_runs = 25
```

These provide stability checks, but runs are not independent because all reuse the same 36 poems.

Poem-level bootstrap:

```text
unit = poem
n_items = 36
bootstrap = resample 36 poems with replacement
recompute paired differences
report 95% bootstrap CIs
```

The poem-level bootstrap is the primary uncertainty estimate for method comparisons.

---

# Results structure

## Result 1: Generic D fails

Generic external literary domains do not recover contemporary human appraisal and can anti-align with human ratings.

Interpretation:

> Generic compression-progress is not a label-free aesthetic value function.

This is the first central result.

---

## Result 2: Preference-shaped D recovers appraisal structure

Human-labeled high/low domains recover human appraisal signal in held-out settings.

Key compression structural result:

```text
none / score_pref_struct:
  compression mean rho = +0.409184
```

But this is halo-inclusive and should not be used as the Surprise-specific headline.

---

## Result 3: Fully controlled compression signal survives against a null

Fully stacked compression structural residual:

```text
feature_set = stacked
metric = v_pref_struct

observed mean partial rho = +0.285508
right-tail p = 0.0103
two-sided p = 0.0206
max-primary p = 0.0217
```

Interpretation:

> Compression produces a positive supervised contrastive signal under stacked controls against a permutation null.

Caution:

> This does not establish compression-specific superiority over other readouts.

---

## Result 4: Baseline readouts converge under full controls

Fully stacked structural target:

```text
compression = +0.285508
embedding   = +0.272937
TF-IDF      = +0.246795
```

Paired run-level differences:

```text
compression - embedding:
  observed diff = +0.012571

compression - TF-IDF:
  observed diff = +0.038713
```

Poem-level bootstrap:

```text
compression - embedding:
  observed diff = +0.012571
  95% CI = [-0.380624, +0.485224]

compression - TF-IDF:
  observed diff = +0.038713
  95% CI = [-0.317221, +0.454646]
```

Interpretation:

> Under full controls, compression, embeddings, and TF-IDF are statistically indistinguishable at n = 36. This supports the claim that the value signal lives in the human-labeled domain, not in a uniquely privileged readout metric.

---

## Result 5: Compression leans higher before full stacking but is unresolved

Other-human residual structural target:

```text
compression = +0.266543
embedding   = +0.138172
TF-IDF      = +0.096371
```

Run-level paired tests favored compression:

```text
compression - embedding:
  observed diff = +0.128371
  run-level p_right = 0.00088

compression - TF-IDF:
  observed diff = +0.170172
  run-level p_right = 0.00001
```

But poem-level bootstrap CIs include zero:

```text
compression - embedding:
  95% CI = [-0.210394, +0.437982]

compression - TF-IDF:
  95% CI = [-0.229377, +0.530668]
```

Interpretation:

> Compression’s point estimates lean positive on the partially controlled structural target, but n = 36 cannot resolve whether this advantage is stable.

Do not claim:

```text
Compression significantly beats baselines at item-level uncertainty.
```

Safe claim:

```text
Compression is competitive and higher by mean before full stacking, but the advantage is unresolved under poem-level bootstrap.
```

---

## Result 6: Matched-other subtraction is load-bearing but unresolved

Canonical matched-other diagnostic:

```text
struct_matched_other = v_pref_struct
raw_plus_ctrl_surface_nll =
  v_pref_raw residualized against v_pref_ctrl + surface + item NLL controls
```

Other-human residual:

```text
struct_matched_other = +0.266543
raw_plus_ctrl_surface_nll = +0.192803
observed diff = +0.073740
bootstrap 95% CI = [-0.097910, +0.319426]
```

Fully stacked:

```text
struct_matched_other = +0.285508
raw_plus_ctrl_surface_nll = +0.231176
observed diff = +0.054332
bootstrap 95% CI = [-0.062995, +0.178836]
```

Interpretation:

> Matched-other subtraction improves compression at the run level and remains higher by mean than explicit normalization, but the item-level bootstrap does not establish that this extra advantage is stable.

Discussion framing:

> If any compression-specific signal exists, it likely lives in the matched-other interaction. The present n = 36 sample cannot resolve whether this is a stable mechanism or a normalization effect.

---

# Main table for paper

```text
Comparison                                Observed diff     Poem bootstrap 95% CI        Interpretation

Compression - Embedding
other-human / struct                       +0.128            [-0.210, +0.438]             leans compression, unresolved

Compression - TF-IDF
other-human / struct                       +0.170            [-0.229, +0.531]             leans compression, unresolved

Compression - Embedding
stacked / struct                           +0.013            [-0.381, +0.485]             no resolvable difference

Compression - TF-IDF
stacked / struct                           +0.039            [-0.317, +0.455]             no resolvable difference

Matched-other - explicit normalization
other-human / struct                       +0.074            [-0.098, +0.319]             leans matched-other, unresolved

Matched-other - explicit normalization
stacked / struct                           +0.054            [-0.063, +0.179]             leans matched-other, unresolved
```

---

# Discussion points

## 1. The negative result is central

The experiment does not support label-free compression value discovery.

Generic D fails. Human-labeled D works.

Therefore:

```text
human labels are where the value signal enters
```

## 2. Metric convergence is positive evidence

The convergence of compression, TF-IDF, and embeddings under full controls is not merely a failed compression-specialness claim.

It is evidence that:

```text
the labeled domain carries the recoverable value signal
```

because three very different readout metrics recover similar signal once D is human-shaped.

## 3. Compression remains theoretically interesting

Compression behaves differently from TF-IDF and embeddings in response to matched-other subtraction.

This is the one unresolved compression-specific mechanism.

But the current dataset cannot establish it.

## 4. The framework boundary is empirically confirmed

The original framework asked whether value could be recovered by frozen compression-progress over a generic domain.

The answer here is no.

Open-ended aesthetic value appears to require:

```text
a human-shaped verifier
or
a human-labeled domain
```

The human is not removed from the selector loop. The human is relocated into D.

---

# Final terminal claim

This experiment does not show that compression-progress mechanizes aesthetic value label-free. It shows that aesthetic value enters through the construction of D. Generic D fails; human-labeled D works. Once D is human-shaped, multiple readout metrics, including compression, TF-IDF, and embeddings, recover similar signal under full controls. Compression is competitive and sometimes higher by mean, especially through matched-other subtraction, but this sample cannot resolve a unique compression advantage. The robust contribution is domain-induced supervised value, not compression-specific value discovery.

---

# One-paragraph final conclusion

We began with the hypothesis that compression-progress might provide an unfrozen, label-free selector for aesthetic value. The experiments return a sharper boundary. Generic world-grounded compression does not recover human poetic appraisal and can anti-align with it. Human-labeled contrastive domains, however, induce a landscape that multiple metrics can read out. Compression is a competitive readout and may contain an unresolved matched-control interaction, but it is not uniquely established under item-level uncertainty. Thus the domain, not the metric, carries the value signal. In this setting, aesthetic value is supervised and domain-induced: the human cannot be removed from the selector loop, only relocated into the construction of D.
