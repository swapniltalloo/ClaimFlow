import pytest
from datetime import datetime, timezone
from app.agents.ehr_parser import EHRParserAgent
from app.models.domain import ClinicalFacts


SAMPLE_DISCHARGE_TEXT = """================================================================================
                    DISCHARGE SUMMARY & CLINICAL RECORD
HOSPITAL: Apollo Super Specialty Hospital
PATIENT: Aarav Sharma   | UHID: UHID-98765432   | AGE: 42   | GENDER: Male
ADMISSION DATE: 10-Oct-2026 10:30
DISCHARGE DATE: 13-Oct-2026 15:45
LENGTH OF STAY: 3 Days (Room Days: 2, ICU Days: 1)
================================================================================

CHIEF COMPLAINTS & PRESENTATION:
Patient presented with acute right lower quadrant pain and fever consistent with Unspecified acute appendicitis (K35.80).

CLINICAL COURSE & MANAGEMENT:
Patient was admitted under General Surgery. Patient required critical care monitoring in ICU for 1 days.

PROCEDURES PERFORMED:
CPT-44970 (Laparoscopic appendectomy uncomplicated)

HOSPITAL COURSE & RECOVERY:
Post-procedural recovery uneventful. Surgical wound clean. Afebrile.

DISCHARGE MEDICATIONS:
1. Oral broad spectrum antibiotics x 5 days
2. Paracetamol 650mg SOS

CONDITION AT DISCHARGE: Hemodynamically stable, ambulating, fit for discharge.
ATTENDING PHYSICIAN: Dr. Vikram Desai, MD/MS
================================================================================
"""


def test_ehr_parser_clinical_facts_extraction():
    agent = EHRParserAgent()
    facts = agent.parse(SAMPLE_DISCHARGE_TEXT, patient_id="PAT-98765")

    assert isinstance(facts, ClinicalFacts)
    assert facts.patient_id == "PAT-98765"
    assert facts.primary_diagnosis_code == "K35.80"
    assert facts.icu_stay_days == 1
    assert facts.room_stay_days == 2
    assert "CPT-44970" in facts.performed_procedure_codes
    assert len(facts.prescribed_medications) == 2
    assert facts.confidence_score >= 0.90
    assert "admit_time" in facts.evidence_snippets
    assert "discharge_time" in facts.evidence_snippets
    assert "length_of_stay" in facts.evidence_snippets
    assert len(facts.flagged_uncertainties) == 0


def test_ehr_parser_low_confidence_flagging():
    agent = EHRParserAgent()
    vague_text = "Patient arrived feeling unwell. Had a headache and some nausea. Treated with fluids and sent home next day."
    facts = agent.parse(vague_text)

    assert isinstance(facts, ClinicalFacts)
    # When admission/discharge dates and explicit diagnostic codes are missing, uncertainties must be flagged!
    assert len(facts.flagged_uncertainties) > 0
    assert facts.confidence_score < 0.80


def test_ehr_parser_fhir_bundle_support():
    agent = EHRParserAgent()
    fhir_bundle = {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {
                        "coding": [{
                            "system": "http://hl7.org/fhir/sid/icd-10",
                            "code": "A97.2",
                            "display": "Severe dengue with plasma leakage"
                        }]
                    }
                }
            }
        ]
    }
    facts = agent.parse("Patient admitted with severe viral fever and petechiae.", fhir_bundle=fhir_bundle)
    assert facts.primary_diagnosis_code == "A97.2"
    assert facts.field_confidences["primary_diagnosis_code"] == 1.0
