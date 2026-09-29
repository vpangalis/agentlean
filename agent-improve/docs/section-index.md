# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 965 lines

| Lines | Heading |
|---|---|
| 1–965 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–324 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–179 |   2.4 One coaching turn |
| 180–215 |   2.5 Checkpoints and persistence |
| 216–268 |   2.6 Human in the loop |
| 269–288 |   2.7 Start-up and deployment, as built |
| 289–324 |   2.8 The upload pipeline |
| 325–598 |  3. Components and interfaces |
| 327–374 |   3.1 Code layout |
| 375–397 |   3.2 Phase nodes |
| 398–495 |   3.3 Executor and middleware |
| 496–502 |   3.4 Models |
| 503–516 |   3.5 Retrieval |
| 517–550 |   3.6 Tools |
| 551–557 |   3.7 Skills |
| 558–570 |   3.8 Validation |
| 571–588 |   3.9 API |
| 589–598 |   3.10 UI |
| 599–930 |  4. Data models |
| 603–673 |   4.1 Shapes and notes |
| 674–930 |   4.2 Declarations |
| 678–690 |    `SupervisorState` — `core/state.py` |
| 691–720 |    `PhaseState` — `core/substate.py` |
| 721–755 |    Planner and coach schemas — `core/substate.py` |
| 756–850 |    Phase records — `phases/{phase}/schema.py` |
| 851–905 |    Search indexes — Azure AI Search |
| 906–913 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 914–930 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 931–945 |  5. Error handling |
| 946–957 |  6. Testing strategy |
| 958–965 |  7. Glossary |
