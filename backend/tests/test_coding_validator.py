import pytest
from datetime import datetime, timezone
from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict, ClinicalFacts
from app.agents.coding_validator import CodingValidatorAgent
from app.rules.coding_rules import (
    CodeValidityRule,
    DiagnosisProcedureMatrixRule,
    BundlingMatrixRule,
    QuantityAndDurationRule,
    PhantomServiceRule,
    DuplicateBillingRule
)


@pytest.fixture
def base_clinical_facts():
    return ClinicalFacts(
        patient_id="PAT-001",
        primary_diagnosis_code="K35.80",
        primary_diagnosis_name="Unspecified acute appendicitis",
        admit_time=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
        discharge_time=datetime(2026, 10, 3, 10, 0, tzinfo=timezone.utc),
        icu_stay_days=0,
        room_stay_days=2,
        performed_procedure_codes=["CPT-44970"],
        prescribed_medications=["Oral antibiotics"]
    )


def test_cr001_code_validity_rule(base_clinical_facts):
    rule = CodeValidityRule()
    valid_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Laparoscopic appendectomy",
        unit_price=55000.0,
        total_amount=55000.0
    )
    passed, reason = rule.evaluate(valid_item, [valid_item], base_clinical_facts)
    assert passed is True
    assert reason is None

    invalid_item = LineItem(
        line_number=2,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="INVALID-9999",
        description="Fake code",
        unit_price=10000.0,
        total_amount=10000.0
    )
    passed, reason = rule.evaluate(invalid_item, [invalid_item], base_clinical_facts)
    assert passed is False
    assert "CR-001" in reason


def test_cr002_diagnosis_procedure_matrix_rule():
    rule = DiagnosisProcedureMatrixRule()
    dengue_facts = ClinicalFacts(
        patient_id="PAT-002",
        primary_diagnosis_code="A97.0",
        primary_diagnosis_name="Dengue fever without warning signs",
        admit_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        icu_stay_days=0,
        room_stay_days=3
    )
    mismatched_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-29888",  # Knee arthroscopy ACL repair
        description="ACL reconstruction",
        unit_price=85000.0,
        total_amount=85000.0
    )
    passed, reason = rule.evaluate(mismatched_item, [mismatched_item], dengue_facts)
    assert passed is False
    assert "CR-002" in reason


def test_cr003_bundling_matrix_rule(base_clinical_facts):
    rule = BundlingMatrixRule()
    primary_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Laparoscopic appendectomy",
        unit_price=55000.0,
        total_amount=55000.0
    )
    unbundled_item = LineItem(
        line_number=2,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-49080",  # Peritoneal lavage (bundled in 44970)
        description="Peritoneal lavage",
        unit_price=14500.0,
        total_amount=14500.0
    )
    items = [primary_item, unbundled_item]

    passed, reason = rule.evaluate(unbundled_item, items, base_clinical_facts)
    assert passed is False
    assert "CR-003" in reason


def test_cr004_quantity_and_duration_rule(base_clinical_facts):
    rule = QuantityAndDurationRule()
    inflated_room = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.ROOM_ICU,
        code="ROOM-STD-PVT",
        description="Standard Room",
        quantity=7.0,  # 7 days billed for 2 days stay
        unit_price=4500.0,
        total_amount=31500.0
    )
    passed, reason = rule.evaluate(inflated_room, [inflated_room], base_clinical_facts)
    assert passed is False
    assert "CR-004" in reason


def test_cr005_phantom_service_rule(base_clinical_facts):
    rule = PhantomServiceRule()
    phantom_proc = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-27447",  # Knee replacement (no evidence in appendicitis)
        description="Total Knee Arthroplasty",
        unit_price=185000.0,
        total_amount=185000.0
    )
    passed, reason = rule.evaluate(phantom_proc, [phantom_proc], base_clinical_facts)
    assert passed is False
    assert "CR-005" in reason


def test_cr006_duplicate_billing_rule(base_clinical_facts):
    rule = DuplicateBillingRule()
    item1 = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.MEDICATION,
        code="MED-IV-ABX",
        description="IV Antibiotics",
        unit_price=4200.0,
        total_amount=4200.0
    )
    item2 = LineItem(
        line_number=2,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.MEDICATION,
        code="MED-IV-ABX",
        description="IV Antibiotics",
        unit_price=4200.0,
        total_amount=4200.0
    )
    items = [item1, item2]

    passed1, reason1 = rule.evaluate(item1, items, base_clinical_facts)
    assert passed1 is True

    passed2, reason2 = rule.evaluate(item2, items, base_clinical_facts)
    assert passed2 is False
    assert "CR-006" in reason2


def test_coding_validator_agent_end_to_end(base_clinical_facts):
    agent = CodingValidatorAgent()
    good_item = LineItem(
        line_number=1,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-44970",
        description="Laparoscopic appendectomy",
        unit_price=55000.0,
        total_amount=55000.0
    )
    bad_item = LineItem(
        line_number=2,
        service_date=datetime.now(timezone.utc),
        item_type=LineItemType.PROCEDURE,
        code="CPT-49080",  # Unbundled
        description="Peritoneal lavage",
        unit_price=14500.0,
        total_amount=14500.0
    )
    claim = Claim(
        claim_id="CLM-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=69500.0,
        line_items=[good_item, bad_item]
    )

    validated_items, fired_rules = agent.validate_claim(claim, base_clinical_facts)

    assert len(validated_items) == 2
    assert validated_items[0].verdict == LineItemVerdict.OK
    assert validated_items[0].approved_amount == 55000.0

    assert validated_items[1].verdict == LineItemVerdict.MISMATCH
    assert validated_items[1].approved_amount == 0.0
    assert "CR-003" in fired_rules
