from pydantic import BaseModel
from typing import List, Optional

class DiscussionMessageSchema(BaseModel):
    id: str
    senderName: str
    senderRole: str # "Auditor" | "Company"
    text: str
    timestamp: str

class DiscussionThreadSchema(BaseModel):
    id: str
    companyName: str
    topic: str
    category: str
    status: str # "Open" | "Closed"
    unreadCount: int
    lastMessage: Optional[str] = None
    lastUpdated: str
    messages: Optional[List[DiscussionMessageSchema]] = []

class NewDiscussionRequest(BaseModel):
    topic: str
    category: str
    initialMessage: str
    company_name: Optional[str] = None

class MessageSendRequest(BaseModel):
    text: str
    sender_name: Optional[str] = None
    sender_role: Optional[str] = None
