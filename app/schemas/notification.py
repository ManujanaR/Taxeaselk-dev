from pydantic import BaseModel
from typing import List, Optional

class NotificationItem(BaseModel):
    id: str
    type: str # "critical", "warning", "info", "success"
    title: str
    message: str
    link: str
    is_read: bool
    created_at: str
    company_name: Optional[str] = None

class NotificationsSummary(BaseModel):
    unread_count: int
    notifications: List[NotificationItem]
