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
scripts/gen_key.py — One-time .env generator

Creates a .env file with a fresh UUID4 AETHER_KEY.
Safe to re-run — will not overwrite an existing .env.

Usage:
    python scripts/gen_key.py
"""

import uuid
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"


def main() -> None:
    if ENV_FILE.exists():
        print(f".env already exists at {ENV_FILE} — not overwriting.")
        print("Delete it manually if you want to regenerate the key.")
        return

    key = uuid.uuid4()
    ENV_FILE.write_text(
        f"# AetherLink environment — do not commit this file\n"
        f"AETHER_KEY={key}\n",
        encoding="utf-8",
    )
    print(f"Created {ENV_FILE}")
    print(f"AETHER_KEY = {key}")
    print("\nKeep this key secret — it authenticates every API request.")


if __name__ == "__main__":
    main()
