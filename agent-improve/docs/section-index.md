# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 945 lines

| Lines | Heading |
|---|---|
| 1–945 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–322 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–178 |   2.4 One coaching turn |
| 179–213 |   2.5 Checkpoints and persistence |
| 214–266 |   2.6 Human in the loop |
| 267–286 |   2.7 Start-up and deployment, as built |
| 287–322 |   2.8 The upload pipeline |
| 323–580 |  3. Components and interfaces |
| 325–368 |   3.1 Code layout |
| 369–391 |   3.2 Phase nodes |
| 392–486 |   3.3 Executor and middleware |
| 487–493 |   3.4 Models |
| 494–507 |   3.5 Retrieval |
| 508–532 |   3.6 Tools |
| 533–539 |   3.7 Skills |
| 540–552 |   3.8 Validation |
| 553–570 |   3.9 API |
| 571–580 |   3.10 UI |
| 581–910 |  4. Data models |
| 585–655 |   4.1 Shapes and notes |
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
| 938–945 |  7. Glossary |
