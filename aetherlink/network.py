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
aetherlink/network.py — Network address detection

Detects LAN IPv4, global IPv6, and whether the machine is
reachable from the internet. Uses UDP "connect trick" — no
actual packets are sent, just triggers OS route lookup.
"""

import socket


def get_lan_ipv4() -> str | None:
    """Return the outgoing LAN IPv4 address (e.g. 192.168.x.x)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 1))
            return s.getsockname()[0]
    except OSError:
        return None


def get_global_ipv6() -> str | None:
    """Return the global-routable IPv6 address (2xxx: prefix)."""
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as s:
            s.connect(("2001:4860:4860::8888", 1))
            ip = s.getsockname()[0]
            # Strip zone ID (%interface) if present
            return ip.split("%")[0]
    except OSError:
        return None


def is_globally_reachable() -> bool:
    """True if the machine has a global IPv6 address (not just link-local)."""
    ip = get_global_ipv6()
    return ip is not None and ip.startswith("2")
