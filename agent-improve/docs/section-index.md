# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 949 lines

| Lines | Heading |
|---|---|
| 1–949 | Agent Improve — Architecture |
| 26–45 |  1. Overview |
| 46–320 |  2. Architecture |
| 48–64 |   2.1 Context |
| 65–91 |   2.2 Containers |
| 92–129 |   2.3 The graph |
| 130–172 |   2.4 One coaching turn |
| 173–214 |   2.5 Checkpoints and persistence |
| 215–268 |   2.6 Human in the loop |
| 269–288 |   2.7 Start-up and deployment, as built |
| 289–320 |   2.8 The upload pipeline |
| 321–577 |  3. Components and interfaces |
| 323–363 |   3.1 Code layout |
| 364–383 |   3.2 Phase nodes |
| 384–487 |   3.3 Executor and middleware |
| 488–494 |   3.4 Models |
| 495–508 |   3.5 Retrieval |
| 509–532 |   3.6 Tools |
| 533–539 |   3.7 Skills |
| 540–552 |   3.8 Validation |
| 553–566 |   3.9 API |
| 567–577 |   3.10 UI |
| 578–911 |  4. Data models |
| 583–656 |   4.1 Shapes and notes |
| 657–911 |   4.2 Declarations |
| 659–671 |    `SupervisorState` — `core/state.py` |
| 672–701 |    `PhaseState` — `core/substate.py` |
| 702–736 |    Planner and coach schemas — `core/substate.py` |
| 737–831 |    Phase records — `phases/{phase}/schema.py` |
| 832–886 |    Search indexes — Azure AI Search |
| 887–894 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 895–911 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 912–926 |  5. Error handling |
| 927–938 |  6. Testing strategy |
| 939–949 |  7. Glossary |
