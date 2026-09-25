# -*- coding: utf-8 -*-
"""
The work, organised as Epic > Story > Task / Bug, each tagged with its component.
A STORY is functionality described from the Belt's side; its acceptance is one or more
capability rows (Appendix H IDs). A TASK is a procedure step. A BUG is something built
that is wrong. RANK is the order the stories were planned in; PRIORITY is Appendix F's
`Order` column (founder, 2026-09-25: "Priority = Appendix F Order column").

NO STATUS IS TYPED HERE (step 6.63, founder 2026-09-25: "Every number, label, diagram
element and status colour on the board is derived from the tree, never typed by hand").
Until 6.63 each task carried a typed status, and 6.54 and 6.46 still read "todo" after
both had landed. resolve() below derives every one from `progress.progress()`:
  a task that is a procedure step takes its step's state (proven / wired / built /
  blocked / unbuilt) — the three proofs of 6.63, read from the tree and git log
  a task that is not a procedure step ("—") has NO source, and says so ("none")
  a story is DONE when every one of its rows is proven; a story with no rows has no
  source, and says so
A BUG is (what is wrong, component, where it was found). Step 6.64 deleted the typed
status each bug carried ("done" / "todo" / "backlog") on the same ruling: nothing in
the tree derives a bug's state, so the board shows none rather than a typed one.
"""
from typing import Any

EPICS: list[dict[str, Any]] = [
 dict(id="E1", title="A Belt can complete Define and close its gate",
      why="The vertical. Done when every story below is done.",
      stories=[
  dict(id="S1", rank=None, rows=[18], comps=["Coach","Phase state"],
       title="What I tell the coach is kept in the shape the method needs",
       ask="My team is kept as a list of people with roles, my scope as in and out, my SIPOC as six parts.",
       tasks=[("6.48","Check each value against its declared type at capture","Phase state"),
              ("S-C05","Put each field's required shape on the response contract","Coach")],
       bugs=[]),
  dict(id="S2", rank=None, rows=[19], comps=["Gate"],
       title="When I have answered everything, a complete gate document can be built",
       ask="The preview shows me a full Define document, not an error.",
       tasks=[("6.20","Derive the Define metric entry at assembly","Gate")],
       bugs=[]),
  dict(id="S3", rank=None, rows=[20,21], comps=["Routes","Storage"],
       title="When I press Submit, my record is saved once and nothing I built is lost",
       ask="Submit saves exactly what the preview showed me; my change log, citations and uploads are still there afterwards.",
       tasks=[("6.42","Submit uses the same assembly as the preview; the save is safe to run twice \u2014 90948de","Routes")],
       bugs=[("write_phase_gate replaces the whole record and drops the change log and the uploads",
              "Storage","62d7f17")],
       note="Proven on the gate-proof case IMPR-2026-1FF: 13 change-log entries survived the write that used to erase them. Row 21's uploads half is proven by fixture only \u2014 1FF has no uploads. The next gate-proof case should carry one."),
  dict(id="S33", rank=3, rows=[25], comps=["Phase state","Coach"],
       title="The baseline and target I give are stored as values Control can compare",
       ask="When I say the error rate is 12.8% and I want 3%, those are kept as 12.8 and 3, percent \u2014 not as a sentence.",
       tasks=[("6.51","A value check at capture for the discrete Define fields, with the shape on the field description as S-C05 did","Phase state")],
       bugs=[("The baseline is stored as a sentence fragment, so Control cannot compare it with the target",
              "Phase state","01e8f8a")],
       note="\u00a763.1 B7: both are discrete because Control parses them for target-versus-actual. Recording them is Define's own job \u2014 the first link of the measurement thread."),
  dict(id="S4", rank=5, rows=[14], comps=["UI"],
       title="I can see how far through Define I am",
       ask="The progress bar reads 5 of 12 when I have done five, instead of 0 of 26 forever.",
       tasks=[("10.3","The page reads the v2 field names and counts them","UI")], bugs=[]),
  dict(id="S5", rank=6, rows=[7], comps=["Coach"],
       title="When I change an answer, my reason is kept with it",
       ask="If I correct the baseline, the record says why, not just that it changed.",
       tasks=[("6.44","Move the contradiction stop out of middleware into a node","Coach")], bugs=[]),
  dict(id="S6", rank=7, rows=[23,34], comps=["Gate","Routes","UI","Storage"],
       title="The human-in-the-loop gate: I review the gate document, approve it, and Define closes",
       ask="The run stops for me at the gate, I approve, and the case moves on with my approval recorded.",
       tasks=[("7.3","The gate pauses, and the pause survives a restart \u2014 the checkpointer holds it","Gate"),
              ("7.7","A route that answers the pause and resumes the run","Routes"),
              ("10.2","The gate screen","UI")],
       bugs=[], note="HITL. Needs a checkpointer that actually writes \u2014 row 33, proven first in S9. 10.2 is blocked on a design only you can give; until then the approval is proven through the route."),
 ]),
 dict(id="E2", title="The coach teaches the Lean Six Sigma method, not just asks questions",
      why="The difference between a coach and a chat window.",
      stories=[
  dict(id="S40", rank=1, rows=[2, 13], comps=["Coach","Storage"],
       title="Every turn answers me inside its time limit",
       ask="When I ask an open question, I get the coach's answer — never an error after forty-five seconds.",
       tasks=[("6.52","The budget starts at node entry, lookups stop blocking, and each judge sees a reply once","Coach"),
              ("6.54","The clients are built once, at startup, before any Belt waits for them","Coach"),
              ("—","6.53: a failed judgement asks the coach again — gated on the G-83 latency ruling","Coach")],
       bugs=[("The grader re-judges the same unchanged reply on each iteration, inside the executor's time budget — rows 2 and 13",
              "Coach","6.49 · trace 01a0d215 · fixed 6.52 B2"),
             ("Coherence (layer 2a) rejects a reply and never asks for a new one — row 12. Re-checking the same text stopped at 6.52 B2; a fresh reply is 6.53",
              "Coach","6.49 · 10 of 10 rejecting turns"),
             ("The executor's soft budget does not end the turn before the 45 s limit — row 2, two traces",
              "Coach","6.49 · traces 01a0d215, 01a0d28e · fixed 6.52 B1")],
       note="G-92. Both live turns on 0E5 on 2026-09-24 hit the 45 s wall: one in the grader, one in three knowledge lookups. Part A found the soft budget's clock started ~5 s late and the lookups held the event loop."),
  dict(id="S7", rank=4, rows=[3], comps=["Coach","Skills"],
       title="Every field is explained, shown with an example, asked, and confirmed",
       ask="Before asking for my team, the coach tells me what a Define team is and shows me one.",
       tasks=[("6.46","The coaching script reaches the model every turn, and the turn records it","Skills")],
       bugs=[("The coaching script was fetched zero times in four live turns",
              "Skills","5dc10ff run · fixed 6.46"),
             ("Coherence rejects the script's own Confirm step as parroting, and nothing records the degrade — G-96",
              "Coach","6.46 live turn 13:14")],
       note="Also removes the four duplicate shape lines from the skill file: the contract is authoritative. AND: once the script is in front of the model every turn, its worked examples are too \u2014 the \u00a722 guard that an example is never captured as the Belt's data becomes load-bearing, and belongs in this card."),
  dict(id="S8", rank=None, rows=[27], comps=["Coach","Skills"],
       title="For every field, I am shown a good example before I am asked",
       ask="Before I write my SIPOC, the coach shows me a finished one and says what makes it good.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.2","Coach")], bugs=[],
       note="\u00a743.2. Mostly delivered by S7's script; the check must also prove the example is never captured as data."),
  dict(id="S34", rank=None, rows=[26], comps=["Coach"],
       title="When the coach runs a calculation, I am taught what it means first",
       ask="Before I get a savings figure, I am told what it measures and what the number will mean.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.1","Coach")], bugs=[],
       note="\u00a743.1, the seven-step computation pattern. In Define it applies to calculate_expected_savings."),
  dict(id="S35", rank=None, rows=[28], comps=["Coach","UI"],
       title="I always know where I am in the session",
       ask="The coach tells me I am on step 6 of 12, and why we are there.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.3","Coach")], bugs=[],
       note="\u00a743.3, the A\u2192F flow. Stage E is empty for Define, which has no Tier 2. Pairs with S4's progress bar."),
  dict(id="S36", rank=None, rows=[29], comps=["Coach","Gate"],
       title="I can see my gate document filling in as I go",
       ask="At any point the coach can show me which of my twelve fields are done and which are missing.",
       tasks=[("\u2014","The check_gate_status tool, bound to Define","Coach")], bugs=[],
       note="\u00a743.4. Define shows one list, not two. The tool does not exist today."),
  dict(id="S37", rank=None, rows=[30], comps=["Coach"],
       title="The coach teaches in its own voice and never hands me a link",
       ask="When I ask about the method, I get an explanation, not a URL.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.5","Coach")], bugs=[],
       note="\u00a743.5. Methodology comes from rag_lookup_methodology \u2014 which is empty until S21 fills the knowledge index."),
  dict(id="S38", rank=None, rows=[31], comps=["Coach"],
       title="Weak answers are challenged, and the coach never writes my answer for me",
       ask="If I say 'costs are too high', I am asked how much and measured how. The problem statement is mine, not the coach's.",
       tasks=[("\u2014","Rubric criteria and a live-turn check for \u00a743.6","Coach")], bugs=[],
       note="\u00a743.6. 'Not doing the Belt's work' is the one the section calls most easily rationalised away."),
  dict(id="S39", rank=None, rows=[32], comps=["Coach","Skills"],
       title="I understand what my metric means, why it matters, and how to read it",
       ask="When my error rate first comes up, the coach explains what it is, why Define cares, and what a good value looks like.",
       tasks=[("\u2014","Bring Define's metric-literacy block to the full \u00a743.7 standard, plus a live-turn check","Skills")], bugs=[],
       note="\u00a743.7 is applied in full to Measure only; Define inherits it 'at its review'. It reads the registry's meaning and never invents one."),
 ]),
 dict(id="E3", title="Every capability is proven, not assumed",
      why="Ten rows almost certainly work today. None of them has a check.",
      stories=[
  dict(id="S9", rank=2, rows=[1,2,5,6,8,10,11,12,13,17,33,35], comps=["all"],
       title="Everything that already works is proven by a check",
       ask="A case opens, a turn replies, answers survive, changes are logged, uploads land, calculations and metrics are kept, coherence and grading run, required fields are checked.",
       tasks=[("6.49","Write one check per row, reading the live case; checks only, no code changes","all")],
       bugs=[]),
 ]),
 dict(id="E4", title="Quality, once Define works end to end",
      why="Real, and none of it stops a Belt closing Define.",
      stories=[
  dict(id="S10", rank=None, rows=[4], comps=["Phase state"],
       title="The coach asks for the right next field",
       ask="Field two comes only once field one is complete, not after a fixed number of turns.",
       tasks=[("6.45","A real is-this-field-complete predicate","Phase state")], bugs=[]),
  dict(id="S11", rank=None, rows=[9], comps=["Coach"],
       title="The coach can read what I upload",
       ask="If I attach a process map, the coach quotes from it.",
       tasks=[("6.43","A tool that returns an uploaded document's text","Coach")],
       bugs=[("The same evidence file is indexed twice, 22 s apart — G-97","Storage","6.46 Part A"),
             ("The evidence upload's interpretation is unavailable — G-98","Storage","6.46 Part A")]),
  dict(id="S12", rank=None, rows=[15,16], comps=["UI"],
       title="I see the coaching properly, and I am told when something fails",
       ask="Explanation, example, prompt and citations appear; a failure says what happened and stays on screen.",
       tasks=[("10.0","Render the four coaching blocks","UI"),
              ("10.4","A readable error when a turn fails","UI")], bugs=[]),
  dict(id="S13", rank=None, rows=[22], comps=["Gate"],
       title="The gate grades my document against the method",
       ask="The gate checks constraints and scores the document against the Define rubric, and can send it back.",
       tasks=[("7.1","The validator's result shape","Gate"),
              ("7.2","Constraints and the phase rubric","Gate"),
              ("7.8","The gate steps that use the grading","Gate")],
       bugs=[], note="Blocked on two things only you can give: the result-shape ruling and the Define rubric text."),
  dict(id="S14", rank=None, rows=[24], comps=["Supervisor","Storage"],
       title="Measure can read what Define decided",
       ask="When I move to Measure, it starts from my approved Define record.",
       tasks=[], bugs=[], note="Needs the graph to own its own boundary, with a version on the write — story S25. Stage 7."),
  dict(id="S31", rank=None, rows=[], comps=["UI","Routes"],
       title="I see the coach's reply as it is being written",
       ask="The answer appears word by word instead of after a long silence.",
       tasks=[("10.1","/ask/stream — server-sent events","Routes")], bugs=[]),
  dict(id="S32", rank=None, rows=[], comps=["Gate"],
       title="When I am stuck after three attempts, someone is told",
       ask="If the gate keeps sending my work back, a person is brought in rather than the loop going on.",
       tasks=[("7.5","Escalation","Gate")], bugs=[]),
 ]),
 dict(id="E5", title="The other four phases work the way Define does",
      why="The shared machinery is built; each phase needs its fields, its script and its gate. Not before Define is done.",
      stories=[
  dict(id="S15", rank=None, rows=[], comps=["Phase state","Skills","Gate"],
       title="Measure coaches its fields in order and closes its gate",
       ask="After Define, I am taken through Measure the same way, and its gate uses tiers.",
       tasks=[("6.14","The skill shape pass for the remaining phases","Skills"),
              ("7.4","Two tiers of field, and the warning verdict","Gate")], bugs=[],
       note="Measure's ordered field list (§39.2.2) has no owner yet."),
  dict(id="S16", rank=None, rows=[], comps=["Phase state","Coach"],
       title="Analyse, Improve and Control do the same",
       ask="Each phase has its own coaching, its own gate, and links back to the metrics Define set.",
       tasks=[("6.10","Analyse's multi-hop retrieval","Coach")], bugs=[],
       note="Three phase specifications and their field lists (§39.3–§39.5) have no owner yet. Nor do the cross-phase reference dicts (§63.6)."),
  dict(id="S17", rank=None, rows=[], comps=["Gate"],
       title="If I change something an earlier gate approved, what depended on it is re-checked",
       ask="Correcting my Define baseline during Measure reopens the parts that used it.",
       tasks=[("7.6","The re-approval cascade","Gate")], bugs=[]),
 ]),
 dict(id="E6", title="The system stays up, and says so when it does not",
      why="Reliability. Stage 8 of the procedure.",
      stories=[
  dict(id="S18", rank=None, rows=[], comps=["Routes","Coach","Storage"],
       title="A turn never hangs and never fails silently",
       ask="If something breaks, the turn ends cleanly, tells me, and I can carry on.",
       tasks=[("8.1","Structured errors","Routes"),("8.2","Timeouts and compensating actions","Coach"),
              ("8.3","Circuit breakers and a fallback chain","Coach"),("8.4","Level 3 cache","Coach"),
              ("8.5","Graceful shutdown","Routes"),("8.6","Context recovery","Storage")], bugs=[]),
  dict(id="S19", rank=None, rows=[], comps=["all"],
       title="Full turn telemetry in LangSmith, for every phase",
       ask="When a Belt says the coach did something odd, we can see exactly what happened in that turn.",
       tasks=[("8.0","Turn telemetry and @traceable","all")], bugs=[],
       note="The basic proof that a Define turn leaves a trace is row 35, in S9. This story is the full telemetry after Define."),
  dict(id="S20", rank=None, rows=[], comps=["Storage","Coach"],
       title="My uploads are managed, and the coach has the capacity it needs",
       ask="I can remove a file I uploaded by mistake, and the coach does not run out of model quota mid-project.",
       tasks=[("8.7","delete_blob and the upload lifecycle","Storage"),
              ("9.2","The premium deployment's quota","Coach")], bugs=[]),
 ]),
 dict(id="E7", title="The coach knows the method and the cases before mine",
      why="Two of the three search indexes are empty.",
      stories=[
  dict(id="S21", rank=None, rows=[], comps=["Storage","Coach"],
       title="The coach consults the DMAIC body of knowledge, not only its script",
       ask="When I ask why a SMART statement needs a date, the answer comes from the method, cited.",
       tasks=[("9.0","Build the knowledge index","Storage")], bugs=[]),
  dict(id="S22", rank=None, rows=[], comps=["Storage","Coach"],
       title="The coach can draw on similar past cases",
       ask="If someone ran a scrap project on a similar line, the coach can point me to what they found.",
       tasks=[("9.1","Build the case index","Storage")],
       bugs=[("Open questions search the empty case index on almost every turn — G-94, 6.55 proposed",
              "Coach","8.0 slice · trace 01a0d366")]),
 ]),
 dict(id="E8", title="The graph owns its own state",
      why="Framework conformance: the places the tree departs from what LangGraph and Azure document.",
      stories=[
  dict(id="S24", rank=None, rows=[], comps=["Storage","Supervisor"],
       title="Nothing I did is lost if the system crashes mid-turn",
       ask="If the server restarts while the coach is answering, I lose at most that one step, and the case resumes.",
       tasks=[("6.47","Durable writes inside a node; persistence loss is never silent","Storage")],
       bugs=[("§16 says the subgraph keeps its state across turns; the tree says it does not",
              "Supervisor","62d7f17")]),
  dict(id="S25", rank=None, rows=[], comps=["Supervisor","Storage"],
       title="Each fact has one writer, and a write cannot overwrite a newer one",
       ask="Two things happening at once on my case can never silently undo each other.",
       tasks=[("—","The graph owns its boundary: call the output mapper, remove the route's write, version the blob write","Supervisor")],
       bugs=[], note="The boundary finding. Required before a second writer exists, which is stage 7."),
  dict(id="S26", rank=None, rows=[], comps=["Phase state"],
       title="Accumulating state can never be silently replaced",
       ask="The conversation, the change log and the evidence only ever grow, whatever code touches them.",
       tasks=[("—","Accumulating channels carry reducers","Phase state")], bugs=[]),
 ]),
 dict(id="E9", title="The register tells the truth",
      why="Governance, from the founder's side: the documents can be trusted without re-auditing them.",
      stories=[
  dict(id="S28", rank=None, rows=[], comps=["Governance"],
       title="As the founder, every claim in the documents can be checked",
       ask="A count, a citation or a claim about the code is verified by a machine, not by me re-reading it.",
       tasks=[("6.17","The count-check","Governance"),("6.22","The middleware order-check","Governance"),
              ("6.23","The source-method check","Governance"),("6.24","The drift hook reads the documents","Governance"),
              ("6.28","Fact ownership at the commit gate","Governance"),("6.29","Search index schema ownership","Governance"),
              ("6.30","Commit claims carry a resolvable reference","Governance"),("6.32","An out-of-band landing gets its lane","Governance"),
              ("6.50","The conformance pass: the tree against the framework's documentation","Governance")],
       bugs=[("read_order() reads zero rows since the Zone column arrived at 6.37 — two copies of one regex, build_board.py and continuity_status.py, so both the step board and CONTINUITY.md show an empty vertical",
              "Governance","6.49 · plan-order check")]),
  dict(id="S29", rank=None, rows=[], comps=["Coach"],
       title="As the founder, I can see whether coaching quality is going up or down",
       ask="A fixed set of cases is run on every change and scored.",
       tasks=[("7.0","The evaluation suite","Coach")], bugs=[]),
  dict(id="S30", rank=None, rows=[], comps=["Governance"],
       title="As the founder, v1 is gone and the governance is closed",
       ask="One codebase, and a register with nothing open that nobody owns.",
       tasks=[("11.1","Delete v1","Governance"),("11.2","Governance close-out","Governance")], bugs=[]),
 ]),
]

UNSTORIED = [
 ("Project members and sign-in", "a case is opened against a free-text name; the change log and the approval already carry an actor, so identity can be added later. A future epic, not yet written."),
]

def resolve(p=None):
    """Each story's and task's status, DERIVED — never read from this file.

    `p` is `progress.progress()`'s dict (computed here when not given), so the page
    counts from the same read it rendered from. Idempotent: tasks become
    (code, title, comp, state, ref) and a second call re-derives from the first three.
    """
    if p is None:
        import progress
        p = progress.progress()
    caps = {c["row"]: c for c in p["capabilities"]}
    for ep in EPICS:
        for st in ep["stories"]:
            missing = [r for r in st["rows"] if r not in caps]
            if missing:
                raise RuntimeError("%s cites rows not in Appendix H: %s" % (st["id"], missing))
            if st["rows"]:
                st["status"] = "done" if all(caps[r]["proven"] for r in st["rows"]) else "open"
                st["ref"] = "Appendix H rows " + ", ".join(map(str, st["rows"]))
            else:
                st["status"], st["ref"] = "open", "none"
            tasks = []
            for code, title, comp, *_ in st["tasks"]:
                step = p["steps"].get(code)
                if step:
                    tasks.append((code, title, comp, step["state"], "step " + code))
                else:
                    tasks.append((code, title, comp, "none", "none"))
            st["tasks"] = tasks
    return p


def epic_of():
    """step -> (epic id, story id): the tag the waterfall puts on each step."""
    out: dict[str, tuple[str, str]] = {}
    for ep in EPICS:
        for st in ep["stories"]:
            for t in st["tasks"]:
                if t[0] != "—":
                    out.setdefault(t[0], (ep["id"], st["id"]))
    return out
