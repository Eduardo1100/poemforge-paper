
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
