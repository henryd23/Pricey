"""User registration and authentication routes."""

import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.app.database import get_session
from backend.app.models import User, UserRegister, UserLogin, UserRead, TokenResponse, utc_now
from backend.app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: UserRegister, session: Session = Depends(get_session)):
    """
    Registers a new Pricey user account (US-12).
    Validates input data and checks for email uniqueness.
    """
    clean_email = req.email.strip().lower()

    if not re.match(EMAIL_REGEX, clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato email non valido.",
        )

    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La password deve contenere almeno 6 caratteri.",
        )

    # US-12: Check if email already registered
    existing_user = session.exec(select(User).where(User.email == clean_email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esiste già un account registrato con questa email.",
        )

    hashed = hash_password(req.password)
    user = User(
        email=clean_email,
        hashed_password=hashed,
        full_name=req.full_name.strip() if req.full_name else None,
        is_active=True,
        created_at=utc_now(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticates a user and returns a JWT access token (US-13).
    """
    clean_email = req.email.strip().lower()
    user = session.exec(select(User).where(User.email == clean_email)).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide. Controlla email e password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Questo account è stato disattivato.",
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserRead)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
    )
