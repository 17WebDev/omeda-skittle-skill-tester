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
    provider: Literal["openai", "anthropic"] | None = Field(
        default=None, description="'openai' or 'anthropic' (defaults to configured)"
    )
    model: str | None = Field(default=None, description="Override the provider's model")


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str
