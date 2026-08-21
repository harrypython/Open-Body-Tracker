"""User model for authentication and profile management."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Float, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class UnitSystemEnum(str, enum.Enum):
    """Unit system preference for the user."""
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


class User(Base):
    """User model for storing user profile and authentication data."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    biological_sex = Column(String(50), nullable=True)  # Could be enum if needed
    height_cm = Column(Float, nullable=True)  # Stored in cm (base unit)
    default_unit_system = Column(Enum(UnitSystemEnum), default=UnitSystemEnum.METRIC)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    
    # Relationships
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
