from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from backend.database import get_db
from backend.models.constituency import Constituency
from backend.models.project import Project
from backend.schemas.constituency import ConstituencyResponse, ConstituencyListResponse

router = APIRouter(prefix="/api/constituencies", tags=["Constituencies"])

@router.get("", response_model=ConstituencyListResponse)
def list_constituencies(
    state: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "average_risk_score",
    sort_dir: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Constituency)
    
    if state and state.strip() and state.lower() != "all":
        query = query.filter(Constituency.state == state.strip())
        
    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter(
            Constituency.name.ilike(s) | Constituency.mp_name.ilike(s) | Constituency.state.ilike(s)
        )

    sort_col = getattr(Constituency, sort_by, Constituency.average_risk_score)
    if sort_dir.lower() == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    constituencies = query.all()
    return ConstituencyListResponse(
        total=len(constituencies),
        constituencies=constituencies
    )

@router.get("/{constituency_id}", response_model=ConstituencyResponse)
def get_constituency_detail(constituency_id: str, db: Session = Depends(get_db)):
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    if not constituency:
        raise HTTPException(status_code=404, detail=f"Constituency '{constituency_id}' not found")
    return constituency

@router.get("/{constituency_id}/projects")
def get_constituency_projects(constituency_id: str, db: Session = Depends(get_db)):
    constituency = db.query(Constituency).filter(Constituency.id == constituency_id).first()
    if not constituency:
        raise HTTPException(status_code=404, detail=f"Constituency '{constituency_id}' not found")
    projects = db.query(Project).filter(Project.constituency == constituency.name).order_by(desc(Project.risk_score)).all()
    return {"constituency_id": constituency_id, "name": constituency.name, "total_projects": len(projects), "projects": projects}
