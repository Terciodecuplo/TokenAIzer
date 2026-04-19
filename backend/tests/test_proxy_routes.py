"""Integration tests for /api/proxy/* REST endpoints."""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

# Patch init_db so tests don't need a real SQLite file
with patch("db.database.init_db"):
    from main import app

client = TestClient(app)

_RUNNING = {"status": "running", "port": 8090}
_STOPPED = {"status": "stopped", "port": None}


def test_status_default_stopped():
    with patch("proxy.lifecycle.get_status", return_value=_STOPPED):
        r = client.get("/api/proxy/status")
    assert r.status_code == 200
    assert r.json()["status"] == "stopped"


def test_start_returns_running():
    with patch("proxy.lifecycle.start", return_value=_RUNNING):
        r = client.post("/api/proxy/start")
    assert r.status_code == 200
    assert r.json() == _RUNNING


def test_stop_returns_stopped():
    with patch("proxy.lifecycle.stop", return_value={"status": "stopped"}):
        r = client.post("/api/proxy/stop")
    assert r.status_code == 200
    assert r.json()["status"] == "stopped"


def test_start_already_running_idempotent():
    with patch("proxy.lifecycle.start", return_value=_RUNNING):
        r1 = client.post("/api/proxy/start")
        r2 = client.post("/api/proxy/start")
    assert r1.json()["status"] == "running"
    assert r2.json()["status"] == "running"


def test_status_after_start():
    with patch("proxy.lifecycle.start", return_value=_RUNNING), \
         patch("proxy.lifecycle.get_status", return_value=_RUNNING):
        client.post("/api/proxy/start")
        r = client.get("/api/proxy/status")
    assert r.json()["status"] == "running"
    assert r.json()["port"] == 8090


def test_status_after_stop():
    with patch("proxy.lifecycle.stop", return_value={"status": "stopped"}), \
         patch("proxy.lifecycle.get_status", return_value=_STOPPED):
        client.post("/api/proxy/stop")
        r = client.get("/api/proxy/status")
    assert r.json()["status"] == "stopped"
