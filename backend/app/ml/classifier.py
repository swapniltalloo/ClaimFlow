import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from typing import Dict, Any, List, Tuple
from app.ml.features import FEATURE_NAMES


class SupervisedFraudClassifier:
    """Layer 3: Supervised Gradient Boosting Classifier with feature attribution."""

    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=4,
            random_state=42
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fits the classifier on labeled historical claim features."""
        self.model.fit(X, y)
        self.is_fitted = True

    def predict_risk(self, x: np.ndarray) -> Tuple[float, List[Tuple[str, float]]]:
        """Predicts probability of fraud (0.0 to 100.0) and top contributing features.
        
        Returns:
            Tuple of:
            - risk_score (0.0 - 100.0)
            - top_features: list of (feature_name, importance_weight)
        """
        if x.ndim == 1:
            x_2d = x.reshape(1, -1)
        else:
            x_2d = x

        if not self.is_fitted:
            # Rule-based fallback if model not pre-fitted
            score = 10.0
            reasons = []
            if x[6] > 2.0:
                score += 50.0
                reasons.append(("max_price_to_median_ratio", float(x[6])))
            if x[8] > 0:
                score += 40.0
                reasons.append(("unbundled_count", float(x[8])))
            if x[9] > 0:
                score += 45.0
                reasons.append(("mismatch_flag", float(x[9])))
            return min(100.0, score), reasons

        prob = self.model.predict_proba(x_2d)[0][1]
        risk_score = round(float(prob * 100.0), 2)

        # Compute feature attribution using tree feature importances & sample activations
        importances = self.model.feature_importances_
        feature_scores = []
        for i, name in enumerate(FEATURE_NAMES):
            weight = float(importances[i] * (x[i] / (1.0 + abs(x[i]))))
            if weight > 0.01:
                feature_scores.append((name, round(weight, 4)))

        feature_scores.sort(key=lambda item: item[1], reverse=True)
        return risk_score, feature_scores[:3]
