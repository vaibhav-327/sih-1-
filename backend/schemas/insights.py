from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AIInsightItem(BaseModel):
    category: str # Financial, Implementation, Contractor, Geographic, Emerging Patterns
    icon_type: str # warning, alert, check, info
    title: str
    description: str
    impact_level: str # CRITICAL, HIGH, MEDIUM, POSITIVE
    metric_value: str
    recommended_action: str
    affected_count: int

class AIInsightsResponse(BaseModel):
    generated_at: datetime
    data_source: str
    summary_headline: str
    total_anomalies_detected: int
    insights: List[AIInsightItem]
    national_overview: Dict[str, Any]

class ModelFeatureImportance(BaseModel):
    feature: str
    importance: float
    description: str

class ModelMetricsResponse(BaseModel):
    model_name: str
    model_version: str
    last_trained: Optional[datetime] = None
    training_sample_size: int
    contamination_rate: float
    features_used: List[str]
    feature_importances: List[ModelFeatureImportance]
    nlp_model_type: str
    nlp_similarity_threshold: float
    anomaly_detection_method: str
    risk_scoring_methodology: str
    performance_metrics: Dict[str, Any]
    confusion_matrix_notes: str

class ValidationIssue(BaseModel):
    rule: str
    severity: str # WARNING, ERROR, CRITICAL
    count: int
    description: str
    affected_ids: List[str]

class DataValidationReport(BaseModel):
    data_quality_score: float # 0 to 100
    total_records: int
    valid_records: int
    invalid_records: int
    duplicates_count: int
    missing_fields_count: int
    issues: List[ValidationIssue]
    passed_checks: List[str]
    timestamp: datetime

class AIScanResult(BaseModel):
    scan_id: str
    timestamp: datetime
    data_source: str
    projects_analyzed: int
    anomalies_detected: int
    high_risk_projects: int
    critical_risk_projects: int
    cost_anomalies: int
    delay_anomalies: int
    efficiency_gap_anomalies: int
    potential_duplicate_projects: int
    contractor_concentration_risks: int
    alerts_generated: int
    top_findings: List[Dict[str, Any]]
    execution_time_seconds: float
