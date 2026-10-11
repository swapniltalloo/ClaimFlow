import json
import os
from typing import List, Dict, Any, Tuple, Optional
from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict, PolicyCoverage
from app.core.logging import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
POLICIES_DIR = os.path.join(BASE_DIR, "data", "policies")


class PolicyAgent:
    """Agent C: Policy Agent (RAG & Deterministic Payable Calculator).
    
    Evaluates billed line items against policy clauses, limits, room caps, waiting periods,
    and exclusions. Computes exact payable amounts deterministically, ensuring EVERY deduction
    carries an explicit, verifiable clause citation.
    """

    def __init__(self, policies_dir: Optional[str] = None):
        self.policies_dir = policies_dir or POLICIES_DIR
        self.policies: Dict[str, Dict[str, Any]] = self._load_policies()

    def _load_policies(self) -> Dict[str, Dict[str, Any]]:
        loaded = {}
        if os.path.exists(self.policies_dir):
            for fname in os.listdir(self.policies_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(self.policies_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        loaded[data["policy_id"]] = data
        return loaded

    def evaluate_policy_coverage(
        self,
        claim: Claim,
        policy_id: Optional[str] = None,
        tenure_days: int = 365
    ) -> Tuple[List[LineItem], float, float, List[str]]:
        """Calculates payable amounts deterministically with per-deduction clause citations.
        
        Returns:
            Tuple of:
            - updated_line_items (with approved_amount, verdict, clause_citations)
            - total_approved_amount
            - total_deducted_amount
            - all_clause_citations
        """
        pol_id = policy_id or claim.policy_id
        policy = self.policies.get(pol_id)
        if not policy:
            logger.warning(f"Policy {pol_id} not found in repository. Using default coverage.")
            policy = list(self.policies.values())[0] if self.policies else {}

        copay_pct = float(policy.get("copay_percentage", 0.0))
        room_cap = policy.get("room_rent_cap_daily")
        icu_cap = policy.get("icu_rent_cap_daily")
        sub_limits = policy.get("sub_limits", {})
        exclusions = policy.get("exclusions", [])
        waiting_days = int(policy.get("initial_waiting_period_days", 30))

        updated_items: List[LineItem] = []
        all_citations: set[str] = set()
        running_approved_total = 0.0

        for item in claim.line_items:
            item_copy = item.model_copy(deep=True)
            clause_citations: List[str] = []
            verdict_reasons: List[str] = list(item_copy.verdict_reasons)

            # If item was already rejected by Coding Validator (MISMATCH or UNSUPPORTED)
            if item_copy.verdict in {LineItemVerdict.MISMATCH, LineItemVerdict.UNSUPPORTED}:
                item_copy.approved_amount = 0.0
                updated_items.append(item_copy)
                continue

            current_allowable = item_copy.total_amount

            # 1. Check Initial Waiting Period
            if tenure_days < waiting_days:
                citation = f"SEC-5.1 Initial Waiting Period: Claim occurred at Day {tenure_days} (before mandatory {waiting_days}-day waiting period). 100% deduction applied."
                clause_citations.append(citation)
                verdict_reasons.append(citation)
                all_citations.add(citation)
                item_copy.verdict = LineItemVerdict.MISMATCH
                item_copy.approved_amount = 0.0
                item_copy.clause_citations = clause_citations
                item_copy.verdict_reasons = verdict_reasons
                updated_items.append(item_copy)
                continue

            # 2. Check Exclusions
            is_excluded = False
            for excl in exclusions:
                if any(word.lower() in item_copy.description.lower() for word in excl.split() if len(word) > 4):
                    citation = f"SEC-EXCL General Exclusion: '{excl}' is excluded under policy terms. Inadmissible expense."
                    clause_citations.append(citation)
                    verdict_reasons.append(citation)
                    all_citations.add(citation)
                    is_excluded = True
                    break

            if is_excluded:
                item_copy.verdict = LineItemVerdict.MISMATCH
                item_copy.approved_amount = 0.0
                item_copy.clause_citations = clause_citations
                item_copy.verdict_reasons = verdict_reasons
                updated_items.append(item_copy)
                continue

            # 3. Check Room Rent / ICU Caps
            if item_copy.item_type == LineItemType.ROOM_ICU:
                if item_copy.code == "ROOM-STD-PVT" and room_cap is not None:
                    daily_billed = item_copy.unit_price
                    if daily_billed > room_cap:
                        excess_per_day = daily_billed - room_cap
                        total_excess = excess_per_day * item_copy.quantity
                        current_allowable = max(0.0, current_allowable - total_excess)
                        citation = f"SEC-3.1 Room Rent Capping: Daily room rent billed at INR {daily_billed:,.0f} exceeds cap of INR {room_cap:,.0f}/day. Deducted excess INR {total_excess:,.0f} across {item_copy.quantity} days."
                        clause_citations.append(citation)
                        all_citations.add(citation)

                elif item_copy.code == "ROOM-ICU-BED" and icu_cap is not None:
                    daily_billed = item_copy.unit_price
                    if daily_billed > icu_cap:
                        excess_per_day = daily_billed - icu_cap
                        total_excess = excess_per_day * item_copy.quantity
                        current_allowable = max(0.0, current_allowable - total_excess)
                        citation = f"SEC-3.1 ICU Rent Capping: Daily ICU rent billed at INR {daily_billed:,.0f} exceeds cap of INR {icu_cap:,.0f}/day. Deducted excess INR {total_excess:,.0f}."
                        clause_citations.append(citation)
                        all_citations.add(citation)

            # 4. Check Procedural Sub-Limits
            for sub_key, sub_val in sub_limits.items():
                if sub_key.lower() in item_copy.description.lower() or sub_key.lower() in item_copy.code.lower():
                    if current_allowable > sub_val:
                        excess = current_allowable - sub_val
                        current_allowable = sub_val
                        citation = f"SEC-SUB Procedural Sub-Limit: Maximum admissible benefit for '{sub_key}' is capped at INR {sub_val:,.0f}. Deducted excess INR {excess:,.0f}."
                        clause_citations.append(citation)
                        all_citations.add(citation)

            # 5. Apply Mandatory Co-Payment
            if copay_pct > 0.0 and current_allowable > 0.0:
                copay_deduction = current_allowable * (copay_pct / 100.0)
                current_allowable -= copay_deduction
                citation = f"SEC-4.2 Mandatory Co-Payment: {copay_pct:.0f}% member co-pay applied (-INR {copay_deduction:,.2f})."
                clause_citations.append(citation)
                all_citations.add(citation)

            # Update line item verdict & approved amount
            item_copy.approved_amount = round(current_allowable, 2)
            item_copy.clause_citations = clause_citations
            if current_allowable < item_copy.total_amount:
                item_copy.verdict = LineItemVerdict.OK  # Approved with policy deductions
            item_copy.verdict_reasons = verdict_reasons

            running_approved_total += item_copy.approved_amount
            updated_items.append(item_copy)

        # 6. Apply Overall Sum Insured Cap
        sum_insured = float(policy.get("sum_insured", 500000.0))
        if running_approved_total > sum_insured:
            si_excess = running_approved_total - sum_insured
            citation = f"SEC-1.0 Sum Insured Exhaustion: Aggregate claim payable exceeded maximum policy sum insured of INR {sum_insured:,.0f}. Capped at limit (-INR {si_excess:,.2f})."
            all_citations.add(citation)
            running_approved_total = sum_insured

        total_claimed = sum(it.total_amount for it in claim.line_items)
        total_deducted = max(0.0, total_claimed - running_approved_total)

        return (
            updated_items,
            round(running_approved_total, 2),
            round(total_deducted, 2),
            sorted(list(all_citations))
        )
