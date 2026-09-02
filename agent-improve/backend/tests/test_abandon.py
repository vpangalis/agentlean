"""§47 requirement 1 — the ABANDON policy on client disconnect.

**These tests exist because the first implementation was wrong twice, and both
times the unit tests were green.** Step 4.2's `azure-query` verification is what
caught it, and only because it was actually run against the live container.

  * **Attempt 1 — a plain inline `await`.** The reasoning was that the graph run
    is the handler's own task and so dies with the client. It does not:
    Starlette never cancels an endpoint coroutine on disconnect. A client killed
    3s into a 30s turn left the turn running; it finished 5s later, wrote 12
    checkpoint blobs and appended two turns to the case blob. **The Belt saw
    nothing and the checkpoint said the turn happened** — §47's opening finding,
    reproduced exactly.
  * **Attempt 2 — racing the run against a `Request.is_disconnected()` poll.**
    Also does not fire. `is_disconnected()` wraps uvicorn's `receive()` in an
    immediately-cancelled `CancelScope`, and that `receive()` does
    `flow.resume_reading()` *then* `await message_event.wait()` — so the poll
    re-arms the socket read and tears down the wait in the same tick, forever.
    The turn completed again, 19s after the client left.
  * **Attempt 3 — awaiting the raw ASGI `receive()`.** Fires on the disconnect
    itself. Verified live: the handler logged the abandonment in the same second
    as the abort, **no node ran at all**, no subgraph namespace was created, and
    the case blob was untouched.

So what is pinned here is the MECHANISM, not just the outcome: a future
refactor that "simplifies" this back to `is_disconnected()` or to a bare
`await` would pass a test that only checked the happy path.
"""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from backend.gateway.routes import ClientGone, _run_turn, _until_disconnect


class FakeRequest:
    """A `Request` stand-in whose `receive()` behaves the way uvicorn's does.

    `receive()` parks until something happens, then yields either an
    `http.request` frame or `http.disconnect` — which is the contract
    `_until_disconnect` is written against.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.is_disconnected_calls = 0

    async def receive(self) -> dict[str, Any]:
        return await self._queue.get()

    async def is_disconnected(self) -> bool:
        # The trap of attempt 2: it exists, it is tempting, and on this stack
        # it never reports True. Anything reading it is doing the wrong thing.
        self.is_disconnected_calls += 1
        return False

    def disconnect(self) -> None:
        self._queue.put_nowait({"type": "http.disconnect"})

    def send_body_frame(self) -> None:
        self._queue.put_nowait({"type": "http.request", "body": b"", "more_body": False})


class FakeGraph:
    """A graph whose `ainvoke` takes `duration` seconds and records its fate."""

    def __init__(self, duration: float = 5.0) -> None:
        self.duration = duration
        self.started = False
        self.completed = False
        self.cancelled = False

    async def ainvoke(self, state, config=None):
        self.started = True
        try:
            await asyncio.sleep(self.duration)
        except asyncio.CancelledError:
            self.cancelled = True
            raise
        self.completed = True
        return {"messages": [], "history": []}


# ── the policy ────────────────────────────────────────────────────────────

def test_a_completed_turn_returns_its_result() -> None:
    """The ordinary path: the client stays, the run wins the race."""
    graph = FakeGraph(duration=0.01)
    http = FakeRequest()
    result = asyncio.run(_run_turn(graph, {}, {}, http))  # type: ignore[arg-type]
    assert graph.completed and not graph.cancelled
    assert result == {"messages": [], "history": []}


def test_a_disconnect_cancels_the_run_and_raises_client_gone() -> None:
    """§47's ratified policy: ABANDON, not COMPLETE."""
    async def scenario():
        graph = FakeGraph(duration=30.0)
        http = FakeRequest()
        task = asyncio.create_task(
            _run_turn(graph, {}, {}, http))  # type: ignore[arg-type]
        await asyncio.sleep(0.05)          # let the run start
        assert graph.started
        http.disconnect()
        with pytest.raises(ClientGone):
            await task
        return graph

    graph = asyncio.run(scenario())
    assert graph.cancelled, "the graph run was not cancelled"
    assert not graph.completed, (
        "the turn completed behind a departed client — this is COMPLETE, and "
        "§47 rules it unacceptable for a nine-step HITL gate"
    )


def test_the_run_is_awaited_to_completion_before_the_handler_returns() -> None:
    """Cancelling without awaiting lets the run outlive the response.

    `task.cancel()` only REQUESTS cancellation. A handler that returns without
    awaiting the task leaves it to finish on the loop — still checkpointing,
    which is the defect the whole mechanism exists to remove.
    """
    async def scenario():
        graph = FakeGraph(duration=30.0)
        http = FakeRequest()
        task = asyncio.create_task(
            _run_turn(graph, {}, {}, http))  # type: ignore[arg-type]
        await asyncio.sleep(0.05)
        http.disconnect()
        with pytest.raises(ClientGone):
            await task
        # By the time ClientGone surfaces, the cancellation must already have
        # been delivered — not merely requested.
        return graph

    assert asyncio.run(scenario()).cancelled


# ── the mechanism, pinned so neither wrong attempt can return ─────────────

def test_the_watcher_does_not_use_is_disconnected() -> None:
    """Attempt 2's trap. `is_disconnected()` never reports True on this stack."""
    async def scenario():
        graph = FakeGraph(duration=30.0)
        http = FakeRequest()
        task = asyncio.create_task(
            _run_turn(graph, {}, {}, http))  # type: ignore[arg-type]
        await asyncio.sleep(0.05)
        http.disconnect()
        with pytest.raises(ClientGone):
            await task
        return http

    http = asyncio.run(scenario())
    assert http.is_disconnected_calls == 0, (
        "the watcher polled Request.is_disconnected() — it re-arms the socket "
        "read and tears down its own wait in the same tick, so it never fires "
        "(verified against the installed starlette 0.50 / uvicorn 0.29)"
    )


def test_body_frames_are_consumed_without_ending_the_turn() -> None:
    """A live client may send more frames; only `http.disconnect` abandons."""
    async def scenario():
        graph = FakeGraph(duration=0.4)
        http = FakeRequest()
        task = asyncio.create_task(
            _run_turn(graph, {}, {}, http))  # type: ignore[arg-type]
        await asyncio.sleep(0.05)
        http.send_body_frame()
        http.send_body_frame()
        return await task, graph

    result, graph = asyncio.run(scenario())
    assert graph.completed and not graph.cancelled
    assert result is not None


def test_the_watcher_returns_only_on_disconnect() -> None:
    """`_until_disconnect` in isolation: parks on frames, returns on the hangup."""
    async def scenario():
        http = FakeRequest()
        watcher = asyncio.create_task(
            _until_disconnect(http))  # type: ignore[arg-type]
        http.send_body_frame()
        await asyncio.sleep(0.05)
        assert not watcher.done(), "a body frame ended the watch"
        http.disconnect()
        await asyncio.wait_for(watcher, timeout=1.0)

    asyncio.run(scenario())


def test_the_watcher_is_cleaned_up_when_the_run_wins() -> None:
    """A leaked watcher would hold the connection's receive channel open."""
    async def scenario():
        graph = FakeGraph(duration=0.01)
        http = FakeRequest()
        before = len(asyncio.all_tasks())
        await _run_turn(graph, {}, {}, http)  # type: ignore[arg-type]
        await asyncio.sleep(0)
        return before, len(asyncio.all_tasks())

    before, after = asyncio.run(scenario())
    assert after <= before, "the disconnect watcher outlived the turn"
