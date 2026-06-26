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
    patch_settings(anthropic_api_key="sk-test")
    with pytest.raises(ValueError, match="Unknown provider"):
        build_chat_model("gemini", "some-model")


def test_openai_missing_key_raises(patch_settings):
    patch_settings(openai_api_key=None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_chat_model("openai", "gpt-4o")


def test_anthropic_missing_key_raises(patch_settings):
    patch_settings(anthropic_api_key=None)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        build_chat_model("anthropic", "claude-opus-4-8")


def test_provider_is_case_insensitive(patch_settings):
    patch_settings(openai_api_key="sk-test")
    model = cast(ChatOpenAI, build_chat_model("OpenAI", "gpt-4o"))
    assert model.model_name == "gpt-4o"


def test_uses_the_requested_model(patch_settings):
    patch_settings(openai_api_key="sk-test")
    model = cast(ChatOpenAI, build_chat_model("openai", "gpt-4o-mini"))
    assert model.model_name == "gpt-4o-mini"


def test_max_tokens_left_at_model_default(patch_settings):
    # We no longer enforce a generic cap; the model keeps whatever the connector
    # derives on its own. Compare against a baseline built the same way to prove
    # we don't impose a max_tokens value.
    patch_settings(anthropic_api_key="sk-test")
    model = cast(ChatAnthropic, build_chat_model("anthropic", "claude-opus-4-8"))
    baseline = ChatAnthropic(model_name="claude-opus-4-8", api_key="sk-test")
    assert model.max_tokens == baseline.max_tokens


def test_same_config_is_cached(patch_settings):
    patch_settings(openai_api_key="sk-test")
    a = build_chat_model("openai", "gpt-4o")
    b = build_chat_model("openai", "gpt-4o")
    assert a is b


def test_supported_providers_constant():
    assert set(SUPPORTED_PROVIDERS) == {"openai", "anthropic"}


def test_provider_for_model_infers_provider():
    assert provider_for_model("gpt-4o") == "openai"
    assert provider_for_model("claude-opus-4-8") == "anthropic"


def test_provider_for_model_rejects_unknown_model():
    with pytest.raises(ValueError, match="Unknown model"):
        provider_for_model("gemini-pro")
