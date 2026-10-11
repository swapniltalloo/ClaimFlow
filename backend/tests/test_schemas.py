import pytest
from datetime import datetime, date
from app.models.fhir import (
    FHIRPatient, FHIREncounter, FHIRCondition, FHIRCoding, FHIRCodeableConcept, FHIRPeriod, FHIRBundle
)
from app.models.domain import (
    Claim, LineItem, LineItemType, LineItemVerdict, PolicyCoverage, Decision, DecisionOutcome, AuditEvent
)
from app.core.security import compute_input_hash, mask_phi
from app.core.config import settings


def test_fhir_patient_schema():
    patient = FHIRPatient(
        id="PAT-001",
        name="Aarav Sharma",
        gender="male",
        birthDate=date(1985, 6, 15)
    )
    data = patient.model_dump()
    assert data["resourceType"] == "Patient"
    assert data["name"] == "Aarav Sharma"
    assert data["gender"] == "male"


def test_fhir_encounter_schema():
    period = FHIRPeriod(
        start=datetime(2026, 10, 1, 10, 0),
        end=datetime(2026, 10, 3, 14, 0)
    )
    encounter = FHIREncounter(
        id="ENC-001",
        status="finished",
        period=period,
        serviceProvider="HOSP-001"
    )
    assert encounter.status == "finished"
    assert encounter.period.start.year == 2026


def test_claim_and_line_item_schema():
    line = LineItem(
        line_number=1,
        service_date=datetime(2026, 10, 1, 12, 0),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Laparoscopic appendectomy",
        quantity=1.0,
        unit_price=55000.0,
        total_amount=55000.0,
        verdict=LineItemVerdict.PENDING
    )
    claim = Claim(
        claim_id="CLM-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-SILVER-001",
        admission_time=datetime(2026, 10, 1, 10, 0),
        discharge_time=datetime(2026, 10, 3, 14, 0),
        total_claimed_amount=55000.0,
        line_items=[line]
    )
    assert claim.claim_id == "CLM-001"
    assert len(claim.line_items) == 1
    assert claim.line_items[0].total_amount == 55000.0


def test_security_input_hash_and_phi_masking():
    payload = {"claim_id": "CLM-001", "amount": 50000}
    h1 = compute_input_hash(payload)
    h2 = compute_input_hash(payload)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 length

    masked = mask_phi("Patient UHID-12345678 admitted under POL-88889999")
    assert "UHID-****5678" in masked
    assert "POL-****9999" in masked


def test_sla_configuration_budget():
    assert settings.SLA_MAX_SECONDS == 900
    assert settings.INGEST_BUDGET_SECONDS + settings.PARSER_BUDGET_SECONDS + settings.VALIDATION_BUDGET_SECONDS + settings.FRAUD_BUDGET_SECONDS + settings.DECISION_BUDGET_SECONDS <= settings.SLA_MAX_SECONDS
