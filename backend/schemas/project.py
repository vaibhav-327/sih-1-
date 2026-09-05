from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class RiskFactor(BaseModel):
    factor: str
    impact: str # LOW, MEDIUM, HIGH, CRITICAL
    value: str
    score_contribution: float
    description: str

class RiskContributionItem(BaseModel):
    name: str
    percentage: float # Percentage contribution to total risk (0-100)
    raw_points: float
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    description: str

class ProjectBase(BaseModel):
    project_name: str
    project_description: Optional[str] = None
    state: str
    district: str
    constituency: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    project_type: str
    beneficiary_count: Optional[int] = 0
    contractor_id: Optional[str] = None
    contractor_name: Optional[str] = None
    implementing_agency: Optional[str] = None
    sanctioned_amount: float
    released_amount: float
    utilized_amount: float
    physical_progress: float
    financial_progress: float
    status: Optional[str] = "In Progress"
    start_date: Optional[datetime] = None
    sanction_date: Optional[datetime] = None
    expected_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None

class ProjectResponse(ProjectBase):
    id: str
    duration_days: Optional[int] = 0
    delay_days: Optional[int] = 0
    cost_deviation: Optional[float] = 0.0
    utilization_percentage: Optional[float] = 0.0
    efficiency_gap: Optional[float] = 0.0
    anomaly_score: Optional[float] = 0.0
    risk_score: float
    risk_level: str
    risk_reasons: Optional[List[Dict[str, Any]]] = []
    recommended_actions: Optional[List[str]] = []
    similar_project_id: Optional[str] = None
    similarity_score: Optional[float] = 0.0
    source: str
    source_file: Optional[str] = None
    source_record_id: Optional[str] = None
    import_timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectRiskExplainability(BaseModel):
    project_id: str
    project_name: str
    risk_score: float
    risk_level: str
    anomaly_score: float
    cost_deviation: float
    delay_days: int
    efficiency_gap: float
    similarity_score: float
    similar_project_id: Optional[str] = None
    factors: List[RiskFactor]
    risk_contributions: Optional[List[RiskContributionItem]] = []
    recommended_actions: List[str]
    where: Dict[str, Any]
    what: str
    why: List[str]
    next_action: str

class ProjectListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    projects: List[ProjectResponse]
