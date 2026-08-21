"""Photo model - Stores uploaded photos for assessments."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class PhotoAngleEnum(str, enum.Enum):
    """Photo angles for body assessment."""
    FRONT = "FRONT"
    SIDE = "SIDE"
    BACK = "BACK"


class Photo(Base):
    """Photo model for storing uploaded body photos."""
    
    __tablename__ = "photos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)  # Path to stored photo
    angle = Column(Enum(PhotoAngleEnum), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="photos")
    
    def __repr__(self):
        return f"<Photo(id={self.id}, assessment_id={self.assessment_id}, angle={self.angle})>"
