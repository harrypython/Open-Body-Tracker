"""Metrics catalog routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from ...database import get_db
from ...models.user import User
from ...models.metric_code import MetricCode, MetricCategoryEnum
from ...models.unit_code import UnitCode
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class MetricCatalogEntry(BaseModel):
    """Metric catalog entry response model."""
    id: UUID
    key: str
    category: str
    is_bilateral: bool
    
    class Config:
        from_attributes = True


class UnitCatalogEntry(BaseModel):
    """Unit catalog entry response model."""
    id: UUID
    key: str
    system_type: str
    conversion_factor_to_base: float
    
    class Config:
        from_attributes = True


class MetricsCatalogResponse(BaseModel):
    """Complete metrics catalog response."""
    metrics: List[MetricCatalogEntry]
    units: List[UnitCatalogEntry]


@router.get("/catalog", response_model=MetricsCatalogResponse)
async def get_metrics_catalog(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the complete catalog of metrics and units for the frontend.
    
    Returns all available metric codes and unit codes that can be tracked.
    This allows the frontend to dynamically build forms and validation.
    """
    metrics = db.query(MetricCode).order_by(MetricCode.category, MetricCode.key).all()
    units = db.query(UnitCode).order_by(UnitCode.system_type, UnitCode.key).all()
    
    return MetricsCatalogResponse(
        metrics=[MetricCatalogEntry.model_validate(m) for m in metrics],
        units=[UnitCatalogEntry.model_validate(u) for u in units]
    )


@router.get("/catalog/metrics", response_model=List[MetricCatalogEntry])
async def get_metrics_list(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of metrics, optionally filtered by category.
    
    Args:
        category: Optional filter by category (VITALS, CIRCUMFERENCE, SKINFOLD)
    """
    query = db.query(MetricCode)
    
    if category:
        query = query.filter(MetricCode.category == category.upper())
    
    metrics = query.order_by(MetricCode.key).all()
    
    return [MetricCatalogEntry.model_validate(m) for m in metrics]


@router.get("/catalog/units", response_model=List[UnitCatalogEntry])
async def get_units_list(
    system_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of units, optionally filtered by system type.
    
    Args:
        system_type: Optional filter by system (METRIC, IMPERIAL)
    """
    query = db.query(UnitCode)
    
    if system_type:
        query = query.filter(UnitCode.system_type == system_type.upper())
    
    units = query.order_by(UnitCode.key).all()
    
    return [UnitCatalogEntry.model_validate(u) for u in units]
