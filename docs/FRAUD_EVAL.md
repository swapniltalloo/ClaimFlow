# ClaimFlow Fraud Detection Evaluation & Metrics

## 1. Evaluation Targets

For each of the 8 fraud patterns, ClaimFlow targets:
- **Precision:** $\ge 0.90$ (minimize false accusations against honest hospitals)
- **Recall:** $\ge 0.85$ (catch at least 85% of illicit or inflated billing attempts)
- **F1-Score:** $\ge 0.87$
- **Inference Latency:** $\le 15$ seconds per claim for multi-layer scoring

---

## 2. Benchmark Matrix

| Pattern ID | Pattern Description | Detection Mechanism | Target Precision | Target Recall | Target F1 |
|---|---|---|---|---|---|
| **FR-001** | Upcoding | Coding Matrix + Clinical NLP | 0.92 | 0.88 | 0.90 |
| **FR-002** | Unbundling | Deterministic Bundling Matrix | 0.98 | 0.95 | 0.96 |
| **FR-003** | Phantom Services | Cross-validation against EHR NLP | 0.94 | 0.90 | 0.92 |
| **FR-004** | Length-of-Stay Inflation | Timestamp Math vs. Billed Units | 0.99 | 0.98 | 0.98 |
| **FR-005** | Duplicate Billing | Hash & Exact Match Rule | 0.99 | 0.98 | 0.98 |
| **FR-006** | Diagnosis-Procedure Mismatch | ICD10-CPT Matrix | 0.95 | 0.92 | 0.93 |
| **FR-007** | Exclusion / Waiting Period | Policy Tenure Evaluation | 0.96 | 0.94 | 0.95 |
| **FR-008** | Price Inflation | Z-Score / Regional Tariff Distribution | 0.90 | 0.86 | 0.88 |

---

## 3. Ground Truth Evaluation Workflow
1. Synthesize 2,000 ground-truth labeled claims (`scripts/generate_synthetic_data.py`).
2. Run Fraud Engine scoring.
3. Compare model outputs (`risk_score >= 60` or pattern verdicts) with ground-truth labels.
4. Output confusion matrices and classification reports per pattern.
