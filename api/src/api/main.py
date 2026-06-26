"""Basic FastAPI app that relays messages to an LLM via LangChain."""

from typing import Literal

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .config import settings
from .llm import AVAILABLE_MODELS, build_chat_model, provider_for_model
from .models import ChatRequest, ChatResponse, ModelInfo, ModelsResponse

app = FastAPI(title="LLM API", version="0.1.0")


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


@app.get("/models", response_model=ModelsResponse)
def list_models(
    provider: Literal["openai", "anthropic"] | None = None,
) -> ModelsResponse:
    """List the models available to consume, optionally filtered by provider.

    The catalog is a curated template (see ``AVAILABLE_MODELS``); ``is_default``
    flags the model resolved when a request omits an explicit ``model``.
    """
    defaults = {
        "openai": settings.default_openai_model,
        "anthropic": settings.default_anthropic_model,
    }
    providers: list[Literal["openai", "anthropic"]] = (
        [provider] if provider else ["anthropic", "openai"]
    )
    models = [
        ModelInfo(id=model, provider=p, is_default=model == defaults[p])
        for p in providers
        for model in AVAILABLE_MODELS[p]
    ]
    return ModelsResponse(
        default_provider=settings.default_provider.lower(), models=models
    )


@app.post("/test-skittle", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    # The payload no longer carries a provider — infer it from the requested
    # model via the catalog. With no model, fall back to the configured default.
    try:
        provider = (
            provider_for_model(req.model)
            if req.model
            else settings.default_provider.lower()
        )
        model = build_chat_model(provider, req.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    data_content = "\n".join(item.model_dump_json() for item in req.data)
    lc_messages = [
        _ROLE_TO_MESSAGE["system"](content=req.system_prompt),
        _ROLE_TO_MESSAGE["user"](content=data_content),
    ]

    try:
        # await the async invocation so the LLM network call yields the event
        # loop instead of blocking the worker thread — lets one worker handle
        # many concurrent requests.
        result = await model.ainvoke(lc_messages)
    except Exception as exc:  # surface upstream/provider errors as 502
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        content=result.text,
        provider=provider,
        model=getattr(model, "model", None)
        or getattr(model, "model_name", None)
        or req.model
        or "",
    )
