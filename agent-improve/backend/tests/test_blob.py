"""`storage/blob.py` — the invariants procedure step 3.5 established.

Two failure modes are pinned here, both of which the step exists to close:

  1. a class reappearing in a file §54 says holds module-level functions only;
  2. a synchronous blob call returning to a path that runs on the event loop.

The behavioural surface is covered by the step's `live-run` verify against the
real container, not by mocks — these are structural guards, and they are cheap
enough to run on every commit.
"""
from __future__ import annotations

import ast
import asyncio
import inspect
import pathlib

import pytest

from backend.storage import blob

BLOB_SRC = pathlib.Path(blob.__file__)
ROUTES_SRC = BLOB_SRC.parent.parent / "gateway" / "routes.py"

#: Coroutines on `azure.storage.blob.aio`. `get_blob_client` is excluded on
#: purpose — it is a plain factory, and awaiting it would be the error.
ASYNC_SDK_METHODS = {
    "upload_blob", "download_blob", "readall", "get_blob_properties",
    "delete_blob", "list_blobs",
}

#: Everything that performs blob I/O. `case_path` is excluded — pure string
#: construction, correctly left synchronous.
IO_FUNCTIONS = [
    "load_case", "save_case", "create_case", "write_phase_gate",
    "append_turn", "load_registry", "save_registry", "register_case",
    "upload_file", "aclose",
]


def _tree(path: pathlib.Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


# ── §54: module-level functions only ──────────────────────────────────────

def test_blob_module_defines_no_class() -> None:
    """`ImproveBlobClient` is gone and no class replaced it (§54, CLAUDE.md §2)."""
    classes = [n.name for n in _tree(BLOB_SRC).body if isinstance(n, ast.ClassDef)]
    assert classes == [], (
        f"storage/blob.py holds module-level functions ONLY (§54); found {classes}"
    )


def test_no_import_of_improve_blob_client_anywhere() -> None:
    """The old singleton is not resurrected under its old name."""
    backend = BLOB_SRC.parent.parent
    offenders = []
    for py in backend.rglob("*.py"):
        if py.name == "test_blob.py":
            continue
        src = py.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.ImportFrom) and node.module and \
                    node.module.endswith("storage.blob"):
                names = {a.name for a in node.names}
                bad = names & {"ImproveBlobClient", "blob_client"}
                if bad:
                    offenders.append(f"{py.name}: {sorted(bad)}")
    assert offenders == [], offenders


# ── §1.4 / §49: aio, and nothing that blocks the loop ─────────────────────

@pytest.mark.parametrize("name", IO_FUNCTIONS)
def test_every_io_function_is_a_coroutine(name: str) -> None:
    fn = getattr(blob, name)
    assert inspect.iscoroutinefunction(fn), (
        f"blob.{name}() performs I/O and must be async (§1.4, §49)"
    )


def test_case_path_stays_synchronous() -> None:
    """Pure path construction — making it async would be noise."""
    assert not inspect.iscoroutinefunction(blob.case_path)
    assert blob.case_path("IMPR-2026-E9D") == "cases/case_IMPR-2026-E9D.json"


def test_module_imports_no_synchronous_blob_client() -> None:
    """Only `ContentSettings` — a plain model — may come from the sync namespace."""
    for node in ast.walk(_tree(BLOB_SRC)):
        if isinstance(node, ast.ImportFrom) and node.module == "azure.storage.blob":
            names = {a.name for a in node.names}
            assert names <= {"ContentSettings"}, (
                f"synchronous blob client imported: {sorted(names - {'ContentSettings'})}"
            )


@pytest.mark.parametrize("src", [BLOB_SRC, ROUTES_SRC], ids=["blob", "routes"])
def test_no_unawaited_async_sdk_call(src: pathlib.Path) -> None:
    """Every aio SDK call is awaited — the event-loop block flagged at 2.5."""
    tree = _tree(src)
    awaited = {
        id(n.value) for n in ast.walk(tree)
        if isinstance(n, ast.Await) and isinstance(n.value, ast.Call)
    } | {
        id(n.iter) for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFor) and isinstance(n.iter, ast.Call)
    }
    unawaited = [
        f"{src.name}:{n.lineno} {n.func.attr}()"
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr in ASYNC_SDK_METHODS and id(n) not in awaited
    ]
    assert unawaited == [], unawaited


def test_every_blob_call_in_routes_is_awaited() -> None:
    """No `blob.<fn>(...)` in routes.py is left as a bare coroutine."""
    tree = _tree(ROUTES_SRC)
    awaited = {
        id(n.value) for n in ast.walk(tree)
        if isinstance(n, ast.Await) and isinstance(n.value, ast.Call)
    }
    io = set(IO_FUNCTIONS)
    unawaited = [
        f"routes.py:{n.lineno} blob.{n.func.attr}()"
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name) and n.func.value.id == "blob"
        and n.func.attr in io and id(n) not in awaited
    ]
    assert unawaited == [], unawaited


# ── §10: the concern boundary ─────────────────────────────────────────────

def test_blob_module_does_not_touch_the_store() -> None:
    """S-C08 stays distinct from S-C06 — 3.5 must not fold into AzureBlobStore."""
    src = BLOB_SRC.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.endswith("core.store"), (
                "storage/blob.py must not import core.store — §10 keeps the "
                "case-record and artifact-store concerns separate"
            )
        if isinstance(node, ast.Name):
            assert node.id != "AzureBlobStore", "S-C08 must not wrap S-C06"


def test_owned_paths_are_the_three_in_the_spec() -> None:
    """§10's physical layout: these prefixes and no others."""
    assert blob.case_path("X") == "cases/case_X.json"
    assert blob.REGISTRY_BLOB_PATH == "registry.json"
    src = BLOB_SRC.read_text(encoding="utf-8")
    assert 'f"uploads/{case_id}/{filename}"' in src


# ── the cached-client lifecycle ───────────────────────────────────────────

def test_container_requires_a_running_loop() -> None:
    """The cache is loop-bound; there is no client to hand out without one."""
    with pytest.raises(RuntimeError):
        blob._container()


def test_aclose_is_idempotent_and_safe_when_never_opened() -> None:
    """Shutdown must not depend on a client having been built."""
    async def go() -> None:
        await blob.aclose()
        await blob.aclose()

    asyncio.run(go())
    assert blob._client is None
