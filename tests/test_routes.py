# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt

"""
tests/test_routes.py — Phase 2 + 3: FastAPI route integration tests

Uses FastAPI TestClient (no real server). Auth header injected from .env.
"""


# ---------------------------------------------------------------------------
# /status
# ---------------------------------------------------------------------------

class TestStatus:

    def test_status_returns_200(self, client):
        r = client.get("/status")
        assert r.status_code == 200

    def test_status_has_required_fields(self, client):
        body = client.get("/status").json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "uptime_seconds" in body
        assert "network" in body
        assert "projects" in body
        assert "commands" in body

    def test_status_network_has_ips(self, client):
        net = client.get("/status").json()["network"]
        assert "lan_ipv4" in net
        assert "global_ipv6" in net


# ---------------------------------------------------------------------------
# /execute — auth guard
# ---------------------------------------------------------------------------

class TestExecuteAuth:

    def test_missing_key_returns_403(self, client):
        r = client.post("/execute", json={"action": "open_directory", "target": "X"})
        assert r.status_code == 403

    def test_wrong_key_returns_403(self, client, bad_auth):
        r = client.post("/execute", json={"action": "open_directory", "target": "X"},
                        headers=bad_auth)
        assert r.status_code == 403


# ---------------------------------------------------------------------------
# /execute — meta
# ---------------------------------------------------------------------------

class TestExecuteMeta:

    def test_meta_returns_projects_and_commands(self, client, auth):
        r = client.get("/execute/meta", headers=auth)
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body["projects"], list)
        assert isinstance(body["commands"], list)
        assert len(body["commands"]) >= 1

    def test_meta_wrong_key_returns_403(self, client, bad_auth):
        r = client.get("/execute/meta", headers=bad_auth)
        assert r.status_code == 403


# ---------------------------------------------------------------------------
# /execute — open_directory
# ---------------------------------------------------------------------------

class TestExecuteOpenDirectory:

    def test_unknown_project_returns_error(self, client, auth):
        r = client.post("/execute",
                        json={"action": "open_directory", "target": "__no__"},
                        headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "error"

    def test_unknown_action_returns_error(self, client, auth):
        r = client.post("/execute",
                        json={"action": "dance", "target": "AetherLink"},
                        headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "error"


# ---------------------------------------------------------------------------
# /execute — run_command
# ---------------------------------------------------------------------------

class TestExecuteRunCommand:

    def test_unlisted_command_returns_error(self, client, auth):
        r = client.post("/execute",
                        json={"action": "run_command",
                              "target": "AetherLink",
                              "command": "rm -rf /"},
                        headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "error"
        assert "allowlist" in r.json()["message"].lower()

    def test_unknown_project_returns_error(self, client, auth):
        r = client.post("/execute",
                        json={"action": "run_command",
                              "target": "__ghost__",
                              "command": "git status"},
                        headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "error"


# ---------------------------------------------------------------------------
# /play — auth guard
# ---------------------------------------------------------------------------

class TestPlayAuth:

    def test_missing_key_returns_403(self, client):
        r = client.post("/play", json={"action": "play", "query": "test"})
        assert r.status_code == 403

    def test_wrong_key_returns_403(self, client, bad_auth):
        r = client.post("/play", json={"action": "play", "query": "test"},
                        headers=bad_auth)
        assert r.status_code == 403


# ---------------------------------------------------------------------------
# /play — status + volume
# ---------------------------------------------------------------------------

class TestPlayStatus:

    def test_play_status_returns_200(self, client, auth):
        r = client.get("/play/status", headers=auth)
        assert r.status_code == 200
        body = r.json()
        assert "now_playing" in body
        assert "volume" in body

    def test_play_status_volume_is_int(self, client, auth):
        body = client.get("/play/status", headers=auth).json()
        assert isinstance(body["volume"], int)
        assert 0 <= body["volume"] <= 100

    def test_play_stop_no_stream_returns_error(self, client, auth):
        r = client.post("/play", json={"action": "stop"}, headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "error"

    def test_play_missing_query_returns_error(self, client, auth):
        r = client.post("/play", json={"action": "play", "query": ""},
                        headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "error"

    def test_volume_endpoint_sets_volume(self, client, auth):
        from aetherlink.services.media import get_volume
        original = get_volume()
        r = client.post("/play/volume", json={"level": 55}, headers=auth)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert r.json()["volume"] == 55
        if original is not None:
            client.post("/play/volume", json={"level": original}, headers=auth)
