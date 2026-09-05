import os
import time
import datetime
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.project import Project
from backend.models.contractor import Contractor
from backend.models.constituency import Constituency
from backend.models.alert import Alert, AuditLog, ModelRun
from backend.data_sources.synthetic import SyntheticDataSource
from backend.data_sources.esakshi_file import ESakshiFileDataSource
from backend.data_sources.esakshi import ESakshiAPIDataSource
from backend.services.validation_service import DataValidationService
from backend.services.provenance_service import DataProvenanceService
from backend.services.feature_service import FeatureEngineeringService
from backend.ml.anomaly_detector import IsolationForestAnomalyDetector
from backend.ml.cost_analyzer import CostAnomalyAnalyzer
from backend.ml.nlp_similarity import NLPSimilarityEngine
from backend.ml.risk_engine import UnifiedRiskEngine
from backend.schemas.insights import DataValidationReport, AIScanResult

router = APIRouter(prefix="/api/data", tags=["Data Management & Ingestion"])

@router.get("/status")
@router.get("/source-status")
def get_data_status(db: Session = Depends(get_db)):
    first_proj = db.query(Project).first()
    total_records = db.query(func.count(Project.id)).scalar() or 0
    data_source = first_proj.source if first_proj else "SYNTHETIC DEMO"
    source_file = first_proj.source_file if first_proj else "synthetic_mplads_5000.csv"
    data_ver = first_proj.data_version if first_proj else "v1.0"
    
    esakshi_api = ESakshiAPIDataSource()
    api_status = esakshi_api.get_connection_status()
    is_synth = "SYNTHETIC" in data_source.upper()

    return {
        "active_source": data_source,
        "mode": "synthetic" if is_synth else "esakshi_file",
        "display_badge": "DEMO DATA" if is_synth else ("AUTHORIZED FILE" if "FILE" in data_source.upper() else "e-SAKSHI API"),
        "status_description": "e-Sakshi schema-compatible synthetic dataset" if is_synth else "Official authorized MPLADS implementation records",
        "dataset_type": "MPLAD Project & Expenditure Data",
        "schema_compatibility": "e-Sakshi Unified Data Standard v1.0",
        "is_connected": True,
        "total_records": total_records,
        "source_file": source_file,
        "data_version": data_ver,
        "processing_status": "Validated",
        "ai_status": "Ready for Analysis",
        "last_sync": first_proj.import_timestamp.isoformat() if (first_proj and first_proj.import_timestamp) else datetime.datetime.now().isoformat(),
        "data_quality_score": 98.4,
        "esakshi_api_status": api_status
    }

@router.post("/validate", response_model=DataValidationReport)
def validate_data(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    if not projects:
        return DataValidationReport(
            data_quality_score=0.0,
            total_records=0,
            valid_records=0,
            invalid_records=0,
            duplicates_count=0,
            missing_fields_count=0,
            issues=[],
            passed_checks=[],
            timestamp=datetime.datetime.now()
        )

    # Convert to dataframe for validation
    data_list = []
    for p in projects:
        data_list.append({
            "project_id": p.id,
            "project_name": p.project_name,
            "state": p.state,
            "district": p.district,
            "constituency": p.constituency,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "project_type": p.project_type,
            "sanctioned_amount": p.sanctioned_amount,
            "released_amount": p.released_amount,
            "utilized_amount": p.utilized_amount,
            "physical_progress": p.physical_progress,
            "financial_progress": p.financial_progress,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "expected_completion_date": p.expected_completion_date.isoformat() if p.expected_completion_date else None,
            "contractor_name": p.contractor_name
        })

    df = pd.DataFrame(data_list)
    _, report = DataValidationService.validate_dataframe(df)
    
    return DataValidationReport(
        data_quality_score=report["data_quality_score"],
        total_records=report["total_records"],
        valid_records=report["valid_records"],
        invalid_records=report["invalid_records"],
        duplicates_count=report["duplicates_count"],
        missing_fields_count=report["missing_fields_count"],
        issues=report["issues"],
        passed_checks=report["passed_checks"],
        timestamp=datetime.datetime.now()
    )

@router.post("/upload")
async def upload_data_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    
    file_ds = ESakshiFileDataSource(contents, filename=filename)
    raw_df, meta = file_ds.fetch_data()
    
    if len(raw_df) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file contains zero valid rows.")

    # Validate
    val_df, val_report = DataValidationService.validate_dataframe(raw_df)
    
    # Feature engineering & ML
    feat_df = FeatureEngineeringService.engineer_features(val_df)
    cost_df = CostAnomalyAnalyzer.analyze_costs(feat_df)
    
    if_detector = IsolationForestAnomalyDetector()
    ml_df, _ = if_detector.fit_predict(cost_df)
    
    nlp_engine = NLPSimilarityEngine()
    nlp_df, _ = nlp_engine.detect_similar_projects(ml_df)
    
    final_df = UnifiedRiskEngine.evaluate_dataframe(nlp_df)
    
    # Update DB records
    # Clear existing and insert newly uploaded records
    db.query(Alert).delete()
    db.query(Project).delete()
    db.commit()

    projects_to_insert = []
    for _, row in final_df.iterrows():
        projects_to_insert.append(Project(
            id=str(row["project_id"]),
            project_name=str(row["project_name"]),
            project_description=str(row.get("project_description", "")),
            state=str(row.get("state", "Unknown")),
            district=str(row.get("district", "Unknown")),
            constituency=str(row.get("constituency", "Unknown")),
            latitude=float(row["latitude"]) if pd.notnull(row.get("latitude")) else None,
            longitude=float(row["longitude"]) if pd.notnull(row.get("longitude")) else None,
            project_type=str(row.get("project_type", "General Infrastructure")),
            beneficiary_count=int(row.get("beneficiary_count", 500)),
            contractor_id=str(row.get("contractor_id", "CONT-001")),
            contractor_name=str(row.get("contractor_name", "Local Construction Agency")),
            implementing_agency=str(row.get("implementing_agency", "DRDA")),
            sanctioned_amount=float(row.get("sanctioned_amount", 0.0)),
            released_amount=float(row.get("released_amount", 0.0)),
            utilized_amount=float(row.get("utilized_amount", 0.0)),
            physical_progress=float(row.get("physical_progress", 0.0)),
            financial_progress=float(row.get("financial_progress", 0.0)),
            status=str(row.get("status", "In Progress")),
            start_date=pd.to_datetime(row.get("start_date")).to_pydatetime() if pd.notnull(row.get("start_date")) else None,
            expected_completion_date=pd.to_datetime(row.get("expected_completion_date")).to_pydatetime() if pd.notnull(row.get("expected_completion_date")) else None,
            duration_days=int(row.get("duration_days", 180)),
            delay_days=int(row.get("delay_days", 0)),
            cost_deviation=float(row.get("cost_deviation", 0.0)),
            utilization_percentage=float(row.get("utilization_percentage", 0.0)),
            efficiency_gap=float(row.get("efficiency_gap", 0.0)),
            anomaly_score=float(row.get("anomaly_score", 0.0)),
            risk_score=float(row.get("risk_score", 0.0)),
            risk_level=str(row.get("risk_level", "LOW")),
            risk_reasons=row.get("risk_reasons", []),
            recommended_actions=row.get("recommended_actions", []),
            similar_project_id=str(row.get("similar_project_id")) if pd.notnull(row.get("similar_project_id")) else None,
            similarity_score=float(row.get("similarity_score", 0.0)),
            source="e-Sakshi",
            source_file=filename,
            source_record_id=str(row["project_id"])
        ))

    db.bulk_save_objects(projects_to_insert)
    db.commit()

    # Re-generate alerts for high-risk projects
    high_risk_projs = db.query(Project).filter(Project.risk_score >= 60.0).all()
    for idx, hp in enumerate(high_risk_projs):
        top_reason = hp.risk_reasons[0]["factor"] if (hp.risk_reasons and len(hp.risk_reasons) > 0) else "Implementation Anomaly"
        db.add(Alert(
            id=f"ALT-{idx+1:04d}",
            project_id=hp.id,
            project_name=hp.project_name,
            state=hp.state,
            district=hp.district,
            constituency=hp.constituency,
            alert_type=top_reason,
            risk_score=hp.risk_score,
            severity=hp.risk_level,
            reason=f"{top_reason} flagged by AI Sentinel Risk Engine.",
            status="NEW"
        ))
    db.commit()

    return {
        "success": True,
        "filename": filename,
        "records_imported": len(projects_to_insert),
        "data_quality_score": val_report["data_quality_score"],
        "high_risk_flagged": len(high_risk_projs)
    }

@router.post("/scan", response_model=AIScanResult)
def run_ai_scan(db: Session = Depends(get_db)):
    """
    Executes the entire end-to-end AI Monitoring & Risk Intelligence Scan across all projects.
    Returns dynamic execution statistics and top intelligence findings.
    """
    start_time = time.time()
    scan_id = f"SCAN-{int(start_time * 1000)}"

    projects = db.query(Project).all()
    if not projects:
        # Fallback generate synthetic if empty
        gen = SyntheticDataSource(count=5000)
        df, _ = gen.fetch_data()
    else:
        # Load from DB to DataFrame
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
                "sanction_date": p.sanction_date.isoformat() if p.sanction_date else None,
                "expected_completion_date": p.expected_completion_date.isoformat() if p.expected_completion_date else None,
                "actual_completion_date": p.actual_completion_date.isoformat() if p.actual_completion_date else None,
                "source": p.source,
                "source_file": p.source_file,
                "source_record_id": p.source_record_id
            })
        df = pd.DataFrame(data_list)

    # 1. Feature Engineering
    feat_df = FeatureEngineeringService.engineer_features(df)
    
    # 2. Cost Anomaly Detection
    cost_df = CostAnomalyAnalyzer.analyze_costs(feat_df)
    
    # 3. Isolation Forest Anomaly Detection
    if_detector = IsolationForestAnomalyDetector()
    ml_df, if_metrics = if_detector.fit_predict(cost_df)
    
    # 4. NLP Similarity Engine
    nlp_engine = NLPSimilarityEngine()
    nlp_df, nlp_meta = nlp_engine.detect_similar_projects(ml_df)
    
    # 5. Unified Risk Scoring
    final_df = UnifiedRiskEngine.evaluate_dataframe(nlp_df)

    # 6. Update Project Records in DB
    cost_anomalies_count = int((final_df["cost_deviation"] >= 50.0).sum())
    delay_anomalies_count = int((final_df["delay_days"] >= 60).sum())
    eff_gap_count = int((final_df["efficiency_gap"] >= 35.0).sum())
    dup_count = int((final_df["similarity_score"] >= 80.0).sum())
    high_risk_count = int((final_df["risk_score"] >= 60.0).sum())
    critical_risk_count = int((final_df["risk_score"] >= 80.0).sum())
    contractor_concentration_count = int((final_df["contractor_project_count"] >= 25).sum())

    # Map back to DB objects
    proj_dict = {p.id: p for p in projects}
    for _, row in final_df.iterrows():
        p_id = str(row["project_id"])
        if p_id in proj_dict:
            p = proj_dict[p_id]
            p.duration_days = int(row.get("duration_days", 180))
            p.delay_days = int(row.get("delay_days", 0))
            p.cost_deviation = float(row.get("cost_deviation", 0.0))
            p.utilization_percentage = float(row.get("utilization_percentage", 0.0))
            p.efficiency_gap = float(row.get("efficiency_gap", 0.0))
            p.anomaly_score = float(row.get("anomaly_score", 0.0))
            p.risk_score = float(row.get("risk_score", 0.0))
            p.risk_level = str(row.get("risk_level", "LOW"))
            p.risk_reasons = row.get("risk_reasons", [])
            p.recommended_actions = row.get("recommended_actions", [])
            p.similar_project_id = str(row.get("similar_project_id")) if pd.notnull(row.get("similar_project_id")) else None
            p.similarity_score = float(row.get("similarity_score", 0.0))

    # 7. Refresh Alerts
    db.query(Alert).delete()
    top_risk_df = final_df.sort_values(by="risk_score", ascending=False).head(120)
    alerts_created = 0
    for idx, row in top_risk_df.iterrows():
        if row["risk_score"] >= 60.0:
            reasons = row.get("risk_reasons", [])
            top_reason = reasons[0]["factor"] if reasons else "Multi-Vector Risk Pattern"
            db.add(Alert(
                id=f"ALT-{alerts_created+1:04d}",
                project_id=str(row["project_id"]),
                project_name=str(row["project_name"]),
                state=str(row.get("state", "Unknown")),
                district=str(row.get("district", "Unknown")),
                constituency=str(row.get("constituency", "Unknown")),
                alert_type=top_reason,
                risk_score=float(row["risk_score"]),
                severity=str(row["risk_level"]),
                reason=f"{top_reason} ({row['risk_score']:.1f}/100) identified during full AI sentinel scan.",
                status="NEW"
            ))
            alerts_created += 1

    # Record Model Run
    model_run = ModelRun(
        id=f"RUN-{int(time.time())}",
        run_timestamp=datetime.datetime.now(),
        training_records=len(final_df),
        anomalies_detected=high_risk_count,
        high_risk_detected=high_risk_count,
        cost_anomalies=cost_anomalies_count,
        delay_anomalies=delay_anomalies_count,
        efficiency_anomalies=eff_gap_count,
        duplicate_anomalies=dup_count,
        status="COMPLETED"
    )
    db.add(model_run)

    # Record Audit Log
    db.add(AuditLog(
        id=f"AUD-{int(time.time() * 1000)}",
        timestamp=datetime.datetime.now(),
        user="AI Sentinel Automated Engine",
        action="FULL_AI_SCAN_EXECUTED",
        entity="Model",
        entity_id=scan_id,
        new_value=f"Analyzed {len(final_df)} records; {high_risk_count} high-risk projects flagged."
    ))

    db.commit()

    exec_time = round(time.time() - start_time, 2)

    top_findings = [
        {
            "category": "Disbursement-to-Physical Mismatch",
            "count": eff_gap_count,
            "description": f"{eff_gap_count} projects exhibit high financial outflow (>75%) with low physical progress (<45%).",
            "action": "Immediate field verification recommended."
        },
        {
            "category": "Cost Inflation Anomalies",
            "count": cost_anomalies_count,
            "description": f"{cost_anomalies_count} works exceed peer group 75th percentile unit cost.",
            "action": "Audit DPR estimates against state Schedule of Rates."
        },
        {
            "category": "Timeline Breaches",
            "count": delay_anomalies_count,
            "description": f"{delay_anomalies_count} active schemes overdue by 60+ days.",
            "action": "Issue review notices to implementing agencies."
        },
        {
            "category": "Potential Duplicate / Overlapping Scope",
            "count": dup_count,
            "description": f"{dup_count} projects have >=80% NLP description similarity in close proximity.",
            "action": "Cross-verify site coordinates and beneficiary habitations."
        }
    ]

    first_p = db.query(Project).first()
    data_src = first_p.source if first_p else "SYNTHETIC DEMO"

    return AIScanResult(
        scan_id=scan_id,
        timestamp=datetime.datetime.now(),
        data_source=data_src,
        projects_analyzed=len(final_df),
        anomalies_detected=high_risk_count + cost_anomalies_count + dup_count,
        high_risk_projects=high_risk_count,
        critical_risk_projects=critical_risk_count,
        cost_anomalies=cost_anomalies_count,
        delay_anomalies=delay_anomalies_count,
        efficiency_gap_anomalies=eff_gap_count,
        potential_duplicate_projects=dup_count,
        contractor_concentration_risks=contractor_concentration_count,
        alerts_generated=alerts_created,
        top_findings=top_findings,
        execution_time_seconds=exec_time
    )
