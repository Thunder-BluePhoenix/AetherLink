"""
aetherlink/routes/play.py — POST /play

Handles audio streaming actions via yt-dlp and a headless player.

Phase 3 implementation.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth import verify_aether_key

# TODO (Phase 3): from ..services.media import start_stream, stop_stream

router = APIRouter(dependencies=[Depends(verify_aether_key)])


class PlayRequest(BaseModel):
    action: str      # "play" | "stop"
    query: str = ""  # search query (for "play")


@router.post("/play")
async def play(req: PlayRequest):
    # TODO (Phase 3): dispatch to media service
    return {"status": "not_implemented", "action": req.action}
