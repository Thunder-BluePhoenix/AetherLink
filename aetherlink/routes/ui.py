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
aetherlink/routes/ui.py — Browser dashboard

Serves the single-page dashboard at GET /.
No auth required to load the page — the JS prompts for and stores the key.
"""

import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

_STATIC = os.path.join(os.path.dirname(__file__), "..", "static")


@router.get("/", include_in_schema=False)
async def dashboard() -> FileResponse:
    return FileResponse(os.path.join(_STATIC, "index.html"), media_type="text/html")
