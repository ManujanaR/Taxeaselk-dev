from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import COOKIE_NAME, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AuditorProfile, Company, User
from app.schemas.auth import (
    ChangePasswordIn, LoginIn, RegisterAuditorIn, RegisterBusinessIn, SessionOut,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        COOKIE_NAME,
        create_access_token(user.id, user.role),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
        path="/",
    )


def _session(user: User) -> SessionOut:
    return SessionOut(user=user, company=user.company, auditor_profile=user.auditor_profile)


def _create_user(db: Session, email: str, password: str, full_name: str, role: str) -> User:
    if db.query(User).filter(User.email == email.lower()).first():
        raise HTTPException(409, "An account with this email already exists")
    user = User(email=email.lower(), password_hash=hash_password(password), full_name=full_name, role=role)
    db.add(user)
    db.flush()
    return user


@router.post("/register/business", response_model=SessionOut, status_code=201)
def register_business(payload: RegisterBusinessIn, response: Response, db: Session = Depends(get_db)):
    user = _create_user(db, payload.email, payload.password, payload.full_name, "business")
    db.add(Company(
        user_id=user.id, company_name=payload.company_name, tin_number=payload.tin_number,
        financial_year=payload.financial_year, industry_sector=payload.industry_sector,
        contact_email=user.email,
    ))
    db.commit()
    db.refresh(user)
    _set_cookie(response, user)
    return _session(user)


@router.post("/register/auditor", response_model=SessionOut, status_code=201)
def register_auditor(payload: RegisterAuditorIn, response: Response, db: Session = Depends(get_db)):
    user = _create_user(db, payload.email, payload.password, payload.full_name, "auditor")
    db.add(AuditorProfile(user_id=user.id, firm_name=payload.firm_name, license_number=payload.license_number))
    db.commit()
    db.refresh(user)
    _set_cookie(response, user)
    return _session(user)


@router.post("/login", response_model=SessionOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(401, "Invalid email or password")
    _set_cookie(response, user)
    return _session(user)


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=SessionOut)
def me(user: User = Depends(get_current_user)):
    return _session(user)


@router.post("/change-password", status_code=204)
def change_password(payload: ChangePasswordIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
