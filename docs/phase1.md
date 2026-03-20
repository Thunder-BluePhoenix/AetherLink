# Phase 1 — Connectivity & Network (The Foundation)

## Goal
Verify that the PC is reachable on port 58008 from:
- **LAN** — any device on the same Wi-Fi/Ethernet (IPv4 or IPv6)
- **Public internet** — Alexa/Lambda via the PC's global IPv6 address

No router port forwarding is required. IPv6 addresses are globally routable by design — the only barrier is the OS firewall. A single dual-stack `[::]` socket handles all three cases (LAN IPv4, LAN IPv6, public IPv6) simultaneously.

> Confirmed via Andromeda's `bind_ipv6_only` / dual-stack binding implementation.

---

## Milestone Unlocked
**M01 — The Handshake**: PONG received over LAN and over public IPv6.

---

## Tasks

### 1.1 — IPv6 Verification
- Confirm a global-routable IPv6 address (prefix `2xxx:`) exists on the Wi-Fi/Ethernet interface
- Note the LAN IPv4 on the same interface
- Both are auto-detected by `aetherlink/network.py` and displayed in the TUI

### 1.2 — Windows Firewall Rule
- Run `scripts/setup_firewall.ps1` in an elevated PowerShell (one-time)
- Rule opens TCP port 58008 on **all profiles** (Domain, Private, Public)
- This is the **only configuration step** needed — no router changes required

### 1.3 — Run the Probe (TUI)
- Launch the TUI: `python tui.py`
- The probe auto-starts and binds `[::]` port 58008 with `IPV6_V6ONLY=0`
- Network panel shows LAN IPv4, global IPv6, and probe status in real time

### 1.4 — LAN Connectivity Test
- From another device on the same network (phone, laptop):
  - `telnet 192.168.31.138 58008` or connect via any TCP client
  - Should receive: `PONG - AetherLink Phase 1 OK`
- Requires only the Windows Firewall rule — no router config

### 1.5 — Public IPv6 Connectivity Test
- Switch the test device to **mobile data** (off Wi-Fi)
- Connect to `[2409:40e1:1134:ac32:d5d7:d70e:c18e:f13f]:58008`
- Should receive: `PONG - AetherLink Phase 1 OK`
- Requires only the Windows Firewall rule — no router config

### 1.6 — (Optional) DuckDNS for Stable IPv6 Hostname
- ISPs may rotate the IPv6 prefix on router reboot
- Register a free DuckDNS domain → points to the current public IPv6
- Lambda function will use the DuckDNS hostname instead of a raw IPv6

---

## Acceptance Criteria
- [ ] TUI shows LAN IPv4 and global IPv6 correctly
- [ ] Windows Firewall rule active on all profiles for port 58008
- [ ] Probe panel shows `LISTENING` in the TUI
- [ ] LAN test: PONG received from a device on the same network
- [ ] Public IPv6 test: PONG received from mobile data
- [ ] All connections appear in the TUI log with timestamp and source IP

---

## Access Matrix

| Path | Firewall Rule | Router Change | Notes |
|---|---|---|---|
| LAN IPv4 (`192.168.x.x`) | Required | None | Dual-stack socket handles this |
| LAN IPv6 (`2409:...`) | Required | None | Same global address, local hop |
| Public IPv6 (`2409:...`) | Required | **None** | IPv6 is directly routable |

---

## Tech Stack
- Network detection: `aetherlink/network.py`
- Probe: `tools/probe.py` (headless) or TUI probe (interactive)
- TUI: `textual` via `aetherlink/cli/app.py`
- Firewall: `scripts/setup_firewall.ps1`

---

## Notes
- `IPV6_V6ONLY = 0` on Windows: a single `[::]` socket accepts IPv4-mapped connections too — no need for a separate `0.0.0.0` socket.
- The TUI probe runs inside Textual's asyncio event loop via `asyncio.start_server(sock=...)`.
- `tools/probe.py` is the headless version for scripting/CI.

---

## Dependencies
- None. This is the first phase.

## Unlocks
- Phase 2 once M01 is confirmed (LAN + public IPv6 both working).
