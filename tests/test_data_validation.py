import unittest
import pandas as pd
from backend.services.validation_service import DataValidationService

class TestDataValidation(unittest.TestCase):
    def test_validation_clean_data(self):
        df = pd.DataFrame([
            {
                "project_id": "MPLAD-001",
                "project_name": "Paved Road",
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "constituency": "Varanasi",
                "sanctioned_amount": 2000000.0,
                "released_amount": 1800000.0,
                "utilized_amount": 1500000.0,
                "physical_progress": 80.0,
                "start_date": "2023-01-01",
                "expected_completion_date": "2023-08-01",
                "contractor_name": "Apex Infra",
                "latitude": 25.3,
                "longitude": 82.9
            }
        ])
        _, report = DataValidationService.validate_dataframe(df)
        self.assertGreaterEqual(report["data_quality_score"], 95.0)
        self.assertEqual(len(report["issues"]), 0)

    def test_validation_detects_violations(self):
        df = pd.DataFrame([
            {
                "project_id": "MPLAD-001",
                "project_name": "Faulty Project",
                "state": "Karnataka",
                "district": "Bengaluru",
                "constituency": "Bengaluru South",
                "sanctioned_amount": 1000000.0,
                "released_amount": 1500000.0, # Released > Sanctioned
                "utilized_amount": 1800000.0, # Utilized > Released
                "physical_progress": 120.0,   # Progress > 100
                "start_date": "2023-06-01",
                "expected_completion_date": "2023-01-01", # Completion before start
                "contractor_name": "Test Contractor"
            },
            {
                "project_id": "MPLAD-001", # Duplicate ID
                "project_name": "Duplicate Project",
                "state": "Karnataka",
                "district": "Bengaluru",
                "constituency": "Bengaluru South",
                "sanctioned_amount": -50000.0, # Negative amount
                "released_amount": 0.0,
                "utilized_amount": 0.0,
                "physical_progress": 0.0,
                "contractor_name": "Test Contractor"
            }
        ])
        _, report = DataValidationService.validate_dataframe(df)
        self.assertLess(report["data_quality_score"], 70.0)
        rules_flagged = [iss["rule"] for iss in report["issues"]]
        self.assertIn("Duplicate Project IDs", rules_flagged)
        self.assertIn("Released Amount Exceeds Sanctioned", rules_flagged)
        self.assertIn("Utilized Amount Exceeds Released", rules_flagged)

if __name__ == "__main__":
    unittest.main()
