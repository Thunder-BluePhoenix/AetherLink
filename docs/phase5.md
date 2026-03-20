# Phase 5 — Deployment (Background Persistence)

## Goal
Register AetherLink as a persistent Windows Service so it starts automatically on boot, runs silently in the background with no terminal window, and survives user logoff and system restarts.

---

## Milestone Unlocked
**M05 — Deployment**: AetherLink runs as a Windows Service, always-on.

---

## Tasks

### 5.1 — Service Wrapper Setup
- Install `pywin32` for Windows Service support
- Create a `AetherLinkService.py` using `win32serviceutil.ServiceFramework`
- The service class must implement:
  - `SvcStart()` — launch uvicorn in a subprocess
  - `SvcStop()` — terminate uvicorn gracefully
- Test install/start/stop via `python AetherLinkService.py install`

### 5.2 — Environment & Secrets at Service Level
- Ensure the `.env` file is readable by the service account (SYSTEM or a dedicated user)
- Do NOT hardcode any secrets in the service file
- Confirm `X-Aether-Key` is loaded correctly when the service starts under SYSTEM context

### 5.3 — Windows Firewall Rule (Persistent)
- Add an inbound firewall rule for port 58008 via PowerShell or Windows Defender Firewall GUI
- Ensure the rule survives reboots:
  ```powershell
  New-NetFirewallRule -DisplayName "AetherLink" -Direction Inbound -Protocol TCP -LocalPort 58008 -Action Allow
  ```
- Confirm the rule is present after a test reboot

### 5.4 — Auto-Start Configuration
- Set service startup type to `Automatic`
- Configure a service recovery action: restart on failure (1st and 2nd failure), restart after 60s delay
- Test: reboot machine → confirm service is running without manual intervention

### 5.5 — Log Management
- Redirect uvicorn logs to a file (e.g., `C:\AetherLink\logs\aetherlink.log`)
- Implement log rotation (max 5MB per file, keep 3 backups) using Python `logging.handlers.RotatingFileHandler`
- Ensure logs are written even when service runs as SYSTEM

### 5.6 — Final System Test
- Reboot PC
- Wait 60 seconds
- From external IPv6 client: send authenticated request to `/status`
- Confirm 200 response — service is live
- Test all milestones end-to-end: voice → folder open, voice → command, voice → music

---

## Acceptance Criteria
- [ ] Service installs without error
- [ ] Service starts on boot automatically (no manual `start`)
- [ ] Service runs with no visible terminal window
- [ ] `.env` secrets load correctly under SYSTEM account
- [ ] Windows Firewall rule persists across reboots
- [ ] Service recovers automatically after a simulated crash
- [ ] Logs written to file with rotation
- [ ] Full end-to-end voice test passes after cold boot

---

## Tech Stack
- Service wrapper: `pywin32` (`win32serviceutil`)
- Server: Uvicorn (subprocess from service)
- Firewall: Windows Defender Firewall / `netsh` / PowerShell
- Logging: Python `RotatingFileHandler`

---

## Notes & Gotchas
- Services run as SYSTEM by default — file paths like `C:\Users\...` may resolve differently. Use absolute paths everywhere.
- MPV/VLC launched from a SYSTEM-context service may not have access to audio devices — test this specifically and use a dedicated user account for the service if needed.
- Do not run the service as Administrator — use a minimal dedicated Windows user account if SYSTEM causes audio access issues.

---

## Dependencies
- All prior phases complete and tested
- `pywin32` installed in the Python environment
- Admin access to the Windows machine

## Unlocks
- AetherLink is production-ready. All milestones are complete.
