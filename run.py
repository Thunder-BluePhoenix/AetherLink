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
run.py — AetherLink server entry point

Starts uvicorn bound to all IPv6 interfaces on the configured port.

Usage:
    python run.py
"""

import uvicorn
from aetherlink.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "aetherlink.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
