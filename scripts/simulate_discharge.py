import argparse
import time
import random
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))


def simulate_discharges(count: int = 50):
    print(f"\n================ CLAIMFLOW DISCHARGE SIMULATION ================")
    print(f"Simulating {count} concurrent/sequential patient discharges...")
    print("----------------------------------------------------------------")

    outcomes = {"AUTO_SETTLE": 0, "PARTIAL_SETTLE": 0, "HUMAN_REVIEW": 0, "SIU_ESCALATE": 0}

    for i in range(1, count + 1):
        claim_id = f"CLM-SIM-{i:04d}"
        roll = random.random()
        if roll < 0.70:
            outcome = "AUTO_SETTLE"
            status_symbol = "[APPROVED]"
            color_code = "GREEN"
        elif roll < 0.85:
            outcome = "PARTIAL_SETTLE"
            status_symbol = "[PARTIAL]"
            color_code = "AMBER"
        elif roll < 0.96:
            outcome = "HUMAN_REVIEW"
            status_symbol = "[REVIEW]"
            color_code = "RED"
        else:
            outcome = "SIU_ESCALATE"
            status_symbol = "[SIU HOLD]"
            color_code = "DARK_RED"

        outcomes[outcome] += 1
        elapsed_sec = random.uniform(1.2, 4.5)
        print(f"[{i:02d}/{count:02d}] Claim {claim_id}: {status_symbol:<15} ({color_code}) | Latency: {elapsed_sec:.2f}s")
        time.sleep(0.02)  # Fast simulated progress

    print("\n---------------------- SUMMARY RESULTS -------------------------")
    print(f"Total Discharges Processed: {count}")
    print(f"Auto-Settled (Green):       {outcomes['AUTO_SETTLE']:>3} ({outcomes['AUTO_SETTLE']/count:.1%})")
    print(f"Partial / Query (Amber):    {outcomes['PARTIAL_SETTLE']:>3} ({outcomes['PARTIAL_SETTLE']/count:.1%})")
    print(f"Human Review (Red):         {outcomes['HUMAN_REVIEW']:>3} ({outcomes['HUMAN_REVIEW']/count:.1%})")
    print(f"SIU Escalation (Dark Red):  {outcomes['SIU_ESCALATE']:>3} ({outcomes['SIU_ESCALATE']/count:.1%})")
    print("================================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate hospital discharge claims.")
    parser.add_argument("--count", type=int, default=50, help="Number of discharge claims to simulate.")
    args = parser.parse_args()
    simulate_discharges(count=args.count)
