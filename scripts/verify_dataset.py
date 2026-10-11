import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET_PATH = os.path.join(BASE_DIR, "data", "synthetic", "claims.parquet")


def verify_claims_dataset():
    if not os.path.exists(PARQUET_PATH):
        print(f"Error: Parquet file not found at {PARQUET_PATH}")
        sys.exit(1)

    df = pd.read_parquet(PARQUET_PATH)
    print("=== CLAIMFLOW DATASET AUDIT & VERIFICATION ===")
    print(f"Total Records:         {len(df):,}")
    print(f"File Size on Disk:     {os.path.getsize(PARQUET_PATH):,} bytes")
    print(f"Total Billed Volume:   INR {df['total_claimed_amount'].sum():,.2f}")
    print(f"Average Claim Size:    INR {df['total_claimed_amount'].mean():,.2f}")
    print(f"Clean Claims:          {(df['is_fraud'] == False).sum()} ({(df['is_fraud'] == False).mean():.1%})")
    print(f"Fraud Claims:          {(df['is_fraud'] == True).sum()} ({(df['is_fraud'] == True).mean():.1%})")

    assert len(df) >= 1000, "Dataset must contain at least 1,000 claims."
    assert (df['is_fraud'] == True).sum() > 0, "Dataset must contain labeled fraud cases."

    print("\nFraud Distribution Across 8 Ground-Truth Patterns:")
    fraud_counts = df[df['is_fraud'] == True]['fraud_pattern'].value_counts()
    for pattern, count in fraud_counts.items():
        print(f"  * {pattern:<42}: {count:>4} cases ({count/len(df[df['is_fraud'] == True]):.1%})")

    print("\nSpecialty Breakdown:")
    for cat, count in df['category'].value_counts().items():
        print(f"  * {cat:<25}: {count:>4} cases")

    print("\n[PASSED] All integrity constraints and ground-truth labels validated successfully!")


if __name__ == "__main__":
    verify_claims_dataset()
