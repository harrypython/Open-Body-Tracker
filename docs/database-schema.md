# Database Schema Documentation

## Overview

This document describes the database schema for Open Body Tracker, implemented using SQLAlchemy ORM with PostgreSQL.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│    User     │───────│  Assessment  │───────│  Measurement │
└─────────────┘       └──────────────┘       └──────────────┘
                            │                      │
                            │                      ├── MetricCode (catalog)
                            │                      │
                            │                      └── UnitCode (catalog)
                            │
                            ├── Photo
                            │
                            └── SkinfoldProtocol (catalog)
```

## Tables

### 1. Users (`users`)

Stores user authentication and profile information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| full_name | VARCHAR(255) | NOT NULL | User's full name |
| birth_date | DATE | NULLABLE | Date of birth |
| biological_sex | VARCHAR(50) | NULLABLE | Biological sex |
| height_cm | FLOAT | NULLABLE | Height in centimeters (base unit) |
| default_unit_system | ENUM | DEFAULT 'METRIC' | METRIC or IMPERIAL |
| created_at | TIMESTAMP | DEFAULT now() | Account creation timestamp |

**Relationships:**
- One-to-Many with `Assessment` (cascade delete)

---

### 2. Metric Codes (`metric_codes`)

Catalog of all 26 trackable metrics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique metric identifier |
| key | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Metric key (e.g., 'weight_kg', 'arm_right_cm') |
| category | VARCHAR(50) | NOT NULL | VITALS, CIRCUMFERENCE, or SKINFOLD |
| is_bilateral | BOOLEAN | DEFAULT FALSE | True if metric has left/right variants |

**Metrics Catalog (26 total):**

**Vitals (4):**
- `weight_kg`
- `resting_hr_bpm`
- `bp_systolic_mmhg`
- `bp_diastolic_mmhg`

**Circumferences (14):**
- `arm_right_cm`, `arm_left_cm`
- `arm_right_contracted_cm`, `arm_left_contracted_cm`
- `forearm_right_cm`, `forearm_left_cm`
- `chest_cm`
- `abdomen_cm`
- `waist_cm`
- `hip_cm`
- `thigh_right_cm`, `thigh_left_cm`
- `calf_right_cm`, `calf_left_cm`

**Skinfolds (8):**
- `tricipital_mm`
- `subscapular_mm`
- `mid_axillary_mm`
- `suprailiac_mm`
- `pectoral_mm`
- `abdominal_mm`
- `thigh_skinfold_mm`
- `bicipital_mm`

**Relationships:**
- One-to-Many with `Measurement`

---

### 3. Unit Codes (`unit_codes`)

Catalog of measurement units with conversion factors.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique unit identifier |
| key | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Unit key (e.g., 'kg', 'cm', 'mm', 'lbs', 'in') |
| system_type | VARCHAR(50) | NOT NULL | METRIC or IMPERIAL |
| conversion_factor_to_base | FLOAT | NOT NULL | Factor to convert to base unit |

**Units Catalog:**

| Key | System | Base Unit | Conversion Factor |
|-----|--------|-----------|-------------------|
| kg | METRIC | kg | 1.0 |
| lbs | IMPERIAL | kg | 0.453592 |
| cm | METRIC | cm | 1.0 |
| in | IMPERIAL | cm | 2.54 |
| mm | METRIC | mm | 1.0 |
| bpm | METRIC | bpm | 1.0 |
| mmhg | METRIC | mmhg | 1.0 |

**Base Units:**
- Weight: kg
- Circumference: cm
- Skinfold: mm

**Relationships:**
- One-to-Many with `Measurement`

---

### 4. Assessments (`assessments`)

Represents a single body assessment session.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique assessment identifier |
| user_id | UUID | FOREIGN KEY → users.id, INDEX, NOT NULL | Owner of the assessment |
| assessment_date | DATE | NOT NULL, INDEX | Date of the assessment |
| notes | VARCHAR(1000) | NULLABLE | Optional notes |
| protocol_used | VARCHAR(100) | NULLABLE | e.g., 'JACKSON_POLLOCK_7' |
| created_at | TIMESTAMP | DEFAULT now() | Creation timestamp |

**Relationships:**
- Many-to-One with `User`
- One-to-Many with `Measurement` (cascade delete)
- One-to-Many with `Photo` (cascade delete)

---

### 5. Measurements (`measurements`)

Individual measurement records linked to an assessment.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique measurement identifier |
| assessment_id | UUID | FOREIGN KEY → assessments.id, INDEX, NOT NULL | Parent assessment |
| metric_code_id | UUID | FOREIGN KEY → metric_codes.id, INDEX, NOT NULL | Metric being measured |
| unit_code_id | UUID | FOREIGN KEY → unit_codes.id, NOT NULL | Unit of measurement |
| value_raw | FLOAT | NOT NULL | **Always stored in base unit** |
| side | ENUM | DEFAULT 'NONE' | RIGHT, LEFT, or NONE |

**Relationships:**
- Many-to-One with `Assessment`
- Many-to-One with `MetricCode`
- Many-to-One with `UnitCode`

---

### 6. Skinfold Protocols (`skinfold_protocols`)

Defines skinfold measurement protocols.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique protocol identifier |
| name | VARCHAR(255) | UNIQUE, NOT NULL | e.g., 'Jackson-Pollock 7-site' |
| formula_key | VARCHAR(100) | NOT NULL | Key to lookup calculation formula |
| required_sites | JSON | NOT NULL | Array of required metric keys |

**Protocols:**

**Jackson-Pollock 7-site:**
- Required sites: `pectoral_mm`, `mid_axillary_mm`, `tricipital_mm`, `subscapular_mm`, `abdominal_mm`, `suprailiac_mm`, `thigh_skinfold_mm`

**Jackson-Pollock 3-site:**
- Required sites: `pectoral_mm`, `abdominal_mm`, `thigh_skinfold_mm`

---

### 7. Photos (`photos`)

Stores uploaded photos for assessments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique photo identifier |
| assessment_id | UUID | FOREIGN KEY → assessments.id, INDEX, NOT NULL | Parent assessment |
| file_path | VARCHAR(500) | NOT NULL | Path to stored photo file |
| angle | ENUM | NOT NULL | FRONT, SIDE, or BACK |
| uploaded_at | TIMESTAMP | DEFAULT now() | Upload timestamp |

**Relationships:**
- Many-to-One with `Assessment`

---

## Enums

### UnitSystemEnum
- `METRIC`
- `IMPERIAL`

### MetricCategoryEnum
- `VITALS`
- `CIRCUMFERENCE`
- `SKINFOLD`

### SideEnum
- `RIGHT`
- `LEFT`
- `NONE`

### PhotoAngleEnum
- `FRONT`
- `SIDE`
- `BACK`

---

## Design Principles

### 1. Base Unit Storage
All measurements are stored in their base units:
- Weight: **kg**
- Circumference: **cm**
- Skinfold: **mm**

Conversion to/from user-preferred units happens at the application layer.

### 2. Data Isolation
All assessments are scoped to `user_id`, ensuring complete data isolation between users.

### 3. Cascade Deletes
- Deleting a user cascades to all their assessments
- Deleting an assessment cascades to all measurements and photos

### 4. Catalog Pattern
Metric codes and unit codes are stored as catalog tables, allowing for:
- Easy extension of supported metrics
- Internationalization support
- Consistent validation

### 5. UUID Primary Keys
All tables use UUID primary keys for:
- Better security (non-sequential IDs)
- Easier data portability
- No information leakage about record counts

---

## Seeder Script

The database includes a seeder script (`app/core/seeders.py`) that populates:
- 7 unit codes
- 26 metric codes
- 2 skinfold protocols

Run the seeder via the API:
```bash
POST /seed
```

Or programmatically:
```python
from app.core.seeders import run_all_seeders
run_all_seeders(db_session)
```

---

## Migration Strategy

For production deployments, use Alembic for schema migrations:

```bash
# Initialize alembic (one-time)
alembic init alembic

# Create new migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

For development, tables are auto-created on application startup via:
```python
Base.metadata.create_all(bind=engine)
```
