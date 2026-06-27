
## Target robustness: Aesthetic Appeal self-domain

Question:
Does the paired generic-vs-supervised domain contrast survive when the target is Aesthetic_Appeal rather than Surprise?

Command:
python pipeline/62_bootstrap_domain_contrast.py \
  --target Aesthetic_Appeal \
  --pool-target Aesthetic_Appeal \
  --generic-metric v_struct \
  --supervised-metric v_pref_struct \
  --n-boot 100 \
  --seed 123 \
  --tag aesthetic_self_smoke

Interpretation:
TBD after inspecting smoke-test output.

Full result, n_boot=5000:

Generic absolute Aesthetic_Appeal effects remain unresolved:
- Accessible Gutenberg / matched-other: observed rho = -0.072, CI [-0.440, +0.304]
- Accessible Gutenberg / word-shuffle: observed rho = -0.090, CI [-0.430, +0.258]
- Formal Gutenberg / matched-other: observed rho = -0.247, CI [-0.560, +0.091]
- Formal Gutenberg / word-shuffle: observed rho = -0.032, CI [-0.362, +0.293]

Paired supervised-vs-generic domain contrasts all resolve positive:
- Accessible Gutenberg / matched-other: Δrho = +0.547, CI [+0.111, +0.961]
- Accessible Gutenberg / word-shuffle: Δrho = +0.565, CI [+0.165, +0.907]
- Formal Gutenberg / matched-other: Δrho = +0.723, CI [+0.290, +1.081]
- Formal Gutenberg / word-shuffle: Δrho = +0.507, CI [+0.122, +0.849]

Interpretation:
The domain-construction effect is not Surprise-specific. Aesthetic_Appeal shows the same qualitative pattern: generic Gutenberg domains do not yield resolved positive absolute alignment, while human-shaped target-specific domains produce resolved paired improvements over generic domains under all tested control settings.
