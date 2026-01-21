from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # Project metadata
    project_name: str = Field(default="Order Service", alias="PROJECT_NAME")
    version: str = Field(default="0.1.0", alias="VERSION")
    debug: bool = Field(default=True, alias="DEBUG")

    # Database configuration
    postgres_db: str = Field(default="order_service", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    # Redis configuration
    redis_host: str = Field(default="", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=1, alias="REDIS_DB")
    cache_ttl: int = Field(default=3600)
    decode_responses: bool = Field(default=True)

    # Database connection pool settings
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_url: str = Field(default="", alias="DATABASE_URL")

    # Application settings
    app_port: int = Field(default=8000, alias="APP_PORT")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json")

    # Catalog service settings
    api_catalog_service: str = Field(default="", alias="CATALOG_SERVICE_API_URL")

    # Payments service settings
    api_payments_service: str = Field(default="", alias="PAYMENTS_SERVICE_API_URL")
    payments_callback_url: str = Field(default="", alias="PAYMENTS_CALLBACK_URL")

    # Notifications service settings
    api_notifications_service: str = Field(
        default="", alias="NOTIFICATIONS_SERVICE_API_URL"
    )

    # Capashino credentials
    access_token: str = Field(default="", alias="CAPASHINO_SERVICE_ACCESS_TOKEN")
