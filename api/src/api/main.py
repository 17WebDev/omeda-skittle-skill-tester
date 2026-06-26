"""Basic FastAPI app that relays messages to an LLM via LangChain."""

from typing import Literal

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from .config import settings
from .llm import build_chat_model

app = FastAPI(title="LLM API", version="0.1.0")


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)
    provider: str | None = Field(
        default=None, description="'openai' or 'anthropic' (defaults to configured)"
    )
    model: str | None = Field(default=None, description="Override the provider's model")
    max_tokens: int | None = None


class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str


_ROLE_TO_MESSAGE = {
    "system": SystemMessage,
    "user": HumanMessage,
    "assistant": AIMessage,
}


def serve() -> None:
    """Console-script entrypoint: `uv run api`."""
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/test-skittle", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    provider = (req.provider or settings.default_provider).lower()

    try:
        model = build_chat_model(provider, req.model, req.max_tokens)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    lc_messages = [_ROLE_TO_MESSAGE[m.role](content=m.content) for m in req.messages]

    try:
        result = model.invoke(lc_messages)
    except Exception as exc:  # surface upstream/provider errors as 502
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        content=result.text,
        provider=provider,
        model=getattr(model, "model", req.model or ""),
    )
