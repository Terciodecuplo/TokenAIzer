"""
Proxy subprocess lifecycle management.
The proxy is stopped by default; call start() to spawn mitmdump.
"""
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

_proc: Optional[subprocess.Popen] = None

PROXY_PORT = 8080
_INTERCEPTOR = Path(__file__).parent / "interceptor.py"
_UPSTREAM = "https://api.anthropic.com"


def _build_cmd() -> list[str]:
    return [
        "mitmdump",
        "--mode", f"reverse:{_UPSTREAM}",
        "-p", str(PROXY_PORT),
        "-s", str(_INTERCEPTOR),
        "--quiet",
    ]


def start() -> dict:
    global _proc
    if _proc is not None and _proc.poll() is None:
        return {"status": "running", "port": PROXY_PORT}

    _proc = subprocess.Popen(
        _build_cmd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    # Give the process a moment to either bind the port or fail
    time.sleep(0.8)
    if _proc.poll() is not None:
        stderr = _proc.stderr.read().decode(errors="replace")
        _proc = None
        if "address already in use" in stderr.lower() or "eaddrinuse" in stderr.lower():
            return {"status": "error", "error": "port_in_use",
                    "message": f"Port {PROXY_PORT} is already in use"}
        return {"status": "error", "error": "startup_failed", "message": stderr[:500]}

    return {"status": "running", "port": PROXY_PORT}


def stop() -> dict:
    global _proc
    if _proc is not None:
        _proc.terminate()
        try:
            _proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _proc.kill()
            _proc.wait()
        _proc = None
    return {"status": "stopped"}


def get_status() -> dict:
    global _proc
    if _proc is not None:
        if _proc.poll() is None:
            return {"status": "running", "port": PROXY_PORT}
        _proc = None  # clear stale reference after unexpected exit
    return {"status": "stopped", "port": None}
