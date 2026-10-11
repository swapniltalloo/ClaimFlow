import pytest
from datetime import datetime, timezone
from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict, DecisionOutcome
from app.agents.settlement_agent import SettlementAgent
from app.services.payment import MockPaymentGateway
from app.services.audit import AuditService


@pytest.fixture
def settlement_setup():
    gateway = MockPaymentGateway()
    audit = AuditService()
    agent = SettlementAgent(payment_gateway=gateway, audit_service=audit)
    return agent, gateway, audit


def test_settlement_auto_settle(settlement_setup):
    agent, gateway, audit = settlement_setup
    line = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Appendectomy",
        unit_price=55000.0,
        total_amount=55000.0,
        approved_amount=55000.0,
        verdict=LineItemVerdict.OK
    )
    claim = Claim(
        claim_id="CLM-SETTLE-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=55000.0,
        line_items=[line]
    )

    decision, txn, notifs = agent.settle_claim(claim, risk_score=15.0)

    assert decision.outcome == DecisionOutcome.AUTO_SETTLE
    assert decision.approved_amount == 55000.0
    assert txn is not None
    assert txn.amount == 55000.0
    assert len(audit.get_events_for_claim("CLM-SETTLE-001")) == 1


def test_settlement_idempotency_prevents_double_pay(settlement_setup):
    agent, gateway, audit = settlement_setup
    line = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Appendectomy",
        unit_price=50000.0,
        total_amount=50000.0,
        approved_amount=50000.0,
        verdict=LineItemVerdict.OK
    )
    claim = Claim(
        claim_id="CLM-IDEMP-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=50000.0,
        line_items=[line]
    )

    # First settlement execution
    dec1, txn1, _ = agent.settle_claim(claim, risk_score=10.0)
    assert txn1 is not None

    # Replay of the identical claim
    dec2, txn2, _ = agent.settle_claim(claim, risk_score=10.0)
    assert txn2 is not None

    # CRITICAL IDEMPOTENCY GUARANTEE: Same transaction ID returned, zero duplicate disbursal
    assert txn1.transaction_id == txn2.transaction_id
    assert len(gateway._processed_transactions) == 1


def test_settlement_human_review_blocks_payment(settlement_setup):
    agent, gateway, audit = settlement_setup
    claim = Claim(
        claim_id="CLM-REVIEW-001",
        patient_id="PAT-002",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=80000.0,
        line_items=[]
    )

    decision, txn, notifs = agent.settle_claim(claim, risk_score=72.0)

    assert decision.outcome == DecisionOutcome.HUMAN_REVIEW
    assert decision.approved_amount == 0.0
    assert txn is None  # Payment MUST NOT be issued


def test_settlement_siu_escalation(settlement_setup):
    agent, gateway, audit = settlement_setup
    claim = Claim(
        claim_id="CLM-SIU-001",
        patient_id="PAT-003",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=150000.0,
        line_items=[]
    )

    decision, txn, notifs = agent.settle_claim(claim, risk_score=92.0)

    assert decision.outcome == DecisionOutcome.SIU_ESCALATE
    assert decision.approved_amount == 0.0
    assert txn is None
