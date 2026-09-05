from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class KPISummary(BaseModel):
    total_projects: int
    total_sanctioned_amount: float
    total_released_amount: float
    total_utilized_amount: float
    utilization_percentage: float
    completed_projects: int
    delayed_projects: int
    high_risk_projects: int
    critical_risk_projects: int
    average_risk_score: float
    data_quality_score: float

class StatusDistribution(BaseModel):
    status: str
    count: int
    percentage: float

class RiskDistribution(BaseModel):
    level: str # LOW, MEDIUM, HIGH, CRITICAL
    count: int
    percentage: float
    color: str

class StateDistribution(BaseModel):
    state: str
    project_count: int
    total_sanctioned: float
    avg_risk_score: float
    delayed_count: int

class ProjectTypeDistribution(BaseModel):
    project_type: str
    count: int
    total_amount: float
    avg_risk: float

class MonthlyTrend(BaseModel):
    month: str
    expenditure: float
    sanctioned: float
    projects_started: int
    anomalies_flagged: int

class EfficiencyScatterPoint(BaseModel):
    project_id: str
    project_name: str
    physical_progress: float
    financial_progress: float
    risk_level: str
    sanctioned_amount: float

class RiskDriverCategory(BaseModel):
    id: str
    title: str
    count: int
    description: str
    filter_key: str
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    icon: str

class PriorityActionItem(BaseModel):
    id: str
    title: str
    headline: str
    count: int
    short_explanation: str
    severity: str # CRITICAL, HIGH, MEDIUM
    action_label: str
    action_url: str
    icon: str

class DecisionPipelineStage(BaseModel):
    id: str
    step: str
    name: str
    description: str
    target_url: str
    icon: str

class AIHighlightSummary(BaseModel):
    title: str
    headline: str
    flagged_count: int
    top_drivers: List[str]
    action_label: str
    action_url: str

class DashboardResponse(BaseModel):
    data_source: str # e-SAKSHI or SYNTHETIC DEMO
    data_source_mode: str
    last_sync: Optional[datetime] = None
    kpis: KPISummary
    ai_highlight: Optional[AIHighlightSummary] = None
    risk_drivers: Optional[List[RiskDriverCategory]] = []
    priority_actions: Optional[List[PriorityActionItem]] = []
    decision_pipeline: Optional[List[DecisionPipelineStage]] = []
    status_distribution: List[StatusDistribution]
    risk_distribution: List[RiskDistribution]
    state_distribution: List[StateDistribution]
    project_type_distribution: List[ProjectTypeDistribution]
    monthly_trend: List[MonthlyTrend]
    top_high_risk_constituencies: List[Dict[str, Any]]
    top_high_risk_contractors: List[Dict[str, Any]]
    efficiency_gap_scatter: List[EfficiencyScatterPoint]
    recent_alerts: List[Dict[str, Any]]
