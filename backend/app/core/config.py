from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QuoteFlow Pro"
    app_env: str = "development"
    database_url: str = "sqlite:///./quoteflow.db"
    secret_key: str = "quoteflow_pro_development_secret_key"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
