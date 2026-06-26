from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Provider credentials (read by the LangChain integrations). The model is
    # always supplied by the consumer per request, so there are no server-side
    # default-model or max-token settings — each model uses its own default.
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


settings = Settings()
