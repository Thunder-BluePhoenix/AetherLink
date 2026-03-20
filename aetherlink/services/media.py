"""
aetherlink/services/media.py — Audio streaming service

Uses yt-dlp to extract a stream URL from a search query,
then launches a headless player (MPV or VLC) via subprocess.
Tracks the player PID for stop/pause control.
Volume control via pycaw (Windows Core Audio).

Phase 3 implementation.
"""

# TODO (Phase 3): implement start_stream(query: str) -> dict
# TODO (Phase 3): implement stop_stream() -> dict
# TODO (Phase 3): implement set_volume(level: int) -> dict
