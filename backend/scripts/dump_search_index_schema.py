"""Experimental/diagnostic runner for ingestion testing.

- This file is an experimental / diagnostic runner.
- It is NOT part of the production backend runtime.
- It must NOT be imported by application, API, domain, or agent code.
- Its logic will later be absorbed into class-based services.
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import os
import json

client = SearchIndexClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"]),
)

index = client.get_index("case_index_v3")

print(json.dumps(
    [
        {
            "name": f.name,
            "type": str(f.type),
            "searchable": f.searchable,
            "filterable": f.filterable,
            "facetable": f.facetable,
            "sortable": f.sortable,
        }
        for f in index.fields
    ],
    indent=2
))
