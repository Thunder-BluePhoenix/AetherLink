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
aetherlink/services/media.py — Audio streaming service

Flow:
  1. Receive a search query.
  2. Use yt-dlp (blocking, run in thread) to get the best audio stream URL.
  3. Launch a headless player (MPV preferred, VLC fallback) via subprocess.
  4. Track the player PID via psutil for reliable process-tree termination.
  5. Volume control via pycaw (Windows Core Audio API).

Player detection order:
  PATH → common Windows install paths (MPV then VLC).
"""

import os
import shutil
import subprocess

import psutil
import yt_dlp
from pycaw.pycaw import AudioUtilities

# ---------------------------------------------------------------------------
# Player detection
# ---------------------------------------------------------------------------

_MPV_PATHS = [
    r"C:\Program Files\mpv\mpv.exe",
    r"C:\Program Files (x86)\mpv\mpv.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\mpv\mpv.exe"),
]
_VLC_PATHS = [
    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
]


def _find_player() -> tuple[str, list[str]] | None:
    """Return (player_name, base_argv) for the first available headless player."""
    mpv = shutil.which("mpv")
    if mpv:
        return ("mpv", [mpv, "--no-video", "--really-quiet"])

    vlc = shutil.which("vlc")
    if vlc:
        return ("vlc", [vlc, "--intf", "dummy", "--no-video", "--play-and-exit"])

    for path in _MPV_PATHS:
        if os.path.isfile(path):
            return ("mpv", [path, "--no-video", "--really-quiet"])

    for path in _VLC_PATHS:
        if os.path.isfile(path):
            return ("vlc", [path, "--intf", "dummy", "--no-video", "--play-and-exit"])

    return None


# ---------------------------------------------------------------------------
# State — one active stream at a time
# ---------------------------------------------------------------------------

_player_proc: subprocess.Popen | None = None
_now_playing: dict = {}


def now_playing() -> dict:
    """Return metadata of the currently playing track, or empty dict."""
    return dict(_now_playing)


# ---------------------------------------------------------------------------
# yt-dlp URL extraction (blocking — call via asyncio.to_thread)
# ---------------------------------------------------------------------------

def _extract_stream(query: str) -> dict:
    """
    Use yt-dlp to find the best audio stream URL for the given search query.
    Returns a dict with keys: title, url, duration, thumbnail — or 'error'.
    """
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)

    if not info or not info.get("entries"):
        return {"error": "No results found for the query."}

    entry = info["entries"][0]

    # Prefer a direct URL; fall back to the last format entry
    url = entry.get("url")
    if not url and entry.get("formats"):
        url = entry["formats"][-1].get("url")

    if not url:
        return {"error": "Could not extract a stream URL from the result."}

    return {
        "title":     entry.get("title", "Unknown"),
        "url":       url,
        "duration":  entry.get("duration"),
        "thumbnail": entry.get("thumbnail"),
        "webpage":   entry.get("webpage_url"),
    }


# ---------------------------------------------------------------------------
# Playback
# ---------------------------------------------------------------------------

def start_stream(query: str) -> dict:
    """
    Stop any current stream, extract a URL for the query, and launch the player.
    This is blocking — wrap in asyncio.to_thread for async routes.
    """
    global _player_proc, _now_playing

    player = _find_player()
    if player is None:
        return {
            "status": "error",
            "message": (
                "No audio player found. Install MPV (recommended) or VLC:\n"
                "  winget install mpv.mpv\n"
                "  winget install VideoLAN.VLC"
            ),
        }

    # Stop any existing stream first
    _kill_player()

    stream = _extract_stream(query)
    if "error" in stream:
        return {"status": "error", "message": stream["error"]}

    player_name, base_argv = player
    argv = base_argv + [stream["url"]]

    _player_proc = subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _now_playing = {
        "title":    stream["title"],
        "duration": stream["duration"],
        "player":   player_name,
        "pid":      _player_proc.pid,
    }
    return {
        "status":  "playing",
        "title":   stream["title"],
        "player":  player_name,
        "pid":     _player_proc.pid,
    }


def stop_stream() -> dict:
    """Stop the currently playing stream."""
    global _player_proc, _now_playing
    if _player_proc is None:
        return {"status": "error", "message": "No stream is currently playing."}
    _kill_player()
    _now_playing = {}
    return {"status": "ok", "message": "Stream stopped."}


def _kill_player() -> None:
    """Kill the player process and its entire process tree."""
    global _player_proc
    if _player_proc is None:
        return
    try:
        parent = psutil.Process(_player_proc.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
    _player_proc = None


# ---------------------------------------------------------------------------
# Volume control (Windows Core Audio)
# ---------------------------------------------------------------------------

_volume: int = 50  # in-memory fallback when pycaw is unavailable


def set_volume(level: int) -> dict:
    """
    Set Windows system volume. level: 0–100.
    Always returns ok; falls back to in-memory state if pycaw unavailable.
    """
    global _volume
    level = max(0, min(100, level))
    _volume = level
    try:
        vol = AudioUtilities.GetSpeakers().EndpointVolume
        vol.SetMasterVolumeLevelScalar(level / 100.0, None)
    except Exception:
        pass  # pycaw unavailable — in-memory value is the effective volume
    return {"status": "ok", "volume": level}


def get_volume() -> int:
    """Return current system volume (0–100); falls back to in-memory value."""
    try:
        vol = AudioUtilities.GetSpeakers().EndpointVolume
        return round(vol.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return _volume
