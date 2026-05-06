# UC09 — Case Ingestion (Open/Update): Code Navigation Links

Companion to [uc09_case_ingestion_open.mmd](./uc09_case_ingestion_open.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | Admin updates D-state on open case | [index.html:943](../../ui/index.html#L943) |
| 2 | fetch POST /entry/case — intent=CASE_INGESTION, action=UPDATE_CASE | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |

---

## Arrows 3–4 — support_routes.py

| # | What | Link |
|---|------|------|
| 3 | _dispatch_entry_handler(envelope) L82 — handle_case_entry() L96, normalize_action() L99 | [support_routes.py:82](../../backend/gateway/api/support_routes.py#L82) |
| 4 | entry_handler.handle_entry(envelope) L84 | [support_routes.py:84](../../backend/gateway/api/support_routes.py#L84) |

---

## Arrow 5 — entry_handler.py

| # | What | Link |
|---|------|------|
| 5 | _handle_case_ingestion(envelope) L66 — action=UPDATE_CASE L74 | [entry_handler.py:66](../../backend/gateway/entry_handler.py#L66) |

---

## Arrows 6–9 — case_ingestion.py → blob_storage.py → Azure Blob (load)

| # | What | Link |
|---|------|------|
| 6 | CaseEntryService.get_case(case_id) L107 | [case_ingestion.py:107](../../backend/storage/ingestion/case_ingestion.py#L107) |
| 7 | CaseRepository.load(case_id) L102 | [blob_storage.py:102](../../backend/storage/blob_storage.py#L102) |
| 8 | Azure Blob get_blob_client().download_blob() | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 9 | Azure Blob returns raw JSON bytes | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 10 | case_doc dict returned to case_ingestion | [blob_storage.py:105](../../backend/storage/blob_storage.py#L105) |

---

## Arrows 10–11 — case_ingestion.py (partial update — no re-embedding)

| # | What | Link |
|---|------|------|
| 11 | IncidentStateAdapter.from_blob() — normalises fields | [incident_models.py:1](../../backend/storage/incident_models.py#L1) |
| 12 | apply partial_update fields — embedding field intentionally omitted | [case_ingestion.py:84](../../backend/storage/ingestion/case_ingestion.py#L84) |

---

## Arrows 12–15 — case_ingestion.py → CaseSearchIndex (raw SDK) → Azure AI Search (merge)

| # | What | Link |
|---|------|------|
| 13 | CaseSearchIndex(case_index_v3) L43 — raw SearchClient (sanctioned SDK exception) | [case_ingestion.py:43](../../backend/storage/ingestion/case_ingestion.py#L43) |
| 14 | merge_or_upload_documents([partial_doc]) L90 — merge semantics, preserves existing embedding | [case_ingestion.py:90](../../backend/storage/ingestion/case_ingestion.py#L90) |
| 15 | Azure AI Search returns IndexDocumentsResult | [case_ingestion.py:90](../../backend/storage/ingestion/case_ingestion.py#L90) |
| 16 | merge result returned to case_ingestion | [case_ingestion.py:84](../../backend/storage/ingestion/case_ingestion.py#L84) |

---

## Arrows 16–19 — case_ingestion.py → blob_storage.py → Azure Blob (save)

| # | What | Link |
|---|------|------|
| 17 | CaseRepository.save(case_id) L107 | [blob_storage.py:107](../../backend/storage/blob_storage.py#L107) |
| 18 | Azure Blob upload_blob(data, overwrite=True) | [blob_storage.py:17](../../backend/storage/blob_storage.py#L17) |
| 19 | Azure Blob returns ok | [blob_storage.py:17](../../backend/storage/blob_storage.py#L17) |
| 20 | saved confirmed to case_ingestion | [blob_storage.py:107](../../backend/storage/blob_storage.py#L107) |

---

## Arrows 20–23 — case_ingestion.py → entry_handler.py → support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 21 | updated=True returned to entry_handler | [case_ingestion.py:107](../../backend/storage/ingestion/case_ingestion.py#L107) |
| 22 | EntryResponseEnvelope status=accepted | [entry_handler.py:39](../../backend/gateway/entry_handler.py#L39) |
| 23 | FastAPI auto-serializes — returned to browser, UI displays success | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
