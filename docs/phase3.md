# Phase 3 — YouTube & Media Logic (Aether Audio)

## Goal
Implement voice-triggered audio streaming: take a search query from Alexa, extract the best audio stream via yt-dlp, and pipe it to a headless player (MPV or VLC). Add system volume control via Windows Core Audio APIs.

---

## Milestone Unlocked
**M04 — Aether Audio**: Saying "Play lofi beats" starts background music on the PC.

---

## Tasks

### 3.1 — yt-dlp Integration
- Install and pin a specific version of `yt-dlp`
- Implement a search function: query → best audio stream URL
  - Use `ytsearch1:<query>` to get the top YouTube result
  - Extract direct audio stream URL (no video download)
- Handle errors: no results, geo-blocked content, deleted videos

### 3.2 — Headless Player Integration
- Choose primary player: **MPV** (preferred for headless) or VLC
- Launch player via `subprocess.Popen` with the stream URL
  - MPV: `mpv --no-video --quiet <url>`
  - VLC: `vlc --intf dummy --no-video <url>`
- Track the player process PID for stop/pause control
- Implement commands: `play`, `stop`, `pause` (if player supports it)

### 3.3 — `/play` Route Implementation
- Accept POST body: `{ "action": "play"|"stop", "query": "..." }`
- `play`: run yt-dlp search → launch headless player with stream URL
- `stop`: kill the tracked player process
- Return: `{ "status": "playing", "title": "...", "url": "..." }`

### 3.4 — Windows Volume Control
- Use `pycaw` library (Python wrapper for Windows Core Audio API)
- Implement `set_volume(level: int)` — accepts 0–100
- Expose via `/execute` with action `set_volume` and `level` param
- Map Alexa intents: "Volume up", "Volume down", "Mute"

### 3.5 — Integration Test
- Send authenticated POST to `/play` with a search query
- Confirm audio starts playing on PC speakers
- Send stop command, confirm player process ends
- Test volume set to 50%, confirm system volume changes

---

## Acceptance Criteria
- [ ] yt-dlp search returns a valid stream URL for a given query
- [ ] MPV/VLC launches headless with the stream URL
- [ ] Audio plays on the PC without opening any window
- [ ] Stop command kills the player process cleanly
- [ ] `set_volume` changes Windows system volume
- [ ] All operations return structured JSON responses

---

## Tech Stack
- Stream extraction: `yt-dlp` (pinned version)
- Player: MPV or VLC (headless mode)
- Volume control: `pycaw` (Windows Core Audio)
- Interface: FastAPI `/play` route (from Phase 2)

---

## Notes & Gotchas
- yt-dlp URLs expire — extract the URL at play time, not cached.
- MPV requires a separate install; document the setup step.
- `pycaw` only works on Windows — keep audio control Windows-specific.
- Kill the player process tree, not just the parent PID (use `psutil`).

---

## Dependencies
- Phase 2 complete (`/play` route scaffold exists)
- MPV or VLC installed on the Windows machine
- `yt-dlp`, `pycaw`, `psutil` installed in the Python environment

## Unlocks
- Phase 4 can wire the `PlayMusic` Alexa Intent to this route.
