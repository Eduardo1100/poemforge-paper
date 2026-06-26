# Phase A Checkpoint

## Current status

PoemForge Phase A has a working compression-progress scoring harness for poetry.

## Data

- 46 rated poems:
  - 36 Chaudhuri 2024 human poems
  - 5 Porter/Machery human poems
  - 5 Porter/Machery AI poems
- External D:
  - 512 Gutenberg Poetry Corpus chunks
  - 328 unique Gutenberg IDs
  - 0.0 eval 5-gram overlap
- Synthetic ladder v0:
  - original
  - line_shuffle
  - bad_template
  - word_shuffle
  - random_salad

## Observer

- distilgpt2
- bits-per-UTF-8-byte NLL
- token-exact prefix/sample scoring

## Main result so far

Against Gutenberg-D, raw compression gain is strongly and stably anti-correlated with the current human aesthetic target.

With word-shuffle control on the 46-item human target:

- v_raw mean rho ≈ -0.506
- v_ctrl mean rho ≈ -0.321
- v_struct mean rho ≈ -0.117
- word_len rho ≈ 0.166
- is_ai rho ≈ 0.397

On Chaudhuri human-only:

- v_raw mean rho ≈ -0.497
- v_ctrl mean rho ≈ -0.362
- v_struct mean rho ≈ -0.062
- word_len rho ≈ 0.176

On synthetic ladder v0 with word-shuffle control:

- v_raw rho ≈ 0.417
- v_ctrl rho ≈ 0.258
- v_struct rho ≈ 0.325

## Current interpretation

The current V formulation detects local coherence and domain compatibility, but has not shown evidence of predicting fine-grained human aesthetic preference.

This is not yet a clean negative result because:
- Gutenberg-D may be distribution-mismatched to the human target.
- Porter and Chaudhuri ratings should not be pooled as the main target.
- The human-rating noise ceiling has not yet been measured.
- n=36–46 is underpowered for claiming a true near-zero effect.

## Next priority

Compute rating reliability / noise ceiling from the raw rating rows.
