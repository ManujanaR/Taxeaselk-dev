"""Every cross-portal event calls notify() for the other party and log() for the audit trail.

notify() also queues a realtime event that is pushed to the recipient's open tabs after commit.
"""
from sqlalchemy.orm import Session

from app.models import AuditLog, Engagement, Notification
from app.services.events import queue_event, touch  # noqa: F401  (touch re-exported for routers)


def notify(db: Session, user_id: str, title: str, message: str = "", link: str = "", type: str = "info") -> None:
    n = Notification(user_id=user_id, type=type, title=title, message=message, link=link)
    db.add(n)
    queue_event(db, user_id, n)


def log(db: Session, company_id: str, actor_id: str, event_type: str, details: str, tone: str = "info") -> None:
    db.add(AuditLog(company_id=company_id, actor_id=actor_id, event_type=event_type, details=details, tone=tone))


def business_user_id(eng: Engagement) -> str:
    return eng.company.user_id


def auditor_user_id(eng: Engagement) -> str:
    return eng.auditor.user_id
