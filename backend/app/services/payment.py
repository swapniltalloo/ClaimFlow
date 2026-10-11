import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class PaymentTransaction(BaseModel):
    transaction_id: str
    idempotency_key: str
    claim_id: str
    hospital_id: str
    amount: float
    currency: str = "INR"
    channel: str = "SIMULATED_NEFT_UPI"
    status: str = "SUCCESS"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MockPaymentGateway:
    """Simulated payment gateway with strict idempotency verification.
    
    Guarantees that replaying a claim or transaction with an identical idempotency key
    will NEVER double-pay.
    """

    def __init__(self):
        # In-memory idempotency cache: idempotency_key -> PaymentTransaction
        self._processed_transactions: Dict[str, PaymentTransaction] = {}

    def disburse_payment(
        self,
        idempotency_key: str,
        claim_id: str,
        hospital_id: str,
        amount: float
    ) -> Tuple[PaymentTransaction, bool]:
        """Disburses funds to the hospital or returns existing transaction if already executed.
        
        Returns:
            Tuple of (transaction: PaymentTransaction, was_already_processed: bool)
        """
        if idempotency_key in self._processed_transactions:
            # Idempotent replay: return cached transaction without re-disbursing funds
            return self._processed_transactions[idempotency_key], True

        tx = PaymentTransaction(
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            idempotency_key=idempotency_key,
            claim_id=claim_id,
            hospital_id=hospital_id,
            amount=round(amount, 2),
            timestamp=datetime.now(timezone.utc)
        )
        self._processed_transactions[idempotency_key] = tx
        return tx, False
