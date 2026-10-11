import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from app.models.domain import Claim, Decision, DecisionOutcome, LineItemVerdict, LineItem
from app.services.payment import MockPaymentGateway, PaymentTransaction
from app.services.audit import AuditService
from app.core.config import settings
from app.core.security import compute_input_hash
from app.core.logging import logger


class SettlementAgent:
    """Agent E: Settlement Agent.
    
    Applies the clearinghouse decision policy, calls payment gateway with idempotency key,
    notifies hospital and patient, and writes immutable audit records.
    An LLM NEVER directly authorizes payment. Only the Settlement Agent can disburse funds.
    """

    def __init__(
        self,
        payment_gateway: Optional[MockPaymentGateway] = None,
        audit_service: Optional[AuditService] = None
    ):
        self.gateway = payment_gateway or MockPaymentGateway()
        self.audit = audit_service or AuditService()

    def settle_claim(
        self,
        claim: Claim,
        risk_score: float,
        parser_confidence: float = 1.0,
        fired_rule_ids: Optional[List[str]] = None,
        clause_citations: Optional[List[str]] = None,
        duration_ms: float = 250.0
    ) -> Tuple[Decision, Optional[PaymentTransaction], Dict[str, Any]]:
        """Applies clearinghouse decision policy, disburses funds idempotently if approved,
        and generates audit log records and notifications.
        
        Returns:
            Tuple of:
            - Decision object
            - Optional PaymentTransaction (None if routed to human review / SIU)
            - Notifications dictionary
        """
        rules_fired = fired_rule_ids or []
        citations = clause_citations or []

        # Calculate approved amount from line items
        approved_amount = sum(
            it.approved_amount if it.approved_amount is not None else 0.0
            for it in claim.line_items
        )
        deductions_amount = max(0.0, claim.total_claimed_amount - approved_amount)

        has_mismatches = any(
            it.verdict in {LineItemVerdict.MISMATCH, LineItemVerdict.UNSUPPORTED}
            for it in claim.line_items
        )

        # Apply Decision Policy (§8)
        if risk_score >= settings.SIU_ESCALATE_RISK_THRESHOLD:
            outcome = DecisionOutcome.SIU_ESCALATE
            notes = f"Critical risk score {risk_score:.1f} >= {settings.SIU_ESCALATE_RISK_THRESHOLD}. Escalate to Special Investigation Unit (SIU)."
            payment_amount = 0.0

        elif risk_score >= settings.HUMAN_REVIEW_RISK_THRESHOLD or parser_confidence < 0.70:
            outcome = DecisionOutcome.HUMAN_REVIEW
            notes = f"High risk score {risk_score:.1f} or low extraction confidence ({parser_confidence:.2f}). Evidence pack sent to medical adjudicator."
            payment_amount = 0.0

        elif has_mismatches:
            outcome = DecisionOutcome.PARTIAL_SETTLE
            notes = f"Clean line items approved (INR {approved_amount:,.2f}). Mismatched/unsupported lines held for clarification."
            payment_amount = approved_amount

        else:
            outcome = DecisionOutcome.AUTO_SETTLE
            notes = f"Auto-settled in real time. Risk score {risk_score:.1f} < {settings.AUTO_SETTLE_RISK_THRESHOLD}. All checks passed."
            payment_amount = approved_amount

        # Execute idempotent payment if funds approved
        transaction: Optional[PaymentTransaction] = None
        was_replay = False
        if outcome in {DecisionOutcome.AUTO_SETTLE, DecisionOutcome.PARTIAL_SETTLE} and payment_amount > 0:
            idempotency_key = f"IDEMP-CLM-{claim.claim_id}"
            transaction, was_replay = self.gateway.disburse_payment(
                idempotency_key=idempotency_key,
                claim_id=claim.claim_id,
                hospital_id=claim.hospital_id,
                amount=payment_amount
            )

        # Cryptographic audit hash of decision inputs
        audit_payload = {
            "claim_id": claim.claim_id,
            "total_claimed": claim.total_claimed_amount,
            "approved_amount": payment_amount,
            "risk_score": risk_score,
            "rules_fired": rules_fired,
            "outcome": outcome.value
        }
        audit_hash = compute_input_hash(audit_payload)

        decision = Decision(
            decision_id=f"DEC-{uuid.uuid4().hex[:12].upper()}",
            claim_id=claim.claim_id,
            outcome=outcome,
            approved_amount=round(payment_amount, 2),
            deductions_amount=round(deductions_amount, 2),
            clause_citations=citations,
            fired_rule_ids=rules_fired,
            audit_hash=audit_hash,
            decided_at=datetime.now(timezone.utc),
            reviewer_notes=notes
        )

        # Record immutable audit event
        self.audit.record_event(
            claim_id=claim.claim_id,
            stage="SETTLEMENT",
            input_payload=audit_payload,
            rule_ids_fired=rules_fired,
            duration_ms=duration_ms,
            details={
                "outcome": outcome.value,
                "approved_amount": payment_amount,
                "was_replay": was_replay,
                "transaction_id": transaction.transaction_id if transaction else None
            }
        )

        # Generate notifications
        notifications = {
            "hospital_notice": {
                "hospital_id": claim.hospital_id,
                "claim_id": claim.claim_id,
                "outcome": outcome.value,
                "amount_settled": payment_amount,
                "message": f"Claim {claim.claim_id} {outcome.value}. Disbursed INR {payment_amount:,.2f}."
            },
            "patient_notice": {
                "patient_id": claim.patient_id,
                "claim_id": claim.claim_id,
                "status": "APPROVED" if outcome in {DecisionOutcome.AUTO_SETTLE, DecisionOutcome.PARTIAL_SETTLE} else "PENDING_REVIEW",
                "message": f"Your hospital discharge claim of INR {claim.total_claimed_amount:,.2f} has been processed: {outcome.value}."
            }
        }

        return decision, transaction, notifications
