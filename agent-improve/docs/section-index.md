# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 969 lines

| Lines | Heading |
|---|---|
| 1–969 | Agent Improve — Architecture |
| 26–47 |  1. Overview |
| 48–332 |  2. Architecture |
| 50–68 |   2.1 Context |
| 69–95 |   2.2 Containers |
| 96–140 |   2.3 The graph |
| 141–185 |   2.4 One coaching turn |
| 186–222 |   2.5 Checkpoints and persistence |
| 223–277 |   2.6 Human in the loop |
| 278–297 |   2.7 Start-up and deployment, as built |
| 298–332 |   2.8 The upload pipeline |
| 333–597 |  3. Components and interfaces |
| 335–377 |   3.1 Code layout |
| 378–400 |   3.2 Phase nodes |
| 401–503 |   3.3 Executor and middleware |
| 504–510 |   3.4 Models |
| 511–524 |   3.5 Retrieval |
| 525–548 |   3.6 Tools |
| 549–555 |   3.7 Skills |
| 556–568 |   3.8 Validation |
| 569–586 |   3.9 API |
| 587–597 |   3.10 UI |
| 598–931 |  4. Data models |
| 603–676 |   4.1 Shapes and notes |
| 677–931 |   4.2 Declarations |
| 679–691 |    `SupervisorState` — `core/state.py` |
| 692–721 |    `PhaseState` — `core/substate.py` |
| 722–756 |    Planner and coach schemas — `core/substate.py` |
| 757–851 |    Phase records — `phases/{phase}/schema.py` |
| 852–906 |    Search indexes — Azure AI Search |
| 907–914 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 915–931 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 932–946 |  5. Error handling |
| 947–958 |  6. Testing strategy |
| 959–969 |  7. Glossary |
