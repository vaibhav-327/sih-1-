import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from backend.database import get_db
from backend.models.alert import Alert, AuditLog
from backend.schemas.alert import AlertResponse, AlertListResponse, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["Alerts & Investigations"])

@router.get("", response_model=AlertListResponse)
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)

    if status and status.strip() and status.lower() != "all":
        query = query.filter(Alert.status == status.strip().upper())
    if severity and severity.strip() and severity.lower() != "all":
        query = query.filter(Alert.severity == severity.strip().upper())
    if alert_type and alert_type.strip() and alert_type.lower() != "all":
        query = query.filter(Alert.alert_type == alert_type.strip())
    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter(
            Alert.project_id.ilike(s) | Alert.project_name.ilike(s) |
            Alert.reason.ilike(s) | Alert.district.ilike(s) | Alert.constituency.ilike(s)
        )

    alerts = query.order_by(desc(Alert.risk_score), desc(Alert.created_at)).all()

    # Summaries for tabs/filters
    status_counts = dict(db.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all())
    severity_counts = dict(db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all())

    return AlertListResponse(
        total=len(alerts),
        alerts=alerts,
        summary_by_status=status_counts,
        summary_by_severity=severity_counts
    )

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: str, update_data: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    old_status = alert.status
    if update_data.status:
        alert.status = update_data.status.upper()
    if update_data.assigned_officer is not None:
        alert.assigned_officer = update_data.assigned_officer
    if update_data.investigation_notes is not None:
        alert.investigation_notes = update_data.investigation_notes
    if update_data.resolution_summary is not None:
        alert.resolution_summary = update_data.resolution_summary

    alert.updated_at = datetime.datetime.now()

    # Record Audit Log
    audit_entry = AuditLog(
        id=f"AUD-{int(datetime.datetime.now().timestamp() * 1000)}",
        timestamp=datetime.datetime.now(),
        user="Investigation Officer",
        action="ALERT_STATUS_UPDATE",
        entity="Alert",
        entity_id=alert.id,
        old_value=f"Status: {old_status}",
        new_value=f"Status: {alert.status}, Officer: {alert.assigned_officer}",
        details={
            "project_id": alert.project_id,
            "investigation_notes": alert.investigation_notes
        }
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(alert)

    return alert
