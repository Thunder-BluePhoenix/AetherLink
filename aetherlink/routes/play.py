# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licenses is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licenses for the specific language governing permissions and
# limitations under the Licenses.

"""
aetherlink/routes/play.py — POST /play  |  GET /play/status

Audio streaming via yt-dlp + headless player.
start_stream / stop_stream run in a thread (blocking I/O).
"""

import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..auth import verify_aether_key
from ..services.media import (
    get_volume,
    now_playing,
    set_volume,
    start_stream,
    stop_stream,
)

router = APIRouter(dependencies=[Depends(verify_aether_key)])


class PlayRequest(BaseModel):
    action: str       # "play" | "stop"
    query:  str = ""  # search query (required for "play")


class VolumeRequest(BaseModel):
    level: int        # 0–100


@router.post("/play")
async def play(req: PlayRequest):
    if req.action == "play":
        if not req.query:
            return {"status": "error", "message": "query is required for action=play"}
        # yt-dlp + subprocess.Popen are blocking — run in thread
        return await asyncio.to_thread(start_stream, req.query)

    if req.action == "stop":
        return await asyncio.to_thread(stop_stream)

    return {"status": "error", "message": f"Unknown action: '{req.action}'"}


@router.get("/play/status")
async def play_status():
    """Return what is currently playing and system volume."""
    return {
        "now_playing": now_playing(),
        "volume":      get_volume(),
    }


@router.post("/play/volume")
async def volume(req: VolumeRequest):
    """Set system volume (0–100)."""
    return set_volume(req.level)
