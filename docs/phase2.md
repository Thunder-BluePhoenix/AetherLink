# Phase 2 — Local Agent Development (The Engine)

## Goal
Build the FastAPI-based local agent that receives authenticated HTTP requests and translates them into controlled OS actions — opening directories and executing sandboxed terminal commands.

---

## Milestones Unlocked
- **M02 — File Navigator**: Alexa opens a project folder by voice.
- **M03 — Commander**: Alexa executes terminal commands (`git pull`, `npm start`, etc.).

---

## Tasks

### 2.1 — FastAPI Scaffold
- Initialize Python project with `FastAPI` and `uvicorn`
- Define three core routes:
  - `GET /status` — health check, returns agent version and uptime
  - `POST /execute` — run a sandboxed shell command
  - `POST /play` — placeholder for Phase 3 media trigger
- Run server bound to `::` (all IPv6 interfaces) on port 58008

### 2.2 — Authentication Middleware
- Read `X-Aether-Key` header on every request
- Compare against a UUID4 secret stored in a local `.env` file
- Return `403 Forbidden` on mismatch — no leaking of error details
- Log all auth failures with timestamp and source IP

### 2.3 — OS Path Mapping
- Define a config file (JSON or TOML) mapping voice keywords to local paths
  - Example: `"Andromeda"` → `C:\Users\User\Dev\Andromeda`
- Load mapping on startup; support hot-reload without restart
- `/execute` with action `open_directory` uses this map exclusively — no raw paths accepted from outside

### 2.4 — Controlled Shell Interface
- Implement a `subprocess.run` wrapper that:
  - Only accepts commands from a predefined allowlist
  - Sets `cwd` to the mapped directory
  - Captures `stdout` and `stderr`
  - Enforces a timeout (e.g., 10 seconds)
  - Never passes raw user input directly to the shell
- Return structured JSON: `{ "status": "ok", "stdout": "...", "stderr": "..." }`

### 2.5 — Integration Test
- Send authenticated POST to `/execute` from an external IPv6 client
- Confirm directory opens or command runs on the local machine
- Confirm unauthenticated requests are rejected with 403

---

## Acceptance Criteria
- [ ] `/status` returns 200 with version info
- [ ] Requests without valid `X-Aether-Key` return 403
- [ ] `open_directory` opens the correct mapped folder
- [ ] Allowlisted shell command runs and returns output
- [ ] Non-allowlisted commands are rejected
- [ ] All actions logged with timestamp and source IP

---

## Tech Stack
- Framework: Python / FastAPI
- Server: Uvicorn (bound to `::`, port 58008)
- Auth: UUID4 header (`X-Aether-Key`)
- Config: `.env` for secret, JSON/TOML for path map
- OS: `subprocess.run`, `os.startfile` (for directory open)

---

## Security Checklist
- [ ] No raw user input passed to shell
- [ ] Command allowlist enforced server-side
- [ ] Auth key stored only in `.env`, never committed
- [ ] Timeout enforced on all subprocess calls

---

## Dependencies
- Phase 1 complete (IPv6 connectivity verified on port 58008)

## Unlocks
- Phase 3 (YouTube & Media Logic) — `/play` route ready to receive implementation
- Phase 4 (Alexa Interaction Model) — API surface is defined and testable
