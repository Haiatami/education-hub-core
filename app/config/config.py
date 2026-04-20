# education-hub-core/app/config/config.py
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# --- POSTGRESQL ---
class PostgresqlSettings(BaseSettings):
    """
    Configuration settings for postgresql + pgvector
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    POSTGRES_HOST: str = Field(default="pgvector")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str = Field(default="education-hub")

    PG_POOL_MIN: int = Field(default=5)
    PG_POOL_MAX: int = Field(default=20)

    @computed_field
    @property
    def postgres_uri(self) -> str:
        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD.get_secret_value())
        return f"postgresql+psycopg://{user}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# --- SETTINGS ---
class Settings(BaseSettings):
    """
    Configuration settings for the application
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    PROJECT_NAME: str = Field(default="Education Hub Core")
    VERSION: str = Field(default="1.0.0")
    API_STR: str = Field(default="/api")
    API_V1_STR: str = Field(default="/v1")

    ENV: str = Field(default="development")

    LOG_LEVEL: str = Field(default="INFO")
    LOG_JSON_FORMAT: bool = Field(default=False)

    postgres: PostgresqlSettings = Field(default_factory=lambda: PostgresqlSettings())


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
