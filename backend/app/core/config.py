import os
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "SAPDO API"
    
    # Supabase settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL", "")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    model_config = {
        "env_file": ".env"
    }


settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings.
    
    Returns:
        The application settings
    """
    return settings
