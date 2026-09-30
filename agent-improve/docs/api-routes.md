# API routes

Generated from the code on every commit by `tools/architecture/generate_routes.py` (the pre-commit
hook, `--stage`); never edited by hand. Linked from [ARCHITECTURE.md §3.9](../ARCHITECTURE.md).

<!-- BEGIN GENERATED: api routes — tools/architecture/generate_routes.py -->

### API routes — `backend/gateway/routes.py`, generated

| Method | Path | Handler | Response | Says |
|---|---|---|---|---|
| GET | `/health` | `health` | `HealthResponse` | — |
| POST | `/summarise` | `summarise_session` | `SummariseResponse` | Generate a 2-3 sentence AI summary of a session's conversation turns. |
| POST | `/context` | `get_session_context` | `ContextResponse` | Generate a re-entry greeting based on current gate status. |
| POST | `/cases` | `create_case` | `CaseCreateResponse` | Create a new improvement case and register it. |
| POST | `/ask` | `ask` | `AskResponse` | One coaching turn, through the compiled graph. |
| GET | `/gate/review/{case_id}/{phase}` | `gate_review` | `GateReviewResponse` | The assembled gate document, shown to the Belt BEFORE approval. |
| POST | `/upload` | `upload_file` | — | §29.1's external-data channel — procedure step 6.11. |
| DELETE | `/files/{case_id}/{file_id}` | `delete_case_file` | — | Remove a file record from the case. |
| POST | `/gate/decision` | `decide_gate` | `GateDecisionResponse` | R6 — approve or reject the Define report, RESUMING the paused graph. |
| POST | `/gate` | `submit_gate` | `GateSubmitResponse` | Submit the phase for gate review — through the same compiled graph. |
| GET | `/registry` | `get_registry` | `list[RegistryEntryOut]` | Management dashboard â returns all cases from registry. |
| GET | `/cases/{case_id}` | `get_case` | — | Load full case document. Also projects every per-phase upload |

<!-- END GENERATED: api routes -->
