from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://obtracker:obtracker@db:5432/open_body_tracker"
    
    # Security
    secret_key: str = "your-secret-key-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Storage
    photo_storage_path: str = "/app/photos"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
