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
aetherlink/auth.py — Request authentication

Verifies the X-Aether-Key header on every protected route.
Returns 403 on mismatch — no detail leaked to the caller.
"""

from fastapi import Header, HTTPException, status
from .config import settings


async def verify_aether_key(x_aether_key: str = Header(...)) -> None:
    # Also reject if AETHER_KEY was never set in .env
    if not settings.aether_key or x_aether_key != settings.aether_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
