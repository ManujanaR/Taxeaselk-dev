from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter(tags=["Compliance Audit Log"])

@router.get("/api/auditor/audit-log")
def get_audit_logs(company_name: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(AuditLog)
    if company_name:
        query = query.filter(AuditLog.company_name == company_name)
    logs = query.order_by(AuditLog.created_at.desc()).all()

    return {
        "total": len(logs),
        "logs": [
            {
                "id": l.id,
                "timestamp": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "2026-10-15 10:30:00",
                "companyName": l.company_name,
                "actor": f"{l.actor_name} ({l.actor_role})",
                "eventType": l.event_type,
                "details": l.details,
                "tone": l.action_tone
            } for l in logs
        ]
    }

@router.post("/api/audit-log")
def record_audit_log(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_log = AuditLog(
        company_name=payload.get("company_name", "ABC (Pvt) Ltd"),
        actor_name=payload.get("actor_name", "System"),
        actor_role=payload.get("actor_role", "Compliance Engine"),
        event_type=payload.get("event_type", "GENERAL_LOG"),
        details=payload.get("details", "Compliance event recorded"),
        action_tone=payload.get("action_tone", "info")
    )
    db.add(new_log)
    db.commit()
    return {"success": True, "log_id": new_log.id}
