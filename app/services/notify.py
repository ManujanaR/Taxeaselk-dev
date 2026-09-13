"""Every cross-portal event calls notify() for the other party and log() for the audit trail."""
from sqlalchemy.orm import Session

from app.models import AuditLog, Engagement, Notification


def notify(db: Session, user_id: str, title: str, message: str = "", link: str = "", type: str = "info") -> None:
    db.add(Notification(user_id=user_id, type=type, title=title, message=message, link=link))


def log(db: Session, company_id: str, actor_id: str, event_type: str, details: str, tone: str = "info") -> None:
    db.add(AuditLog(company_id=company_id, actor_id=actor_id, event_type=event_type, details=details, tone=tone))


def business_user_id(eng: Engagement) -> str:
    return eng.company.user_id


def auditor_user_id(eng: Engagement) -> str:
    return eng.auditor.user_id
