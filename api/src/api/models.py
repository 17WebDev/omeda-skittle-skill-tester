from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ChatRequest(BaseModel):
    """Skill-test payload from the frontend (camelCase on the wire)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    model: str | None = None
    environment_id: int
    data_view_id: str
    jwt: str
    system_prompt: str
    folder_id: str
    folder_value_id: str
    user_input: str
    skill: str


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str


class ModelInfo(BaseModel):
    id: str
    provider: Literal["openai", "anthropic"]


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
