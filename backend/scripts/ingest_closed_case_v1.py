"""Experimental/diagnostic runner for ingestion testing.

- This file is an experimental / diagnostic runner.
- It is NOT part of the production backend runtime.
- It must NOT be imported by application, API, domain, or agent code.
- Its logic will later be absorbed into class-based services.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import AzureOpenAI


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config import settings
from backend.infrastructure.embeddings.EmbeddingClient import EmbeddingClient
from backend.infrastructure.search import case_index
from backend.infrastructure.search.CaseSearchIndex import CaseSearchIndex


class IngestClosedCaseV1Runner:
    def __init__(self) -> None:
        self._settings = settings
        self._search_index = CaseSearchIndex(
            endpoint=self._settings.AZURE_SEARCH_ENDPOINT,
            index_name=case_index.CASE_INDEX_NAME,
            admin_key=self._settings.AZURE_SEARCH_ADMIN_KEY,
        )
        self._openai_client = AzureOpenAI(
            api_key=self._settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=self._settings.AZURE_OPENAI_ENDPOINT,
            api_version=self._settings.AZURE_OPENAI_API_VERSION,
        )
        self._embedding_client = EmbeddingClient(
            openai_client=self._openai_client,
            settings_module=self._settings,
        )

    def run(self) -> None:
        case_json_path = (
            Path(__file__).resolve().parent.parent / "INC-20260122-0001.json"
        )

        self._print_openai_config()
        case_data = self._load_case(case_json_path)
        self._ingest_closed_case(case_data)

    def _load_case(self, case_json_path: Path) -> dict[str, Any]:
        with open(case_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _ingest_closed_case(self, case_data: dict[str, Any]) -> None:
        case_id = case_data["case"]["case_number"]
        status = case_data["case"]["status"]

        if status != "closed":
            raise ValueError(
                f"Only closed cases can be ingested. Case {case_id} status={status}."
            )

        opening_date = self._to_datetime_offset(case_data["case"]["opening_date"])
        closure_date = self._to_datetime_offset(case_data["case"]["closure_date"])

        meta = case_data["meta"]
        version = meta["version"]
        created_at = self._to_datetime_offset(meta["created_at"])
        updated_at = self._to_datetime_offset(meta["updated_at"])

        d1 = case_data["phases"]["D1_D2"]["data"]
        d3 = case_data["phases"]["D3"]["data"]

        problem_description = d1["problem_description"]

        organization = d1["organization"]
        organization_country = organization["country"]
        organization_site = organization["site"]
        organization_department = organization["department"]

        team_members = d1.get("team_members", [])

        what_happened = d3["what_happened"]
        why_problem = d3["why_problem"]
        when = d3["when"]
        where = d3["where"]
        who = d3["who"]
        how_identified = d3["how_identified"]
        impact = d3["impact"]

        immediate_actions_text = self._join_actions(
            case_data["phases"]["D4"]["data"]["actions"], "action"
        )

        permanent_actions_text = self._join_actions(
            case_data["phases"]["D6"]["data"]["actions"], "action"
        )

        investigation_tasks_text = self._join_actions(
            case_data["phases"]["D5"]["data"]["investigation_tasks"], "task"
        )

        d5 = case_data["phases"]["D5"]["data"]

        fishbone_text = "\n".join(
            f"{k.upper()}: {', '.join(v)}" for k, v in d5["fishbone"].items()
        )

        factors_text = "\n".join(
            f"- {f['factor']} (Owner: {f['owner']}, Status: {f['status']})"
            for f in d5["factors"]
        )

        five_whys_text = "\n".join(
            f"{k}: {' → '.join(v)}" for k, v in d5["five_whys"].items()
        )

        embedding_text = (
            f"""
CASE {case_id}

Problem:
{problem_description}

What happened:
{what_happened}

Why:
{why_problem}

Impact:
{impact}

When:
{when}

Where:
{where}

Who:
{who}

How identified:
{how_identified}

Immediate actions:
{immediate_actions_text}

Permanent actions:
{permanent_actions_text}

Investigation tasks:
{investigation_tasks_text}

Fishbone analysis:
{fishbone_text}

Key factors:
{factors_text}

Five whys:
{five_whys_text}
"""
        ).strip()

        self._preflight()

        embedding = self._embedding_client.generate_embedding(embedding_text)

        if len(embedding) != self._settings.AZURE_SEARCH_VECTOR_DIMENSIONS:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"expected {self._settings.AZURE_SEARCH_VECTOR_DIMENSIONS}, "
                f"got {len(embedding)}."
            )

        document = {
            "case_id": case_id,
            "status": status,
            "opening_date": opening_date,
            "closure_date": closure_date,
            "created_at": created_at,
            "updated_at": updated_at,
            "version": version,
            "organization_country": organization_country,
            "organization_site": organization_site,
            "organization_department": organization_department,
            "discipline_completed": [
                "D1",
                "D2",
                "D3",
                "D4",
                "D5",
                "D6",
                "D7",
                "D8",
            ],
            "problem_description": problem_description,
            "team_members": team_members,
            "what_happened": what_happened,
            "why_problem": why_problem,
            "when": when,
            "where": where,
            "who": who,
            "how_identified": how_identified,
            "impact": impact,
            "immediate_actions_text": immediate_actions_text,
            "permanent_actions_text": permanent_actions_text,
            "investigation_tasks_text": investigation_tasks_text,
            "factors_text": factors_text,
            "fishbone_text": fishbone_text,
            "five_whys_text": five_whys_text,
            "evidence_descriptions": "",
            "evidence_tags": [],
            "ai_summary": "",
            "content_vector": embedding,
        }

        document["doc_id"] = case_index.build_doc_id(case_id)
        case_index.validate_doc_id(document["doc_id"])

        document.update(
            {
                "problem_description": self._normalize_string(
                    document["problem_description"]
                ),
                "what_happened": self._normalize_string(document["what_happened"]),
                "why_problem": self._normalize_string(document["why_problem"]),
                "when": self._normalize_string(document["when"]),
                "where": self._normalize_string(document["where"]),
                "who": self._normalize_string(document["who"]),
                "how_identified": self._normalize_string(document["how_identified"]),
                "impact": self._normalize_string(document["impact"]),
                "immediate_actions_text": self._normalize_string(
                    document["immediate_actions_text"]
                ),
                "permanent_actions_text": self._normalize_string(
                    document["permanent_actions_text"]
                ),
                "investigation_tasks_text": self._normalize_string(
                    document["investigation_tasks_text"]
                ),
                "factors_text": self._normalize_string(document["factors_text"]),
                "fishbone_text": self._normalize_string(document["fishbone_text"]),
                "five_whys_text": self._normalize_string(document["five_whys_text"]),
                "evidence_descriptions": self._normalize_string(
                    document["evidence_descriptions"]
                ),
                "ai_summary": self._normalize_string(document["ai_summary"]),
                "team_members": self._normalize_string_list(document["team_members"]),
                "discipline_completed": self._normalize_string_list(
                    document["discipline_completed"]
                ),
                "evidence_tags": self._normalize_string_list(
                    document["evidence_tags"]
                ),
                "content_vector": self._normalize_vector(document["content_vector"]),
            }
        )

        for key, value in document.items():
            if isinstance(value, list) and key not in self._allowed_list_fields():
                raise RuntimeError(
                    f"❌ LIST STILL PRESENT IN PRIMITIVE FIELD: {key} -> {value}"
                )

        upload_results = self._search_index.upload_documents([document])

        failed = [r for r in upload_results if not r.succeeded]
        if failed:
            messages = "; ".join(f"{r.key}: {r.error_message}" for r in failed)
            raise ValueError(f"Azure Search upload failed: {messages}")

        try:
            self._search_index.get_document(document["doc_id"])
        except Exception as exc:
            raise ValueError(
                f"Uploaded document not retrievable by key: {document['doc_id']}"
            ) from exc

        print(f"✅ Ingested closed case {case_id} into {case_index.CASE_INDEX_NAME}")
        print(f"✅ Uploaded doc_id: {document['doc_id']}")

    def _preflight(self) -> None:
        required = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_ADMIN_KEY",
        ]
        missing = [name for name in required if not getattr(self._settings, name, None)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        self._search_index.ensure_index_exists(
            case_index.CASE_INDEX_NAME,
            f"Index {case_index.CASE_INDEX_NAME} not found.",
        )

        test_embedding = self._embedding_client.generate_embedding("ping")
        if len(test_embedding) != self._settings.AZURE_SEARCH_VECTOR_DIMENSIONS:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"expected {self._settings.AZURE_SEARCH_VECTOR_DIMENSIONS}, "
                f"got {len(test_embedding)}."
            )

    def _print_openai_config(self) -> None:
        print(
            "Azure OpenAI config loaded:",
            f"endpoint={'SET' if self._settings.AZURE_OPENAI_ENDPOINT else 'MISSING'}",
            f"api_key={self._mask_secret(self._settings.AZURE_OPENAI_API_KEY)}",
            f"api_version={'SET' if self._settings.AZURE_OPENAI_API_VERSION else 'MISSING'}",
            (
                f"deployment={self._settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT or 'MISSING'}"
            ),
        )

    @staticmethod
    def _to_datetime_offset(value: str | None) -> str | None:
        if not value:
            return None

        dt = datetime.fromisoformat(value.replace("Z", ""))
        return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _join_actions(actions: list[dict[str, Any]], key: str) -> str:
        return "\n".join(
            (
                f"- {a[key]} (Responsible: {a['responsible']}, "
                f"Due: {a['due_date']}, Actual: {a['actual_date']})"
            )
            for a in actions
        )

    @staticmethod
    def _normalize_string(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, list):
            return "\n".join(str(v) for v in value if v is not None)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @staticmethod
    def _normalize_string_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            normalized = []
            for v in value:
                if isinstance(v, (str, int, float)):
                    normalized.append(str(v))
                elif v is None:
                    continue
                else:
                    raise ValueError(
                        f"Invalid item in collection field: {type(v).__name__} -> {v}"
                    )
            return normalized

        if isinstance(value, (str, int, float)):
            return [str(value)]

        raise ValueError(
            f"Invalid value for collection field: {type(value).__name__} -> {value}"
        )

    @staticmethod
    def _normalize_vector(value: Any) -> list[float]:
        if not isinstance(value, list):
            raise ValueError("content_vector must be a list of floats")
        return [float(v) for v in value]

    @staticmethod
    def _mask_secret(value: str | None) -> str:
        if not value:
            return "MISSING"
        if len(value) <= 4:
            return "****"
        return f"****{value[-4:]}"

    @staticmethod
    def _allowed_list_fields() -> set[str]:
        return {
            "team_members",
            "discipline_completed",
            "evidence_tags",
            "content_vector",
        }


IngestClosedCaseV1Runner().run()
