from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LineItemVerdict(str, Enum):
    PENDING = "PENDING"
    OK = "OK"
    MISMATCH = "MISMATCH"
    UNSUPPORTED = "UNSUPPORTED"


class LineItemType(str, Enum):
    PROCEDURE = "PROCEDURE"
    ROOM_ICU = "ROOM_ICU"
    MEDICATION = "MEDICATION"
    INVESTIGATION = "INVESTIGATION"
    CONSUMABLE = "CONSUMABLE"


class DecisionOutcome(str, Enum):
    AUTO_SETTLE = "AUTO_SETTLE"
    PARTIAL_SETTLE = "PARTIAL_SETTLE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    SIU_ESCALATE = "SIU_ESCALATE"


class ClaimStatus(str, Enum):
    INGESTED = "INGESTED"
    PARSED = "PARSED"
    VALIDATING = "VALIDATING"
    FRAUD_CHECKED = "FRAUD_CHECKED"
    AUTO_SETTLED = "AUTO_SETTLED"
    PARTIAL_SETTLED = "PARTIAL_SETTLED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    SIU_ESCALATED = "SIU_ESCALATED"


class LineItem(BaseModel):
    line_number: int
    service_date: datetime
    item_type: LineItemType
    code: str
    description: str
    quantity: float = 1.0
    unit_price: float
    total_amount: float
    verdict: LineItemVerdict = LineItemVerdict.PENDING
    verdict_reasons: List[str] = Field(default_factory=list)
    clause_citations: List[str] = Field(default_factory=list)
    approved_amount: Optional[float] = None
    is_fraudulent: bool = False
    injected_fraud_pattern: Optional[str] = None


class ClinicalFacts(BaseModel):
    patient_id: str
    primary_diagnosis_code: str
    primary_diagnosis_name: str
    secondary_diagnoses: List[str] = Field(default_factory=list)
    admit_time: datetime
    discharge_time: datetime
    icu_stay_days: int = 0
    room_stay_days: int = 0
    performed_procedure_codes: List[str] = Field(default_factory=list)
    prescribed_medications: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0
    evidence_snippets: Dict[str, str] = Field(default_factory=list)


class PolicyCoverage(BaseModel):
    policy_id: str
    plan_name: str
    sum_insured: float
    remaining_sum_insured: float
    room_rent_cap_daily: Optional[float] = None
    icu_rent_cap_daily: Optional[float] = None
    copay_percentage: float = 0.0
    waiting_period_months: int = 0
    policy_tenure_months: int = 12
    exclusions: List[str] = Field(default_factory=list)
    sub_limits: Dict[str, float] = Field(default_factory=dict)


class Claim(BaseModel):
    claim_id: str
    patient_id: str
    hospital_id: str
    policy_id: str
    admission_time: datetime
    discharge_time: datetime
    total_claimed_amount: float
    total_approved_amount: float = 0.0
    status: ClaimStatus = ClaimStatus.INGESTED
    risk_score: float = 0.0
    risk_reasons: List[str] = Field(default_factory=list)
    line_items: List[LineItem] = Field(default_factory=list)
    clinical_facts: Optional[ClinicalFacts] = None
    created_at: datetime = Field(default_factory=utc_now)
    settled_at: Optional[datetime] = None
    is_fraud: bool = False
    fraud_pattern: Optional[str] = None


class Decision(BaseModel):
    decision_id: str
    claim_id: str
    outcome: DecisionOutcome
    approved_amount: float
    deductions_amount: float
    clause_citations: List[str] = Field(default_factory=list)
    fired_rule_ids: List[str] = Field(default_factory=list)
    audit_hash: str
    decided_at: datetime = Field(default_factory=utc_now)
    reviewer_notes: Optional[str] = None


class AuditEvent(BaseModel):
    event_id: str
    claim_id: str
    stage: str
    input_hash: str
    rule_ids_fired: List[str] = Field(default_factory=list)
    model_version: str = "v1.0.0"
    duration_ms: float
    timestamp: datetime = Field(default_factory=utc_now)
    details: Dict[str, Any] = Field(default_factory=dict)
