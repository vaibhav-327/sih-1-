from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from backend.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, index=True) # ALT-XXXX
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    project_name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    constituency = Column(String(100), nullable=False)
    
    alert_type = Column(String(100), nullable=False, index=True) 
    # e.g., "Cost Inflation Anomaly", "Extreme Delay & Stalled Work", "High Financial vs Physical Progress Gap", "Contractor Concentration Risk", "Potential Similar/Duplicate Project"
    
    risk_score = Column(Float, nullable=False, index=True)
    severity = Column(String(20), default="HIGH", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    detected_date = Column(DateTime, default=func.now())
    reason = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    
    # Workflow fields
    status = Column(String(50), default="NEW", index=True) 
    # NEW, UNDER REVIEW, FIELD VERIFICATION, RESOLVED, FALSE POSITIVE
    
    assigned_officer = Column(String(100), nullable=True)
    investigation_notes = Column(Text, nullable=True)
    resolution_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    user = Column(String(100), default="AI Sentinel System")
    action = Column(String(100), nullable=False) # e.g., "DATA_IMPORT", "MODEL_RUN", "ALERT_STATUS_UPDATE", "FIELD_VERIFICATION_ASSIGNED"
    entity = Column(String(50), nullable=False) # "Project", "Alert", "Model", "DataSource"
    entity_id = Column(String(64), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    details = Column(JSON, default=dict)

class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(String(64), primary_key=True, index=True)
    run_timestamp = Column(DateTime, default=func.now())
    model_type = Column(String(100), default="Isolation Forest + NLP Similarity + Rule Risk Engine")
    training_records = Column(Integer, default=0)
    anomalies_detected = Column(Integer, default=0)
    high_risk_detected = Column(Integer, default=0)
    cost_anomalies = Column(Integer, default=0)
    delay_anomalies = Column(Integer, default=0)
    efficiency_anomalies = Column(Integer, default=0)
    duplicate_anomalies = Column(Integer, default=0)
    parameters = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    status = Column(String(50), default="COMPLETED")
