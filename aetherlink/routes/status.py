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
aetherlink/routes/status.py — GET /status

Health-check endpoint. No auth required.
"""

import time

from fastapi import APIRouter

from .. import __version__
from ..network import get_global_ipv6, get_lan_ipv4
from ..services.directory import list_projects
from ..services.shell import list_commands

router = APIRouter()
_start_time = time.time()


@router.get("/status")
async def get_status():
    return {
        "status": "ok",
        "version": __version__,
        "uptime_seconds": int(time.time() - _start_time),
        "network": {
            "lan_ipv4": get_lan_ipv4(),
            "global_ipv6": get_global_ipv6(),
        },
        "projects": list_projects(),
        "commands": list_commands(),
    }
