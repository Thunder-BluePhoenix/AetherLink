# AetherLink — Project Plan

## Motto
> Voice meets machine. Direct. Private. Latency-free.

AetherLink grants Alexa voice-control over a local Windows machine via direct network communication — no third-party tunnels, no compromises on latency or privacy. It operates over two access paths: **LAN** (any device on the same network) and **public IPv6** (Alexa/Lambda from the internet).

---

## Project Overview

AetherLink is a distributed system bridging Amazon Alexa's voice interface with a Windows PC over a direct network channel. The architecture eliminates relay services like Ngrok by binding the local FastAPI agent to all interfaces — making it reachable both on LAN (via the PC's local IP) and from the internet (via the PC's global IPv6 address).

---

## System Architecture

| Layer | Component | Technology |
|---|---|---|
| Voice Entry | Alexa Skill | Amazon Developer Console |
| Relay Logic | HTTP Client | AWS Lambda |
| Transport | Dual-stack `[::]` TCP | LAN (IPv4/IPv6) + Public IPv6, port 58008 |
| Local Brain | REST API Server | Python / FastAPI |
| Media Engine | Stream extractor + Player | yt-dlp + MPV/VLC (headless) |

### Flow

**Internet path (Alexa → PC):**
```
[User Voice] → [Alexa Skill] → [AWS Lambda] → [Public IPv6 :58008] → [FastAPI Agent] → [Windows OS / Media]
```

**LAN path (local device → PC):**
```
[Local Device] → [LAN IPv4 or IPv6 :58008] → [FastAPI Agent] → [Windows OS / Media]
```

The agent binds `[::]` with `IPV6_V6ONLY=0` (dual-stack) — one socket, all three paths, same auth, same routes.

**No router port forwarding needed.** IPv6 addresses are globally routable by design. The only barrier is the OS firewall. (Confirmed via Andromeda's IPv6 binding implementation.)

---

## Security Model

| Concern | Solution |
|---|---|
| Transport | Strictly defined port (58008) on all interfaces — LAN + WAN |
| Authentication | `X-Aether-Key` UUID4 header on every request |
| Command Sandboxing | Allowlist of directories and scripts — no arbitrary code execution |

---

## Phases Summary

| Phase | Name | Goal |
|---|---|---|
| 1 | Connectivity & Network | LAN reachability + verified public IPv6 access |
| 2 | Local Agent Development | FastAPI server with OS integration |
| 3 | YouTube & Media Logic | Voice-triggered audio streaming |
| 4 | Alexa Interaction Model | Intents, slots, Lambda bridge |
| 5 | Deployment | AetherLink as a persistent Windows Service |

---

## Milestones

| # | Milestone | Deliverable |
|---|---|---|
| 01 | The Handshake | PONG received over LAN and over public IPv6 |
| 02 | File Navigator | Alexa opens a project folder by voice |
| 03 | Commander | Alexa triggers `git pull` or `npm start` |
| 04 | Aether Audio | Background music via voice search |
| 05 | Deployment | AetherLink runs as a Windows Service |

---

## Key Design Principles

- **No third-party tunnels** — LAN or public IPv6, always direct.
- **Dual-mode access** — same server, same auth, reachable on LAN for dev/local tools and on public IPv6 for Alexa/Lambda.
- **Minimal attack surface** — command sandboxing is non-negotiable on both paths.
- **Headless-first** — all local operations run without a UI.
- **Privacy by default** — no data leaves the local network except through the Alexa/Lambda path.
