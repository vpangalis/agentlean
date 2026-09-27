# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 941 lines

| Lines | Heading |
|---|---|
| 1–941 | Agent Improve — Architecture |
| 26–45 |  1. Overview |
| 46–313 |  2. Architecture |
| 48–64 |   2.1 Context |
| 65–91 |   2.2 Containers |
| 92–122 |   2.3 The graph |
| 123–165 |   2.4 One coaching turn |
| 166–207 |   2.5 Checkpoints and persistence |
| 208–261 |   2.6 Human in the loop |
| 262–281 |   2.7 Start-up and deployment, as built |
| 282–313 |   2.8 The upload pipeline |
| 314–569 |  3. Components and interfaces |
| 316–356 |   3.1 Code layout |
| 357–376 |   3.2 Phase nodes |
| 377–480 |   3.3 Executor and middleware |
| 481–487 |   3.4 Models |
| 488–501 |   3.5 Retrieval |
| 502–524 |   3.6 Tools |
| 525–531 |   3.7 Skills |
| 532–544 |   3.8 Validation |
| 545–558 |   3.9 API |
| 559–569 |   3.10 UI |
| 570–903 |  4. Data models |
| 575–648 |   4.1 Shapes and notes |
| 649–903 |   4.2 Declarations |
| 651–663 |    `SupervisorState` — `core/state.py` |
| 664–693 |    `PhaseState` — `core/substate.py` |
| 694–728 |    Planner and coach schemas — `core/substate.py` |
| 729–823 |    Phase records — `phases/{phase}/schema.py` |
| 824–878 |    Search indexes — Azure AI Search |
| 879–886 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 887–903 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 904–918 |  5. Error handling |
| 919–930 |  6. Testing strategy |
| 931–941 |  7. Glossary |
