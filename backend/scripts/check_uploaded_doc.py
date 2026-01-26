"""Experimental/diagnostic runner for ingestion testing.

- This file is an experimental / diagnostic runner.
- It is NOT part of the production backend runtime.
- It must NOT be imported by application, API, domain, or agent code.
- Its logic will later be absorbed into class-based services.
"""

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from backend.main import get_settings

settings = get_settings()

client = SearchClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    index_name="case_index_v3",
    credential=AzureKeyCredential(settings.AZURE_SEARCH_ADMIN_KEY),
)

doc_id = "INC-20260122-0001__case_index_v3"

doc = client.get_document(doc_id)
print("FOUND:", doc["doc_id"])
