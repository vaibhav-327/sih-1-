from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List, Dict, Any
from backend.database import get_db
from backend.models.project import Project

router = APIRouter(prefix="/api/map", tags=["Map Intelligence"])

@router.get("/projects")
def get_map_projects(
    state: Optional[str] = None,
    district: Optional[str] = None,
    project_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = Query(1000, ge=10, le=5000),
    db: Session = Depends(get_db)
):
    query = db.query(
        Project.id,
        Project.project_name,
        Project.state,
        Project.district,
        Project.constituency,
        Project.latitude,
        Project.longitude,
        Project.project_type,
        Project.sanctioned_amount,
        Project.utilized_amount,
        Project.physical_progress,
        Project.financial_progress,
        Project.risk_score,
        Project.risk_level,
        Project.status,
        Project.contractor_name,
        Project.delay_days
    ).filter(
        Project.latitude.isnot(None),
        Project.longitude.isnot(None)
    )

    if state and state.strip() and state.lower() != "all":
        query = query.filter(Project.state == state.strip())
    if district and district.strip() and district.lower() != "all":
        query = query.filter(Project.district == district.strip())
    if project_type and project_type.strip() and project_type.lower() != "all":
        query = query.filter(Project.project_type == project_type.strip())
    if risk_level and risk_level.strip() and risk_level.lower() != "all":
        query = query.filter(Project.risk_level == risk_level.strip().upper())

    projects = query.order_by(desc(Project.risk_score)).limit(limit).all()

    features = []
    for p in projects:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p.longitude, p.latitude]
            },
            "properties": {
                "id": p.id,
                "name": p.project_name,
                "state": p.state,
                "district": p.district,
                "constituency": p.constituency,
                "project_type": p.project_type,
                "sanctioned_amount": p.sanctioned_amount,
                "utilized_amount": p.utilized_amount,
                "physical_progress": p.physical_progress,
                "financial_progress": p.financial_progress,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "status": p.status,
                "contractor_name": p.contractor_name,
                "delay_days": p.delay_days
            }
        })

    return {
        "type": "FeatureCollection",
        "count": len(features),
        "features": features
    }
