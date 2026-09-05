from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from backend.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True) # project_id
    project_name = Column(String(255), nullable=False, index=True)
    project_description = Column(Text, nullable=True)
    
    # Geographic metadata
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    constituency = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Classification & Stakeholders
    project_type = Column(String(100), nullable=False, index=True) # Road, School, Water Supply, Healthcare, Solar, etc.
    beneficiary_count = Column(Integer, default=0)
    contractor_id = Column(String(64), nullable=True, index=True)
    contractor_name = Column(String(255), nullable=True, index=True)
    implementing_agency = Column(String(255), nullable=True)
    
    # Financial fields (in Rupees)
    sanctioned_amount = Column(Float, default=0.0)
    released_amount = Column(Float, default=0.0)
    utilized_amount = Column(Float, default=0.0)
    
    # Progress fields (0 to 100)
    physical_progress = Column(Float, default=0.0) # Percentage (0-100)
    financial_progress = Column(Float, default=0.0) # Percentage (0-100)
    status = Column(String(50), default="In Progress", index=True) # In Progress, Completed, Delayed, Stalled, Sanctioned
    
    # Timeline
    start_date = Column(DateTime, nullable=True)
    sanction_date = Column(DateTime, nullable=True)
    expected_completion_date = Column(DateTime, nullable=True)
    actual_completion_date = Column(DateTime, nullable=True)
    
    # Derived & Engineered features
    duration_days = Column(Integer, default=0)
    delay_days = Column(Integer, default=0)
    cost_deviation = Column(Float, default=0.0) # Percentage deviation vs baseline/cohort
    utilization_percentage = Column(Float, default=0.0)
    efficiency_gap = Column(Float, default=0.0) # financial_progress - physical_progress
    
    # AI & Risk Engine outputs
    anomaly_score = Column(Float, default=0.0) # 0-100 from Isolation Forest
    risk_score = Column(Float, default=0.0, index=True) # 0-100 unified risk score
    risk_level = Column(String(20), default="LOW", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    risk_reasons = Column(JSON, default=list) # List of explainability factors
    recommended_actions = Column(JSON, default=list) # List of suggested actions
    
    # Similarity / Duplicate flags
    similar_project_id = Column(String(64), nullable=True)
    similarity_score = Column(Float, default=0.0)
    
    # Data Provenance
    source = Column(String(50), default="e-Sakshi") # e-Sakshi, Synthetic Demo, etc.
    source_file = Column(String(255), nullable=True)
    source_record_id = Column(String(100), nullable=True)
    import_timestamp = Column(DateTime, default=func.now())
    data_version = Column(String(20), default="v1.0")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
