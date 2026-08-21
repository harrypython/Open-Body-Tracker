"""Measurement model - Individual measurement records."""

import uuid
from sqlalchemy import Column, ForeignKey, Float, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class SideEnum(str, enum.Enum):
    """Side of the body for bilateral measurements."""
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    NONE = "NONE"  # For non-bilateral measurements


class Measurement(Base):
    """Individual measurement record linked to an assessment.
    
    value_raw is always stored in the base unit:
    - Weight: kg
    - Circumference: cm
    - Skinfold: mm
    """
    
    __tablename__ = "measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_code_id = Column(UUID(as_uuid=True), ForeignKey("metric_codes.id"), nullable=False, index=True)
    unit_code_id = Column(UUID(as_uuid=True), ForeignKey("unit_codes.id"), nullable=False)
    value_raw = Column(Float, nullable=False)  # Always stored in base unit
    side = Column(Enum(SideEnum), default=SideEnum.NONE)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="measurements")
    metric_code = relationship("MetricCode", back_populates="measurements")
    unit_code = relationship("UnitCode", back_populates="measurements")
    
    def __repr__(self):
        return f"<Measurement(id={self.id}, assessment_id={self.assessment_id}, metric={self.metric_code_id})>"
