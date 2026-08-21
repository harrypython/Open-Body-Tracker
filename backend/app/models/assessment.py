"""Assessment model - Represents a single body assessment session."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Assessment(Base):
    """Assessment model representing a single measurement session for a user."""
    
    __tablename__ = "assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_date = Column(Date, nullable=False, index=True)
    notes = Column(String(1000), nullable=True)
    protocol_used = Column(String(100), nullable=True)  # e.g., 'JACKSON_POLLOCK_7'
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    measurements = relationship("Measurement", back_populates="assessment", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, user_id={self.user_id}, date={self.assessment_date})>"
