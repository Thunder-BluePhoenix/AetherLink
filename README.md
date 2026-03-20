# AetherLink

> Voice meets machine. Direct. Private. Latency-free.

AetherLink gives Amazon Alexa voice-control over a local Windows PC via a direct IPv6 connection — no third-party tunnels, no Ngrok, no latency tax.

---

## How it works

```
[Voice] → [Alexa Skill] → [AWS Lambda] → [IPv6 :58008] → [FastAPI Agent] → [Windows OS / Media]
                                                    ↑
                                         LAN devices also connect here
                                         (dual-stack [::] socket)
```

- **One socket** bound to `[::]` with `IPV6_V6ONLY=0` handles LAN IPv4, LAN IPv6, and public IPv6 simultaneously.
- **No router port-forwarding needed** — IPv6 addresses are globally routable by design.
- **Only barrier:** Windows Firewall inbound rule for TCP port 58008.

---

## Features

| Feature | Phase |
|---|---|
| IPv6 / LAN dual-stack connectivity probe | 1 |
| Directory open via voice | 2 |
| Sandboxed terminal command execution | 2 |
| YouTube audio streaming (yt-dlp + MPV/VLC) | 3 |
| Windows volume control | 3 |
| Alexa Skill + Lambda bridge | 4 |
| Windows Service (auto-start on boot) | 5 |

---

## Quick Start

### 1. Install dependencies
```powershell
pip install -r requirements.txt
```

### 2. Generate your secret key (one-time)
```powershell
python scripts/gen_key.py
```

### 3. Open Windows Firewall (admin PowerShell, one-time)
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_firewall.ps1
```

### 4. Add your projects to `path_map.json`
```json
{
  "AetherLink": "F:\\proj_guides\\AetherLink",
  "Andromeda":  "F:\\proj_guides\\Andromeda"
}
```

### 5. Run the TUI
```powershell
python tui.py
```

- **`P`** — toggle IPv6 connectivity probe
- **`A`** — toggle FastAPI agent
- **`Q`** — quit

### 6. Install a media player (for audio streaming)
```powershell
winget install mpv.mpv
```

---

## Project Structure

```
AetherLink/
├── aetherlink/              # Main application package
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Settings (.env loader)
│   ├── auth.py              # X-Aether-Key middleware
│   ├── network.py           # IP address detection
│   ├── cli/app.py           # Textual TUI
│   ├── routes/
│   │   ├── status.py        # GET  /status
│   │   ├── execute.py       # POST /execute | GET /execute/meta
│   │   └── play.py          # POST /play | GET /play/status | POST /play/volume
│   └── services/
│       ├── directory.py     # path_map.json + os.startfile
│       ├── shell.py         # Sandboxed subprocess (allowlist)
│       └── media.py         # yt-dlp + headless player + pycaw
├── alexa/
│   └── interaction_model.json   # Upload to Alexa Developer Console
├── lambda/
│   ├── handler.py           # AWS Lambda function (stdlib only)
│   └── deploy.md            # Step-by-step deployment guide
├── tools/probe.py           # Headless connectivity probe
├── scripts/
│   ├── setup_firewall.ps1   # Windows Firewall rule (run as admin)
│   └── gen_key.py           # One-time .env generator
├── tests/                   # pytest suite
├── docs/                    # Phase docs + master tracker
├── .env.example
├── path_map.example.json
├── requirements.txt
├── run.py                   # FastAPI server entry point
└── tui.py                   # TUI entry point
```

---

## API Reference

All routes except `GET /status` require the `X-Aether-Key` header.

| Method | Route | Auth | Description |
|---|---|---|---|
| GET | `/status` | No | Version, uptime, network info, projects, commands |
| POST | `/execute` | Yes | Open directory / run command / set volume |
| GET | `/execute/meta` | Yes | List projects + allowlisted commands |
| POST | `/play` | Yes | Play or stop audio stream |
| GET | `/play/status` | Yes | Now playing + system volume |
| POST | `/play/volume` | Yes | Set system volume (0–100) |

### POST `/execute` examples
```json
{ "action": "open_directory", "target": "AetherLink" }
{ "action": "run_command",    "target": "AetherLink", "command": "git pull" }
{ "action": "set_volume",     "level": 70 }
```

### POST `/play` examples
```json
{ "action": "play", "query": "lofi hip hop" }
{ "action": "stop" }
```

---

## Security

- `X-Aether-Key` UUID4 stored only in `.env` (gitignored) and Lambda env vars — never in source code.
- Commands restricted to `COMMAND_ALLOWLIST` in `services/shell.py` — no arbitrary execution.
- `subprocess.run(..., shell=False)` always — raw input never reaches the shell.
- Agent refuses to serve if `AETHER_KEY` is not set.

---

## Testing

```powershell
pip install pytest httpx
pytest tests/ -v
```

---

## Deploying to Alexa

See [lambda/deploy.md](lambda/deploy.md) for the full 7-step guide.

---

## License

Dual-licensed under **Apache 2.0** and **GPL 3.0** — see [LICENSE](LICENSE).
Copyright (c) 2024 Thunder-BluePhoenix
