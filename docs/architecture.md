# Architecture Overview

## Backend

- **Ingestion adapters** implement a shared `SourceAdapter` interface with discover/fetch/parse/link stages.
- **Validation** uses strict Pydantic models at parse time. Invalid records are quarantined.
- **Analysis** includes semantic ordinance diff and budget delta.
- **Search** provides lexical and semantic-style retrieval interfaces.
- **RAG** separates factual retrieval from movement-context retrieval.

## Frontend

- Dashboard-style Next.js UI with meeting coverage, semantic diff section, search panel, document citation references, and organizer brief area.

## Data Safety

- Public-source-only ingestion.
- Provenance fields (`source_id`, `content_hash`, `retrieved_at`, `robots_policy`) attached to normalized records.
