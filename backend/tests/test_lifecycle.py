"""Tests for proxy lifecycle management (start/stop idempotency)."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import proxy.lifecycle as lc


def _reset():
    lc._proc = None


def test_get_status_default_stopped():
    _reset()
    status = lc.get_status()
    assert status["status"] == "stopped"
    assert status["port"] is None


def test_stop_idempotent_when_already_stopped():
    _reset()
    result = lc.stop()
    assert result == {"status": "stopped"}


def test_start_returns_running_if_already_running():
    _reset()
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None  # still alive
    lc._proc = mock_proc

    result = lc.start()
    assert result["status"] == "running"
    assert result["port"] == lc.PROXY_PORT
    # Popen should NOT be called again
    mock_proc.poll.assert_called()


def test_stop_terminates_process():
    _reset()
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    lc._proc = mock_proc

    result = lc.stop()
    mock_proc.terminate.assert_called_once()
    assert result == {"status": "stopped"}
    assert lc._proc is None


def test_get_status_clears_stale_reference():
    _reset()
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 1  # process exited
    lc._proc = mock_proc

    status = lc.get_status()
    assert status["status"] == "stopped"
    assert lc._proc is None


def test_start_detects_port_in_use():
    _reset()
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 1  # died immediately
    mock_proc.stderr.read.return_value = b"OSError: [Errno 48] Address already in use"

    with patch("proxy.lifecycle.subprocess.Popen", return_value=mock_proc), \
         patch("proxy.lifecycle.time.sleep"):
        result = lc.start()

    assert result["status"] == "error"
    assert result["error"] == "port_in_use"
    assert lc._proc is None
