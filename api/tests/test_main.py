"""Endpoint tests driven through FastAPI's TestClient."""


class _FakeResult:
    """Stands in for a LangChain message result (only ``.text`` is read)."""

    def __init__(self, text: str):
        self.text = text


class _FakeModel:
    """Drop-in for a chat model so ``/test-skittle`` never hits the network."""

    model = "claude-opus-4-8"

    def __init__(self, reply: str = "ok", error: Exception | None = None):
        self._reply = reply
        self._error = error

    async def ainvoke(self, messages):
        if self._error is not None:
            raise self._error
        return _FakeResult(self._reply)


def _payload(**overrides):
    body = {
        "system_prompt": "be helpful",
        "data": [{"onq_folder": 1, "folder_id": [10, 20]}],
    }
    body.update(overrides)
    return body


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_models_returns_both_providers(client):
    resp = client.get("/models")
    assert resp.status_code == 200
    providers = {m["provider"] for m in resp.json()["models"]}
    assert providers == {"openai", "anthropic"}


def test_list_models_filtered_by_provider(client):
    resp = client.get("/models", params={"provider": "anthropic"})
    assert resp.status_code == 200
    models = resp.json()["models"]
    assert models  # non-empty
    assert all(m["provider"] == "anthropic" for m in models)


def test_list_models_rejects_unknown_provider(client):
    resp = client.get("/models", params={"provider": "gemini"})
    assert resp.status_code == 422


def test_chat_returns_model_reply(client, monkeypatch):
    monkeypatch.setattr("api.main.build_chat_model", lambda *a, **k: _FakeModel("pong"))
    resp = client.post("/test-skittle", json=_payload(model="claude-opus-4-8"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["content"] == "pong"
    assert body["provider"] == "anthropic"
    assert body["model"] == "claude-opus-4-8"


def test_chat_infers_provider_from_model(client, monkeypatch):
    captured = {}

    def _fake_build(provider, model=None, *a, **k):
        captured["provider"] = provider
        captured["model"] = model
        return _FakeModel()

    monkeypatch.setattr("api.main.build_chat_model", _fake_build)
    resp = client.post("/test-skittle", json=_payload(model="gpt-4o"))
    assert resp.status_code == 200
    # "gpt-4o" lives under the openai catalog, so the provider is inferred.
    assert captured == {"provider": "openai", "model": "gpt-4o"}


def test_chat_requires_model(client):
    # `model` is required now that there is no server-side default.
    resp = client.post("/test-skittle", json=_payload())
    assert resp.status_code == 422


def test_chat_unknown_model_returns_400(client):
    resp = client.post("/test-skittle", json=_payload(model="gemini-pro"))
    assert resp.status_code == 400
    assert "Unknown model" in resp.json()["detail"]


def test_chat_upstream_error_returns_502(client, monkeypatch):
    fake = _FakeModel(error=RuntimeError("provider exploded"))
    monkeypatch.setattr("api.main.build_chat_model", lambda *a, **k: fake)
    resp = client.post("/test-skittle", json=_payload(model="claude-opus-4-8"))
    assert resp.status_code == 502
    assert "provider exploded" in resp.json()["detail"]


def test_chat_requires_nonempty_data(client):
    resp = client.post(
        "/test-skittle",
        json={"system_prompt": "x", "data": [], "model": "claude-opus-4-8"},
    )
    assert resp.status_code == 422
