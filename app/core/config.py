from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_JWT_SECRET = "change-this-secret-key-change-this-secret-key"


def normalize_database_url(raw_url: str, username: str = "", password: str = "") -> str:
    raw = (raw_url or "").strip()
    normalized_username = (username or "").strip()
    normalized_password = (password or "").strip()

    if raw.startswith("jdbc:mysql://"):
        host_and_database = raw.removeprefix("jdbc:mysql://")
        auth = quote_plus(normalized_username)
        if normalized_password:
            auth = f"{auth}:{quote_plus(normalized_password)}"
        return f"mysql+pymysql://{auth}@{host_and_database}"

    if raw.startswith("mysql://"):
        return raw.replace("mysql://", "mysql+pymysql://", 1)

    if raw.startswith("jdbc:postgresql://"):
        host_and_database = raw.removeprefix("jdbc:postgresql://")
        auth = quote_plus(normalized_username)
        if normalized_password:
            auth = f"{auth}:{quote_plus(normalized_password)}"
        return f"postgresql+psycopg://{auth}@{host_and_database}"

    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql+psycopg://", 1)

    if raw.startswith("postgresql://"):
        return raw.replace("postgresql://", "postgresql+psycopg://", 1)

    return raw


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    app_name: str = Field(default="college-server", validation_alias="APP_NAME")
    app_env: Literal["development", "test", "staging", "production"] = Field(default="development", validation_alias="APP_ENV")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    server_host: str = Field(default="0.0.0.0", validation_alias="SERVER_HOST")
    server_port: int = Field(default=8000, validation_alias="SERVER_PORT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    docs_enabled: bool = Field(default=True, validation_alias="DOCS_ENABLED")

    db_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/college_server", validation_alias="DB_URL")
    db_username: str = Field(default="", validation_alias="DB_USERNAME")
    db_password: str = Field(default="", validation_alias="DB_PASSWORD")
    db_pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    db_pool_recycle_seconds: int = Field(default=1800, validation_alias="DB_POOL_RECYCLE_SECONDS")
    db_pool_pre_ping: bool = Field(default=True, validation_alias="DB_POOL_PRE_PING")
    auto_initialize_schema: bool = Field(default=False, validation_alias="AUTO_INITIALIZE_SCHEMA")
    run_migrations_on_startup: bool = Field(default=False, validation_alias="RUN_MIGRATIONS_ON_STARTUP")

    jwt_secret: str = Field(default=DEFAULT_JWT_SECRET, validation_alias="JWT_SECRET")
    jwt_issuer: str = Field(default="college-server", validation_alias="JWT_ISSUER")
    jwt_audience: str = Field(default="college-clients", validation_alias="JWT_AUDIENCE")
    jwt_expiration_minutes: int = Field(default=120, validation_alias="JWT_EXPIRATION_MINUTES")
    jwt_leeway_seconds: int = Field(default=5, validation_alias="JWT_LEEWAY_SECONDS")
    refresh_token_expiration_days: int = Field(default=14, validation_alias="REFRESH_TOKEN_EXPIRATION_DAYS")
    max_active_refresh_tokens_per_user: int = Field(default=5, validation_alias="MAX_ACTIVE_REFRESH_TOKENS_PER_USER")

    login_rate_limit_window_seconds: int = Field(default=300, validation_alias="LOGIN_RATE_LIMIT_WINDOW_SECONDS")
    login_rate_limit_max_attempts: int = Field(default=5, validation_alias="LOGIN_RATE_LIMIT_MAX_ATTEMPTS")
    login_rate_limit_lockout_seconds: int = Field(default=900, validation_alias="LOGIN_RATE_LIMIT_LOCKOUT_SECONDS")

    bootstrap_admin_enabled: bool = Field(default=False, validation_alias="BOOTSTRAP_ADMIN_ENABLED")
    bootstrap_admin_username: str = Field(default="admin", validation_alias="BOOTSTRAP_ADMIN_USERNAME")
    bootstrap_admin_password: str = Field(default="admin12345", validation_alias="BOOTSTRAP_ADMIN_PASSWORD")
    bootstrap_admin_email: str = Field(default="admin@college.com", validation_alias="BOOTSTRAP_ADMIN_EMAIL")

    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ALLOWED_ORIGINS",
    )
    trusted_hosts: str = Field(default="localhost,127.0.0.1,::1,testserver", validation_alias="TRUSTED_HOSTS")
    request_id_header_name: str = Field(default="X-Request-ID", validation_alias="REQUEST_ID_HEADER_NAME")

    @model_validator(mode="after")
    def validate_production_safety(self) -> Settings:
        if self.jwt_expiration_minutes <= 0:
            raise ValueError("JWT_EXPIRATION_MINUTES must be greater than zero")
        if self.jwt_leeway_seconds < 0:
            raise ValueError("JWT_LEEWAY_SECONDS must be zero or greater")
        if self.refresh_token_expiration_days <= 0:
            raise ValueError("REFRESH_TOKEN_EXPIRATION_DAYS must be greater than zero")
        if self.max_active_refresh_tokens_per_user <= 0:
            raise ValueError("MAX_ACTIVE_REFRESH_TOKENS_PER_USER must be greater than zero")
        if self.login_rate_limit_window_seconds <= 0:
            raise ValueError("LOGIN_RATE_LIMIT_WINDOW_SECONDS must be greater than zero")
        if self.login_rate_limit_max_attempts <= 0:
            raise ValueError("LOGIN_RATE_LIMIT_MAX_ATTEMPTS must be greater than zero")
        if self.login_rate_limit_lockout_seconds <= 0:
            raise ValueError("LOGIN_RATE_LIMIT_LOCKOUT_SECONDS must be greater than zero")
        if self.db_pool_size <= 0:
            raise ValueError("DB_POOL_SIZE must be greater than zero")
        if self.db_max_overflow < 0:
            raise ValueError("DB_MAX_OVERFLOW must be zero or greater")
        if self.db_pool_recycle_seconds <= 0:
            raise ValueError("DB_POOL_RECYCLE_SECONDS must be greater than zero")
        if self.app_env == "production":
            if not self.jwt_secret.strip() or self.jwt_secret == DEFAULT_JWT_SECRET:
                raise ValueError("JWT_SECRET must be set to a non-default value in production")
            if "*" in self.cors_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS cannot contain '*' in production")
            if "*" in self.trusted_hosts_list:
                raise ValueError("TRUSTED_HOSTS cannot contain '*' in production")
            if self.auto_initialize_schema:
                raise ValueError("AUTO_INITIALIZE_SCHEMA must be false in production")
            if self.bootstrap_admin_enabled:
                raise ValueError("BOOTSTRAP_ADMIN_ENABLED must be false in production")
        return self

    @property
    def database_url(self) -> str:
        return normalize_database_url(self.db_url, self.db_username, self.db_password)

    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.docs_enabled else None

    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.docs_enabled else None

    @property
    def openapi_url(self) -> str | None:
        return "/openapi.json" if self.docs_enabled else None

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_allowed_origins.split(",") if item.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [item.strip() for item in self.trusted_hosts.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
