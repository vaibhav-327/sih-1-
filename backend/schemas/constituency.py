from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ConstituencyBase(BaseModel):
    name: str
    state: str
    mp_name: Optional[str] = None
    mp_house: Optional[str] = "Lok Sabha"
    term: Optional[str] = "17th Lok Sabha"

class ConstituencyResponse(ConstituencyBase):
    id: str
    total_projects: int
    total_sanctioned_amount: float
    total_released_amount: float
    total_utilized_amount: float
    utilization_rate: float
    completion_rate: float
    delay_rate: float
    completed_projects: int
    delayed_projects: int
    high_risk_projects: int
    average_risk_score: float
    average_cost_deviation: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConstituencyListResponse(BaseModel):
    total: int
    constituencies: List[ConstituencyResponse]
