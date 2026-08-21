"""Database seeders for initial catalog data (MetricCodes and UnitCodes)."""

import uuid
from sqlalchemy.orm import Session

from ..models.metric_code import MetricCode, MetricCategoryEnum
from ..models.unit_code import UnitCode, SystemTypeEnum
from ..models.skinfold_protocol import SkinfoldProtocol


def get_metric_codes_data():
    """Returns the 27 metric codes as per specification."""
    return [
        # Vitals (4)
        {"key": "weight_kg", "category": MetricCategoryEnum.VITALS.value, "is_bilateral": False},
        {"key": "resting_hr_bpm", "category": MetricCategoryEnum.VITALS.value, "is_bilateral": False},
        {"key": "bp_systolic_mmhg", "category": MetricCategoryEnum.VITALS.value, "is_bilateral": False},
        {"key": "bp_diastolic_mmhg", "category": MetricCategoryEnum.VITALS.value, "is_bilateral": False},
        
        # Circumferences (14) - all in cm
        {"key": "arm_right_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "arm_left_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "arm_right_contracted_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "arm_left_contracted_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "forearm_right_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "forearm_left_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "chest_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": False},
        {"key": "abdomen_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": False},
        {"key": "waist_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": False},
        {"key": "hip_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": False},
        {"key": "thigh_right_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "thigh_left_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "calf_right_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        {"key": "calf_left_cm", "category": MetricCategoryEnum.CIRCUMFERENCE.value, "is_bilateral": True},
        
        # Skinfolds (9) - all in mm (added bicipital to complete the list from spec)
        {"key": "tricipital_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "subscapular_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "mid_axillary_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "suprailiac_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "pectoral_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "abdominal_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "thigh_skinfold_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
        {"key": "bicipital_mm", "category": MetricCategoryEnum.SKINFOLD.value, "is_bilateral": False},
    ]


def get_unit_codes_data():
    """Returns unit codes with conversion factors to base units."""
    return [
        # Weight units (base: kg)
        {"key": "kg", "system_type": SystemTypeEnum.METRIC.value, "conversion_factor_to_base": 1.0},
        {"key": "lbs", "system_type": SystemTypeEnum.IMPERIAL.value, "conversion_factor_to_base": 0.453592},
        
        # Length units for circumferences (base: cm)
        {"key": "cm", "system_type": SystemTypeEnum.METRIC.value, "conversion_factor_to_base": 1.0},
        {"key": "in", "system_type": SystemTypeEnum.IMPERIAL.value, "conversion_factor_to_base": 2.54},
        
        # Length units for skinfolds (base: mm)
        {"key": "mm", "system_type": SystemTypeEnum.METRIC.value, "conversion_factor_to_base": 1.0},
        
        # Other units
        {"key": "bpm", "system_type": SystemTypeEnum.METRIC.value, "conversion_factor_to_base": 1.0},  # beats per minute
        {"key": "mmhg", "system_type": SystemTypeEnum.METRIC.value, "conversion_factor_to_base": 1.0},  # blood pressure
    ]


def get_skinfold_protocols_data():
    """Returns skinfold protocol definitions."""
    return [
        {
            "name": "Jackson-Pollock 7-site",
            "formula_key": "JACKSON_POLLOCK_7",
            "required_sites": [
                "pectoral_mm",
                "mid_axillary_mm",
                "tricipital_mm",
                "subscapular_mm",
                "abdominal_mm",
                "suprailiac_mm",
                "thigh_skinfold_mm",
            ],
        },
        {
            "name": "Jackson-Pollock 3-site",
            "formula_key": "JACKSON_POLLOCK_3",
            "required_sites": [
                "pectoral_mm",
                "abdominal_mm",
                "thigh_skinfold_mm",
            ],
        },
    ]


def seed_metric_codes(db: Session):
    """Seed metric codes catalog."""
    existing_keys = {mc.key for mc in db.query(MetricCode.key).all()}
    
    for data in get_metric_codes_data():
        if data["key"] not in existing_keys:
            metric_code = MetricCode(
                id=uuid.uuid4(),
                key=data["key"],
                category=data["category"],
                is_bilateral=data["is_bilateral"],
            )
            db.add(metric_code)
            print(f"Added MetricCode: {data['key']}")
    
    db.commit()
    print("Metric codes seeding completed.")


def seed_unit_codes(db: Session):
    """Seed unit codes catalog."""
    existing_keys = {uc.key for uc in db.query(UnitCode.key).all()}
    
    for data in get_unit_codes_data():
        if data["key"] not in existing_keys:
            unit_code = UnitCode(
                id=uuid.uuid4(),
                key=data["key"],
                system_type=data["system_type"],
                conversion_factor_to_base=data["conversion_factor_to_base"],
            )
            db.add(unit_code)
            print(f"Added UnitCode: {data['key']}")
    
    db.commit()
    print("Unit codes seeding completed.")


def seed_skinfold_protocols(db: Session):
    """Seed skinfold protocols."""
    existing_names = {sp.name for sp in db.query(SkinfoldProtocol.name).all()}
    
    for data in get_skinfold_protocols_data():
        if data["name"] not in existing_names:
            protocol = SkinfoldProtocol(
                id=uuid.uuid4(),
                name=data["name"],
                formula_key=data["formula_key"],
                required_sites=data["required_sites"],
            )
            db.add(protocol)
            print(f"Added SkinfoldProtocol: {data['name']}")
    
    db.commit()
    print("Skinfold protocols seeding completed.")


def run_all_seeders(db: Session):
    """Run all seeders in order."""
    print("Starting database seeding...")
    seed_unit_codes(db)
    seed_metric_codes(db)
    seed_skinfold_protocols(db)
    print("All seeders completed successfully!")
