from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.project import Project
from backend.services.insights_service import DynamicInsightsService
from backend.schemas.insights import AIInsightsResponse

router = APIRouter(prefix="/api/insights", tags=["AI Insights"])

@router.get("", response_model=AIInsightsResponse)
def get_ai_insights(db: Session = Depends(get_db)):
    first_proj = db.query(Project).first()
    data_source = first_proj.source if first_proj else "SYNTHETIC DEMO"
    insights_data = DynamicInsightsService.generate_insights(db, data_source=data_source)
    return insights_data
