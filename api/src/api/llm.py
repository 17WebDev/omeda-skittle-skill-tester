"""LLM factory: builds a LangChain chat model for the requested provider.

Two connectors are wired up:
  - OpenAI   via ``langchain_openai.ChatOpenAI``
  - Anthropic (Claude) via ``langchain_anthropic.ChatAnthropic``
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from .config import settings

SUPPORTED_PROVIDERS = ("openai", "anthropic")


def build_chat_model(
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """Return a configured chat model for ``provider``.

    Raises ValueError for an unknown provider or a missing API key.
    """
    provider = (provider or settings.default_provider).lower()
    max_tokens = max_tokens or settings.default_max_tokens

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return ChatOpenAI(
            model=model or settings.default_openai_model,
            api_key=settings.openai_api_key,
            max_tokens=max_tokens,
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        return ChatAnthropic(
            model=model or settings.default_anthropic_model,
            api_key=settings.anthropic_api_key,
            max_tokens=max_tokens,
        )

    raise ValueError(
        f"Unknown provider {provider!r}; expected one of {SUPPORTED_PROVIDERS}"
    )
