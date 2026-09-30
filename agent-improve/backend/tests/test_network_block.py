"""Controls review, item 2 (founder, 2026-09-30): the test run reaches no network beyond this
machine. Until now only the stub fixtures kept a test from a live call; a test that forgot one
would have called Azure. pytest-socket's `--allow-hosts` (set in conftest.pytest_configure) blocks
every other connect; loopback stays. The live run-through scripts are not pytest runs."""
from __future__ import annotations

import socket

import pytest
from pytest_socket import SocketConnectBlockedError


def test_a_connect_beyond_this_machine_is_blocked() -> None:
    s = socket.socket()
    try:
        with pytest.raises(SocketConnectBlockedError):
            s.connect(("93.184.216.34", 443))
    finally:
        s.close()


def test_loopback_still_connects() -> None:
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    c = socket.socket()
    try:
        c.connect(srv.getsockname())
    finally:
        c.close()
        srv.close()


def test_the_block_is_on_by_default(pytestconfig) -> None:
    from backend.tests.conftest import LOCAL_HOSTS
    assert pytestconfig.option.allow_hosts == LOCAL_HOSTS


def test_only_the_capability_rows_may_reach_the_network() -> None:
    """Founder 2026-09-30 (review of b472e17, item 3): after test_wiring.py moved to in-memory
    storage, the one file with the explicit allow is test_capability_rows.py, which reads the live
    Define case by design (procedure step 6.49)."""
    from pathlib import Path
    here = Path(__file__).resolve().parent
    allowed = sorted(p.name for p in here.glob("test_*.py")
                     if p.name != Path(__file__).name
                     and ("enable_socket" in p.read_text(encoding="utf-8")
                          or "socket_enabled" in p.read_text(encoding="utf-8")))
    assert allowed == ["test_capability_rows.py"], allowed
