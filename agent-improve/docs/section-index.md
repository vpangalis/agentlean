# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 930 lines

| Lines | Heading |
|---|---|
| 1–930 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–319 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–176 |   2.4 One coaching turn |
| 177–211 |   2.5 Checkpoints and persistence |
| 212–264 |   2.6 Human in the loop |
| 265–284 |   2.7 Start-up and deployment, as built |
| 285–319 |   2.8 The upload pipeline |
| 320–565 |  3. Components and interfaces |
| 322–364 |   3.1 Code layout |
| 365–387 |   3.2 Phase nodes |
| 388–473 |   3.3 Executor and middleware |
| 474–480 |   3.4 Models |
| 481–494 |   3.5 Retrieval |
| 495–517 |   3.6 Tools |
| 518–524 |   3.7 Skills |
| 525–537 |   3.8 Validation |
| 538–555 |   3.9 API |
| 556–565 |   3.10 UI |
| 566–895 |  4. Data models |
| 570–640 |   4.1 Shapes and notes |
| 641–895 |   4.2 Declarations |
| 643–655 |    `SupervisorState` — `core/state.py` |
| 656–685 |    `PhaseState` — `core/substate.py` |
| 686–720 |    Planner and coach schemas — `core/substate.py` |
| 721–815 |    Phase records — `phases/{phase}/schema.py` |
| 816–870 |    Search indexes — Azure AI Search |
| 871–878 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 879–895 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 896–910 |  5. Error handling |
| 911–922 |  6. Testing strategy |
| 923–930 |  7. Glossary |
