"""SkinfoldProtocol model - Defines skinfold measurement protocols."""

import uuid
from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class SkinfoldProtocol(Base):
    """Skinfold protocol definition (e.g., Jackson-Pollock 7-site)."""
    
    __tablename__ = "skinfold_protocols"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)  # e.g., 'Jackson-Pollock 7-site'
    formula_key = Column(String(100), nullable=False)  # Key to lookup formula in calculation engine
    required_sites = Column(JSON, nullable=False)  # Array of required metric keys
    
    def __repr__(self):
        return f"<SkinfoldProtocol(name={self.name})>"


# Association table for protocol sites (if needed for more complex relationships)
skinfold_protocol_sites = None  # Using JSON column for simplicity
