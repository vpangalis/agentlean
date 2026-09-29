# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 967 lines

| Lines | Heading |
|---|---|
| 1–967 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–325 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–180 |   2.4 One coaching turn |
| 181–216 |   2.5 Checkpoints and persistence |
| 217–269 |   2.6 Human in the loop |
| 270–289 |   2.7 Start-up and deployment, as built |
| 290–325 |   2.8 The upload pipeline |
| 326–599 |  3. Components and interfaces |
| 328–375 |   3.1 Code layout |
| 376–398 |   3.2 Phase nodes |
| 399–496 |   3.3 Executor and middleware |
| 497–503 |   3.4 Models |
| 504–517 |   3.5 Retrieval |
| 518–551 |   3.6 Tools |
| 552–558 |   3.7 Skills |
| 559–571 |   3.8 Validation |
| 572–589 |   3.9 API |
| 590–599 |   3.10 UI |
| 600–932 |  4. Data models |
| 604–675 |   4.1 Shapes and notes |
| 676–932 |   4.2 Declarations |
| 680–692 |    `SupervisorState` — `core/state.py` |
| 693–722 |    `PhaseState` — `core/substate.py` |
| 723–757 |    Planner and coach schemas — `core/substate.py` |
| 758–852 |    Phase records — `phases/{phase}/schema.py` |
| 853–907 |    Search indexes — Azure AI Search |
| 908–915 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 916–932 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 933–947 |  5. Error handling |
| 948–959 |  6. Testing strategy |
| 960–967 |  7. Glossary |
