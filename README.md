# TokenAIzer

> Local token usage tracker for Anthropic LLM models.

TokenAIzer is a personal dashboard that monitors token consumption across Anthropic models — input, output, thinking, and cache — with estimated cost in USD and EUR. It runs entirely on your machine, with no external dependencies beyond the Anthropic API itself.

---

## Features

- Real-time token tracking via a local HTTP proxy
- Per-model breakdown: input, output, thinking, and cache tokens
- Estimated cost using live pricing data from LiteLLM
- Time-series chart with animated transitions
- Proxy lifecycle control (start / stop) from the dashboard
- Manual entry for sessions that bypass the proxy
- SQLite storage — no database server required

## Supported Models

- claude-sonnet-4-6
- claude-haiku-4-5
- claude-opus-4-6

## Architecture

TokenAIzer consists of two independent processes that share a local SQLite database:

```
[Claude Code / Agents]
        │
        │  ANTHROPIC_BASE_URL=localhost:8080
        ▼
[Proxy — Python]  ──────────────────────►  [SQLite]
        │                                      ▲
        │  forwards to api.anthropic.com        │
        ▼                                      │
[Anthropic API]                        [FastAPI REST]
                                               │
                                               ▼
                                     [Dashboard — Svelte]
```

- **Proxy** intercepts API traffic and extracts token usage from each response
- **FastAPI** exposes a REST API for the dashboard and proxy lifecycle control
- **Svelte + Chart.js** renders the dashboard as a local web interface
- **SQLite** persists all usage events and pricing data

## Tech Stack

| Layer | Technology |
|---|---|
| Proxy & API | Python, FastAPI |
| Database | SQLite |
| Frontend | Svelte, Chart.js |
| Pricing data | LiteLLM model prices JSON |

## Getting Started

> Prerequisites: Python 3.11+, Node.js 20.19.0+

```bash
# Clone the repository
git clone https://github.com/Terciodecuplo/TokenAIzer.git
cd TokenAIzer

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py

# Dashboard
cd dashboard
npm install
npm run dev
```

Set `ANTHROPIC_BASE_URL=http://localhost:8080` in any Anthropic client to route traffic through the proxy.

## Development

This project uses [OpenSpec](https://openspec.dev/) for spec-driven development. Specifications live in `openspec/specs/` alongside the code.

```bash
# View current specs
ls openspec/specs/

# Propose a new change (requires Claude Code)
/opsx:propose <feature-name>
```

## License

MIT — see [LICENSE](./LICENSE) for details.
