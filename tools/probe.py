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
tools/probe.py — AetherLink Phase 1 Connectivity Probe

Temporary IPv6 TCP listener used to verify that the machine is
reachable from the public internet on the AetherLink port.
Not part of the main application; replaced by the FastAPI server
once Phase 2 is complete.

Usage:
    python tools/probe.py
    python tools/probe.py --port 58008

Stop: Ctrl+C
"""

import argparse
import datetime
import socket


DEFAULT_PORT = 58008


def _log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def run(port: int) -> None:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # IPV6_V6ONLY = 0: accept both IPv6 and IPv4-mapped connections on Windows
        server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        server.bind(("::", port))
        server.listen(5)
        _log(f"AetherLink probe listening on [::]:{port}")
        _log("Waiting for connections... (Ctrl+C to stop)\n")

        while True:
            try:
                conn, addr = server.accept()
                with conn:
                    src_ip, src_port = addr[0], addr[1]
                    _log(f"CONNECT  [{src_ip}]:{src_port}")
                    conn.sendall(b"PONG - AetherLink Phase 1 OK\n")
                    _log(f"PONG  -> [{src_ip}]:{src_port}")
            except KeyboardInterrupt:
                _log("Probe stopped.")
                break
            except OSError as exc:
                _log(f"ERROR: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AetherLink IPv6 connectivity probe")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"TCP port to listen on (default: {DEFAULT_PORT})")
    args = parser.parse_args()
    run(args.port)


if __name__ == "__main__":
    main()
