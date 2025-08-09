import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ClarityCheck"
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Analysis Settings
    MAX_ANALYSIS_TIME: int = 30  # seconds
    CACHE_EXPIRY: int = 21600  # 6 hours
    
    # Playwright Settings
    PLAYWRIGHT_TIMEOUT: int = 30000  # ms
    VIEWPORT_WIDTH: int = 1920
    VIEWPORT_HEIGHT: int = 1080
    
    # Scoring Thresholds
    VISUAL_SCORE_WEIGHTS: dict = {
        "contrast": 0.3,
        "layout": 0.25,
        "cta_visibility": 0.25,
        "font_size": 0.2
    }
    
    TEXT_SCORE_WEIGHTS: dict = {
        "readability": 0.4,
        "structure": 0.3,
        "complexity": 0.3
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()