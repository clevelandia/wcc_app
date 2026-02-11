from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Whatcom Civic Watch")
app.include_router(router, prefix="/api")
