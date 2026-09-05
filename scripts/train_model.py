import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal
from backend.models.project import Project
from backend.services.feature_service import FeatureEngineeringService
from backend.ml.anomaly_detector import IsolationForestAnomalyDetector
from backend.ml.cost_analyzer import CostAnomalyAnalyzer
from backend.ml.nlp_similarity import NLPSimilarityEngine
from backend.ml.risk_engine import UnifiedRiskEngine

def main():
    print("🤖 Retraining MPLAD AI Sentinel Anomaly & Risk Models...")
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        if not projects:
            print("No records found in database. Please run scripts/seed_database.py first.")
            return

        data_list = []
        for p in projects:
            data_list.append({
                "project_id": p.id,
                "project_name": p.project_name,
                "project_description": p.project_description,
                "state": p.state,
                "district": p.district,
                "constituency": p.constituency,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "project_type": p.project_type,
                "beneficiary_count": p.beneficiary_count,
                "contractor_id": p.contractor_id,
                "contractor_name": p.contractor_name,
                "implementing_agency": p.implementing_agency,
                "sanctioned_amount": p.sanctioned_amount,
                "released_amount": p.released_amount,
                "utilized_amount": p.utilized_amount,
                "physical_progress": p.physical_progress,
                "financial_progress": p.financial_progress,
                "status": p.status,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "expected_completion_date": p.expected_completion_date.isoformat() if p.expected_completion_date else None
            })

        df = pd.DataFrame(data_list)
        feat_df = FeatureEngineeringService.engineer_features(df)
        cost_df = CostAnomalyAnalyzer.analyze_costs(feat_df)
        
        if_detector = IsolationForestAnomalyDetector()
        ml_df, if_metrics = if_detector.fit_predict(cost_df)
        
        nlp_engine = NLPSimilarityEngine()
        nlp_df, nlp_meta = nlp_engine.detect_similar_projects(ml_df)
        
        final_df = UnifiedRiskEngine.evaluate_dataframe(nlp_df)

        print(f"✅ Training completed successfully on {len(final_df)} records.")
        print(f"   • ML Pattern Anomalies: {if_metrics['anomalies_detected']}")
        print(f"   • High-Risk Projects: {(final_df['risk_score'] >= 60.0).sum()}")
        print(f"   • Duplicate suspects: {nlp_meta['similar_pairs_count']}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
