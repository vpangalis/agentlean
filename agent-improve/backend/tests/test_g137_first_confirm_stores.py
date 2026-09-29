"""G-137 — element 5's FIRST read-back carries the metric definitions, so the Belt's first Confirm
stores (founder rulings 2026-09-29, item 2; DEF-008 stays strict: every Confirm stores).

Two run-throughs (define_runthrough_20260929T111219, …113121) read back the baseline and left
`metric_definitions` out — named second, after a baseline entry that says "the Belt's words" — so
the first Confirm was refused; the retry, whose instruction opened with what was missing and that
nothing was stored, carried both. The read-back instruction now opens with the entries, the
structured one first with its keys, and what leaving one out costs.
"""
from __future__ import annotations

from typing import Any, cast

import pytest
from langchain_core.messages import HumanMessage

from backend.core.substate import CoachingPlan
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases import moves
from backend.phases.define.schema import METRIC_DEFINITION_KEYS

#: The Belt's answer at element 5 in both failing runs, word for word.
BELT_5 = ("One metric: late payment rate, in %, meaning the share of supplier invoices paid more than "
          "30 days after the invoice date. It is about 23% today, from the AP ledger for January to June "
          "2026. It feeds our finance KPI, creditor days.")


def _move_section(plan: CoachingPlan) -> str:
    # List content on the Belt's message (§4.5: a message-construction test uses list content).
    state: Any = {"artifacts": {}, "phase_context": "", "coaching_plan": plan,
                  "messages": [HumanMessage(content=[{"type": "text", "text": BELT_5}])]}
    mw = BeforeModelStateInjection("define", cast(Any, state))
    mw.before_agent(None, None)
    return mw._move[mw._move.index("MOVE: READ BACK"):]


def _read_back(field: str) -> CoachingPlan:
    fields = list(dict(moves.positions("define"))[field])
    return CoachingPlan(focus_field=field, status="answered", move="read_back",
                        pending={"field": field, "fields": fields, "belt_words": BELT_5, "messages": 1})


def test_g137_element_5s_first_read_back_names_the_registry_first_with_its_keys() -> None:
    body = _move_section(_read_back("baseline_estimate"))
    registry, baseline = body.index("  - `metric_definitions`:"), body.index("  - `baseline_estimate`:")
    assert registry < baseline, "the structured entry comes first"
    keys = "{" + ", ".join(METRIC_DEFINITION_KEYS) + "}"
    assert keys in body and "the primary metric FIRST" in body
    # What leaving one out costs is said BEFORE the read-back is described, as the retry said it.
    assert body.index("stores NOTHING when the Belt confirms") < body.index("Read back ONE version")
    assert "without this entry nothing of the position can be stored" in body
    assert "by the unit `metric_definitions` gives" in body


@pytest.mark.parametrize("field", ["voc_summary", "problem_statement", "baseline_estimate"])
def test_g137_every_two_field_read_back_lists_every_entry_the_structured_one_first(field: str) -> None:
    fields = dict(moves.positions("define"))[field]
    assert len(fields) == 2
    body = _move_section(_read_back(field))
    at = {f: body.index(f"  - `{f}`:") for f in fields}
    inside = next(f for f in fields if f != field)              # the CTQs, the 5W2H, the registry
    assert at[inside] < at[field], (field, at)
