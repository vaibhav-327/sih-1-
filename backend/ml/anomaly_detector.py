import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any, List

FEATURE_COLUMNS = [
    "sanctioned_amount",
    "cost_per_beneficiary",
    "duration_days",
    "delay_days",
    "financial_progress",
    "physical_progress",
    "efficiency_gap",
    "utilization_percentage",
    "contractor_project_count",
    "contractor_total_value",
    "constituency_project_count",
    "cost_deviation"
]

class IsolationForestAnomalyDetector:
    """
    Unsupervised multi-dimensional anomaly detection using scikit-learn Isolation Forest.
    Standardizes feature space and maps decision function anomaly scores to 0-100 scale.
    """

    def __init__(self, contamination: float = 0.08, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples="auto",
            bootstrap=False,
            n_jobs=1
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = FEATURE_COLUMNS

    def fit_predict(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        df = df.copy()
        
        # Prepare feature matrix
        X_df = pd.DataFrame(index=df.index)
        for col in self.feature_names:
            if col in df.columns:
                X_df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            else:
                X_df[col] = 0.0

        # Scale features
        X_scaled = self.scaler.fit_transform(X_df)
        
        # Fit model and predict
        self.model.fit(X_scaled)
        self.is_fitted = True
        
        # raw decision score: lower values represent higher anomaly degree
        raw_scores = self.model.decision_function(X_scaled)
        predictions = self.model.predict(X_scaled) # -1 for anomaly, 1 for inlier
        
        # Normalize score to 0 - 100 range where 100 = most anomalous, 0 = normal
        # Min-max inversion of decision score
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s > min_s:
            norm_scores = 100.0 * (1.0 - (raw_scores - min_s) / (max_s - min_s))
        else:
            norm_scores = np.zeros(len(df))

        df["anomaly_score"] = norm_scores.round(1)
        df["is_ml_anomaly"] = (predictions == -1)

        metrics = {
            "model_type": "Isolation Forest",
            "total_samples": len(df),
            "features_used": self.feature_names,
            "anomalies_detected": int((predictions == -1).sum()),
            "anomaly_rate": round(float((predictions == -1).mean()) * 100, 2),
            "contamination_parameter": self.contamination,
            "random_state": self.random_state
        }

        return df, metrics
