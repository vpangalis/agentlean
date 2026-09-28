# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 937 lines

| Lines | Heading |
|---|---|
| 1–937 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–321 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–178 |   2.4 One coaching turn |
| 179–213 |   2.5 Checkpoints and persistence |
| 214–266 |   2.6 Human in the loop |
| 267–286 |   2.7 Start-up and deployment, as built |
| 287–321 |   2.8 The upload pipeline |
| 322–572 |  3. Components and interfaces |
| 324–366 |   3.1 Code layout |
| 367–389 |   3.2 Phase nodes |
| 390–480 |   3.3 Executor and middleware |
| 481–487 |   3.4 Models |
| 488–501 |   3.5 Retrieval |
| 502–524 |   3.6 Tools |
| 525–531 |   3.7 Skills |
| 532–544 |   3.8 Validation |
| 545–562 |   3.9 API |
| 563–572 |   3.10 UI |
| 573–902 |  4. Data models |
| 577–647 |   4.1 Shapes and notes |
| 648–902 |   4.2 Declarations |
| 650–662 |    `SupervisorState` — `core/state.py` |
| 663–692 |    `PhaseState` — `core/substate.py` |
| 693–727 |    Planner and coach schemas — `core/substate.py` |
| 728–822 |    Phase records — `phases/{phase}/schema.py` |
| 823–877 |    Search indexes — Azure AI Search |
| 878–885 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 886–902 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 903–917 |  5. Error handling |
| 918–929 |  6. Testing strategy |
| 930–937 |  7. Glossary |
