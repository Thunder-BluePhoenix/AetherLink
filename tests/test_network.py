# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# This software is licensed under the Apache License, Version 2.0 (the "License")
# or the GNU General Public License, Version 3.0 (the "GPL").
# You may not use this file except in compliance with one of these Licenses.
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/gpl-3.0.txt

"""
tests/test_network.py — Phase 1: network detection
"""

from aetherlink.network import get_global_ipv6, get_lan_ipv4, is_globally_reachable


def test_lan_ipv4_is_string():
    ip = get_lan_ipv4()
    assert isinstance(ip, str)
    assert len(ip) > 0


def test_lan_ipv4_looks_like_ipv4():
    ip = get_lan_ipv4()
    parts = ip.split(".")
    assert len(parts) == 4
    assert all(p.isdigit() for p in parts)


def test_global_ipv6_is_string():
    ip = get_global_ipv6()
    assert isinstance(ip, str)
    assert ":" in ip


def test_global_ipv6_is_globally_routable():
    ip = get_global_ipv6()
    # Global addresses start with 2 or 3, not fe80 (link-local)
    assert ip.startswith("2") or ip.startswith("3"), (
        f"Expected global IPv6 (2xxx: or 3xxx:), got: {ip}"
    )


def test_global_ipv6_no_zone_id():
    """Zone ID (%interface) must be stripped — Lambda URLs can't contain it."""
    ip = get_global_ipv6()
    assert "%" not in ip


def test_is_globally_reachable():
    assert is_globally_reachable() is True
