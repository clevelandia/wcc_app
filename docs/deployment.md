# Deployment Notes

- Deploy backend behind a reverse proxy (Nginx/Traefik) with HTTPS.
- Use managed Postgres with `pgvector` enabled for production indexing.
- Run ingestion jobs in scheduled worker pods/containers with isolated network rules.
- Configure source cadence via `config/sources.yaml` and movement corpus via `config/movement_sources.yaml`.
