"""
Integration tests for all REST API endpoints.
Uses TestClient with an isolated temp-file SQLite database.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import db.database as _db_mod

_ORIGINAL_DB_PATH = _db_mod.DB_PATH


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_api.sqlite"
    monkeypatch.setattr(_db_mod, "DB_PATH", db_file)
    _db_mod.init_db()

    # Import app after DB is patched so all router dependencies use the right path
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    monkeypatch.setattr(_db_mod, "DB_PATH", _ORIGINAL_DB_PATH)


# ---------------------------------------------------------------------------
# Usage summary
# ---------------------------------------------------------------------------

def test_summary_zero_data_returns_all_seeded_models(client):
    r = client.get("/api/usage/summary")
    assert r.status_code == 200
    body = r.json()
    models = {m["model"] for m in body["models"]}
    assert "claude-sonnet-4-6" in models
    assert "claude-haiku-4-5" in models
    assert "claude-opus-4-6" in models
    for m in body["models"]:
        assert m["input_tokens"] == 0
        assert m["output_tokens"] == 0
        assert m["estimated_cost"] == 0.0


def test_summary_returns_per_model_totals(client):
    from db.usage import write_usage_event
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 100, "output_tokens": 50}, source="proxy")
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 200, "output_tokens": 100}, source="proxy")

    r = client.get("/api/usage/summary")
    assert r.status_code == 200
    body = r.json()
    sonnet = next(m for m in body["models"] if m["model"] == "claude-sonnet-4-6")
    assert sonnet["input_tokens"] == 300
    assert sonnet["output_tokens"] == 150
    assert sonnet["estimated_cost"] > 0
    assert body["total"]["input_tokens"] == 300


# ---------------------------------------------------------------------------
# Usage history
# ---------------------------------------------------------------------------

def test_history_no_filters_returns_all(client):
    from db.usage import write_usage_event
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 1}, source="proxy")
    write_usage_event("claude-haiku-4-5",  {"input_tokens": 2}, source="manual")

    r = client.get("/api/usage/history")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_history_filter_source_excludes_other(client):
    from db.usage import write_usage_event
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 1}, source="proxy")
    write_usage_event("claude-haiku-4-5",  {"input_tokens": 2}, source="manual")

    r = client.get("/api/usage/history?source=proxy")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["source"] == "proxy"


def test_history_filter_model(client):
    from db.usage import write_usage_event
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 1}, source="proxy")
    write_usage_event("claude-haiku-4-5",  {"input_tokens": 2}, source="proxy")

    r = client.get("/api/usage/history?model=claude-sonnet-4-6")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["model"] == "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Manual entry
# ---------------------------------------------------------------------------

def test_manual_entry_creates_event(client):
    r = client.post("/api/usage/manual", json={
        "model": "claude-sonnet-4-6",
        "input_tokens": 10,
        "output_tokens": 5,
    })
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "created"
    assert "id" in body

    # Event is retrievable via history
    history = client.get("/api/usage/history?source=manual").json()
    assert len(history) == 1
    assert history[0]["input_tokens"] == 10


def test_manual_entry_missing_model_returns_400(client):
    r = client.post("/api/usage/manual", json={"input_tokens": 5})
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------

def test_pricing_returns_all_seeded_models(client):
    r = client.get("/api/pricing")
    assert r.status_code == 200
    models = {row["model"] for row in r.json()}
    assert "claude-sonnet-4-6" in models
    assert "claude-haiku-4-5" in models
    assert "claude-opus-4-6" in models


# ---------------------------------------------------------------------------
# Exchange rate
# ---------------------------------------------------------------------------

def test_exchange_rate_returns_eur_on_success(client, monkeypatch):
    import api.exchange_rate as _er_mod
    import urllib.request
    import io

    class _FakeResp:
        def __init__(self):
            self._data = b'{"rates": {"EUR": 0.92}}'
        def read(self):
            return self._data
        def __enter__(self):
            return self
        def __exit__(self, *_):
            pass

    monkeypatch.setattr(_er_mod.urllib.request, "urlopen", lambda *a, **kw: _FakeResp())
    r = client.get("/api/exchange-rate")
    assert r.status_code == 200
    assert r.json() == {"eur": 0.92}


def test_exchange_rate_returns_null_on_error(client, monkeypatch):
    import api.exchange_rate as _er_mod

    def _fail(*a, **kw):
        raise OSError("network down")

    monkeypatch.setattr(_er_mod.urllib.request, "urlopen", _fail)
    r = client.get("/api/exchange-rate")
    assert r.status_code == 200
    assert r.json() == {"eur": None}


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

def test_cors_header_present(client):
    r = client.get("/api/pricing", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 200
    assert "access-control-allow-origin" in r.headers
