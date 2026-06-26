"""Builds LLM messages from a skill-test request.

System prompt = the skill under test. The data folders are handed to the model
as a JSON user message.
"""
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .models import ChatRequest


def build_messages(req: ChatRequest) -> list[BaseMessage]:
    return [
        SystemMessage(content=req.system_prompt),
        HumanMessage(content=req.user_input),
    ]


def demo() -> None:
    req = ChatRequest(
        environment_id=1,
        data_view_id="1",
        jwt="x",
        system_prompt="test skill",
        folder_id="f",
        folder_value_id="fv",
        user_input="hello",
        skill="s",
    )
    msgs = build_messages(req)
    assert len(msgs) == 2
    assert isinstance(msgs[0], SystemMessage)
    assert msgs[1].content == "hello"
    print("ok")


if __name__ == "__main__":
    demo()
