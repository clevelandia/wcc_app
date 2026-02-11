from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.db import init_db

app = FastAPI(title='Whatcom Civic Watch')


@app.on_event('startup')
def startup() -> None:
    init_db()


app.include_router(router, prefix='/api')
