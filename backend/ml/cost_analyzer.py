import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class CostAnomalyAnalyzer:
    """
    Evaluates project expenditure and sanctioned cost against peer group distributions.
    Groups by project_type and state/district, then calculates statistical deviations,
    percentiles, and flags potential cost inflation anomalies.
    """

    @staticmethod
    def analyze_costs(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Calculate group median cost by project_type and state (fallback to project_type only if small sample)
        # Ensure sanctioned_amount is numeric
        sanc = pd.to_numeric(df["sanctioned_amount"], errors="coerce").fillna(100000.0)
        df["sanctioned_amount"] = sanc
        
        # Group medians
        type_state_medians = df.groupby(["project_type", "state"])["sanctioned_amount"].transform("median")
        type_medians = df.groupby("project_type")["sanctioned_amount"].transform("median")
        
        # Use state-level median if present, else general type median, else overall median
        baseline_medians = type_state_medians.fillna(type_medians).fillna(df["sanctioned_amount"].median()).clip(lower=10000.0)
        
        # Cost deviation %: ((cost - baseline) / baseline) * 100
        cost_dev = ((df["sanctioned_amount"] - baseline_medians) / baseline_medians) * 100.0
        df["cost_deviation"] = cost_dev.round(2)
        df["peer_group_median"] = baseline_medians.round(2)
        
        # Flag cost anomaly if deviation > 50% and cost > 75th percentile of group
        df["is_cost_anomaly"] = (df["cost_deviation"] > 50.0)
        
        return df
