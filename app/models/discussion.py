import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from app.core.database import Base

class DiscussionThread(Base):
    __tablename__ = "discussion_threads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), index=True)
    topic = Column(String(255), nullable=False)
    category = Column(String(100), default="Statutory CIT")
    status = Column(String(50), default="Open") # "Open", "Closed"
    unread_count = Column(Integer, default=0)
    last_message = Column(Text, nullable=True)
    last_updated = Column(String(100), default="Just now")
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscussionMessage(Base):
    __tablename__ = "discussion_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String(36), ForeignKey("discussion_threads.id"), nullable=False)
    sender_name = Column(String(255), nullable=False)
    sender_role = Column(String(50), nullable=False) # "Auditor", "Company"
    text = Column(Text, nullable=False)
    timestamp = Column(String(100), default="Just now")
    created_at = Column(DateTime, default=datetime.utcnow)
