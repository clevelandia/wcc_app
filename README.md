# Whatcom Civic Watch

Whatcom Civic Watch is a civic research application for full Whatcom County Council history.

## Quick Start

```bash
docker compose up -d --build
```

Backend API: `http://localhost:8000/api`  
Frontend UI: `http://localhost:3000`

## Ingestion commands

Run backfill for all years available from the Legistar API:

```bash
cw ingest --source whatcom_legistar_api --mode backfill
```

Optional bounded backfill window for faster testing:

```bash
cw ingest --source whatcom_legistar_api --mode backfill --from 2020-01-01 --to 2021-12-31
```

Run incremental updates (scheduled every 30 minutes by default):

```bash
cw ingest --all --mode incremental
```

## Confirm that data exists

1. Open `http://localhost:3000/meetings` and verify multiple years of timeline data.
2. Run a search at `http://localhost:3000/search` for a known term (example: `ordinance`).
3. Check jobs at `http://localhost:3000/jobs` and confirm completed ingest jobs with processed counts.

## Notes

- Data storage uses PostgreSQL FTS indexes for search.
- Meeting agenda and minutes PDFs are downloaded to object storage (`/data/object_storage`) and text is extracted for document search/citations.
- No mock data is used on production paths.
