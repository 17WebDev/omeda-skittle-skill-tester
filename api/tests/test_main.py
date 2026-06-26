"""Endpoint tests driven through FastAPI's TestClient."""


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_models_returns_both_providers(client, patch_settings):
    patch_settings(default_provider="anthropic")
    resp = client.get("/models")
    assert resp.status_code == 200
    body = resp.json()
    assert body["default_provider"] == "anthropic"
    providers = {m["provider"] for m in body["models"]}
    assert providers == {"openai", "anthropic"}


def test_list_models_flags_configured_defaults(client, patch_settings):
    patch_settings(
        default_anthropic_model="claude-opus-4-8", default_openai_model="gpt-4o"
    )
    resp = client.get("/models")
    defaults = {
        m["provider"]: m["id"] for m in resp.json()["models"] if m["is_default"]
    }
    assert defaults == {"anthropic": "claude-opus-4-8", "openai": "gpt-4o"}


def test_list_models_filtered_by_provider(client):
    resp = client.get("/models", params={"provider": "anthropic"})
    assert resp.status_code == 200
    models = resp.json()["models"]
    assert models  # non-empty
    assert all(m["provider"] == "anthropic" for m in models)


def test_list_models_rejects_unknown_provider(client):
    resp = client.get("/models", params={"provider": "gemini"})
    assert resp.status_code == 422
