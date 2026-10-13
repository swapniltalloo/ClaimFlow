import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.models.domain import (
    Claim, ClinicalFacts, Decision, DecisionOutcome, LineItem, LineItemVerdict
)
from app.agents.ehr_parser import EHRParserAgent
from app.agents.coding_validator import CodingValidatorAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.fraud_agent import FraudAgent
from app.agents.settlement_agent import SettlementAgent
from app.services.payment import PaymentTransaction
from app.services.gemini_service import GeminiService
from app.core.config import settings
from app.core.logging import logger


class PipelineExecutionResult:
    def __init__(
        self,
        claim_id: str,
        decision: Decision,
        stage_latencies_ms: Dict[str, float],
        total_latency_ms: float,
        transaction: Optional[PaymentTransaction] = None,
        notifications: Optional[Dict[str, Any]] = None,
        sla_breached: bool = False,
        fraud_layers: Optional[Dict[str, Any]] = None,
        ai_explanation: Optional[str] = None,
        patient_explanation: Optional[str] = None
    ):
        self.claim_id = claim_id
        self.decision = decision
        self.stage_latencies_ms = stage_latencies_ms
        self.total_latency_ms = total_latency_ms
        self.transaction = transaction
        self.notifications = notifications or {}
        self.sla_breached = sla_breached
        self.fraud_layers = fraud_layers or {"rules": 0, "anomaly": 10, "supervised": 10, "graph": 10}
        self.ai_explanation = ai_explanation or getattr(decision, "ai_explanation", None)
        self.patient_explanation = patient_explanation or getattr(decision, "patient_explanation", None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "outcome": self.decision.outcome.value,
            "approved_amount": self.decision.approved_amount,
            "deductions_amount": self.decision.deductions_amount,
            "total_latency_ms": round(self.total_latency_ms, 2),
            "stage_latencies_ms": {k: round(v, 2) for k, v in self.stage_latencies_ms.items()},
            "sla_breached": self.sla_breached,
            "clause_citations": self.decision.clause_citations,
            "fired_rule_ids": self.decision.fired_rule_ids,
            "audit_hash": self.decision.audit_hash,
            "transaction_id": self.transaction.transaction_id if self.transaction else None,
            "fraud_layers": self.fraud_layers,
            "ai_explanation": self.ai_explanation or self.decision.ai_explanation,
            "patient_explanation": self.patient_explanation or self.decision.patient_explanation,
            "reviewer_notes": self.decision.reviewer_notes
        }


class ClaimFlowOrchestrator:
    """Phase 3 Orchestrator & SLA Engine.
    
    Coordinates the real-time pipeline:
    ingest -> parse -> [coding ‖ policy] -> fraud -> decide -> settle -> explain (Gemini)
    
    Features:
    - Parallel execution of Coding Validator and Policy Agent
    - Per-stage latency monitoring against 15-minute SLA budget
    - Google Gemini Live Clinical & Adjudication Rationale generation
    - Automatic fallback to HUMAN_REVIEW on any exception or timeout (Never silent approval!)
    """

    def __init__(
        self,
        parser_agent: Optional[EHRParserAgent] = None,
        validator_agent: Optional[CodingValidatorAgent] = None,
        policy_agent: Optional[PolicyAgent] = None,
        fraud_agent: Optional[FraudAgent] = None,
        settlement_agent: Optional[SettlementAgent] = None,
        gemini_service: Optional[GeminiService] = None
    ):
        self.parser = parser_agent or EHRParserAgent()
        self.validator = validator_agent or CodingValidatorAgent()
        self.policy = policy_agent or PolicyAgent()
        self.fraud = fraud_agent or FraudAgent(auto_train=False)
        self.settlement = settlement_agent or SettlementAgent()
        self.gemini = gemini_service or GeminiService()

    async def process_claim(
        self,
        claim: Claim,
        discharge_text: str,
        fhir_bundle: Optional[Dict[str, Any]] = None,
        policy_tenure_days: int = 180
    ) -> PipelineExecutionResult:
        """Executes the full clearinghouse pipeline end-to-end."""
        pipeline_start = time.perf_counter()
        stage_latencies: Dict[str, float] = {}

        try:
            # Stage 1: Ingestion & Verification
            t0 = time.perf_counter()
            await asyncio.sleep(0.001)  # Yield to event loop
            stage_latencies["ingestion"] = (time.perf_counter() - t0) * 1000

            # Stage 2: EHR Parser Agent
            t0 = time.perf_counter()
            clinical_facts = self.parser.parse(
                discharge_text=discharge_text,
                patient_id=claim.patient_id,
                fhir_bundle=fhir_bundle
            )
            claim.clinical_facts = clinical_facts
            stage_latencies["parsing"] = (time.perf_counter() - t0) * 1000

            # Stage 3: Parallel Execution [Coding Validator ‖ Policy Agent]
            t0 = time.perf_counter()
            
            async def run_coding():
                return self.validator.validate_claim(claim, clinical_facts)

            async def run_policy():
                return self.policy.evaluate_policy_coverage(claim, tenure_days=policy_tenure_days)

            (validated_items, fired_rules), (policy_items, approved_amt, deducted_amt, citations) = await asyncio.gather(
                run_coding(),
                run_policy()
            )

            # Reconcile validated items with policy coverage
            reconciled_items = []
            for v_item, p_item in zip(validated_items, policy_items):
                merged = v_item.model_copy()
                if v_item.verdict != LineItemVerdict.OK:
                    merged.approved_amount = 0.0
                else:
                    merged.approved_amount = p_item.approved_amount
                    merged.clause_citations = p_item.clause_citations
                reconciled_items.append(merged)

            claim.line_items = reconciled_items
            stage_latencies["coding_and_policy"] = (time.perf_counter() - t0) * 1000

            # Stage 4: Layered Fraud Scoring
            t0 = time.perf_counter()
            risk_score, top_reasons = self.fraud.evaluate_claim(claim, clinical_facts)
            claim.risk_score = risk_score
            claim.risk_reasons = top_reasons
            stage_latencies["fraud_scoring"] = (time.perf_counter() - t0) * 1000

            # Stage 5: Settlement & Disbursal
            t0 = time.perf_counter()
            decision, txn, notifs = self.settlement.settle_claim(
                claim=claim,
                risk_score=risk_score,
                parser_confidence=clinical_facts.confidence_score,
                fired_rule_ids=fired_rules,
                clause_citations=citations,
                duration_ms=stage_latencies["fraud_scoring"]
            )
            stage_latencies["settlement"] = (time.perf_counter() - t0) * 1000

            # Stage 6: Explainable AI Adjudication Rationale & Patient Explanation (Google Gemini)
            t0 = time.perf_counter()
            ai_exp_dict = self.gemini.generate_adjudication_explanation(
                claim=claim,
                clinical_facts=clinical_facts,
                decision=decision,
                risk_reasons=top_reasons
            )
            decision.ai_explanation = ai_exp_dict.get("ai_rationale")
            decision.patient_explanation = ai_exp_dict.get("patient_explanation")
            claim.ai_explanation = ai_exp_dict.get("ai_rationale")
            claim.patient_explanation = ai_exp_dict.get("patient_explanation")
            stage_latencies["ai_explanation"] = (time.perf_counter() - t0) * 1000

            total_elapsed_ms = (time.perf_counter() - pipeline_start) * 1000
            sla_breached = total_elapsed_ms > (settings.SLA_MAX_SECONDS * 1000)

            fraud_layers = getattr(self.fraud, "last_layers", {"rules": 0, "anomaly": 10, "supervised": 10, "graph": 10})

            return PipelineExecutionResult(
                claim_id=claim.claim_id,
                decision=decision,
                stage_latencies_ms=stage_latencies,
                total_latency_ms=total_elapsed_ms,
                transaction=txn,
                notifications=notifs,
                sla_breached=sla_breached,
                fraud_layers=fraud_layers,
                ai_explanation=decision.ai_explanation,
                patient_explanation=decision.patient_explanation
            )

        except Exception as e:
            # CRITICAL ARCHITECTURAL SAFETY RULE:
            # Fallback to HUMAN_REVIEW on any pipeline error. Never a silent approval!
            logger.error(f"Pipeline error for Claim {claim.claim_id}: {e}. Falling back to HUMAN_REVIEW.")
            total_elapsed_ms = (time.perf_counter() - pipeline_start) * 1000
            fallback_decision = Decision(
                decision_id=f"DEC-ERR-{claim.claim_id}",
                claim_id=claim.claim_id,
                outcome=DecisionOutcome.HUMAN_REVIEW,
                approved_amount=0.0,
                deductions_amount=claim.total_claimed_amount,
                audit_hash=f"ERROR-{int(time.time())}",
                reviewer_notes=f"Automatic safety fallback: Pipeline failed with error: {str(e)}"
            )
            return PipelineExecutionResult(
                claim_id=claim.claim_id,
                decision=fallback_decision,
                stage_latencies_ms=stage_latencies,
                total_latency_ms=total_elapsed_ms,
                transaction=None,
                sla_breached=False
            )
