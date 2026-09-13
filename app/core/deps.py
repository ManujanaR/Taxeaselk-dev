from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import AuditorProfile, Company, Engagement, LIVE_ENGAGEMENT_STATUSES, User

COOKIE_NAME = "taxease_session"


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth = request.headers.get("authorization", "")
        token = auth[7:] if auth.lower().startswith("bearer ") else None
    payload = decode_access_token(token) if token else None
    user = db.get(User, payload["sub"]) if payload else None
    if not user or not user.is_active:
        raise HTTPException(401, "Not authenticated")
    return user


def require_role(role: str):
    def dep(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(403, f"{role} role required")
        return user
    return dep


def current_company(user: User = Depends(require_role("business"))) -> Company:
    return user.company


def current_auditor(user: User = Depends(require_role("auditor"))) -> AuditorProfile:
    return user.auditor_profile


def live_engagement(db: Session, company_id: str) -> Engagement | None:
    return (
        db.query(Engagement)
        .filter(Engagement.company_id == company_id, Engagement.status.in_(LIVE_ENGAGEMENT_STATUSES))
        .first()
    )


def engagement_for_auditor(engagement_id: str, auditor: AuditorProfile, db: Session) -> Engagement:
    eng = db.get(Engagement, engagement_id)
    if not eng or eng.auditor_id != auditor.id:
        raise HTTPException(404, "Engagement not found")
    return eng
