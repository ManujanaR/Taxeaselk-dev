from datetime import date, datetime

from pydantic import Field

from app.schemas.base import CamelModel


class EngagementOut(CamelModel):
    id: str
    company_id: str
    auditor_id: str
    tax_year: str
    status: str
    message: str
    created_at: datetime
    accepted_at: datetime | None
    submitted_at: datetime | None
    approved_at: datetime | None


class AuditorSummary(CamelModel):
    id: str
    name: str
    firm: str
    email: str
    average_rating: float | None
    total_reviews: int


class ReviewIn(CamelModel):
    rating: int = Field(ge=1, le=5)
    timeliness: int = Field(ge=1, le=5)
    communication: int = Field(ge=1, le=5)
    technical: int = Field(ge=1, le=5)
    comment: str = ""


class ReviewOut(ReviewIn):
    id: str
    created_at: datetime


class ChecklistItemIn(CamelModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = ""
    description: str = ""
    required: bool = True


class ChecklistItemOut(ChecklistItemIn):
    id: str
    order_index: int
    provided_document_id: str | None = None


class DocumentOut(CamelModel):
    id: str
    name: str
    doc_type: str
    status: str
    size_bytes: int
    content_type: str
    checklist_item_id: str | None
    created_at: datetime
    verified_at: datetime | None


class AttachmentOut(CamelModel):
    id: str
    name: str = Field(validation_alias="original_name")
    size_bytes: int
    content_type: str


class IssueOut(CamelModel):
    id: str
    engagement_id: str
    title: str
    comment: str
    source: str
    severity: str
    status: str
    response_text: str
    created_at: datetime
    resolved_at: datetime | None
    attachments: list[AttachmentOut] = []


class ResponseOut(CamelModel):
    id: str
    request_id: str
    note: str
    revision_note: str
    status: str
    created_at: datetime
    attachments: list[AttachmentOut] = []


class RequestOut(CamelModel):
    id: str
    engagement_id: str
    reference_code: str
    title: str
    description: str
    category: str
    priority: str
    due_date: date | None
    status: str
    created_at: datetime
    response: ResponseOut | None = None


class NotificationOut(CamelModel):
    id: str
    type: str
    title: str
    message: str
    link: str
    is_read: bool
    created_at: datetime


class AuditLogOut(CamelModel):
    id: str
    company_id: str
    company_name: str
    actor_name: str
    actor_role: str
    event_type: str
    details: str
    tone: str
    created_at: datetime
