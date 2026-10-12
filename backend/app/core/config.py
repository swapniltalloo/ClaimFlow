import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    PROJECT_NAME: str = "ClaimFlow Clearinghouse"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://claimflow:claimflow_secret@localhost:5432/claimflow_db"
    )
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./claimflow_dev.db"
    USE_SQLITE_FALLBACK: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # SLA Budget in seconds (15-minute target = 900s)
    SLA_MAX_SECONDS: int = 900
    INGEST_BUDGET_SECONDS: int = 10
    PARSER_BUDGET_SECONDS: int = 45
    VALIDATION_BUDGET_SECONDS: int = 60
    FRAUD_BUDGET_SECONDS: int = 15
    DECISION_BUDGET_SECONDS: int = 30

    # Decision thresholds
    AUTO_SETTLE_RISK_THRESHOLD: float = 30.0
    HUMAN_REVIEW_RISK_THRESHOLD: float = 60.0
    SIU_ESCALATE_RISK_THRESHOLD: float = 85.0

    # Google Cloud & AI Settings
    GEMINI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    GCP_PROJECT_ID: str = "claimflow-prod"
    GCP_LOCATION: str = "asia-south1"
    GCP_DATASET_ID: str = "abdm-claims"
    GCP_FHIR_STORE_ID: str = "nhcx-store"
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
