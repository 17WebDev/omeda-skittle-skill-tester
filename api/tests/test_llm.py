"""Unit tests for the chat-model factory.

These avoid any network calls: constructing ``ChatOpenAI`` / ``ChatAnthropic``
does not hit the provider, so we only assert on configuration and validation.
"""

from typing import cast

import pytest
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from api.llm import SUPPORTED_PROVIDERS, build_chat_model, provider_for_model


def test_unknown_provider_raises(patch_settings):
    patch_settings(default_provider="anthropic")
    with pytest.raises(ValueError, match="Unknown provider"):
        build_chat_model("gemini")


def test_openai_missing_key_raises(patch_settings):
    patch_settings(openai_api_key=None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_chat_model("openai")


def test_anthropic_missing_key_raises(patch_settings):
    patch_settings(anthropic_api_key=None)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        build_chat_model("anthropic")


def test_provider_is_case_insensitive(patch_settings):
    patch_settings(openai_api_key="sk-test", default_openai_model="gpt-4o")
    model = cast(ChatOpenAI, build_chat_model("OpenAI"))
    assert model.model_name == "gpt-4o"


def test_defaults_to_configured_provider(patch_settings):
    patch_settings(
        default_provider="anthropic",
        anthropic_api_key="sk-test",
        default_anthropic_model="claude-opus-4-8",
    )
    model = cast(ChatAnthropic, build_chat_model(provider=None))
    assert model.model == "claude-opus-4-8"


def test_openai_uses_default_model(patch_settings):
    patch_settings(openai_api_key="sk-test", default_openai_model="gpt-4o")
    model = cast(ChatOpenAI, build_chat_model("openai"))
    assert model.model_name == "gpt-4o"


def test_explicit_model_overrides_default(patch_settings):
    patch_settings(openai_api_key="sk-test")
    model = cast(ChatOpenAI, build_chat_model("openai", model="gpt-4o-mini"))
    assert model.model_name == "gpt-4o-mini"


def test_max_tokens_passed_through(patch_settings):
    patch_settings(anthropic_api_key="sk-test")
    model = cast(ChatAnthropic, build_chat_model("anthropic", max_tokens=256))
    assert model.max_tokens == 256


def test_max_tokens_falls_back_to_default(patch_settings):
    patch_settings(anthropic_api_key="sk-test", default_max_tokens=1024)
    model = cast(ChatAnthropic, build_chat_model("anthropic"))
    assert model.max_tokens == 1024


def test_supported_providers_constant():
    assert set(SUPPORTED_PROVIDERS) == {"openai", "anthropic"}


def test_provider_for_model_infers_provider():
    assert provider_for_model("gpt-4o") == "openai"
    assert provider_for_model("claude-opus-4-8") == "anthropic"


def test_provider_for_model_rejects_unknown_model():
    with pytest.raises(ValueError, match="Unknown model"):
        provider_for_model("gemini-pro")
