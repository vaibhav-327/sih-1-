import unittest
from fastapi.testclient import TestClient
from backend.main import app
from scripts.seed_database import seed_database
import pandas as pd

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure test database has records seeded
        seed_database(count=200)
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_dashboard_endpoint(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("kpis", data)
        self.assertEqual(data["kpis"]["total_projects"], 200)
        self.assertIn("status_distribution", data)
        self.assertIn("risk_distribution", data)
        self.assertIn("data_source", data)

    def test_projects_list_and_filtering(self):
        response = self.client.get("/api/projects?page=1&page_size=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 200)
        self.assertEqual(len(data["projects"]), 10)

        # Risk level filter
        r_resp = self.client.get("/api/projects?risk_level=HIGH")
        self.assertEqual(r_resp.status_code, 200)
        for p in r_resp.json()["projects"]:
            self.assertEqual(p["risk_level"], "HIGH")

    def test_project_risk_explainability(self):
        list_resp = self.client.get("/api/projects?page=1&page_size=1")
        p_id = list_resp.json()["projects"][0]["id"]
        
        resp = self.client.get(f"/api/projects/{p_id}/risk")
        self.assertEqual(resp.status_code, 200)
        risk_data = resp.json()
        self.assertIn("where", risk_data)
        self.assertIn("what", risk_data)
        self.assertIn("why", risk_data)
        self.assertIn("next_action", risk_data)
        self.assertIn("factors", risk_data)

    def test_contractors_and_graph(self):
        resp = self.client.get("/api/contractors")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.json()["total"], 0)

        graph_resp = self.client.get("/api/contractors/network/graph")
        self.assertEqual(graph_resp.status_code, 200)
        self.assertIn("nodes", graph_resp.json())
        self.assertIn("edges", graph_resp.json())

    def test_alerts_and_update(self):
        resp = self.client.get("/api/alerts")
        self.assertEqual(resp.status_code, 200)
        alerts = resp.json()["alerts"]
        self.assertGreater(len(alerts), 0)

        # Update alert status
        first_alert_id = alerts[0]["id"]
        put_resp = self.client.put(f"/api/alerts/{first_alert_id}", json={
            "status": "FIELD_VERIFICATION",
            "assigned_officer": "Chief Vigilance Officer",
            "investigation_notes": "Inspection scheduled for Friday."
        })
        self.assertEqual(put_resp.status_code, 200)
        self.assertEqual(put_resp.json()["status"], "FIELD_VERIFICATION")
        self.assertEqual(put_resp.json()["assigned_officer"], "Chief Vigilance Officer")

    def test_map_endpoint(self):
        resp = self.client.get("/api/map/projects?limit=50")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["type"], "FeatureCollection")
        self.assertLessEqual(len(resp.json()["features"]), 50)

    def test_insights_endpoint(self):
        resp = self.client.get("/api/insights")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("insights", resp.json())
        self.assertGreater(len(resp.json()["insights"]), 0)

    def test_model_metrics_endpoint(self):
        resp = self.client.get("/api/model/metrics")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["model_name"], "MPLAD AI Sentinel Hybrid Risk Engine")

if __name__ == "__main__":
    unittest.main()
