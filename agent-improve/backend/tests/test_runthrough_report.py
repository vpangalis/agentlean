"""The run-through report's "Grader findings" section (founder ruling 2026-10-14) — offline, no model call."""
from __future__ import annotations



def test_the_grader_findings_section_reads_each_turns_step_log(monkeypatch) -> None:
    """Founder ruling 2026-10-14 — offline: the run-through report's "Grader findings" lists each flagged
    turn with its move, element, failed criterion and the grader's reason, counts per criterion, and the
    coached replies without a verdict; a turn's entry is read only from that turn's own checkpoint."""
    from langchain_core.messages import AIMessage, HumanMessage
    import scripts.coaching_proof_656 as proof
    from scripts import define_runthrough as R

    final = {"messages": [HumanMessage(content="Our scope is invoices."), AIMessage(content="Here is the scope.")],
             "step_log": [{"node": "coaching_grader", "status": "failed", "move": "read_back",
                           "failed": [{"criterion": "C3", "feedback": "adds a step the Belt did not give"}]}]}
    monkeypatch.setattr(proof, "_latest_final", lambda case_id: final)
    entry = R.grader_entry("case-1", "Our scope is invoices.")
    assert entry == {"status": "failed", "move": "read_back",
                     "failed": [{"criterion": "C3", "reason": "adds a step the Belt did not give"}]}
    assert R.grader_entry("case-1", "Confirm") is None          # the checkpoint is another turn's
    turns = [{"kind": "turn", "n": 4, "field": "project_scope", "move": "read_back", "model_calls": ["coach", "grader"],
              "grader": entry},
             {"kind": "turn", "n": 5, "field": "project_scope", "model_calls": ["coach", "grader"],
              "grader": {"status": "pass", "move": "teach", "failed": []}},
             {"kind": "turn", "n": 6, "model_calls": ["coach"], "grader": None},
             {"kind": "turn", "n": 7, "model_calls": [], "grader": None}]
    g = R.grader_findings(turns)
    assert g["findings"] == [{"n": 4, "move": "read_back", "element": "project_scope", "criterion": "C3",
                              "reason": "adds a step the Belt did not give"}]
    assert g["per_criterion"] == {"C3": 1} and g["coached_replies"] == 3 and g["without_verdict"] == [6]
    text = R.grader_findings_text(g)
    assert "## Grader findings" in text and "| 4 | read_back | project_scope | C3 |" in text
