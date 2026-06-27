# Domain Construction Drives Compression-Based Signals in Poetic Appraisal

## Abstract

We test whether compression-progress scores over held-out poetic domains recover human poetic appraisal. The label-free version of the hypothesis fails: generic Gutenberg-derived domains do not show resolved positive alignment with human ratings, and matched-control generic-domain effects often trend negative. Generic literary compression appears to track typicality more than human-rated poetic value in this setting.

The surviving result is domain-relative but more bounded. When the held-out domain $D$ is constructed from human-labeled contrasts, structural compression readouts show positive alignment with human appraisal targets. A paired poem-level bootstrap comparing human-shaped contrastive domains against generic single-domain Gutenberg scores resolves under matched controls across Surprise, Aesthetic Appeal, and Creativity. However, this contrast mixes score form as well as domain source: the human-shaped side uses a high-minus-low contrastive score, while the generic side uses a single-domain structural score. A same-form Surprise follow-up comparing human-labeled `v_pref_struct` against a surface-pool `v_pref_struct` contrast does not resolve.

This does not establish a label-free aesthetic evaluator, a compression-specific advantage over TF-IDF and embedding baselines, or a fully isolated human-domain-construction mechanism. Absolute supervised effects remain underresolved at item level, word-shuffle controls resolve only in the cleanest self-domain cases, and the available same-form Surprise comparison against a surface-pool contrast is positive but unresolved. A bounded observer-family check using existing GPT-2 and GPT-2-medium artifacts also shows positive but unresolved Aesthetic Appeal alignment. The result is a boundary claim: generic compression alone does not recover human poetic appraisal, while human-shaped contrastive construction is suggestive but not yet isolated from contrastive form at $n=36$.

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

This evaluation shows that the distinction is decisive. The original label-free version of the hypothesis does not yield resolved positive alignment. Generic Gutenberg-derived domains do not recover human poetic appraisal as a resolved positive signal. Human-shaped domains, however, produce stronger alignment, and paired item-level domain contrasts resolve under matched-control settings across multiple appraisal targets. The value signal lives less in compression as such than in the construction of $D$.

This reframes PoemForge. The project is not evidence for an unsupervised aesthetic evaluator. It is evidence for a domain-relative probing framework in which human-labeled contrastive domains induce measurable appraisal landscapes. The paper therefore treats domain construction as the primary object of study and compression as one readout over that constructed domain.

## 2. Experimental Setup

### 2.1 Items and human targets

The evaluation set contains human-rated poems from the Chaudhuri-style poem evaluation substrate. Each poem has target ratings for dimensions including Aesthetic Appeal, Clarity, Creativity, Felt Valence, and Surprise. Surprise is the primary target in the original readout-convergence and compression-vs-baseline analyses, because it is central to the compression-progress hypothesis and tests whether the readout captures something beyond simple predictability. The final paired domain-contrast analyses extend beyond Surprise to Aesthetic Appeal and Creativity.

The normalized data stage freezes item text, target ratings, surface features, and matched-control pools. These artifacts define the item universe for the rest of the pipeline.

### 2.2 Domains

We compare two broad domain types.

First, generic literary domains are sampled from Gutenberg-derived poetry-like text. These domains test the strong label-free hypothesis: if compression-progress over generic literary text is enough to recover human poetic appraisal, then generic $D$ should correlate positively with human ratings.

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

Generic Gutenberg-derived domains do not support the label-free compression-aesthetics hypothesis as a resolved positive-alignment claim. In the generated generic-domain summary, raw compression scores are negative for both accessible and formal Gutenberg variants. Structural controls do not produce a stable positive preference signal. In the item-level bootstrap, formal matched-control structural scores are resolved negative, accessible matched-control structural scores trend negative but remain unresolved, and word-shuffle structural variants remain near zero or unresolved.

This result is important because it blocks the strongest interpretation of the original idea. Compression-progress against arbitrary literary text is not enough to recover human poetic appraisal. The held-out domain must be shaped in relation to the target preference structure.

See Table 3, generated as `results/tables/table_3_generic_d_summary.*`, for the generic-domain summary.

### 3.2 Human-shaped domains outperform generic domains under paired bootstrap

The critic-relevant comparison is not only whether a supervised readout is absolutely resolved, but whether human-shaped domains align better than generic domains when the readout and item set are held fixed. We therefore computed paired poem-level bootstraps over the same $n=36$ Chaudhuri poems, comparing structural compression scores from human-shaped domains against structural compression scores from generic Gutenberg domains.

The paired domain contrast is informative but should be interpreted as a mixed-form comparison. For target-matched domains, Aesthetic Appeal resolves in all four generic-control comparisons, Surprise resolves in three of four, and Creativity resolves in the two matched-control comparisons. In the consolidated target-pair matrix, every pool-target and evaluation-target pairing has a positive mean contrast. However, the contrast compares human-shaped `v_pref_struct` scores against generic `v_struct` scores, so it combines domain source with contrastive scoring form.

The strongest and most stable version of this mixed-form effect is the matched-control comparison. In the control-family summary, every target-matched condition resolves under matched controls. Aesthetic Appeal also resolves under word-shuffle controls, and Surprise partially resolves under word-shuffle controls, but word-shuffle robustness does not generalize broadly across cross-target settings. Thus, the robust claim is not that compression beats every possible null, nor that human labels have been isolated from contrastive scoring. The defensible claim is narrower: generic literary compression fails as a label-free signal, while human-shaped contrastive construction is positive and often stronger than generic single-domain scoring under matched controls.

See Table 7, generated as `results/tables/table_7_domain_contrast_target_pair_matrix.*`, for the consolidated target-pair matrix, and Table 8, generated as `results/tables/table_8_domain_contrast_by_control_family.*`, for the matched-control versus word-shuffle split.

### 3.3 Cross-target transfer is positive but asymmetric

Cross-target transfer tests whether human-shaped domains are target-specific silos or encode shared appraisal structure. The results support an intermediate view. Cross-target contrasts are positive by mean across all tested pairings, but they resolve less often than target-matched contrasts.

Aesthetic Appeal behaves like the broadest appraisal domain among the tested targets. Aesthetic-shaped domains transfer to Surprise and Creativity under matched controls. In the reverse direction, Surprise-shaped and Creativity-shaped domains transfer into Aesthetic Appeal less cleanly, resolving only in the formal matched-control condition. Surprise and Creativity transfer to each other symmetrically under matched controls, but not under word-shuffle controls.

This exploratory pattern is consistent with shared appraisal structure and target-specific sharpening, but it should not be treated as resolved evidence for a shared appraisal manifold. Human-shaped domains are not interchangeable, but neither are they fully isolated by point estimate. Aesthetic Appeal appears to capture broader quality/appraisal structure, while Surprise and Creativity behave more like narrower appraisal directions.

### 3.4 Preference-shaped domains recover held-out Surprise structure, but not as a compression-specific claim

Preference-shaped domains behave differently from generic domains. In held-out Surprise K-fold runs, all three readout families recover positive structural signal. Compression has the largest mean run-level structural correlation without residual controls and after residualization against other human targets.

However, these run-level summaries are stability diagnostics rather than independent inferential evidence. K-fold and seed runs reuse the same small item set, so the primary uncertainty standard is the poem-level bootstrap over items. Under that standard, the positive supervised Surprise effects remain underresolved, and the compression-vs-baseline comparisons do not resolve a unique compression advantage over TF-IDF or embedding similarity.

This pattern supports the domain-relative interpretation. Human-shaped domains induce a label contrast that multiple similarity-style metrics can read. Compression is competitive and often strongest by point estimate, but the signal is not compression-exclusive and should be interpreted as supervised contrastive probing rather than label-free value discovery.

See Table 1, generated as `results/tables/table_1_readout_convergence.*`, Table 2, generated as `results/tables/table_2_bootstrap_uncertainty.*`, Table 5, generated as `results/tables/table_5_absolute_effect_uncertainty.*`, Figure 1, generated as `results/figures/figure_1_readout_convergence.*`, and Figure 2, generated as `results/figures/figure_2_bootstrap_uncertainty.*`.

### 3.5 Same-form Surprise contrast is positive but unresolved

To address whether the paired domain contrast isolates domain construction from scoring form, we ran a same-form follow-up comparing human-labeled Surprise `v_pref_struct` against the available nonhuman `Surprise_surfacepool` `v_pref_struct` artifact. Both sides use the same contrastive score form and the same item-level bootstrap procedure.

The same-form contrast is not resolved. Human-labeled Surprise has observed $\rho=+0.518$, while the surface-pool contrast has observed $\rho=+0.481$. The observed difference is $+0.037$ with 95% bootstrap interval $[-0.179,+0.254]$. This result supports the stricter interpretation: the previous large mixed-form contrasts should not be treated as an isolated human-domain-construction mechanism. At $n=36$, human-labeled contrastive construction is positive, but it does not significantly outperform this available surface-pool contrastive construction.

See `results/analyses/bootstrap_same_form_domain_contrast_summary_surprise_surfacepool.csv`.

### 3.6 Observer-family check is positive but unresolved

As a bounded observer-family check, we used existing GPT-2 and GPT-2-medium prefcontrast artifacts for Aesthetic Appeal. This analysis tests absolute supervised alignment for the human-shaped Aesthetic Appeal readout under alternate GPT-2-family observers. It is not the full paired generic-vs-human-domain Stage 62 contrast, because GPT-2 Gutenberg and GPT-2 kfold-surface artifacts are not currently available.

Both alternate observers show positive point estimates, but neither 95% bootstrap interval excludes zero. GPT-2 has observed mean $\rho=+0.235$ with interval $[-0.078,+0.511]$, and GPT-2-medium has observed mean $\rho=+0.283$ with interval $[-0.045,+0.562]$. This suggests that the supervised human-shaped signal is not obviously unique to DistilGPT-2, but observer-family robustness remains unresolved.

See `results/analyses/bootstrap_observer_family_summary_aesthetic_observer.csv`.

### 3.7 Higher-rated poems are often more predictable

A separate item-level predictability diagnostic shows that higher-rated poems are often more predictable under the language model, not less. This is a useful boundary condition. Human-rated Surprise is not equivalent to language-model confusion. In this dataset, better or more surprising poems are not simply harder for a language model to predict. This weakens naive novelty-only interpretations and reinforces the need for domain-relative contrastive structure.

See Table 4, generated as `results/tables/table_4_item_nll_correlations.*`.

## 4. Discussion

### 4.1 What failed

The label-free compression-evaluator hypothesis failed. Generic literary domains do not recover human poetic appraisal as a resolved positive signal. This failure is not a nuisance result; it defines the boundary of the framework. The held-out domain $D$ is not an implementation detail. It is the source of the appraisal geometry.

A compression score can only be interpreted relative to the domain being compressed. If $D$ is generic, the score reflects generic literary predictability or typicality. If $D$ is preference-shaped, the score reflects the contrast encoded by that preference-shaped domain.

### 4.2 What survived

The domain-relative probing framework survives in a bounded form. When $D$ is built from human preference structure, structural compression readouts are positive and often align better than generic Gutenberg-domain readouts. However, the paired generic-vs-human contrast is mixed-form, because it compares contrastive human-shaped scores against single-domain generic scores. The same-form Surprise follow-up against a surface-pool contrast does not resolve, so the current evidence does not fully isolate human labels in $D$ from contrastive construction.

The convergence across targets is still useful, but mainly as an exploratory map. The result is not merely a Surprise artifact: Aesthetic Appeal, Surprise, and Creativity all show positive human-shaped contrastive scores relative to generic single-domain scores. But the strongest confirmatory statement remains the negative boundary result for generic compression and the matched-control mixed-form advantage, not a fully isolated multi-target domain-construction mechanism.

### 4.3 What the cross-target pattern suggests

The cross-target matrix suggests that human-shaped domains encode both shared and target-specific structure. Aesthetic Appeal behaves like a broad appraisal hub: it transfers to Surprise and Creativity under matched controls, while Surprise and Creativity transfer back into Aesthetic Appeal less cleanly. Surprise and Creativity transfer to each other under matched controls but not word-shuffle controls.

This supports a shared-appraisal interpretation rather than a pure silo interpretation. The domains appear to encode overlapping evaluative geometry, but each target sharpens the geometry differently. Word-shuffle controls are useful here because they ask a stricter question: whether the within-domain lexical/structural arrangement matters beyond target-shaped selection alone. Those controls resolve mainly in the cleanest self-domain cases.

### 4.4 Compression’s remaining role

Compression remains interesting, but the claim must be narrower. Compression has strong point estimates in several settings, and structural compression readouts outperform baselines by mean under no controls and under other-human-target residualization. However, the poem-level bootstrap does not resolve a unique compression advantage at the item level.

The matched-other diagnostic should first be interpreted as possible variance normalization: compression-gain estimates are noisy, so matched-control subtraction may help them more than it helps cosine-style similarities. The observed differences are positive, but unresolved under bootstrap. A compression-specific mechanism remains possible but is not established by the present data.

### 4.5 Implications for PoemForge

The practical implication is that PoemForge should not be framed as a label-free aesthetic evaluator. A more accurate framing is a domain construction and readout system. Its core capability is to build, audit, and compare domains that make a creative preference legible to different metrics.

In this framing, the main workflow is:

1. define a target domain;
2. construct human-shaped contrasts;
3. score candidates by their effect on held-out domain structure;
4. compare against generic and perturbed controls;
5. audit whether the induced signal generalizes across targets, controls, and observers.

The result is less sweeping than an unsupervised evaluator, but more scientifically useful. It turns aesthetic judgment into an experimentally manipulable domain-construction problem.

## 5. Limitations

The primary limitation is sample size. The final item-level analysis has $n=36$ poems, which is too small to resolve fine-grained differences between readout families. The bootstrap intervals make this limitation explicit.

A second limitation is domain specificity. The positive results depend on human-shaped contrastive domains. This is appropriate for supervised probing, but it means the results should not be generalized to unsupervised aesthetic discovery.

A third limitation is score-form confounding in the paired domain contrast. The main generic-vs-human contrast compares human-shaped `v_pref_struct` scores against generic `v_struct` scores. This is useful as a comparison between the full supervised contrastive construction and generic single-domain compression, but it does not isolate human labels in $D$ from contrastive scoring form. A same-form Surprise follow-up comparing human-labeled `v_pref_struct` against a surface-pool `v_pref_struct` contrast is positive but unresolved.

A fourth limitation is observer-family robustness. The strongest paired domain-contrast results use DistilGPT-2 score artifacts. A bounded GPT-2/GPT-2-medium check shows positive but unresolved Aesthetic Appeal alignment, but it does not reproduce the full paired generic-vs-human-domain contrast. A full observer-family replication would require generating GPT-2-family Gutenberg-domain and kfold-surface score artifacts.

A fifth limitation is control interpretation. Matched-control contrasts are robust across targets, while word-shuffle controls are stricter and less stable. We therefore treat word-shuffle resolution as stronger evidence when present, and we do not treat matched-control resolution alone as establishing structure beyond lexical or contrastive-form effects.

A sixth limitation is reproducibility depth. The current pipeline freezes and promotes several archived inferential artifacts rather than fully recomputing every expensive analysis from scratch. This is acceptable for a reproducibility bridge, but a final archival version should progressively replace frozen-result promotion with direct regeneration.


## 6. Conclusion

PoemForge began with a strong hypothesis: compression-progress over a held-out literary domain might provide a label-free proxy for poetic value. The evidence does not support that claim. Generic domains fail as resolved positive predictors of human poetic appraisal.

The surviving result is sharper but narrower. Generic literary compression fails as a resolved positive predictor of human poetic appraisal, and formal generic compression can anti-align with ratings. Human-shaped contrastive readouts are positive and outperform generic single-domain Gutenberg readouts under matched-control paired resampling, but this mixed-form contrast should not be treated as a fully isolated human-domain-construction mechanism. In the available same-form Surprise comparison, human-labeled contrastive scoring does not significantly outperform a surface-pool contrastive score.

The final claim is therefore domain-relative supervised probing, not label-free compression aesthetics. The decisive object is not the readout metric alone, but the held-out domain $D$. Compression remains a useful readout over that domain, but the human signal enters through domain construction.

## Reproducibility

All reported manuscript tables and figures are generated by the reproducibility pipeline. The pipeline freezes normalized data, domain artifacts, score artifacts, control features, inferential results, bootstrap summaries, manuscript tables, manuscript figures, and scaffold numeric diffs.

The main manuscript-facing artifacts are:

- `results/tables/table_1_readout_convergence.*`;
- `results/tables/table_2_bootstrap_uncertainty.*`;
- `results/tables/table_3_generic_d_summary.*`;
- `results/tables/table_4_item_nll_correlations.*`;
- `results/tables/table_5_absolute_effect_uncertainty.*`;
- `results/tables/table_6_domain_contrast_bootstrap.*`;
- `results/tables/table_7_domain_contrast_target_pair_matrix.*`;
- `results/tables/table_8_domain_contrast_by_control_family.*`;
- `results/analyses/bootstrap_same_form_domain_contrast_summary_surprise_surfacepool.csv`;
- `results/analyses/bootstrap_observer_family_summary_aesthetic_observer.csv`;
- `results/figures/figure_1_readout_convergence.*`;
- `results/figures/figure_2_bootstrap_uncertainty.*`;
- `results/diffs/scaffold_numeric_diff.csv`;
- `results/diffs/scaffold_diff_report.md`.

The final scaffold check verifies 39 canonical manuscript values against expected values with tolerance $10^{-9}$. All checks pass.
