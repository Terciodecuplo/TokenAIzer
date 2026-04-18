"""Unit tests for the SSE chunk accumulator in proxy/interceptor.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from proxy.sse import accumulate_sse_usage


def _event(data: str) -> str:
    return f"data: {data}\n\n"


def test_happy_path_usage_extracted():
    payload = '{"type":"message_delta","usage":{"input_tokens":10,"output_tokens":50}}'
    buffer, usage = accumulate_sse_usage(_event(payload), "")
    assert usage == {"input_tokens": 10, "output_tokens": 50}
    assert buffer == ""


def test_usage_updated_by_later_chunk():
    first = _event('{"type":"message_start","usage":{"input_tokens":5,"output_tokens":0}}')
    second = _event('{"type":"message_delta","usage":{"input_tokens":5,"output_tokens":30}}')

    buffer, u1 = accumulate_sse_usage(first, "")
    buffer, u2 = accumulate_sse_usage(second, buffer)

    assert u2["output_tokens"] == 30


def test_done_sentinel_ignored():
    buffer, usage = accumulate_sse_usage("data: [DONE]\n\n", "")
    assert usage is None
    assert buffer == ""


def test_no_usage_field_returns_none():
    payload = '{"type":"content_block_delta","delta":{"text":"hello"}}'
    buffer, usage = accumulate_sse_usage(_event(payload), "")
    assert usage is None


def test_partial_chunk_buffered():
    partial = "data: {\"type\":\"message_delta\","
    buffer, usage = accumulate_sse_usage(partial, "")
    # No complete event yet — usage must be None and buffer holds the partial line
    assert usage is None
    assert partial in buffer


def test_split_across_chunks_assembled():
    chunk1 = 'data: {"type":"message_delta","usage":'
    chunk2 = '{"input_tokens":7,"output_tokens":20}}\n\n'
    buffer, u1 = accumulate_sse_usage(chunk1, "")
    buffer, u2 = accumulate_sse_usage(chunk2, buffer)
    assert u2 == {"input_tokens": 7, "output_tokens": 20}


def test_malformed_json_ignored():
    bad = "data: {not valid json}\n\n"
    buffer, usage = accumulate_sse_usage(bad, "")
    assert usage is None
