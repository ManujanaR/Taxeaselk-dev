from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, live_engagement
from app.models import Engagement, LIVE_ENGAGEMENT_STATUSES, Message, Notification, Request, Response, Thread, User
from app.schemas.base import CamelModel
from app.schemas.shared import NotificationOut
from app.services.events import touch

router = APIRouter(prefix="/api", tags=["notifications"])


class NotificationsOut(CamelModel):
    unread_count: int
    notifications: list[NotificationOut]


class BadgesOut(CamelModel):
    requests: int = 0
    responses: int = 0
    threads: int = 0


@router.get("/notifications", response_model=NotificationsOut)
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    return NotificationsOut(
        unread_count=q.filter(Notification.is_read.is_(False)).count(),
        notifications=q.order_by(Notification.created_at.desc()).limit(50).all(),
    )


@router.post("/notifications/{notification_id}/read", status_code=204)
def mark_read(notification_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notification_id)
    if not n or n.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    touch(db, user.id)
    db.commit()


@router.post("/notifications/read-all", status_code=204)
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).update(
        {"is_read": True}, synchronize_session=False)
    touch(db, user.id)
    db.commit()


def unread_thread_count(db: Session, user: User, engagement_ids: list[str]) -> int:
    if not engagement_ids:
        return 0
    read_col = Thread.business_read_at if user.role == "business" else Thread.auditor_read_at
    return (
        db.query(func.count(func.distinct(Thread.id)))
        .join(Message, Message.thread_id == Thread.id)
        .filter(Thread.engagement_id.in_(engagement_ids), Message.sender_id != user.id)
        .filter((read_col.is_(None)) | (Message.created_at > read_col))
        .scalar() or 0
    )


@router.get("/nav/badges", response_model=BadgesOut)
def nav_badges(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "business":
        eng = live_engagement(db, user.company.id)
        ids = [eng.id] if eng else []
        pending = db.query(Request).filter(Request.engagement_id.in_(ids), Request.status.in_(["pending", "revision_requested"])).count() if ids else 0
        return BadgesOut(requests=pending, threads=unread_thread_count(db, user, ids))
    ids = [e.id for e in db.query(Engagement.id).filter(
        Engagement.auditor_id == user.auditor_profile.id, Engagement.status.in_(LIVE_ENGAGEMENT_STATUSES))]
    unreviewed = (db.query(Response).join(Request).filter(Request.engagement_id.in_(ids), Response.status == "unreviewed").count()
                  if ids else 0)
    return BadgesOut(responses=unreviewed, threads=unread_thread_count(db, user, ids))
