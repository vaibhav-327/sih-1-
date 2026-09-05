import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

class UnifiedRiskEngine:
    """
    Modular, explainable risk scoring engine.
    Combines Isolation Forest anomaly score, statistical cost deviations,
    delay tracking, financial-physical progress gaps, contractor metrics,
    and NLP duplicate scores into a composite 0-100 Risk Score.
    """

    @staticmethod
    def calculate_project_risk(row: pd.Series) -> Dict[str, Any]:
        risk_score = 0.0
        factors = []
        recommendations = []
        
        # Extract inputs
        sanc = float(row.get("sanctioned_amount", 0.0))
        phys_prog = float(row.get("physical_progress", 0.0))
        fin_prog = float(row.get("financial_progress", 0.0))
        delay_days = int(row.get("delay_days", 0))
        cost_dev = float(row.get("cost_deviation", 0.0))
        anomaly_score = float(row.get("anomaly_score", 0.0))
        sim_score = float(row.get("similarity_score", 0.0))
        sim_id = row.get("similar_project_id", None)
        contractor_count = int(row.get("contractor_project_count", 1))
        
        # 1. Implementation Efficiency Gap (Financial >> Physical)
        eff_gap = fin_prog - phys_prog
        if eff_gap >= 40.0:
            contrib = min(30.0, eff_gap * 0.5)
            risk_score += contrib
            factors.append({
                "factor": "High Financial vs Physical Progress Gap",
                "impact": "CRITICAL" if eff_gap >= 50 else "HIGH",
                "value": f"Gap of {eff_gap:.1f}% (Financial: {fin_prog:.1f}%, Physical: {phys_prog:.1f}%)",
                "score_contribution": round(contrib, 1),
                "description": "High fund disbursement reported while ground physical execution lags substantially."
            })
            recommendations.append("Conduct physical on-site inspection to verify ground completion status before releasing subsequent tranches.")
        elif eff_gap >= 25.0:
            contrib = 15.0
            risk_score += contrib
            factors.append({
                "factor": "Moderate Progress Disparity",
                "impact": "MEDIUM",
                "value": f"Gap of {eff_gap:.1f}%",
                "score_contribution": round(contrib, 1),
                "description": "Disbursement velocity moderately outpacing physical milestones."
            })
            recommendations.append("Request geo-tagged photographs and measurement book entries from the implementing agency.")

        # 2. Cost Inflation Anomaly
        if cost_dev >= 70.0:
            contrib = 25.0
            risk_score += contrib
            factors.append({
                "factor": "Significant Cost Deviation",
                "impact": "HIGH",
                "value": f"{cost_dev:.1f}% above peer group median",
                "score_contribution": round(contrib, 1),
                "description": "Sanctioned cost is statistically higher than comparable projects of the same category in this region."
            })
            recommendations.append("Review detailed project estimate (DPR) and rate approvals against the state Schedule of Rates (SoR).")
        elif cost_dev >= 40.0:
            contrib = 14.0
            risk_score += contrib
            factors.append({
                "factor": "Moderate Cost Deviation",
                "impact": "MEDIUM",
                "value": f"{cost_dev:.1f}% above peer group median",
                "score_contribution": round(contrib, 1),
                "description": "Cost is above average for similar infrastructure in this state."
            })

        # 3. Schedule Delay & Stalled Progress
        if delay_days >= 180:
            contrib = 20.0
            risk_score += contrib
            factors.append({
                "factor": "Extreme Implementation Delay",
                "impact": "HIGH",
                "value": f"{delay_days} days overdue",
                "score_contribution": round(contrib, 1),
                "description": "Project has severely breached target completion timeline with pending milestones."
            })
            recommendations.append("Issue show-cause notice to the implementing agency and contractor regarding timeline adherence.")
        elif delay_days >= 60:
            contrib = 10.0
            risk_score += contrib
            factors.append({
                "factor": "Moderate Timeline Delay",
                "impact": "MEDIUM",
                "value": f"{delay_days} days overdue",
                "score_contribution": round(contrib, 1),
                "description": "Work is running behind expected completion date."
            })

        # 4. Isolation Forest ML Anomaly Score
        if anomaly_score >= 70.0:
            contrib = 15.0
            risk_score += contrib
            factors.append({
                "factor": "Multi-Dimensional ML Pattern Anomaly",
                "impact": "HIGH",
                "value": f"Anomaly Index: {anomaly_score:.1f}/100",
                "score_contribution": round(contrib, 1),
                "description": "Unsupervised Isolation Forest detected unusual multivariate patterns across financial, timeline, and agency parameters."
            })
        elif anomaly_score >= 50.0:
            contrib = 8.0
            risk_score += contrib
            factors.append({
                "factor": "Mild Multivariate Anomaly",
                "impact": "LOW",
                "value": f"Anomaly Index: {anomaly_score:.1f}/100",
                "score_contribution": round(contrib, 1),
                "description": "Slight divergence from statistical peer norms."
            })

        # 5. NLP Description Similarity / Duplicate Suspect
        if sim_score >= 85.0 and sim_id:
            contrib = 20.0
            risk_score += contrib
            factors.append({
                "factor": "Potential Similar / Duplicate Project",
                "impact": "HIGH",
                "value": f"{sim_score:.1f}% text similarity with {sim_id}",
                "score_contribution": round(contrib, 1),
                "description": "Project title and scope description are nearly identical to another work sanctioned in close proximity."
            })
            recommendations.append(f"Review spatial scope with project {sim_id} to ensure no overlapping work or duplicate sanctioning.")
        elif sim_score >= 75.0 and sim_id:
            contrib = 8.0
            risk_score += contrib
            factors.append({
                "factor": "High Text Similarity with Nearby Work",
                "impact": "LOW",
                "value": f"{sim_score:.1f}% similarity with {sim_id}",
                "score_contribution": round(contrib, 1),
                "description": "Similar work description recorded in the same district."
            })

        # 6. Contractor Concentration
        if contractor_count >= 25:
            contrib = 8.0
            risk_score += contrib
            factors.append({
                "factor": "High Contractor Concentration",
                "impact": "MEDIUM",
                "value": f"{contractor_count} works awarded to same contractor",
                "score_contribution": round(contrib, 1),
                "description": "High volume of projects clustered under a single contracting entity."
            })
            recommendations.append("Assess contractor operational capacity and workload distribution across concurrent schemes.")

        # Final score scaling (strictly bounded 0.0 - 100.0)
        final_score = min(100.0, max(0.0, risk_score))
        
        # Categorize risk level: LOW (0–30), MEDIUM (31–60), HIGH (61–80), CRITICAL (81–100)
        if final_score > 80.0:
            risk_level = "CRITICAL"
        elif final_score > 60.0:
            risk_level = "HIGH"
        elif final_score > 30.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Default recommendation if clean
        if len(recommendations) == 0:
            recommendations.append("Continue routine milestone monitoring as per standard MPLADS operational guidelines.")

        # Structure 4 Questions answers
        where = {
            "state": str(row.get("state", "Unknown")),
            "district": str(row.get("district", "Unknown")),
            "constituency": str(row.get("constituency", "Unknown")),
            "latitude": float(row.get("latitude", 0.0)) if pd.notnull(row.get("latitude")) else None,
            "longitude": float(row.get("longitude", 0.0)) if pd.notnull(row.get("longitude")) else None
        }
        what = f"Flagged with {risk_level} risk score ({final_score:.1f}/100) due to {len(factors)} active risk indicators."
        why = [f"{f['factor']}: {f['value']}" for f in factors]
        next_action = recommendations[0] if recommendations else "Routine monitoring."

        return {
            "risk_score": round(final_score, 1),
            "risk_level": risk_level,
            "factors": factors,
            "recommended_actions": recommendations,
            "where": where,
            "what": what,
            "why": why,
            "next_action": next_action
        }

    @staticmethod
    def evaluate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        scores = []
        levels = []
        reasons_list = []
        actions_list = []

        for _, row in df.iterrows():
            eval_res = UnifiedRiskEngine.calculate_project_risk(row)
            scores.append(eval_res["risk_score"])
            levels.append(eval_res["risk_level"])
            reasons_list.append(eval_res["factors"])
            actions_list.append(eval_res["recommended_actions"])

        df["risk_score"] = scores
        df["risk_level"] = levels
        df["risk_reasons"] = reasons_list
        df["recommended_actions"] = actions_list

        return df
