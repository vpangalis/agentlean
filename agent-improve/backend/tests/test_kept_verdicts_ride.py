"""ADR-0109 (founder and Desktop, 2026-10-22; supersedes ADR-0108): the kept verdicts (`judged`, `gate`, `offered`,
DEF-224 / DEF-098) ride only on the reply whose turn changed them; the record on every reply carries none; the
newest record is read back with the newest verdicts joined in, so every reader sees what it saw before."""
from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from backend.phases import record

JUDGED = {"fp": "f1", "verdict": {"status": "sufficient"}}
GATE = {"c1": {"fp": "f1", "status": "pass", "feedback": ""}}


def _full(**entries: dict) -> dict:
    return {**record.empty("define"), "field_status": {f: dict(v) for f, v in entries.items()}}


def _reply(messages: list, full: dict) -> AIMessage:
    """What graph.py attaches: the turn's payload, the merged record in it."""
    payload = {"phase": "define", "field_status": dict(full["field_status"]), record.KEY: full}
    msg = AIMessage(content="ok", additional_kwargs=record.for_reply(payload, messages, "define"))
    messages.append(msg)
    return msg


def test_the_reply_carries_the_verdicts_only_when_its_turn_changed_them() -> None:
    msgs: list = [HumanMessage(content="hi")]
    first = _reply(msgs, _full(goal_statement={"status": "answered", "judged": JUDGED, "gate": GATE}))
    rec = first.additional_kwargs[record.KEY]
    assert rec["field_status"]["goal_statement"] == {"status": "answered"}, "the record carries no verdict"
    assert "judged" not in first.additional_kwargs["field_status"]["goal_statement"]
    assert first.additional_kwargs[record.KEPT_KEY] == {
        "phase": "define", "verdicts": {"goal_statement": {"judged": JUDGED, "gate": GATE}}}

    msgs.append(HumanMessage(content="next"))
    second = _reply(msgs, _full(goal_statement={"status": "confirmed", "judged": JUDGED, "gate": GATE}))
    assert record.KEPT_KEY not in second.additional_kwargs, "unchanged verdicts are not carried again"

    joined = record.latest(msgs, "define") or {}
    assert joined["field_status"]["goal_statement"] == {"status": "confirmed", "judged": JUDGED, "gate": GATE}
    assert record.latest_by_phase(msgs)["define"] == joined


def test_a_cleared_verdict_is_carried_as_cleared() -> None:
    msgs: list = []
    _reply(msgs, _full(team={"status": "answered", "judged": JUDGED}))
    cleared = _reply(msgs, _full(team={"status": "answered"}))
    assert cleared.additional_kwargs[record.KEPT_KEY]["verdicts"] == {}
    assert (record.latest(msgs, "define") or {})["field_status"]["team"] == {"status": "answered"}


def test_an_old_checkpoint_reads_the_same_and_its_verdicts_carry_on() -> None:
    """A reply written before ADR-0109 holds its verdicts inside the record: it is read as before, and a newer reply
    that changed nothing (so carries none) still reads them from it."""
    old_rec = _full(goal_statement={"status": "answered", "judged": JUDGED, "offered": {"value": "x"}})
    msgs: list = [AIMessage(content="old", additional_kwargs={record.KEY: old_rec})]
    assert record.latest(msgs, "define") == old_rec
    newer = _reply(msgs, _full(goal_statement={"status": "answered", "judged": JUDGED, "offered": {"value": "x"}}))
    assert record.KEPT_KEY not in newer.additional_kwargs
    assert (record.latest(msgs, "define") or {})["field_status"]["goal_statement"]["offered"] == {"value": "x"}
