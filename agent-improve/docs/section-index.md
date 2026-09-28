# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 960 lines

| Lines | Heading |
|---|---|
| 1–960 | Agent Improve — Architecture |
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
| 324–595 |  3. Components and interfaces |
| 326–371 |   3.1 Code layout |
| 372–394 |   3.2 Phase nodes |
| 395–492 |   3.3 Executor and middleware |
| 493–499 |   3.4 Models |
| 500–513 |   3.5 Retrieval |
| 514–547 |   3.6 Tools |
| 548–554 |   3.7 Skills |
| 555–567 |   3.8 Validation |
| 568–585 |   3.9 API |
| 586–595 |   3.10 UI |
| 596–925 |  4. Data models |
| 600–670 |   4.1 Shapes and notes |
| 671–925 |   4.2 Declarations |
| 673–685 |    `SupervisorState` — `core/state.py` |
| 686–715 |    `PhaseState` — `core/substate.py` |
| 716–750 |    Planner and coach schemas — `core/substate.py` |
| 751–845 |    Phase records — `phases/{phase}/schema.py` |
| 846–900 |    Search indexes — Azure AI Search |
| 901–908 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 909–925 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 926–940 |  5. Error handling |
| 941–952 |  6. Testing strategy |
| 953–960 |  7. Glossary |
