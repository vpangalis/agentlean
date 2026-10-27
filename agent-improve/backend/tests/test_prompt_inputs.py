"""G-252 — what the coach and the grader read, and the schema the coach writes (founder ruling 2026-10-23
afternoon, item 2 a-f; measured first in Claude outputs/PROMPT_ANATOMY.md).

a. No value is cut: a value the current element needs is sent complete; another element's is one line written in
   code ("High-level process (SIPOC, as-is): 6 steps, confirmed"). The grader's context the same way.
b. Display names, never code names, for the values.
c. Each section's body and each value in XML-style tags; no Python dict text.
d. CoachingResponse's description says what the reply is, in a line or two; no field description carries a §, ADR,
   step or defect code.
e. fields_captured is a typed entry (field_name from the phase's field list, value, source); its shape rules are in
   the turn's task section, for the fields read back.
f. citations and contradiction_flag are typed (CONTRADICTION_FLAG_KEYS defines the latter).
"""
from __future__ import annotations

import json
import re
from typing import Any, cast

from langchain_core.messages import HumanMessage

from backend.core.substate import (CONTRADICTION_FLAG_KEYS, CoachingPlan, CoachingResponse,
                                   coaching_response_model)
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases import moves

LONG_CASE = ("Across our three hospital sites, 23% of supplier invoices were paid after their 30-day terms from "
             "January to June 2026. " * 8 + "We paid about EUR 62,000 in interest and lost discounts last year.")
SIPOC = {"suppliers": "Suppliers", "inputs": "Invoices", "outputs": "Payments", "customers": "Suppliers",
         "process_metrics": "Days to pay", "process_performance": {"lead_time": "about 40 days"},
         "process_steps": [{"name": f"Step number {i}", "duration": {"avg": "1 day"}} for i in range(1, 7)]}
TEAM = [{"name": "Priya Shah", "role": "Leader", "function": "Green Belt"},
        {"name": "Tom Okafor", "role": "Sponsor", "function": "Finance Director"}]


def _sections(plan: CoachingPlan, artifacts: dict[str, Any]) -> BeforeModelStateInjection:
    state: Any = {"artifacts": artifacts, "phase_context": "", "coaching_plan": plan,
                  "messages": [HumanMessage(content=[{"type": "text", "text": "hello"}])]}
    mw = BeforeModelStateInjection("define", cast(Any, state))
    mw.before_agent(None, None)
    return mw


def _confirmed(block: str) -> str:
    return block[block.index("<confirmed_values>"):block.index("</confirmed_values>")]


def _asked(field: str) -> CoachingPlan:
    return CoachingPlan(focus_field=field, status="asked", move="teach")


def test_a_a_value_the_current_element_needs_is_sent_complete() -> None:
    mw = _sections(_asked("problem_statement"), {"business_case": LONG_CASE, "team": TEAM})
    assert LONG_CASE in mw._block, "the business case the problem statement needs was cut"


def test_a_another_elements_value_is_one_line_written_in_code() -> None:
    mw = _sections(_asked("issues_and_barriers"), {"business_case": LONG_CASE, "process_map_sipoc": SIPOC})
    line = next(l for l in _confirmed(mw._block).splitlines() if "High-level process" in l)
    assert "6 steps" in line and "confirmed" in line, line
    assert "Step number 3" not in mw._block, "a value the element does not need was sent whole"
    assert LONG_CASE not in mw._block and "Business case" in _confirmed(mw._block)


def test_a_the_value_awaiting_confirmation_is_sent_complete() -> None:
    plan = CoachingPlan(focus_field="business_case", status="answered", move="read_back",
                        pending={"field": "business_case", "fields": ["business_case"], "belt_words": LONG_CASE,
                                 "store": {"business_case": LONG_CASE}, "messages": 1})
    mw = _sections(plan, {})
    pending = mw._block[mw._block.index("<pending>"):mw._block.index("</pending>")]
    assert pending.count(LONG_CASE) >= 1, pending


def test_a_the_graders_context_is_never_cut() -> None:
    from backend.phases import nodes_common
    state: Any = {"artifacts": {"business_case": LONG_CASE, "process_map_sipoc": SIPOC}}
    context = nodes_common._grader_context("define", state, "problem_statement")
    assert LONG_CASE in context, context[:400]
    sipoc = next(l for l in context.splitlines() if "High-level process" in l)
    assert "6 steps" in sipoc and "Step number 3" not in context, sipoc


def test_b_values_carry_display_names_not_code_names() -> None:
    mw = _sections(_asked("issues_and_barriers"), {"business_case": LONG_CASE, "process_map_sipoc": SIPOC,
                                                     "team": TEAM})
    confirmed = _confirmed(mw._block)
    assert 'name="High-level process (SIPOC, as-is)"' in confirmed and 'name="Team"' in confirmed, confirmed
    for code in ("process_map_sipoc", "business_case", "team:"):
        assert code not in confirmed, (code, confirmed)


def test_c_each_section_and_value_is_tagged_and_no_dict_text() -> None:
    plan = CoachingPlan(focus_field="team", status="answered", move="read_back",
                        pending={"field": "team", "fields": ["team"], "belt_words": "Priya leads.",
                                 "store": {"team": TEAM}, "messages": 1})
    mw = _sections(plan, {"business_case": LONG_CASE, "process_map_sipoc": SIPOC})
    for tag in ("project_state", "confirmed_values", "pending"):
        assert f"<{tag}>" in mw._block and f"</{tag}>" in mw._block, tag
    assert "<this_turns_move>" in mw._move and "</this_turns_move>" in mw._move
    assert re.search(r'<value name="[^"]+"', mw._block)
    for text in (mw._block, mw._move):
        assert not re.search(r"\{'|': '|\['", text), re.search(r".{40}(\{'|': '|\[').{40}", text)


def _descriptions(node: Any, path: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        if isinstance(node.get("description"), str):
            out.append((path, node["description"]))
        for k, v in node.items():
            out += _descriptions(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _descriptions(v, f"{path}/{i}")
    return out


def test_d_the_schema_says_what_the_reply_is_without_codes() -> None:
    schema = coaching_response_model("define").model_json_schema()
    assert len(schema["description"]) <= 240 and schema["description"].count("\n") <= 1, schema["description"]
    codes = re.compile(r"§|\bADR\b|ADR-\d|\bstep \d|\bS-[A-Z]\d|\bG-\d|\bDEF-\d|\bv1\.\d|\bT\d\d\b")
    found = [(p, d) for p, d in _descriptions(schema) if codes.search(d)]
    assert not found, found
    assert len(json.dumps(schema)) < 4000, len(json.dumps(schema))


def test_e_fields_captured_is_a_typed_entry_from_the_phase_list() -> None:
    from backend.phases.gate_registry import GATE_SPECS
    schema = coaching_response_model("define").model_json_schema()
    item = schema["properties"]["fields_captured"]["items"]
    entry = schema["$defs"][item["$ref"].rsplit("/", 1)[-1]]
    names = set(entry["properties"]["field_name"]["enum"])
    assert names == set(GATE_SPECS["define"].model.model_fields) - {"computation_results", "acknowledged_gaps",
                                                                     "citations", "uploads"}, names
    assert {"value", "source"} <= set(entry["properties"]), entry["properties"]
    assert len(schema["properties"]["fields_captured"]["description"]) <= 200
    # The shape rules ride in the task section, for the fields read back.
    plan = CoachingPlan(focus_field="team", status="answered", move="read_back",
                        pending={"field": "team", "fields": ["team"], "belt_words": "Priya leads.", "messages": 1})
    move = _sections(plan, {})._move
    assert "LIST of {name, role, function}" in move and "control_plan" not in move, move[-900:]


def test_e_a_typed_capture_reaches_the_store_and_the_reasons() -> None:
    from backend.phases import nodes_common
    model = coaching_response_model("define")
    reply = model.model_validate({"message": "Is this right?", "fields_captured": [
        {"field_name": "team", "value": TEAM, "source": "belt", "reason": "Tom replaces Mark"}]})
    assert isinstance(reply, CoachingResponse)
    assert nodes_common._captured_fields("define", reply) == {"team": TEAM}
    assert nodes_common.captured_entries(reply) == [{"field_name": "team", "value": TEAM, "source": "belt",
                                                     "reason": "Tom replaces Mark"}]


def test_f_citations_and_the_contradiction_flag_are_typed() -> None:
    from backend.middleware.contradiction import ContradictionDetectionMiddleware
    schema = coaching_response_model("define").model_json_schema()
    cite = schema["$defs"][schema["properties"]["citations"]["items"]["$ref"].rsplit("/", 1)[-1]]
    assert {"source", "relevance_summary"} <= set(cite["properties"]), cite
    ref = next(a["$ref"] for a in schema["properties"]["contradiction_flag"]["anyOf"] if "$ref" in a)
    flag = schema["$defs"][ref.rsplit("/", 1)[-1]]
    assert tuple(flag["properties"]) == CONTRADICTION_FLAG_KEYS and set(flag["required"]) == set(CONTRADICTION_FLAG_KEYS)
    values = {k: f"{k} value" for k in CONTRADICTION_FLAG_KEYS}
    reply = coaching_response_model("define").model_validate({
        "message": "m", "contradiction_flag": values,
        "citations": [{"source": "ap.csv", "relevance_summary": "late rate"}]})
    assert ContradictionDetectionMiddleware._flag({"structured_response": reply}) == values
    assert moves is not None


# ── ADR-0111 (founder ruling 2026-10-27): D3 cuts said, D5 the grader reads what the coach read, G-254 given ──────


def test_adr_0111_d3_a_cut_is_a_cap_on_a_whole_part_and_says_so() -> None:
    """D3: cuts stay only as caps on whole parts, and every cut says so in the text ("[cut at N characters]"); the
    model-input builders cut through the one helper, never by slicing."""
    import inspect

    from backend.core.prompts import cut_at
    from backend.middleware import grader as G
    from backend.phases import nodes_common
    assert cut_at("abc", 3) == "abc"
    assert cut_at("abcdef", 3) == "abc [cut at 3 characters]"
    state: Any = {"phase_context": "framing " * 400, "artifacts": {}}
    prompt = nodes_common._judgment_prompt("define", state, "business_case", "", "Late payments.", False)
    assert "[cut at 1500 characters]" in prompt
    for fn in (G.DMAICGraderMiddleware._grade, nodes_common._judgment_prompt, nodes_common._grader_sources,
               nodes_common._grader_context, BeforeModelStateInjection._upload_manifest):
        assert not re.search(r"\[-?\d*:-?\d+\]", inspect.getsource(fn)), f"{fn.__qualname__} cuts by slicing"


def test_adr_0111_d5_the_grader_reads_the_values_and_the_pending_answer_as_section_3_gives_them() -> None:
    """D5: the coaching grader's "case so far" and its element sources are section 3's own lines, by the same
    functions — display names, tags, whole values — never a second rendering."""
    from backend.phases import nodes_common
    plan = CoachingPlan(focus_field="business_case", status="answered", move="read_back",
                        pending={"field": "business_case", "fields": ["business_case"], "belt_words": LONG_CASE,
                                 "store": {"business_case": LONG_CASE}, "messages": 1})
    artifacts = {"process_map_sipoc": SIPOC, "problem_statement": "23% of invoices are paid late."}
    block = _sections(plan, artifacts)._block
    state: Any = {"artifacts": artifacts, "coaching_plan": plan}
    context = nodes_common._grader_context("define", state, "business_case")
    sources = nodes_common._grader_sources("define", plan)
    assert LONG_CASE in sources and "High-level process" in context
    for part in (context, sources):
        missing = [line for line in part.splitlines() if line not in block]
        assert not missing, missing[:3]


def test_g254_code_written_lines_and_the_scripts_example_reach_the_grader_as_given_and_are_not_graded() -> None:
    """G-254 (founder ruling 2026-10-27, item 3): the eval's E20 failed on the coaching grader quoting the script's
    own example as ungrounded. What the reply carries as given — the element's worked example, a line code wrote —
    reaches the grader in its tag, and a fail quoting it is not counted; the coach's own words are graded."""
    import asyncio
    from types import SimpleNamespace

    from backend.middleware import grader as G
    from backend.middleware.skills import element_text
    from backend.validation.schemas import CoachingGraderVerdict, CriterionResult
    show = element_text("define", "secondary_metrics", "Show")
    calc = "Cost of the gap today (at the baseline): EUR 62,000 a year — 23% × 2,400 units × EUR 112."
    mw = G.DMAICGraderMiddleware("define", move="respond", given=(show, calc))
    own = "When the late rate falls, watch what else moves."
    reply = SimpleNamespace(message=f"{own}\n{calc}", explanation="", example=show, prompt="What else could change?")
    state: Any = {"structured_response": reply}
    shown = G.DMAICGraderMiddleware._coach_text(state, mw._is_given)
    assert shown.count("<given ") == 2 and own in shown and f">{own}<" not in shown, shown
    seen: list[str] = []

    class _Model:
        def with_structured_output(self, schema, **_):
            return self

        async def ainvoke(self, prompt):
            seen.append(prompt)
            return CoachingGraderVerdict(criteria=[
                CriterionResult(criterion="G3", status="fail", feedback="invented", evidence=show.strip('"')[:60]),
                CriterionResult(criterion="G1", status="fail", feedback="off the question", evidence=own)])
    original = G.get_llm
    G.get_llm = lambda role, **kw: _Model()          # type: ignore[assignment]
    try:
        mw._shown = shown                             # as aafter_agent sets it
        graded = asyncio.run(mw._grade("What could get worse?", G.DMAICGraderMiddleware._coach_text(state)))
    finally:
        G.get_llm = original                          # type: ignore[assignment]
    by = {c.criterion: c.status for c in graded.criteria}
    assert by == {"G3": "pass", "G1": "fail"}, by      # the given sentence is not graded; the coach's own is
    assert mw._uncounted and mw._uncounted[0]["given"] is True, mw._uncounted
    assert '<given source="code or the phase script" graded="no">' in seen[0]
