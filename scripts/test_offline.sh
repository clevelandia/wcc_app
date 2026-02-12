#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"
if python -c "import fastapi, pydantic" >/dev/null 2>&1; then
  echo 'Running backend tests (offline-compatible)...'
  python -m pytest
else
  echo 'Skipping backend tests: fastapi/pydantic are not available in this offline environment.'
fi

echo 'Running frontend node built-in tests (offline-compatible)...'
cd "$ROOT_DIR/frontend"
node --test tests/**/*.test.mjs
