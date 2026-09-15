"""Step 3.2's `live-run` Verify — headless, against real Azure Blob.

Procedure step 3.2 "Done when": a headless script writes a gate document and
reads it back identically. **It writes to
`store/projects/{case_id}/_verification/store_roundtrip.json`, NOT to the gate
path** — see below.

IT DOES NOT WRITE TO THE GATE PATH, AND THAT IS DELIBERATE
-----------------------------------------------------------
This wrote `artifacts/define` until 2026-09-15. Under a hard-coded case that
was merely untidy; once the case is resolved from the registry it is
**writing a document that reads as a passed Define gate into a live case**.
Step 7.3's Done-when has gate approval write exactly that path, so a leftover
from this script is indistinguishable from the gate's own output.

**Delete-on-exit was considered and rejected**: a crash between the write and
the delete leaves the file there, and an existing real `define.json` would be
overwritten and then removed. A namespace this script owns has neither failure
mode.

**The round-trip loses nothing by moving.** Every assertion below exercises
`blob_path()` construction, the aput/aget dispatchers, namespace and key
preservation, blob-property timestamps, replay idempotence, the missing-key
contract, `asearch` with and without `filter=`, the `query=` rejection and the
sync dispatcher. **None of them reads the key name or the `artifacts` segment.**
The one that mentions "define" filters on document CONTENT (`filter={"phase":
"define"}`), not on path. The namespace stays under `projects/{case_id}/` so the
§9 path shape the Store is actually about is still the shape under test.

Runs the async path (`aput`/`aget`), because that is the one the graph
travels (§1.4), and then the sync path over the same key so both dispatchers
are exercised. Reports the blob path actually written.

    cd agent-improve
    PYTHONPATH=. .venv/Scripts/python.exe scripts/verify_store.py

THE CASE IS READ FROM THE REGISTRY, NEVER HARD-CODED — WATCH 22
----------------------------------------------------------------
**This script named `IMPR-2026-E9D` in a module constant until 2026-09-15, and
that is the exact defect WATCH 22 registers**: *"any later step whose Verify
method is `live-run` or `azure-query`"* against a hard-coded case inherits that
case's fate. E9D was `complete` and returned 409; step 7.3's Done-when was
corrected on 2026-09-07 for precisely this, to *"a case the registry shows in
`define`"*, and step 4.2's was corrected before it.

**A hard-coded id fails in the worse direction here.** `aput` CREATES the blob
it writes, so this script never needed the case to exist — after the case was
deleted it would have silently recreated `store/projects/{deleted_id}/…`,
resurrecting storage for a case nothing else knows about. It would have
reported PASS while doing it. Reading the registry makes the dependency real:
no coachable case, no run, and the script says so.
"""
from __future__ import annotations

import asyncio
import gc
import sys
import warnings

from backend.storage import blob
from backend.core.store import blob_path, get_store

#: The five wired phases. `complete` is excluded deliberately — a completed
#: case has no coachable phase and `/ask` returns 409 on it by design, which is
#: what made E9D the wrong target rather than merely a stale one.
COACHABLE_PHASES = ("define", "measure", "analyse", "improve", "control")

#: The namespace segment and key this script owns. **Not `artifacts`/`define`** —
#: that is the gate's path (§33.2, step 7.3), and nothing but the gate writes it.
VERIFY_SEGMENT = "_verification"
KEY = "store_roundtrip"

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


async def coachable_case() -> str:
    """The first registry case in a coachable phase, read at run time.

    Raises rather than falling back to a default. **A default is what WATCH 22
    is about** — it would let this script pass against a case the registry does
    not list, which is the condition the lookup exists to detect.

    **Closes the blob module's cached client before returning**, and that is not
    housekeeping: this script FAILS on an unclosed aiohttp session warning (see
    the `unclosed` check at the foot of the file). `load_registry` opens the
    module-level client `storage/blob.py` caches deliberately, so the one place
    that opens it is the one place that closes it. `AzureBlobStore` needs no
    such call — it opens and closes per operation by design (§10).
    """
    try:
        registry = await blob.load_registry()
    finally:
        await blob.aclose()
    for entry in registry.cases:
        if entry.current_phase in COACHABLE_PHASES:
            return entry.case_id
    listed = ", ".join(
        f"{e.case_id}={e.current_phase}" for e in registry.cases
    ) or "(registry is empty)"
    raise SystemExit(
        "No case in a coachable phase — this live-run cannot be verified.\n"
        f"  registry lists: {listed}\n"
        f"  coachable phases: {', '.join(COACHABLE_PHASES)}\n"
        "Create a case (POST /cases) and re-run. Do NOT hard-code an id here "
        "(WATCH 22)."
    )


async def main() -> int:
    store = get_store()
    case_id = await coachable_case()
    namespace = ("projects", case_id, VERIFY_SEGMENT)
    path = blob_path(namespace, KEY)
    print("AzureBlobStore live-run — procedure step 3.2")
    print(f"  case      : {case_id}   (from registry.json, not hard-coded)")
    print(f"  namespace : {namespace}")
    print(f"  key       : {KEY!r}")
    print(f"  blob path : {path}")
    print(f"  isinstance(store, BaseStore): "
          f"{__import__('langgraph.store.base', fromlist=['BaseStore']).BaseStore in type(store).__mro__}")
    print()

    ok = True

    # ── async path — the one the graph travels ────────────────────────
    await store.aput(namespace, KEY, GATE_DOCUMENT)
    item = await store.aget(namespace, KEY)
    ok &= report("aput -> aget returns an Item", item is not None)
    if item is None:
        return 1
    ok &= report("round-trips IDENTICALLY", item.value == GATE_DOCUMENT,
                 f"{len(item.value)} keys")
    ok &= report("Item.namespace preserved", item.namespace == namespace)
    ok &= report("Item.key preserved", item.key == KEY)
    ok &= report("timestamps populated from blob properties",
                 item.created_at is not None and item.updated_at is not None,
                 f"updated_at={item.updated_at}")

    # ── B1: overwrite, so a replayed write is idempotent ──────────────
    await store.aput(namespace, KEY, GATE_DOCUMENT)
    again = await store.aget(namespace, KEY)
    ok &= report("B1 replayed put is idempotent",
                 again is not None and again.value == GATE_DOCUMENT)

    # ── B2: a key never written returns None rather than raising ──────
    missing = await store.aget(namespace, "measure__does_not_exist")
    ok &= report("B2 unwritten key returns None, no raise", missing is None)

    # ── search over the namespace ─────────────────────────────────────
    found = await store.asearch(namespace, limit=10)
    ok &= report("asearch finds the written key",
                 any(i.key == KEY for i in found), f"{len(found)} item(s)")
    filtered = await store.asearch(namespace, filter={"phase": "define"}, limit=10)
    ok &= report("asearch filter= narrows",
                 any(i.key == KEY for i in filtered), f"{len(filtered)} item(s)")

    # semantic query is deliberately unsupported — S-C06's "two mechanisms,
    # no overlap" invariant
    try:
        await store.asearch(namespace, query="root cause")
        ok &= report("asearch(query=) rejected", False, "it did not raise")
    except NotImplementedError as e:
        ok &= report("asearch(query=) rejected, pointing at §24",
                     "rag_lookup_case_history" in str(e))

    # ── sync dispatcher over the same key ─────────────────────────────
    sync_item = store.get(namespace, KEY)
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
