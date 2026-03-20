# AetherLink — Master Tracker

> Single source of truth for all phases, tasks, and milestones.
> Update status as work progresses: `Pending` → `In Progress` → `Done` | `Blocked`

---

## Legend
| Symbol | Meaning |
|---|---|
| `[ ]` | Pending |
| `[~]` | In Progress |
| `[x]` | Done |
| `[!]` | Blocked |

---

## Milestone Status

| ID | Milestone | Phase | Status | Notes |
|---|---|---|---|---|
| M01 | The Handshake | Phase 1 | `[~]` In Progress | IPv6 confirmed, probe ready — awaiting firewall + LAN test |
| M02 | File Navigator | Phase 2 | `[x]` Done | Code complete + 63/63 tests passing |
| M03 | Commander | Phase 2 | `[x]` Done | Code complete + 63/63 tests passing |
| M04 | Aether Audio | Phase 3 | `[~]` In Progress | Code complete — blocked on MPV/VLC install for live test |
| M05 | Deployment | Phase 5 | `[~]` In Progress | Service wrapper + installer done — awaiting install + reboot test |

---

## Phase 1 — Connectivity & Network

**Goal:** Verify reachability over LAN and public IPv6 on port 58008. No router config needed — IPv6 is directly routable.
**Milestone:** M01 — The Handshake
**Status:** `[~]` In Progress

| # | Task | Status | Notes |
|---|---|---|---|
| 1.1 | IPv6 + LAN IPv4 verified | `[x]` | `2409:40e1:...` (IPv6), `192.168.31.138` (IPv4), auto-detected by `network.py` |
| 1.2 | Windows Firewall rule for TCP 58008 (all profiles) | `[~]` | Run `scripts/setup_firewall.ps1` as admin — only config needed |
| 1.3 | TUI probe starts and shows `LISTENING` | `[x]` | `python tui.py` — probe auto-starts, self-test passed |
| 1.4 | LAN test: PONG from device on same network | `[ ]` | Needs Firewall rule only |
| 1.5 | Public IPv6 test: PONG from mobile data | `[ ]` | Needs Firewall rule only — no router change |
| 1.6 | (Optional) DuckDNS for stable IPv6 hostname | `[ ]` | If ISP rotates IPv6 prefix |

---

## Phase 2 — Local Agent Development

**Goal:** FastAPI server with auth, path mapping, and sandboxed shell execution.
**Milestones:** M02 — File Navigator, M03 — Commander
**Status:** `[~]` In Progress

| # | Task | Status | Notes |
|---|---|---|---|
| 2.1 | FastAPI scaffold with `/status`, `/execute`, `/play` routes | `[x]` | All routes wired; `GET /execute/meta` exposes projects + commands |
| 2.2 | `X-Aether-Key` auth — rejects empty key + mismatch | `[x]` | `aetherlink/auth.py`; key set via `python scripts/gen_key.py` |
| 2.3 | Path map loaded from `path_map.json` (hot-reload via `reload()`) | `[x]` | `services/directory.py`; `list_projects()` exposed on `/status` |
| 2.4 | Sandboxed subprocess wrapper with `COMMAND_ALLOWLIST` | `[x]` | `services/shell.py`; `shell=False`, timeout=15s |
| 2.5 | Integration test: open directory + run command via external IPv6 | `[x]` | Unit + route tests: 63/63 passing; live IPv6 test requires M01 |

---

## Phase 3 — YouTube & Media Logic

**Goal:** Voice-triggered audio streaming via yt-dlp and headless player.
**Milestone:** M04 — Aether Audio
**Status:** `[~]` In Progress

| # | Task | Status | Notes |
|---|---|---|---|
| 3.1 | yt-dlp search query → stream URL | `[x]` | `_extract_stream()` in `services/media.py`; run via `asyncio.to_thread` |
| 3.2 | Headless player launch + psutil process-tree kill | `[x]` | MPV preferred, VLC fallback; auto-detected from PATH + common install paths |
| 3.3 | `POST /play`, `GET /play/status`, `POST /play/volume` | `[x]` | `routes/play.py` fully wired |
| 3.4 | Windows volume control via `pycaw` (EndpointVolume API) | `[x]` | `get_volume()` / `set_volume()` working — current: 94% |
| 3.5 | Integration test: music plays and stops via API | `[~]` | VLC installed — live test requires `AETHER_KEY` in `.env` + TUI running |

---

## Phase 4 — Alexa Interaction Model

**Goal:** Alexa Skill + Lambda bridge translates voice to AetherLink API calls.
**Milestones:** All milestones gain voice interface.
**Status:** `[~]` In Progress

| # | Task | Status | Notes |
|---|---|---|---|
| 4.1 | Alexa Skill created with invocation name `aether link` | `[ ]` | Manual — Alexa Developer Console |
| 4.2 | Intents + utterances defined | `[x]` | `alexa/interaction_model.json` — 6 intents, 5–7 utterances each |
| 4.3 | Slot types: `PROJECT_NAME`, `COMMAND_NAME`, `AMAZON.SearchQuery` | `[x]` | In interaction model; update values to match `path_map.json` + `shell.py` |
| 4.4 | Lambda handler written (stdlib only, no external deps) | `[x]` | `aws_lambda/handler.py` — reads `AETHER_KEY`, `AETHER_HOST`, `AETHER_PORT` from env |
| 4.5 | Skill endpoint wired to Lambda ARN | `[ ]` | Manual — see `aws_lambda/deploy.md` |
| 4.6 | End-to-end voice test on physical Alexa device | `[ ]` | Manual — after 4.1 + 4.5 |

---

## Phase 5 — Deployment

**Goal:** AetherLink runs as a persistent Windows Service, auto-starts on boot.
**Milestone:** M05 — Deployment
**Status:** `[ ]` Pending

| # | Task | Status | Notes |
|---|---|---|---|
| 5.1 | `pywin32` service wrapper (`AetherLinkService.py`) | `[x]` | Subprocess launcher + pipe capture; `install/start/stop/remove` CLI |
| 5.2 | `.env` secrets accessible under SYSTEM service account | `[x]` | Absolute `BASE_DIR` paths in service; `.env` must be in project root |
| 5.3 | Windows Firewall inbound rule for port 58008 (persistent) | `[x]` | Included in `scripts/install_service.ps1` (idempotent) |
| 5.4 | Service set to Automatic start with recovery actions | `[x]` | `install_service.ps1` sets Automatic + sc.exe failure restart×3 after 60s |
| 5.5 | Log rotation configured (`RotatingFileHandler`) | `[x]` | `logs/aetherlink.log` — 5 MB max, 3 backups; uvicorn output piped in |
| 5.6 | Cold boot end-to-end test: all milestones pass after reboot | `[ ]` | Manual — run install_service.ps1, reboot, test `/status` from LAN |

---

## Blockers & Notes

| Date | Phase | Description | Resolution |
|---|---|---|---|
| — | 1 | Firewall rule not yet applied | Run `scripts/setup_firewall.ps1` as admin, then test LAN PONG |
| — | 3 | Live music test needs `.env` + TUI running | `python scripts/gen_key.py` → `python tui.py` → `[A]` to start agent |
| — | 4 | Alexa Skill + Lambda not yet deployed | Follow `aws_lambda/deploy.md` for tasks 4.1, 4.5, 4.6 |

---

## Progress Summary

| Phase | Total Tasks | Done | In Progress | Blocked |
|---|---|---|---|---|
| Phase 1 | 6 | 3 | 1 | 0 |
| Phase 2 | 5 | 5 | 0 | 0 |
| Phase 3 | 5 | 4 | 1 | 0 |
| Phase 4 | 6 | 3 | 0 | 0 |
| Phase 5 | 6 | 5 | 1 | 0 |
| **Total** | **28** | **20** | **3** | **0** |
