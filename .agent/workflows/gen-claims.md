# Workflow: /gen-claims

Generates batches of clinically coherent synthetic claims with ground-truth labeled fraud patterns.

## Steps
1. Execute `python scripts/generate_synthetic_data.py --count 2000 --fraud-rate 0.15`.
2. Verify generation summary and fraud distribution (`python scripts/verify_dataset.py`).
3. Output dataset stored at `data/synthetic/claims.parquet` and `data/synthetic/fhir_bundles/`.
