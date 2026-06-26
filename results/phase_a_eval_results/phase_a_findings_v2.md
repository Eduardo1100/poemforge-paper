# Phase A Findings v2

## Setup

PoemForge Phase A tested whether compression-progress over observer language models predicts human aesthetic response to poems.

Core score:

    V(a | H) = L(D | O + H) - L(D | O + H + a)

implemented as bits-per-byte NLL reduction on held-out domain D.

Observer:

- distilgpt2

Eval set:

- 46 rated poems total
- 36 Chaudhuri 2024 human poems
- 10 Porter/Machery poems, 5 AI and 5 human

Primary clean slice:

- Chaudhuri human-only, n=36

D variants:

- random Gutenberg-D
- accessible Gutenberg-D heuristic subset
- formal Gutenberg-D heuristic subset

Controls:

- line_shuffle
- word_shuffle
- matched_other

Baselines:

- word_len
- is_ai

## Rating reliability

Human ratings are reliable enough to evaluate against.

Chaudhuri Spearman-Brown reliability:

- Aesthetic_Appeal ≈ 0.834
- Clarity ≈ 0.917
- Creativity ≈ 0.624
- Felt_Arousal ≈ 0.659
- Felt_Valence ≈ 0.868
- Surprise ≈ 0.692

Therefore, the near-zero or negative V results are not easily explained by rating unreliability.

## Per-dimension analysis

The pooled composite does not appear to hide a strong positive v_struct signal.

For Chaudhuri:

- Aesthetic_Appeal v_struct ≈ -0.114
- Creativity v_struct ≈ +0.079

Porter contains larger apparent effects, especially witty/original, but Porter has n=10 and a severe AI/authorship confound.

## Synthetic ladder

On synthetic degradation ladder v0:

- word-shuffle control gives positive v_struct
- line-shuffle control does not

Interpretation:

The scorer detects local lexical/syntactic coherence and degradation, but not global poetic order or aesthetic preference.

## D mismatch result

D choice strongly affects v_raw.

On Chaudhuri human-only:

Accessible Gutenberg-D:

- v_raw ≈ -0.300
- v_struct with word-shuffle ≈ -0.008

Formal Gutenberg-D:

- v_raw ≈ -0.454
- v_struct with word-shuffle ≈ -0.007

Interpretation:

Accessible-D weakens the raw anti-correlation; formal-D intensifies it. V is domain-relative.

## Matched-other control result

Matched-other control compares each poem to a similar-length poem from the same dataset.

On Chaudhuri human-only:

Accessible Gutenberg-D + matched_other:

- v_raw ≈ -0.300
- v_ctrl ≈ -0.012
- v_struct ≈ -0.223

Formal Gutenberg-D + matched_other:

- v_raw ≈ -0.454
- v_ctrl ≈ +0.134
- v_struct ≈ -0.365

Interpretation:

Higher-rated Chaudhuri poems condition Gutenberg-D worse than similar-length matched poems, especially for formal-D.

This is not merely a null result. It is evidence of domain-relative anti-alignment.

## Current conclusion

The simple Phase A compression-progress score does not predict human aesthetic preference on the current target.

More precisely:

- v_raw measures domain compatibility.
- v_struct can detect degradation/local coherence under word-shuffle controls.
- matched-other residuals are negative for the clean Chaudhuri human-only slice.
- Gutenberg-D induces a value landscape anti-aligned with contemporary human aesthetic response.

## Revised hypothesis

Compression-progress is not a universal beauty detector.

It is a domain-relative compatibility measure whose apparent value depends on:

- observer model
- held-out domain D
- control family
- human target construction

The next research question is not whether V finds beauty in general, but whether a preference-aligned D or richer observer population can induce a value landscape that tracks human preference.

## Next steps

1. Stop tuning distilgpt2 + Gutenberg-D.
2. Build a genuinely contemporary/accessibility-matched D.
3. Build a preference-shaped D from pairwise winners or high-rated poems.
4. Expand evaluation with matched pairs:
   - same topic
   - same length
   - same form
   - different quality
5. Only then test larger observers.
