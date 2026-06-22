from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(
        default="QuoteFlow Pro",
        validation_alias="APP_NAME",
    )
    app_env: str = Field(
        default="development",
        validation_alias="APP_ENV",
    )
    database_url: str = Field(
        default="postgresql+psycopg://quoteflow:quoteflow_password@localhost:5433/quoteflow",
        validation_alias="DATABASE_URL",
    )
    secret_key: str = Field(
        default="quoteflow_pro_development_secret_key",
        validation_alias="SECRET_KEY",
    )
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
