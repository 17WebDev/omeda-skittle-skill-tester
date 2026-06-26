"""Basic FastAPI app that relays messages to an LLM via LangChain."""

from typing import Literal

from fastapi import FastAPI, HTTPException

from .llm import AVAILABLE_MODELS, build_chat_model, provider_for_model
from .models import ChatRequest, ChatResponse, ModelInfo, ModelsResponse
from .prompt import build_messages

app = FastAPI(title="LLM API", version="0.1.0")


def serve() -> None:
    """Console-script entrypoint: `uv run api`."""
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/models", response_model=ModelsResponse)
def list_models(
    provider: Literal["openai", "anthropic"] | None = None,
) -> ModelsResponse:
    """List the models available to consume, optionally filtered by provider.

    The catalog is a curated allowlist (see ``AVAILABLE_MODELS``); a request must
    specify one of these model ids.
    """
    providers: list[Literal["openai", "anthropic"]] = (
        [provider] if provider else ["anthropic", "openai"]
    )
    models = [
        ModelInfo(id=model, provider=p)
        for p in providers
        for model in AVAILABLE_MODELS[p]
    ]
    return ModelsResponse(models=models)


@app.post("/test-skittle", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    # The payload carries no provider — infer it from the (required) model via
    # the catalog.
    try:
        provider = provider_for_model(req.model)
        model = build_chat_model(provider, req.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Message construction lives in the prompt module (the "prompt strategy").
    lc_messages = build_messages(req)

    try:
        # await the async invocation so the LLM network call yields the event
        # loop instead of blocking the worker thread — lets one worker handle
        # many concurrent requests.
        result = await model.ainvoke(lc_messages)
    except Exception as exc:  # surface upstream/provider errors as 502
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(content=result.text, provider=provider, model=req.model)
