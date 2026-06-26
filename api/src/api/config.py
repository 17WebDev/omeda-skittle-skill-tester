from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Provider credentials (read by the LangChain integrations).
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Defaults for the chat endpoint.
    default_provider: str = "anthropic"
    default_openai_model: str = "gpt-4o"
    default_anthropic_model: str = "claude-opus-4-8"
    default_max_tokens: int = 1024


settings = Settings()
