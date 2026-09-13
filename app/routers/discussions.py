"""Discussion threads between a company and its auditor. Scoped by the caller's engagements."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, live_engagement
from app.models import Engagement, LIVE_ENGAGEMENT_STATUSES, Message, Thread, User, now
from app.schemas.base import CamelModel
from app.services.notify import log, notify

router = APIRouter(prefix="/api/threads", tags=["discussions"])


class ThreadOut(CamelModel):
    id: str
    engagement_id: str
    company_name: str
    auditor_name: str
    topic: str
    category: str
    status: str
    last_message: str
    last_message_at: datetime
    unread_count: int


class MessageOut(CamelModel):
    id: str
    sender_id: str
    sender_name: str
    sender_role: str
    text: str
    created_at: datetime


def _my_engagement_ids(db: Session, user: User) -> list[str]:
    if user.role == "business":
        eng = live_engagement(db, user.company.id)
        return [eng.id] if eng and eng.status != "invited" else []
    return [e.id for e in db.query(Engagement.id).filter(Engagement.auditor_id == user.auditor_profile.id,
                                                          Engagement.status.in_(LIVE_ENGAGEMENT_STATUSES + ("approved",)))]


def _thread_for(db: Session, user: User, thread_id: str) -> Thread:
    t = db.get(Thread, thread_id)
    if not t or t.engagement_id not in _my_engagement_ids(db, user):
        raise HTTPException(404, "Thread not found")
    return t


def _read_at(t: Thread, user: User) -> datetime | None:
    return t.business_read_at if user.role == "business" else t.auditor_read_at


def _other_party(t: Thread, user: User) -> str:
    return t.engagement.auditor.user_id if user.role == "business" else t.engagement.company.user_id


def thread_out(t: Thread, user: User) -> ThreadOut:
    read_at = _read_at(t, user)
    last = t.messages[-1] if t.messages else None
    return ThreadOut(
        id=t.id, engagement_id=t.engagement_id, company_name=t.engagement.company.company_name,
        auditor_name=t.engagement.auditor.user.full_name, topic=t.topic, category=t.category, status=t.status,
        last_message=last.text if last else "", last_message_at=t.last_message_at,
        unread_count=sum(1 for m in t.messages if m.sender_id != user.id and (read_at is None or m.created_at > read_at)),
    )


def message_out(m: Message) -> MessageOut:
    return MessageOut(id=m.id, sender_id=m.sender_id, sender_name=m.sender.full_name, sender_role=m.sender.role, text=m.text, created_at=m.created_at)


@router.get("", response_model=list[ThreadOut])
def list_threads(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ids = _my_engagement_ids(db, user)
    if not ids:
        return []
    threads = db.query(Thread).filter(Thread.engagement_id.in_(ids)).order_by(Thread.last_message_at.desc()).all()
    return [thread_out(t, user) for t in threads]


class ThreadIn(CamelModel):
    topic: str
    category: str = "General"
    text: str
    engagement_id: str | None = None  # auditors must say which client


@router.post("", response_model=ThreadOut, status_code=201)
def create_thread(payload: ThreadIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ids = _my_engagement_ids(db, user)
    eng_id = ids[0] if user.role == "business" and ids else payload.engagement_id
    if not eng_id or eng_id not in ids:
        raise HTTPException(409, "No active engagement to discuss with")
    t = Thread(engagement_id=eng_id, topic=payload.topic.strip(), category=payload.category)
    db.add(t)
    db.flush()
    _post(db, t, user, payload.text)
    db.commit()
    db.refresh(t)
    return thread_out(t, user)


def _post(db: Session, t: Thread, user: User, text: str) -> Message:
    m = Message(thread_id=t.id, sender_id=user.id, text=text.strip())
    db.add(m)
    t.last_message_at = now()
    if user.role == "business":
        t.business_read_at = t.last_message_at
    else:
        t.auditor_read_at = t.last_message_at
    who = user.company.company_name if user.role == "business" else user.full_name
    notify(db, _other_party(t, user), f"New message: {t.topic}", f"{who}: {text.strip()[:120]}",
           "/auditor-discussions" if user.role == "business" else "/discussions")
    log(db, t.engagement.company_id, user.id, "DISCUSSION_MESSAGE", f"Message in '{t.topic}'.")
    return m


@router.get("/{thread_id}/messages", response_model=list[MessageOut])
def list_messages(thread_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = _thread_for(db, user, thread_id)
    if user.role == "business":
        t.business_read_at = now()
    else:
        t.auditor_read_at = now()
    db.commit()
    return [message_out(m) for m in t.messages]


class MessageIn(CamelModel):
    text: str


@router.post("/{thread_id}/messages", response_model=MessageOut, status_code=201)
def post_message(thread_id: str, payload: MessageIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = _thread_for(db, user, thread_id)
    if not payload.text.strip():
        raise HTTPException(422, "Message cannot be empty")
    m = _post(db, t, user, payload.text)
    db.commit()
    db.refresh(m)
    return message_out(m)


class StatusIn(CamelModel):
    status: str


@router.post("/{thread_id}/status", response_model=ThreadOut)
def set_status(thread_id: str, payload: StatusIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = _thread_for(db, user, thread_id)
    if payload.status not in ("open", "closed"):
        raise HTTPException(422, "status must be open or closed")
    t.status = payload.status
    db.commit()
    return thread_out(t, user)
