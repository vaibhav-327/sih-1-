from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AlertBase(BaseModel):
    project_id: str
    project_name: str
    state: str
    district: str
    constituency: str
    alert_type: str
    risk_score: float
    severity: str
    reason: str
    evidence: Optional[Dict[str, Any]] = {}
    status: Optional[str] = "NEW"
    assigned_officer: Optional[str] = None
    investigation_notes: Optional[str] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_officer: Optional[str] = None
    investigation_notes: Optional[str] = None
    resolution_summary: Optional[str] = None

class AlertResponse(AlertBase):
    id: str
    detected_date: Optional[datetime] = None
    resolution_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    total: int
    alerts: List[AlertResponse]
    summary_by_status: Dict[str, int]
    summary_by_severity: Dict[str, int]
