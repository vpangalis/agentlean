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
