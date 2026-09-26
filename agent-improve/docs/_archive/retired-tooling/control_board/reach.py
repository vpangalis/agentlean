"""Reachability from the API routes — step 6.63, the check behind WIRED.

A symbol can EXIST and be reached by nothing: G-49 (a plan no channel read),
G-69 (fields dropped at the route), G-76 (a warning returned to no reader).
`built` proves existence; this proves the symbol is on a path from the API.

AN AST CALL-GRAPH WALK, CONSERVATIVE BY DESIGN
    Nodes are module-level functions and class methods under `backend/`.
    Edges are every NAME a body mentions that resolves to one — a call, or a
    reference passed along (`builder.add_node("executor", partial(executor, …))`
    names `executor` without calling it). Referencing a CLASS reaches all its
    methods: middleware hooks are called by the framework, never by us.
    The walk starts at `app.py` and every function decorated `@router.*` in
    `gateway/routes.py`. Attribute calls on objects (`x.method()`) are not
    resolved — so a symbol is reported reachable only on a path this can SEE,
    and an unreachable verdict means no visible path exists.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
BACKEND = PROJECT / "backend"


def _modname(path: Path) -> str:
    rel = path.relative_to(PROJECT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _index(root: Path = BACKEND) -> dict[str, dict]:
    mods: dict[str, dict] = {}
    for p in root.rglob("*.py"):
        if "tests" in p.parts or "__pycache__" in p.parts:
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        mods[_modname(p)] = {"tree": tree, "defs": {}, "aliases": {}}
    for name, m in mods.items():
        for node in ast.walk(m["tree"]):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                for a in node.names:
                    m["aliases"][a.asname or a.name] = (node.module, a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    m["aliases"][a.asname or a.name.split(".")[0]] = (a.name, None)
        for node in m["tree"].body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                m["defs"][node.name] = node
            elif isinstance(node, ast.ClassDef):
                m["defs"][node.name] = node
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m["defs"][f"{node.name}.{sub.name}"] = sub
    return mods


def _resolve(mods: dict, mod: str, name: str) -> tuple[str, str] | None:
    m = mods.get(mod)
    if m is None:
        return None
    if name in m["defs"]:
        return (mod, name)
    alias = m["aliases"].get(name)
    if alias:
        target_mod, target = alias
        if target is None:
            return None
        if f"{target_mod}.{target}" in mods:          # `from pkg import module`
            return None
        return _resolve(mods, target_mod, target) if target_mod in mods else None
    return None


def _edges(mods: dict, mod: str, name: str) -> set[tuple[str, str]]:
    node = mods[mod]["defs"][name]
    out: set[tuple[str, str]] = set()
    if isinstance(node, ast.ClassDef):                # a class reaches its methods
        return {(mod, k) for k in mods[mod]["defs"] if k.startswith(name + ".")}
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            r = _resolve(mods, mod, n.id)
            if r:
                out.add(r)
        elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
            alias = mods[mod]["aliases"].get(n.value.id)
            if alias:
                target_mod = alias[0] if alias[1] is None else f"{alias[0]}.{alias[1]}"
                if target_mod in mods:
                    r = _resolve(mods, target_mod, n.attr)
                    if r:
                        out.add(r)
    for n in ast.walk(node):                           # a referenced class, via a call
        if isinstance(n, ast.Name):
            r = _resolve(mods, mod, n.id)
            if r and isinstance(mods[r[0]]["defs"][r[1]], ast.ClassDef):
                out |= {(r[0], k) for k in mods[r[0]]["defs"] if k.startswith(r[1] + ".")}
    # A DYNAMIC import — `importlib.import_module(f"backend.phases.{phase}.nodes")`
    # (`subgraph_common.phase_nodes`) — names no symbol an AST can follow. The
    # f-string is the pattern: every module matching it is loaded, and its
    # functions are what the builder registers as graph nodes.
    for n in ast.walk(node):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "import_module" and n.args
                and isinstance(n.args[0], (ast.JoinedStr, ast.Constant))):
            arg = n.args[0]
            pattern = (re.escape(str(arg.value)) if isinstance(arg, ast.Constant) else "".join(
                re.escape(str(v.value)) if isinstance(v, ast.Constant) else r"[^.]+"
                for v in arg.values))
            for other in mods:
                if re.fullmatch(pattern, other):
                    out |= {(other, k) for k in mods[other]["defs"]}
    return out


def entry_points(mods: dict) -> set[tuple[str, str]]:
    starts: set[tuple[str, str]] = set()
    routes = mods.get("backend.gateway.routes")
    if routes:
        for k, node in routes["defs"].items():
            decs = getattr(node, "decorator_list", [])
            if any(isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                   and isinstance(d.func.value, ast.Name) and d.func.value.id == "router"
                   for d in decs):
                starts.add(("backend.gateway.routes", k))
    app = mods.get("backend.app")
    if app:
        starts |= {("backend.app", k) for k in app["defs"]}
    return starts


def reachable(mods: dict | None = None) -> set[tuple[str, str]]:
    mods = mods or _index()
    seen: set[tuple[str, str]] = set()
    todo = list(entry_points(mods))
    while todo:
        cur = todo.pop()
        if cur in seen or cur[1] not in mods.get(cur[0], {}).get("defs", {}):
            continue
        seen.add(cur)
        todo.extend(_edges(mods, *cur) - seen)
    return seen


def unreachable(symbols: list[str], mods: dict | None = None) -> list[str]:
    """Each `module::name` that exists but has no visible path from the routes;
    a symbol that does not exist is reported as such."""
    mods = mods or _index()
    seen = reachable(mods)
    out = []
    for s in symbols:
        mod, _, name = s.partition("::")
        if name not in mods.get(mod, {}).get("defs", {}):
            out.append(f"{s} does not exist")
        elif (mod, name) not in seen:
            out.append(f"{s} exists and is not reachable from app.py's routes")
    return out


if __name__ == "__main__":
    import sys
    bad = unreachable(sys.argv[1:])
    print("\n".join(bad) or "all reachable")
    sys.exit(1 if bad else 0)
