"""Builds LLM messages from a skill-test request.

System prompt = the skill under test. The data folders are handed to the model
as a JSON user message.
"""
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .models import ChatRequest


def build_messages(req: ChatRequest) -> list[BaseMessage]:
    data_json = "\n".join(d.model_dump_json() for d in req.data)
    return [
        SystemMessage(content=req.system_prompt),
        HumanMessage(content=data_json),
    ]


def demo() -> None:
    req = ChatRequest(
        system_prompt="test skill",
        data=[{"onq_folder": 1, "folder_id": [2, 3]}],
        model="claude-opus-4-8",
    )
    msgs = build_messages(req)
    assert len(msgs) == 2
    assert isinstance(msgs[0], SystemMessage)
    assert '"onq_folder":1' in msgs[1].content
    print("ok")


if __name__ == "__main__":
    demo()
