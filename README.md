# Whatcom Civic Watch

Whatcom Civic Watch is a config-driven civic intelligence platform for municipal data ingestion, indexing, analysis, and organizer-facing context generation.

## Monorepo Layout

- `backend/` FastAPI + ingestion + analysis + search + RAG services.
- `frontend/` Next.js dashboard for meetings, ordinance diffs, search, and briefs.
- `config/` Source configuration (`sources.yaml`, `movement_sources.yaml`).
- `tests/` Automated acceptance coverage.
- `docs/` Architecture and deployment notes.

## Quick Start

```bash
docker compose up --build
```

Backend API: `http://localhost:8000/api`
Frontend UI: `http://localhost:3000`

## Security + Compliance

- Robots policy and fetch headers are captured in provenance logs.
- RSS ingestion stores metadata/snippets only.
- Generated brief output labels interpretation explicitly.
- Drafting assistants are assistive only and require user review before publication.
