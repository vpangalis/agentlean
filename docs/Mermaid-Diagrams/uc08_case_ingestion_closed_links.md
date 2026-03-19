# UC08 — Case Ingestion (Closed): Code Navigation Links

Companion to [uc08_case_ingestion_closed.mmd](./uc08_case_ingestion_closed.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | Admin triggers close case action | [index.html:943](../../ui/index.html#L943) |
| 2 | fetch POST /entry/case — intent=CASE_INGESTION, action=CLOSE_CASE | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |

---

## Arrows 3–4 — support_routes.py

| # | What | Link |
|---|------|------|
| 3 | _dispatch_entry_handler(envelope) L82 — handle_case_entry() L96, validate action L100-104 | [support_routes.py:82](../../backend/gateway/api/support_routes.py#L82) |
| 4 | entry_handler.handle_entry(envelope) L84 | [support_routes.py:84](../../backend/gateway/api/support_routes.py#L84) |

---

## Arrow 5 — entry_handler.py

| # | What | Link |
|---|------|------|
| 5 | _handle_case_ingestion(envelope) L66 — action=CLOSE_CASE L74 | [entry_handler.py:66](../../backend/gateway/entry_handler.py#L66) |

---

## Arrows 6–10 — entry_handler.py → case_ingestion.py → blob_storage.py → Azure Blob

| # | What | Link |
|---|------|------|
| 6 | CaseEntryService.get_case(case_id) L107 | [case_ingestion.py:107](../../backend/storage/ingestion/case_ingestion.py#L107) |
| 7 | CaseRepository.load(case_id) L102 | [blob_storage.py:102](../../backend/storage/blob_storage.py#L102) |
| 8 | Azure Blob get_blob_client().download_blob() | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 9 | Azure Blob returns raw JSON bytes | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 10 | case_doc dict returned to case_ingestion | [blob_storage.py:105](../../backend/storage/blob_storage.py#L105) |

---

## Arrows 11–13 — case_ingestion.py (normalisation + build)

| # | What | Link |
|---|------|------|
| 11 | IncidentFactory.from_blob_doc() — normalises d_states, D1_2, status, opened_at | [incident_models.py:1](../../backend/storage/incident_models.py#L1) |
| 12 | build document_text — problem_description + ai_summary + d_state texts | [case_ingestion.py:84](../../backend/storage/ingestion/case_ingestion.py#L84) |
| 13 | _build_doc_id() L509 — sha256(case_id + content_text) | [case_ingestion.py:509](../../backend/storage/ingestion/case_ingestion.py#L509) |

---

## Arrows 14–17 — case_ingestion.py → embeddings.py → Azure OpenAI

| # | What | Link |
|---|------|------|
| 14 | generate_embedding(document_text) L52 | [embeddings.py:52](../../backend/knowledge/embeddings.py#L52) |
| 15 | embeddings.create() — text-embedding-3-large | [embeddings.py:19](../../backend/knowledge/embeddings.py#L19) |
| 16 | Azure OpenAI returns vector list[float] dim=3072 | [embeddings.py:52](../../backend/knowledge/embeddings.py#L52) |
| 17 | embedding vector returned to case_ingestion | [embeddings.py:52](../../backend/knowledge/embeddings.py#L52) |

---

## Arrows 18–21 — case_ingestion.py → AzureSearch VectorStore → Azure AI Search

| # | What | Link |
|---|------|------|
| 18 | build metadata dict — case_id, status, d_states, opened_at, organization_country | [case_ingestion.py:84](../../backend/storage/ingestion/case_ingestion.py#L84) |
| 19 | _get_case_vector_store() L30 — AzureSearch(case_index_v3) | [case_ingestion.py:30](../../backend/storage/ingestion/case_ingestion.py#L30) |
| 20 | add_texts([content_text], metadatas, ids) — LangChain VectorStore | [case_ingestion.py:84](../../backend/storage/ingestion/case_ingestion.py#L84) |
| 21 | Azure AI Search returns [doc_id] | [case_ingestion.py:84](../../backend/storage/ingestion/case_ingestion.py#L84) |

---

## Arrows 22–25 — case_ingestion.py → blob_storage.py → Azure Blob (save)

| # | What | Link |
|---|------|------|
| 22 | CaseRepository.save(case_id) L107 | [blob_storage.py:107](../../backend/storage/blob_storage.py#L107) |
| 23 | Azure Blob upload_blob(data, overwrite=True) | [blob_storage.py:17](../../backend/storage/blob_storage.py#L17) |
| 24 | Azure Blob returns ok | [blob_storage.py:17](../../backend/storage/blob_storage.py#L17) |
| 25 | saved confirmed to case_ingestion | [blob_storage.py:107](../../backend/storage/blob_storage.py#L107) |

---

## Arrows 26–29 — case_ingestion.py → entry_handler.py → support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 26 | indexed=True returned to entry_handler | [case_ingestion.py:107](../../backend/storage/ingestion/case_ingestion.py#L107) |
| 27 | EntryResponseEnvelope status=accepted | [entry_handler.py:39](../../backend/gateway/entry_handler.py#L39) |
| 28 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 29 | fetch() resolves — UI displays success | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |
