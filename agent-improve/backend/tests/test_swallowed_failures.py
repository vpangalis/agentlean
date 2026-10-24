"""The failures the audit found swallowed or logged without what an operator needs (W5, W6, W7, W9; founder ruling
2026-10-24, B5) — each now says what happened, and none reports a state it did not reach."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, cast

import pytest


def test_w5_an_undo_that_fails_says_so(monkeypatch, caplog) -> None:
    """G-267: when a failed approval's undo itself fails, the undo reports False and logs CRITICAL naming the case —
    no longer an error line that reads like the end of the story."""
    from backend.core import graph
    from backend.storage import blob
    from backend.storage.models import CaseDocument

    before = CaseDocument.new(case_id="C-W5", title="t", belt_level="green", leader="L", department="D",
                              target_date="2027-03-31", team=[])

    async def unreachable(_cid: str) -> Any:
        raise ConnectionError("storage unreachable")
    monkeypatch.setattr(blob, "load_case", unreachable)
    with caplog.at_level(logging.CRITICAL, logger="backend.core.graph"):
        assert asyncio.run(graph._undo_case_write("C-W5", "define", before)) is False
    assert any(r.levelno == logging.CRITICAL and "C-W5" in r.getMessage() for r in caplog.records), caplog.text

    class Store:
        def get(self, *a: Any, **k: Any) -> Any:
            raise ConnectionError("storage unreachable")
    caplog.clear()
    with caplog.at_level(logging.CRITICAL, logger="backend.core.graph"):
        assert graph._undo_gate_write(Store(), "C-W5", "define", {"x": 1}) is False
    assert any(r.levelno == logging.CRITICAL and "C-W5" in r.getMessage() for r in caplog.records), caplog.text
    assert graph._undo_gate_write(None, "C-W5", "define", {"x": 1}) is True, "nothing to undo is not a failure"


def test_w6_a_date_that_cannot_be_read_leaves_the_rag_status_as_it_was(caplog) -> None:
    """G-268: the case list's RAG status is recomputed from the dates; a date that cannot be read leaves the status
    as it was and logs the case — never the green it used to be set to."""
    from backend.storage import blob
    from backend.storage.models import CaseDocument, CaseRegistry, RegistryEntry

    case = CaseDocument.new(case_id="C-W6", title="t", belt_level="green", leader="L", department="D",
                            target_date="not a date", team=[])
    entry = RegistryEntry(case_id="C-W6", title="t", belt_level="green", leader="L", department="D",
                          created_at=case.created_at, target_date="not a date", current_phase="define",
                          rag_status="red")
    registry = CaseRegistry(cases=[entry])
    with caplog.at_level(logging.WARNING, logger="backend.storage.blob"):
        blob._gate_passed_entry(registry, case, "define", "approved", "2026-10-24T00:00:00+00:00")
    assert registry.cases[0].rag_status == "red", registry.cases[0].rag_status
    assert any("C-W6" in r.getMessage() and "RAG" in r.getMessage() for r in caplog.records), caplog.text


def test_w7_the_guard_says_when_it_loses_the_element(monkeypatch, caplog) -> None:
    """G-269: the input guard's element context, read from the Store, is logged when it cannot be read — the reply
    still goes out, without it; and its runtime probe catches only the error raised outside a graph run."""
    from backend.core import guard
    from backend.phases import mappers_common

    def unreadable(*a: Any, **k: Any) -> Any:
        raise ConnectionError("store unreachable")
    monkeypatch.setattr(mappers_common, "read_case_record", unreadable)
    with caplog.at_level(logging.WARNING, logger="backend.core.guard"):
        state = cast(Any, {"current_phase": "define", "case_id": "C-W7", "messages": []})
        field = guard.current_field(state, cast(Any, object()))
    assert field == "business_case", field
    assert any("could not be read" in r.getMessage() for r in caplog.records), caplog.text
    assert guard._attempt() == 1


@pytest.mark.degraded_expected
def test_w9_a_degraded_reply_logs_the_traceback_behind_it(caplog) -> None:
    """G-270: in production the degraded reply's failure is logged with its traceback, which the handler's own line
    (type and message) does not carry. Marked degraded_expected so the suite's re-raise does not replace it."""
    from backend.core import graph

    try:
        raise ValueError("the gate document could not be assembled")
    except ValueError as exc:
        cause = exc
    with caplog.at_level(logging.ERROR, logger="backend.core.graph"):
        graph.on_degraded("define_phase", cause)
    rec = next(r for r in caplog.records if "behind the degraded reply" in r.getMessage())
    assert rec.exc_info and rec.exc_info[1] is cause and rec.exc_info[2] is not None, rec.exc_info
