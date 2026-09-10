#!/usr/bin/env python3
"""Step 6.13 sub-steps 1 and 3 — the evidence index migration.

    python scripts/backfill_evidence_index.py            # dry run, the default
    python scripts/backfill_evidence_index.py --apply    # write

**Dry run is the default and `--apply` is the only way to write.** This script
deletes documents from a live index (ruling AT3), and a migration whose default
mode mutates production is one keystroke from an accident.

WHAT IT DOES, in the order 6.13 fixes and for the reasons 6.13 gives
--------------------------------------------------------------------
1. **Schema add** — §23.2's seven fields on the live index. All seven are
   additive, so Azure assigns `null` to existing documents and no rebuild is
   required (verified against Microsoft Learn, Part AQ3). Idempotent.

3. **Backfill**, in three passes because the corpus has three populations:

   a. **Superseded, bytes gone → DELETE** (ruling AT3). `storage/blob.py`
      writes with `overwrite=True`, so where one `blob_path` was uploaded twice
      the container kept the later bytes and the index kept both documents. A
      digest for the earlier one could only be computed from the later bytes —
      the newer version's digest written onto the older chunk, which is the
      exact claim `content_digest` exists to make, made falsely. §23.2 already
      rules that supersession DELETES rather than flags; these predate the
      supersession path and this applies the existing rule to the backlog.
      **The case-blob `evidence_index_id` is nulled in the same pass**, or the
      blob points at a document that no longer exists.

   b. **Reachable from a case blob → MERGE.** The normal path.

   c. **No case-blob record → RECONSTRUCT from the index's own metadata**
      (ruling AT2). One live document has no upload record at all. Its
      `metadata` carries `filename`, `upload_phase` and `timestamp`, and its
      bytes survive under `uploads/`, so a real digest is computable with no
      case record.

**`role` is read from the RAW STORED JSON, never from a loaded `UploadRecord`**
— the single most important line in this script. `role`, `shape_match` and
`content_digest` are *absent keys* on every pre-6.12 record; a loaded model
manufactures `'other evidence'` and `'unsolicited'` for them as Pydantic
defaults. Reading the model would write a fabricated role into a filterable
field and record it as migrated (DECISIONS Part AT1).

**Writes are `mergeOrUpload` and deliberately OMIT `content_vector`.** Measured
on this index: `stored: true`, `retrievable: false` (§23.2). Under `stored:
true` a partial update keeps the vector, and the field is not retrievable, so
supplying it would mean re-embedding every document touched — the cost
`stored: true` exists to avoid. **If `stored` is ever declared `false` here,
this script must be rewritten before that change lands.**
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchableField, SimpleField
from azure.search.documents.indexes.models import SearchFieldDataType as T

from backend.core.config import settings
from backend.storage import blob
# §23.2.1's sentinel is domain vocabulary, not migration plumbing, so it is
# defined next to the other role values and imported here.
from backend.upload.asks import SENTINEL_KIND, SENTINEL_ROLE, SENTINEL_SHAPE

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("backfill")

# The Azure SDK logs every request and response header at INFO. On a corpus
# this size that is several hundred lines of noise around the handful that say
# what the migration decided, and a migration you cannot read the output of is
# one you cannot check before applying.
for _noisy in ("azure", "azure.core.pipeline.policies.http_logging_policy"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

# The seven, with §23.2's attributes field for field.
NEW_FIELDS = [
    SimpleField(name="phase", type=T.String, filterable=True),
    SimpleField(name="uploaded_at", type=T.String,
                filterable=True, sortable=True),
    SearchableField(name="role", type=T.String, filterable=True),
    SimpleField(name="kind", type=T.String, filterable=True),
    SearchableField(name="description", type=T.String),
    SimpleField(name="content_digest", type=T.String, filterable=True),
    SimpleField(name="shape_match", type=T.String, filterable=True),
]


def _index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=settings.AZURE_SEARCH_ENDPOINT,
                             credential=AzureKeyCredential(
                                 settings.AZURE_SEARCH_API_KEY))


def _search_client() -> SearchClient:
    return SearchClient(endpoint=settings.AZURE_SEARCH_ENDPOINT,
                        index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
                        credential=AzureKeyCredential(
                            settings.AZURE_SEARCH_API_KEY))


# ─────────────────────────── sub-step 1: schema ────────────────────────────

def add_schema_fields(apply: bool) -> list[str]:
    """Add the seven. Returns the names actually missing before the call."""
    ic = _index_client()
    name = settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX
    idx = ic.get_index(name)
    have = {f.name for f in idx.fields}
    missing = [f for f in NEW_FIELDS if f.name not in have]

    if not missing:
        logger.info("sub-step 1 schema: all seven already present — no-op")
        return []

    logger.info("sub-step 1 schema: adding %d field(s): %s",
                len(missing), ", ".join(f.name for f in missing))
    if apply:
        idx.fields = list(idx.fields) + missing
        ic.create_or_update_index(idx)
        logger.info("sub-step 1 schema: applied")
    else:
        logger.info("sub-step 1 schema: DRY RUN, not applied")
    return [f.name for f in missing]


# ──────────────────────── the case-blob side, raw ──────────────────────────

async def read_blob_records() -> tuple[dict, list]:
    """Every upload record, as RAW stored JSON — never a loaded model.

    Returns (by_index_id, all_records). Each record is a dict carrying the raw
    upload dict plus the case id and phase key it was stored under.
    """
    container = blob._container()
    case_ids: list[str] = []
    async for b in container.list_blobs(name_starts_with="cases/"):
        stem = b.name.split("/")[-1]
        # `case_path` is `cases/case_{case_id}.json` — the prefix is part of
        # the filename, not a folder, so it has to come off here or every
        # download misses and the whole corpus reads as unreachable.
        if stem.startswith("case_") and stem.endswith(".json"):
            case_ids.append(stem[len("case_"):-len(".json")])

    by_index_id: dict[str, dict] = {}
    all_records: list[dict] = []
    for case_id in sorted(set(case_ids)):
        try:
            doc = json.loads(await blob._download(blob.case_path(case_id)))
        except Exception as e:                      # noqa: BLE001
            logger.warning("  case %s unreadable: %s", case_id, e)
            continue
        for phase_key, prec in (doc.get("phases") or {}).items():
            for raw in (prec or {}).get("uploads") or []:
                rec = {"case_id": case_id, "phase": phase_key, "raw": raw}
                all_records.append(rec)
                eid = raw.get("evidence_index_id")
                if eid:
                    by_index_id[eid] = rec
    return by_index_id, all_records


def mark_superseded(all_records: list) -> set[str]:
    """Index ids whose bytes no longer exist — ruling AT3.

    One `blob_path` uploaded twice means the container holds the LATER bytes
    only. Every record for that path except the latest is a version whose
    bytes are gone.
    """
    by_path: dict[tuple, list] = defaultdict(list)
    for rec in all_records:
        key = (rec["case_id"], rec["raw"].get("blob_path") or "")
        by_path[key].append(rec)

    dead: set[str] = set()
    for key, recs in by_path.items():
        if len(recs) < 2:
            continue
        recs.sort(key=lambda r: r["raw"].get("uploaded_at") or "")
        for stale in recs[:-1]:                     # all but the newest
            eid = stale["raw"].get("evidence_index_id")
            if eid:
                dead.add(eid)
                stale["_superseded"] = True
    return dead


async def digest_of(blob_path: str) -> str | None:
    if not blob_path:
        return None
    try:
        return hashlib.sha256(await blob.download_bytes(blob_path)).hexdigest()
    except Exception as e:                          # noqa: BLE001
        logger.warning("    digest unavailable for %s: %s", blob_path, e)
        return None


def role_of(raw: dict) -> str:
    """The stored role, or the sentinel — and ABSENCE is what decides.

    `"role" in raw` is the whole test. A loaded UploadRecord would answer
    'other evidence' here for a record that has never carried a role, and the
    migration would record a fabricated value as migrated (Part AT1).
    """
    stored = raw.get("role")
    return stored if ("role" in raw and stored) else SENTINEL_ROLE


# ─────────────────────────── sub-step 3: backfill ──────────────────────────

async def backfill(apply: bool) -> dict:
    sc = _search_client()
    live = list(sc.search(search_text="*",
                          select=["id", "case_id", "metadata"], top=1000))
    logger.info("\nsub-step 3 backfill: %d live document(s)", len(live))

    by_index_id, all_records = await read_blob_records()
    dead = mark_superseded(all_records)
    logger.info("  case-blob records: %d, naming %d index document(s)",
                len(all_records), len(by_index_id))

    merges: list[dict] = []
    deletes: list[dict] = []
    reconstructed: list[str] = []

    for row in live:
        doc_id = row["id"]
        rec = by_index_id.get(doc_id)

        # (a) superseded, bytes gone → delete
        if doc_id in dead:
            logger.info("  DELETE   %s  (superseded, bytes overwritten)", doc_id)
            deletes.append({"id": doc_id})
            continue

        if rec is not None:
            # (b) reachable from a case blob
            raw = rec["raw"]
            digest = await digest_of(raw.get("blob_path") or "")
            doc = {
                "id": doc_id,
                "phase": rec["phase"],
                "uploaded_at": raw.get("uploaded_at") or "",
                "role": role_of(raw),
                "kind": raw.get("kind") or SENTINEL_KIND,
                "description": raw.get("summary") or "",
                "content_digest": digest or "",
                "shape_match": (raw.get("shape_match")
                                if "shape_match" in raw else SENTINEL_SHAPE),
            }
            logger.info("  MERGE    %s  role=%r kind=%r digest=%s",
                        doc_id, doc["role"], doc["kind"],
                        (digest or "-")[:12])
            merges.append(doc)
            continue

        # (c) no case-blob record → reconstruct from the index's own metadata
        try:
            meta = json.loads(row.get("metadata") or "{}")
        except (json.JSONDecodeError, TypeError):
            meta = {}
        digest = await digest_of(meta.get("blob_path") or "")
        doc = {
            "id": doc_id,
            "phase": meta.get("upload_phase") or "",
            "uploaded_at": meta.get("timestamp") or "",
            "role": SENTINEL_ROLE,
            "kind": meta.get("kind") or SENTINEL_KIND,
            "description": meta.get("filename") or "",
            "content_digest": digest or "",
            "shape_match": SENTINEL_SHAPE,
        }
        logger.info("  RECONST  %s  (no blob record) file=%r digest=%s",
                    doc_id, meta.get("filename"), (digest or "-")[:12])
        reconstructed.append(doc_id)
        merges.append(doc)

    if not apply:
        logger.info("\n  DRY RUN — %d merge(s), %d delete(s) not written",
                    len(merges), len(deletes))
        return {"merges": len(merges), "deletes": len(deletes),
                "reconstructed": reconstructed, "applied": False}

    if merges:
        sc.merge_or_upload_documents(merges)
        logger.info("\n  merged %d document(s)", len(merges))
    if deletes:
        sc.delete_documents(deletes)
        logger.info("  deleted %d document(s)", len(deletes))

    # The case blob must stop naming a document that no longer exists.
    nulled = await null_dead_index_ids(all_records)
    logger.info("  nulled evidence_index_id on %d case-blob record(s)", nulled)

    return {"merges": len(merges), "deletes": len(deletes),
            "reconstructed": reconstructed, "nulled": nulled, "applied": True}


async def null_dead_index_ids(all_records: list) -> int:
    """Null `evidence_index_id` on every record whose document was deleted."""
    touched: dict[str, dict] = {}
    for rec in all_records:
        if not rec.get("_superseded"):
            continue
        case_id = rec["case_id"]
        if case_id not in touched:
            touched[case_id] = json.loads(
                await blob._download(blob.case_path(case_id)))
        doc = touched[case_id]
        for raw in ((doc.get("phases") or {})
                    .get(rec["phase"], {}) or {}).get("uploads") or []:
            if raw.get("evidence_index_id") == rec["raw"].get("evidence_index_id"):
                raw["evidence_index_id"] = None

    n = 0
    for case_id, doc in touched.items():
        await blob._upload(blob.case_path(case_id),
                           json.dumps(doc, indent=2, ensure_ascii=False))
        n += sum(1 for r in all_records
                 if r.get("_superseded") and r["case_id"] == case_id)
    return n


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="write. Without it, this is a dry run.")
    args = ap.parse_args()

    if not args.apply:
        logger.info("=== DRY RUN — pass --apply to write ===\n")

    add_schema_fields(args.apply)
    result = await backfill(args.apply)
    await blob.aclose()
    logger.info("\n%s", json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
