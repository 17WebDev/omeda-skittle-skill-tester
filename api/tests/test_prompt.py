"""Tests for the prompt strategy (message construction)."""

from langchain_core.messages import HumanMessage, SystemMessage

from api.models import ChatRequest
from api.prompt import build_messages

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


def test_three_messages_system_then_two_human():
    msgs = build_messages(_request())
    assert len(msgs) == 3
    assert isinstance(msgs[0], SystemMessage)
    assert isinstance(msgs[1], HumanMessage)
    assert isinstance(msgs[2], HumanMessage)


def test_system_message_combines_prompt_and_skill():
    msgs = build_messages(_request(systemPrompt="P", skill="S"))
    assert msgs[0].content == "P\n\nS"


def test_data_message_is_folder_json():
    msgs = build_messages(_request(folderId="dddd", folderValueId="10,11"))
    assert msgs[1].content == '{"folderId":"dddd","folderValueId":[10,11]}'


def test_user_input_is_the_last_message():
    msgs = build_messages(_request(userInput="what is this?"))
    assert msgs[2].content == "what is this?"
