import os
import sys
import datetime
import pandas as pd
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import Base, engine, SessionLocal
from backend.models import (
    Project, Contractor, Constituency, Transaction, Milestone, Alert, AuditLog, ModelRun
)
from backend.data_sources.synthetic import SyntheticDataSource, CONTRACTORS_LIST, INDIAN_STATES_DATA
from backend.services.validation_service import DataValidationService
from backend.services.feature_service import FeatureEngineeringService
from backend.ml.anomaly_detector import IsolationForestAnomalyDetector
from backend.ml.cost_analyzer import CostAnomalyAnalyzer
from backend.ml.nlp_similarity import NLPSimilarityEngine
from backend.ml.risk_engine import UnifiedRiskEngine

def seed_database(count: int = 5000):
    print(f"[*] [1/7] Initializing Database & Generating {count:,} Synthetic MPLAD Records...", flush=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Step 1: Generate Synthetic Data
        generator = SyntheticDataSource(count=count, seed=42)
        raw_df, meta = generator.fetch_data()
        print(f"[OK] Generated {len(raw_df):,} projects across {len(INDIAN_STATES_DATA)} Indian States & UTs.", flush=True)

        # Step 2: Validate Data
        print("[*] [2/7] Running Data Validation & Integrity Checks...", flush=True)
        val_df, val_report = DataValidationService.validate_dataframe(raw_df)
        print(f"[OK] Data Quality Score: {val_report['data_quality_score']}/100. Issues identified: {len(val_report['issues'])}", flush=True)

        # Step 3: Feature Engineering
        print("[*] [3/7] Engineering Features (Cost per Beneficiary, Efficiency Gap, Timeline Delays)...", flush=True)
        feat_df = FeatureEngineeringService.engineer_features(val_df)

        # Step 4: ML Anomaly Detection (Isolation Forest & Cost Deviations)
        print("[*] [4/7] Training Isolation Forest & Running Cost Anomaly Analysis...", flush=True)
        cost_df = CostAnomalyAnalyzer.analyze_costs(feat_df)
        if_detector = IsolationForestAnomalyDetector(contamination=0.08, random_state=42)
        ml_df, if_metrics = if_detector.fit_predict(cost_df)
        print(f"[OK] Isolation Forest identified {if_metrics['anomalies_detected']} pattern anomalies ({if_metrics['anomaly_rate']}%).", flush=True)

        # Step 5: NLP Text Similarity Analysis
        print("[*] [5/7] Running NLP TF-IDF & Geospatial Duplicate Identification...", flush=True)
        nlp_engine = NLPSimilarityEngine(similarity_threshold=0.82)
        nlp_df, nlp_meta = nlp_engine.detect_similar_projects(ml_df)
        print(f"[OK] NLP engine flagged {nlp_meta['similar_pairs_count']} potential duplicate/similar work descriptions.", flush=True)

        # Step 6: Unified Risk Scoring Engine
        print("[*] [6/7] Synthesizing Multi-Factor Risk Scores (0-100)...", flush=True)
        final_df = UnifiedRiskEngine.evaluate_dataframe(nlp_df)

        # Step 7: Persisting into Database
        print("[*] [7/7] Seeding SQLite Database Tables...", flush=True)
        
        # A. Projects Table
        projects = []
        for _, row in final_df.iterrows():
            p = Project(
                id=str(row["project_id"]),
                project_name=str(row["project_name"]),
                project_description=str(row.get("project_description", "")),
                state=str(row["state"]),
                district=str(row["district"]),
                constituency=str(row["constituency"]),
                latitude=float(row["latitude"]) if pd.notnull(row["latitude"]) else None,
                longitude=float(row["longitude"]) if pd.notnull(row["longitude"]) else None,
                project_type=str(row["project_type"]),
                beneficiary_count=int(row.get("beneficiary_count", 500)),
                contractor_id=str(row["contractor_id"]),
                contractor_name=str(row["contractor_name"]),
                implementing_agency=str(row["implementing_agency"]),
                sanctioned_amount=float(row["sanctioned_amount"]),
                released_amount=float(row["released_amount"]),
                utilized_amount=float(row["utilized_amount"]),
                physical_progress=float(row["physical_progress"]),
                financial_progress=float(row["financial_progress"]),
                status=str(row["status"]),
                start_date=pd.to_datetime(row["start_date"]).to_pydatetime() if pd.notnull(row["start_date"]) else None,
                sanction_date=pd.to_datetime(row["sanction_date"]).to_pydatetime() if pd.notnull(row["sanction_date"]) else None,
                expected_completion_date=pd.to_datetime(row["expected_completion_date"]).to_pydatetime() if pd.notnull(row["expected_completion_date"]) else None,
                actual_completion_date=pd.to_datetime(row["actual_completion_date"]).to_pydatetime() if pd.notnull(row.get("actual_completion_date")) else None,
                duration_days=int(row["duration_days"]),
                delay_days=int(row["delay_days"]),
                cost_deviation=float(row["cost_deviation"]),
                utilization_percentage=float(row["utilization_percentage"]),
                efficiency_gap=float(row["efficiency_gap"]),
                anomaly_score=float(row["anomaly_score"]),
                risk_score=float(row["risk_score"]),
                risk_level=str(row["risk_level"]),
                risk_reasons=row.get("risk_reasons", []),
                recommended_actions=row.get("recommended_actions", []),
                similar_project_id=str(row["similar_project_id"]) if pd.notnull(row["similar_project_id"]) else None,
                similarity_score=float(row["similarity_score"]),
                source="SYNTHETIC DEMO",
                source_file="synthetic_mplads_5000.csv",
                source_record_id=str(row["project_id"]),
                data_version="v1.0"
            )
            projects.append(p)
            
        db.bulk_save_objects(projects)
        db.commit()
        print(f"  + {len(projects):,} projects inserted.", flush=True)

        # B. Contractors Table
        contractor_objs = []
        for c in CONTRACTORS_LIST:
            c_projects = [p for p in projects if p.contractor_id == c["id"]]
            c_count = len(c_projects)
            c_total_val = sum(p.sanctioned_amount for p in c_projects)
            c_delayed = sum(1 for p in c_projects if p.delay_days >= 30)
            c_high_risk = sum(1 for p in c_projects if p.risk_score >= 60.0)
            c_avg_delay = (sum(p.delay_days for p in c_projects) / c_count) if c_count > 0 else 0.0
            c_avg_cost_dev = (sum(p.cost_deviation for p in c_projects) / c_count) if c_count > 0 else 0.0
            c_avg_risk = (sum(p.risk_score for p in c_projects) / c_count) if c_count > 0 else 0.0
            
            c_risk_level = "HIGH" if c_high_risk >= 5 or c_avg_risk >= 55 else ("MEDIUM" if c_high_risk >= 2 else "LOW")
            
            factors = []
            if c_delayed >= 10:
                factors.append({"factor": "High Delay Rate", "value": f"{c_delayed} delayed projects"})
            if c_high_risk >= 3:
                factors.append({"factor": "Elevated Risk Cluster", "value": f"{c_high_risk} high-risk projects"})
            if c_count >= 200:
                factors.append({"factor": "High Concentration", "value": f"{c_count} concurrent works"})

            contractor_objs.append(Contractor(
                id=c["id"],
                contractor_name=c["name"],
                registration_number=c["reg"],
                state="National",
                total_projects=c_count,
                total_contract_value=round(c_total_val, 2),
                average_project_value=round(c_total_val / c_count, 2) if c_count > 0 else 0.0,
                completed_projects=sum(1 for p in c_projects if p.status == "Completed"),
                delayed_projects=c_delayed,
                high_risk_projects=c_high_risk,
                average_delay_days=round(c_avg_delay, 1),
                average_cost_deviation=round(c_avg_cost_dev, 1),
                share_of_constituency_projects=round((c_count / count) * 100, 2),
                contractor_risk_score=round(c_avg_risk, 1),
                contractor_risk_level=c_risk_level,
                risk_factors=factors
            ))
            
        db.bulk_save_objects(contractor_objs)
        db.commit()
        print(f"  + {len(contractor_objs)} contractors seeded.", flush=True)

        # C. Constituencies Table
        constituency_names = set(p.constituency for p in projects)
        constituency_objs = []
        for cname in constituency_names:
            c_projs = [p for p in projects if p.constituency == cname]
            st = c_projs[0].state if c_projs else "Unknown"
            sanc_sum = sum(p.sanctioned_amount for p in c_projs)
            rel_sum = sum(p.released_amount for p in c_projs)
            util_sum = sum(p.utilized_amount for p in c_projs)
            c_comp = sum(1 for p in c_projs if p.status == "Completed")
            c_del = sum(1 for p in c_projs if p.delay_days >= 30)
            c_hr = sum(1 for p in c_projs if p.risk_score >= 60.0)
            avg_risk = sum(p.risk_score for p in c_projs) / len(c_projs) if c_projs else 0.0

            constituency_objs.append(Constituency(
                id=f"PC-{cname.upper().replace(' ', '_')[:20]}",
                name=cname,
                state=st,
                mp_name=f"Hon. Member of Parliament ({cname})",
                mp_house="Lok Sabha",
                term="17th Lok Sabha",
                total_projects=len(c_projs),
                total_sanctioned_amount=round(sanc_sum, 2),
                total_released_amount=round(rel_sum, 2),
                total_utilized_amount=round(util_sum, 2),
                utilization_rate=round((util_sum / sanc_sum * 100), 1) if sanc_sum > 0 else 0.0,
                completion_rate=round((c_comp / len(c_projs) * 100), 1) if c_projs else 0.0,
                delay_rate=round((c_del / len(c_projs) * 100), 1) if c_projs else 0.0,
                completed_projects=c_comp,
                delayed_projects=c_del,
                high_risk_projects=c_hr,
                average_risk_score=round(avg_risk, 1),
                average_cost_deviation=round(sum(p.cost_deviation for p in c_projs) / len(c_projs), 1) if c_projs else 0.0
            ))

        db.bulk_save_objects(constituency_objs)
        db.commit()
        print(f"  + {len(constituency_objs)} parliamentary constituencies seeded.", flush=True)

        # D. Alerts Table (Top high risk projects)
        high_risk_projects = [p for p in projects if p.risk_score >= 60.0]
        high_risk_projects.sort(key=lambda x: x.risk_score, reverse=True)
        
        alerts = []
        for idx, hp in enumerate(high_risk_projects[:150]):
            top_reason = hp.risk_reasons[0]["factor"] if hp.risk_reasons else "Potential Implementation Risk"
            severity = "CRITICAL" if hp.risk_score >= 80 else "HIGH"
            
            # Simulated investigation status
            if idx % 5 == 0:
                st = "UNDER REVIEW"
                officer = "Shri R. K. Sharma (Superintending Engineer)"
                notes = "DPR requested from DRDA executive officer for verification of civil item rates."
            elif idx % 7 == 0:
                st = "FIELD VERIFICATION"
                officer = "Smt. Priya Nair (District Quality Monitor)"
                notes = "Physical site inspection scheduled for verification of foundation and structural work."
            elif idx % 11 == 0:
                st = "RESOLVED"
                officer = "Shri V. Anand (District Planning Officer)"
                notes = "Contractor clarified geo-tagging delay; measurement book reconciled."
            else:
                st = "NEW"
                officer = None
                notes = None

            alerts.append(Alert(
                id=f"ALT-{idx+1:04d}",
                project_id=hp.id,
                project_name=hp.project_name,
                state=hp.state,
                district=hp.district,
                constituency=hp.constituency,
                alert_type=top_reason,
                risk_score=hp.risk_score,
                severity=severity,
                reason=f"{top_reason}: Flagged by AI Sentinel risk detection engine with composite score of {hp.risk_score:.1f}/100.",
                status=st,
                assigned_officer=officer,
                investigation_notes=notes,
                detected_date=datetime.datetime.now() - datetime.timedelta(days=idx % 30)
            ))

        db.bulk_save_objects(alerts)
        db.commit()
        print(f"  + {len(alerts)} alerts generated and loaded into investigation workflow.", flush=True)

        # E. Model Run Metadata
        m_run = ModelRun(
            id="RUN-INIT-001",
            run_timestamp=datetime.datetime.now(),
            model_type="Isolation Forest + TF-IDF NLP + Rule Risk Engine",
            training_records=count,
            anomalies_detected=len(high_risk_projects),
            high_risk_detected=len(high_risk_projects),
            cost_anomalies=int((final_df["cost_deviation"] >= 50.0).sum()),
            delay_anomalies=int((final_df["delay_days"] >= 60).sum()),
            efficiency_anomalies=int((final_df["efficiency_gap"] >= 35.0).sum()),
            duplicate_anomalies=int((final_df["similarity_score"] >= 80.0).sum()),
            parameters={"contamination": 0.08, "random_state": 42, "nlp_threshold": 0.82},
            metrics={"quality_score": val_report["data_quality_score"], "high_risk_count": len(high_risk_projects)},
            status="COMPLETED"
        )
        db.add(m_run)

        # F. Initial Audit Log
        db.add(AuditLog(
            id="AUD-0001",
            timestamp=datetime.datetime.now(),
            user="System Administrator",
            action="DATABASE_INITIALIZED",
            entity="Database",
            entity_id="mplad_sentinel.db",
            new_value=f"Seeded {count:,} projects, {len(alerts)} alerts, and initialized AI models."
        ))

        db.commit()
        print("\n========================================================", flush=True)
        print("   MPLAD AI SENTINEL DATABASE SEEDING COMPLETE!", flush=True)
        print(f"   * Total Projects: {count:,}", flush=True)
        print(f"   * High-Risk Projects Flagged: {len(high_risk_projects):,}", flush=True)
        print(f"   * Active Investigation Alerts: {len(alerts):,}", flush=True)
        print(f"   * Data Quality Score: {val_report['data_quality_score']}/100", flush=True)
        print("========================================================\n", flush=True)

    except Exception as e:
        db.rollback()
        print(f"[-] Error during database seeding: {e}", flush=True)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(count=5000)
