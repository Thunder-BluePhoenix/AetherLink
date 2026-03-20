# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licenses is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licenses for the specific language governing permissions and
# limitations under the Licenses.

"""
lambda/handler.py — AetherLink AWS Lambda handler

Translates Alexa intent requests into authenticated HTTP calls
to the AetherLink FastAPI agent running on the local Windows PC.

Required Lambda environment variables:
  AETHER_KEY   — matches X-Aether-Key set in the PC's .env
  AETHER_HOST  — the PC's global IPv6 address (without brackets)
  AETHER_PORT  — TCP port (default: 58008)

No external dependencies — stdlib only (urllib, json, os).
"""

import json
import os
import urllib.error
import urllib.request

# ---------------------------------------------------------------------------
# Config — from Lambda environment variables
# ---------------------------------------------------------------------------

_KEY  = os.environ.get("AETHER_KEY", "")
_HOST = os.environ.get("AETHER_HOST", "")
_PORT = int(os.environ.get("AETHER_PORT", "58008"))
_TIMEOUT = 4  # seconds before "PC not reachable" response


# ---------------------------------------------------------------------------
# AetherLink HTTP client
# ---------------------------------------------------------------------------

def _base_url() -> str:
    return f"http://[{_HOST}]:{_PORT}"


def _post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req  = urllib.request.Request(
        _base_url() + path,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-Aether-Key": _KEY,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read())


def _get(path: str) -> dict:
    req = urllib.request.Request(
        _base_url() + path,
        headers={"X-Aether-Key": _KEY},
    )
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Alexa response builder
# ---------------------------------------------------------------------------

def _speak(text: str, end_session: bool = True) -> dict:
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session,
        },
    }


def _slot(slots: dict, name: str) -> str:
    """Safely extract a slot value, returning empty string if absent."""
    return (slots.get(name) or {}).get("value") or ""


# ---------------------------------------------------------------------------
# Intent handlers
# ---------------------------------------------------------------------------

def _handle_open_directory(slots: dict) -> dict:
    name = _slot(slots, "ProjectName")
    if not name:
        return _speak("Which project should I open?", end_session=False)
    try:
        result = _post("/execute", {"action": "open_directory", "target": name})
        if result.get("status") == "ok":
            return _speak(f"Opening {name}.")
        return _speak(result.get("message", f"Couldn't open {name}."))
    except (urllib.error.URLError, OSError):
        return _speak("Your PC is not reachable. Make sure AetherLink is running.")


def _handle_run_command(slots: dict) -> dict:
    command = _slot(slots, "CommandName")
    project = _slot(slots, "ProjectName")
    if not command or not project:
        return _speak("Please say a command and a project name.", end_session=False)
    try:
        result = _post("/execute", {
            "action":  "run_command",
            "target":  project,
            "command": command,
        })
        if result.get("status") == "ok":
            rc = result.get("returncode", 0)
            if rc == 0:
                return _speak(f"Done. {command} completed successfully in {project}.")
            return _speak(f"{command} finished with exit code {rc} in {project}.")
        return _speak(result.get("message", f"Couldn't run {command}."))
    except (urllib.error.URLError, OSError):
        return _speak("Your PC is not reachable. Make sure AetherLink is running.")


def _handle_play_music(slots: dict) -> dict:
    query = _slot(slots, "SearchQuery")
    if not query:
        return _speak("What would you like me to play?", end_session=False)
    try:
        result = _post("/play", {"action": "play", "query": query})
        if result.get("status") == "playing":
            title = result.get("title", query)
            return _speak(f"Now playing: {title}.")
        return _speak(result.get("message", "Couldn't start playback."))
    except (urllib.error.URLError, OSError):
        return _speak("Your PC is not reachable. Make sure AetherLink is running.")


def _handle_stop_music() -> dict:
    try:
        result = _post("/play", {"action": "stop"})
        if result.get("status") == "ok":
            return _speak("Music stopped.")
        return _speak(result.get("message", "Nothing is playing."))
    except (urllib.error.URLError, OSError):
        return _speak("Your PC is not reachable. Make sure AetherLink is running.")


def _handle_set_volume(slots: dict) -> dict:
    raw = _slot(slots, "Level")
    if not raw or not raw.isdigit():
        return _speak("Please say a volume level between 0 and 100.", end_session=False)
    level = max(0, min(100, int(raw)))
    try:
        result = _post("/execute", {"action": "set_volume", "level": level})
        if result.get("status") == "ok":
            return _speak(f"Volume set to {level} percent.")
        return _speak(result.get("message", "Couldn't change the volume."))
    except (urllib.error.URLError, OSError):
        return _speak("Your PC is not reachable. Make sure AetherLink is running.")


def _handle_status_check() -> dict:
    try:
        result = _get("/status")
        uptime = result.get("uptime_seconds", 0)
        minutes = uptime // 60
        return _speak(f"AetherLink is online. Uptime: {minutes} minutes.")
    except (urllib.error.URLError, OSError):
        return _speak("AetherLink is not reachable right now.")


def _handle_help() -> dict:
    return _speak(
        "You can say: open a project, run a command, play music, "
        "stop music, set volume, or ask for status.",
        end_session=False,
    )


# ---------------------------------------------------------------------------
# Main Lambda handler
# ---------------------------------------------------------------------------

def lambda_handler(event: dict, context) -> dict:
    request_type = event.get("request", {}).get("type", "")

    # ---- Launch ----
    if request_type == "LaunchRequest":
        return _speak(
            "AetherLink ready. You can open projects, run commands, "
            "play music, or check status.",
            end_session=False,
        )

    # ---- Session ended ----
    if request_type == "SessionEndedRequest":
        return {"version": "1.0", "response": {}}

    # ---- Intent ----
    if request_type == "IntentRequest":
        intent = event["request"]["intent"]
        name   = intent["name"]
        slots  = intent.get("slots", {})

        if name == "OpenDirectory":
            return _handle_open_directory(slots)
        if name == "RunCommand":
            return _handle_run_command(slots)
        if name == "PlayMusic":
            return _handle_play_music(slots)
        if name == "StopMusic":
            return _handle_stop_music()
        if name == "SetVolume":
            return _handle_set_volume(slots)
        if name == "StatusCheck":
            return _handle_status_check()
        if name in ("AMAZON.HelpIntent",):
            return _handle_help()
        if name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return _speak("Goodbye.")
        if name == "AMAZON.FallbackIntent":
            return _speak(
                "I didn't understand that. Try saying: open a project, "
                "run a command, or play music.",
                end_session=False,
            )

    return _speak("Sorry, something went wrong.", end_session=True)
