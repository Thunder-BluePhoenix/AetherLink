# Lambda & Alexa Skill — Deployment Guide

## Overview
```
[Alexa Device] → [Alexa Skill] → [AWS Lambda] → [IPv6 HTTP] → [AetherLink Agent on PC]
```

---

## Step 1 — Create the Lambda Function

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda)
2. Click **Create function** → **Author from scratch**
3. Settings:
   - Name: `AetherLinkHandler`
   - Runtime: **Python 3.11**
   - Architecture: `x86_64`
4. Click **Create function**

### Upload the handler

In the Lambda code editor, replace the default `lambda_function.py` with the contents of `aws_lambda/handler.py`.
Rename the file to `lambda_function.py` **or** set the handler to:

```
handler.lambda_handler
```

No external packages needed — stdlib only.

---

## Step 2 — Set Environment Variables

In Lambda → **Configuration** → **Environment variables**, add:

| Key | Value |
|---|---|
| `AETHER_KEY` | Your UUID from the `.env` file on the PC |
| `AETHER_HOST` | The PC's global IPv6 (e.g. `2409:40e1:1134:ac32:...`) |
| `AETHER_PORT` | `58008` |

**Never put these values in the source code.**

---

## Step 3 — Set Lambda Timeout

In Lambda → **Configuration** → **General configuration**:
- Timeout: `10 seconds` (allows for yt-dlp search + PC response)

---

## Step 4 — Create the Alexa Skill

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click **Create Skill**
3. Settings:
   - Skill name: `AetherLink`
   - Primary locale: English (your region)
   - Model: **Custom**
   - Hosting: **Provision your own**
4. Choose **Start from scratch**

### Upload the Interaction Model

1. In the skill editor, go to **JSON Editor** (left sidebar)
2. Paste the entire contents of `alexa/interaction_model.json`
3. Click **Save Model** → **Build Model**
4. Wait for the build to complete

### Add your projects and commands

In the JSON editor, update `PROJECT_NAME` values with your actual project names, and `COMMAND_NAME` with any additional commands you want to add to the allowlist in `services/shell.py`.

---

## Step 5 — Wire Skill to Lambda

1. In the Alexa skill, go to **Endpoint** (left sidebar)
2. Select **AWS Lambda ARN**
3. Copy your Lambda ARN from the Lambda console (top-right)
4. Paste into **Default Region** field
5. Click **Save Endpoints**

### Add Alexa trigger to Lambda

Back in Lambda → **Configuration** → **Triggers** → **Add trigger**:
- Source: `Alexa Skills Kit`
- Skill ID: found in Alexa Developer Console → **Endpoint**
- Click **Add**

---

## Step 6 — Test in Alexa Simulator

1. In Alexa Developer Console → **Test** tab
2. Enable testing (toggle to "Development")
3. Try:
   - `"ask aether link are you there"` → should get uptime response
   - `"ask aether link open AetherLink"` → should open folder on PC
   - `"ask aether link play lofi beats"` → should start music

---

## Step 7 — Test on Physical Device

Say: **"Alexa, open aether link"** or **"Alexa, ask aether link to open AetherLink"**

---

## Troubleshooting

| Issue | Check |
|---|---|
| `PC not reachable` | AetherLink TUI running? Firewall rule set? IPv6 address correct in Lambda env? |
| `403 Forbidden` | `AETHER_KEY` in Lambda env matches the `.env` on the PC? |
| Intent not resolving | Rebuild the interaction model; check utterance training |
| Lambda timeout | Increase Lambda timeout to 15s; check PC response time |
| `AMAZON.SearchQuery` slot empty | Ensure the slot type is `AMAZON.SearchQuery` not a custom type |
