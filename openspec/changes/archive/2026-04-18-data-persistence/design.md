## Context

The proxy-capture change established `backend/db/database.py` (SQLite init, WAL mode, table creation) and `backend/db/usage.py` (write + query functions). The `model_pricing` table exists but has no write path — `GET /api/pricing` returns an empty list and cost estimates in `get_usage_summary` are always zero because no pricing rows exist.

The three supported models are defined in the README: `claude-sonnet-4-6`, `claude-haiku-4-5`, `claude-opus-4-6`. Their prices are publicly available from Anthropic and will be hardcoded as seed data for v1.

## Goals / Non-Goals

**Goals:**
- Add `backend/db/pricing.py` with `upsert_pricing` and `get_all_pricing` functions
- Seed default pricing for all three supported models in `init_db()` (only if table is empty)
- Add `source` parameter to `get_usage_history` so callers can filter `proxy` vs `manual` events
- Write unit tests for all persistence functions using a temporary in-memory SQLite database

**Non-Goals:**
- Live pricing sync from LiteLLM or any external API (future change)
- EUR conversion (out of scope for persistence layer)
- Database migrations for schema changes (schema is already correct)

## Decisions

### 1. Seed pricing in `init_db()` with `INSERT OR IGNORE`

**Decision**: Add `INSERT OR IGNORE INTO model_pricing …` statements for each supported model in `init_db()`, so default prices are present after the very first run without requiring a separate seeding step.

**Rationale**: `INSERT OR IGNORE` is idempotent — if the user later updates pricing via a future sync job, those rows won't be overwritten on the next restart. No extra boot logic or migration table needed.

**Alternative considered**: Seed only when `SELECT COUNT(*) = 0` — slightly more explicit, but one extra query per startup for no benefit.

---

### 2. Separate `pricing.py` module (not merged into `usage.py`)

**Decision**: Put pricing functions in `backend/db/pricing.py` rather than adding them to `usage.py`.

**Rationale**: Usage events and pricing are distinct domain objects. Keeping them in separate modules prevents `usage.py` from becoming a catch-all and makes each file easier to test in isolation.

---

### 3. Tests use in-memory SQLite via `get_connection` monkeypatching

**Decision**: Unit tests override `DB_PATH` before importing the module under test, pointing it at `:memory:`. Each test gets a fresh `init_db()` call.

**Rationale**: No test fixtures on disk, no cleanup needed, fast. The SQLite in-memory mode is the closest possible simulation of the real DB without touching the filesystem.

**Alternative considered**: `tempfile.NamedTemporaryFile` — works but leaves files if a test crashes; in-memory is simpler.

## Risks / Trade-offs

- **Hardcoded prices go stale** → Document clearly that v1 prices are approximations; a future pricing-sync change should replace them. Add a comment in `pricing.py` with the date prices were set.
- **`get_usage_history` signature change** → Adding `source: Optional[str] = None` is backwards-compatible; all existing callers pass no `source` argument.
- **WAL mode + subprocess writes** → Already established in the proxy-capture design. Tests use in-memory DB which doesn't exercise WAL; this is acceptable because WAL is a connectivity concern, not a logic concern.
