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
aetherlink/cli/app.py — AetherLink TUI

Interactive terminal dashboard built with Textual.

Layout:
  Left  — Network info | Probe status | Agent status | Media status
  Right — Live log (probe connections + agent stdout)

Keybindings:
  P — toggle probe  (Phase 1 connectivity test)
  A — toggle agent  (Phase 2+ FastAPI server)
  C — clear log
  Q — quit

Probe and Agent are mutually exclusive — both use port 58008.
"""

import asyncio
import datetime
import socket
import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, RichLog, Static

from ..config import settings
from ..network import get_global_ipv6, get_lan_ipv4, is_globally_reachable
from ..services.media import get_volume, now_playing


# ---------------------------------------------------------------------------
# Left-panel widget
# ---------------------------------------------------------------------------

class StatusPanel(Static):
    """Displays network, probe, agent, and media status."""

    probe_active: reactive[bool] = reactive(False)
    agent_active: reactive[bool] = reactive(False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._lan4   = get_lan_ipv4()    or "unavailable"
        self._ipv6   = get_global_ipv6() or "unavailable"
        self._reach  = is_globally_reachable()
        self._key_ok = bool(settings.aether_key)

    def render(self) -> str:
        reach = "[green]YES[/green]"  if self._reach    else "[yellow]NO[/yellow]"
        probe = "[green]ON[/green]"   if self.probe_active else "[red]OFF[/red]"
        agent = "[green]ON[/green]"   if self.agent_active else "[red]OFF[/red]"
        key   = "[green]SET[/green]"  if self._key_ok      else "[yellow]NOT SET[/yellow]"

        track = now_playing()
        vol   = get_volume()
        if track:
            title   = track.get("title", "")[:30]
            player  = track.get("player", "")
            media_s = f"  [green]{title}[/green]\n  [dim]via {player}[/dim]"
        else:
            media_s = "  [dim]idle[/dim]"

        vol_s = f"{vol}%" if vol is not None else "N/A"

        return (
            f"[bold dim]NETWORK[/bold dim]\n"
            f"  [dim]LAN IPv4[/dim]  {self._lan4}\n"
            f"  [dim]IPv6[/dim]      {self._ipv6[:36]}\n"
            f"  [dim]Routable[/dim]  {reach}\n"
            f"  [dim]Port[/dim]      {settings.port}\n\n"
            f"[bold dim]PROBE[/bold dim]   [P]\n"
            f"  Status     {probe}\n\n"
            f"[bold dim]AGENT[/bold dim]   [A]\n"
            f"  Status     {agent}\n"
            f"  Auth key   {key}\n\n"
            f"[bold dim]MEDIA[/bold dim]\n"
            f"{media_s}\n"
            f"  [dim]Volume[/dim]    {vol_s}"
        )


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class AetherLinkApp(App):
    """AetherLink terminal dashboard."""

    TITLE = "AetherLink"

    CSS = """
    Screen {
        background: $surface;
    }
    #layout {
        height: 1fr;
        padding: 0 1;
    }
    #left {
        width: 46;
        height: 100%;
        border: round $primary;
        padding: 1 2;
        margin-right: 1;
    }
    #right {
        width: 1fr;
        height: 100%;
        border: round $primary;
        padding: 1 2;
    }
    .panel-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    Rule {
        margin: 1 0;
        color: $primary-darken-3;
    }
    """

    BINDINGS = [
        Binding("p", "toggle_probe", "Probe"),
        Binding("a", "toggle_agent", "Agent"),
        Binding("c", "clear_log",   "Clear"),
        Binding("q", "quit",        "Quit"),
    ]

    # Probe state
    _probe_task: asyncio.Task | None = None
    _probe_server: asyncio.Server | None = None

    # Agent state
    _agent_task: asyncio.Task | None = None
    _agent_proc: asyncio.subprocess.Process | None = None

    # ------------------------------------------------------------------ compose

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="left"):
                yield Label("STATUS", classes="panel-title")
                yield StatusPanel(id="status-panel")
            with Vertical(id="right"):
                yield Label("LOG", classes="panel-title")
                yield RichLog(id="log", highlight=True, markup=True, auto_scroll=True)
        yield Footer()

    def on_mount(self) -> None:
        if not settings.aether_key:
            self._log("[yellow]No AETHER_KEY set. Run: python scripts/gen_key.py[/yellow]")
        self._log("AetherLink TUI ready.")
        self._log(f"  LAN  {get_lan_ipv4()}")
        self._log(f"  IPv6 {get_global_ipv6()}")
        self._log("")
        self.action_toggle_probe()  # auto-start probe

    # ------------------------------------------------------------------ probe

    def action_toggle_probe(self) -> None:
        if self._probe_task and not self._probe_task.done():
            self._stop_probe()
        else:
            if self._agent_task and not self._agent_task.done():
                self._stop_agent()
            self._probe_task = asyncio.create_task(self._run_probe())

    def _stop_probe(self) -> None:
        if self._probe_server:
            self._probe_server.close()
            self._probe_server = None
        self._set_probe(False)
        self._log("[yellow]Probe stopped.[/yellow]")

    async def _run_probe(self) -> None:
        port = settings.port
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # IPV6_V6ONLY=0: dual-stack — LAN IPv4, LAN IPv6, public IPv6
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.setblocking(False)
            sock.bind(("::", port))
            sock.listen(5)

            self._probe_server = await asyncio.start_server(
                self._handle_probe_connection, sock=sock
            )
            self._set_probe(True)
            self._log(f"[green]Probe active — [::]:{port} (dual-stack)[/green]")

            async with self._probe_server:
                await self._probe_server.serve_forever()

        except OSError as exc:
            self._log(f"[red]Probe error: {exc}[/red]")
        finally:
            self._set_probe(False)
            self._probe_server = None

    async def _handle_probe_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        addr = writer.get_extra_info("peername")
        src  = f"[{addr[0]}]:{addr[1]}"
        self._log(f"[cyan]PROBE CONNECT[/cyan]  {src}")
        try:
            writer.write(b"PONG - AetherLink Phase 1 OK\n")
            await writer.drain()
            self._log(f"[green]PONG[/green]          -> {src}")
        finally:
            writer.close()
            await writer.wait_closed()

    # ------------------------------------------------------------------ agent

    def action_toggle_agent(self) -> None:
        if self._agent_task and not self._agent_task.done():
            self._stop_agent()
        else:
            if self._probe_task and not self._probe_task.done():
                self._stop_probe()
            self._agent_task = asyncio.create_task(self._run_agent())

    def _stop_agent(self) -> None:
        if self._agent_proc:
            try:
                self._agent_proc.terminate()
            except ProcessLookupError:
                pass
            self._agent_proc = None
        self._set_agent(False)
        self._log("[yellow]Agent stopped.[/yellow]")

    async def _run_agent(self) -> None:
        if not settings.aether_key:
            self._log("[red]Cannot start agent — AETHER_KEY not set.[/red]")
            self._log("[dim]Run: python scripts/gen_key.py[/dim]")
            return

        port = settings.port
        try:
            self._agent_proc = await asyncio.create_subprocess_exec(
                sys.executable, "run.py",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            self._set_agent(True)
            self._log(f"[green]Agent started — [::]:{port}[/green]")

            assert self._agent_proc.stdout
            async for line in self._agent_proc.stdout:
                text = line.decode(errors="replace").rstrip()
                if text:
                    self._log(f"[dim][agent][/dim] {text}")

        except Exception as exc:
            self._log(f"[red]Agent error: {exc}[/red]")
        finally:
            self._set_agent(False)
            self._agent_proc = None
            self._log("[yellow]Agent process ended.[/yellow]")

    # ------------------------------------------------------------------ helpers

    def _set_probe(self, value: bool) -> None:
        self.query_one(StatusPanel).probe_active = value

    def _set_agent(self, value: bool) -> None:
        self.query_one(StatusPanel).agent_active = value

    def _log(self, msg: str) -> None:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.query_one(RichLog).write(f"[dim]{ts}[/dim]  {msg}")

    def action_clear_log(self) -> None:
        self.query_one(RichLog).clear()
