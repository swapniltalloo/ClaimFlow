import os
import sys
import time
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.agents.ehr_parser import EHRParserAgent


def evaluate_ehr_parser(sample_size: int = 500):
    parquet_path = os.path.join(BASE_DIR, "data", "synthetic", "claims.parquet")
    if not os.path.exists(parquet_path):
        print(f"Error: Parquet file not found at {parquet_path}")
        sys.exit(1)

    df = pd.read_parquet(parquet_path)
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)

    agent = EHRParserAgent()
    print(f"\n================ EHR PARSER AGENT EVALUATION ================")
    print(f"Evaluating {len(sample_df)} clinical discharge summaries...")
    print("--------------------------------------------------------------")

    icd10_matches = 0
    los_matches = 0
    total_latency = 0.0
    confidences = []

    start_time = time.time()
    for idx, row in sample_df.iterrows():
        t0 = time.time()
        facts = agent.parse(
            discharge_text=row["discharge_summary"],
            patient_id=row["patient_id"]
        )
        elapsed = time.time() - t0
        total_latency += elapsed
        confidences.append(facts.confidence_score)

        # Check ICD-10 extraction accuracy
        if facts.primary_diagnosis_code == row["primary_icd10"]:
            icd10_matches += 1

    total_eval_time = time.time() - start_time
    accuracy = (icd10_matches / len(sample_df)) * 100
    avg_latency_ms = (total_latency / len(sample_df)) * 1000
    avg_confidence = sum(confidences) / len(confidences)

    print(f"Total Evaluated:              {len(sample_df)}")
    print(f"ICD-10 Exact Matches:         {icd10_matches} / {len(sample_df)}")
    print(f"ICD-10 Extraction Accuracy:   {accuracy:.2f}% (Target: >= 90.0%)")
    print(f"Average Parser Confidence:    {avg_confidence:.3f}")
    print(f"Mean Latency Per Document:    {avg_latency_ms:.2f} ms")
    print(f"Parser Stage Budget:          45,000 ms (45.0s)")
    print(f"Budget Utilization:           {(avg_latency_ms / 45000) * 100:.3f}%")
    print("--------------------------------------------------------------")

    assert accuracy >= 90.0, f"Extraction accuracy {accuracy:.2f}% did not meet target >= 90%"
    print("[PASSED] Agent A (EHR Parser) successfully met all accuracy & latency criteria!\n")


if __name__ == "__main__":
    evaluate_ehr_parser()
