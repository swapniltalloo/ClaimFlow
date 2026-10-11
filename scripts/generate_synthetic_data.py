import os
import sys
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import pandas as pd

# Load reference datasets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_REF_DIR = os.path.join(BASE_DIR, "data", "reference")
POLICIES_DIR = os.path.join(BASE_DIR, "data", "policies")
OUTPUT_SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
FHIR_OUTPUT_DIR = os.path.join(OUTPUT_SYNTHETIC_DIR, "fhir_bundles")

os.makedirs(OUTPUT_SYNTHETIC_DIR, exist_ok=True)
os.makedirs(FHIR_OUTPUT_DIR, exist_ok=True)

with open(os.path.join(DATA_REF_DIR, "icd10_codes.json"), "r") as f:
    ICD10_CATALOG = json.load(f)

with open(os.path.join(DATA_REF_DIR, "procedure_tariffs.json"), "r") as f:
    TARIFFS = json.load(f)
    TARIFF_MAP = {item["code"]: item for item in TARIFFS}

with open(os.path.join(DATA_REF_DIR, "bundling_matrix.json"), "r") as f:
    BUNDLING_RULES = json.load(f)

POLICY_FILES = [
    "silver_health_plan.json",
    "gold_comprehensive.json",
    "corporate_floater.json"
]
POLICIES = []
for pfile in POLICY_FILES:
    with open(os.path.join(POLICIES_DIR, pfile), "r") as f:
        POLICIES.append(json.load(f))

HOSPITALS = [
    {"id": "HOSP-001", "name": "Apollo Super Specialty Hospital", "tier": "METRO_T1"},
    {"id": "HOSP-002", "name": "Fortis Escorts Heart & Surgical Institute", "tier": "METRO_T1"},
    {"id": "HOSP-003", "name": "Max Healthcare Multispecialty", "tier": "METRO_T1"},
    {"id": "HOSP-004", "name": "City Metro General Hospital", "tier": "TIER_2"},
    {"id": "HOSP-005", "name": "Sunrise Community Health Care", "tier": "TIER_2"}
]

FIRST_NAMES = ["Aarav", "Vihaan", "Aditya", "Rohan", "Suresh", "Priya", "Ananya", "Sneha", "Kavita", "Pooja", "Vikram", "Neha", "Rahul", "Deepak"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Gupta", "Mehta", "Iyer", "Nair", "Kulkarni", "Singh", "Reddy", "Chopra", "Deshmukh"]

FRAUD_PATTERNS = [
    "FR-001_UPCODING",
    "FR-002_UNBUNDLING",
    "FR-003_PHANTOM_SERVICES",
    "FR-004_LOS_INFLATION",
    "FR-005_DUPLICATE_BILLING",
    "FR-006_DIAGNOSIS_PROCEDURE_MISMATCH",
    "FR-007_EXCLUSION_WAITING_PERIOD_VIOLATION",
    "FR-008_PRICE_INFLATION"
]


def generate_discharge_summary(patient_name: str, uhid: str, diag: Dict[str, Any], admit_dt: datetime, disch_dt: datetime, los_days: int, icu_days: int, procedures: List[str]) -> str:
    summary = f"""================================================================================
                    DISCHARGE SUMMARY & CLINICAL RECORD
HOSPITAL: {random.choice(HOSPITALS)['name']}
PATIENT: {patient_name}   | UHID: {uhid}   | AGE: {random.randint(22, 74)}   | GENDER: {random.choice(['Male', 'Female'])}
ADMISSION DATE: {admit_dt.strftime('%d-%b-%Y %H:%M')}
DISCHARGE DATE: {disch_dt.strftime('%d-%b-%Y %H:%M')}
LENGTH OF STAY: {los_days} Days (Room Days: {max(0, los_days - icu_days)}, ICU Days: {icu_days})
================================================================================

CHIEF COMPLAINTS & PRESENTATION:
Patient presented with acute onset symptoms consistent with {diag['name']} ({diag['code']}).
Physical examination and diagnostic workup revealed acute clinical findings requiring immediate inpatient care.

CLINICAL COURSE & MANAGEMENT:
Patient was admitted under {diag['category']}. Monitored closely for hemodynamic parameters.
{"Patient required critical care monitoring in ICU for " + str(icu_days) + " days." if icu_days > 0 else "Patient maintained stable vitals in private room accommodation."}

PROCEDURES PERFORMED:
{', '.join(procedures) if procedures else 'Supportive inpatient medical management and intravenous medications.'}

HOSPITAL COURSE & RECOVERY:
Post-procedural recovery was uneventful. Pain controlled on oral analgesics. Surgical wound clean and dry, healing by primary intention.
Afebrile for >24 hours prior to discharge. Systemic examination within normal limits.

DISCHARGE MEDICATIONS:
1. Oral broad spectrum antibiotics x 5 days
2. Analgesic / anti-inflammatory tabs as needed
3. Supportive multi-vitamin therapy

CONDITION AT DISCHARGE: Hemodynamically stable, ambulating, fit for discharge.
ATTENDING PHYSICIAN: Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}, MD/MS
================================================================================
"""
    return summary


def create_synthetic_claim(claim_idx: int, inject_fraud: bool, fraud_type: str = None) -> Dict[str, Any]:
    patient_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    uhid = f"UHID-{random.randint(10000000, 99999999)}"
    patient_id = f"PAT-{random.randint(10000, 99999)}"
    claim_id = f"CLM-2026-{claim_idx:05d}"
    hospital = random.choice(HOSPITALS)
    policy = random.choice(POLICIES)

    # Pick a clinical diagnosis
    diag = random.choice(ICD10_CATALOG)
    base_los = diag["expected_los_days"]
    icu_days = diag["typical_icu_days"]
    room_days = max(1, base_los - icu_days)
    total_days = room_days + icu_days

    # Set dates
    days_ago = random.randint(1, 90)
    admit_time = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(1, 8))
    discharge_time = admit_time + timedelta(days=total_days, hours=random.randint(2, 6))

    line_items = []
    line_no = 1
    procedures_billed = []
    fraud_pattern_fired = None
    fraud_lines = []

    # 1. Room line item
    room_tariff = TARIFF_MAP["ROOM-STD-PVT"]
    line_items.append({
        "line_number": line_no,
        "service_date": admit_time.isoformat(),
        "item_type": "ROOM_ICU",
        "code": "ROOM-STD-PVT",
        "description": room_tariff["description"],
        "quantity": float(room_days),
        "unit_price": room_tariff["median_price"],
        "total_amount": float(room_days * room_tariff["median_price"]),
        "verdict": "PENDING",
        "verdict_reasons": [],
        "clause_citations": [],
        "is_fraudulent": False,
        "injected_fraud_pattern": None
    })
    line_no += 1

    # 2. ICU line item if applicable
    if icu_days > 0:
        icu_tariff = TARIFF_MAP["ROOM-ICU-BED"]
        line_items.append({
            "line_number": line_no,
            "service_date": admit_time.isoformat(),
            "item_type": "ROOM_ICU",
            "code": "ROOM-ICU-BED",
            "description": icu_tariff["description"],
            "quantity": float(icu_days),
            "unit_price": icu_tariff["median_price"],
            "total_amount": float(icu_days * icu_tariff["median_price"]),
            "verdict": "PENDING",
            "verdict_reasons": [],
            "clause_citations": [],
            "is_fraudulent": False,
            "injected_fraud_pattern": None
        })
        line_no += 1

    # 3. Main procedure if applicable
    std_procs = diag.get("standard_procedures", [])
    primary_cpt = None
    if std_procs and std_procs[0].startswith("CPT-"):
        primary_cpt = std_procs[0]
        cpt_tariff = TARIFF_MAP.get(primary_cpt, {
            "code": primary_cpt,
            "description": "Standard Surgical Procedure",
            "median_price": 50000.0
        })
        procedures_billed.append(primary_cpt)
        line_items.append({
            "line_number": line_no,
            "service_date": (admit_time + timedelta(hours=6)).isoformat(),
            "item_type": "PROCEDURE",
            "code": primary_cpt,
            "description": cpt_tariff["description"],
            "quantity": 1.0,
            "unit_price": cpt_tariff["median_price"],
            "total_amount": cpt_tariff["median_price"],
            "verdict": "PENDING",
            "verdict_reasons": [],
            "clause_citations": [],
            "is_fraudulent": False,
            "injected_fraud_pattern": None
        })
        line_no += 1

    # 4. Routine Lab & Medications
    cbc_tariff = TARIFF_MAP["LAB-CBC-PLATE"]
    line_items.append({
        "line_number": line_no,
        "service_date": admit_time.isoformat(),
        "item_type": "INVESTIGATION",
        "code": "LAB-CBC-PLATE",
        "description": cbc_tariff["description"],
        "quantity": 2.0,
        "unit_price": cbc_tariff["median_price"],
        "total_amount": 2.0 * cbc_tariff["median_price"],
        "verdict": "PENDING",
        "verdict_reasons": [],
        "clause_citations": [],
        "is_fraudulent": False,
        "injected_fraud_pattern": None
    })
    line_no += 1

    med_tariff = TARIFF_MAP["MED-IV-ABX"]
    line_items.append({
        "line_number": line_no,
        "service_date": admit_time.isoformat(),
        "item_type": "MEDICATION",
        "code": "MED-IV-ABX",
        "description": med_tariff["description"],
        "quantity": float(base_los),
        "unit_price": med_tariff["median_price"],
        "total_amount": float(base_los * med_tariff["median_price"]),
        "verdict": "PENDING",
        "verdict_reasons": [],
        "clause_citations": [],
        "is_fraudulent": False,
        "injected_fraud_pattern": None
    })
    line_no += 1

    # Injected Fraud Implementation
    if inject_fraud and fraud_type:
        fraud_pattern_fired = fraud_type

        if fraud_type == "FR-001_UPCODING":
            # Upcode uncomplicated appendectomy (CPT-44970) to complicated peritonitis (CPT-44960)
            for item in line_items:
                if item["item_type"] == "PROCEDURE":
                    item["code"] = "CPT-44960"
                    item["description"] = TARIFF_MAP["CPT-44960"]["description"]
                    item["unit_price"] = TARIFF_MAP["CPT-44960"]["median_price"]
                    item["total_amount"] = item["unit_price"]
                    item["is_fraudulent"] = True
                    item["injected_fraud_pattern"] = fraud_type
                    fraud_lines.append(item["line_number"])
                    break

        elif fraud_type == "FR-002_UNBUNDLING":
            # Add bundled component codes alongside primary procedure
            bundled_extra = {
                "line_number": line_no,
                "service_date": (admit_time + timedelta(hours=6)).isoformat(),
                "item_type": "PROCEDURE",
                "code": "CPT-49080",
                "description": "Peritoneal lavage / irrigation (Unbundled component)",
                "quantity": 1.0,
                "unit_price": 14500.0,
                "total_amount": 14500.0,
                "verdict": "PENDING",
                "verdict_reasons": [],
                "clause_citations": [],
                "is_fraudulent": True,
                "injected_fraud_pattern": fraud_type
            }
            line_items.append(bundled_extra)
            fraud_lines.append(line_no)
            line_no += 1

        elif fraud_type == "FR-003_PHANTOM_SERVICES":
            # Bill serial ABG tests and abdominal CT scan with zero mention in EHR
            phantom_item = {
                "line_number": line_no,
                "service_date": (admit_time + timedelta(days=1)).isoformat(),
                "item_type": "INVESTIGATION",
                "code": "LAB-ABG-SERIAL",
                "description": TARIFF_MAP["LAB-ABG-SERIAL"]["description"],
                "quantity": 4.0,
                "unit_price": TARIFF_MAP["LAB-ABG-SERIAL"]["median_price"],
                "total_amount": 4.0 * TARIFF_MAP["LAB-ABG-SERIAL"]["median_price"],
                "verdict": "PENDING",
                "verdict_reasons": [],
                "clause_citations": [],
                "is_fraudulent": True,
                "injected_fraud_pattern": fraud_type
            }
            line_items.append(phantom_item)
            fraud_lines.append(line_no)
            line_no += 1

        elif fraud_type == "FR-004_LOS_INFLATION":
            # Inflate room days from 2 to 7 days
            for item in line_items:
                if item["code"] == "ROOM-STD-PVT":
                    item["quantity"] += 5.0
                    item["total_amount"] = item["quantity"] * item["unit_price"]
                    item["is_fraudulent"] = True
                    item["injected_fraud_pattern"] = fraud_type
                    fraud_lines.append(item["line_number"])
                    break

        elif fraud_type == "FR-005_DUPLICATE_BILLING":
            # Duplicate the antibiotic medication line item
            dup_item = dict(line_items[-1])
            dup_item["line_number"] = line_no
            dup_item["is_fraudulent"] = True
            dup_item["injected_fraud_pattern"] = fraud_type
            line_items.append(dup_item)
            fraud_lines.append(line_no)
            line_no += 1

        elif fraud_type == "FR-006_DIAGNOSIS_PROCEDURE_MISMATCH":
            # Billed knee arthroscopy for Dengue or Respiratory infection
            mismatch_item = {
                "line_number": line_no,
                "service_date": (admit_time + timedelta(hours=12)).isoformat(),
                "item_type": "PROCEDURE",
                "code": "CPT-29888",
                "description": TARIFF_MAP["CPT-29888"]["description"],
                "quantity": 1.0,
                "unit_price": TARIFF_MAP["CPT-29888"]["median_price"],
                "total_amount": TARIFF_MAP["CPT-29888"]["median_price"],
                "verdict": "PENDING",
                "verdict_reasons": [],
                "clause_citations": [],
                "is_fraudulent": True,
                "injected_fraud_pattern": fraud_type
            }
            line_items.append(mismatch_item)
            fraud_lines.append(line_no)
            line_no += 1

        elif fraud_type == "FR-007_EXCLUSION_WAITING_PERIOD_VIOLATION":
            # Associate claim with Silver plan and policy inception only 5 days ago
            policy = POLICIES[0]  # Silver plan has 30-day waiting period
            admit_time = datetime.now(timezone.utc) - timedelta(days=5)
            discharge_time = admit_time + timedelta(days=base_los)
            for item in line_items:
                if item["item_type"] == "PROCEDURE":
                    item["is_fraudulent"] = True
                    item["injected_fraud_pattern"] = fraud_type
                    fraud_lines.append(item["line_number"])

        elif fraud_type == "FR-008_PRICE_INFLATION":
            # Inflate consumable kit to 3.5x standard price (> 2 sigma)
            inflated_item = {
                "line_number": line_no,
                "service_date": admit_time.isoformat(),
                "item_type": "CONSUMABLE",
                "code": "CONS-SURG-KIT",
                "description": TARIFF_MAP["CONS-SURG-KIT"]["description"],
                "quantity": 1.0,
                "unit_price": TARIFF_MAP["CONS-SURG-KIT"]["median_price"] * 3.5,
                "total_amount": TARIFF_MAP["CONS-SURG-KIT"]["median_price"] * 3.5,
                "verdict": "PENDING",
                "verdict_reasons": [],
                "clause_citations": [],
                "is_fraudulent": True,
                "injected_fraud_pattern": fraud_type
            }
            line_items.append(inflated_item)
            fraud_lines.append(line_no)
            line_no += 1

    total_billed = sum(item["total_amount"] for item in line_items)

    discharge_text = generate_discharge_summary(
        patient_name=patient_name,
        uhid=uhid,
        diag=diag,
        admit_dt=admit_time,
        disch_dt=discharge_time,
        los_days=total_days,
        icu_days=icu_days,
        procedures=procedures_billed
    )

    return {
        "claim_id": claim_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "hospital_id": hospital["id"],
        "hospital_name": hospital["name"],
        "policy_id": policy["policy_id"],
        "plan_name": policy["plan_name"],
        "admission_time": admit_time.isoformat(),
        "discharge_time": discharge_time.isoformat(),
        "primary_icd10": diag["code"],
        "primary_diagnosis": diag["name"],
        "category": diag["category"],
        "total_claimed_amount": round(total_billed, 2),
        "total_approved_amount": 0.0,
        "status": "INGESTED",
        "is_fraud": inject_fraud,
        "fraud_pattern": fraud_pattern_fired,
        "fraud_line_numbers": fraud_lines,
        "line_items_count": len(line_items),
        "line_items_json": json.dumps(line_items),
        "discharge_summary": discharge_text
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic ClaimFlow datasets.")
    parser.add_argument("--count", type=int, default=2000, help="Total claims to generate (default: 2000)")
    parser.add_argument("--fraud-rate", type=float, default=0.15, help="Proportion of claims with fraud (default: 0.15)")
    args = parser.parse_args()

    total_claims = args.count
    fraud_rate = args.fraud_rate
    num_fraud = int(total_claims * fraud_rate)
    num_clean = total_claims - num_fraud

    print(f"Generating {total_claims} synthetic claims ({num_clean} clean, {num_fraud} fraud)...")

    # Determine fraud distribution evenly among 8 patterns
    fraud_pattern_allocations = []
    for i in range(num_fraud):
        fraud_pattern_allocations.append(FRAUD_PATTERNS[i % len(FRAUD_PATTERNS)])
    random.shuffle(fraud_pattern_allocations)

    claims = []
    for idx in range(1, total_claims + 1):
        if idx <= num_fraud:
            f_type = fraud_pattern_allocations[idx - 1]
            c = create_synthetic_claim(idx, inject_fraud=True, fraud_type=f_type)
        else:
            c = create_synthetic_claim(idx, inject_fraud=False)
        claims.append(c)

    # Shuffle claims so fraud is distributed naturally throughout the dataset
    random.shuffle(claims)

    df = pd.DataFrame(claims)
    parquet_path = os.path.join(OUTPUT_SYNTHETIC_DIR, "claims.parquet")
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    print(f"Saved claims dataset to: {parquet_path} ({os.path.getsize(parquet_path):,} bytes)")

    # Save 5 sample FHIR bundles for ingestion testing
    sample_fhir = {
        "resourceType": "Bundle",
        "id": "FHIR-BUNDLE-SAMPLE-001",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": claims[0]["patient_id"],
                    "name": claims[0]["patient_name"],
                    "gender": "male"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": f"COND-{claims[0]['claim_id']}",
                    "code": {
                        "coding": [{
                            "system": "http://hl7.org/fhir/sid/icd-10",
                            "code": claims[0]["primary_icd10"],
                            "display": claims[0]["primary_diagnosis"]
                        }]
                    },
                    "subject": f"Patient/{claims[0]['patient_id']}"
                }
            }
        ]
    }
    with open(os.path.join(FHIR_OUTPUT_DIR, "sample_bundle.json"), "w") as f:
        json.dump(sample_fhir, f, indent=2)

    # Print summary statistics
    print("\n================ DATASET GENERATION SUMMARY ================")
    print(f"Total Claims Generated: {len(df)}")
    print(f"Clean Claims:           {(df['is_fraud'] == False).sum()} ({(df['is_fraud'] == False).mean():.1%})")
    print(f"Fraudulent Claims:      {(df['is_fraud'] == True).sum()} ({(df['is_fraud'] == True).mean():.1%})")
    print("\nFraud Breakdown by Pattern:")
    for pat, count in df[df['is_fraud'] == True]['fraud_pattern'].value_counts().items():
        print(f"  - {pat:<45}: {count} cases")
    print("============================================================\n")


if __name__ == "__main__":
    main()
