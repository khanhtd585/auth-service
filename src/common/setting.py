from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """
    Include all settings from environment variables
    """
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PW: str
    DB_NAME: str
    
    # Service
    HOST: str
    PORT: int
    DEBUG_MODE: bool = False
    SERVICE_NAME: str = 'auth_service'
    
    # Auth Token
    PEPPER: str = 'pepsi'
    
    # JWT / token
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_SECONDS: int = 900  # 15m
    REFRESH_TOKEN_EXPIRES_DAY: int = 7  # 30 days
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0  # 15m
    DECODE_RESPONSES: bool = True
    TOKEN_TTL_MIN: int = 1




@lru_cache
def get_settings() -> Settings:
    """
    Function to get 'Settings' instance.
    Use 'lru_cache' so that 'Settings' is created only once
    """
    return Settings()
