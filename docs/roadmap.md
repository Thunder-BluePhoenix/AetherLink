# AetherLink — Roadmap

## Vision
A fully voice-controlled local machine — private, fast, tunnel-free — powered by Alexa over direct IPv6.

---

## Milestone Timeline

```
Phase 1            Phase 2            Phase 3            Phase 4            Phase 5
   |                  |                  |                  |                  |
[M01: Handshake] → [M02: Navigator] → [M04: Audio] → [M03: Commander] → [M05: Deployment]
IPv6 verified      Folders open       Music streams     Commands fire      Runs as Service
```

---

## Milestone Details

### M01 — The Handshake
- **Objective:** Establish secure, verified IPv6 communication from the internet to the PC.
- **Key Deliverable:** A Python listener on port 58008 receives and responds to an external IPv6 ping.
- **Phase:** 1 — Connectivity & Network
- **Status:** Pending

---

### M02 — File Navigator
- **Objective:** Voice command opens a specific project directory on the Windows machine.
- **Key Deliverable:** Saying "Open Andromeda" triggers Alexa → Lambda → FastAPI → `explorer.exe` path.
- **Phase:** 2 — Local Agent Development
- **Status:** Pending

---

### M03 — Commander
- **Objective:** Execute terminal commands on the local machine via voice.
- **Key Deliverable:** Alexa triggers `git pull` or `npm start` inside a sandboxed directory.
- **Phase:** 2 — Local Agent Development
- **Status:** Pending

---

### M04 — Aether Audio
- **Objective:** Stream YouTube audio in the background via a voice search query.
- **Key Deliverable:** Saying "Play lofi beats" starts headless yt-dlp + MPV/VLC audio.
- **Phase:** 3 — YouTube & Media Logic
- **Status:** Pending

---

### M05 — Deployment
- **Objective:** AetherLink runs persistently without a terminal window open.
- **Key Deliverable:** FastAPI agent registered as a Windows Service, auto-starts on boot.
- **Phase:** 5 — Deployment
- **Status:** Pending

---

## Phase-to-Milestone Map

| Phase | Milestones Unlocked |
|---|---|
| Phase 1: Connectivity & Network | M01 — The Handshake |
| Phase 2: Local Agent Development | M02 — File Navigator, M03 — Commander |
| Phase 3: YouTube & Media Logic | M04 — Aether Audio |
| Phase 4: Alexa Interaction Model | All milestones gain voice interface |
| Phase 5: Deployment | M05 — Deployment |

---

## Risk & Dependency Notes

| Risk | Mitigation |
|---|---|
| ISP blocking IPv6 | Test early (Phase 1); have fallback port options |
| Router firewall blocking port | Document exact router config steps in Phase 1 |
| yt-dlp API changes | Pin yt-dlp version; add update step to maintenance |
| Alexa Skill certification delays | Build and test Lambda locally before submission |
| Windows Service permissions | Test service account permissions in Phase 5 sandbox |
