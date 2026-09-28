# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 943 lines

| Lines | Heading |
|---|---|
| 1–943 | Agent Improve — Architecture |
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
| 323–578 |  3. Components and interfaces |
| 325–368 |   3.1 Code layout |
| 369–391 |   3.2 Phase nodes |
| 392–486 |   3.3 Executor and middleware |
| 487–493 |   3.4 Models |
| 494–507 |   3.5 Retrieval |
| 508–530 |   3.6 Tools |
| 531–537 |   3.7 Skills |
| 538–550 |   3.8 Validation |
| 551–568 |   3.9 API |
| 569–578 |   3.10 UI |
| 579–908 |  4. Data models |
| 583–653 |   4.1 Shapes and notes |
| 654–908 |   4.2 Declarations |
| 656–668 |    `SupervisorState` — `core/state.py` |
| 669–698 |    `PhaseState` — `core/substate.py` |
| 699–733 |    Planner and coach schemas — `core/substate.py` |
| 734–828 |    Phase records — `phases/{phase}/schema.py` |
| 829–883 |    Search indexes — Azure AI Search |
| 884–891 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 892–908 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 909–923 |  5. Error handling |
| 924–935 |  6. Testing strategy |
| 936–943 |  7. Glossary |
