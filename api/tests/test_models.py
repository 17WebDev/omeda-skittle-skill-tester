"""Validation tests for the request/response models."""

import pytest
from pydantic import ValidationError

from api.models import (
    ChatRequest,
    ChatResponse,
    InputData,
    Message,
    ModelInfo,
    ModelsResponse,
)


def test_input_data_minimal():
    item = InputData(onq_folder=1, folder_id=[10, 20])
    assert item.onq_folder == 1
    assert item.folder_id == [10, 20]


def test_chat_request_valid():
    req = ChatRequest(
        system_prompt="be helpful",
        data=[InputData(onq_folder=1, folder_id=[1])],
    )
    assert req.model is None
    assert len(req.data) == 1


def test_chat_request_requires_nonempty_data():
    with pytest.raises(ValidationError, match="at least 1"):
        ChatRequest(system_prompt="x", data=[])


def test_chat_request_requires_system_prompt():
    with pytest.raises(ValidationError):
        ChatRequest(data=[InputData(onq_folder=1, folder_id=[1])])  # type: ignore[call-arg]


def test_message_role_validated():
    assert Message(role="user", content="hi").role == "user"
    with pytest.raises(ValidationError):
        # "robot" is intentionally outside the allowed Literal.
        Message(role="robot", content="hi")  # pyrefly: ignore[bad-argument-type]


def test_chat_response_roundtrip():
    resp = ChatResponse(content="hello", provider="openai", model="gpt-4o")
    assert resp.model_dump() == {
        "content": "hello",
        "provider": "openai",
        "model": "gpt-4o",
    }


def test_model_info_provider_validated():
    assert ModelInfo(id="gpt-4o", provider="openai").is_default is False
    with pytest.raises(ValidationError):
        ModelInfo(id="x", provider="gemini")  # pyrefly: ignore[bad-argument-type]


def test_models_response_nests_model_info():
    resp = ModelsResponse(
        default_provider="anthropic",
        models=[ModelInfo(id="claude-opus-4-8", provider="anthropic", is_default=True)],
    )
    assert resp.models[0].is_default is True
