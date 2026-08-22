"""Assessment routes - Create, read, and manage body assessments."""

import uuid
import os
import shutil
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field, field_validator, model_serializer
from typing import Any
from uuid import UUID

from ...database import get_db
from ...models.user import User
from ...models.assessment import Assessment
from ...models.measurement import Measurement, SideEnum
from ...models.metric_code import MetricCode
from ...models.unit_code import UnitCode
from ...models.photo import Photo, PhotoAngleEnum
from ...services.body_composition_calculator import BodyCompositionCalculator, Sex
from ...services.unit_converter import UnitConverter
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/assessments", tags=["Assessments"])


# Request/Response Models
class VitalsInput(BaseModel):
    """Vitals input model."""
    weight: float  # in kg or lbs (will be converted)
    resting_hr: Optional[int] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None


class CircumferencesInput(BaseModel):
    """Circumferences input model."""
    arm_right: Optional[float] = None
    arm_left: Optional[float] = None
    arm_right_contracted: Optional[float] = None
    arm_left_contracted: Optional[float] = None
    forearm_right: Optional[float] = None
    forearm_left: Optional[float] = None
    chest: Optional[float] = None
    abdomen: Optional[float] = None
    waist: Optional[float] = None
    hip: Optional[float] = None
    thigh_right: Optional[float] = None
    thigh_left: Optional[float] = None
    calf_right: Optional[float] = None
    calf_left: Optional[float] = None


class SkinfoldsInput(BaseModel):
    """Skinfolds input model."""
    pectoral: Optional[float] = None
    mid_axillary: Optional[float] = None
    tricipital: Optional[float] = None
    subscapular: Optional[float] = None
    abdominal: Optional[float] = None
    suprailiac: Optional[float] = None
    thigh_skinfold: Optional[float] = None
    bicipital: Optional[float] = None


class AssessmentCreate(BaseModel):
    """Assessment creation model."""
    assessment_date: date
    vitals: VitalsInput
    circumferences: CircumferencesInput
    skinfolds: SkinfoldsInput
    protocol_used: str = "JACKSON_POLLOCK_7"
    notes: Optional[str] = None


class MeasurementResponse(BaseModel):
    """Measurement response model."""
    id: UUID
    metric_code_key: str
    value_raw: float
    unit_code_key: str
    side: Optional[str] = None

    class Config:
        from_attributes = True
    
    @model_serializer
    def serialize_model(self):
        return {
            "id": self.id,
            "metric_code_key": self.metric_code_key,
            "value_raw": self.value_raw,
            "unit_code_key": self.unit_code_key,
            "side": self.side
        }


class AssessmentResponse(BaseModel):
    """Assessment response model."""
    id: UUID
    user_id: UUID
    assessment_date: date
    notes: Optional[str] = None
    protocol_used: Optional[str] = None
    created_at: datetime
    measurements: List[MeasurementResponse] = []
    
    class Config:
        from_attributes = True


def _measurement_to_response(measurement: Measurement) -> MeasurementResponse:
    """Convert a Measurement ORM object to MeasurementResponse DTO.
    
    This extracts the key strings from related MetricCode and UnitCode objects.
    """
    return MeasurementResponse(
        id=measurement.id,
        metric_code_key=measurement.metric_code.key if measurement.metric_code else "",
        value_raw=measurement.value_raw,
        unit_code_key=measurement.unit_code.key if measurement.unit_code else "",
        side=measurement.side.value if measurement.side else None
    )


# Helper functions
def _get_metric_key_to_id_map(db: Session) -> Dict[str, uuid.UUID]:
    """Get mapping of metric keys to their IDs."""
    metrics = db.query(MetricCode).all()
    return {m.key: m.id for m in metrics}


def _get_unit_key_to_id_map(db: Session) -> Dict[str, uuid.UUID]:
    """Get mapping of unit keys to their IDs."""
    units = db.query(UnitCode).all()
    return {u.key: u.id for u in units}


def _validate_jackson_pollock_7_skinfolds(skinfolds: SkinfoldsInput):
    """Validate that all required skinfolds for Jackson-Pollock 7-site are present."""
    required_sites = [
        "pectoral",
        "mid_axillary",
        "tricipital",
        "subscapular",
        "abdominal",
        "suprailiac",
        "thigh_skinfold"
    ]
    
    missing = []
    for site in required_sites:
        value = getattr(skinfolds, site, None)
        if value is None:
            missing.append(site)
    
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required skinfold sites for Jackson-Pollock 7-site protocol: {', '.join(missing)}"
        )


@router.post("/new", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new body assessment.
    
    Converts units, validates Jackson-Pollock 7-site skinfolds,
    saves to database, and calculates derived metrics.
    """
    # Get metric and unit mappings
    metric_map = _get_metric_key_to_id_map(db)
    unit_map = _get_unit_key_to_id_map(db)

    # Ensure required metric and unit keys exist; otherwise instruct seeding
    required_metrics = [
        "weight_kg",
        "resting_hr_bpm",
        "bp_systolic_mmhg",
        "bp_diastolic_mmhg",
        "arm_right_cm",
        "arm_left_cm",
        "arm_right_contracted_cm",
        "arm_left_contracted_cm",
        "forearm_right_cm",
        "forearm_left_cm",
        "chest_cm",
        "abdomen_cm",
        "waist_cm",
        "hip_cm",
        "thigh_right_cm",
        "thigh_left_cm",
        "calf_right_cm",
        "calf_left_cm",
        "pectoral_mm",
        "mid_axillary_mm",
        "tricipital_mm",
        "subscapular_mm",
        "abdominal_mm",
        "suprailiac_mm",
        "thigh_skinfold_mm",
        "bicipital_mm",
    ]
    required_units = ["kg", "bpm", "mmhg", "cm", "mm"]

    missing_metrics = [m for m in required_metrics if m not in metric_map]
    missing_units = [u for u in required_units if u not in unit_map]
    if missing_metrics or missing_units:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Database missing metric or unit definitions. Run the /seed endpoint to initialize required data."
                if not missing_metrics else
                f"Missing metrics: {', '.join(missing_metrics)}"
                if not missing_units else
                f"Missing units: {', '.join(missing_units)}"
            )
        )

    # Validate Jackson-Pollock 7-site if that protocol is used
    if assessment_data.protocol_used == "JACKSON_POLLOCK_7":
        _validate_jackson_pollock_7_skinfolds(assessment_data.skinfolds)
    # Create assessment record
    new_assessment = Assessment(
        user_id=current_user.id,
        assessment_date=assessment_data.assessment_date,
        notes=assessment_data.notes,
        protocol_used=assessment_data.protocol_used
    )
    
    db.add(new_assessment)
    db.flush()  # Get the assessment ID
    
    measurements_to_add = []
    
    # Process vitals
    vitals = assessment_data.vitals
    
    # Weight (convert to kg if needed)
    if hasattr(vitals, 'weight') and vitals.weight is not None:
        weight_kg = vitals.weight  # Assuming input is already in kg (base unit)
        measurements_to_add.append(Measurement(
            assessment_id=new_assessment.id,
            metric_code_id=metric_map.get("weight_kg"),
            unit_code_id=unit_map.get("kg"),
            value_raw=weight_kg,
            side=SideEnum.NONE
        ))
    
    # Resting heart rate
    if vitals.resting_hr is not None:
        measurements_to_add.append(Measurement(
            assessment_id=new_assessment.id,
            metric_code_id=metric_map.get("resting_hr_bpm"),
            unit_code_id=unit_map.get("bpm"),
            value_raw=float(vitals.resting_hr),
            side=SideEnum.NONE
        ))
    
    # Blood pressure
    if vitals.bp_systolic is not None:
        measurements_to_add.append(Measurement(
            assessment_id=new_assessment.id,
            metric_code_id=metric_map.get("bp_systolic_mmhg"),
            unit_code_id=unit_map.get("mmhg"),
            value_raw=float(vitals.bp_systolic),
            side=SideEnum.NONE
        ))
    
    if vitals.bp_diastolic is not None:
        measurements_to_add.append(Measurement(
            assessment_id=new_assessment.id,
            metric_code_id=metric_map.get("bp_diastolic_mmhg"),
            unit_code_id=unit_map.get("mmhg"),
            value_raw=float(vitals.bp_diastolic),
            side=SideEnum.NONE
        ))
    
    # Process circumferences (all in cm - base unit)
    circumferences = assessment_data.circumferences
    circumference_mapping = {
        "arm_right": ("arm_right_cm", SideEnum.RIGHT),
        "arm_left": ("arm_left_cm", SideEnum.LEFT),
        "arm_right_contracted": ("arm_right_contracted_cm", SideEnum.RIGHT),
        "arm_left_contracted": ("arm_left_contracted_cm", SideEnum.LEFT),
        "forearm_right": ("forearm_right_cm", SideEnum.RIGHT),
        "forearm_left": ("forearm_left_cm", SideEnum.LEFT),
        "chest": ("chest_cm", SideEnum.NONE),
        "abdomen": ("abdomen_cm", SideEnum.NONE),
        "waist": ("waist_cm", SideEnum.NONE),
        "hip": ("hip_cm", SideEnum.NONE),
        "thigh_right": ("thigh_right_cm", SideEnum.RIGHT),
        "thigh_left": ("thigh_left_cm", SideEnum.LEFT),
        "calf_right": ("calf_right_cm", SideEnum.RIGHT),
        "calf_left": ("calf_left_cm", SideEnum.LEFT),
    }
    
    for field_name, (metric_key, side) in circumference_mapping.items():
        value = getattr(circumferences, field_name, None)
        if value is not None and metric_key in metric_map:
            measurements_to_add.append(Measurement(
                assessment_id=new_assessment.id,
                metric_code_id=metric_map.get(metric_key),
                unit_code_id=unit_map.get("cm"),
                value_raw=value,
                side=side
            ))
    
    # Process skinfolds (all in mm - base unit)
    skinfolds = assessment_data.skinfolds
    skinfold_mapping = {
        "pectoral": "pectoral_mm",
        "mid_axillary": "mid_axillary_mm",
        "tricipital": "tricipital_mm",
        "subscapular": "subscapular_mm",
        "abdominal": "abdominal_mm",
        "suprailiac": "suprailiac_mm",
        "thigh_skinfold": "thigh_skinfold_mm",
        "bicipital": "bicipital_mm",
    }
    
    for field_name, metric_key in skinfold_mapping.items():
        value = getattr(skinfolds, field_name, None)
        if value is not None and metric_key in metric_map:
            measurements_to_add.append(Measurement(
                assessment_id=new_assessment.id,
                metric_code_id=metric_map.get(metric_key),
                unit_code_id=unit_map.get("mm"),
                value_raw=value,
                side=SideEnum.NONE
            ))
    
    # Add all measurements
    for measurement in measurements_to_add:
        db.add(measurement)
    
    db.commit()
    db.refresh(new_assessment)
    
    # Load measurements with their related metric_code and unit_code for response
    assessment_with_measurements = db.query(Assessment).options(
        joinedload(Assessment.measurements).joinedload(Measurement.metric_code),
        joinedload(Assessment.measurements).joinedload(Measurement.unit_code)
    ).filter(Assessment.id == new_assessment.id).first()
    
    # Manually construct response to handle nested relationships
    return {
        "id": assessment_with_measurements.id,
        "user_id": assessment_with_measurements.user_id,
        "assessment_date": assessment_with_measurements.assessment_date,
        "notes": assessment_with_measurements.notes,
        "protocol_used": assessment_with_measurements.protocol_used,
        "created_at": assessment_with_measurements.created_at,
        "measurements": [_measurement_to_response(m) for m in assessment_with_measurements.measurements]
    }


@router.get("/history", response_model=List[AssessmentResponse])
async def get_assessments_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's assessment history as time series optimized for charts.
    
    Returns assessments ordered by date, with loading time < 2s.
    """
    assessments = db.query(Assessment).options(
        joinedload(Assessment.measurements).joinedload(Measurement.metric_code),
        joinedload(Assessment.measurements).joinedload(Measurement.unit_code)
    ).filter(
        Assessment.user_id == current_user.id
    ).order_by(Assessment.assessment_date.desc()).all()
    
    # Manually construct response to handle nested relationships
    return [{
        "id": a.id,
        "user_id": a.user_id,
        "assessment_date": a.assessment_date,
        "notes": a.notes,
        "protocol_used": a.protocol_used,
        "created_at": a.created_at,
        "measurements": [_measurement_to_response(m) for m in a.measurements]
    } for a in assessments]


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete details of a specific assessment."""
    assessment = db.query(Assessment).options(
        joinedload(Assessment.measurements).joinedload(Measurement.metric_code),
        joinedload(Assessment.measurements).joinedload(Measurement.unit_code)
    ).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Manually construct response to handle nested relationships
    return {
        "id": assessment.id,
        "user_id": assessment.user_id,
        "assessment_date": assessment.assessment_date,
        "notes": assessment.notes,
        "protocol_used": assessment.protocol_used,
        "created_at": assessment.created_at,
        "measurements": [_measurement_to_response(m) for m in assessment.measurements]
    }


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an assessment."""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    db.delete(assessment)
    db.commit()
    
    return None
