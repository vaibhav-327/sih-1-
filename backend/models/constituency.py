from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Constituency(Base):
    __tablename__ = "constituencies"

    id = Column(String(64), primary_key=True, index=True) # E.g., "PC-VARANASI" or "PC-01"
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    mp_name = Column(String(150), nullable=True)
    mp_house = Column(String(50), default="Lok Sabha") # Lok Sabha / Rajya Sabha
    term = Column(String(50), default="17th Lok Sabha")
    
    # Financial and project statistics
    total_projects = Column(Integer, default=0)
    total_sanctioned_amount = Column(Float, default=0.0)
    total_released_amount = Column(Float, default=0.0)
    total_utilized_amount = Column(Float, default=0.0)
    
    utilization_rate = Column(Float, default=0.0) # Percentage (0-100)
    completion_rate = Column(Float, default=0.0) # Percentage (0-100)
    delay_rate = Column(Float, default=0.0) # Percentage
    
    completed_projects = Column(Integer, default=0)
    delayed_projects = Column(Integer, default=0)
    high_risk_projects = Column(Integer, default=0)
    average_risk_score = Column(Float, default=0.0)
    average_cost_deviation = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
