"""
aetherlink/main.py — FastAPI application factory

Registers all routers and returns the app instance.
Server startup is handled by run.py (uvicorn).
"""

from fastapi import FastAPI
from .routes import status, execute, play

app = FastAPI(title="AetherLink", version="0.1.0", docs_url=None, redoc_url=None)

app.include_router(status.router)
app.include_router(execute.router)
app.include_router(play.router)
