# Workflow: /new-fraud-rule

Scaffolds a new deterministic fraud detection rule, including the rule class implementation, unit test, and documentation update.

## Steps
1. Define the rule specification in `docs/FRAUD_RULES.md` with:
   - Unique Rule ID (e.g. `FR-009`)
   - Detection category (Upcoding, Unbundling, Phantom, Tariff, etc.)
   - Severity / penalty score (0-100)
2. Implement the rule class in `backend/app/rules/` inheriting from `BaseRule`.
3. Create corresponding unit tests in `backend/tests/test_rules.py` covering true-positive and true-negative cases.
4. Register the rule in the Fraud Engine rule registry.
