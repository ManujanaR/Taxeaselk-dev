"""All ORM models. Every child row is keyed by id (never by company name)."""
import uuid
from datetime import datetime, timezone, date

from sqlalchemy import (
    Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """Always hand back tz-aware UTC datetimes (SQLite drops tzinfo; Postgres timestamptz keeps it)."""
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=timezone.utc) if value is not None and value.tzinfo is None else value


def _uuid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=now)


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # business | auditor
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company: Mapped["Company | None"] = relationship(back_populates="user", uselist=False)
    auditor_profile: Mapped["AuditorProfile | None"] = relationship(back_populates="user", uselist=False)


class Company(Base):
    __tablename__ = "companies"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    company_name: Mapped[str] = mapped_column(String(255))
    trading_name: Mapped[str] = mapped_column(String(255), default="")
    registration_number: Mapped[str] = mapped_column(String(50), default="")
    tin_number: Mapped[str] = mapped_column(String(50), default="")
    vat_number: Mapped[str] = mapped_column(String(50), default="")
    is_svat_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    svat_number: Mapped[str] = mapped_column(String(50), default="")
    cit_tax_rate_category: Mapped[str] = mapped_column(String(20), default="standard_30")  # standard_30 | sme_14
    financial_year: Mapped[str] = mapped_column(String(20), default="2025/26")
    contact_email: Mapped[str] = mapped_column(String(255), default="")
    contact_phone: Mapped[str] = mapped_column(String(50), default="")
    registered_address: Mapped[str] = mapped_column(Text, default="")
    industry_sector: Mapped[str] = mapped_column(String(100), default="")

    user: Mapped[User] = relationship(back_populates="company")
    engagements: Mapped[list["Engagement"]] = relationship(back_populates="company")


class AuditorProfile(Base):
    __tablename__ = "auditor_profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    firm_name: Mapped[str] = mapped_column(String(255))
    firm_reg_no: Mapped[str] = mapped_column(String(50), default="")
    license_number: Mapped[str] = mapped_column(String(50), default="")
    icasl_member_no: Mapped[str] = mapped_column(String(50), default="")
    ird_practitioner_no: Mapped[str] = mapped_column(String(50), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    office_address: Mapped[str] = mapped_column(Text, default="")

    user: Mapped[User] = relationship(back_populates="auditor_profile")
    engagements: Mapped[list["Engagement"]] = relationship(back_populates="auditor")


LIVE_ENGAGEMENT_STATUSES = ("invited", "active", "under_review")
OPEN_REQUEST_STATUSES = ("pending", "responded", "revision_requested")
CLOSED_REQUEST_STATUSES = ("resolved", "dismissed")


class Engagement(Base):
    """An invitation is an engagement with status 'invited'."""
    __tablename__ = "engagements"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    auditor_id: Mapped[str] = mapped_column(ForeignKey("auditor_profiles.id", ondelete="CASCADE"), index=True)
    tax_year: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="invited")  # invited|declined|active|under_review|approved|terminated
    message: Mapped[str] = mapped_column(Text, default="")
    accepted_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    submitted_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    approved_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    company: Mapped[Company] = relationship(back_populates="engagements")
    auditor: Mapped[AuditorProfile] = relationship(back_populates="engagements")
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(back_populates="engagement", cascade="all, delete-orphan", order_by="ChecklistItem.order_index")
    requests: Mapped[list["Request"]] = relationship(back_populates="engagement", cascade="all, delete-orphan", order_by="Request.created_at")
    threads: Mapped[list["Thread"]] = relationship(back_populates="engagement", cascade="all, delete-orphan")
    review: Mapped["AuditorReview | None"] = relationship(back_populates="engagement", uselist=False)

    __table_args__ = (
        Index(
            "ux_engagements_one_live_per_company", "company_id", unique=True,
            postgresql_where=text("status IN ('invited','active','under_review')"),
            sqlite_where=text("status IN ('invited','active','under_review')"),
        ),
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    engagement_id: Mapped[str] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    engagement: Mapped[Engagement] = relationship(back_populates="checklist_items")
    documents: Mapped[list["Document"]] = relationship(back_populates="checklist_item")


class Document(Base):
    __tablename__ = "documents"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    checklist_item_id: Mapped[str | None] = mapped_column(ForeignKey("checklist_items.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(100))
    doc_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded|verified|review_required
    verified_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    submitted_at: Mapped[datetime | None] = mapped_column(UTCDateTime)  # NULL until the handover pack is sent

    checklist_item: Mapped[ChecklistItem | None] = relationship(back_populates="documents")


class FinancialInputs(Base):
    __tablename__ = "financial_inputs"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), unique=True)
    tax_year: Mapped[str] = mapped_column(String(20))
    revenue: Mapped[float] = mapped_column(Float, default=0)
    cost_of_sales: Mapped[float] = mapped_column(Float, default=0)
    operating_expenses: Mapped[float] = mapped_column(Float, default=0)
    accounting_depreciation: Mapped[float] = mapped_column(Float, default=0)
    entertainment_expenses: Mapped[float] = mapped_column(Float, default=0)
    tax_depreciation_allowances: Mapped[float] = mapped_column(Float, default=0)
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=now, onupdate=now)


class Request(Base):
    __tablename__ = "requests"
    engagement_id: Mapped[str] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), index=True)
    reference_code: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(100), default="General Inquiry")
    priority: Mapped[str] = mapped_column(String(10), default="MEDIUM")  # HIGH|MEDIUM|LOW
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending|responded|resolved|revision_requested

    engagement: Mapped[Engagement] = relationship(back_populates="requests")
    response: Mapped["Response | None"] = relationship(back_populates="request", uselist=False, cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), unique=True)
    submitted_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str] = mapped_column(Text, default="")
    revision_note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="unreviewed")  # unreviewed|resolved|revision_requested

    request: Mapped[Request] = relationship(back_populates="response")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="response", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    response_id: Mapped[str | None] = mapped_column(ForeignKey("responses.id", ondelete="CASCADE"))
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(100))

    response: Mapped[Response | None] = relationship(back_populates="attachments")


class Thread(Base):
    __tablename__ = "threads"
    engagement_id: Mapped[str] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), default="General")
    status: Mapped[str] = mapped_column(String(10), default="open")  # open|closed
    last_message_at: Mapped[datetime] = mapped_column(UTCDateTime, default=now)
    business_read_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    auditor_read_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    engagement: Mapped[Engagement] = relationship(back_populates="threads")
    messages: Mapped[list["Message"]] = relationship(back_populates="thread", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"
    thread_id: Mapped[str] = mapped_column(ForeignKey("threads.id", ondelete="CASCADE"), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)

    thread: Mapped[Thread] = relationship(back_populates="messages")
    sender: Mapped[User] = relationship()


class Notification(Base):
    __tablename__ = "notifications"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(20), default="info")  # critical|warning|info|success
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(String(255), default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    details: Mapped[str] = mapped_column(Text, default="")
    tone: Mapped[str] = mapped_column(String(10), default="info")  # success|warning|info

    actor: Mapped[User] = relationship()
    company: Mapped[Company] = relationship()


class AuditorReview(Base):
    __tablename__ = "auditor_reviews"
    engagement_id: Mapped[str] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), unique=True)
    rating: Mapped[int] = mapped_column(Integer)
    timeliness: Mapped[int] = mapped_column(Integer)
    communication: Mapped[int] = mapped_column(Integer)
    technical: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default="")

    engagement: Mapped[Engagement] = relationship(back_populates="review")
