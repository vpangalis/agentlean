# Section index — GENERATED, never hand-edit

Written by `.claude/hooks/section_index.py` on every commit that touches a
document below (step 6.66). Find the section here, then read only its lines
(CLAUDE.md, Three layers). A range runs to the next heading of the same or higher level.

## `agent-improve/ARCHITECTURE.md` — 961 lines

| Lines | Heading |
|---|---|
| 1–961 | Agent Improve — Architecture |
| 20–41 |  1. Overview |
| 42–323 |  2. Architecture |
| 44–62 |   2.1 Context |
| 63–89 |   2.2 Containers |
| 90–131 |   2.3 The graph |
| 132–179 |   2.4 One coaching turn |
| 180–214 |   2.5 Checkpoints and persistence |
| 215–267 |   2.6 Human in the loop |
| 268–287 |   2.7 Start-up and deployment, as built |
| 288–323 |   2.8 The upload pipeline |
| 324–596 |  3. Components and interfaces |
| 326–372 |   3.1 Code layout |
| 373–395 |   3.2 Phase nodes |
| 396–493 |   3.3 Executor and middleware |
| 494–500 |   3.4 Models |
| 501–514 |   3.5 Retrieval |
| 515–548 |   3.6 Tools |
| 549–555 |   3.7 Skills |
| 556–568 |   3.8 Validation |
| 569–586 |   3.9 API |
| 587–596 |   3.10 UI |
| 597–926 |  4. Data models |
| 601–671 |   4.1 Shapes and notes |
| 672–926 |   4.2 Declarations |
| 674–686 |    `SupervisorState` — `core/state.py` |
| 687–716 |    `PhaseState` — `core/substate.py` |
| 717–751 |    Planner and coach schemas — `core/substate.py` |
| 752–846 |    Phase records — `phases/{phase}/schema.py` |
| 847–901 |    Search indexes — Azure AI Search |
| 902–909 |    Store namespaces — `storage/layout.py::STORE_NAMESPACES` |
| 910–926 |    Blob layout — container `agent-improve-cases` (the default of `settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS` |
| 927–941 |  5. Error handling |
| 942–953 |  6. Testing strategy |
| 954–961 |  7. Glossary |
