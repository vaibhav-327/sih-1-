import unittest
import pandas as pd
from backend.ml.risk_engine import UnifiedRiskEngine

class TestRiskEngine(unittest.TestCase):
    def test_risk_calculation_clean_project(self):
        row = pd.Series({
            "sanctioned_amount": 2000000.0,
            "released_amount": 2000000.0,
            "utilized_amount": 1900000.0,
            "physical_progress": 95.0,
            "financial_progress": 95.0,
            "delay_days": 0,
            "cost_deviation": 5.0,
            "anomaly_score": 10.0,
            "similarity_score": 0.0,
            "contractor_project_count": 5,
            "state": "Uttar Pradesh",
            "district": "Varanasi",
            "constituency": "Varanasi"
        })
        result = UnifiedRiskEngine.calculate_project_risk(row)
        self.assertLessEqual(result["risk_score"], 30.0)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(len(result["factors"]), 0)

    def test_risk_calculation_high_efficiency_gap(self):
        row = pd.Series({
            "sanctioned_amount": 3000000.0,
            "released_amount": 2800000.0,
            "utilized_amount": 2700000.0,
            "physical_progress": 30.0,
            "financial_progress": 90.0, # 60% efficiency gap
            "delay_days": 120,
            "cost_deviation": 80.0,
            "anomaly_score": 75.0,
            "similarity_score": 10.0,
            "contractor_project_count": 10,
            "state": "Maharashtra",
            "district": "Pune",
            "constituency": "Pune"
        })
        result = UnifiedRiskEngine.calculate_project_risk(row)
        self.assertGreaterEqual(result["risk_score"], 60.0)
        self.assertIn(result["risk_level"], ("HIGH", "CRITICAL"))
        factor_names = [f["factor"] for f in result["factors"]]
        self.assertIn("High Financial vs Physical Progress Gap", factor_names)
        self.assertIn("Significant Cost Deviation", factor_names)
        self.assertGreater(len(result["recommended_actions"]), 0)

    def test_risk_explainability_structure(self):
        row = pd.Series({
            "sanctioned_amount": 2500000.0,
            "physical_progress": 50.0,
            "financial_progress": 85.0,
            "delay_days": 70,
            "cost_deviation": 45.0,
            "anomaly_score": 55.0,
            "similarity_score": 88.0,
            "similar_project_id": "MPLAD-00042",
            "contractor_project_count": 30,
            "state": "Bihar",
            "district": "Patna",
            "constituency": "Patna Sahib"
        })
        result = UnifiedRiskEngine.calculate_project_risk(row)
        self.assertIn("where", result)
        self.assertIn("what", result)
        self.assertIn("why", result)
        self.assertIn("next_action", result)
        self.assertEqual(result["where"]["state"], "Bihar")
        self.assertEqual(result["where"]["district"], "Patna")

if __name__ == "__main__":
    unittest.main()
