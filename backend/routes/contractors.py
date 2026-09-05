from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List, Dict, Any
from backend.database import get_db
from backend.models.contractor import Contractor
from backend.models.project import Project
from backend.schemas.contractor import ContractorResponse, ContractorListResponse

router = APIRouter(prefix="/api/contractors", tags=["Contractors"])

@router.get("", response_model=ContractorListResponse)
def list_contractors(
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "contractor_risk_score",
    sort_dir: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Contractor)
    
    if risk_level and risk_level.strip() and risk_level.lower() != "all":
        query = query.filter(Contractor.contractor_risk_level == risk_level.strip().upper())
        
    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter(
            Contractor.contractor_name.ilike(s) | Contractor.id.ilike(s)
        )

    sort_col = getattr(Contractor, sort_by, Contractor.contractor_risk_score)
    if sort_dir.lower() == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    contractors = query.all()
    return ContractorListResponse(
        total=len(contractors),
        contractors=contractors
    )

@router.get("/network/graph")
def get_relationship_graph(limit: int = 35, db: Session = Depends(get_db)):
    """
    Generates node-link relationship graph structure connecting:
    Contractors <-> Projects <-> Constituencies.
    Nodes are sized by project counts and colored by risk intensity.
    """
    sample_projects = (
        db.query(Project)
        .order_by(desc(Project.risk_score))
        .limit(limit)
        .all()
    )

    nodes = []
    edges = []
    node_ids = set()

    for p in sample_projects:
        # Project Node
        p_node_id = f"proj_{p.id}"
        if p_node_id not in node_ids:
            nodes.append({
                "id": p_node_id,
                "label": p.project_name[:22] + "...",
                "fullName": p.project_name,
                "type": "project",
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "sanctioned_amount": p.sanctioned_amount,
                "state": p.state,
                "district": p.district,
                "constituency": p.constituency,
                "size": 18 + int(p.risk_score * 0.16)
            })
            node_ids.add(p_node_id)

        # Contractor Node
        c_name = p.contractor_name or "National Civil Enterprise"
        c_node_id = f"cont_{p.contractor_id or 'CONT-001'}"
        if c_node_id not in node_ids:
            # Query contractor stats
            c_rec = db.query(Contractor).filter(Contractor.id == p.contractor_id).first()
            c_score = c_rec.contractor_risk_score if c_rec else p.risk_score
            c_level = c_rec.contractor_risk_level if c_rec else p.risk_level
            c_total = c_rec.total_projects if c_rec else 15
            
            nodes.append({
                "id": c_node_id,
                "contractor_id": p.contractor_id,
                "label": c_name,
                "fullName": c_name,
                "type": "contractor",
                "risk_score": c_score,
                "risk_level": c_level,
                "total_projects": c_total,
                "size": 28 + min(20, int(c_total * 0.1))
            })
            node_ids.add(c_node_id)

        # Constituency Node
        const_node_id = f"const_{p.constituency}"
        if const_node_id not in node_ids:
            nodes.append({
                "id": const_node_id,
                "label": f"PC: {p.constituency}",
                "fullName": f"Constituency of {p.constituency}",
                "type": "constituency",
                "risk_score": 42,
                "state": p.state,
                "size": 24
            })
            node_ids.add(const_node_id)

        # Edges
        edges.append({
            "source": c_node_id,
            "target": p_node_id,
            "relation": "EXECUTED_BY",
            "is_high_risk": p.risk_score >= 60.0
        })
        edges.append({
            "source": p_node_id,
            "target": const_node_id,
            "relation": "LOCATED_IN",
            "is_high_risk": p.risk_score >= 60.0
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

@router.get("/{contractor_id}", response_model=ContractorResponse)
def get_contractor_detail(contractor_id: str, db: Session = Depends(get_db)):
    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail=f"Contractor '{contractor_id}' not found")
    return contractor

@router.get("/{contractor_id}/network")
def get_contractor_network_profile(contractor_id: str, db: Session = Depends(get_db)):
    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail=f"Contractor '{contractor_id}' not found")
    
    projects = db.query(Project).filter(Project.contractor_id == contractor_id).order_by(desc(Project.risk_score)).all()
    
    constituencies = list(set(p.constituency for p in projects))
    delayed = sum(1 for p in projects if p.delay_days >= 30)
    high_risk = sum(1 for p in projects if p.risk_score >= 60.0)
    total_val = sum(p.sanctioned_amount for p in projects)
    
    notable_reasons = []
    if len(projects) >= 10:
        notable_reasons.append(f"High concentration of concurrent works ({len(projects)} projects across schemes).")
    if high_risk >= 2:
        notable_reasons.append(f"Multiple works flagged with elevated risk indicators ({high_risk} high-risk projects).")
    if delayed >= 3:
        notable_reasons.append(f"Above-average timeline delay rate ({delayed} projects overdue by >30 days).")
    if len(constituencies) >= 2:
        notable_reasons.append(f"Active implementation across {len(constituencies)} distinct parliamentary constituencies.")
    
    if not notable_reasons:
        notable_reasons.append("Contractor metrics align within standard operational variance.")

    return {
        "contractor": contractor,
        "connected_projects_count": len(projects),
        "total_sanctioned_value": round(total_val, 2),
        "constituencies_count": len(constituencies),
        "constituencies": constituencies,
        "delayed_count": delayed,
        "high_risk_count": high_risk,
        "notable_reasons": notable_reasons,
        "top_projects": [
            {
                "id": p.id,
                "project_name": p.project_name,
                "sanctioned_amount": p.sanctioned_amount,
                "physical_progress": p.physical_progress,
                "financial_progress": p.financial_progress,
                "delay_days": p.delay_days,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "constituency": p.constituency
            }
            for p in projects[:15]
        ]
    }

@router.get("/{contractor_id}/projects")
def get_contractor_projects(contractor_id: str, db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.contractor_id == contractor_id).order_by(desc(Project.risk_score)).all()
    return {"contractor_id": contractor_id, "total_projects": len(projects), "projects": projects}
