"""
Persistence layer tests.
Uses an in-memory SQLite DB — no files written to disk.
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# Fixture: redirect DB_PATH to :memory: before any module imports run
# ---------------------------------------------------------------------------

import sqlite3

import db.database as _db_mod

_ORIGINAL_DB_PATH = _db_mod.DB_PATH


@pytest.fixture(autouse=True)
def in_memory_db(tmp_path, monkeypatch):
    """
    Point DB_PATH at a fresh temp file so each test gets an isolated DB.
    (True :memory: can't be shared across connections easily; a tmp file is
    the next-simplest option while still being cleaned up automatically.)
    """
    db_file = tmp_path / "test.sqlite"
    monkeypatch.setattr(_db_mod, "DB_PATH", db_file)
    _db_mod.init_db()
    yield
    monkeypatch.setattr(_db_mod, "DB_PATH", _ORIGINAL_DB_PATH)


# ---------------------------------------------------------------------------
# Imports after fixture ensures correct DB_PATH is in place at call time
# ---------------------------------------------------------------------------

from db.pricing import get_all_pricing, upsert_pricing
from db.usage import get_usage_history, get_usage_summary, write_usage_event

# ---------------------------------------------------------------------------
# Usage event tests
# ---------------------------------------------------------------------------

def test_write_usage_event_defaults_absent_fields_to_zero():
    event_id = write_usage_event("claude-sonnet-4-6", {"input_tokens": 10}, source="proxy")
    assert event_id == 1
    rows = get_usage_history()
    assert len(rows) == 1
    row = rows[0]
    assert row["output_tokens"] == 0
    assert row["thinking_tokens"] == 0
    assert row["cache_creation_tokens"] == 0
    assert row["cache_read_tokens"] == 0


def test_get_usage_history_no_filters_returns_all():
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 1}, source="proxy")
    write_usage_event("claude-haiku-4-5", {"input_tokens": 2}, source="manual")
    rows = get_usage_history()
    assert len(rows) == 2


def test_get_usage_history_filter_by_source_excludes_other():
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 1}, source="proxy")
    write_usage_event("claude-haiku-4-5", {"input_tokens": 2}, source="manual")

    proxy_rows = get_usage_history(source="proxy")
    assert len(proxy_rows) == 1
    assert proxy_rows[0]["source"] == "proxy"

    manual_rows = get_usage_history(source="manual")
    assert len(manual_rows) == 1
    assert manual_rows[0]["source"] == "manual"


def test_get_usage_history_filter_by_model_and_date_range():
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 5}, source="proxy")
    write_usage_event("claude-haiku-4-5",  {"input_tokens": 3}, source="proxy")

    rows = get_usage_history(model="claude-sonnet-4-6")
    assert len(rows) == 1
    assert rows[0]["model"] == "claude-sonnet-4-6"

    # date_from far in the future → no results
    rows_future = get_usage_history(date_from="2099-01-01T00:00:00+00:00")
    assert rows_future == []


def test_get_usage_summary_per_model_totals_and_global():
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 100, "output_tokens": 50}, source="proxy")
    write_usage_event("claude-sonnet-4-6", {"input_tokens": 200, "output_tokens": 100}, source="proxy")
    write_usage_event("claude-haiku-4-5",  {"input_tokens": 10,  "output_tokens": 5},  source="manual")

    summary = get_usage_summary()
    assert "models" in summary
    assert "total" in summary

    by_model = {m["model"]: m for m in summary["models"]}
    assert by_model["claude-sonnet-4-6"]["input_tokens"] == 300
    assert by_model["claude-sonnet-4-6"]["output_tokens"] == 150
    assert by_model["claude-haiku-4-5"]["input_tokens"] == 10

    assert summary["total"]["input_tokens"] == 310
    assert summary["total"]["output_tokens"] == 155
    assert "estimated_cost" in summary["total"]


# ---------------------------------------------------------------------------
# Pricing tests
# ---------------------------------------------------------------------------

def test_default_seed_rows_exist_after_init_db():
    rows = get_all_pricing()
    models = {r["model"] for r in rows}
    assert "claude-sonnet-4-6" in models
    assert "claude-haiku-4-5" in models
    assert "claude-opus-4-6" in models
    for r in rows:
        assert r["input_price_per_million"] > 0
        assert r["output_price_per_million"] > 0


def test_seed_is_idempotent():
    _db_mod.init_db()  # run again
    rows = get_all_pricing()
    models = [r["model"] for r in rows]
    # No duplicates — each model appears exactly once
    assert len(models) == len(set(models))


def test_upsert_pricing_updates_without_duplicates():
    upsert_pricing("claude-sonnet-4-6", {
        "input_price_per_million": 999.0,
        "output_price_per_million": 888.0,
    })
    rows = get_all_pricing()
    sonnet = next(r for r in rows if r["model"] == "claude-sonnet-4-6")
    assert sonnet["input_price_per_million"] == 999.0
    assert sonnet["output_price_per_million"] == 888.0
    # Still only one row per model
    assert sum(1 for r in rows if r["model"] == "claude-sonnet-4-6") == 1


def test_get_all_pricing_returns_all_seeded_models():
    rows = get_all_pricing()
    assert len(rows) == 3  # sonnet, haiku, opus
