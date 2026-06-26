# api

Basic FastAPI service that relays chat messages to an LLM through LangChain.
Two connectors are wired up: **OpenAI** (`langchain-openai`) and **Claude /
Anthropic** (`langchain-anthropic`).

## Setup

```bash
cp .env.example .env   # then add your API keys
uv sync
```

## Run

```bash
uv run api              # http://localhost:8000 (auto-reload)
# or
uv run python main.py
```

Interactive docs at `http://localhost:8000/docs`.

## Endpoints

- `GET /health` — liveness check.
- `POST /chat` — send messages to the LLM.

### Example

```bash
curl -s http://localhost:8000/chat \
  -H 'content-type: application/json' \
  -d '{
        "provider": "anthropic",
        "messages": [
          {"role": "system", "content": "You are concise."},
          {"role": "user", "content": "Say hello in one word."}
        ]
      }'
```

`provider` is `"openai"` or `"anthropic"` (defaults to `DEFAULT_PROVIDER`).
`model` and `max_tokens` are optional per-request overrides.

## Layout

- `src/api/config.py` — settings / env loading.
- `src/api/llm.py` — provider factory (OpenAI + Anthropic).
- `src/api/main.py` — FastAPI app and `/chat` endpoint.
