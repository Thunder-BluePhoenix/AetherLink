# Phase 4 — Alexa Interaction Model (The Voice Bridge)

## Goal
Build the Alexa Skill and AWS Lambda function that translates voice commands into authenticated AetherLink API calls. This phase wires all prior phases together through a voice interface.

---

## Milestones Unlocked
All milestones gain their voice interface — M01 through M04 become fully voice-driven.

---

## Tasks

### 4.1 — Alexa Skill Setup
- Create a new custom Alexa Skill on Amazon Developer Console
- Set invocation name (e.g., "Aether" or "Aether Link")
- Choose "Custom" model + "Provision your own" endpoint (Lambda)

### 4.2 — Intent Definitions
Define the following intents in the Alexa Interaction Model:

| Intent | Example Utterance | Slots |
|---|---|---|
| `OpenDirectory` | "Open {ProjectName}" | `ProjectName` (custom slot) |
| `RunCommand` | "Run {CommandName} in {ProjectName}" | `CommandName`, `ProjectName` |
| `PlayMusic` | "Play {SearchQuery}" | `SearchQuery` (free-form) |
| `StopMusic` | "Stop the music" | — |
| `SetVolume` | "Set volume to {Level}" | `Level` (AMAZON.NUMBER) |
| `StatusCheck` | "Are you there" | — |

### 4.3 — Slot Training
- `ProjectName` slot: add all project keywords ("Andromeda", "AetherLink", etc.)
- `CommandName` slot: add allowlisted commands ("git pull", "npm start", etc.)
- `SearchQuery` slot: use `AMAZON.SearchQuery` built-in type for free-form music queries
- Add at least 5 utterance variations per intent for NLU robustness

### 4.4 — AWS Lambda Function
- Create Lambda function (Python 3.x runtime)
- Store `X-Aether-Key` and the PC's IPv6 address as Lambda environment variables (never hardcode)
- Implement handler:
  1. Parse incoming Alexa JSON (`intentName`, slot values)
  2. Map intent → AetherLink API route + payload
  3. Send authenticated HTTP request to `http://[IPv6]:58008/<route>`
  4. Return Alexa response card with result or error message
- Handle timeout: if PC doesn't respond in 3s, return friendly "PC not reachable" response

### 4.5 — Skill-Lambda Wiring
- Set Lambda ARN as the Alexa Skill endpoint
- Enable the skill in Alexa Developer Console
- Test via Alexa Simulator before testing on a physical device

### 4.6 — End-to-End Test
- Say "Alexa, ask Aether to open Andromeda" → folder opens on PC
- Say "Alexa, ask Aether to play lofi beats" → music starts on PC
- Say "Alexa, ask Aether to stop the music" → player stops
- Say "Alexa, ask Aether, are you there" → status response returned

---

## Acceptance Criteria
- [ ] Skill created with correct invocation name
- [ ] All intents defined with slot types and utterances
- [ ] Lambda reads credentials from environment variables only
- [ ] Lambda routes each intent to the correct FastAPI endpoint
- [ ] Alexa Simulator confirms intents resolve correctly
- [ ] Physical device test: at least one intent works end-to-end
- [ ] Unreachable PC returns a graceful Alexa error response

---

## Tech Stack
- Voice Layer: Alexa Custom Skill (Amazon Developer Console)
- Serverless: AWS Lambda (Python 3.x)
- HTTP Client: `urllib` or `requests` (in Lambda)
- Auth: `X-Aether-Key` header injected from Lambda env vars
- Testing: Alexa Developer Console Simulator

---

## Security Checklist
- [ ] `X-Aether-Key` stored as Lambda environment variable, not in code
- [ ] Lambda only calls the specific IPv6+port, nothing else
- [ ] Alexa Skill set to account-linking disabled (local use only)
- [ ] Lambda execution role has minimal IAM permissions

---

## Dependencies
- Phase 2 complete (FastAPI routes functional and authenticated)
- Phase 3 complete (for `PlayMusic` / `StopMusic` intents)
- AWS account with Lambda access
- Amazon Developer Console account

## Unlocks
- Phase 5 (Deployment) — all logic is complete, now harden and persist.
