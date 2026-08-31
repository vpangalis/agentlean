"""Step 3.2's `live-run` Verify — headless, against real Azure Blob.

Procedure step 3.2 "Done when": a headless script writes a gate document to
`store/projects/IMPR-2026-E9D/artifacts/define.json` and reads it back
identically.

Runs the async path (`aput`/`aget`), because that is the one the graph
travels (§1.4), and then the sync path over the same key so both dispatchers
are exercised. Reports the blob path actually written.

    cd agent-improve
    PYTHONPATH=. .venv/Scripts/python.exe scripts/verify_store.py
"""
from __future__ import annotations

import asyncio
import gc
import sys
import warnings

from backend.core.store import blob_path, get_store

CASE_ID = "IMPR-2026-E9D"
NAMESPACE = ("projects", CASE_ID, "artifacts")
KEY = "define"

# Shaped like a real approved Define gate document (§10): captured fields as
# strings (§7), plus citations, uploads and acknowledged_gaps.
GATE_DOCUMENT = {
    "phase": "define",
    "problem_statement": (
        "The customer complaint rate in the call center has risen from "
        "20 per week to 38 per week since January, against a target of 20."
    ),
    "goal_statement": "Reduce complaints to 20 per week by 2026-12-31.",
    "baseline_metric": "38 complaints per week, measured over Q1 2026",
    "citations": [
        {"source": "BB eBook", "page": "47",
         "content_summary": "Problem statement structure", "turn": 3},
    ],
    "uploads": [],
    "acknowledged_gaps": [],
    "computation_results": [],
    "_verify": "procedure step 3.2 live-run",
}


def report(label: str, ok: bool, detail: str = "") -> bool:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{'  — ' + detail if detail else ''}")
    return ok


async def main() -> int:
    store = get_store()
    path = blob_path(NAMESPACE, KEY)
    print("AzureBlobStore live-run — procedure step 3.2")
    print(f"  namespace : {NAMESPACE}")
    print(f"  key       : {KEY!r}")
    print(f"  blob path : {path}")
    print(f"  isinstance(store, BaseStore): "
          f"{__import__('langgraph.store.base', fromlist=['BaseStore']).BaseStore in type(store).__mro__}")
    print()

    ok = True

    # ── async path — the one the graph travels ────────────────────────
    await store.aput(NAMESPACE, KEY, GATE_DOCUMENT)
    item = await store.aget(NAMESPACE, KEY)
    ok &= report("aput -> aget returns an Item", item is not None)
    if item is None:
        return 1
    ok &= report("round-trips IDENTICALLY", item.value == GATE_DOCUMENT,
                 f"{len(item.value)} keys")
    ok &= report("Item.namespace preserved", item.namespace == NAMESPACE)
    ok &= report("Item.key preserved", item.key == KEY)
    ok &= report("timestamps populated from blob properties",
                 item.created_at is not None and item.updated_at is not None,
                 f"updated_at={item.updated_at}")

    # ── B1: overwrite, so a replayed write is idempotent ──────────────
    await store.aput(NAMESPACE, KEY, GATE_DOCUMENT)
    again = await store.aget(NAMESPACE, KEY)
    ok &= report("B1 replayed put is idempotent",
                 again is not None and again.value == GATE_DOCUMENT)

    # ── B2: a key never written returns None rather than raising ──────
    missing = await store.aget(NAMESPACE, "measure__does_not_exist")
    ok &= report("B2 unwritten key returns None, no raise", missing is None)

    # ── search over the namespace ─────────────────────────────────────
    found = await store.asearch(NAMESPACE, limit=10)
    ok &= report("asearch finds the written key",
                 any(i.key == KEY for i in found), f"{len(found)} item(s)")
    filtered = await store.asearch(NAMESPACE, filter={"phase": "define"}, limit=10)
    ok &= report("asearch filter= narrows",
                 any(i.key == KEY for i in filtered), f"{len(filtered)} item(s)")

    # semantic query is deliberately unsupported — S-C06's "two mechanisms,
    # no overlap" invariant
    try:
        await store.asearch(NAMESPACE, query="root cause")
        ok &= report("asearch(query=) rejected", False, "it did not raise")
    except NotImplementedError as e:
        ok &= report("asearch(query=) rejected, pointing at §24",
                     "rag_lookup_case_history" in str(e))

    # ── sync dispatcher over the same key ─────────────────────────────
    sync_item = store.get(NAMESPACE, KEY)
    ok &= report("sync get() sees the same value",
                 sync_item is not None and sync_item.value == GATE_DOCUMENT)

    print()
    print(f"  blob written: {path}")
    return 0 if ok else 1


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    rc = asyncio.run(main())
    gc.collect()

never_awaited = [str(w.message) for w in caught
                 if issubclass(w.category, RuntimeWarning)
                 and "never awaited" in str(w.message)]
unclosed = [str(w.message) for w in caught
            if "unclosed" in str(w.message).lower()
            and ("session" in str(w.message).lower()
                 or "connector" in str(w.message).lower())]

print()
print(f"  RuntimeWarning 'never awaited' : {len(never_awaited)}")
for m in never_awaited[:5]:
    print("    -", m)
print(f"  unclosed aiohttp session/connector warnings : {len(unclosed)}")
for m in unclosed[:5]:
    print("    -", m)

clean = not never_awaited and not unclosed
print(f"\nVERIFY (live-run): {'PASS' if rc == 0 and clean else 'FAIL'}")
sys.exit(0 if (rc == 0 and clean) else 1)
