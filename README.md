# omeda-skittle-skill-tester

Monorepo for the Skittle skill tester.

## Structure

- **`api/`** — FastAPI service that relays prompts to an LLM (OpenAI or Claude)
  via LangChain, with the provider inferred from the requested model. See
  [`api/README.md`](api/README.md) for setup, configuration, and endpoints.
- **`frontend/`** — web client (not yet implemented).

## Quick start (API)

```bash
cd api
cp .env.example .env   # add your API key(s)
docker compose up --build   # http://localhost:8000  (docs at /docs)
```

For local dev with auto-reload and full details, see [`api/README.md`](api/README.md).
