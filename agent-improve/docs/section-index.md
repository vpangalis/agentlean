# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 943 lines

| Lines | Heading |
|---|---|
| 1–943 | Agent Improve — Architecture |
| 26–45 |  1. Overview |
| 46–314 |  2. Architecture |
| 48–64 |   2.1 Context |
| 65–91 |   2.2 Containers |
| 92–125 |   2.3 The graph |
| 126–168 |   2.4 One coaching turn |
| 169–210 |   2.5 Checkpoints and persistence |
| 211–264 |   2.6 Human in the loop |
| 265–282 |   2.7 Start-up and deployment, as built |
| 283–314 |   2.8 The upload pipeline |
| 315–571 |  3. Components and interfaces |
| 317–357 |   3.1 Code layout |
| 358–377 |   3.2 Phase nodes |
| 378–481 |   3.3 Executor and middleware |
| 482–488 |   3.4 Models |
| 489–502 |   3.5 Retrieval |
| 503–526 |   3.6 Tools |
| 527–533 |   3.7 Skills |
| 534–546 |   3.8 Validation |
| 547–560 |   3.9 API |
| 561–571 |   3.10 UI |
| 572–905 |  4. Data models |
| 577–650 |   4.1 Shapes and notes |
| 651–905 |   4.2 Declarations |
| 653–665 |    `SupervisorState` — `core/state.py` |
| 666–695 |    `PhaseState` — `core/substate.py` |
| 696–730 |    Planner and coach schemas — `core/substate.py` |
| 731–825 |    Phase records — `phases/{phase}/schema.py` |
| 826–880 |    Search indexes — Azure AI Search |
| 881–888 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 889–905 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 906–920 |  5. Error handling |
| 921–932 |  6. Testing strategy |
| 933–943 |  7. Glossary |
