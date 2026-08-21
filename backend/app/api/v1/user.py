"""User profile routes."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

from app.database import get_db
from app.models.user import User, UnitSystemEnum
from app.api.v1.auth import get_current_user, get_password_hash, verify_password

router = APIRouter(prefix="/user", tags=["User"])


class UserProfileResponse(BaseModel):
    """User profile response model."""
    id: UUID
    email: str
    full_name: str
    birth_date: Optional[date] = None
    biological_sex: Optional[str] = None
    height_cm: Optional[float] = None
    default_unit_system: UnitSystemEnum
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update model."""
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    biological_sex: Optional[str] = None
    height_cm: Optional[float] = None
    default_unit_system: Optional[UnitSystemEnum] = None


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get the current user's profile.
    
    Returns static user data including height for BMI calculations.
    """
    return current_user


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile.
    
    Updates static user data fields.
    """
    update_data = profile_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
