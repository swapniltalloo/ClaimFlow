import pytest
from datetime import datetime, timezone
from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict
from app.agents.fraud_agent import FraudAgent


@pytest.fixture
def fraud_agent():
    return FraudAgent(auto_train=False)


def test_fraud_agent_clean_claim_scoring(fraud_agent):
    clean_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Laparoscopic appendectomy",
        unit_price=55000.0,
        total_amount=55000.0,
        verdict=LineItemVerdict.OK
    )
    claim = Claim(
        claim_id="CLM-CLEAN-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=55000.0,
        line_items=[clean_item]
    )

    risk_score, reasons = fraud_agent.evaluate_claim(claim)
    assert risk_score < 35.0  # Clean claim must have low risk


def test_fraud_agent_inflated_price_detection(fraud_agent):
    # 3.5x inflated consumable kit
    inflated_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.CONSUMABLE,
        code="CONS-SURG-KIT",
        description="Surgical Trocar Kit",
        unit_price=43750.0,  # standard is 12,500
        total_amount=43750.0,
        verdict=LineItemVerdict.PENDING
    )
    claim = Claim(
        claim_id="CLM-FRAUD-001",
        patient_id="PAT-002",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=43750.0,
        line_items=[inflated_item]
    )

    risk_score, reasons = fraud_agent.evaluate_claim(claim)
    assert risk_score >= 50.0
    assert any("FR-008" in r for r in reasons)


def test_fraud_agent_unbundling_detection(fraud_agent):
    proc_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Appendectomy",
        unit_price=55000.0,
        total_amount=55000.0
    )
    unbundled_item = LineItem(
        line_number=2,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-49080",
        description="Peritoneal lavage",
        unit_price=14500.0,
        total_amount=14500.0
    )
    claim = Claim(
        claim_id="CLM-FRAUD-002",
        patient_id="PAT-003",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=69500.0,
        line_items=[proc_item, unbundled_item]
    )

    risk_score, reasons = fraud_agent.evaluate_claim(claim)
    assert risk_score >= 50.0
    assert any("FR-002" in r for r in reasons)
