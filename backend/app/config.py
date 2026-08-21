from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - supports both individual vars and DATABASE_URL
    database_url: Optional[str] = None
    postgres_user: str = "obtracker"
    postgres_password: str = "obtracker_secure_password_change_me"
    postgres_db: str = "open_body_tracker"
    postgres_host: str = "localhost"  # Default for local development; use 'db' for Docker
    postgres_port: int = 5432
    
    class Config:
        case_sensitive = False
        env_prefix = ""
    
    @property
    def database_url_resolved(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Security
    secret_key: str = "your-secret-key-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # File Storage
    photo_storage_path: str = "/app/photos"


settings = Settings()
