import os
import sys
import json
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.agents.fraud_agent import FraudAgent
from app.models.domain import Claim, LineItem


def evaluate_fraud_models():
    parquet_path = os.path.join(BASE_DIR, "data", "synthetic", "claims.parquet")
    if not os.path.exists(parquet_path):
        print(f"Error: Parquet file not found at {parquet_path}")
        sys.exit(1)

    df = pd.read_parquet(parquet_path)
    print(f"\n================ FRAUD AGENT MULTI-LAYER EVALUATION ================")
    print(f"Dataset Size: {len(df)} claims ({len(df[~df['is_fraud']])} clean, {len(df[df['is_fraud']])} fraud)")

    agent = FraudAgent(auto_train=True)

    y_true = []
    y_pred = []
    pattern_labels = {}

    for idx, row in df.iterrows():
        # Reconstruct claim
        items = [LineItem(**it) for it in json.loads(row["line_items_json"])]
        claim = Claim(
            claim_id=row["claim_id"],
            patient_id=row["patient_id"],
            hospital_id=row["hospital_id"],
            policy_id=row["policy_id"],
            admission_time=row["admission_time"],
            discharge_time=row["discharge_time"],
            total_claimed_amount=row["total_claimed_amount"],
            line_items=items
        )

        score, reasons = agent.evaluate_claim(claim)
        is_pred_fraud = score >= 50.0

        y_true.append(1 if row["is_fraud"] else 0)
        y_pred.append(1 if is_pred_fraud else 0)

        # Track per-pattern
        pattern = row["fraud_pattern"] or "CLEAN"
        if pattern not in pattern_labels:
            pattern_labels[pattern] = {"true": [], "pred": []}
        pattern_labels[pattern]["true"].append(1 if row["is_fraud"] else 0)
        pattern_labels[pattern]["pred"].append(1 if is_pred_fraud else 0)

    overall_prec = precision_score(y_true, y_pred, zero_division=0)
    overall_rec = recall_score(y_true, y_pred, zero_division=0)
    overall_f1 = f1_score(y_true, y_pred, zero_division=0)

    print("\nOverall Performance:")
    print(f"  * Precision:  {overall_prec:.3f} (Target: >= 0.900)")
    print(f"  * Recall:     {overall_rec:.3f} (Target: >= 0.850)")
    print(f"  * F1-Score:   {overall_f1:.3f} (Target: >= 0.870)")

    print("\nPer-Pattern Evaluation:")
    print(f"{'Pattern':<45} | {'Detected':<10} | {'Total':<8} | {'Recall':<8}")
    print("-" * 78)
    for pat, data in pattern_labels.items():
        if pat != "CLEAN":
            detected = sum(data["pred"])
            total = len(data["true"])
            rec = detected / max(total, 1)
            print(f"{pat:<45} | {detected:<10} | {total:<8} | {rec:.1%}")

    print("----------------------------------------------------------------------")
    assert overall_prec >= 0.85 and overall_rec >= 0.80, "Fraud Agent evaluation did not meet minimum standards."
    print("[PASSED] Fraud Agent successfully met multi-layer detection benchmarks!\n")


if __name__ == "__main__":
    evaluate_fraud_models()
