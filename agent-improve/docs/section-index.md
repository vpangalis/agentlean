# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 968 lines

| Lines | Heading |
|---|---|
| 1–968 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–326 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–181 |   2.4 One coaching turn |
| 182–217 |   2.5 Checkpoints and persistence |
| 218–270 |   2.6 Human in the loop |
| 271–290 |   2.7 Start-up and deployment, as built |
| 291–326 |   2.8 The upload pipeline |
| 327–600 |  3. Components and interfaces |
| 329–376 |   3.1 Code layout |
| 377–399 |   3.2 Phase nodes |
| 400–497 |   3.3 Executor and middleware |
| 498–504 |   3.4 Models |
| 505–518 |   3.5 Retrieval |
| 519–552 |   3.6 Tools |
| 553–559 |   3.7 Skills |
| 560–572 |   3.8 Validation |
| 573–590 |   3.9 API |
| 591–600 |   3.10 UI |
| 601–933 |  4. Data models |
| 605–676 |   4.1 Shapes and notes |
| 677–933 |   4.2 Declarations |
| 681–693 |    `SupervisorState` — `core/state.py` |
| 694–723 |    `PhaseState` — `core/substate.py` |
| 724–758 |    Planner and coach schemas — `core/substate.py` |
| 759–853 |    Phase records — `phases/{phase}/schema.py` |
| 854–908 |    Search indexes — Azure AI Search |
| 909–916 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 917–933 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 934–948 |  5. Error handling |
| 949–960 |  6. Testing strategy |
| 961–968 |  7. Glossary |
