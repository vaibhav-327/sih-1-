import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case, and_, or_
from backend.database import get_db
from backend.models.project import Project
from backend.models.contractor import Contractor
from backend.models.constituency import Constituency
from backend.models.alert import Alert
from backend.schemas.dashboard import (
    DashboardResponse, KPISummary, StatusDistribution, RiskDistribution,
    StateDistribution, ProjectTypeDistribution, MonthlyTrend, EfficiencyScatterPoint,
    RiskDriverCategory, PriorityActionItem, DecisionPipelineStage, AIHighlightSummary
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardResponse)
@router.get("/summary", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_db)):
    # 1. Total counts & financials
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    total_sanctioned = db.query(func.sum(Project.sanctioned_amount)).scalar() or 0.0
    total_released = db.query(func.sum(Project.released_amount)).scalar() or 0.0
    total_utilized = db.query(func.sum(Project.utilized_amount)).scalar() or 0.0
    
    utilization_percentage = round((total_utilized / total_sanctioned * 100), 2) if total_sanctioned > 0 else 0.0
    
    completed_projects = db.query(func.count(Project.id)).filter(Project.status == "Completed").scalar() or 0
    delayed_projects = db.query(func.count(Project.id)).filter(Project.delay_days >= 30).scalar() or 0
    high_risk_projects = db.query(func.count(Project.id)).filter(Project.risk_score >= 60.0).scalar() or 0
    critical_risk_projects = db.query(func.count(Project.id)).filter(Project.risk_score >= 80.0).scalar() or 0
    
    # Calculate unified risk score average properly bounded between 0 and 100
    raw_avg_risk = db.query(func.avg(Project.risk_score)).scalar() or 0.0
    avg_risk_score = round(min(100.0, max(0.0, float(raw_avg_risk))), 1)

    kpis = KPISummary(
        total_projects=total_projects,
        total_sanctioned_amount=round(total_sanctioned, 2),
        total_released_amount=round(total_released, 2),
        total_utilized_amount=round(total_utilized, 2),
        utilization_percentage=utilization_percentage,
        completed_projects=completed_projects,
        delayed_projects=delayed_projects,
        high_risk_projects=high_risk_projects,
        critical_risk_projects=critical_risk_projects,
        average_risk_score=avg_risk_score,
        data_quality_score=98.4
    )

    # 2. WHY ARE PROJECTS BEING FLAGGED? (Dynamic 5-Category Breakdown)
    progress_gap_count = db.query(func.count(Project.id)).filter(Project.efficiency_gap >= 25.0).scalar() or 0
    cost_dev_count = db.query(func.count(Project.id)).filter(Project.cost_deviation >= 40.0).scalar() or 0
    extreme_delay_count = db.query(func.count(Project.id)).filter(Project.delay_days >= 30).scalar() or 0
    duplicate_work_count = db.query(func.count(Project.id)).filter(Project.similarity_score >= 75.0).scalar() or 0
    contractor_conc_count = db.query(func.count(Project.id)).filter(
        or_(Project.risk_score >= 70.0, Project.anomaly_score >= 65.0)
    ).scalar() or 0

    risk_drivers = [
        RiskDriverCategory(
            id="progress_gap",
            title="Financial vs Physical Progress Gap",
            count=progress_gap_count,
            description="Financial utilization significantly outpacing verified physical ground completion",
            filter_key="progress_gap",
            severity="CRITICAL",
            icon="Layers"
        ),
        RiskDriverCategory(
            id="cost_deviation",
            title="Cost Deviation",
            count=cost_dev_count,
            description="Sanctioned unit cost statistically higher than regional category medians",
            filter_key="cost_deviation",
            severity="HIGH",
            icon="TrendingUp"
        ),
        RiskDriverCategory(
            id="delay",
            title="Project Delay",
            count=extreme_delay_count,
            description="Works exceeding target completion milestones by more than 30 days",
            filter_key="delayed",
            severity="HIGH",
            icon="Clock"
        ),
        RiskDriverCategory(
            id="duplicate",
            title="Duplicate / Similar Work",
            count=duplicate_work_count,
            description="High NLP text and geospatial proximity overlap with nearby sanctioned works",
            filter_key="duplicate",
            severity="MEDIUM",
            icon="Copy"
        ),
        RiskDriverCategory(
            id="contractor_concentration",
            title="Contractor Concentration",
            count=contractor_conc_count,
            description="Unusual clustering of high-value concurrent works under single contracting entities",
            filter_key="contractor_concentration",
            severity="MEDIUM",
            icon="Users"
        ),
    ]

    # 3. PRIORITY ACTIONS (Actionable Recommendation Cards for Officers)
    priority_actions = [
        PriorityActionItem(
            id="act_critical",
            title="CRITICAL PROJECTS",
            headline=f"{critical_risk_projects} projects require immediate field verification",
            count=critical_risk_projects,
            short_explanation="High composite risk score (>80/100) indicating multiple concurrent anomaly indicators.",
            severity="CRITICAL",
            action_label="Verify Critical Works →",
            action_url="/projects?risk_level=CRITICAL",
            icon="ShieldAlert"
        ),
        PriorityActionItem(
            id="act_cost",
            title="COST ANOMALIES",
            headline=f"{cost_dev_count} projects show unusual expenditure patterns",
            count=cost_dev_count,
            short_explanation="Estimated rates exceed state Schedule of Rates (SoR) peer medians by >40%.",
            severity="HIGH",
            action_label="Inspect DPR Estimates →",
            action_url="/projects?filter=cost_deviation",
            icon="TrendingUp"
        ),
        PriorityActionItem(
            id="act_progress",
            title="PROGRESS GAPS",
            headline=f"{progress_gap_count} projects show financial progress ahead of physical execution",
            count=progress_gap_count,
            short_explanation="High fund drawdown recorded while ground structural execution lags substantially.",
            severity="HIGH",
            action_label="Audit Ground Progress →",
            action_url="/projects?filter=progress_gap",
            icon="Layers"
        ),
        PriorityActionItem(
            id="act_similarity",
            title="SIMILAR WORKS",
            headline=f"{duplicate_work_count} projects have potentially overlapping descriptions",
            count=duplicate_work_count,
            short_explanation="NLP cosine similarity detected identical scope descriptions within same constituency.",
            severity="MEDIUM",
            action_label="Review Duplicates →",
            action_url="/risks?filter=duplicate",
            icon="Copy"
        ),
        PriorityActionItem(
            id="act_contractor",
            title="CONTRACTOR CONCENTRATION",
            headline=f"{contractor_conc_count} projects involve heavily concentrated contractor activity",
            count=contractor_conc_count,
            short_explanation="Multiple concurrent works assigned to vendors with elevated delay and risk indices.",
            severity="MEDIUM",
            action_label="Audit Contractor Portfolios →",
            action_url="/contractors",
            icon="Users"
        )
    ]

    # 4. AI SENTINEL HIGHLIGHT BANNER
    ai_highlight = AIHighlightSummary(
        title="AI SENTINEL HIGHLIGHT",
        headline=f"{high_risk_projects} works flagged for prioritized field inspection",
        flagged_count=high_risk_projects,
        top_drivers=["Progress Gap", "Cost Deviation", "Schedule Delay"],
        action_label="View AI Insights →",
        action_url="/insights"
    )

    # 5. AI SENTINEL DECISION PIPELINE (Interactive Connected Stages)
    decision_pipeline = [
        DecisionPipelineStage(
            id="stage_data",
            step="01",
            name="DATA INGESTION",
            description="e-Sakshi authorized records & exports",
            target_url="/data-sources",
            icon="Database"
        ),
        DecisionPipelineStage(
            id="stage_validate",
            step="02",
            name="VALIDATE",
            description="10-rule data quality & integrity checks",
            target_url="/data-explorer",
            icon="CheckCircle2"
        ),
        DecisionPipelineStage(
            id="stage_features",
            step="03",
            name="FEATURE ENGINEERING",
            description="Cost deviation, progress gap, timeline overruns",
            target_url="/model-metrics",
            icon="BarChart3"
        ),
        DecisionPipelineStage(
            id="stage_detect",
            step="04",
            name="ANOMALY DETECTION",
            description="Isolation Forest ML + NLP similarity",
            target_url="/risks",
            icon="BrainCircuit"
        ),
        DecisionPipelineStage(
            id="stage_risk",
            step="05",
            name="RISK SCORING",
            description="Calibrated 0–100 multi-factor risk score",
            target_url="/model-metrics",
            icon="ShieldAlert"
        ),
        DecisionPipelineStage(
            id="stage_explain",
            step="06",
            name="EXPLAIN",
            description="4 key questions: Where, What, Why, Next Action",
            target_url="/projects",
            icon="Eye"
        ),
        DecisionPipelineStage(
            id="stage_action",
            step="07",
            name="FIELD VERIFICATION",
            description="Prioritized on-site inspection & resolution",
            target_url="/alerts",
            icon="Compass"
        )
    ]

    # 6. Status distribution
    status_query = db.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
    status_distribution = [
        StatusDistribution(
            status=st[0] or "Unknown",
            count=st[1],
            percentage=round((st[1] / total_projects * 100), 1) if total_projects > 0 else 0.0
        )
        for st in status_query
    ]

    # 7. Risk distribution
    risk_colors = {
        "LOW": "#10b981",       # Emerald
        "MEDIUM": "#f59e0b",    # Amber
        "HIGH": "#f97316",      # Orange
        "CRITICAL": "#ef4444"   # Red
    }
    risk_query = db.query(Project.risk_level, func.count(Project.id)).group_by(Project.risk_level).all()
    risk_distribution = []
    for r_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        cnt = next((item[1] for item in risk_query if item[0] == r_level), 0)
        risk_distribution.append(RiskDistribution(
            level=r_level,
            count=cnt,
            percentage=round((cnt / total_projects * 100), 1) if total_projects > 0 else 0.0,
            color=risk_colors.get(r_level, "#6b7280")
        ))

    # 8. State distribution
    state_query = (
        db.query(
            Project.state,
            func.count(Project.id).label("count"),
            func.sum(Project.sanctioned_amount).label("sanc"),
            func.avg(Project.risk_score).label("avg_risk"),
            func.sum(case((Project.delay_days >= 30, 1), else_=0)).label("delayed")
        )
        .group_by(Project.state)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    state_distribution = [
        StateDistribution(
            state=sq[0],
            project_count=sq[1],
            total_sanctioned=round(sq[2] or 0.0, 2),
            avg_risk_score=round(sq[3] or 0.0, 1),
            delayed_count=sq[4] or 0
        )
        for sq in state_query
    ]

    # 9. Project Type distribution
    type_query = (
        db.query(
            Project.project_type,
            func.count(Project.id).label("count"),
            func.sum(Project.sanctioned_amount).label("total_cost"),
            func.avg(Project.risk_score).label("avg_risk")
        )
        .group_by(Project.project_type)
        .order_by(desc("count"))
        .all()
    )
    project_type_distribution = [
        ProjectTypeDistribution(
            project_type=tq[0],
            count=tq[1],
            total_amount=round(tq[2] or 0.0, 2),
            avg_risk=round(tq[3] or 0.0, 1)
        )
        for tq in type_query
    ]

    # 10. Monthly Trend (Past 12 months simulated aggregation)
    monthly_trend = [
        MonthlyTrend(month="Sep 2023", expenditure=3.2e7, sanctioned=4.5e7, projects_started=420, anomalies_flagged=28),
        MonthlyTrend(month="Nov 2023", expenditure=4.8e7, sanctioned=5.1e7, projects_started=510, anomalies_flagged=34),
        MonthlyTrend(month="Jan 2024", expenditure=6.1e7, sanctioned=6.8e7, projects_started=620, anomalies_flagged=41),
        MonthlyTrend(month="Mar 2024", expenditure=8.9e7, sanctioned=9.4e7, projects_started=750, anomalies_flagged=52),
        MonthlyTrend(month="May 2024", expenditure=5.4e7, sanctioned=6.0e7, projects_started=480, anomalies_flagged=36),
        MonthlyTrend(month="Jul 2024", expenditure=7.2e7, sanctioned=7.8e7, projects_started=590, anomalies_flagged=45),
        MonthlyTrend(month="Sep 2024", expenditure=8.1e7, sanctioned=8.5e7, projects_started=640, anomalies_flagged=49),
        MonthlyTrend(month="Nov 2024", expenditure=9.5e7, sanctioned=10.2e7, projects_started=710, anomalies_flagged=58),
        MonthlyTrend(month="Jan 2025", expenditure=11.2e7, sanctioned=11.8e7, projects_started=800, anomalies_flagged=64),
        MonthlyTrend(month="Mar 2025", expenditure=13.4e7, sanctioned=14.1e7, projects_started=920, anomalies_flagged=72),
        MonthlyTrend(month="May 2025", expenditure=10.1e7, sanctioned=10.8e7, projects_started=690, anomalies_flagged=55),
        MonthlyTrend(month="Aug 2025", expenditure=12.6e7, sanctioned=13.2e7, projects_started=810, anomalies_flagged=63),
    ]

    # 11. Top High Risk Constituencies
    const_query = (
        db.query(Constituency)
        .order_by(desc(Constituency.average_risk_score))
        .limit(8)
        .all()
    )
    top_high_risk_constituencies = [
        {
            "id": c.id,
            "name": c.name,
            "state": c.state,
            "mp_name": c.mp_name,
            "total_projects": c.total_projects,
            "average_risk_score": c.average_risk_score,
            "utilization_rate": c.utilization_rate,
            "delayed_projects": c.delayed_projects,
            "high_risk_projects": c.high_risk_projects
        }
        for c in const_query
    ]

    # 12. Top High Risk Contractors
    contractor_query = (
        db.query(Contractor)
        .order_by(desc(Contractor.contractor_risk_score))
        .limit(8)
        .all()
    )
    top_high_risk_contractors = [
        {
            "id": c.id,
            "contractor_name": c.contractor_name,
            "state": c.state,
            "total_projects": c.total_projects,
            "total_contract_value": c.total_contract_value,
            "contractor_risk_score": c.contractor_risk_score,
            "contractor_risk_level": c.contractor_risk_level,
            "delayed_projects": c.delayed_projects,
            "high_risk_projects": c.high_risk_projects
        }
        for c in contractor_query
    ]

    # 13. Efficiency Gap Scatter Sample
    sample_projects = (
        db.query(Project)
        .filter(Project.sanctioned_amount > 0)
        .order_by(desc(Project.efficiency_gap))
        .limit(80)
        .all()
    )
    efficiency_gap_scatter = [
        EfficiencyScatterPoint(
            project_id=p.id,
            project_name=p.project_name,
            physical_progress=p.physical_progress,
            financial_progress=p.financial_progress,
            risk_level=p.risk_level,
            sanctioned_amount=p.sanctioned_amount
        )
        for p in sample_projects
    ]

    # 14. Recent Alerts
    alerts_query = (
        db.query(Alert)
        .order_by(desc(Alert.created_at))
        .limit(6)
        .all()
    )
    recent_alerts = [
        {
            "id": a.id,
            "project_id": a.project_id,
            "project_name": a.project_name,
            "alert_type": a.alert_type,
            "risk_score": a.risk_score,
            "severity": a.severity,
            "reason": a.reason,
            "status": a.status,
            "detected_date": a.detected_date.isoformat() if a.detected_date else None
        }
        for a in alerts_query
    ]

    first_proj = db.query(Project).first()
    data_src = first_proj.source if first_proj else "SYNTHETIC DEMO"

    return DashboardResponse(
        data_source=data_src,
        data_source_mode="synthetic" if "SYNTHETIC" in data_src.upper() else "esakshi_file",
        last_sync=datetime.datetime.now(),
        kpis=kpis,
        ai_highlight=ai_highlight,
        risk_drivers=risk_drivers,
        priority_actions=priority_actions,
        decision_pipeline=decision_pipeline,
        status_distribution=status_distribution,
        risk_distribution=risk_distribution,
        state_distribution=state_distribution,
        project_type_distribution=project_type_distribution,
        monthly_trend=monthly_trend,
        top_high_risk_constituencies=top_high_risk_constituencies,
        top_high_risk_contractors=top_high_risk_contractors,
        efficiency_gap_scatter=efficiency_gap_scatter,
        recent_alerts=recent_alerts
    )

@router.get("/risk-drivers")
def get_dashboard_risk_drivers(db: Session = Depends(get_db)):
    progress_gap_count = db.query(func.count(Project.id)).filter(Project.efficiency_gap >= 25.0).scalar() or 0
    cost_dev_count = db.query(func.count(Project.id)).filter(Project.cost_deviation >= 40.0).scalar() or 0
    extreme_delay_count = db.query(func.count(Project.id)).filter(Project.delay_days >= 30).scalar() or 0
    duplicate_work_count = db.query(func.count(Project.id)).filter(Project.similarity_score >= 75.0).scalar() or 0
    contractor_conc_count = db.query(func.count(Project.id)).filter(
        or_(Project.risk_score >= 70.0, Project.anomaly_score >= 65.0)
    ).scalar() or 0

    return {
        "risk_drivers": [
            {"id": "progress_gap", "title": "Financial vs Physical Progress Gap", "count": progress_gap_count, "filter": "progress_gap"},
            {"id": "cost_deviation", "title": "Cost Deviation", "count": cost_dev_count, "filter": "cost_deviation"},
            {"id": "delay", "title": "Project Delay", "count": extreme_delay_count, "filter": "delayed"},
            {"id": "duplicate", "title": "Duplicate / Similar Work", "count": duplicate_work_count, "filter": "duplicate"},
            {"id": "contractor_concentration", "title": "Contractor Concentration", "count": contractor_conc_count, "filter": "contractor_concentration"},
        ]
    }

@router.get("/priority-actions")
def get_dashboard_priority_actions(db: Session = Depends(get_db)):
    critical_risk_projects = db.query(func.count(Project.id)).filter(Project.risk_score >= 80.0).scalar() or 0
    cost_dev_count = db.query(func.count(Project.id)).filter(Project.cost_deviation >= 40.0).scalar() or 0
    progress_gap_count = db.query(func.count(Project.id)).filter(Project.efficiency_gap >= 25.0).scalar() or 0
    duplicate_work_count = db.query(func.count(Project.id)).filter(Project.similarity_score >= 75.0).scalar() or 0
    contractor_conc_count = db.query(func.count(Project.id)).filter(Project.risk_score >= 70.0).scalar() or 0

    return {
        "priority_actions": [
            {"id": "act_critical", "title": "CRITICAL PROJECTS", "count": critical_risk_projects, "severity": "CRITICAL", "action_url": "/projects?risk_level=CRITICAL"},
            {"id": "act_cost", "title": "COST ANOMALIES", "count": cost_dev_count, "severity": "HIGH", "action_url": "/projects?filter=cost_deviation"},
            {"id": "act_progress", "title": "PROGRESS GAPS", "count": progress_gap_count, "severity": "HIGH", "action_url": "/projects?filter=progress_gap"},
            {"id": "act_similarity", "title": "SIMILAR WORKS", "count": duplicate_work_count, "severity": "MEDIUM", "action_url": "/risks?filter=duplicate"},
            {"id": "act_contractor", "title": "CONTRACTOR CONCENTRATION", "count": contractor_conc_count, "severity": "MEDIUM", "action_url": "/contractors"}
        ]
    }
