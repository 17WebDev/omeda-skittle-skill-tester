"""Validation tests for the request/response models."""

import pytest
from pydantic import ValidationError

from api.models import ChatRequest, ChatResponse, Message, ModelInfo, ModelsResponse

BASE_PAYLOAD = {
    "model": "claude-opus-4-8",
    "environmentId": 12344,
    "dataViewId": "1",
    "jwt": "tok",
    "systemPrompt": "be helpful",
    "folderId": "dddd",
    "folderValueId": "10,11",
    "userInput": "hello",
    "skill": "my-skill",
}


def _request(**overrides) -> ChatRequest:
    return ChatRequest.model_validate({**BASE_PAYLOAD, **overrides})


def test_chat_request_accepts_camelcase_payload():
    req = _request()
    assert req.model == "claude-opus-4-8"
    assert req.environment_id == 12344
    assert req.data_view_id == "1"
    assert req.user_input == "hello"
    assert req.skill == "my-skill"


def test_chat_request_also_accepts_snake_case():
    # populate_by_name=True lets the python field names work on the wire too.
    req = ChatRequest.model_validate(
        {
            "model": "claude-opus-4-8",
            "environment_id": 7,
            "data_view_id": "1",
            "jwt": "tok",
            "system_prompt": "be helpful",
            "folder_id": "dddd",
            "folder_value_id": "10,11",
            "user_input": "hi",
            "skill": "my-skill",
        }
    )
    assert req.environment_id == 7
    assert req.user_input == "hi"


def test_folder_value_id_parses_csv_string():
    assert _request(folderValueId="10,11").folder_value_id == [10, 11]


def test_folder_value_id_accepts_list():
    assert _request(folderValueId=[10, 11]).folder_value_id == [10, 11]


def test_chat_request_requires_model():
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "model"}
    with pytest.raises(ValidationError):
        ChatRequest.model_validate(payload)


def test_chat_request_requires_system_prompt():
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "systemPrompt"}
    with pytest.raises(ValidationError):
        ChatRequest.model_validate(payload)


def test_message_role_validated():
    assert Message(role="user", content="hi").role == "user"
    with pytest.raises(ValidationError):
        # "robot" is intentionally outside the allowed Literal.
        Message(role="robot", content="hi")  # pyrefly: ignore[bad-argument-type]


def test_chat_response_roundtrip():
    resp = ChatResponse(content="hello")
    assert resp.model_dump() == {"content": "hello"}


def test_model_info_provider_validated():
    assert ModelInfo(id="gpt-4o", provider="openai").provider == "openai"
    with pytest.raises(ValidationError):
        ModelInfo(id="x", provider="gemini")  # pyrefly: ignore[bad-argument-type]


def test_models_response_nests_model_info():
    resp = ModelsResponse(models=[ModelInfo(id="claude-opus-4-8", provider="anthropic")])
    assert resp.models[0].id == "claude-opus-4-8"
