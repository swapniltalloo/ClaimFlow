import pytest
from datetime import datetime, timezone
from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict
from app.agents.policy_agent import PolicyAgent


@pytest.fixture
def policy_agent():
    return PolicyAgent()


def test_policy_agent_room_rent_cap_and_copay(policy_agent):
    # New India Assurance Yuva Bharat (PSU GIPSA): Room rent capped at 3,000/day, Copay 20%
    room_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.ROOM_ICU,
        code="ROOM-STD-PVT",
        description="Standard Room Accommodation",
        quantity=2.0,
        unit_price=4500.0,  # 4,500 > 3,000 cap
        total_amount=9000.0,
        verdict=LineItemVerdict.OK
    )
    claim = Claim(
        claim_id="CLM-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-NIA-YUVA-009",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=9000.0,
        line_items=[room_item]
    )

    items, approved, deducted, citations = policy_agent.evaluate_policy_coverage(claim, tenure_days=180)

    # Room allowable: 2 * 3,000 = 6,000. Less 20% copay = 4,800.
    assert approved == 4800.0
    assert deducted == 4200.0
    assert len(citations) >= 2
    # Check clause citations
    assert any("SEC-3.1" in c for c in citations)
    assert any("SEC-4.2" in c for c in citations)


def test_policy_agent_waiting_period_deduction(policy_agent):
    # New India Assurance Yuva Bharat: 30-day waiting period. Claim at Day 12 must be deducted 100%
    proc_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Appendectomy",
        quantity=1.0,
        unit_price=55000.0,
        total_amount=55000.0,
        verdict=LineItemVerdict.OK
    )
    claim = Claim(
        claim_id="CLM-002",
        patient_id="PAT-002",
        hospital_id="HOSP-001",
        policy_id="POL-NIA-YUVA-009",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=55000.0,
        line_items=[proc_item]
    )

    items, approved, deducted, citations = policy_agent.evaluate_policy_coverage(claim, tenure_days=12)

    assert approved == 0.0
    assert deducted == 55000.0
    assert any("SEC-5.1" in c for c in citations)


def test_policy_agent_hdfc_optima_zero_deductions(policy_agent):
    # HDFC ERGO Optima Secure: No room cap, 0% copay
    room_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.ROOM_ICU,
        code="ROOM-STD-PVT",
        description="Single AC Private Room",
        quantity=3.0,
        unit_price=6000.0,
        total_amount=18000.0,
        verdict=LineItemVerdict.OK
    )
    claim = Claim(
        claim_id="CLM-003",
        patient_id="PAT-003",
        hospital_id="HOSP-001",
        policy_id="POL-HDFC-OPTIMA-002",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=18000.0,
        line_items=[room_item]
    )

    items, approved, deducted, citations = policy_agent.evaluate_policy_coverage(claim, tenure_days=200)

    assert approved == 18000.0
    assert deducted == 0.0
