"""
aetherlink/routes/status.py — GET /status

Health-check endpoint. No auth required — returns version and uptime.
"""

import time
from fastapi import APIRouter
from .. import __version__

router = APIRouter()
_start_time = time.time()


@router.get("/status")
async def get_status():
    uptime_seconds = int(time.time() - _start_time)
    return {
        "status": "ok",
        "version": __version__,
        "uptime_seconds": uptime_seconds,
    }
