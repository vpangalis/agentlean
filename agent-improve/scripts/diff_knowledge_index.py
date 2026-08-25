"""Diff a rebuilt knowledge corpus against the live improve_knowledge_index.

Step 2 of the ratified rebuild procedure — **ingest into a fresh index, diff
against live, then swap**. This is the diff.

**It exists because re-ingestion is not idempotent.** The keyword classifier
reproduces only ~58% of the live `phase_relevance` values, and the pipeline
that populated the index originally is not in the repository and cannot be
recovered. So "re-run the ingest" is a content change every time, and the only
way to swap responsibly is to see the change first.

Two things it compares, and the distinction matters:

  - a **built corpus** (`ingest_knowledge.py --dry-run --out corpus.jsonl`),
    which costs nothing and can be inspected before a single embedding call
    is spent; or
  - a **fresh Azure index**, once one has been ingested.

Both are diffed against live the same way. Read-only against every index it
touches — it creates nothing, writes nothing and deletes nothing.

Usage:
    python scripts/diff_knowledge_index.py --new-jsonl corpus.jsonl
    python scripts/diff_knowledge_index.py --new-index improve_knowledge_index_v2
    python scripts/diff_knowledge_index.py --new-jsonl corpus.jsonl --samples 5
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from backend.core.config import settings
from backend.knowledge.retriever import CROSS_PHASE_RELEVANCE

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Azure caps a single search response at 1000 documents, so a full read must
# page — and this index makes the two obvious ways of doing that unavailable:
#
#   - **`$orderby id` is rejected.** `id` is filterable but NOT sortable, and
#     Azure refuses a sort on a non-sortable field. So the usual
#     "order by key, filter past the last one seen" loop cannot run here.
#   - **`$skip` paging is unsafe.** Without an explicit sort Azure guarantees
#     no ordering across pages, so a skip-based read can miss documents and
#     return others twice — silently, which is the worst way to be wrong in a
#     tool whose whole job is to report a delta accurately.
#
# So the read partitions the KEY SPACE by filter instead of paging through a
# result set. `id` is an md5 hex digest, and range filters on a filterable
# string field are permitted — see `_hex_range`.
PAGE = 1000

HEX = "0123456789abcdef"


def _client(index_name: str) -> SearchClient:
    return SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=index_name,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )


def _hex_range(prefix: str) -> str:
    """OData filter matching exactly the ids that start with `prefix`.

    `id ge 'a' and id lt 'ag'` is exact for a hex alphabet: every md5 digest
    beginning with 'a' continues with hex characters, all of which sort below
    'g'. So the upper bound needs no knowledge of digest length and cannot
    clip a real key.
    """
    safe = prefix.replace("'", "''")
    return f"id ge '{safe}' and id lt '{safe}g'"


def read_index(index_name: str) -> dict[str, dict]:
    """Read every document's metadata fields from an index. Read-only.

    Walks the key space by hex prefix, deepening any bucket that comes back
    saturated. **Saturation is treated as "this bucket may be truncated",
    never as "this bucket has exactly PAGE documents"** — a bucket returning
    exactly the cap is indistinguishable from one that was cut off, so it is
    re-read one hex digit deeper rather than trusted.
    """
    sc = _client(index_name)
    total = sc.get_document_count()
    out: dict[str, dict] = {}
    select = ["id", "source_file", "phase_relevance", "page_number"]

    def walk(prefix: str) -> None:
        rows = list(sc.search(search_text="*", filter=_hex_range(prefix),
                              select=select, top=PAGE))
        if len(rows) >= PAGE:
            if len(prefix) >= 8:                     # 16^8 buckets — unreachable
                raise RuntimeError(
                    f"bucket {prefix!r} still saturated at depth 8; the key "
                    f"format is not the md5 hex this read assumes")
            for c in HEX:
                walk(prefix + c)
            return
        for r in rows:
            out[r["id"]] = {
                "source_file": r.get("source_file"),
                "phase_relevance": r.get("phase_relevance"),
                "page_number": r.get("page_number"),
            }

    for c in HEX:
        walk(c)

    logger.info("  read %d documents from %s (index reports %d)",
                len(out), index_name, total)
    if len(out) != total:
        logger.warning(
            "  COUNT MISMATCH — read %d, index reports %d. Either a key is "
            "not md5 hex, or the index changed mid-read.", len(out), total)
    return out


def read_jsonl(path: Path) -> dict[str, dict]:
    """Read a built corpus produced by `ingest_knowledge.py --out`."""
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            out[d["id"]] = {
                "source_file": d["metadata"]["source_file"],
                "phase_relevance": d["metadata"]["phase_relevance"],
                "page_number": d["metadata"]["page_number"],
            }
    return out


def _tally(docs: dict[str, dict], key: str) -> Counter:
    return Counter(v[key] for v in docs.values())


def _table(title: str, old: Counter, new: Counter) -> None:
    logger.info("\n%s", title)
    logger.info("  %-24s %8s %8s %9s", "value", "live", "new", "delta")
    for k in sorted(set(old) | set(new), key=lambda x: (x is None, str(x))):
        o, n = old.get(k, 0), new.get(k, 0)
        mark = "" if o == n else "   <-- changed"
        logger.info("  %-24s %8d %8d %+9d%s", k, o, n, n - o, mark)


def _by_page(docs: dict[str, dict]) -> dict[tuple, Counter]:
    """Group phase tags by (source_file, page_number)."""
    out: dict[tuple, Counter] = {}
    for v in docs.values():
        key = (v["source_file"], v["page_number"])
        out.setdefault(key, Counter())[v["phase_relevance"]] += 1
    return out


def _page_level(old: dict[str, dict], new: dict[str, dict], samples: int) -> None:
    """Compare classification per source page rather than per document id.

    **This is the comparison that still works when the ids do not line up.**
    Chunk boundaries move whenever extraction changes, so a chunk id is not a
    stable identity across a rebuild — but a *page* is. Asking "does page 53 of
    the eBook still classify the way it did?" is the question the id-level
    diff was trying to answer, and it survives a re-chunk.
    """
    o, n = _by_page(old), _by_page(new)
    shared = set(o) & set(n)
    logger.info("\nRECLASSIFICATION (by source page — survives re-chunking)")
    logger.info("  pages: live %d, new %d, in both %d", len(o), len(n), len(shared))
    if not shared:
        logger.info("  no pages in common")
        return

    # A page's dominant tag is what a phase filter effectively selects on.
    #
    # **Ties break alphabetically, and that is not cosmetic.** `most_common`
    # preserves insertion order among equal counts, so the same corpus read
    # from a JSONL and from Azure produced different dominant tags on the
    # handful of tied pages — and therefore a different headline percentage
    # on identical data. A statistic that moves when nothing moved cannot be
    # used to judge a swap.
    def dom(c: Counter) -> str:
        return min(c, key=lambda k: (-c[k], str(k)))

    moved = [(k, dom(o[k]), dom(n[k])) for k in shared if dom(o[k]) != dom(n[k])]
    logger.info("  %d of %d shared pages changed dominant phase_relevance (%.0f%%)",
                len(moved), len(shared), 100 * len(moved) / len(shared))
    for (a, b), c in Counter((a, b) for _, a, b in moved).most_common(12):
        logger.info("    %-10s -> %-10s %5d", a, b, c)
    if samples and moved:
        logger.info("  sample pages:")
        for k, a, b in sorted(moved, key=lambda x: (str(x[0][0]), x[0][1]))[:samples]:
            logger.info("    %s p%-4s %s -> %s", k[0], k[1], a, b)


def diff(old: dict[str, dict], new: dict[str, dict], samples: int) -> int:
    """Report the change. Returns a process exit code."""
    old_ids, new_ids = set(old), set(new)
    added, removed, kept = new_ids - old_ids, old_ids - new_ids, old_ids & new_ids

    logger.info("=" * 66)
    logger.info("DOCUMENT COUNTS")
    logger.info("  live %d  ->  new %d   (%+d)", len(old), len(new), len(new) - len(old))
    logger.info("  added   %6d", len(added))
    logger.info("  removed %6d", len(removed))
    logger.info("  kept    %6d  (same deterministic id)", len(kept))

    _table("SOURCE_FILE", _tally(old, "source_file"), _tally(new, "source_file"))
    _table("PHASE_RELEVANCE", _tally(old, "phase_relevance"),
           _tally(new, "phase_relevance"))

    # Reclassification among the documents that survive, which is the part a
    # count-only comparison hides entirely: totals can match while a large
    # share of individual documents changed phase.
    logger.info("\nRECLASSIFICATION (by document id)")
    if not kept:
        logger.info(
            "  NO IDS IN COMMON — id-level comparison is not meaningful here.\n"
            "  The live index was not built by this script's make_doc_id(), so "
            "its\n  keys do not collide with the ones a rebuild generates. See "
            "the page-level\n  comparison below, and the WRITE SAFETY note at "
            "the end.")
    else:
        moved = [(i, old[i]["phase_relevance"], new[i]["phase_relevance"])
                 for i in kept
                 if old[i]["phase_relevance"] != new[i]["phase_relevance"]]
        logger.info("  %d of %d kept documents changed phase_relevance (%.0f%%)",
                    len(moved), len(kept), 100 * len(moved) / len(kept))
        for (a, b), n in Counter((a, b) for _, a, b in moved).most_common(12):
            logger.info("    %-10s -> %-10s %5d", a, b, n)
        if samples and moved:
            logger.info("  sample ids:")
            for i, a, b in sorted(moved)[:samples]:
                logger.info("    %s  %s -> %s  (%s p%s)",
                            i, a, b, new[i]["source_file"], new[i]["page_number"])

    _page_level(old, new, samples)

    # The one check that is pass/fail rather than informational.
    logger.info("\n" + "=" * 66)
    problems = 0
    n_general = _tally(new, "phase_relevance").get(CROSS_PHASE_RELEVANCE, 0)
    if n_general == 0:
        logger.error(
            "FAIL  no '%s' documents. A phase filter ORs this value in, so "
            "cross-phase methodology would be unreachable from every phase.",
            CROSS_PHASE_RELEVANCE)
        problems += 1
    else:
        logger.info("OK    '%s' sentinel present on %d documents",
                    CROSS_PHASE_RELEVANCE, n_general)

    bad = {v for v in _tally(new, "phase_relevance") if v in ("all", "phase", None)}
    if bad:
        logger.error("FAIL  forbidden phase_relevance values present: %s", bad)
        problems += 1
    else:
        logger.info("OK    no 'all' / 'phase' / null phase_relevance values")

    missing = [k for k in ("source_file", "phase_relevance", "page_number")
               if any(v[k] in (None, "") for v in new.values())]
    if missing:
        logger.error(
            "FAIL  %s null or empty on some documents — the promotable "
            "metadata keys must all be populated, or $filter cannot reach "
            "them (reference §23.4)", missing)
        problems += 1
    else:
        logger.info("OK    source_file / phase_relevance / page_number all populated")

    # Not a pass/fail check — a consequence of the id comparison that decides
    # HOW the swap may be done, and that is easy to get wrong.
    logger.info("\nWRITE SAFETY")
    overlap = len(set(old) & set(new))
    if overlap == 0:
        logger.warning(
            "  NO id overlap with live. Azure Search upserts on key, so "
            "ingesting this\n  corpus INTO the live index would ADD %d "
            "documents beside the existing %d\n  (total %d) and replace "
            "nothing — the removed sources would survive.\n"
            "  => Ingest to a FRESH index and swap. Do not write to live.",
            len(new), len(old), len(old) + len(new))
    elif overlap < len(old):
        logger.warning(
            "  PARTIAL id overlap: %d of %d live documents would be replaced, "
            "%d would\n  survive untouched. A live write leaves a mixed "
            "corpus. => Fresh index and swap.",
            overlap, len(old), len(old) - overlap)
    else:
        logger.info(
            "  Every live document's id is reproduced, so a live write would "
            "replace the\n  corpus cleanly. A fresh index is still the safer "
            "route.")

    logger.info("=" * 66)
    if problems:
        logger.error("%d check(s) FAILED — do not swap.", problems)
        return 1
    logger.info("All structural checks passed. The content delta above is a "
                "judgement call, not a check.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Diff a rebuilt knowledge corpus against the live index.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--new-jsonl", type=Path,
                     help="Corpus built by ingest_knowledge.py --out")
    src.add_argument("--new-index", help="A freshly ingested Azure index name")
    ap.add_argument("--live-index",
                    default=settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
                    help="The index to treat as the baseline.")
    ap.add_argument("--samples", type=int, default=0,
                    help="Show N sample ids for reclassified documents.")
    args = ap.parse_args()

    logger.info("Reading live index %s ...", args.live_index)
    old = read_index(args.live_index)

    if args.new_jsonl:
        logger.info("Reading built corpus %s ...", args.new_jsonl)
        new = read_jsonl(args.new_jsonl)
    else:
        logger.info("Reading new index %s ...", args.new_index)
        new = read_index(args.new_index)

    return diff(old, new, args.samples)


if __name__ == "__main__":
    sys.exit(main())
