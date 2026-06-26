# External Validation Plan

The current result is primarily based on one rated poetry dataset with n = 36 items. Before strong submission, test whether the core triad replicates on at least one additional rated creative-writing dataset.

## Core triad

1. Generic D fails or misaligns.
2. Preference-shaped D works.
3. Compression, TF-IDF, and embedding readouts converge under controls.

## Protocol

1. Add a dataset loader.
2. Normalize to `item_id`, `text`, and target columns.
3. Run the same domain construction.
4. Run the same readouts.
5. Run the same controls.
6. Run the same bootstrap.
7. Compare triad status.

Do not introduce a new metric or special-case the new dataset until after this validation attempt.
