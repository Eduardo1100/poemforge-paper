# Generic Compression Does Not Recover Human Poetic Appraisal

## Abstract

We test whether label-free compression progress over a generic literary domain can recover human poetic appraisal. The answer is negative in this evaluation setting. Compression scores against Gutenberg-derived poetry domains fail to align with human ratings and in several settings trend in the opposite direction, suggesting that generic literary compression primarily tracks typicality rather than human-rated poetic value.

We then examine a supervised contrastive variant in which the held-out domain $D$ is constructed from high-rated and low-rated poems. In run-level summaries, compression, TF-IDF similarity, and embedding similarity all show positive held-out Surprise point estimates in the main controlled settings. This pattern should be interpreted as supervised domain-relative probing rather than as evidence for a label-free aesthetic evaluator: the human signal enters through the construction of $D$, the readout metric is not uniquely compression-specific, and smoke-test absolute poem-level bootstrap intervals include zero for all three readout families.

Across 25 held-out Surprise K-fold runs, compression has strong point estimates under some control settings, but poem-level bootstrap intervals over $n=36$ items do not resolve either a unique compression advantage over TF-IDF or embedding baselines or a fully resolved absolute supervised effect. We therefore treat run-level resampling results as stability diagnostics, not independent evidence. The main conclusion is a boundary result: generic compression does not mechanize poetic appraisal in this dataset, while supervised preference-shaped domains provide exploratory evidence of readable label structure.

## 1. Introduction

A natural way to formalize value is as expected improvement in a model’s ability to predict or compress future observations. In a creative setting, this suggests a strong hypothesis: a poem may be valuable if it helps compress a relevant poetic domain. This project began from that hypothesis.

Let a candidate artifact be $a$, a history be $H$, possible future observations be $O_i$, and a held-out domain be $D$. The value functional can be written as:

```math
V(a \mid H)
=
\sum_i q_i
\Big[
L(D \mid O_i \oplus H)
-
L(D \mid O_i \oplus H \oplus a)
\Big]
-
\mathrm{cost}(a).
```

The key invariant is that the score is not the likelihood of the candidate itself. The score is the candidate’s effect on a held-out domain $D$. This distinction matters. If $D$ is generic literary text, the system asks whether the candidate improves compression of a broad literary distribution. If $D$ is constructed from high-rated versus low-rated poems, the system asks whether the candidate is closer to the human preference contrast encoded in that domain.

This evaluation shows that the distinction is decisive. The original label-free version of the hypothesis fails. Generic Gutenberg-derived domains do not recover human poetic preference. But preference-shaped domains recover held-out Surprise structure across compression, TF-IDF, and embedding readouts. The value signal lives less in compression as such than in the construction of $D$.

This reframes PoemForge. The project is not evidence for an unsupervised aesthetic evaluator. It is evidence for a domain-relative probing framework in which human-labeled contrastive domains induce measurable label-contrast landscapes.

## 2. Experimental Setup

### 2.1 Items and human targets

The evaluation set contains human-rated poems from the Chaudhuri-style poem evaluation substrate. Each poem has target ratings for dimensions including Aesthetic Appeal, Clarity, Creativity, Felt Valence, and Surprise. The primary target in the final controlled experiments is Surprise, because it is central to the original compression-progress hypothesis and because it provides a test of whether the readout captures something beyond simple predictability.

The normalized data stage freezes item text, target ratings, surface features, and matched-control pools. These artifacts define the item universe for the rest of the pipeline.

### 2.2 Domains

We compare two broad domain types.

First, generic literary domains are sampled from Gutenberg-derived poetry-like text. These domains test the strong label-free hypothesis: if compression-progress over generic literary text is enough to recover human preference, then generic $D$ should correlate positively with human ratings.

Second, preference-shaped domains are constructed from high-rated and low-rated poems under a held-out K-fold protocol. For a target such as Surprise, high and low preference pools are rebuilt inside each training fold, and test items are scored against the resulting contrast. This prevents direct leakage from test items into the domain construction.

### 2.3 Readout metrics

We compare three readout families:

1. compression or language-model readouts;
2. TF-IDF similarity readouts;
3. embedding similarity readouts.

For preference-shaped domains, each readout produces raw, control, and structural preference scores. The structural score subtracts a matched-control effect:

```math
v_{\mathrm{struct}} = v_{\mathrm{raw}} - v_{\mathrm{ctrl}}.
```

For contrastive preference scoring, the main quantity is:

```math
v_{\mathrm{pref\_struct}}
=
\left(
v_{\mathrm{high\_raw}} - v_{\mathrm{low\_raw}}
\right)
-
\left(
v_{\mathrm{high\_ctrl}} - v_{\mathrm{low\_ctrl}}
\right).
```

The same conceptual structure is applied to TF-IDF and embedding baselines, producing comparable structural preference readouts.

### 2.4 Controls

We report three levels of control in the regenerated run-level summaries:

1. no residual controls;
2. residualization against other human target dimensions;
3. residualization against other human targets plus surface features.

The archived evaluation artifacts also include stacked controls using other human targets, surface features, and item-level language-model predictability. These are promoted into the bootstrap uncertainty table, because the item-level bootstrap was run over the canonical fully controlled outputs.

### 2.5 Statistical interpretation

Because the K-fold and seed runs reuse the same small item set, run-level statistics are not treated as independent inferential evidence. We report run-level means and permutation summaries as internal stability diagnostics: they show whether an effect is stable under fold and seed variation, but they do not replace item-level uncertainty over poems. For claims comparing readout families, the primary uncertainty standard is the poem-level bootstrap.

The stacked control setting should also be interpreted cautiously. Item-level language-model predictability is mechanistically closer to compression readouts than to TF-IDF or embedding cosine readouts, because compression scores are themselves derived from likelihood changes. Thus stacked controls are useful as a conservative stress test, but they are not a neutral adjustment across metrics. Apparent convergence under these controls may reflect suppressor effects and metric-asymmetric residualization in a small $n=36$ sample.

## 3. Results

### 3.1 Generic domains do not recover human preference

Generic Gutenberg-derived domains do not support the label-free compression-aesthetics hypothesis. In the generated generic-domain summary, raw compression scores are negative for both accessible and formal Gutenberg variants. Structural controls do not produce a stable positive preference signal. In several conditions, the correlations remain negative or near zero.

This result is important because it blocks the strongest interpretation of the original idea. Compression-progress against arbitrary literary text is not enough to recover human poetic appraisal. The domain must be shaped in relation to the target preference structure.

See Table 3, generated as `results/tables/table_3_generic_d_summary.*`, for the generic-domain summary.

### 3.2 Preference-shaped domains recover held-out Surprise structure

Preference-shaped domains behave differently. In held-out Surprise K-fold runs, all three readout families recover positive structural signal. Compression has the largest mean run-level structural correlation without residual controls and after residualization against other human targets.

The main readout convergence table shows:

* without residual controls, compression exceeds both embedding and TF-IDF;
* after controlling for other human targets, compression remains ahead by mean;
* after adding surface controls, the gap narrows substantially.

This pattern supports the domain-relative interpretation. Human-shaped domains induce a label contrast that multiple similarity-style metrics can read. Compression is competitive and often strongest by point estimate, but the signal is not compression-exclusive and should be interpreted as supervised contrastive probing rather than label-free value discovery. The absolute-effect smoke bootstrap adds a second caution: the positive supervised point estimates are not yet resolved at item level.

See Table 1, generated as `results/tables/table_1_readout_convergence.*`, Table 5, generated as `results/tables/table_5_absolute_effect_uncertainty.*`, and Figure 1, generated as `results/figures/figure_1_readout_convergence.*`.

### 3.3 Item-level bootstrap leaves the supervised effects unresolved

Run-level means lean toward compression in several partially controlled settings. But item-level bootstrap uncertainty is wide. For the key compression-vs-baseline comparisons, the observed differences are positive, but all 95% bootstrap intervals include zero.

This means the correct interpretation is not “compression is equal to the baselines.” The correct interpretation is underresolution at the item level. With $n=36$ poems, the data do not support a strong claim that compression uniquely outperforms TF-IDF or embedding similarity.

The same caution applies to the matched-other diagnostic. Point estimates are positive, but bootstrap intervals include zero. The leading interpretation is variance normalization, with any compression-specific mechanism unresolved.

As an additional check, we computed smoke-test absolute poem-level bootstrap intervals for the supervised Surprise effects themselves rather than only readout differences. These intervals include zero for compression, TF-IDF, and embedding under the main controlled settings, including the fully stacked condition. Thus the supervised contrastive result should be read as a positive point-estimate pattern, not as a resolved item-level effect in this small sample.

See Table 2, generated as `results/tables/table_2_bootstrap_uncertainty.*`, Table 5, generated as `results/tables/table_5_absolute_effect_uncertainty.*`, and Figure 2, generated as `results/figures/figure_2_bootstrap_uncertainty.*`.

### 3.4 Higher-rated poems are often more predictable

The item-level NLL analysis shows that higher-rated poems tend to be more language-model predictable. Correlations between unconditional item NLL and human targets are generally negative, especially for Aesthetic Appeal, Creativity, and Felt Valence. Surprise is also negatively correlated with NLL for the smallest model and weaker for larger models.

This is a useful boundary condition. Human-rated Surprise is not equivalent to language-model confusion. In this dataset, better or more surprising poems are not simply harder for a language model to predict. This weakens naive novelty-only interpretations and reinforces the need for domain-relative contrastive structure.

See Table 4, generated as `results/tables/table_4_item_nll_correlations.*`.

## 4. Discussion

### 4.1 What failed

The label-free compression-evaluator hypothesis failed. Generic literary domains do not recover human preference. This failure is not a nuisance result; it defines the boundary of the framework. The held-out domain $D$ is not an implementation detail. It is the source of the appraisal geometry.

A compression score can only be interpreted relative to the domain being compressed. If $D$ is generic, the score reflects generic literary predictability. If $D$ is preference-shaped, the score reflects the contrast encoded by that preference-shaped domain.

### 4.2 What survived

The domain-relative probing framework survived. When $D$ is built from human preference structure, multiple readouts recover held-out label structure. This includes compression, TF-IDF, and embeddings.

The convergence across readout families is a useful diagnostic, but not a strong independent contribution. It suggests that the preference-shaped domain contains robust structure rather than a metric-specific artifact. The system is therefore better interpreted as reading out structure induced by a supervised domain, rather than discovering aesthetic value without preference-shaped evidence.

### 4.3 Compression’s remaining role

Compression remains interesting, but the claim must be narrower. Compression has strong point estimates in several settings, and structural compression readouts outperform baselines by mean under no controls and under other-human-target residualization. However, the poem-level bootstrap does not resolve a unique compression advantage at the item level.

The matched-other diagnostic should first be interpreted as possible variance normalization: compression-gain estimates are noisy, so matched-control subtraction may help them more than it helps cosine-style similarities. The observed differences are positive, but unresolved under bootstrap. A compression-specific mechanism remains possible but is not established by the present data.

### 4.4 Implications for PoemForge

The practical implication is that PoemForge should not be framed as a label-free aesthetic evaluator. A more accurate framing is a domain construction and readout system. Its core capability is to build, audit, and compare domains that make a creative preference legible to different metrics.

Under this framing, the valuable object is not a universal compression score. The valuable object is a reproducible preference-probing pipeline:

1. define a target domain;
2. construct contrastive high/low pools;
3. score candidates through multiple readouts;
4. residualize against plausible confounds;
5. quantify uncertainty at the item level;
6. report where signal is robust, unresolved, or absent.

## 5. Limitations

The primary limitation is sample size. The final item-level analysis has $n=36$ poems, which is too small to resolve fine-grained differences between readout families. The bootstrap intervals make this limitation explicit.

A second limitation is domain specificity. The positive results depend on human-shaped contrastive domains. This is appropriate for supervised probing, but it means the results should not be generalized to unsupervised aesthetic discovery.

A third limitation is that the current pipeline freezes and promotes several archived inferential artifacts rather than fully recomputing every expensive analysis from scratch. This is acceptable for a reproducibility bridge, but a final archival version should progressively replace frozen-result promotion with direct regeneration.

## 6. Conclusion

PoemForge began with a strong hypothesis: compression-progress over a held-out literary domain might provide a label-free proxy for poetic value. The evidence does not support that claim. Generic domains fail.

The surviving result is sharper but narrower. Human-labeled domains induce label-contrast landscapes. When $D$ is constructed from human preference structure, compression, TF-IDF, and embedding readouts show positive held-out label-structure point estimates. Compression is competitive and often strongest by point estimate, but item-level bootstrap uncertainty does not establish either a unique compression advantage or a fully resolved absolute supervised effect at $n=36$.

The final claim is therefore domain-relative supervised probing, not label-free compression aesthetics. The decisive object is not the readout metric alone, but the held-out domain $D$.

## Reproducibility

All reported manuscript tables and figures are generated by the reproducibility pipeline. The pipeline freezes normalized data, domain artifacts, score artifacts, control features, inferential results, bootstrap summaries, manuscript tables, manuscript figures, and scaffold numeric diffs.

The main manuscript-facing artifacts are:

- `results/tables/table_1_readout_convergence.*`;
- `results/tables/table_2_bootstrap_uncertainty.*`;
- `results/tables/table_3_generic_d_summary.*`;
- `results/tables/table_4_item_nll_correlations.*`;
- `results/tables/table_5_absolute_effect_uncertainty.*`;
- `results/figures/figure_1_readout_convergence.*`;
- `results/figures/figure_2_bootstrap_uncertainty.*`;
- `results/diffs/scaffold_numeric_diff.csv`;
- `results/diffs/scaffold_diff_report.md`.

The final scaffold check verifies 39 canonical manuscript values against expected values with tolerance $10^{-9}$. All checks pass.
