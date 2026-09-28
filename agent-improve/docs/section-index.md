# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 947 lines

| Lines | Heading |
|---|---|
| 1–947 | Agent Improve — Architecture |
| 26–45 |  1. Overview |
| 46–316 |  2. Architecture |
| 48–64 |   2.1 Context |
| 65–91 |   2.2 Containers |
| 92–126 |   2.3 The graph |
| 127–169 |   2.4 One coaching turn |
| 170–211 |   2.5 Checkpoints and persistence |
| 212–266 |   2.6 Human in the loop |
| 267–284 |   2.7 Start-up and deployment, as built |
| 285–316 |   2.8 The upload pipeline |
| 317–575 |  3. Components and interfaces |
| 319–361 |   3.1 Code layout |
| 362–381 |   3.2 Phase nodes |
| 382–485 |   3.3 Executor and middleware |
| 486–492 |   3.4 Models |
| 493–506 |   3.5 Retrieval |
| 507–530 |   3.6 Tools |
| 531–537 |   3.7 Skills |
| 538–550 |   3.8 Validation |
| 551–564 |   3.9 API |
| 565–575 |   3.10 UI |
| 576–909 |  4. Data models |
| 581–654 |   4.1 Shapes and notes |
| 655–909 |   4.2 Declarations |
| 657–669 |    `SupervisorState` — `core/state.py` |
| 670–699 |    `PhaseState` — `core/substate.py` |
| 700–734 |    Planner and coach schemas — `core/substate.py` |
| 735–829 |    Phase records — `phases/{phase}/schema.py` |
| 830–884 |    Search indexes — Azure AI Search |
| 885–892 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 893–909 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 910–924 |  5. Error handling |
| 925–936 |  6. Testing strategy |
| 937–947 |  7. Glossary |
