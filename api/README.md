# api

FastAPI service that relays prompts to an LLM through LangChain. Two connectors
are wired up — **OpenAI** (`langchain-openai`) and **Claude / Anthropic**
(`langchain-anthropic`) — and the provider is **inferred from the requested
model**, so callers pick a model and the service figures out the rest.

## Setup

```bash
cp .env.example .env   # then add your API key(s)
uv sync
```

## Run

### Local (dev, auto-reload)

```bash
uv run api              # http://localhost:8000
# or
uv run python main.py
```

### Docker

```bash
docker compose up --build          # http://localhost:8000
# or without compose:
docker build -t omeda-skittle-api .
docker run --rm -p 8000:8000 --env-file .env omeda-skittle-api
```

Interactive docs at `http://localhost:8000/docs`.

## Configuration

Settings load from environment / `.env` (see `.env.example`):

| Variable            | Purpose                                       |
| ------------------- | --------------------------------------------- |
| `OPENAI_API_KEY`    | Key for OpenAI models (required to use them). |
| `ANTHROPIC_API_KEY` | Key for Claude models (required to use them). |

There are no default-model or max-token settings: the consumer always specifies
the `model`, and each model keeps its own `max_tokens` default rather than a cap
we impose.

## Endpoints

- `GET /health` — liveness check → `{"status": "ok"}`.
- `GET /models` — list available models; optional `?provider=openai|anthropic` filter.
- `POST /test-skittle` — run a prompt against the LLM.

### `GET /models`

```bash
curl -s http://localhost:8000/models
```

```json
{
  "models": [
    {"id": "claude-opus-4-8", "provider": "anthropic"},
    {"id": "gpt-4o", "provider": "openai"}
  ]
}
```

The catalog is an allowlist — a request must use one of these model ids.

### `POST /test-skittle`

Fields use **camelCase** on the wire (snake_case is also accepted). The payload
carries **no `provider`** — it is inferred from the (required) `model` against
the list returned by `GET /models`.

| Field            | Type                  | Notes                                                       |
| ---------------- | --------------------- | ----------------------------------------------------------- |
| `model`          | `string` (**required**) | A model id from `GET /models`; provider inferred.         |
| `systemPrompt`   | `string`              | Combined with `skill` into the system message.              |
| `skill`          | `string`              | Appended to the system message (agent instructions/context).|
| `userInput`      | `string`              | Sent as its own (final) human message.                      |
| `folderId`       | `string`              | Part of the JSON data human message.                        |
| `folderValueId`  | `int[]` or CSV string | Parsed to a list of ints; part of the JSON data message.    |
| `environmentId`  | `int`                 | Accepted, not yet used.                                     |
| `dataViewId`     | `string`              | Accepted, not yet used.                                     |
| `jwt`            | `string`              | Accepted, not sent to the LLM.                              |

The LLM receives three messages: a **system** message (`systemPrompt` + `skill`),
a **human** message with the folder data as JSON (`{folderId, folderValueId}`),
and a **human** message with `userInput`.

```bash
curl -s http://localhost:8000/test-skittle \
  -H 'content-type: application/json' \
  -d '{
        "model": "claude-opus-4-8",
        "environmentId": 12344,
        "dataViewId": "1",
        "jwt": "…",
        "systemPrompt": "You are concise.",
        "folderId": "dddd",
        "folderValueId": "10,11",
        "userInput": "Summarize the selection.",
        "skill": "summarizer"
      }'
```

Response:

```json
{ "content": "..." }
```

A missing `model` returns `422`; an unknown `model` returns `400`; an
upstream/provider error returns `502`.

## Notes

- **Async / non-blocking** — `/test-skittle` is `async` and awaits `model.ainvoke(...)`,
  so a single worker handles many concurrent requests without blocking the event loop.
- **Cached model instances** — chat models are built once per
  `(provider, model)` and reused across requests rather than re-instantiated
  each call (`src/api/llm.py`).

## Layout

- `src/api/config.py` — settings / env loading.
- `src/api/llm.py` — model catalog (`AVAILABLE_MODELS`), provider inference, cached factory.
- `src/api/models.py` — request/response schemas.
- `src/api/prompt.py` — prompt strategy: builds the LLM messages from a request.
- `src/api/main.py` — FastAPI app and endpoints.
- `Dockerfile`, `.dockerignore`, `docker-compose.yml` — container build & run.
