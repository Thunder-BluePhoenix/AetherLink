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
tests/conftest.py — Shared pytest fixtures
"""

import pytest
from fastapi.testclient import TestClient

from aetherlink.config import settings
from aetherlink.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI test client — no real server started."""
    return TestClient(app)


@pytest.fixture(scope="session")
def auth(client) -> dict:
    """Valid X-Aether-Key header for protected routes."""
    return {"X-Aether-Key": settings.aether_key}


@pytest.fixture(scope="session")
def bad_auth() -> dict:
    """An intentionally wrong auth header."""
    return {"X-Aether-Key": "00000000-0000-0000-0000-000000000000"}
