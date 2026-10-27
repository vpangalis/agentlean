# Post-Define list

Work found while Define's scope is frozen (`.claude/rules/planning.md`, founder 2026-10-22) that needs a new feature,
a ruling or the founder's own text: listed here, not built, until Define is done. A feature on this list carries
`track: "post_define"` in `docs/define_features.json` — it does not count toward Define and is not ranked.

| Item | Waits for | Placed |
|---|---|---|
| DEF-107 — the Belt picks any unconfirmed element whose prerequisites are confirmed (W4) | W4's open decision 1 (which prerequisites each element has — the proposal in business.md's open-decisions table) and the decision record W4 asks for (the chosen element becomes a planner input; the move stays decided in code) | Founder ruling 2026-10-22 afternoon, item 5 |
| The "Team overview" texts of the five phases (W1, DEF-106 merged into DEF-214) | The founder's texts, one "Team overview" section per phase skill file; until then the Define overview is built from the skill's opening and section F (DEF-214) | Founder ruling 2026-10-22 afternoon, item 2 |
| DEF-059 — the coach's reply appears as it is written (server-sent events); a dropped client abandons the turn (R1) | ADR-0097 (PROPOSED: steps through LangGraph's custom stream, a streamed variant of POST /ask) — its ruling after the stated verification | Founder ruling 2026-10-22 evening, item 3 |
| DEF-213's plain-words steps while a turn runs (W12) — the visible "working…" indicator is built now; the steps wait | ADR-0097, as above | Founder ruling 2026-10-22 evening, item 3 |
| DEF-111 — thumbs up/down and a comment on every reply, stored against its trace (W14) | A storage decision: LangSmith's feedback API, a Store namespace, or both (a reply carries no trace id today) | Founder ruling 2026-10-22 evening, item 4 |
| Coach charter and decision-trail intake (R21; R19 and W8 amendments; three audit requirements drafted as T95–T97, which clash with the repo's T95 and T97 and must be renumbered). Source: the founder's parked intake, deferred 2026-09-30 until the refactor is complete. | The founder's intake, once the refactor is complete; the queued step that read FUTURE_security_requirements.md is dropped | Founder ruling 2026-10-22 evening, item 6 |
| The semantic ranker on the methodology search (ADR-0060 decision 2; the switch AZURE_SEARCH_KNOWLEDGE_SEMANTIC_CONFIG, built off in 2171794; the index carries the configuration `improve-knowledge-semantic`) | An eval with it on that makes no task worse — on 2026-10-24 it took E20 from 2 of 3 to 0 of 3 (evals_20261024T201512 against …T203122) | Founder ruling 2026-10-27, item 8 |
| The coach's per-turn state and move placed after the conversation, so the conversation's prefix is cached too (about 3,000 tokens a call; ADR-0111 D2 left the order static · per element · per turn · task, with the conversation last) | The order changed in the coach's input and a run-through measuring the cache by role | Founder review 2026-10-27 (cached tokens) |
| The testing ADR drafted on 2026-10-20 — the D7 for escape classes path_test, join and assumption (defect loop R-B) | The founder's draft: it is not in the repository; until it is ruled, `docs/defects.json` escape_controls names the controls in place | Founder ruling 2026-10-23 afternoon, item 1d |
