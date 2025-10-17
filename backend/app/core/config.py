"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 9000
    API_CORS_ORIGINS: str = "http://localhost:9010,http://localhost:3000"
    
    # AI Services
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    OPENAI_MODEL: str = "gemini-2.0-flash"  # Using Gemini Flash for vision analysis
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Runware AI Configuration
    RUNWARE_API_KEY: str = "your_runware_api_key_here"
    RUNWARE_TIMEOUT: int = 30
    RUNWARE_MAX_RETRIES: int = 3
    RUNWARE_BASE_URL: str = "https://api.runware.com"
    
    # Service Management
    PRIMARY_IMAGE_PROVIDER: str = "runware"
    FALLBACK_IMAGE_PROVIDERS: str = "gemini"
    SERVICE_HEALTH_CHECK_INTERVAL: int = 60
    SERVICE_ROUTING_STRATEGY: str = "primary_first"  # primary_first, round_robin, least_loaded, cost_optimized, quality_focused, health_based
    
    # Firebase
    GOOGLE_APPLICATION_CREDENTIALS: str = "./firebase-credentials.json"
    FIREBASE_PROJECT_ID: str
    FIREBASE_STORAGE_BUCKET: str
    
    # Firestore Collections
    COLLECTION_USERS: str = "users"
    COLLECTION_PLANS: str = "plans"
    COLLECTION_INPUTS: str = "user_inputs"
    COLLECTION_VENDORS: str = "vendors"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Pinterest Scraping
    PINTEREST_SCRAPING_STRATEGY: str = "api_endpoint,html_scrape,playwright_render"
    PINTEREST_TIMEOUT_SECONDS: int = 30
    PINTEREST_MAX_RETRIES: int = 3
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 500
    
    # Storage
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_FORMATS: str = "image/jpeg,image/png,image/webp"
    USE_LOCAL_STORAGE: bool = True  # Set to False to use Firebase Storage
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

