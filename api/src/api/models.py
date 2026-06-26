from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


class ChatRequest(BaseModel):
    """Skill-test payload from the frontend (camelCase on the wire)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    model: str = Field(
        ..., description="Model id from GET /models; the provider is inferred from it."
    )
    environment_id: int
    data_view_id: str
    jwt: str
    system_prompt: str
    folder_id: str
    folder_value_id: list[int]
    user_input: str
    skill: str

    @field_validator("folder_value_id", mode="before")
    @classmethod
    def _coerce_folder_value_id(cls, value: object) -> object:
        """Accept a comma-separated string (e.g. "10,11") as well as a list."""
        if isinstance(value, str):
            return [int(part) for part in value.split(",") if part.strip()]
        return value


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    content: str


class ModelInfo(BaseModel):
    id: str
    provider: Literal["openai", "anthropic"]


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
