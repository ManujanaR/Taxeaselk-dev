from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.discussion import DiscussionThread, DiscussionMessage
from app.models.notification import Notification
from app.schemas.discussion import (
    DiscussionThreadSchema, DiscussionMessageSchema, NewDiscussionRequest, MessageSendRequest
)

router = APIRouter(tags=["Discussions"])

@router.get("/api/business/discussions", response_model=list[DiscussionThreadSchema])
def get_business_discussions(company_name: str = Query("ABC (Pvt) Ltd"), db: Session = Depends(get_db)):
    threads = db.query(DiscussionThread).filter(DiscussionThread.company_name == company_name).all()
    results = []
    for th in threads:
        messages = db.query(DiscussionMessage).filter(DiscussionMessage.thread_id == th.id).order_by(DiscussionMessage.created_at.asc()).all()
        msg_schemas = [
            DiscussionMessageSchema(
                id=str(m.id),
                senderName=m.sender_name,
                senderRole=m.sender_role,
                text=m.text,
                timestamp=m.timestamp
            ) for m in messages
        ]
        results.append(DiscussionThreadSchema(
            id=str(th.id),
            companyName=th.company_name,
            topic=th.topic,
            category=th.category,
            status=th.status,
            unreadCount=th.unread_count,
            lastMessage=th.last_message,
            lastUpdated=th.last_updated,
            messages=msg_schemas
        ))
    return results

@router.post("/api/business/discussions")
def create_business_discussion(payload: NewDiscussionRequest, db: Session = Depends(get_db)):
    comp_name = payload.company_name or "ABC (Pvt) Ltd"
    thread = DiscussionThread(
        company_name=comp_name,
        topic=payload.topic,
        category=payload.category,
        status="Open",
        unread_count=1,
        last_message=payload.initialMessage,
        last_updated="Just now"
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)

    msg = DiscussionMessage(
        thread_id=thread.id,
        sender_name="Finance Director",
        sender_role="Company",
        text=payload.initialMessage,
        timestamp="Just now"
    )
    db.add(msg)
    db.add(Notification(
        recipient_role="auditor",
        company_name=comp_name,
        type="info",
        title=f"New Discussion: {payload.topic}",
        message=f"{comp_name} started a new audit discussion topic.",
        link="/auditor-discussions"
    ))
    db.commit()
    return {"success": True, "thread_id": thread.id}

@router.post("/api/business/discussions/{thread_id}/messages")
def send_business_message(thread_id: str, payload: MessageSendRequest, db: Session = Depends(get_db)):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")

    sender_role = payload.sender_role or "Company"
    sender_name = payload.sender_name or ("Finance Director" if sender_role == "Company" else "K.L. Perera, FCA")

    msg = DiscussionMessage(
        thread_id=thread.id,
        sender_name=sender_name,
        sender_role=sender_role,
        text=payload.text,
        timestamp="Just now"
    )
    db.add(msg)
    thread.last_message = payload.text
    thread.last_updated = "Just now"

    recipient = "auditor" if sender_role == "Company" else "business"
    db.add(Notification(
        recipient_role=recipient,
        company_name=thread.company_name,
        type="info",
        title=f"New message in {thread.topic}",
        message=f"{sender_name}: {payload.text[:80]}...",
        link="/auditor-discussions" if recipient == "auditor" else "/discussions"
    ))
    db.commit()
    return {"success": True, "message_id": msg.id}

@router.post("/api/business/discussions/{thread_id}/resolve")
def resolve_business_discussion(thread_id: str, db: Session = Depends(get_db)):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if thread:
        thread.status = "Closed"
        db.commit()
    return {"success": True, "status": "Closed"}

# --- AUDITOR MULTI-CLIENT DISCUSSIONS ---
@router.get("/api/auditor/discussions", response_model=list[DiscussionThreadSchema])
@router.get("/api/discussions", response_model=list[DiscussionThreadSchema])
def get_auditor_discussions(db: Session = Depends(get_db)):
    threads = db.query(DiscussionThread).all()
    results = []
    for th in threads:
        messages = db.query(DiscussionMessage).filter(DiscussionMessage.thread_id == th.id).order_by(DiscussionMessage.created_at.asc()).all()
        msg_schemas = [
            DiscussionMessageSchema(
                id=str(m.id),
                senderName=m.sender_name,
                senderRole=m.sender_role,
                text=m.text,
                timestamp=m.timestamp
            ) for m in messages
        ]
        results.append(DiscussionThreadSchema(
            id=str(th.id),
            companyName=th.company_name,
            topic=th.topic,
            category=th.category,
            status=th.status,
            unreadCount=th.unread_count,
            lastMessage=th.last_message,
            lastUpdated=th.last_updated,
            messages=msg_schemas
        ))
    return results

@router.post("/api/auditor/discussions/{thread_id}/reply")
@router.post("/api/auditor/discussions/{thread_id}/messages")
def reply_auditor_discussion(thread_id: str, payload: MessageSendRequest, db: Session = Depends(get_db)):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Discussion thread not found")

    msg = DiscussionMessage(
        thread_id=thread.id,
        sender_name="K.L. Perera, FCA",
        sender_role="Auditor",
        text=payload.text,
        timestamp="Just now"
    )
    db.add(msg)
    thread.last_message = payload.text
    thread.last_updated = "Just now"

    db.add(Notification(
        recipient_role="business",
        company_name=thread.company_name,
        type="info",
        title=f"Auditor replied to {thread.topic}",
        message=f"K.L. Perera: {payload.text[:80]}...",
        link="/discussions"
    ))
    db.commit()
    return {"success": True, "message_id": msg.id, "timestamp": "Just now"}

@router.post("/api/auditor/discussions/{thread_id}/resolve")
def resolve_auditor_discussion(thread_id: str, db: Session = Depends(get_db)):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if thread:
        thread.status = "Closed" if thread.status == "Open" else "Open"
        db.commit()
    return {"success": True, "status": thread.status if thread else "Closed"}
