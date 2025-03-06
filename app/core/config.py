from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nigeria Retail Economics API"
    API_V1_STR: str = "/api/v1"

    # Allowed Origins
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Environment
    ENVIRONMENT: str
    DEBUG: bool

    # BigQuery Settings
    GOOGLE_CLOUD_PROJECT: str
    BIGQUERY_DATASET: str

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TTL: int = 3600  # Cache TTL in seconds

    # MongoDB Settings
    MONGODB_URI: str = "mongodb+srv://rc-ai-lab:j9NQ9s78T2UAxZ@rc-cluster0.r1day.mongodb.net/"
    MONGODB_DB: str = "nigeria_unit_economics"

    class Config:
        env_file = ".env"


settings = Settings()
