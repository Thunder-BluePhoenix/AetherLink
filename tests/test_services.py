# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt

"""
tests/test_services.py — Phase 2 + 3: service layer
Covers directory, shell, and media services.
"""

import pytest

from aetherlink.services.directory import get_path, list_projects, open_directory
from aetherlink.services.media import get_volume, now_playing, stop_stream
from aetherlink.services.shell import COMMAND_ALLOWLIST, list_commands, run_command


# ---------------------------------------------------------------------------
# Directory service
# ---------------------------------------------------------------------------

class TestDirectory:

    def test_list_projects_returns_list(self):
        projects = list_projects()
        assert isinstance(projects, list)
        assert len(projects) >= 1

    def test_get_path_known_project(self):
        projects = list_projects()
        path = get_path(projects[0])
        assert path is not None
        assert isinstance(path, str)

    def test_get_path_unknown_returns_none(self):
        assert get_path("__nonexistent_project__") is None

    def test_open_directory_unknown_returns_error(self):
        result = open_directory("__nonexistent_project__")
        assert result["status"] == "error"
        assert "Unknown project" in result["message"]

    def test_open_directory_invalid_path_returns_error(self, tmp_path, monkeypatch):
        """If the mapped path doesn't exist on disk, return error gracefully."""
        monkeypatch.setattr(
            "aetherlink.services.directory._path_map",
            {"FakeProject": str(tmp_path / "does_not_exist")},
        )
        monkeypatch.setattr("aetherlink.services.directory._loaded", True)
        result = open_directory("FakeProject")
        assert result["status"] == "error"
        assert "not found" in result["message"]


# ---------------------------------------------------------------------------
# Shell service
# ---------------------------------------------------------------------------

class TestShell:

    def test_list_commands_returns_list(self):
        cmds = list_commands()
        assert isinstance(cmds, list)
        assert len(cmds) >= 1

    def test_allowlist_not_empty(self):
        assert len(COMMAND_ALLOWLIST) >= 1

    def test_allowlist_values_are_lists(self):
        for name, argv in COMMAND_ALLOWLIST.items():
            assert isinstance(argv, list), f"{name!r} argv must be a list"
            assert len(argv) >= 1

    def test_run_command_unknown_command_returns_error(self):
        result = run_command("rm -rf /", "AetherLink")
        assert result["status"] == "error"
        assert "allowlist" in result["message"].lower()

    def test_run_command_unknown_project_returns_error(self):
        result = run_command("git status", "__nonexistent__")
        assert result["status"] == "error"
        assert "Unknown project" in result["message"]

    def test_run_command_git_status_in_aetherlink(self):
        """Integration: actually runs git status — requires git in PATH."""
        projects = list_projects()
        if not projects:
            pytest.skip("No projects in path_map.json")
        result = run_command("git status", projects[0])
        # May fail if git not installed or project isn't a repo — just check structure
        assert "status" in result
        assert result["status"] in ("ok", "error")
        if result["status"] == "ok":
            assert "stdout" in result
            assert "returncode" in result


# ---------------------------------------------------------------------------
# Media service
# ---------------------------------------------------------------------------

class TestMedia:

    def test_get_volume_returns_int(self):
        vol = get_volume()
        assert vol is not None
        assert isinstance(vol, int)
        assert 0 <= vol <= 100

    def test_now_playing_empty_initially(self):
        track = now_playing()
        assert isinstance(track, dict)

    def test_stop_stream_no_active_stream(self):
        result = stop_stream()
        assert result["status"] == "error"
        assert "No stream" in result["message"]

    def test_set_volume_valid_range(self):
        from aetherlink.services.media import set_volume
        original = get_volume()
        result = set_volume(50)
        assert result["status"] == "ok"
        assert result["volume"] == 50
        # Restore
        if original is not None:
            set_volume(original)

    def test_set_volume_clamps_above_100(self):
        from aetherlink.services.media import set_volume
        original = get_volume()
        result = set_volume(150)
        assert result["status"] == "ok"
        assert result["volume"] == 100
        if original is not None:
            set_volume(original)

    def test_set_volume_clamps_below_0(self):
        from aetherlink.services.media import set_volume
        original = get_volume()
        result = set_volume(-10)
        assert result["status"] == "ok"
        assert result["volume"] == 0
        if original is not None:
            set_volume(original)
