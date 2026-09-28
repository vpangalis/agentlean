# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 944 lines

| Lines | Heading |
|---|---|
| 1–944 | Agent Improve — Architecture |
| 26–45 |  1. Overview |
| 46–315 |  2. Architecture |
| 48–64 |   2.1 Context |
| 65–91 |   2.2 Containers |
| 92–125 |   2.3 The graph |
| 126–168 |   2.4 One coaching turn |
| 169–210 |   2.5 Checkpoints and persistence |
| 211–265 |   2.6 Human in the loop |
| 266–283 |   2.7 Start-up and deployment, as built |
| 284–315 |   2.8 The upload pipeline |
| 316–572 |  3. Components and interfaces |
| 318–358 |   3.1 Code layout |
| 359–378 |   3.2 Phase nodes |
| 379–482 |   3.3 Executor and middleware |
| 483–489 |   3.4 Models |
| 490–503 |   3.5 Retrieval |
| 504–527 |   3.6 Tools |
| 528–534 |   3.7 Skills |
| 535–547 |   3.8 Validation |
| 548–561 |   3.9 API |
| 562–572 |   3.10 UI |
| 573–906 |  4. Data models |
| 578–651 |   4.1 Shapes and notes |
| 652–906 |   4.2 Declarations |
| 654–666 |    `SupervisorState` — `core/state.py` |
| 667–696 |    `PhaseState` — `core/substate.py` |
| 697–731 |    Planner and coach schemas — `core/substate.py` |
| 732–826 |    Phase records — `phases/{phase}/schema.py` |
| 827–881 |    Search indexes — Azure AI Search |
| 882–889 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 890–906 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 907–921 |  5. Error handling |
| 922–933 |  6. Testing strategy |
| 934–944 |  7. Glossary |
