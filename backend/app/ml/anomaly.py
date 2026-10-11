import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Optional


class AnomalyDetector:
    """Layer 2: Unsupervised Isolation Forest Anomaly Detection."""

    def __init__(self, contamination: float = 0.15):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Fits Isolation Forest on baseline claim feature vectors."""
        self.model.fit(X)
        self.is_fitted = True

    def score(self, x: np.ndarray) -> float:
        """Returns anomaly risk score between 0.0 and 100.0."""
        if not self.is_fitted:
            # Fallback heuristic score based on feature bounds
            ratio = x[6]  # max_price_to_median_ratio
            if ratio > 2.0 or x[8] > 0 or x[9] > 0:
                return 80.0
            return 15.0

        if x.ndim == 1:
            x = x.reshape(1, -1)
        # decision_function gives negative values for anomalies, positive for normal
        raw_score = self.model.decision_function(x)[0]
        # Map raw score [-0.5, 0.5] to [100.0, 0.0]
        normalized = max(0.0, min(100.0, (0.5 - raw_score) * 100.0))
        return round(float(normalized), 2)
