# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 958 lines

| Lines | Heading |
|---|---|
| 1–958 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–323 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–179 |   2.4 One coaching turn |
| 180–214 |   2.5 Checkpoints and persistence |
| 215–267 |   2.6 Human in the loop |
| 268–287 |   2.7 Start-up and deployment, as built |
| 288–323 |   2.8 The upload pipeline |
| 324–593 |  3. Components and interfaces |
| 326–371 |   3.1 Code layout |
| 372–394 |   3.2 Phase nodes |
| 395–492 |   3.3 Executor and middleware |
| 493–499 |   3.4 Models |
| 500–513 |   3.5 Retrieval |
| 514–545 |   3.6 Tools |
| 546–552 |   3.7 Skills |
| 553–565 |   3.8 Validation |
| 566–583 |   3.9 API |
| 584–593 |   3.10 UI |
| 594–923 |  4. Data models |
| 598–668 |   4.1 Shapes and notes |
| 669–923 |   4.2 Declarations |
| 671–683 |    `SupervisorState` — `core/state.py` |
| 684–713 |    `PhaseState` — `core/substate.py` |
| 714–748 |    Planner and coach schemas — `core/substate.py` |
| 749–843 |    Phase records — `phases/{phase}/schema.py` |
| 844–898 |    Search indexes — Azure AI Search |
| 899–906 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 907–923 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 924–938 |  5. Error handling |
| 939–950 |  6. Testing strategy |
| 951–958 |  7. Glossary |
