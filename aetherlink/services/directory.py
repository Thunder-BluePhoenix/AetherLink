"""
aetherlink/services/directory.py — Path map and directory open

Loads a JSON keyword→path map and opens directories via the OS.
Accepts only mapped project names — no raw paths from outside.

Phase 2 implementation.
"""

# TODO (Phase 2): load path_map.json on startup (hot-reload support)
# TODO (Phase 2): implement open_directory(project_name: str) -> dict
# TODO (Phase 2): implement get_path(project_name: str) -> str | None
