from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, Base, get_db
from .core.seeders import run_all_seeders
from .api.v1 import auth_router, user_router, assessments_router, data_router, metrics_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Open Body Tracker API",
    description="Self-hosted platform for longitudinal tracking of anthropometric data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(assessments_router, prefix="/api/v1")
app.include_router(data_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Open Body Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/seed")
async def seed_database(db: Session = Depends(get_db)):
    """Seed the database with initial catalog data.
    
    This endpoint populates the database with:
    - Unit codes (kg, lbs, cm, in, mm, bpm, mmhg)
    - Metric codes (27 metrics: vitals, circumferences, skinfolds)
    - Skinfold protocols (Jackson-Pollock 7-site, 3-site)
    """
    try:
        run_all_seeders(db)
        return {"message": "Database seeded successfully"}
    except Exception as e:
        return {"error": str(e)}
