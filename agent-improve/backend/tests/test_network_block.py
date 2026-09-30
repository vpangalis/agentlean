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


def test_an_async_request_beyond_this_machine_is_blocked() -> None:
    """G-144: an async httpx client on Windows connects without `socket.connect` (the proactor
    loop's ConnectEx), so the socket block missed it; the transport refuses it instead."""
    import asyncio

    import httpx

    async def call() -> None:
        async with httpx.AsyncClient(timeout=2) as client:
            await client.get("https://93.184.216.34/")

    with pytest.raises(SocketConnectBlockedError):
        asyncio.run(call())


def test_prompt_shields_answers_from_memory_in_a_test() -> None:
    """G-144: every guarded turn in the suite called live Content Safety (2 calls a turn; 429s
    under the parallel run failed the turn closed). In a test it answers "no attack", reachable."""
    import asyncio

    from backend.core import content_safety

    verdict = asyncio.run(content_safety.shield(user_prompt="hello", documents=["a", "b"]))
    if content_safety.configured():
        assert verdict["reachable"] and not verdict["user_attack"], verdict
        assert verdict["document_attacks"] == [False, False], verdict
