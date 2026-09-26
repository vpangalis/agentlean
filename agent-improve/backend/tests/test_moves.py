"""The coaching move is decided in code — step 6.61.

Founder ruling 2026-09-25 (ARCHITECTURE.md v1.75, CLAUDE.md §21). Each test
here is one clause of it, driven against `backend/phases/moves.py` with a fake
judgment — the ONE thing the planner's model decides — so what is proven is
that everything else is code:

    not yet taught            -> teach, and no model call
    answered, sufficient      -> read back the Belt's own words, held PENDING
    answered, insufficient    -> challenge, naming what is missing
    read back, the Belt: yes  -> store the pending value, and advance
    read back, a correction   -> answered again: judged, read back again
    a question, not an answer -> respond; the status does not change

Plus the D7 guard (6.61's 8D): the coaching rules and the Define script carry
no move-sequencing text. 6.62 extends the same guard to the other four scripts.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, cast

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from backend.core import prompts
from backend.core.substate import SufficiencyJudgment
from backend.phases import moves

AD5 = ("Late payments to our suppliers are costing us: we paid about £62,000 in "
       "late-payment interest and lost early-payment discounts last year, and "
       "three key medical suppliers put us on stop twice this year, which held "
       "up ward stock.")


class Judge:
    """The planner model's one judgment, faked — and counted."""

    def __init__(self, verdict: str = "sufficient", reason: str = "complete") -> None:
        self.verdict, self.reason = verdict, reason
        self.calls: list[tuple[str, str, str, str]] = []

    async def __call__(self, field: str, previous: str, latest: str,
                       reading_back: str) -> SufficiencyJudgment:
        self.calls.append((field, previous, latest, reading_back))
        return SufficiencyJudgment(verdict=self.verdict, reason=self.reason)  # type: ignore[arg-type]


def _decide(field_status: dict | None, belt: str, judge: Judge,
            artifacts: dict | None = None, phase: str = "define",
            action: str | None = None) -> dict[str, Any]:
    return asyncio.run(moves.decide(phase, dict(artifacts or {}), dict(field_status or {}),
                                    belt, judge, action=action))


# ── the walk and the status — STORED (ruling R5) ─────────────────────────


def test_define_walks_thirteen_positions_with_three_fields_inside() -> None:
    """R4 (2026-09-26): thirteen elements; the CTQs inside 3, the 5W2H inside
    4, the registry inside 5."""
    walk = moves.positions("define")
    assert len(walk) == 13
    assert walk[0] == ("business_case", ("business_case",))
    assert walk[2] == ("voc_summary", ("voc_summary", "critical_to_quality"))
    assert walk[3] == ("problem_statement", ("problem_statement", "problem_5w2h"))
    assert walk[4] == ("baseline_estimate", ("baseline_estimate", "metric_definitions"))
    assert walk[9] == ("benefits_analysis", ("benefits_analysis",))


def test_the_status_is_stored_never_derived_from_a_reply() -> None:
    """R5: four statuses, all starting "not taught", read from
    `PhaseState.field_status`. A case from before 6.61 — values stored, no
    statuses — reads its stored positions as confirmed."""
    s = moves.field_statuses("define", {}, {"team": {"status": "asked"}})
    assert (s["business_case"], s["team"], s["voc_summary"]) == ("not taught", "asked", "not taught")
    legacy = moves.field_statuses("define", {"business_case": "x"}, {})
    assert legacy["business_case"] == "confirmed"


# ── the moves ────────────────────────────────────────────────────────────


def test_opening_teaches_the_first_field_and_asks_the_model_nothing() -> None:
    judge = Judge()
    d = _decide(None, "Hi — I'm ready to start Define.", judge)
    assert (d["field"], d["status"], d["move"]) == ("business_case", "not taught", "teach")
    assert d["field_status"]["business_case"]["status"] == "asked", "code records the teach"
    assert judge.calls == []


def test_a_good_answer_is_read_back_and_held_pending() -> None:
    judge = Judge("sufficient")
    d = _decide({"business_case": {"status": "asked"}}, AD5, judge)
    assert (d["status"], d["move"]) == ("asked", "read_back")
    after = d["field_status"]["business_case"]
    assert after["status"] == "answered" and after["pending"]["belt_words"] == AD5
    assert d["store"] == {}, "nothing is stored on a read-back"
    assert len(judge.calls) == 1


def test_a_weak_answer_is_challenged() -> None:
    judge = Judge("insufficient", "no cost figure")
    d = _decide({"business_case": {"status": "asked"}}, "It's a bit slow.", judge)
    assert (d["move"], d["store"]) == ("challenge", {})
    assert d["reason"] == "no cost figure"
    assert d["field_status"]["business_case"] == {"status": "asked", "answer": "It's a bit slow.",
                                                  "messages": 1}


def test_the_piece_a_challenge_asked_for_joins_the_answer() -> None:
    judge = Judge("sufficient")
    fs = {"business_case": {"status": "asked", "answer": "It's slow.", "messages": 1}}
    d = _decide(fs, "It costs £62,000 a year.", judge)
    assert d["move"] == "read_back"
    assert d["pending"]["belt_words"] == "It's slow.\nIt costs £62,000 a year."
    assert d["pending"]["messages"] == 2


def _awaiting(store: dict | None = None) -> dict:
    return {"business_case": {
        "status": "answered", "answer": AD5, "messages": 1,
        "pending": {"field": "business_case", "fields": ["business_case"], "belt_words": AD5,
                    "messages": 1,
                    "store": store if store is not None else {"business_case": AD5}}}}


def test_the_belt_types_yes_and_the_pending_value_is_stored() -> None:
    judge = Judge()
    d = _decide(_awaiting(), "Yes, that's right.", judge)
    assert (d["move"], d["stored_field"]) == ("store_and_advance", "business_case")
    assert d["store"] == {"business_case": AD5}
    assert d["field"] == "team", "the same reply teaches the next field"
    assert d["field_status"]["business_case"]["status"] == "confirmed"
    assert d["field_status"]["team"]["status"] == "asked"
    assert judge.calls == [], "a plain yes costs no model call"


def test_the_belt_clicks_confirm_and_the_status_is_set_in_code() -> None:
    """R4 — a click, whatever the text says."""
    judge = Judge()
    d = _decide(_awaiting(), "Confirm", judge, action="confirm")
    assert (d["move"], d["store"]) == ("store_and_advance", {"business_case": AD5})
    assert judge.calls == []


def test_the_belt_clicks_change_and_the_field_goes_back_to_asked() -> None:
    judge = Judge()
    d = _decide(_awaiting(), "Change", judge, action="change")
    assert d["move"] == "challenge" and d["reason"] == moves.CHANGE_REASON
    assert d["field_status"]["business_case"]["status"] == "asked"
    assert d["field_status"]["business_case"]["answer"] == AD5, "their words are kept"
    assert d["store"] == {} and judge.calls == []


def test_the_belt_corrects_the_read_back_and_it_is_answered_again() -> None:
    """*"The Belt correcting a read-back returns to 'answered'."*"""
    judge = Judge("sufficient")
    d = _decide(_awaiting(), "Nearly — it was £65,000, not £62,000.", judge)
    assert d["move"] == "read_back" and d["store"] == {}
    assert d["pending"]["messages"] == 2, "a corrected answer spans two messages"
    assert judge.calls[0][3] == "yes", "the judge is told a read-back awaits confirmation"


def test_where_do_we_stand_is_answered_and_the_status_does_not_move() -> None:
    judge = Judge("not_an_answer", "asks for the status")
    taught = _decide({"business_case": {"status": "asked"}}, "Where do we stand?", judge)
    assert taught["move"] == "respond"
    assert taught["field_status"]["business_case"] == {"status": "asked"}
    awaiting = _decide(_awaiting(), "Where do we stand?", judge)
    assert awaiting["move"] == "respond"
    assert awaiting["field_status"]["business_case"]["pending"]["belt_words"] == AD5
    assert awaiting["store"] == {}


def test_a_yes_that_cannot_complete_the_position_is_read_back_again() -> None:
    fs = {"business_case": {"status": "confirmed"},
          "team": {"status": "answered", "pending": {
              "field": "team", "fields": ["team"], "belt_words": "Ana leads.",
              "messages": 1, "store": {}}}}
    d = _decide(fs, "Yes.", Judge(), artifacts={"business_case": "x"})
    assert (d["move"], d["store"]) == ("read_back", {})


def test_every_field_confirmed_is_a_response_not_a_move_on_a_field() -> None:
    done = {f: "x" for _, fs in moves.positions("define") for f in fs}
    d = _decide(None, "Anything else?", Judge(), artifacts=done)
    assert (d["field"], d["move"]) == (None, "respond")


def test_the_other_phases_walk_their_gate_list() -> None:
    d = _decide(None, "hello", Judge(), phase="measure")
    assert d["move"] == "teach" and d["field"] == moves.positions("measure")[0][0]


def test_sections_3_and_4_agree_on_the_confirming_turn() -> None:
    """Item 2 — section 3 is the state AFTER this turn's change: business_case
    confirmed and stored, Step 2 of 13, team current — what section 4 says."""
    from langchain_core.messages import HumanMessage as H
    from backend.core.substate import CoachingPlan
    from backend.middleware.state_injection import BeforeModelStateInjection
    d = _decide(_awaiting(), "Yes, that's right.", Judge())
    plan = CoachingPlan(focus_field=d["field"], status=d["status"], move=d["move"],
                        store=d["store"], stored_field=d["stored_field"],
                        statuses=d["statuses"], field_status=d["field_status"])
    mw = BeforeModelStateInjection("define", cast(Any, {
        "artifacts": {}, "phase_context": "", "coaching_plan": plan,
        "messages": [H(content="Yes, that's right.")]}))
    mw.before_agent(None, None)
    state, move = mw._block, mw._move
    assert "Define · Step 2 of 13" in state
    assert "1. business_case — confirmed" in state and "CURRENT FIELD: team" in state
    assert f"business_case: {AD5[:60]}" in state, "shown stored"
    assert "RECORD `business_case`, THEN TEACH `team`" in move
    assert "Field: team — status after this turn: asked" in move, "section 4's status is section 3's"


# ── confirmation is a rule ───────────────────────────────────────────────


@pytest.mark.parametrize("text", [
    "Yes", "yes, that's right.", "Yes, that's right — please record it exactly as I said it.",
    "That's correct", "Correct.", "Looks good", "Yep, no changes", "Perfect, thanks!",
])
def test_a_plain_yes_confirms(text: str) -> None:
    assert moves.is_confirmation(text), text


@pytest.mark.parametrize("text", [
    "Yes but the figure was £65,000", "No", "Nearly — change the second supplier",
    "Yes, and also add the ward stock delays", "Where do we stand?", "Actually it was three stops",
    "", "It costs us £62,000 a year",
])
def test_anything_more_than_a_plain_yes_does_not(text: str) -> None:
    assert not moves.is_confirmation(text), text


# ── what a confirmation stores ───────────────────────────────────────────


def test_a_one_message_string_answer_stores_the_belts_words_not_a_paraphrase() -> None:
    """AD5: the coach's tidied read-back dropped the stops. The store is the
    Belt's own words, whatever the read-back reworded."""
    pending = {"field": "business_case", "fields": ["business_case"], "belt_words": AD5, "messages": 1}
    store = moves.pending_store("define", pending, {"business_case": "Late payments cost £62k."})
    assert store == {"business_case": AD5}
    assert "three key medical suppliers" in store["business_case"] and "twice" in store["business_case"]


def test_a_composed_or_corrected_answer_stores_the_version_read_back() -> None:
    composed = {"field": "problem_statement", "fields": ["problem_statement"],
                "belt_words": "what: … where: …", "messages": 1}
    assert moves.pending_store("define", composed, {"problem_statement": "Between …"}) == {
        "problem_statement": "Between …"}
    corrected = {"field": "business_case", "fields": ["business_case"],
                 "belt_words": AD5 + "\nit was £65,000", "messages": 2}
    assert moves.pending_store("define", corrected, {"business_case": "£65,000 …"}) == {
        "business_case": "£65,000 …"}


def test_position_five_stores_both_of_its_fields() -> None:
    pending = {"field": "baseline_estimate", "fields": ["baseline_estimate", "metric_definitions"],
               "belt_words": "error rate 12%", "messages": 1}
    registry = [{"name": "invoice_error_rate", "unit": "%", "meaning": "returned invoices"}]
    store = moves.pending_store("define", pending, {"baseline_estimate": "about 12%",
                                                    "metric_definitions": registry})
    assert store == {"baseline_estimate": "error rate 12%", "metric_definitions": registry}


# ── D7: no move-sequencing in the rules or the Define script ─────────────

#: Phrases that sequence moves — the wording the ruling removed. 6.62 applies
#: the same list to the other four scripts.
SEQUENCING = re.compile(
    r"(?i)\b(then move on|move on\b|moving on|then advance|, advance\b|\badvance\.|"
    r"confirm and (move|advance)|one move, then stop|does one thing and then stops|"
    r"ends the turn|the next turn\b(?! and)|one at a time|column by column|"
    r"\*\*confirm\*\*)")


def test_the_coaching_rules_carry_no_move_sequencing() -> None:
    for name in ("COACHING_STANCE", "CAPTURE_CONTRACT", "ANTI_HALLUCINATION",
                 "MEMORY_HIERARCHY", "CONTRADICTION_CHECK"):
        hits = SEQUENCING.findall(getattr(prompts, name))
        assert not hits, f"{name} sequences moves: {hits}"


def test_the_define_script_carries_no_move_sequencing() -> None:
    from backend.middleware.skills import SKILLS_ROOT
    d = SKILLS_ROOT / "dmaic-define-phase"
    for f in ("coaching_script.md", "SKILL.md"):
        text = (d / f).read_text(encoding="utf-8")
        text = text.replace("gone by the next turn", "")    # a block's lifetime, not a move
        hits = SEQUENCING.findall(text)
        assert not hits, f"{f} sequences moves: {hits}"


def test_the_guard_would_have_caught_the_old_text() -> None:
    """The mutation proof: the lines 6.61 removed, quoted, are caught."""
    removed = ["> **Confirm**, then move on.",
               "  A coaching turn does ONE thing and then stops for the Belt's reply.",
               "> **Confirm** each name with its role and function, then advance.",
               "> **Ask (one at a time):** What's happening?"]
    for line in removed:
        assert SEQUENCING.search(line), line


# ── item 3: the grader per move; section 5 never contradicts section 4 ─────


def test_each_move_is_graded_only_on_what_it_does() -> None:
    """A read-back is not failed for not challenging, and a challenge is not
    failed for not citing methodology — fix 1's cause: that verdict, carried
    into the next challenge, sent the coach on lookups the move never asked
    for (4 of 5 live runs, one to the backstop)."""
    from backend.middleware.grader import applies, rubric_for_move
    methodology = "Coach must reference methodology when guiding (not just opinion)"
    challenge = "Coach must challenge weak inputs with specific follow-up questions"
    assert not applies(methodology, "challenge") and applies(challenge, "challenge")
    assert not applies(challenge, "read_back") and not applies(challenge, "store_and_advance")
    assert applies(methodology, "teach")
    computation = "Coach must not dump raw statistical output without explanation."
    assert [m for m in ("teach", "challenge", "read_back", "store_and_advance", "respond")
            if applies(computation, m)] == ["teach", "store_and_advance"]
    assert "reference methodology" not in rubric_for_move("challenge")
    assert "challenge weak inputs" in rubric_for_move("challenge")


def test_section_5_leaves_out_what_this_turns_move_does_not_do() -> None:
    from backend.core.substate import CoachingPlan
    from backend.middleware.state_injection import BeforeModelStateInjection
    methodology = "Coach must reference methodology when guiding (not just opinion)"
    fb: dict[str, Any] = {"grader": {"status": "fail", "criteria_failed": [methodology],
                     "failed": [{"criterion": methodology, "feedback": "cite the book"}]},
          "coherence": {"coherent": True, "reason": ""}}
    prior = AIMessage(content="What is it costing you?",
                      additional_kwargs={moves.QUALITY_FEEDBACK_KEY: fb})

    def section_5(move: str) -> str:
        plan = CoachingPlan(focus_field="business_case", status="asked", move=move)
        mw = BeforeModelStateInjection("define", cast(Any, {
            "artifacts": {}, "phase_context": "", "coaching_plan": plan,
            "messages": [HumanMessage(content="Hi"), prior, HumanMessage(content="It's slow.")]}))
        return mw._compose_feedback()

    assert "nothing that applies to this turn's move" in section_5("challenge")
    assert "cite the book" in section_5("teach")
    # A verdict on a reply graded as a read-back carries nothing a read-back
    # is not graded on — even into a move that would be.
    fb["grader"]["move"] = "read_back"
    assert "nothing that applies to this turn's move" in section_5("teach")

