"""
mitmproxy inline script for TokenAIzer.
Run via mitmdump: mitmdump --mode reverse:https://api.anthropic.com -p 8080 -s interceptor.py
"""
import json
import logging
import sys
from pathlib import Path
from typing import Iterator, Optional

from mitmproxy import http

# Ensure the backend package is importable when run as a subprocess
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.usage import write_usage_event
from proxy.sse import accumulate_sse_usage

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_model(flow: http.HTTPFlow) -> Optional[str]:
    try:
        return json.loads(flow.request.content).get("model")
    except (json.JSONDecodeError, ValueError, AttributeError):
        return None


def _extract_usage(usage_obj: dict) -> dict:
    thinking = (
        usage_obj.get("thinking_tokens")
        or (usage_obj.get("input_tokens_details") or {}).get("thinking_tokens")
        or 0
    )
    return {
        "input_tokens":           usage_obj.get("input_tokens", 0),
        "output_tokens":          usage_obj.get("output_tokens", 0),
        "thinking_tokens":        thinking,
        "cache_creation_tokens":  usage_obj.get("cache_creation_input_tokens", 0),
        "cache_read_tokens":      usage_obj.get("cache_read_input_tokens", 0),
    }


# ---------------------------------------------------------------------------
# mitmproxy hooks
# ---------------------------------------------------------------------------

def responseheaders(flow: http.HTTPFlow) -> None:
    """Enable streaming mode for SSE responses."""
    if "text/event-stream" in flow.response.headers.get("content-type", ""):
        model = _get_model(flow)
        flow.response.stream = _make_sse_streamer(model)


def response(flow: http.HTTPFlow) -> None:
    """Extract and persist usage from non-streaming JSON responses."""
    if "text/event-stream" in flow.response.headers.get("content-type", ""):
        return  # handled via streaming in responseheaders

    model = _get_model(flow)
    try:
        resp_json = json.loads(flow.response.content)
        usage = resp_json.get("usage")
        if usage and model:
            write_usage_event(model, _extract_usage(usage), source="proxy")
    except (json.JSONDecodeError, ValueError):
        pass


# ---------------------------------------------------------------------------
# SSE streaming
# ---------------------------------------------------------------------------

def _make_sse_streamer(model: Optional[str]):
    """Return a streaming callable that captures usage from SSE chunks."""

    def _streamer(chunks: Iterator[bytes]) -> Iterator[bytes]:
        buffer = ""
        last_usage: Optional[dict] = None
        for chunk in chunks:
            yield chunk
            text = chunk.decode("utf-8", errors="replace")
            buffer, seen_usage = accumulate_sse_usage(text, buffer)
            if seen_usage is not None:
                last_usage = seen_usage

        if last_usage is not None and model:
            write_usage_event(model, _extract_usage(last_usage), source="proxy")
        elif last_usage is None:
            log.warning("SSE stream ended without parseable usage data for model=%s", model)

    return _streamer
