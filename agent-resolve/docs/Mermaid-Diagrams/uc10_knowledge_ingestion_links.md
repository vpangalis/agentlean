# UC10 — Knowledge Document Ingestion: Code Navigation Links

Companion to [uc10_knowledge_ingestion.mmd](./uc10_knowledge_ingestion.mmd).
The **#** column matches the Mermaid `autonumber` arrow number shown in the diagram exactly.

---

## Arrows 1–2 — cosolve-ui.js

| # | What | Link |
|---|------|------|
| 1 | Admin uploads .docx / .pptx / .pdf knowledge document | [index.html:943](../../ui/index.html#L943) |
| 2 | fetch POST /entry/knowledge — multipart/form-data | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |

---

## Arrow 3 — support_routes.py

| # | What | Link |
|---|------|------|
| 3 | handle_knowledge_upload(file: UploadFile) L121 — data=await file.read() L123 | [support_routes.py:121](../../backend/gateway/api/support_routes.py#L121) |

---

## Arrow 4 — entry_handler.py

| # | What | Link |
|---|------|------|
| 4 | upload_knowledge(filename, data, content_type) L126 | [support_routes.py:126](../../backend/gateway/api/support_routes.py#L126) |

---

## Arrows 5–8 — knowledge_ingestion.py → blob_storage.py → Azure Blob (upload raw file)

| # | What | Link |
|---|------|------|
| 5 | upload_document(filename, data) L84 — _get_knowledge_store() L26 | [knowledge_ingestion.py:84](../../backend/storage/ingestion/knowledge_ingestion.py#L84) |
| 6 | upload_file(filename, data) L29 | [blob_storage.py:29](../../backend/storage/blob_storage.py#L29) |
| 7 | Azure Blob upload_blob(filename, data) | [blob_storage.py:41](../../backend/storage/blob_storage.py#L41) |
| 8 | Azure Blob returns ok | [blob_storage.py:41](../../backend/storage/blob_storage.py#L41) |
| 9 | confirmed returned to knowledge_ingestion | [blob_storage.py:29](../../backend/storage/blob_storage.py#L29) |

---

## Arrows 9–14 — knowledge_ingestion.py (text extraction + chunking)

| # | What | Link |
|---|------|------|
| 10 | _extract_text(data, content_type) L513 — .docx / .pptx / .pdf | [knowledge_ingestion.py:513](../../backend/storage/ingestion/knowledge_ingestion.py#L513) |
| 11 | _extract_pdf_text() L563 — PdfReader per page | [knowledge_ingestion.py:563](../../backend/storage/ingestion/knowledge_ingestion.py#L563) |
| 12 | _split_into_sections() L188 — _detect_cosolve_phase() L363, _build_small_chunks() L440 | [knowledge_ingestion.py:188](../../backend/storage/ingestion/knowledge_ingestion.py#L188) |
| 13 | delete_by_source(filename) L53 — removes existing docs before re-indexing | [knowledge_ingestion.py:53](../../backend/storage/ingestion/knowledge_ingestion.py#L53) |
| 14 | _build_doc_id() L509 + build metadata per chunk | [knowledge_ingestion.py:509](../../backend/storage/ingestion/knowledge_ingestion.py#L509) |
| 15 | get_embeddings() L19 — lru_cache singleton, text-embedding-3-large | [embeddings.py:19](../../backend/knowledge/embeddings.py#L19) |

---

## Arrows 15–19 — knowledge_ingestion.py → AzureSearch VectorStore → Azure OpenAI → Azure AI Search

| # | What | Link |
|---|------|------|
| 16 | AzureSearch(knowledge_index_v2) — VectorStore setup | [knowledge_ingestion.py:26](../../backend/storage/ingestion/knowledge_ingestion.py#L26) |
| 17 | add_texts(texts, metadatas, ids) L154 — LangChain handles embedding internally | [knowledge_ingestion.py:154](../../backend/storage/ingestion/knowledge_ingestion.py#L154) |
| 18 | Azure OpenAI returns embeddings batch | [embeddings.py:52](../../backend/knowledge/embeddings.py#L52) |
| 19 | Azure AI Search returns List[doc_id] | [knowledge_ingestion.py:154](../../backend/storage/ingestion/knowledge_ingestion.py#L154) |

---

## Arrows 20–23 — knowledge_ingestion.py → entry_handler.py → support_routes.py → cosolve-ui.js

| # | What | Link |
|---|------|------|
| 20 | chunks_indexed=N returned to entry_handler | [knowledge_ingestion.py:84](../../backend/storage/ingestion/knowledge_ingestion.py#L84) |
| 21 | EntryResponseEnvelope status=accepted | [entry_handler.py:39](../../backend/gateway/entry_handler.py#L39) |
| 22 | FastAPI auto-serializes to JSON — returned to browser | [support_routes.py:111](../../backend/gateway/api/support_routes.py#L111) |
| 23 | fetch() resolves — UI displays success | [cosolve-ui.js:1948](../../ui/cosolve-ui.js#L1948) |
