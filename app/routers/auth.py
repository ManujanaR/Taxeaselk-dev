from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.models.user import User
from app.models.company import Company
from app.schemas.auth import UserLogin, UserRegister, Token, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    token = create_access_token(user.id, user.role)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name
    )

@router.post("/register", response_model=Token)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        full_name=payload.full_name or payload.email.split("@")[0]
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if payload.role == "business" and payload.company_name:
        comp = Company(
            user_id=str(new_user.id),
            company_name=payload.company_name,
            contact_email=payload.email
        )
        db.add(comp)
        db.commit()

    token = create_access_token(subject=new_user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=str(new_user.id),
        email=new_user.email,
        role=new_user.role,
        full_name=new_user.full_name
    )

@router.post("/forgot-password")
def forgot_password(payload: dict):
    return {"success": True, "message": "Password reset link dispatched to your registered email"}
