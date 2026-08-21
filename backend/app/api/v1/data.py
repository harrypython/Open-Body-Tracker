"""Data export and import routes."""

import csv
import io
import tempfile
import os
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from appdatabase import get_db
from appmodels.user import User
from appmodels.assessment import Assessment
from appmodels.measurement import Measurement
from appmodels.metric_code import MetricCode
from appmodels.unit_code import UnitCode
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/data", tags=["Data"])


class ImportPreviewRow(BaseModel):
    """Preview row for CSV import."""
    row_number: int
    is_valid: bool
    errors: List[str] = []
    data: dict = {}


class ImportPreviewResponse(BaseModel):
    """Response for CSV import preview."""
    total_rows: int
    valid_rows: int
    invalid_rows: int
    preview: List[ImportPreviewRow]


@router.get("/export")
async def export_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user history as CSV stream.
    
    Returns a downloadable CSV file with complete assessment history.
    """
    # Get all assessments for the user
    assessments = db.query(Assessment).filter(
        Assessment.user_id == current_user.id
    ).order_by(Assessment.assessment_date.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    fieldnames = [
        "assessment_id",
        "assessment_date",
        "protocol_used",
        "notes",
        "metric_key",
        "value",
        "unit",
        "side"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Write data
    for assessment in assessments:
        for measurement in assessment.measurements:
            metric = measurement.metric_code
            unit = measurement.unit_code
            
            writer.writerow({
                "assessment_id": str(assessment.id),
                "assessment_date": assessment.assessment_date.isoformat(),
                "protocol_used": assessment.protocol_used or "",
                "notes": assessment.notes or "",
                "metric_key": metric.key if metric else "",
                "value": measurement.value_raw,
                "unit": unit.key if unit else "",
                "side": measurement.side.value if measurement.side else ""
            })
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=user_{current_user.id}_export.csv"
        }
    )


class ImportPreviewRow(BaseModel):
    """Preview row for CSV import."""
    row_number: int
    is_valid: bool
    errors: List[str] = []
    data: dict = {}


class ImportPreviewResponse(BaseModel):
    """Response for CSV import preview."""
    total_rows: int
    valid_rows: int
    invalid_rows: int
    preview: List[ImportPreviewRow]


@router.post("/import/preview", response_model=ImportPreviewResponse)
async def preview_csv_import(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview CSV import validation without committing.
    
    Validates CSV structure and shows which rows would succeed/fail.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    # Read and parse CSV
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))
        
        preview_rows = []
        valid_count = 0
        invalid_count = 0
        
        required_columns = ['assessment_date', 'metric_key', 'value']
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            errors = []
            
            # Check required columns
            for col in required_columns:
                if col not in row or not row[col]:
                    errors.append(f"Missing required column: {col}")
            
            # Validate date format
            if 'assessment_date' in row and row['assessment_date']:
                try:
                    date.fromisoformat(row['assessment_date'])
                except ValueError:
                    errors.append(f"Invalid date format: {row['assessment_date']}")
            
            # Validate value is numeric
            if 'value' in row and row['value']:
                try:
                    float(row['value'])
                except ValueError:
                    errors.append(f"Value must be numeric: {row['value']}")
            
            is_valid = len(errors) == 0
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
            
            preview_rows.append(ImportPreviewRow(
                row_number=row_num,
                is_valid=is_valid,
                errors=errors,
                data=dict(row)
            ))
            
            # Limit preview to first 100 rows
            if len(preview_rows) >= 100:
                break
        
        return ImportPreviewResponse(
            total_rows=len(preview_rows),
            valid_rows=valid_count,
            invalid_rows=invalid_count,
            preview=preview_rows
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing CSV: {str(e)}"
        )


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import CSV data with transactional commit.
    
    Validates entire file before committing any data.
    Rolls back on any error.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))
        
        # Parse all rows first (don't commit yet)
        assessments_to_create = {}  # key: (date, protocol) -> assessment data
        measurements_to_create = []
        
        required_columns = ['assessment_date', 'metric_key', 'value']
        
        for row_num, row in enumerate(reader, start=2):
            # Validate required columns
            for col in required_columns:
                if col not in row or not row[col]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Row {row_num}: Missing required column '{col}'"
                    )
            
            # Validate date
            try:
                assessment_date = date.fromisoformat(row['assessment_date'])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Row {row_num}: Invalid date format '{row['assessment_date']}'"
                )
            
            # Validate value
            try:
                value = float(row['value'])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Row {row_num}: Value must be numeric: '{row['value']}'"
                )
            
            # Get metric code
            metric_key = row['metric_key']
            metric = db.query(MetricCode).filter(MetricCode.key == metric_key).first()
            if not metric:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Row {row_num}: Unknown metric key '{metric_key}'"
                )
            
            # Get or create assessment key
            protocol = row.get('protocol_used', '')
            assessment_key = (assessment_date.isoformat(), protocol)
            
            if assessment_key not in assessments_to_create:
                assessments_to_create[assessment_key] = {
                    'date': assessment_date,
                    'protocol': protocol,
                    'notes': row.get('notes', '')
                }
            
            # Store measurement data
            measurements_to_create.append({
                'assessment_key': assessment_key,
                'metric_id': metric.id,
                'value': value,
                'unit_key': row.get('unit', 'kg'),  # Default to kg
                'side': row.get('side', 'NONE')
            })
        
        # Now create everything in a transaction
        assessment_map = {}  # key -> assessment ID
        
        for key, data in assessments_to_create.items():
            assessment = Assessment(
                user_id=current_user.id,
                assessment_date=data['date'],
                protocol_used=data['protocol'] if data['protocol'] else None,
                notes=data['notes'] if data['notes'] else None
            )
            db.add(assessment)
            db.flush()
            assessment_map[key] = assessment.id
        
        # Create measurements
        unit_map = {u.key: u.id for u in db.query(UnitCode).all()}
        
        for meas_data in measurements_to_create:
            unit_id = unit_map.get(meas_data['unit_key'])
            if not unit_id:
                unit_id = unit_map.get('kg')  # Fallback
            
            side_value = meas_data.get('side', 'NONE')
            try:
                from appmodels.measurement import SideEnum
                side = SideEnum(side_value)
            except ValueError:
                side = SideEnum.NONE
            
            measurement = Measurement(
                assessment_id=assessment_map[meas_data['assessment_key']],
                metric_code_id=meas_data['metric_id'],
                unit_code_id=unit_id,
                value_raw=meas_data['value'],
                side=side
            )
            db.add(measurement)
        
        db.commit()
        
        return {
            "message": "CSV imported successfully",
            "assessments_created": len(assessments_to_create),
            "measurements_created": len(measurements_to_create)
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import failed: {str(e)}"
        )
