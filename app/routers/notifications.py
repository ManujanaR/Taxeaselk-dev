from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationsSummary, NotificationItem

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("", response_model=NotificationsSummary)
def get_notifications(
    role: str = Query("business"),
    company: str = Query(None),
    company_name: str = Query(None),
    db: Session = Depends(get_db)
):
    target_comp = company or company_name
    query = db.query(Notification).filter(Notification.recipient_role == role)
    if target_comp and role == "business":
        query = query.filter(Notification.company_name == target_comp)

    notifications_db = query.order_by(Notification.created_at.desc()).all()
    unread_cnt = len([n for n in notifications_db if not n.is_read])

    items = [
        NotificationItem(
            id=str(n.id),
            type=n.type,
            title=n.title,
            message=n.message,
            link=n.link,
            is_read=n.is_read,
            created_at=n.created_at.strftime("%I:%M %p") if n.created_at else "Just now",
            company_name=n.company_name
        ) for n in notifications_db
    ]

    return NotificationsSummary(
        unread_count=unread_cnt,
        notifications=items
    )

@router.post("/{notification_id}/read")
def mark_notification_as_read(notification_id: str, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"success": True, "id": notification_id}

@router.post("/mark-all-read")
def mark_all_notifications_as_read(role: str = Query("business"), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.recipient_role == role).update({"is_read": True})
    db.commit()
    return {"success": True, "message": "All notifications marked as read"}
