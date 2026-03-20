"""
aetherlink/routes/execute.py — POST /execute

Handles directory-open and shell-command actions.
All actions are sandboxed via services/shell.py and services/directory.py.

Phase 2 implementation.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth import verify_aether_key

# TODO (Phase 2): from ..services.shell import run_command
# TODO (Phase 2): from ..services.directory import open_directory

router = APIRouter(dependencies=[Depends(verify_aether_key)])


class ExecuteRequest(BaseModel):
    action: str          # "open_directory" | "run_command" | "set_volume"
    target: str = ""     # project name (for open_directory / run_command)
    command: str = ""    # allowlisted command name (for run_command)
    level: int = 50      # 0-100 (for set_volume)


@router.post("/execute")
async def execute(req: ExecuteRequest):
    # TODO (Phase 2): dispatch to service layer
    return {"status": "not_implemented", "action": req.action}
