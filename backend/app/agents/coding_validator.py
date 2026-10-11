from typing import List, Dict, Any, Tuple
from app.models.domain import Claim, LineItem, LineItemVerdict, ClinicalFacts
from app.rules.base import BaseCodingRule
from app.rules.coding_rules import (
    CodeValidityRule,
    DiagnosisProcedureMatrixRule,
    BundlingMatrixRule,
    QuantityAndDurationRule,
    PhantomServiceRule,
    DuplicateBillingRule
)
from app.core.logging import logger


class CodingValidatorAgent:
    """Agent B: Coding Validator Agent.
    
    Performs deterministic validation of billed line items against clinical facts,
    diagnosis-procedure matrix, unbundling schedules, and quantity limits.
    Assigns verdicts: OK, MISMATCH, or UNSUPPORTED.
    """

    def __init__(self, rules: List[BaseCodingRule] = None):
        self.rules = rules or [
            CodeValidityRule(),
            DiagnosisProcedureMatrixRule(),
            BundlingMatrixRule(),
            QuantityAndDurationRule(),
            PhantomServiceRule(),
            DuplicateBillingRule()
        ]

    def validate_claim(self, claim: Claim, clinical_facts: ClinicalFacts) -> Tuple[List[LineItem], List[str]]:
        """Evaluates every line item in the claim, applying all deterministic rules.
        
        Returns:
            Tuple of (validated_line_items, fired_rule_ids)
        """
        validated_items: List[LineItem] = []
        all_fired_rules: set[str] = set()

        for item in claim.line_items:
            item_copy = item.model_copy(deep=True)
            item_verdict = LineItemVerdict.OK
            reasons = []

            for rule in self.rules:
                passed, reason = rule.evaluate(item_copy, claim.line_items, clinical_facts)
                if not passed:
                    all_fired_rules.add(rule.rule_id)
                    reasons.append(reason)

                    # Determine severity of verdict
                    if rule.rule_id in {"CR-001", "CR-005"}:
                        item_verdict = LineItemVerdict.UNSUPPORTED
                    else:
                        item_verdict = LineItemVerdict.MISMATCH

            item_copy.verdict = item_verdict
            item_copy.verdict_reasons = reasons

            # Calculate preliminary line item approval
            if item_verdict == LineItemVerdict.OK:
                item_copy.approved_amount = item_copy.total_amount
            else:
                item_copy.approved_amount = 0.0

            validated_items.append(item_copy)

        return validated_items, sorted(list(all_fired_rules))
