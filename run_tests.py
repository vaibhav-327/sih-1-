import sys
import os

# Ensure workspace root in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.ml.risk_engine import UnifiedRiskEngine
from backend.services.validation_service import DataValidationService
from backend.ml.nlp_similarity import NLPSimilarityEngine, haversine_distance_km
from scripts.seed_database import seed_database
from fastapi.testclient import TestClient
from backend.main import app
import pandas as pd

def test_risk():
    print("  Testing UnifiedRiskEngine...", flush=True)
    row_clean = pd.Series({
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
    res_clean = UnifiedRiskEngine.calculate_project_risk(row_clean)
    assert res_clean["risk_score"] <= 30.0, f"Expected LOW risk score, got {res_clean['risk_score']}"
    assert res_clean["risk_level"] == "LOW"

    row_anomaly = pd.Series({
        "sanctioned_amount": 3000000.0,
        "released_amount": 2800000.0,
        "utilized_amount": 2700000.0,
        "physical_progress": 30.0,
        "financial_progress": 90.0,
        "delay_days": 120,
        "cost_deviation": 80.0,
        "anomaly_score": 75.0,
        "similarity_score": 10.0,
        "contractor_project_count": 10,
        "state": "Maharashtra",
        "district": "Pune",
        "constituency": "Pune"
    })
    res_anomaly = UnifiedRiskEngine.calculate_project_risk(row_anomaly)
    assert res_anomaly["risk_score"] >= 60.0
    assert len(res_anomaly["factors"]) >= 2
    assert "where" in res_anomaly and "what" in res_anomaly and "why" in res_anomaly and "next_action" in res_anomaly
    print("  [OK] UnifiedRiskEngine passed.", flush=True)

def test_validation():
    print("  Testing DataValidationService...", flush=True)
    df_clean = pd.DataFrame([{
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
        "contractor_name": "Apex Infra"
    }])
    _, rep_clean = DataValidationService.validate_dataframe(df_clean)
    assert rep_clean["data_quality_score"] >= 95.0

    df_dirty = pd.DataFrame([{
        "project_id": "MPLAD-001",
        "project_name": "Bad Project",
        "state": "Karnataka",
        "district": "Bengaluru",
        "constituency": "Bengaluru South",
        "sanctioned_amount": 1000000.0,
        "released_amount": 1500000.0, # Released > sanctioned
        "utilized_amount": 1800000.0, # Utilized > released
        "physical_progress": 150.0, # > 100
        "start_date": "2023-06-01",
        "expected_completion_date": "2023-01-01",
        "contractor_name": "Bad Contractor"
    }])
    _, rep_dirty = DataValidationService.validate_dataframe(df_dirty)
    assert rep_dirty["data_quality_score"] < 75.0
    print("  [OK] DataValidationService passed.", flush=True)

def test_nlp():
    print("  Testing NLPSimilarityEngine & Geospatial calculations...", flush=True)
    dist = haversine_distance_km(25.3176, 82.9739, 25.3500, 82.9900)
    assert 3.0 < dist < 8.0

    df = pd.DataFrame([
        {
            "project_id": "MPLAD-101",
            "project_name": "Construction of CC road from Rampur Main Chowk to Panchayat Bhavan",
            "project_description": "CC road paving and drainage in Rampur village.",
            "state": "Uttar Pradesh",
            "district": "Varanasi",
            "latitude": 25.3176,
            "longitude": 82.9739
        },
        {
            "project_id": "MPLAD-102",
            "project_name": "Construction of CC road from Rampur Main Chowk to Panchayat Bhavan Ward 4",
            "project_description": "CC road paving and drainage in Rampur village.",
            "state": "Uttar Pradesh",
            "district": "Varanasi",
            "latitude": 25.3180,
            "longitude": 82.9745
        }
    ])
    engine = NLPSimilarityEngine(similarity_threshold=0.75)
    res_df, meta = engine.detect_similar_projects(df)
    assert res_df.loc[0, "similarity_score"] >= 75.0
    print("  [OK] NLPSimilarityEngine passed.", flush=True)

def test_api():
    print("  Testing FastAPI Endpoints with TestClient...", flush=True)
    client = TestClient(app)
    
    # 1. Health
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    
    # 2. Dashboard
    r = client.get("/api/dashboard")
    assert r.status_code == 200, f"Dashboard failed: {r.text}"
    db_data = r.json()
    assert "kpis" in db_data
    assert "status_distribution" in db_data
    assert "risk_distribution" in db_data

    # 3. Projects
    r = client.get("/api/projects?page=1&page_size=5")
    assert r.status_code == 200
    p_data = r.json()
    assert len(p_data["projects"]) > 0
    first_id = p_data["projects"][0]["id"]

    # 4. Project Risk Explainability
    r = client.get(f"/api/projects/{first_id}/risk")
    assert r.status_code == 200
    risk_info = r.json()
    assert "where" in risk_info
    assert "what" in risk_info
    assert "why" in risk_info
    assert "next_action" in risk_info

    # 5. Contractors
    r = client.get("/api/contractors")
    assert r.status_code == 200

    # 6. Graph
    r = client.get("/api/contractors/network/graph")
    assert r.status_code == 200
    assert "nodes" in r.json()

    # 7. Map
    r = client.get("/api/map/projects?limit=20")
    assert r.status_code == 200
    assert r.json()["type"] == "FeatureCollection"

    # 8. Alerts
    r = client.get("/api/alerts")
    assert r.status_code == 200
    alerts = r.json()["alerts"]
    if len(alerts) > 0:
        a_id = alerts[0]["id"]
        upd = client.put(f"/api/alerts/{a_id}", json={
            "status": "FIELD_VERIFICATION",
            "assigned_officer": "District Quality Monitor",
            "investigation_notes": "Physical audit scheduled."
        })
        assert upd.status_code == 200
        assert upd.json()["status"] == "FIELD_VERIFICATION"

    # 9. Insights
    r = client.get("/api/insights")
    assert r.status_code == 200
    assert len(r.json()["insights"]) > 0

    # 10. Model Metrics
    r = client.get("/api/model/metrics")
    assert r.status_code == 200

    print("  [OK] All FastAPI endpoints passed.", flush=True)

def run_all():
    print("==================================================", flush=True)
    print("   MPLAD AI SENTINEL COMPREHENSIVE TEST SUITE", flush=True)
    print("==================================================", flush=True)
    
    print("\n[Step 1/5] Seeding Test Database with 250 records...", flush=True)
    seed_database(count=250)

    print("\n[Step 2/5] Running Risk Engine Tests...", flush=True)
    test_risk()

    print("\n[Step 3/5] Running Data Validation Tests...", flush=True)
    test_validation()

    print("\n[Step 4/5] Running NLP & Spatial Tests...", flush=True)
    test_nlp()

    print("\n[Step 5/5] Running API Endpoint Integration Tests...", flush=True)
    test_api()

    print("\n==================================================", flush=True)
    print("   ALL UNIT & INTEGRATION TESTS PASSED 100%!", flush=True)
    print("==================================================\n", flush=True)

if __name__ == "__main__":
    run_all()
