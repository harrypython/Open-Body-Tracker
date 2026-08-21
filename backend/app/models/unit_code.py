"""UnitCode model - Catalog of measurement units with conversion factors."""

import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from ..database import Base


class SystemTypeEnum(str, enum.Enum):
    """Unit system types."""
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


class UnitCode(Base):
    """Catalog of measurement units with conversion factors to base units.
    
    Base units:
    - Weight: kg
    - Length: cm
    - Skinfold: mm
    """
    
    __tablename__ = "unit_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'kg', 'cm', 'mm', 'lbs', 'in'
    system_type = Column(String(50), nullable=False)  # METRIC or IMPERIAL
    conversion_factor_to_base = Column(Float, nullable=False)  # Factor to convert to base unit
    
    # Relationships
    measurements = relationship("Measurement", back_populates="unit_code")
    
    def __repr__(self):
        return f"<UnitCode(key={self.key}, system_type={self.system_type})>"
