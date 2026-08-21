"""MetricCode model - Catalog of all trackable metrics."""

import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class MetricCategoryEnum(str, enum.Enum):
    """Categories for metrics."""
    VITALS = "VITALS"
    CIRCUMFERENCE = "CIRCUMFERENCE"
    SKINFOLD = "SKINFOLD"


class MetricCode(Base):
    """Catalog of all trackable metrics (27 metrics total)."""
    
    __tablename__ = "metric_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False, index=True)  # e.g., 'weight_kg', 'arm_right_cm'
    category = Column(String(50), nullable=False)  # vitals, circumference, skinfold
    is_bilateral = Column(Boolean, default=False)  # True if metric has left/right variants
    
    # Relationships
    measurements = relationship("Measurement", back_populates="metric_code")
    
    def __repr__(self):
        return f"<MetricCode(key={self.key}, category={self.category})>"
