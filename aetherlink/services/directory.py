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
aetherlink/services/directory.py — Path map and directory open

Loads path_map.json on first use (lazy) and opens directories
via the OS shell. Accepts only mapped project names — no raw
paths are accepted from outside.
"""

import json
import os
from pathlib import Path

from ..config import settings

# In-memory map; populated on first call to get_path()
_path_map: dict[str, str] = {}
_loaded = False


def _load() -> None:
    global _path_map, _loaded
    map_file = Path(settings.path_map_file)
    if not map_file.exists():
        _loaded = True
        return
    with open(map_file, encoding="utf-8") as f:
        data = json.load(f)
    # Strip comment keys (prefixed with _)
    _path_map = {k: v for k, v in data.items() if not k.startswith("_")}
    _loaded = True


def reload() -> None:
    """Force a reload of path_map.json (hot-reload without restart)."""
    global _loaded
    _loaded = False
    _load()


def get_path(name: str) -> str | None:
    """Return the local path for a project keyword, or None if unknown."""
    if not _loaded:
        _load()
    return _path_map.get(name)


def list_projects() -> list[str]:
    """Return all registered project keywords."""
    if not _loaded:
        _load()
    return list(_path_map.keys())


def open_directory(name: str) -> dict:
    """
    Open the mapped project directory in Windows Explorer.
    Returns a structured result dict.
    """
    path = get_path(name)
    if path is None:
        return {
            "status": "error",
            "message": f"Unknown project: '{name}'. "
                       f"Known projects: {list_projects()}",
        }
    if not os.path.isdir(path):
        return {
            "status": "error",
            "message": f"Path not found on disk: {path}",
        }
    os.startfile(path)
    return {"status": "ok", "project": name, "path": path}
