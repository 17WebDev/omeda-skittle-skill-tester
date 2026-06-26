"""LLM factory: builds a LangChain chat model for the requested provider.

Two connectors are wired up:
  - OpenAI   via ``langchain_openai.ChatOpenAI``
  - Anthropic (Claude) via ``langchain_anthropic.ChatAnthropic``

Model instances are cached per (provider, model, max_tokens) so each distinct
configuration is constructed once and reused across requests rather than rebuilt
on every call. ``ChatOpenAI`` / ``ChatAnthropic`` are safe to share — they hold a
reusable HTTP client and carry no per-request state.
"""

from functools import lru_cache

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from .config import settings

SUPPORTED_PROVIDERS = ("openai", "anthropic")

# Template catalog of models known to work with the connectors wired up above.
# This is a curated starting list, not an exhaustive or live-queried inventory —
# extend it as providers ship new models. Order is most- to least-capable so the
# first entry per provider reads as a sensible default suggestion.
AVAILABLE_MODELS: dict[str, tuple[str, ...]] = {
    "anthropic": (
        "claude-opus-4-8",
        "claude-opus-4-7",
        "claude-sonnet-4-6",
        "claude-haiku-4-5",
    ),
    "openai": (
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ),
}


# Reverse index: model id -> provider, derived from the catalog above so the two
# never drift. Assumes model ids are unique across providers.
_MODEL_TO_PROVIDER: dict[str, str] = {
    model: provider
    for provider, models in AVAILABLE_MODELS.items()
    for model in models
}


def provider_for_model(model: str) -> str:
    """Infer the provider that serves ``model`` from the available-model list.

    Raises ValueError if the model is not in the catalog.
    """
    try:
        return _MODEL_TO_PROVIDER[model]
    except KeyError:
        raise ValueError(
            f"Unknown model {model!r}; not in the available model list "
            f"(see GET /models)"
        ) from None


@lru_cache(maxsize=None)
def _construct_chat_model(
    provider: str, model: str, max_tokens: int
) -> BaseChatModel:
    """Build one chat model. Cached: identical args return the same instance.

    A raised ValueError is not cached, so a request that fails for a missing key
    can succeed later once the key is configured.
    """
    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return ChatOpenAI(
            model=model, api_key=settings.openai_api_key, max_tokens=max_tokens
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        return ChatAnthropic(
            model_name=model,
            api_key=settings.anthropic_api_key,
            max_tokens=max_tokens,
        )

    raise ValueError(
        f"Unknown provider {provider!r}; expected one of {SUPPORTED_PROVIDERS}"
    )


def build_chat_model(
    provider: str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """Return a cached chat model for ``provider``, resolving defaults first.

    Raises ValueError for an unknown provider or a missing API key.
    """
    provider = (provider or settings.default_provider).lower()
    max_tokens = max_tokens or settings.default_max_tokens

    if provider == "openai":
        model = model or settings.default_openai_model
    elif provider == "anthropic":
        model = model or settings.default_anthropic_model
    else:
        raise ValueError(
            f"Unknown provider {provider!r}; expected one of {SUPPORTED_PROVIDERS}"
        )

    return _construct_chat_model(provider, model, max_tokens)


def clear_chat_model_cache() -> None:
    """Clear cached model instances; useful when settings change in tests."""
    _construct_chat_model.cache_clear()
