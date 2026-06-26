"""Shared pytest fixtures.

Keeps tests hermetic: provider credentials live in module-scoped ``settings``,
so we patch the attributes per-test rather than relying on a real ``.env``.
"""

import pytest

from api import config, llm


@pytest.fixture
def patch_settings(monkeypatch):
    """Return a helper that overrides fields on the shared ``settings`` object.

    The same ``settings`` instance is imported by ``api.llm``, so patching it
    here is visible to the code under test.
    """

    def _patch(**overrides):
        llm.clear_chat_model_cache()
        for key, value in overrides.items():
            monkeypatch.setattr(config.settings, key, value, raising=True)
            # ``api.llm`` imported ``settings`` by name; it points at the same
            # object, so the attribute override above is already in effect.
        return config.settings

    yield _patch
    llm.clear_chat_model_cache()


@pytest.fixture
def client():
    """FastAPI TestClient for the app."""
    from fastapi.testclient import TestClient

    from api.main import app

    return TestClient(app)
