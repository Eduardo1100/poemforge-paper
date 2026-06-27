
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

## Target robustness: Aesthetic_Appeal self-domain, full run

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
Aesthetic_Appeal shows the strongest target-robustness pattern so far: generic Gutenberg domains do not yield resolved positive absolute alignment, while human-shaped target-specific domains produce resolved paired improvements over generic domains under all tested control settings.

## Target robustness: Creativity self-domain, full run

Full result, n_boot=5000:

Generic absolute Creativity effects:
- Accessible Gutenberg / matched-other: observed rho = -0.184, CI [-0.489, +0.143], unresolved
- Accessible Gutenberg / word-shuffle: observed rho = +0.174, CI [-0.201, +0.515], unresolved
- Formal Gutenberg / matched-other: observed rho = -0.352, CI [-0.582, -0.069], resolved negative
- Formal Gutenberg / word-shuffle: observed rho = +0.174, CI [-0.188, +0.501], unresolved

Paired supervised-vs-generic domain contrasts:
- Accessible Gutenberg / matched-other: Δrho = +0.525, CI [+0.125, +0.886], resolved
- Accessible Gutenberg / word-shuffle: Δrho = +0.167, CI [-0.282, +0.616], unresolved
- Formal Gutenberg / matched-other: Δrho = +0.692, CI [+0.235, +1.064], resolved
- Formal Gutenberg / word-shuffle: Δrho = +0.167, CI [-0.312, +0.646], unresolved

Interpretation:
Creativity supports the matched-control version of the domain-construction effect but not the stronger word-shuffle robustness claim. The emerging cross-target result is therefore: human-shaped domains consistently beat generic domains under matched-control paired item bootstrap across Surprise, Aesthetic_Appeal, and Creativity, while word-shuffle robustness varies by target.
