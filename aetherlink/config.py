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
aetherlink/config.py — Application settings

Loads configuration from the .env file at the project root.
All values are read once at import time via pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Network
    host: str = "::"
    port: int = 58008

    # Security — optional here; auth.py raises 403 if empty at request time
    aether_key: str = ""  # set in .env; required for Phase 2 protected routes

    # Path map: loaded separately from path_map.json (see services/directory.py)
    path_map_file: str = "path_map.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Single shared instance imported everywhere
settings = Settings()
