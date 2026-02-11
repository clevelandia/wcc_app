# Development Setup

## Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
PYTHONPATH=backend pytest -q
```
