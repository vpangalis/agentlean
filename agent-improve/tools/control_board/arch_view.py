"""
The architecture view — containers, their features, conditions and exceptions,
down to the nodes of a phase. Status is the audit's (tree evidence at 208e4a7)
and every open item names the card that closes it, so this page and the board
agree by construction.

b = built · p = a stand-in that says so · a = absent · u = not knowable from code
"""

LEVEL1 = dict(
  title="Main graph — the supervisor",
  role="orchestrator",
  sub="One per case. Routes between phases and nothing else.",
  what=[
    ("b", "Not an agent. No model call anywhere in it."),
    ("b", "Static edges in fixed DMAIC order; it chooses only whether to advance."),
    ("b", "One thread per project — the case id is the thread id."),
  ],
  state=dict(
    title="SupervisorState — seven fields, and an eighth needs a formal amendment",
    fields=[
      ("messages", "the Belt↔system conversation, append-only"),
      ("history", "human-readable breadcrumbs; no control logic reads it"),
      ("case_id", "the project. Also the thread id and the first store segment"),
      ("phase_index", "how far along — derived, written by the output mapper only"),
      ("current_phase", "which phase — derived, same single writer"),
      ("gate_passed", "which gates are approved. The authoritative routing signal"),
      ("final_output", "the assembled deliverable; None until Control's gate passes"),
    ]),
  conditions=[
    "Absence of a key in gate_passed means 'not yet reached', never an error.",
    "phase_index and current_phase have exactly ONE writer. A second writer would turn a derived field into a competing source of truth.",
    "The re-approval cascade sets a phase back to False rather than deleting its key.",
  ],
  exceptions=[
    ("p", "Phase advancement is driven by the old HTTP route today, not by the graph. The graph's output mapper is not called — by ruling, until stage 7.", "stage 7"),
    ("a", "Captured fields, gate documents and phase-internal data MUST NOT appear here. They live in the phase state and the store.", ""),
  ],
)

LEVEL2 = dict(
  title="Phase subgraph — one per DMAIC phase",
  role="the phase",
  sub="Five phases, ONE class. There is no DefineState, MeasureState or any other — "
      "they were specified thirteen times, never built, and ruled out on 11 September.",
  what=[
    ("b", "A compiled state graph, invoked inside a node of the parent."),
    ("b", "Compiled with NO checkpointer and NO store of its own — the child inherits the parent's saver."),
    ("b", "Invoked directly with the inherited config, never a fresh one, and never from inside a tool."),
    ("p", "Because it has no checkpointer of its own, its state does NOT persist across turns. The case record carries it."),
  ],
  state=dict(
    title="PhaseState — twenty-three fields, shared by all five phases",
    fields=[
      ("artifacts", "the captured fields, computation_results, phase_metrics"),
      ("field_log", "every field change, dated, with its prior value — landed 22 Sep"),
      ("field_index", "which field is being coached"),
      ("coaching_plan", "what this turn is meant to do"),
      ("messages", "the phase conversation"),
      ("asks", "outstanding requests for evidence, keyed on role"),
      ("uploads", "what the Belt attached"),
      ("phase_context", "prior phases' committed values, loaded before the model runs"),
      ("citations", "the evidence trail"),
      ("hop_results / synthesis_output", "multi-hop retrieval, populated in Analyse"),
      ("gate_attempts", "the shared counter, cap 3"),
      ("validator_feedback", "accumulated across layers, never per layer"),
      ("rejection_feedback", "the Belt's own reason for rejecting a gate — a third actor"),
      ("turn_count", "…and the rest"),
    ]),
  conditions=[
    "The parent and the child share no keys. That is why the mapper pattern is forced, and why concurrent-update errors have never occurred.",
    "Field names, counts and types are owned by one module and are not restated in the architecture.",
    "At the moment the child starts writing back to the parent, any shared key needs a reducer on the parent side.",
  ],
  exceptions=[
    ("b", "The state is seeded from the case record and folded back by merge — this was replacing, and was fixed on 22 September.", "6.33 done"),
  ],
)

NODES = [
 dict(name="Phase planner", agent=False, status="p", step="6.45",
   one="Decides which field to coach next, and when the phase is ready for its gate.",
   what=["A model call, but not an agent — it has no tools.",
         "Owns the field/gate decision; the executor decides no strategy.",
         "Returns a routing command; it is one of the three decision points."],
   cond=["Reads field_index against the ordered field list.",
         "Three exits: coach the current field, coach the next, or go to the gate."],
   exc=[("p","The real predicate — 'is the current field complete?' — does not exist. A turn counter stands in, and says so in its own comment.","6.45")]),

 dict(name="Phase executor — the coach", agent=True, status="b", step="",
   one="THIS is the agent. Everything else in the phase is a plain function or a pause.",
   what=["Built with the framework's agent constructor.",
         "Has the model inside it, the phase's tools bound to it, and eight middleware positions wrapped around it.",
         "Decides which tool to call and when.",
         "Returns the Belt-facing message plus the fields it captured."],
   cond=["Runs one coaching turn. It executes the plan; it does not make one.",
         "Its response carries eight declared fields — message, explanation, example, prompt, progress, captured fields, citations, contradiction flag."],
   exc=[("p","Four of those eight reach the browser and are not rendered.","10.0"),
        ("a","The response has no field for the Belt's REASON for a change, so the change log's reason column cannot be filled.","6.44")]),

 dict(name="Validation stack", agent=False, status="p", step="7.1 · 7.2",
   one="Four layers, one shared retry cap of three, accumulated feedback.",
   what=["Not an agent. Deterministic checks and model-graded checks, in cheapest-first order.",
         "Runs once, at the gate boundary — except layer 2a, which is middleware and runs every turn."],
   cond=["Each layer fires only if the previous passes.",
         "The counter and the feedback live on the phase state, never in route scope, never per layer.",
         "Never downgrade the coherence or constraint checks to keyword checks."],
   exc=[("p","Layer 2b runs, but only at the gate, and reads the store the old write path filled.","7.1"),
        ("a","Layers 2c and 2d do not exist. 2d is the reader the design means when it says the grader scans the computation results.","7.2")]),

 dict(name="Gate review", agent=False, status="p", step="7.3",
   one="Where the phase stops and hands control back to the Belt.",
   what=["Not an agent. No model call. Builds the review payload and pauses.",
         "The prebuilt approval middleware is banned here — two confirmed bugs would silently discard a Belt's correction."],
   cond=["It routes nothing. It presents the validated fields and stops.",
         "A pause needs a live checkpointer, and resuming re-runs this node from its first line — so it must write nothing."],
   exc=[("p","It logs and passes straight through. There is no pause in production code anywhere.","7.3"),
        ("a","And no route that could answer one. An interrupt with no resume parks the case forever, which is why it was removed rather than left firing.","7.3 · 7.7")]),

 dict(name="Gate apply", agent=False, status="p", step="6.42",
   one="Writes the gate document and branches on your answer.",
   what=["Not an agent. No model call — schema validation over the captured fields.",
         "Two invariants run BEFORE the document is built, and both raise: every schema field must be referenced, and the metric entry must equal its mirrored scalars."],
   cond=["Approve ends the phase; reject returns to the planner carrying the Belt's reason.",
         "Because resume re-runs the node, this write must be safe to perform twice."],
   exc=[("p","It applies nothing, by design, until the gate card is built \u2014 the route does the write.","7.3"),
        ("b","The route's write now uses the same assembly as the preview and merges rather than replaces \u2014 fixed at 90948de.","")]),
]

MIDDLEWARE = [
 (1,"State injection","b","Prior-phase committed values reach the model each turn.",""),
 (2,"Skills","p","Offers a catalogue; the full coaching script arrives only if the model asks for it, and nothing records whether it did.","6.46"),
 (3,"Summarising","b","Long conversations compact.",""),
 (4,"Model retry","b","A flaked model call retries twice.",""),
 (5,"Tool retry","b","A failed retrieval retries.",""),
 (6,"Coaching grader","b","Grades the coach's process against the coaching rubric, every turn. Never reads artifacts — by design.",""),
 (7,"Coherence","b","Catches gibberish, vague non-answers and self-contradiction, every turn. Silent retry, max two.",""),
 (8,"Contradiction","p","Ships inert — the call is removed, the import kept so restoring it is one line. Detection is correct and cheap; the STOP belongs in a node.","6.44"),
]

VALIDATION = [
 ("2a","Coherence","b","Every turn","Lightweight model call. It is middleware, not part of the node.",""),
 ("2b","Field presence","p","Gate only","Deterministic, free, runs first. Its return shape is undefined — a founder decision.","7.1"),
 ("2c","Constraints","a","Gate + key moments","Asks whether a decision addresses budget, timeline, risk and measurement. Deliberately a model call, never a keyword check.","7.2"),
 ("2d","Quality rubric","a","Gate, last","Grades the finished gate document against that phase's rubric. The five rubrics have coverage lists and no text.","7.2"),
]

TOOLS = dict(
 bound=[("rag_lookup_methodology","b"),("rag_lookup_evidence","b"),("rag_lookup_case_history","b"),
        ("propose_template","b"),("propose_diagram","b"),("load_evidence_series","b"),
        ("calculate_expected_savings","b")],
 absent=[("check_gate_status","the live gate preview cannot work without it","7.1"),
         ("request_human_approval","the universal set is six, not the ratified eight",""),
         ("read_artefact","the coach is told a document exists and cannot read its text","6.43")],
)

STORES = [
 ("Case record","b","cases/{id}.json — the permanent record: captured fields, the change log, citations, uploads, gate documents.",
  "Read whole at the start of a turn, written whole at the end. One writer today; a second arrives at stage 7 and needs either a handover or a version check.",""),
 ("Checkpoints","b","checkpoints/{case}/… — the whole graph state after every node, conversation included.",
  "Written constantly, read only to continue a thread. Never queried, never rolled back to. A pause would depend on it.",""),
 ("Evidence index","b","Uploads, chunked, twelve fields. Artefacts are never indexed, by ruling.","",""),
 ("Knowledge index","a","The DMAIC corpus. Schema exists; nothing ingested — so the coach recites what was copied into its script rather than consulting the book.","","9.0"),
 ("Case index","a","Prior cases. A field rename is pending.","","9.1"),
]

PHASES = [
 ("Define",  12, 12, "b","complete — all twelve fields have explain · show · ask · confirm", "ratified · Option A, no tiers"),
 ("Measure", 10,  7, "p","exists; the shape pass is blocked", "ratified 26 Aug · tiered"),
 ("Analyse",  9,  4, "p","exists; the shape pass is blocked", "stubbed — field list blocked on the mappers and gate assembly"),
 ("Improve",  9,  4, "p","exists; the shape pass is blocked", "stubbed — same two blockers"),
 ("Control", 12,  3, "p","exists; the shape pass is blocked", "stubbed — same two blockers"),
]
