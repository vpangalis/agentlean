# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 948 lines

| Lines | Heading |
|---|---|
| 1–948 | Agent Improve — Architecture |
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
| 321–576 |  3. Components and interfaces |
| 323–363 |   3.1 Code layout |
| 364–383 |   3.2 Phase nodes |
| 384–487 |   3.3 Executor and middleware |
| 488–494 |   3.4 Models |
| 495–508 |   3.5 Retrieval |
| 509–531 |   3.6 Tools |
| 532–538 |   3.7 Skills |
| 539–551 |   3.8 Validation |
| 552–565 |   3.9 API |
| 566–576 |   3.10 UI |
| 577–910 |  4. Data models |
| 582–655 |   4.1 Shapes and notes |
| 656–910 |   4.2 Declarations |
| 658–670 |    `SupervisorState` — `core/state.py` |
| 671–700 |    `PhaseState` — `core/substate.py` |
| 701–735 |    Planner and coach schemas — `core/substate.py` |
| 736–830 |    Phase records — `phases/{phase}/schema.py` |
| 831–885 |    Search indexes — Azure AI Search |
| 886–893 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 894–910 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 911–925 |  5. Error handling |
| 926–937 |  6. Testing strategy |
| 938–948 |  7. Glossary |
