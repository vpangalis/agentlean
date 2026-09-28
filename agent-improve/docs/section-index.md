# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 931 lines

| Lines | Heading |
|---|---|
| 1–931 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–320 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–177 |   2.4 One coaching turn |
| 178–212 |   2.5 Checkpoints and persistence |
| 213–265 |   2.6 Human in the loop |
| 266–285 |   2.7 Start-up and deployment, as built |
| 286–320 |   2.8 The upload pipeline |
| 321–566 |  3. Components and interfaces |
| 323–365 |   3.1 Code layout |
| 366–388 |   3.2 Phase nodes |
| 389–474 |   3.3 Executor and middleware |
| 475–481 |   3.4 Models |
| 482–495 |   3.5 Retrieval |
| 496–518 |   3.6 Tools |
| 519–525 |   3.7 Skills |
| 526–538 |   3.8 Validation |
| 539–556 |   3.9 API |
| 557–566 |   3.10 UI |
| 567–896 |  4. Data models |
| 571–641 |   4.1 Shapes and notes |
| 642–896 |   4.2 Declarations |
| 644–656 |    `SupervisorState` — `core/state.py` |
| 657–686 |    `PhaseState` — `core/substate.py` |
| 687–721 |    Planner and coach schemas — `core/substate.py` |
| 722–816 |    Phase records — `phases/{phase}/schema.py` |
| 817–871 |    Search indexes — Azure AI Search |
| 872–879 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 880–896 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 897–911 |  5. Error handling |
| 912–923 |  6. Testing strategy |
| 924–931 |  7. Glossary |
