from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    postgres_user: str = "obtracker"
    postgres_password: str = "obtracker_secure_password_change_me"
    postgres_db: str = "open_body_tracker"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    @property
    def database_url(self) -> str:
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
    
    class Config:
        case_sensitive = False


settings = Settings()
