"""Builds the LLM messages from a skill-test request (the "prompt strategy").

- System message: the skill's system prompt plus the ``skill`` itself, which
  carries further instructions / context for the agent.
- Human message: the folder selection (``folderId`` + ``folderValueId``) as JSON.
- Human message: the user's input, as its own turn (the actionable ask, last).
"""

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .models import ChatRequest


def build_messages(req: ChatRequest) -> list[BaseMessage]:
    system = "\n\n".join(part for part in (req.system_prompt, req.skill) if part)
    data_json = req.model_dump_json(
        include={"folder_id", "folder_value_id"}, by_alias=True
    )
    return [
        SystemMessage(content=system),
        HumanMessage(content=data_json),
        HumanMessage(content=req.user_input),
    ]
