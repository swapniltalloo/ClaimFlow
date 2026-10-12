import pytest
from datetime import datetime, timezone
from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict, DecisionOutcome
from app.orchestrator.pipeline import ClaimFlowOrchestrator


SAMPLE_EHR = """================================================================================
                    DISCHARGE SUMMARY & CLINICAL RECORD
HOSPITAL: Apollo Super Specialty Hospital
PATIENT: Aarav Sharma   | UHID: UHID-12345678   | AGE: 38   | GENDER: Male
ADMISSION DATE: 01-Oct-2026 09:00
DISCHARGE DATE: 03-Oct-2026 12:00
LENGTH OF STAY: 2 Days (Room Days: 2, ICU Days: 0)
================================================================================

CHIEF COMPLAINTS & PRESENTATION:
Patient presented with acute right lower quadrant abdominal pain consistent with Unspecified acute appendicitis (K35.80).

PROCEDURES PERFORMED:
CPT-44970 (Laparoscopic appendectomy uncomplicated)

DISCHARGE MEDICATIONS:
1. Oral broad spectrum antibiotics
2. Paracetamol 650mg
================================================================================
"""


@pytest.mark.asyncio
async def test_orchestrator_clean_claim_pipeline():
    orchestrator = ClaimFlowOrchestrator()

    room_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.ROOM_ICU,
        code="ROOM-STD-PVT",
        description="Standard Room",
        quantity=2.0,
        unit_price=3000.0,
        total_amount=6000.0
    )
    proc_item = LineItem(
        line_number=2,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Laparoscopic appendectomy",
        quantity=1.0,
        unit_price=55000.0,
        total_amount=55000.0
    )
    claim = Claim(
        claim_id="CLM-ORCH-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-HDFC-OPTIMA-002",  # HDFC Optima has 0% copay, no room cap
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=61000.0,
        line_items=[room_item, proc_item]
    )

    result = await orchestrator.process_claim(claim, discharge_text=SAMPLE_EHR, policy_tenure_days=180)

    assert result.decision.outcome == DecisionOutcome.AUTO_SETTLE
    assert result.decision.approved_amount == 61000.0
    assert result.transaction is not None
    assert result.sla_breached is False
    assert "parsing" in result.stage_latencies_ms
    assert "coding_and_policy" in result.stage_latencies_ms
    assert "fraud_scoring" in result.stage_latencies_ms
    assert "settlement" in result.stage_latencies_ms


@pytest.mark.asyncio
async def test_orchestrator_fallback_on_failure():
    orchestrator = ClaimFlowOrchestrator()
    claim = Claim(
        claim_id="CLM-ERR-001",
        patient_id="PAT-002",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=25000.0,
        line_items=[]
    )

    # Force a failure by corrupting input text
    result = await orchestrator.process_claim(claim, discharge_text=None)

    # Architectural rule: Must NEVER silently approve. Always fallback to HUMAN_REVIEW!
    assert result.decision.outcome == DecisionOutcome.HUMAN_REVIEW
    assert result.decision.approved_amount == 0.0
    assert result.transaction is None
