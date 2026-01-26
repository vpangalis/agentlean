"""Experimental/diagnostic runner for ingestion testing.

- This file is an experimental / diagnostic runner.
- It is NOT part of the production backend runtime.
- It must NOT be imported by application, API, domain, or agent code.
- Its logic will later be absorbed into class-based services.
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from backend.main import get_settings

settings = get_settings()

client = SearchIndexClient(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(settings.AZURE_SEARCH_ADMIN_KEY),
)

index = client.get_index("case_index_v3")
print("✅ Index found:", index.name)
