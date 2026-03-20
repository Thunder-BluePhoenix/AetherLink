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
aetherlink/services/shell.py — Sandboxed shell interface

Rules:
  - Only commands in COMMAND_ALLOWLIST may be executed.
  - The working directory is always pinned to a mapped project path.
  - Raw user input is never passed to the shell (shell=False always).
  - Execution is bounded by TIMEOUT_SECONDS.
"""

import subprocess
from pathlib import Path

from .directory import get_path, list_projects

# ---------------------------------------------------------------------------
# Allowlist — add entries here to expose new commands to Alexa
# Format:  "spoken name": [argv list]
# ---------------------------------------------------------------------------
COMMAND_ALLOWLIST: dict[str, list[str]] = {
    "git pull":      ["git", "pull"],
    "git status":    ["git", "status"],
    "git log":       ["git", "log", "--oneline", "-10"],
    "git diff":      ["git", "diff", "--stat"],
    "npm start":     ["npm", "start"],
    "npm install":   ["npm", "install"],
    "npm run build": ["npm", "run", "build"],
    "pip install":   ["pip", "install", "-r", "requirements.txt"],
}

TIMEOUT_SECONDS = 15


def list_commands() -> list[str]:
    """Return all allowlisted command names."""
    return list(COMMAND_ALLOWLIST.keys())


def run_command(command: str, project: str) -> dict:
    """
    Execute an allowlisted command inside the given project's directory.
    Returns a structured result dict with stdout/stderr.
    """
    argv = COMMAND_ALLOWLIST.get(command)
    if argv is None:
        return {
            "status": "error",
            "message": f"Command not in allowlist: '{command}'. "
                       f"Allowed: {list_commands()}",
        }

    cwd = get_path(project)
    if cwd is None:
        return {
            "status": "error",
            "message": f"Unknown project: '{project}'. "
                       f"Known projects: {list_projects()}",
        }
    if not Path(cwd).is_dir():
        return {
            "status": "error",
            "message": f"Project path not found on disk: {cwd}",
        }

    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            shell=False,  # never True — no raw input to shell
        )
        return {
            "status": "ok",
            "command": command,
            "project": project,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": f"Command timed out after {TIMEOUT_SECONDS}s",
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"Executable not found: '{argv[0]}' — is it installed?",
        }
