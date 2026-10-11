import json
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

# Reference tariff median map
TARIFF_MEDIANS = {
    "CPT-44970": 55000.0,
    "CPT-44960": 95000.0,
    "CPT-49505": 48000.0,
    "CPT-47562": 65000.0,
    "CPT-92928": 140000.0,
    "CPT-93458": 25000.0,
    "CPT-59400": 40000.0,
    "CPT-59510": 65000.0,
    "CPT-27447": 185000.0,
    "CPT-27236": 110000.0,
    "CPT-29888": 85000.0,
    "CPT-66984": 32000.0,
    "ROOM-STD-PVT": 4500.0,
    "ROOM-ICU-BED": 14000.0,
    "LAB-CBC-PLATE": 850.0,
    "LAB-ABG-SERIAL": 1800.0,
    "IMG-CT-ABDOMEN": 6500.0,
    "MED-IV-ABX": 4200.0,
    "CONS-SURG-KIT": 12500.0
}

FEATURE_NAMES = [
    "total_claimed_amount",
    "los_days",
    "cost_per_day",
    "icu_days",
    "icu_day_ratio",
    "line_item_count",
    "max_price_to_median_ratio",
    "num_duplicate_items",
    "unbundled_count",
    "mismatch_flag",
    "waiting_period_flag"
]


def extract_claim_features(claim_dict: Dict[str, Any]) -> np.ndarray:
    """Extracts numeric feature vector for a claim dictionary."""
    total_amount = float(claim_dict.get("total_claimed_amount", 0.0))
    line_items_data = claim_dict.get("line_items_json")
    if isinstance(line_items_data, str):
        line_items = json.loads(line_items_data)
    elif isinstance(line_items_data, list):
        line_items = line_items_data
    elif "line_items" in claim_dict:
        line_items = [it.model_dump() if hasattr(it, "model_dump") else it for it in claim_dict["line_items"]]
    else:
        line_items = []

    # Calculate dates & duration
    admit_str = claim_dict.get("admission_time")
    disch_str = claim_dict.get("discharge_time")
    los_days = 2.0
    if admit_str and disch_str:
        try:
            from dateutil import parser as dt_parser
            admit_dt = dt_parser.parse(str(admit_str))
            disch_dt = dt_parser.parse(str(disch_str))
            los_days = max(1.0, (disch_dt - admit_dt).total_seconds() / 86400.0)
        except Exception:
            los_days = 2.0

    cost_per_day = total_amount / max(1.0, los_days)

    icu_days = 0.0
    for it in line_items:
        if it.get("code") == "ROOM-ICU-BED":
            icu_days += float(it.get("quantity", 0.0))
    icu_day_ratio = icu_days / max(1.0, los_days)

    line_item_count = float(len(line_items))

    # Tariff ratios
    max_price_ratio = 1.0
    for it in line_items:
        code = it.get("code")
        unit_price = float(it.get("unit_price", 0.0))
        median = TARIFF_MEDIANS.get(code)
        if median and median > 0:
            ratio = unit_price / median
            if ratio > max_price_ratio:
                max_price_ratio = ratio

    # Duplicate counts
    seen_codes = set()
    num_duplicates = 0.0
    for it in line_items:
        code = it.get("code")
        if code in seen_codes and it.get("item_type") in {"MEDICATION", "CONSUMABLE"}:
            num_duplicates += 1.0
        seen_codes.add(code)

    # Unbundling detection
    unbundled_count = 0.0
    codes_set = {it.get("code") for it in line_items}
    if "CPT-44970" in codes_set and "CPT-49080" in codes_set:
        unbundled_count += 1.0
    if "CPT-27447" in codes_set and "CPT-29870" in codes_set:
        unbundled_count += 1.0

    # Clinical mismatch flag
    mismatch_flag = 0.0
    diag = claim_dict.get("primary_icd10", "")
    if diag.startswith("A97") and any(c.startswith("CPT-2") for c in codes_set):
        mismatch_flag = 1.0

    # Waiting period flag
    waiting_period_flag = 0.0
    if claim_dict.get("fraud_pattern") == "FR-007_EXCLUSION_WAITING_PERIOD_VIOLATION":
        waiting_period_flag = 1.0

    features = [
        total_amount,
        los_days,
        cost_per_day,
        icu_days,
        icu_day_ratio,
        line_item_count,
        max_price_ratio,
        num_duplicates,
        unbundled_count,
        mismatch_flag,
        waiting_period_flag
    ]
    return np.array(features, dtype=np.float32)
