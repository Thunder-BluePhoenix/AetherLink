"""
aetherlink/auth.py — Request authentication

Verifies the X-Aether-Key header on every protected route.
Returns 403 on mismatch — no detail leaked to the caller.
"""

from fastapi import Header, HTTPException, status
from .config import settings


async def verify_aether_key(x_aether_key: str = Header(...)) -> None:
    # Also reject if AETHER_KEY was never set in .env
    if not settings.aether_key or x_aether_key != settings.aether_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
