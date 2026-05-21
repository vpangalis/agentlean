from __future__ import annotations

import logging
import os
import sys

# Add parent to path so backend imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceExistsError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
)

from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_DIMENSIONS = 3072   # text-embedding-3-large
HNSW_CONFIG_NAME  = "improve-hnsw"
VECTOR_PROFILE    = "improve-vector-profile"


def get_index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )


def create_improve_case_index() -> None:
    """
    improve_case_index
    One document per case — written on every phase gate pass.
    Used by: management dashboard, Orchestrator context loading.
    """
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String,
                    key=True, filterable=True),
        SimpleField(name="case_id", type=SearchFieldDataType.String,
                    filterable=True, sortable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SimpleField(name="belt_level", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="leader", type=SearchFieldDataType.String,
                    filterable=True),
        SearchableField(name="department", type=SearchFieldDataType.String,
                        filterable=True),
        SimpleField(name="current_phase", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="rag_status", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="status", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="created_at", type=SearchFieldDataType.String,
                    filterable=True, sortable=True),
        SimpleField(name="target_date", type=SearchFieldDataType.String,
                    filterable=True, sortable=True),
        SimpleField(name="days_in_phase", type=SearchFieldDataType.Int32,
                    filterable=True, sortable=True),
        # Phase summaries — one per DMAIC phase
        SearchableField(name="phase_summary_define",
                        type=SearchFieldDataType.String),
        SearchableField(name="phase_summary_measure",
                        type=SearchFieldDataType.String),
        SearchableField(name="phase_summary_analyse_phase",
                        type=SearchFieldDataType.String),
        SearchableField(name="phase_summary_improve",
                        type=SearchFieldDataType.String),
        SearchableField(name="phase_summary_control",
                        type=SearchFieldDataType.String),
        # Searchable summary for semantic/vector search
        SearchableField(name="content_text",
                        type=SearchFieldDataType.String),
        # Vector field
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=HNSW_CONFIG_NAME)],
        profiles=[VectorSearchProfile(
            name=VECTOR_PROFILE,
            algorithm_configuration_name=HNSW_CONFIG_NAME,
        )],
    )

    semantic_search = SemanticSearch(configurations=[
        SemanticConfiguration(
            name="improve-case-semantic",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content_text")],
                keywords_fields=[
                    SemanticField(field_name="title"),
                    SemanticField(field_name="department"),
                ],
            ),
        )
    ])

    index = SearchIndex(
        name=settings.AZURE_SEARCH_IMPROVE_CASE_INDEX,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    _create_or_skip(index)


def create_improve_knowledge_index() -> None:
    """
    improve_knowledge_index
    DMAIC methodology content — chunked from PDF training + Excel toolkit.
    Used by: Orchestrator (all phases), Analyst agent.
    """
    fields = [
        SimpleField(name="doc_id", type=SearchFieldDataType.String,
                    key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="section_title",
                        type=SearchFieldDataType.String),
        SearchableField(name="content_text",
                        type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String,
                    filterable=True),
        SimpleField(name="phase", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="tool_name", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="belt_level", type=SearchFieldDataType.String,
                    filterable=True, facetable=True),
        SimpleField(name="chunk_type", type=SearchFieldDataType.String,
                    filterable=True),
        SimpleField(name="page_start", type=SearchFieldDataType.Int32,
                    filterable=True),
        SimpleField(name="page_end", type=SearchFieldDataType.Int32,
                    filterable=True),
        SimpleField(name="char_count", type=SearchFieldDataType.Int32,
                    filterable=True),
        SimpleField(name="created_at", type=SearchFieldDataType.String,
                    filterable=True),
        # Vector field
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=HNSW_CONFIG_NAME)],
        profiles=[VectorSearchProfile(
            name=VECTOR_PROFILE,
            algorithm_configuration_name=HNSW_CONFIG_NAME,
        )],
    )

    semantic_search = SemanticSearch(configurations=[
        SemanticConfiguration(
            name="improve-knowledge-semantic",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content_text")],
                keywords_fields=[
                    SemanticField(field_name="section_title"),
                    SemanticField(field_name="tool_name"),
                ],
            ),
        )
    ])

    index = SearchIndex(
        name=settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    _create_or_skip(index)


def _create_or_skip(index: SearchIndex) -> None:
    client = get_index_client()
    try:
        client.create_index(index)
        logger.info("Created index: %s", index.name)
    except ResourceExistsError:
        logger.info("Index already exists — skipping: %s", index.name)
    except Exception as e:
        logger.error("Failed to create index %s: %s", index.name, e)
        raise


if __name__ == "__main__":
    logger.info("Creating Agent Improve Azure Search indexes...")
    create_improve_case_index()
    create_improve_knowledge_index()
    logger.info("Done.")
