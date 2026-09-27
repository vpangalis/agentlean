# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 863 lines

| Lines | Heading |
|---|---|
| 1–863 | Agent Improve — Architecture |
| 26–45 |  1. Overview |
| 46–251 |  2. Architecture |
| 48–64 |   2.1 Context |
| 65–91 |   2.2 Containers |
| 92–121 |   2.3 The graph |
| 122–154 |   2.4 One coaching turn |
| 155–196 |   2.5 Checkpoints and persistence |
| 197–251 |   2.6 Human in the loop |
| 252–491 |  3. Components and interfaces |
| 254–294 |   3.1 Code layout |
| 295–304 |   3.2 Phase nodes |
| 305–408 |   3.3 Executor and middleware |
| 409–415 |   3.4 Models |
| 416–429 |   3.5 Retrieval |
| 430–446 |   3.6 Tools |
| 447–453 |   3.7 Skills |
| 454–466 |   3.8 Validation |
| 467–480 |   3.9 API |
| 481–491 |   3.10 UI |
| 492–825 |  4. Data models |
| 497–570 |   4.1 Shapes and notes |
| 571–825 |   4.2 Declarations |
| 573–585 |    `SupervisorState` — `core/state.py` |
| 586–615 |    `PhaseState` — `core/substate.py` |
| 616–650 |    Planner and coach schemas — `core/substate.py` |
| 651–745 |    Phase records — `phases/{phase}/schema.py` |
| 746–800 |    Search indexes — Azure AI Search |
| 801–808 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 809–825 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 826–840 |  5. Error handling |
| 841–852 |  6. Testing strategy |
| 853–863 |  7. Glossary |
