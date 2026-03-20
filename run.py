"""
run.py — AetherLink server entry point

Starts uvicorn bound to all IPv6 interfaces on the configured port.

Usage:
    python run.py
"""

import uvicorn
from aetherlink.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "aetherlink.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
