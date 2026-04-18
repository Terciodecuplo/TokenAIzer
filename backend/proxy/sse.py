"""
Pure-Python SSE chunk parsing — no mitmproxy dependency.
Extracted here so unit tests can run without mitmproxy installed.
"""
import json
from typing import Optional


def accumulate_sse_usage(raw_text: str, buffer: str) -> tuple[str, Optional[dict]]:
    """
    Append raw_text to buffer, parse any complete SSE events (delimited by
    double newline), and return (updated_buffer, last_usage_seen_or_None).
    """
    buffer += raw_text
    last_usage: Optional[dict] = None
    while "\n\n" in buffer:
        event, buffer = buffer.split("\n\n", 1)
        for line in event.split("\n"):
            line = line.strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    data = json.loads(line[6:])
                    if "usage" in data:
                        last_usage = data["usage"]
                except (json.JSONDecodeError, ValueError):
                    pass
    return buffer, last_usage
