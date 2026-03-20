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
aetherlink/routes/execute.py — POST /execute

Dispatches authenticated execute requests to the service layer.
All actions are sandboxed — no raw paths or commands reach the OS.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..auth import verify_aether_key
from ..services.directory import list_projects, open_directory
from ..services.media import set_volume
from ..services.shell import list_commands, run_command

router = APIRouter(dependencies=[Depends(verify_aether_key)])


class ExecuteRequest(BaseModel):
    action: str          # "open_directory" | "run_command" | "set_volume"
    target: str = ""     # project keyword (for open_directory / run_command)
    command: str = ""    # allowlisted command name (for run_command)
    level: int = 50      # 0–100 (for set_volume — Phase 3)


@router.post("/execute")
async def execute(req: ExecuteRequest):
    if req.action == "open_directory":
        return open_directory(req.target)

    if req.action == "run_command":
        return run_command(req.command, req.target)

    if req.action == "set_volume":
        return set_volume(req.level)

    return {
        "status": "error",
        "message": f"Unknown action: '{req.action}'",
    }


@router.get("/execute/meta")
async def execute_meta():
    """Return available projects and allowlisted commands (for Lambda/debugging)."""
    return {
        "projects": list_projects(),
        "commands": list_commands(),
    }
