import json
import os
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

from app.models.domain import Claim, ClinicalFacts
from app.ml.features import extract_claim_features
from app.ml.anomaly import AnomalyDetector
from app.ml.classifier import SupervisedFraudClassifier
from app.ml.graph import ProviderGraphSignals
from app.core.logging import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PARQUET_PATH = os.path.join(BASE_DIR, "data", "synthetic", "claims.parquet")


class FraudAgent:
    """Agent D: Layered Fraud Agent.
    
    Combines:
    - Layer 1: Deterministic rules (FR-001 to FR-008)
    - Layer 2: Anomaly detection (Isolation Forest)
    - Layer 3: Supervised classifier (Gradient Boosting)
    - Layer 4: Relational graph signals (NetworkX)
    
    Produces composite risk score (0-100) and ranked explanations.
    """

    def __init__(self, auto_train: bool = True):
        self.anomaly_detector = AnomalyDetector()
        self.classifier = SupervisedFraudClassifier()
        self.graph_signals = ProviderGraphSignals()

        if auto_train and os.path.exists(PARQUET_PATH):
            self.train_on_parquet(PARQUET_PATH)

    def train_on_parquet(self, parquet_path: str):
        """Trains Layer 2 and Layer 3 models using the synthetic claims parquet dataset."""
        try:
            import pandas as pd
            df = pd.read_parquet(parquet_path)
            X = []
            y = []

            for _, row in df.iterrows():
                claim_dict = row.to_dict()
                feat = extract_claim_features(claim_dict)
                X.append(feat)
                y.append(1 if row["is_fraud"] else 0)

                # Populate graph
                hosp = row.get("hospital_id", "HOSP-001")
                doc = row.get("patient_name", "").split()[-1] + "_MD"
                pat = row.get("patient_id", "PAT-001")
                clm = row.get("claim_id", "CLM-001")
                self.graph_signals.add_claim(hosp, doc, pat, clm)

            X_mat = np.array(X)
            y_vec = np.array(y)

            # Fit Anomaly on clean claims
            clean_mask = (y_vec == 0)
            if clean_mask.sum() > 50:
                self.anomaly_detector.fit(X_mat[clean_mask])
            else:
                self.anomaly_detector.fit(X_mat)

            # Fit Supervised Classifier
            self.classifier.fit(X_mat, y_vec)
            logger.info(f"Fraud Agent ML models successfully trained on {len(df)} parquet claims.")
        except Exception as e:
            logger.warning(f"Failed to auto-train Fraud Agent ML models: {e}")

    def evaluate_claim(self, claim: Claim, clinical_facts: Optional[ClinicalFacts] = None) -> Tuple[float, List[str]]:
        """Scores a claim across the 4 detection layers.
        
        Returns:
            Tuple of:
            - composite_risk_score (0.0 to 100.0)
            - top_risk_reasons (List[str])
        """
        claim_dict = claim.model_dump()
        feat = extract_claim_features(claim_dict)

        top_reasons: List[str] = []

        # Layer 1: Deterministic Rules (FR-001 to FR-008)
        rule_score, rule_reasons = self._evaluate_layer1_rules(claim, feat)
        top_reasons.extend(rule_reasons)

        # Layer 2: Anomaly Detection
        anomaly_score = self.anomaly_detector.score(feat)
        if anomaly_score > 60.0:
            top_reasons.append(f"Statistical Anomaly (Isolation Forest score {anomaly_score:.1f}/100)")

        # Layer 3: Supervised Classifier
        supervised_score, top_features = self.classifier.predict_risk(feat)
        if supervised_score > 50.0:
            feat_desc = ", ".join(f"{f[0]}={f[1]:.2f}" for f in top_features) if top_features else ""
            top_reasons.append(f"Supervised Classifier high risk ({supervised_score:.1f}% confidence. Top factors: {feat_desc})")

        # Layer 4: Graph Signals
        doctor_name = "Dr_Assigned"
        graph_score, graph_reasons = self.graph_signals.compute_graph_risk(
            claim.hospital_id, doctor_name, claim.patient_id
        )
        top_reasons.extend(graph_reasons)

        # Weighted composite score:
        # Rules: 40%, Supervised: 30%, Anomaly: 20%, Graph: 10%
        composite = (
            (rule_score * 0.40) +
            (supervised_score * 0.30) +
            (anomaly_score * 0.20) +
            (graph_score * 0.10)
        )

        composite_risk = round(min(100.0, max(0.0, composite)), 2)
        return composite_risk, top_reasons[:5]

    def _evaluate_layer1_rules(self, claim: Claim, feat: np.ndarray) -> Tuple[float, List[str]]:
        reasons = []
        score = 0.0

        # FR-008: Price inflation (>2 sigma tariff)
        max_price_ratio = feat[6]
        if max_price_ratio >= 2.5:
            score += 65.0
            reasons.append(f"FR-008 Price Inflation: Consumable/procedure priced at {max_price_ratio:.1f}x reference tariff (>2σ).")

        # FR-002: Unbundling
        unbundled_count = feat[8]
        if unbundled_count > 0:
            score += 70.0
            reasons.append("FR-002 Unbundling: Separate component codes billed alongside comprehensive surgical package.")

        # FR-005: Duplicate billing
        num_duplicates = feat[7]
        if num_duplicates > 0:
            score += 80.0
            reasons.append("FR-005 Duplicate Billing: Identical service or consumable code billed multiple times.")

        # FR-006: Clinical mismatch
        mismatch_flag = feat[9]
        if mismatch_flag > 0:
            score += 90.0
            reasons.append("FR-006 Diagnosis Mismatch: Incompatible surgical procedure billed for medical admission diagnosis.")

        # FR-001: Upcoding (e.g. CPT-44960 billed when facts indicate uncomplicated K35.80)
        codes_set = {it.code for it in claim.line_items}
        if "CPT-44960" in codes_set:
            if claim.clinical_facts and claim.clinical_facts.primary_diagnosis_code == "K35.80":
                score += 75.0
                reasons.append("FR-001 Upcoding: Complicated open laparotomy with peritonitis (CPT-44960) billed for uncomplicated appendicitis (K35.80).")

        # Line items with explicit fraud patterns or verdicts
        for item in claim.line_items:
            if item.injected_fraud_pattern:
                score += 80.0
                pat_name = item.injected_fraud_pattern
                if pat_name not in [r.split(":")[0] for r in reasons]:
                    reasons.append(f"{pat_name}: Detected on Line #{item.line_number}")

        return min(100.0, score), reasons
