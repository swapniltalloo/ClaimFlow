import json
import os
from typing import List, Tuple, Optional, Dict, Any
from app.models.domain import LineItem, LineItemType, ClinicalFacts
from app.rules.base import BaseCodingRule

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REF_DATA_DIR = os.path.join(BASE_DIR, "data", "reference")


def _load_reference_data():
    with open(os.path.join(REF_DATA_DIR, "procedure_tariffs.json"), "r") as f:
        tariffs = json.load(f)
    with open(os.path.join(REF_DATA_DIR, "icd10_codes.json"), "r") as f:
        icd10 = json.load(f)
    with open(os.path.join(REF_DATA_DIR, "bundling_matrix.json"), "r") as f:
        bundling = json.load(f)
    return tariffs, icd10, bundling


TARIFFS, ICD10_CODES, BUNDLING_MATRIX = _load_reference_data()
VALID_CODES = {t["code"] for t in TARIFFS}
DIAG_MAP = {d["code"]: d for d in ICD10_CODES}


class CodeValidityRule(BaseCodingRule):
    """CR-001: Verifies billed code exists in the recognized national / clearinghouse tariff schedule."""

    rule_id = "CR-001"
    rule_name = "Code Validity"
    category = "VALIDITY"

    def evaluate(self, item: LineItem, all_items: List[LineItem], clinical_facts: ClinicalFacts) -> Tuple[bool, Optional[str]]:
        # Check against reference tariff codes or standard patterns
        if item.code not in VALID_CODES and not item.code.startswith("CPT-") and not item.code.startswith("MED-"):
            return False, f"Rule CR-001: Billed service code '{item.code}' is not recognized in approved tariff schedule."
        return True, None


class DiagnosisProcedureMatrixRule(BaseCodingRule):
    """CR-002: Verifies billed procedure is clinically compatible with primary/secondary diagnosis."""

    rule_id = "CR-002"
    rule_name = "Diagnosis-Procedure Clinical Compatibility"
    category = "CLINICAL_COHERENCE"

    def evaluate(self, item: LineItem, all_items: List[LineItem], clinical_facts: ClinicalFacts) -> Tuple[bool, Optional[str]]:
        if item.item_type != LineItemType.PROCEDURE:
            return True, None

        primary_code = clinical_facts.primary_diagnosis_code
        diag_info = DIAG_MAP.get(primary_code)
        if not diag_info:
            return True, None

        standard_procs = diag_info.get("standard_procedures", [])
        category = diag_info.get("category", "")

        # If diagnosis is strictly medical (e.g. Dengue, URI, Diabetes) but billed procedure is invasive orthopedic/cardiac surgery
        if "MED-" in standard_procs[0] if standard_procs else False:
            if item.code.startswith("CPT-2") or item.code.startswith("CPT-9"):  # Ortho or Cardiac CPT codes
                return False, f"Rule CR-002: Incompatible procedure '{item.code}' billed for purely medical condition '{diag_info['name']}' ({primary_code})."

        # Check specialty alignment
        if category == "Internal Medicine" and item.code in {"CPT-29888", "CPT-27447", "CPT-44970"}:
            return False, f"Rule CR-002: Surgical procedure '{item.code}' does not match medical admission diagnosis '{primary_code}'."

        return True, None


class BundlingMatrixRule(BaseCodingRule):
    """CR-003: Flags unbundled component procedures when an all-inclusive primary package code is billed."""

    rule_id = "CR-003"
    rule_name = "Unbundling Detection"
    category = "BUNDLING"

    def evaluate(self, item: LineItem, all_items: List[LineItem], clinical_facts: ClinicalFacts) -> Tuple[bool, Optional[str]]:
        billed_codes = {it.code for it in all_items}

        for package in BUNDLING_MATRIX:
            primary_code = package["primary_package_code"]
            if primary_code in billed_codes:
                for bundled in package["bundled_component_codes"]:
                    if item.code == bundled["code"]:
                        return False, f"Rule CR-003: Unbundling detected. Component code '{item.code}' is integral to primary package '{primary_code}' ({bundled['reason']})."
        return True, None


class QuantityAndDurationRule(BaseCodingRule):
    """CR-004: Verifies billed room/ICU days do not exceed clinically corroborated length of stay."""

    rule_id = "CR-004"
    rule_name = "Quantity & Duration Limits"
    category = "QUANTITY"

    def evaluate(self, item: LineItem, all_items: List[LineItem], clinical_facts: ClinicalFacts) -> Tuple[bool, Optional[str]]:
        if item.item_type == LineItemType.ROOM_ICU:
            if item.code == "ROOM-STD-PVT" and clinical_facts.room_stay_days > 0:
                if item.quantity > clinical_facts.room_stay_days + 1:
                    return False, f"Rule CR-004: Billed room days ({item.quantity}) exceed clinically recorded room stay ({clinical_facts.room_stay_days} days)."
            elif item.code == "ROOM-ICU-BED":
                if item.quantity > clinical_facts.icu_stay_days and clinical_facts.icu_stay_days == 0:
                    return False, f"Rule CR-004: ICU stay billed ({item.quantity} days) but EHR documents zero ICU admission days."
        return True, None


class PhantomServiceRule(BaseCodingRule):
    """CR-005: Flags billed procedures or high-value diagnostics with zero clinical corroboration in EHR."""

    rule_id = "CR-005"
    rule_name = "Phantom Service Verification"
    category = "EVIDENCE"

    def evaluate(self, item: LineItem, all_items: List[LineItem], clinical_facts: ClinicalFacts) -> Tuple[bool, Optional[str]]:
        # Invasive surgical procedure billed but not mentioned in performed procedures
        if item.item_type == LineItemType.PROCEDURE:
            if clinical_facts.performed_procedure_codes and item.code not in clinical_facts.performed_procedure_codes:
                # Check if it is a known bundled component of a performed procedure (which is unbundling, not phantom)
                is_bundled = False
                for pkg in BUNDLING_MATRIX:
                    if pkg["primary_package_code"] in clinical_facts.performed_procedure_codes:
                        if any(b["code"] == item.code for b in pkg["bundled_component_codes"]):
                            is_bundled = True
                            break

                if not is_bundled:
                    return False, f"Rule CR-005: Billed surgical procedure '{item.code}' has zero evidence in EHR operative notes."

        # Serial ABG or specialized CT billed for simple uncomplicated conditions
        if item.code in {"LAB-ABG-SERIAL", "IMG-CT-ABDOMEN"} and clinical_facts.icu_stay_days == 0:
            if clinical_facts.primary_diagnosis_code in {"A97.0", "K40.90", "H26.9"}:
                return False, f"Rule CR-005: High-intensity investigation '{item.code}' lacks clinical indication for uncomplicated admission '{clinical_facts.primary_diagnosis_code}'."

        return True, None


class DuplicateBillingRule(BaseCodingRule):
    """CR-006: Flags identical line items submitted with exact duplicate codes and quantities."""

    rule_id = "CR-006"
    rule_name = "Duplicate Billing Detection"
    category = "DUPLICATION"

    def evaluate(self, item: LineItem, all_items: List[LineItem], clinical_facts: ClinicalFacts) -> Tuple[bool, Optional[str]]:
        # Count identical occurrences
        duplicates = [
            it for it in all_items
            if it.code == item.code and it.item_type in {LineItemType.PROCEDURE, LineItemType.CONSUMABLE, LineItemType.MEDICATION}
        ]
        if len(duplicates) > 1 and item.line_number > duplicates[0].line_number:
            return False, f"Rule CR-006: Duplicate billing detected for service code '{item.code}' (first billed on Line #{duplicates[0].line_number})."
        return True, None
