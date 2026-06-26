from typing import Literal
from pydantic import BaseModel, Field


class InputData(BaseModel):
    onq_folder: int
    folder_id: list[int] = Field(
        default_factory=lambda s: [int(x) for x in s.split(",")]
    )


class ChatRequest(BaseModel):
    system_prompt: str
    data: list[InputData] = Field(..., min_length=1)
    model: str | None = Field(
        default=None,
        description="Model id from GET /models; the provider is inferred from it. "
        "Omit to use the configured default.",
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
    is_default: bool = Field(
        default=False, description="True if this is the configured default for its provider"
    )


class ModelsResponse(BaseModel):
    default_provider: str
    models: list[ModelInfo]
