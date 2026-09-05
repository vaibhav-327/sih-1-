from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Optional, List, Dict, Any
from backend.database import get_db
from backend.models.project import Project
from backend.models.transaction import Transaction, Milestone
from backend.schemas.project import (
    ProjectResponse, ProjectListResponse, ProjectRiskExplainability,
    RiskFactor, RiskContributionItem
)

router = APIRouter(prefix="/api/projects", tags=["Projects"])

def calculate_risk_contributions(project: Project) -> List[RiskContributionItem]:
    """
    Computes a deterministic, transparent breakdown of how different anomaly
    vectors contribute to this project's overall risk score (sums to ~100%).
    """
    eff_gap = max(0.0, float(project.efficiency_gap or 0.0))
    cost_dev = max(0.0, float(project.cost_deviation or 0.0))
    delay = max(0, int(project.delay_days or 0))
    anomaly = max(0.0, float(project.anomaly_score or 0.0))
    sim = max(0.0, float(project.similarity_score or 0.0))
    
    # Raw points contribution modeling
    p_progress = min(35.0, eff_gap * 0.5) if eff_gap >= 20.0 else 0.0
    p_cost = min(30.0, cost_dev * 0.35) if cost_dev >= 30.0 else 0.0
    p_delay = min(25.0, (delay / 180.0) * 20.0) if delay >= 20 else 0.0
    p_ml = min(20.0, anomaly * 0.2) if anomaly >= 40.0 else 0.0
    p_nlp = min(20.0, sim * 0.2) if sim >= 65.0 else 0.0
    p_base = 5.0 # Base compliance factor

    total_raw = p_progress + p_cost + p_delay + p_ml + p_nlp + p_base
    if total_raw <= 0:
        total_raw = 1.0

    contributions = [
        RiskContributionItem(
            name="Progress Gap (Financial >> Physical)",
            percentage=round((p_progress / total_raw) * 100, 1),
            raw_points=round(p_progress, 1),
            severity="CRITICAL" if p_progress >= 20 else ("HIGH" if p_progress >= 10 else "LOW"),
            description=f"Efficiency gap of {eff_gap:.1f}% between financial release and verified physical execution."
        ),
        RiskContributionItem(
            name="Cost Deviation vs Regional Median",
            percentage=round((p_cost / total_raw) * 100, 1),
            raw_points=round(p_cost, 1),
            severity="HIGH" if p_cost >= 15 else ("MEDIUM" if p_cost >= 8 else "LOW"),
            description=f"Sanctioned outlay is {cost_dev:.1f}% above statistical cohort baseline."
        ),
        RiskContributionItem(
            name="Implementation Schedule Overrun",
            percentage=round((p_delay / total_raw) * 100, 1),
            raw_points=round(p_delay, 1),
            severity="HIGH" if p_delay >= 12 else ("MEDIUM" if p_delay >= 6 else "LOW"),
            description=f"Timeline delayed by {delay} days beyond expected completion milestone."
        ),
        RiskContributionItem(
            name="Isolation Forest Multivariate Pattern",
            percentage=round((p_ml / total_raw) * 100, 1),
            raw_points=round(p_ml, 1),
            severity="HIGH" if p_ml >= 12 else ("MEDIUM" if p_ml >= 6 else "LOW"),
            description=f"Unsupervised ML pattern anomaly score of {anomaly:.1f}/100 across agency vectors."
        ),
        RiskContributionItem(
            name="NLP Duplicate / Similar Description",
            percentage=round((p_nlp / total_raw) * 100, 1),
            raw_points=round(p_nlp, 1),
            severity="HIGH" if p_nlp >= 12 else ("MEDIUM" if p_nlp >= 6 else "LOW"),
            description=f"Text similarity index of {sim:.1f}% with nearby sanctioned project scope."
        ),
    ]

    # Filter out near zero items if total has significant flags, or adjust to 100%
    active_contributions = [c for c in contributions if c.percentage > 0]
    if not active_contributions:
        return [
            RiskContributionItem(
                name="Baseline Compliance Index",
                percentage=100.0,
                raw_points=5.0,
                severity="LOW",
                description="Project metrics align with standard operational parameters."
            )
        ]
    
    # Normalize percentages to exactly sum to 100%
    sum_pct = sum(c.percentage for c in active_contributions)
    if sum_pct > 0:
        for c in active_contributions:
            c.percentage = round((c.percentage / sum_pct) * 100, 1)

    return active_contributions

@router.get("", response_model=ProjectListResponse)
def list_projects(
    state: Optional[str] = None,
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    project_type: Optional[str] = None,
    risk: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    contractor: Optional[str] = None,
    filter: Optional[str] = None, # progress_gap, cost_deviation, delayed, duplicate, contractor_concentration, critical, high_risk
    search: Optional[str] = None,
    sort_by: Optional[str] = "risk_score",
    sort_dir: Optional[str] = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Project)

    # Dimensional Filtering
    if state and state.strip() and state.lower() != "all":
        query = query.filter(Project.state == state.strip())
    if district and district.strip() and district.lower() != "all":
        query = query.filter(Project.district == district.strip())
    if constituency and constituency.strip() and constituency.lower() != "all":
        query = query.filter(Project.constituency == constituency.strip())
    if project_type and project_type.strip() and project_type.lower() != "all":
        query = query.filter(Project.project_type == project_type.strip())
    
    # Handle risk/risk_level filter
    r_filter = risk_level or risk
    if r_filter and r_filter.strip() and r_filter.lower() != "all":
        query = query.filter(Project.risk_level == r_filter.strip().upper())

    if status and status.strip() and status.lower() != "all":
        query = query.filter(Project.status == status.strip())
    if contractor and contractor.strip():
        query = query.filter(
            or_(
                Project.contractor_name.ilike(f"%{contractor.strip()}%"),
                Project.contractor_id == contractor.strip()
            )
        )

    # Special Quick-Action Category Filters
    if filter and filter.strip():
        f = filter.strip().lower()
        if f in ("progress_gap", "efficiency_gap"):
            query = query.filter(Project.efficiency_gap >= 25.0)
        elif f in ("cost_deviation", "cost_anomaly", "cost"):
            query = query.filter(Project.cost_deviation >= 40.0)
        elif f in ("delayed", "delay"):
            query = query.filter(Project.delay_days >= 30)
        elif f in ("duplicate", "similarity", "nlp"):
            query = query.filter(Project.similarity_score >= 75.0)
        elif f in ("contractor_concentration", "contractor_risk"):
            query = query.filter(or_(Project.risk_score >= 70.0, Project.anomaly_score >= 65.0))
        elif f == "critical":
            query = query.filter(Project.risk_score >= 80.0)
        elif f == "high_risk":
            query = query.filter(Project.risk_score >= 60.0)

    # Full text search
    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Project.id.ilike(s),
                Project.project_name.ilike(s),
                Project.district.ilike(s),
                Project.constituency.ilike(s),
                Project.contractor_name.ilike(s)
            )
        )

    # Sorting
    sort_column = getattr(Project, sort_by, Project.risk_score)
    if sort_dir.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    projects = query.offset(offset).limit(page_size).all()

    return ProjectListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        projects=projects
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_detail(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return project

@router.get("/{project_id}/risk", response_model=ProjectRiskExplainability)
def get_project_risk_explainability(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    factors = []
    if project.risk_reasons and isinstance(project.risk_reasons, list):
        for r in project.risk_reasons:
            if isinstance(r, dict):
                factors.append(RiskFactor(
                    factor=r.get("factor", "Anomaly Indicator"),
                    impact=r.get("impact", "MEDIUM"),
                    value=str(r.get("value", "")),
                    score_contribution=float(r.get("score_contribution", 0.0)),
                    description=r.get("description", "")
                ))

    # Answers to 4 key questions
    where = {
        "state": project.state,
        "district": project.district,
        "constituency": project.constituency,
        "latitude": project.latitude,
        "longitude": project.longitude,
        "implementing_agency": project.implementing_agency
    }
    what = f"Flagged with {project.risk_level} Risk Level ({project.risk_score:.1f}/100) across {len(factors)} active detection vectors."
    why = [f"{f.factor} ({f.impact} impact): {f.value}" for f in factors] if factors else ["All implementation metrics align with standard norms."]
    next_action = project.recommended_actions[0] if (project.recommended_actions and len(project.recommended_actions) > 0) else "Conduct routine progress inspection as per MPLADS guidelines."

    contributions = calculate_risk_contributions(project)

    return ProjectRiskExplainability(
        project_id=project.id,
        project_name=project.project_name,
        risk_score=project.risk_score,
        risk_level=project.risk_level,
        anomaly_score=project.anomaly_score or 0.0,
        cost_deviation=project.cost_deviation or 0.0,
        delay_days=project.delay_days or 0,
        efficiency_gap=project.efficiency_gap or 0.0,
        similarity_score=project.similarity_score or 0.0,
        similar_project_id=project.similar_project_id,
        factors=factors,
        risk_contributions=contributions,
        recommended_actions=project.recommended_actions or [next_action],
        where=where,
        what=what,
        why=why,
        next_action=next_action
    )

@router.get("/{project_id}/risk-contributions")
def get_project_risk_contributions(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    contributions = calculate_risk_contributions(project)
    return {
        "project_id": project.id,
        "risk_score": project.risk_score,
        "risk_level": project.risk_level,
        "contributions": contributions
    }

@router.get("/{project_id}/risk-explanation")
def get_project_risk_explanation_alias(project_id: str, db: Session = Depends(get_db)):
    return get_project_risk_explainability(project_id, db)
