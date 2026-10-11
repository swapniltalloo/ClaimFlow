from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from app.models.domain import LineItem, ClinicalFacts


class BaseCodingRule(ABC):
    """Abstract base class for all deterministic coding validation rules."""

    rule_id: str
    rule_name: str
    category: str

    @abstractmethod
    def evaluate(
        self,
        item: LineItem,
        all_items: List[LineItem],
        clinical_facts: ClinicalFacts
    ) -> Tuple[bool, Optional[str]]:
        """Evaluates a single line item in the context of the entire claim and clinical facts.
        
        Returns:
            Tuple of (passed: bool, reason: Optional[str])
        """
        pass
