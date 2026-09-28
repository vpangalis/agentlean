# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 968 lines

| Lines | Heading |
|---|---|
| 1–968 | Agent Improve — Architecture |
| 26–47 |  1. Overview |
| 48–332 |  2. Architecture |
| 50–68 |   2.1 Context |
| 69–95 |   2.2 Containers |
| 96–140 |   2.3 The graph |
| 141–185 |   2.4 One coaching turn |
| 186–227 |   2.5 Checkpoints and persistence |
| 228–282 |   2.6 Human in the loop |
| 283–300 |   2.7 Start-up and deployment, as built |
| 301–332 |   2.8 The upload pipeline |
| 333–596 |  3. Components and interfaces |
| 335–377 |   3.1 Code layout |
| 378–400 |   3.2 Phase nodes |
| 401–504 |   3.3 Executor and middleware |
| 505–511 |   3.4 Models |
| 512–525 |   3.5 Retrieval |
| 526–549 |   3.6 Tools |
| 550–556 |   3.7 Skills |
| 557–569 |   3.8 Validation |
| 570–585 |   3.9 API |
| 586–596 |   3.10 UI |
| 597–930 |  4. Data models |
| 602–675 |   4.1 Shapes and notes |
| 676–930 |   4.2 Declarations |
| 678–690 |    `SupervisorState` — `core/state.py` |
| 691–720 |    `PhaseState` — `core/substate.py` |
| 721–755 |    Planner and coach schemas — `core/substate.py` |
| 756–850 |    Phase records — `phases/{phase}/schema.py` |
| 851–905 |    Search indexes — Azure AI Search |
| 906–913 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 914–930 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 931–945 |  5. Error handling |
| 946–957 |  6. Testing strategy |
| 958–968 |  7. Glossary |
