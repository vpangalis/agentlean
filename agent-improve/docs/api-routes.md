# API routes

Generated from the code on every commit by `tools/architecture/generate_routes.py` (the pre-commit
hook, `--stage`); never edited by hand. Linked from [ARCHITECTURE.md §3.9](../ARCHITECTURE.md).

<!-- BEGIN GENERATED: api routes — tools/architecture/generate_routes.py -->

### API routes — `backend/gateway/routes.py`, generated

| Method | Path | Handler | Response | Says |
|---|---|---|---|---|
| GET | `/health` | `health` | `HealthResponse` | W16 (DEF-113): reachable (this answer) and ready — storage configured and every required credential set. No |
| POST | `/summarise` | `summarise_session` | `SummariseResponse` | Generate a 2-3 sentence AI summary of a session's conversation turns. G-262 (audit A4): the dialogue comes from |
| POST | `/cases` | `create_case` | `CaseCreateResponse` | Create a new improvement case and register it. |
| POST | `/ask` | `ask` | `AskResponse` | One coaching turn, through the compiled graph. |
| GET | `/cases/{case_id}/sign-in` | `sign_in_info` | `SignInInfo` | W17 — what the sign-in window says: the case, who may enter, the lead. Whether the case asks for sign-in |
| POST | `/cases/{case_id}/session` | `sign_in` | `SessionOut` | ADR-0091 decision 2: sign in with the company e-mail the lead registered; the session is this case's. |
| POST | `/cases/{case_id}/people/{who}/code` | `issue_code` | `CodeIssued` | ADR-0105 decisions 1-4 (DEF-103): the lead issues a one-time code for one confirmed member — shown once, here; |
| GET | `/cases/{case_id}/people` | `get_people` | `PeopleResponse` | ADR-0090: the team panel — everyone on the case, the lead first, proposed members marked. |
| POST | `/cases/{case_id}/people` | `add_person` | `PeopleResponse` | ADR-0090 / R8b: the lead adds a member — full name and role; the e-mail before they sign in. |
| POST | `/cases/{case_id}/people/{who}` | `change_person` | `PeopleResponse` | ADR-0090: the lead completes a person's details; with `confirm`, confirms a proposed member — only with |
| DELETE | `/cases/{case_id}/people/{who}` | `remove_person` | `PeopleResponse` | DEF-104 (R8b, ADR-0090): the lead removes a member — never themselves (the case keeps one lead; handing the |
| POST | `/cases/{case_id}/lead` | `hand_over_lead` | `PeopleResponse` | DEF-105 (R8c, founder ruling 2026-10-21): the lead hands the role to another registered member. The case |
| GET | `/gate/review/{case_id}/{phase}` | `gate_review` | `GateReviewResponse` | The assembled gate document, shown to the Belt BEFORE approval. |
| POST | `/upload` | `upload_file` | — | §29.1's external-data channel — procedure step 6.11. |
| DELETE | `/files/{case_id}/{file_id}` | `delete_case_file` | — | W7 (DEF-109): remove an uploaded file — its blob, its `improve_evidence_index` document (by the id the |
| POST | `/gate/decision` | `decide_gate` | `GateDecisionResponse` | R6 — approve or reject the Define report, RESUMING the paused graph. |
| POST | `/gate` | `submit_gate` | `GateSubmitResponse` | Submit the phase for gate review — through the same compiled graph. |
| GET | `/registry` | `get_registry` | `list[RegistryEntryOut]` | Management dashboard — returns all cases from registry. |
| GET | `/cases/{case_id}` | `get_case` | — | Load full case document. Also projects every per-phase upload |

<!-- END GENERATED: api routes -->
