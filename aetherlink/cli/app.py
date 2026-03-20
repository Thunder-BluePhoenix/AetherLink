"""
aetherlink/cli/app.py — AetherLink TUI

Interactive terminal dashboard built with Textual.

Panels:
  Left  — Network info + probe status
  Right — Live connection log (scrollable)

Keybindings:
  P — toggle probe on/off
  C — clear log
  Q — quit

Phase 1: runs the IPv6/LAN connectivity probe.
Phase 2+: will also show FastAPI agent status.
"""

import asyncio
import datetime
import socket

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, RichLog, Rule, Static

from ..config import settings
from ..network import get_global_ipv6, get_lan_ipv4, is_globally_reachable


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

class NetworkPanel(Static):
    """Left panel: addresses and probe status."""

    probe_active: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    NetworkPanel {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._lan4 = get_lan_ipv4() or "unavailable"
        self._ipv6 = get_global_ipv6() or "unavailable"
        self._reachable = is_globally_reachable()

    def render(self) -> str:
        reach = "[green]YES[/green]" if self._reachable else "[yellow]NO[/yellow]"
        status = "[green]LISTENING[/green]" if self.probe_active else "[red]STOPPED[/red]"
        return (
            f"[dim]LAN IPv4[/dim]\n  {self._lan4}\n\n"
            f"[dim]Global IPv6[/dim]\n  {self._ipv6}\n\n"
            f"[dim]Routable[/dim]   {reach}\n"
            f"[dim]Port[/dim]       {settings.port}\n\n"
            f"[dim]Probe[/dim]      {status}"
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
        width: 42;
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
        Binding("c", "clear_log", "Clear"),
        Binding("q", "quit", "Quit"),
    ]

    # Probe state
    _probe_task: asyncio.Task | None = None
    _server: asyncio.Server | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="left"):
                yield Label("NETWORK", classes="panel-title")
                yield NetworkPanel(id="net-panel")
                yield Rule()
                yield Label("PROBE", classes="panel-title")
                # probe status is rendered inside NetworkPanel
            with Vertical(id="right"):
                yield Label("CONNECTION LOG", classes="panel-title")
                yield RichLog(id="log", highlight=True, markup=True, auto_scroll=True)
        yield Footer()

    def on_mount(self) -> None:
        self._log("AetherLink TUI started.")
        self._log(f"Binding on [::]:{settings.port}")
        self.action_toggle_probe()  # auto-start probe

    # ------------------------------------------------------------------
    # Probe management
    # ------------------------------------------------------------------

    def action_toggle_probe(self) -> None:
        if self._probe_task and not self._probe_task.done():
            self._stop_probe()
        else:
            self._probe_task = asyncio.create_task(self._run_probe())

    def _stop_probe(self) -> None:
        if self._server:
            self._server.close()
            self._server = None
        self._set_probe_active(False)
        self._log("[yellow]Probe stopped.[/yellow]")

    async def _run_probe(self) -> None:
        port = settings.port
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # IPV6_V6ONLY = 0: dual-stack — accepts LAN IPv4, LAN IPv6, public IPv6
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.setblocking(False)
            sock.bind(("::", port))
            sock.listen(5)

            self._server = await asyncio.start_server(
                self._handle_connection, sock=sock
            )
            self._set_probe_active(True)
            self._log(f"[green]Probe active — [::]:{port} (dual-stack)[/green]")

            async with self._server:
                await self._server.serve_forever()

        except OSError as exc:
            self._log(f"[red]Probe error: {exc}[/red]")
            self._set_probe_active(False)
        finally:
            self._set_probe_active(False)
            self._server = None

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        addr = writer.get_extra_info("peername")
        src = f"[{addr[0]}]:{addr[1]}"
        self._log(f"[cyan]CONNECT[/cyan]   {src}")
        try:
            writer.write(b"PONG - AetherLink Phase 1 OK\n")
            await writer.drain()
            self._log(f"[green]PONG[/green]   -> {src}")
        finally:
            writer.close()
            await writer.wait_closed()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_probe_active(self, value: bool) -> None:
        self.query_one(NetworkPanel).probe_active = value

    def _log(self, msg: str) -> None:
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.query_one(RichLog).write(f"[dim]{ts}[/dim]  {msg}")

    def action_clear_log(self) -> None:
        self.query_one(RichLog).clear()
