# UC11 — Evidence Ingestion: Code Navigation Links

Companion to [uc11_evidence_ingestion.mmd](./uc11_evidence_ingestion.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | Admin uploads evidence file for a specific case | [index.html:943](../../ui/index.html#L943) |
| 2 | fetch POST /entry/case — intent=CASE_INGESTION, action=UPLOAD_EVIDENCE | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |

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
| 5 | _handle_case_ingestion(envelope) L66 — action=UPLOAD_EVIDENCE L74 | [entry_handler.py:66](../../backend/gateway/entry_handler.py#L66) |

---

## Arrow 6 — evidence_ingestion.py (_ensure_case_exists)

| # | What | Link |
|---|------|------|
| 6 | upload_evidence(case_id, filename, data) L36 — _ensure_case_exists(case_id) L68 | [evidence_ingestion.py:36](../../backend/storage/ingestion/evidence_ingestion.py#L36) |

---

## Arrows 7–10 — evidence_ingestion.py → blob_storage.py → Azure Blob (case existence check)

| # | What | Link |
|---|------|------|
| 7 | CaseRepository.load(case_id) L102 — confirms case exists | [blob_storage.py:102](../../backend/storage/blob_storage.py#L102) |
| 8 | Azure Blob get_blob_client().download_blob() | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 9 | Azure Blob returns raw JSON bytes | [blob_storage.py:20](../../backend/storage/blob_storage.py#L20) |
| 10 | case exists confirmed to evidence_ingestion | [blob_storage.py:105](../../backend/storage/blob_storage.py#L105) |

---

## Arrows 11–14 — evidence_ingestion.py → blob_storage.py → Azure Blob (upload evidence file)

| # | What | Link |
|---|------|------|
| 11 | upload_file("{case_id}/{filename}") L29 | [blob_storage.py:29](../../backend/storage/blob_storage.py#L29) |
| 12 | Azure Blob upload_blob(data, overwrite=True) | [blob_storage.py:41](../../backend/storage/blob_storage.py#L41) |
| 13 | Azure Blob returns ok | [blob_storage.py:41](../../backend/storage/blob_storage.py#L41) |
| 14 | confirmed returned to evidence_ingestion | [blob_storage.py:29](../../backend/storage/blob_storage.py#L29) |

---

## Arrows 15–17 — evidence_ingestion.py (text extraction + metadata)

| # | What | Link |
|---|------|------|
| 15 | _extract_text(data, content_type) L75 — .docx / .pdf / plain text | [evidence_ingestion.py:75](../../backend/storage/ingestion/evidence_ingestion.py#L75) |
| 16 | _build_doc_id(case_id, filename) L71 — sha256(case_id + filename) | [evidence_ingestion.py:71](../../backend/storage/ingestion/evidence_ingestion.py#L71) |
| 17 | build metadata{case_id, filename, content_type, ingested_at} | [evidence_ingestion.py:36](../../backend/storage/ingestion/evidence_ingestion.py#L36) |

---

## Arrow 18 — evidence_ingestion.py → embeddings.py

| # | What | Link |
|---|------|------|
| 18 | get_embeddings() L19 — lru_cache singleton, text-embedding-3-large | [embeddings.py:19](../../backend/knowledge/embeddings.py#L19) |

---

## Arrows 19–22 — evidence_ingestion.py → AzureSearch VectorStore → Azure OpenAI → Azure AI Search

| # | What | Link |
|---|------|------|
| 19 | _get_evidence_store() L16 — AzureSearch(evidence_index_v1) | [evidence_ingestion.py:16](../../backend/storage/ingestion/evidence_ingestion.py#L16) |
| 20 | add_texts([content_text], metadatas, ids) L45 — case_id in metadata enables OData filter at search time | [evidence_ingestion.py:45](../../backend/storage/ingestion/evidence_ingestion.py#L45) |
| 21 | Azure OpenAI returns embedding dim=3072 | [embeddings.py:52](../../backend/knowledge/embeddings.py#L52) |
| 22 | Azure AI Search returns [doc_id] | [evidence_ingestion.py:45](../../backend/storage/ingestion/evidence_ingestion.py#L45) |

---

## Arrows 23–26 — evidence_ingestion.py → entry_handler.py → support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 23 | indexed=True returned to entry_handler | [evidence_ingestion.py:36](../../backend/storage/ingestion/evidence_ingestion.py#L36) |
| 24 | EntryResponseEnvelope status=accepted | [entry_handler.py:39](../../backend/gateway/entry_handler.py#L39) |
| 25 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 26 | fetch() resolves — UI displays success | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |
