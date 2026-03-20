# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt

"""
tests/test_lambda.py — Phase 4: Lambda handler unit tests

All HTTP calls are mocked — no real network needed.
Tests verify intent routing, speech output, and error handling.
"""

import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

# Patch env vars before importing handler so it reads them
import os
os.environ.setdefault("AETHER_KEY",  "test-key")
os.environ.setdefault("AETHER_HOST", "2001:db8::1")
os.environ.setdefault("AETHER_PORT", "58008")

from aws_lambda.handler import lambda_handler  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _intent(name: str, slots: dict | None = None) -> dict:
    """Build a minimal Alexa IntentRequest event."""
    return {
        "request": {
            "type": "IntentRequest",
            "intent": {
                "name": name,
                "slots": {
                    k: {"name": k, "value": v}
                    for k, v in (slots or {}).items()
                },
            },
        }
    }


def _mock_response(body: dict) -> MagicMock:
    """Return a mock urlopen context manager that yields body as JSON."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def _speech(event: dict) -> str:
    return lambda_handler(event, None)["response"]["outputSpeech"]["text"]


# ---------------------------------------------------------------------------
# LaunchRequest
# ---------------------------------------------------------------------------

def test_launch_request_welcomes():
    event = {"request": {"type": "LaunchRequest"}}
    text = _speech(event)
    assert "AetherLink" in text
    assert lambda_handler(event, None)["response"]["shouldEndSession"] is False


# ---------------------------------------------------------------------------
# SessionEndedRequest
# ---------------------------------------------------------------------------

def test_session_ended_returns_empty_response():
    event = {"request": {"type": "SessionEndedRequest"}}
    result = lambda_handler(event, None)
    assert result == {"version": "1.0", "response": {}}


# ---------------------------------------------------------------------------
# StatusCheck
# ---------------------------------------------------------------------------

def test_status_check_pc_online():
    mock = _mock_response({"status": "ok", "uptime_seconds": 300})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("StatusCheck"))
    assert "online" in text.lower()
    assert "5 minutes" in text or "300" in text or "minute" in text


def test_status_check_pc_unreachable():
    with patch("aws_lambda.handler.urllib.request.urlopen",
               side_effect=urllib.error.URLError("timeout")):
        text = _speech(_intent("StatusCheck"))
    assert "not reachable" in text.lower()


# ---------------------------------------------------------------------------
# OpenDirectory
# ---------------------------------------------------------------------------

def test_open_directory_success():
    mock = _mock_response({"status": "ok", "project": "AetherLink"})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("OpenDirectory", {"ProjectName": "AetherLink"}))
    assert "Opening" in text
    assert "AetherLink" in text


def test_open_directory_missing_slot():
    text = _speech(_intent("OpenDirectory", {}))
    assert "which project" in text.lower()
    assert lambda_handler(_intent("OpenDirectory", {}), None)["response"]["shouldEndSession"] is False


def test_open_directory_pc_unreachable():
    with patch("aws_lambda.handler.urllib.request.urlopen",
               side_effect=urllib.error.URLError("timeout")):
        text = _speech(_intent("OpenDirectory", {"ProjectName": "AetherLink"}))
    assert "not reachable" in text.lower()


# ---------------------------------------------------------------------------
# RunCommand
# ---------------------------------------------------------------------------

def test_run_command_success_exit_0():
    mock = _mock_response({"status": "ok", "returncode": 0,
                           "stdout": "Already up to date."})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("RunCommand",
                               {"CommandName": "git pull", "ProjectName": "AetherLink"}))
    assert "successfully" in text.lower() or "Done" in text


def test_run_command_success_nonzero_exit():
    mock = _mock_response({"status": "ok", "returncode": 1, "stdout": ""})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("RunCommand",
                               {"CommandName": "git pull", "ProjectName": "AetherLink"}))
    assert "exit code 1" in text


def test_run_command_missing_slots():
    text = _speech(_intent("RunCommand", {}))
    assert "command" in text.lower() and "project" in text.lower()


# ---------------------------------------------------------------------------
# PlayMusic
# ---------------------------------------------------------------------------

def test_play_music_success():
    mock = _mock_response({"status": "playing", "title": "Lofi Hip Hop Radio"})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("PlayMusic", {"SearchQuery": "lofi hip hop"}))
    assert "Lofi Hip Hop Radio" in text or "playing" in text.lower()


def test_play_music_missing_query():
    text = _speech(_intent("PlayMusic", {}))
    assert "play" in text.lower()
    assert lambda_handler(_intent("PlayMusic", {}), None)["response"]["shouldEndSession"] is False


def test_play_music_pc_unreachable():
    with patch("aws_lambda.handler.urllib.request.urlopen",
               side_effect=urllib.error.URLError("timeout")):
        text = _speech(_intent("PlayMusic", {"SearchQuery": "lofi"}))
    assert "not reachable" in text.lower()


# ---------------------------------------------------------------------------
# StopMusic
# ---------------------------------------------------------------------------

def test_stop_music_success():
    mock = _mock_response({"status": "ok"})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("StopMusic"))
    assert "stopped" in text.lower()


def test_stop_music_pc_unreachable():
    with patch("aws_lambda.handler.urllib.request.urlopen",
               side_effect=urllib.error.URLError("timeout")):
        text = _speech(_intent("StopMusic"))
    assert "not reachable" in text.lower()


# ---------------------------------------------------------------------------
# SetVolume
# ---------------------------------------------------------------------------

def test_set_volume_success():
    mock = _mock_response({"status": "ok", "volume": 70})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("SetVolume", {"Level": "70"}))
    assert "70" in text


def test_set_volume_missing_level():
    text = _speech(_intent("SetVolume", {}))
    assert "0 and 100" in text or "volume level" in text.lower()
    assert lambda_handler(_intent("SetVolume", {}), None)["response"]["shouldEndSession"] is False


def test_set_volume_clamps_to_100():
    mock = _mock_response({"status": "ok", "volume": 100})
    with patch("aws_lambda.handler.urllib.request.urlopen", return_value=mock):
        text = _speech(_intent("SetVolume", {"Level": "150"}))
    assert "100" in text


# ---------------------------------------------------------------------------
# Built-in Alexa intents
# ---------------------------------------------------------------------------

def test_stop_intent():
    text = _speech(_intent("AMAZON.StopIntent"))
    assert "goodbye" in text.lower() or "bye" in text.lower()


def test_cancel_intent():
    text = _speech(_intent("AMAZON.CancelIntent"))
    assert len(text) > 0


def test_help_intent():
    text = _speech(_intent("AMAZON.HelpIntent"))
    assert lambda_handler(_intent("AMAZON.HelpIntent"), None)["response"]["shouldEndSession"] is False


def test_fallback_intent():
    text = _speech(_intent("AMAZON.FallbackIntent"))
    assert "didn't understand" in text.lower() or "sorry" in text.lower()
    assert lambda_handler(_intent("AMAZON.FallbackIntent"), None)["response"]["shouldEndSession"] is False
