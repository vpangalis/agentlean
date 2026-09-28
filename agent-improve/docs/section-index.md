# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 954 lines

| Lines | Heading |
|---|---|
| 1–954 | Agent Improve — Architecture |
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
| 324–589 |  3. Components and interfaces |
| 326–370 |   3.1 Code layout |
| 371–393 |   3.2 Phase nodes |
| 394–488 |   3.3 Executor and middleware |
| 489–495 |   3.4 Models |
| 496–509 |   3.5 Retrieval |
| 510–541 |   3.6 Tools |
| 542–548 |   3.7 Skills |
| 549–561 |   3.8 Validation |
| 562–579 |   3.9 API |
| 580–589 |   3.10 UI |
| 590–919 |  4. Data models |
| 594–664 |   4.1 Shapes and notes |
| 665–919 |   4.2 Declarations |
| 667–679 |    `SupervisorState` — `core/state.py` |
| 680–709 |    `PhaseState` — `core/substate.py` |
| 710–744 |    Planner and coach schemas — `core/substate.py` |
| 745–839 |    Phase records — `phases/{phase}/schema.py` |
| 840–894 |    Search indexes — Azure AI Search |
| 895–902 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 903–919 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 920–934 |  5. Error handling |
| 935–946 |  6. Testing strategy |
| 947–954 |  7. Glossary |
