"""Authentication routes - Register and Login."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User, UnitSystemEnum
from app.api.v1.auth import (
    get_current_user,
    get_password_hash,
    verify_password,
    create_access_token
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegister(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str
    full_name: str
    birth_date: Optional[str] = None
    biological_sex: Optional[str] = None
    height_cm: Optional[float] = None
    default_unit_system: UnitSystemEnum = UnitSystemEnum.METRIC


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    email: str
    full_name: str
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user.
    
    Creates a new user account with hashed password.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        birth_date=user_data.birth_date,
        biological_sex=user_data.biological_sex,
        height_cm=user_data.height_cm,
        default_unit_system=user_data.default_unit_system
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token.
    
    Validates credentials and returns JWT access token.
    """
    # Find user by email (username field from OAuth2 form)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
