from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"
    RATE_LIMIT_AUTH_PER_MIN: int = 5
    RATE_LIMIT_API_PER_MIN: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
