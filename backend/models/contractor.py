from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.sql import func
from backend.database import Base

class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(String(64), primary_key=True, index=True)
    contractor_name = Column(String(255), nullable=False, index=True)
    registration_number = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    
    # Aggregated metrics
    total_projects = Column(Integer, default=0)
    total_contract_value = Column(Float, default=0.0)
    average_project_value = Column(Float, default=0.0)
    completed_projects = Column(Integer, default=0)
    delayed_projects = Column(Integer, default=0)
    high_risk_projects = Column(Integer, default=0)
    average_delay_days = Column(Float, default=0.0)
    average_cost_deviation = Column(Float, default=0.0)
    share_of_constituency_projects = Column(Float, default=0.0) # Percentage
    
    # Risk assessment
    contractor_risk_score = Column(Float, default=0.0)
    contractor_risk_level = Column(String(20), default="LOW")
    risk_factors = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
