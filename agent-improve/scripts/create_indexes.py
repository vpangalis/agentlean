from __future__ import annotations

import argparse
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
    HnswParameters,
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
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)

from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_DIMENSIONS = 3072   # text-embedding-3-large

# improve_case_index's names. Reference §23.3 records this index as the only
# one whose vector configuration is named differently, and schedules the
# normalisation to `default` for the step 9.1 reindex. Until that lands these
# are the live names and this script must keep producing them.
HNSW_CONFIG_NAME  = "improve-hnsw"
VECTOR_PROFILE    = "improve-vector-profile"

# improve_knowledge_index's names — both literally "default" on the live
# index, and matching `KNOWLEDGE_INDEX_FIELDS` in knowledge/retriever.py.
# NOT interchangeable with the two above.
KNOWLEDGE_HNSW_CONFIG   = "default"
KNOWLEDGE_VECTOR_PROFILE = "default"


def get_index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )


def create_improve_case_index() -> None:
    """
    improve_case_index
    One document per case â written on every phase gate pass.
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
        # Phase summaries â one per DMAIC phase
        SearchableField(name="phase_summary_define",
                        type=SearchFieldDataType.String),
        SearchableField(name="phase_summary_measure",
                        type=SearchFieldDataType.String),
        SearchableField(name="phase_summary_analyse",
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


def create_improve_knowledge_index(name: str | None = None) -> None:
    """
    improve_knowledge_index
    LSS Black Belt eBook methodology, chunked per page. Static.
    Used by: `rag_lookup_methodology` (reference §24), all five phases.

    **This definition mirrors the LIVE index exactly**, verified field by
    field against Azure (2026-08-25) and against reference §23.1 /
    CLAUDE.md §7.3. That exactness is the requirement, not a nicety: `name`
    exists so a FRESH index can be created for the ingest-fresh / diff /
    swap procedure, and a fresh index whose schema differs from live cannot
    be swapped in.

    Two things in particular must not drift:

      - **The vector profile is named `default`**, not
        `improve-vector-profile`. `KNOWLEDGE_INDEX_FIELDS` in
        `knowledge/retriever.py` declares `vector_search_profile_name=
        "default"`, and the live index agrees. `improve_case_index` is the
        one that uses `improve-vector-profile`, and reference §23.3 is
        normalising that away rather than spreading it.

      - **There is no semantic configuration.** The live index has none,
        and `search_type="hybrid"` on the vectorstore does not use one.
        Adding one would make a "fresh" index quietly non-identical.

    *Previously this function declared a completely different schema:
    `doc_id`, `title`, `section_title`, `content_text`, `source`, `phase`,
    `tool_name`, `belt_level`, `chunk_type`, `page_start`, `page_end`,
    `created_at`, and a vector field named `embedding`. **Not one of those
    fields exists on the live index**, and `phase` is specifically the name
    reference §23.1 records as the filter bug that makes Azure reject the
    whole query. An index created from it would have rejected every write
    `ingest_knowledge.py` makes. Corrected 2026-08-25 against the live
    schema.*
    """
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String,
                    key=True, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name=KNOWLEDGE_VECTOR_PROFILE,
        ),
        SearchableField(name="metadata", type=SearchFieldDataType.String),
        SimpleField(name="source_file", type=SearchFieldDataType.String,
                    filterable=True),
        SimpleField(name="phase_relevance", type=SearchFieldDataType.String,
                    filterable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32,
                    filterable=True),
    ]

    # Matches the live index: HNSW, cosine, m=4, efConstruction=400,
    # efSearch=500, algorithm and profile both named 'default'.
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(
            name=KNOWLEDGE_HNSW_CONFIG,
            parameters=HnswParameters(
                m=4, ef_construction=400, ef_search=500,
                metric=VectorSearchAlgorithmMetric.COSINE,
            ),
        )],
        profiles=[VectorSearchProfile(
            name=KNOWLEDGE_VECTOR_PROFILE,
            algorithm_configuration_name=KNOWLEDGE_HNSW_CONFIG,
        )],
    )

    index = SearchIndex(
        name=name or settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
        fields=fields,
        vector_search=vector_search,
    )

    _create_or_skip(index)


def _create_or_skip(index: SearchIndex) -> None:
    client = get_index_client()
    try:
        client.create_index(index)
        logger.info("Created index: %s", index.name)
    except ResourceExistsError:
        logger.info("Index already exists â skipping: %s", index.name)
    except Exception as e:
        logger.error("Failed to create index %s: %s", index.name, e)
        raise


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Create Agent Improve Azure AI Search indexes.")
    ap.add_argument(
        "--which", choices=["all", "case", "knowledge"], default="all",
        help="Which index to create. Existing indexes are skipped, never "
             "altered or deleted.")
    ap.add_argument(
        "--name",
        help="Override the index name. Only valid with --which knowledge, "
             "and the reason it exists: the ratified rebuild procedure is "
             "ingest into a FRESH index, diff against live, then swap.")
    args = ap.parse_args()

    if args.name and args.which != "knowledge":
        ap.error("--name is only supported with --which knowledge")

    if args.which in ("all", "case"):
        create_improve_case_index()
    if args.which in ("all", "knowledge"):
        create_improve_knowledge_index(args.name)
    logger.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
