from typing import Literal
from pydantic import BaseModel, Field, field_validator


class InputData(BaseModel):
    onq_folder: int
    folder_id: list[int] = Field(default_factory=list)

    @field_validator("folder_id", mode="before")
    @classmethod
    def _coerce_folder_id(cls, value: object) -> object:
        """Accept a comma-separated string (e.g. "10,11") as well as a list."""
        if isinstance(value, str):
            return [int(part) for part in value.split(",") if part.strip()]
        return value


class ChatRequest(BaseModel):
    system_prompt: str
    data: list[InputData] = Field(..., min_length=1)
    model: str = Field(
        ...,
        description="Model id from GET /models; the provider is inferred from it.",
    )


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
