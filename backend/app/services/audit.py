import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.models.domain import AuditEvent, Decision, Claim
from app.core.security import compute_input_hash
from app.core.logging import logger


class AuditService:
    """Immutable Audit Trail Service.
    
    Logs every clearinghouse decision, input payload SHA-256 hash, model versions,
    fired rule IDs, and execution durations to guarantee reproducible adjudication.
    """

    def __init__(self):
        self._audit_log: List[AuditEvent] = []

    def record_event(
        self,
        claim_id: str,
        stage: str,
        input_payload: Any,
        rule_ids_fired: List[str],
        duration_ms: float,
        details: Optional[Dict[str, Any]] = None,
        model_version: str = "v1.0.0"
    ) -> AuditEvent:
        """Creates an immutable audit record with cryptographic input hash."""
        input_hash = compute_input_hash(input_payload)
        event = AuditEvent(
            event_id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            claim_id=claim_id,
            stage=stage,
            input_hash=input_hash,
            rule_ids_fired=sorted(list(set(rule_ids_fired))),
            model_version=model_version,
            duration_ms=round(duration_ms, 2),
            timestamp=datetime.now(timezone.utc),
            details=details or {}
        )
        self._audit_log.append(event)
        logger.info(f"Audit event recorded: [{stage}] Claim {claim_id} | Hash: {input_hash[:12]}... | Rules: {event.rule_ids_fired}")
        return event

    def get_events_for_claim(self, claim_id: str) -> List[AuditEvent]:
        return [e for e in self._audit_log if e.claim_id == claim_id]
