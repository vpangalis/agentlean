"""The wiring check — brief Part F6 (founder, 2026-09-27). Reads source with `ast`, runs nothing.

A component that exists but is not wired has been the most repeated failure of the refactor
(declared-but-unwired, at least seven times; G-112 the latest: the output mappers had no
production caller). Three checks:

  1  every node, middleware, mapper, tool and route ARCHITECTURE.md §3 names has a PRODUCTION
     caller — reached from `core/graph.py`, `phases/nodes_common.py::_build_executor`, a route
     or `app.py` — not only a test caller
  2  every route with a state-changing verb (POST, PUT, PATCH, DELETE) reaches the compiled
     graph or a named storage function
  3  every feature test is end to end: a feature test that calls a node or a mapper directly
     is flagged; one that neither drives the graph nor the API is listed apart

Reachability is static and by name: module-level definitions, resolved through each module's
imports. A call built from a string (`getattr`, `importlib`) is invisible to it — so the
check WARNS (founder ruling: it becomes a refusal after the first findings are reviewed).

    python tools/architecture/wiring.py            # the findings
    python tools/architecture/wiring.py --json     # as JSON (the board reads `findings()`)
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
BACKEND = PROJECT / "backend"
ARCH = PROJECT / "ARCHITECTURE.md"
FEATURES = PROJECT / "docs" / "define_features.json"
PHASES = ("define", "measure", "analyse", "improve", "control")
GRAPH_CALLS = frozenset({"ainvoke", "invoke", "astream", "stream", "aupdate_state", "update_state",
                         "get_graph", "build_supervisor"})
DRIVES = GRAPH_CALLS | {"TestClient", "AsyncClient", "post", "get", "delete"}
_MAPPER = re.compile(r"^\w+_(?:input|output)_mapper$")

Key = tuple[str, str]          # (module, name)


def _module(path: Path) -> str:
    return ".".join(path.relative_to(PROJECT).with_suffix("").parts)


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return None


class _Index:
    """Every module-level definition of backend/ (tests excluded) and what each refers to."""

    def __init__(self) -> None:
        self.defs: dict[Key, ast.AST] = {}
        self.refs: dict[Key, set[Key]] = {}
        self.routes: dict[Key, tuple[str, str]] = {}          # handler -> (VERB, path)
        self.modules: set[str] = set()
        for path in sorted(BACKEND.rglob("*.py")):
            if "tests" in path.parts or "__pycache__" in path.parts:
                continue
            tree = _parse(path)
            if tree is None:
                continue
            mod = _module(path)
            self.modules.add(mod)
            imports = self._imports(tree, mod)
            local = {n for s in tree.body for n in _names_defined(s)}
            for stmt in tree.body:
                names = _names_defined(stmt) or ["<module>"]
                for name in names:
                    key = (mod, name)
                    self.defs[key] = stmt
                    self.refs.setdefault(key, set()).update(self._resolve(stmt, mod, imports, local))
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for d in stmt.decorator_list:
                        if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                                and d.func.attr in ("get", "post", "put", "patch", "delete")
                                and d.args and isinstance(d.args[0], ast.Constant)):
                            self.routes[(mod, stmt.name)] = (d.func.attr.upper(), str(d.args[0].value))

    @staticmethod
    def _imports(tree: ast.Module, mod: str) -> dict[str, tuple[str, str | None]]:
        out: dict[str, tuple[str, str | None]] = {}
        pkg = mod.rsplit(".", 1)[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    parts = pkg.split(".")
                    base = ".".join(parts[: len(parts) - node.level + 1] + ([base] if base else []))
                for a in node.names:
                    out[a.asname or a.name] = (base, a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    out[a.asname or a.name.split(".")[0]] = (a.name if a.asname else a.name.split(".")[0], None)
        return out

    @staticmethod
    def _resolve(stmt: ast.AST, mod: str, imports: dict, local: set[str]) -> set[Key]:
        out: set[Key] = set()
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name):
                if node.id in local:
                    out.add((mod, node.id))
                elif node.id in imports:
                    src, name = imports[node.id]
                    out.add((src, name) if name else (src, "<module>"))
                else:
                    out.add(("<ext>", node.id))
            elif isinstance(node, ast.Attribute):
                out.add(("<attr>", node.attr))
                if isinstance(node.value, ast.Name) and node.value.id in imports:
                    src, name = imports[node.value.id]
                    target = f"{src}.{name}" if name else src
                    out.add((target, node.attr))
        return out

    def reach(self, roots: set[Key]) -> set[Key]:
        seen: set[Key] = set()
        stack = list(roots)
        while stack:
            k = stack.pop()
            if k in seen:
                continue
            seen.add(k)
            stack.extend(r for r in self.refs.get(k, ()) if r in self.defs and r not in seen)
            if k[1] == "<module>" or k in self.defs:
                stack.extend((k[0], n) for (m, n) in self.defs if m == k[0] and n == "<module>")
        return seen

    def attrs(self, keys: set[Key]) -> set[str]:
        return {n for k in keys for (m, n) in self.refs.get(k, ()) if m in ("<attr>", "<ext>")} | \
               {n for k in keys for (m, n) in self.refs.get(k, ())}


def _names_defined(stmt: ast.stmt) -> list[str]:
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [stmt.name]
    if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
        targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
        return [t.id for t in targets if isinstance(t, ast.Name)]
    return []


# ── what ARCHITECTURE.md §3 names ───────────────────────────────────────────


def named(text: str | None = None) -> dict[str, list[str]]:
    """{kind: [names]} — the nodes (§3.2), middleware (§3.3), mappers ({phase}/mappers.py),
    tools (§3.5, §3.6) and routes (§3.9) the design names."""
    text = ARCH.read_text(encoding="utf-8") if text is None else text
    s, e = text.find("\n## 3."), text.find("\n## 4.")
    sec = text[s:e]

    def sub(title: str) -> str:
        a = sec.find(f"\n### {title}")
        b = sec.find("\n### ", a + 5)
        return sec[a:b if b > 0 else None] if a >= 0 else ""

    nodes = re.findall(r"^\| `(\w+)` \|", sub("3.2"), re.M)
    middleware = re.findall(r"^\*\*\d+ · `(\w+)`\*\*", sub("3.3"), re.M)
    tools = sorted(set(re.findall(r"`((?:rag_lookup|propose|load)_\w+)", sub("3.5") + sub("3.6"))))
    routes = []
    for line in sub("3.9").splitlines():
        if line.startswith("| `"):
            routes += re.findall(r"`(GET|POST|PUT|PATCH|DELETE) ([^`]+)`", line.split("|")[1])
    mappers = [f"{p}_{io}_mapper" for p in PHASES for io in ("input", "output")] \
        if "{phase}/mappers.py" in sec else []
    return {"node": nodes, "middleware": middleware, "mapper": mappers, "tool": tools,
            "route": [f"{v} {p}" for v, p in routes]}


# ── the three checks ────────────────────────────────────────────────────────


def _roots(ix: _Index) -> set[Key]:
    roots = {k for k in ix.defs if k[0] in ("backend.core.graph", "backend.app")}
    roots |= {k for k in ix.defs if k[1] == "_build_executor"}
    roots |= set(ix.routes)
    return roots


def check_callers(ix: _Index, names: dict[str, list[str]]) -> list[dict]:
    reach = ix.reach(_roots(ix))
    reached_names = {n for (_, n) in reach} | ix.attrs(reach)
    out = []
    for kind in ("node", "middleware", "mapper", "tool"):
        for name in names[kind]:
            defined = [k for k in ix.defs if k[1] == name]
            if defined and not any(k in reach for k in defined) and name not in ix.attrs(reach):
                out.append({"check": 1, "kind": kind, "name": name,
                            "where": ", ".join(f"{m}.{n}" for m, n in defined),
                            "finding": f"{kind} `{name}` has no production caller (reached only from tests, or not at all)"})
            elif not defined and name not in reached_names:
                out.append({"check": 1, "kind": kind, "name": name, "where": "—",
                            "finding": f"{kind} `{name}` is named in §3 and neither defined in backend/ nor referenced"})
    have = {f"{v} {p}" for v, p in ix.routes.values()}
    for r in names["route"]:
        norm = re.sub(r"\{[^}]+\}", "{}", r)
        if norm not in {re.sub(r"\{[^}]+\}", "{}", h) for h in have}:
            out.append({"check": 1, "kind": "route", "name": r, "where": "gateway/routes.py",
                        "finding": f"route `{r}` is named in §3.9 and has no handler"})
    return out


def check_routes(ix: _Index) -> list[dict]:
    storage = {k for k in ix.defs if k[0].startswith(("backend.storage.", "backend.core.store",
                                                       "backend.core.checkpointer"))}
    out = []
    for handler, (verb, path) in sorted(ix.routes.items(), key=lambda x: x[1][1]):
        if verb == "GET":
            continue
        closure = ix.reach({handler})
        if closure & storage or ix.attrs(closure) & GRAPH_CALLS:
            continue
        out.append({"check": 2, "kind": "route", "name": f"{verb} {path}", "where": f"{handler[0]}.{handler[1]}",
                    "finding": f"`{verb} {path}` reaches neither the compiled graph nor a storage function "
                               "(if it changes nothing, it is read-only and a GET would say so)"})
    return out


def _test_defs(path: Path, seen: set[Path] | None = None) -> dict[str, ast.AST]:
    """The functions a test module can reach by name: its own, and those it imports from
    other test modules (helpers and fixtures), transitively."""
    seen = set() if seen is None else seen
    if path in seen:
        return {}
    seen.add(path)
    tree = _parse(path)
    if tree is None:
        return {}
    defs: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("backend.tests."):
            other = PROJECT / (node.module.replace(".", "/") + ".py")  # type: ignore[union-attr]
            got = _test_defs(other, seen)
            defs.update({(a.asname or a.name): got[a.name] for a in node.names if a.name in got})
    defs.update({s.name: s for s in tree.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))})
    return defs


def _test_calls(path: Path, func: str) -> tuple[set[str], bool] | None:
    """What the test calls, following its helpers and its fixtures (parameters) by name."""
    defs = _test_defs(path)
    if func not in defs:
        return None
    seen: set[str] = set()
    stack, calls = [func], set()
    while stack:
        f = stack.pop()
        if f in seen or f not in defs:
            continue
        seen.add(f)
        fn = defs[f]
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack.extend(a.arg for a in fn.args.args)
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                n = node.func.id if isinstance(node.func, ast.Name) else                     node.func.attr if isinstance(node.func, ast.Attribute) else None
                if n:
                    calls.add(n)
                    if n in defs:
                        stack.append(n)
    return calls, "_not_written" in calls


def check_feature_tests(names: dict[str, list[str]], feats: list[dict] | None = None) -> list[dict]:
    feats = json.loads(FEATURES.read_text(encoding="utf-8"))["features"] if feats is None else feats
    direct = set(names["node"]) | {n for n in names["mapper"]}
    out = []
    for f in feats:
        file, _, func = f["test"].partition("::")
        got = _test_calls(PROJECT / file, func)
        if got is None:
            continue
        calls, stub = got
        if stub:
            continue
        hit = sorted(c for c in calls if c in direct or _MAPPER.match(c))
        if hit:
            out.append({"check": 3, "kind": "feature test", "name": f["id"], "where": f["test"],
                        "finding": f"{f['id']}'s test calls {', '.join(hit)} directly instead of driving the compiled graph or the API"})
        elif not calls & DRIVES:
            out.append({"check": 3, "kind": "feature test", "name": f["id"], "where": f["test"],
                        "finding": f"{f['id']}'s test drives neither the compiled graph nor the API (a structural test)"})
    return out


def findings() -> list[dict]:
    ix = _Index()
    names = named()
    return check_callers(ix, names) + check_routes(ix) + check_feature_tests(names)


def main(argv: list[str]) -> int:
    got = findings()
    if "--json" in argv:
        print(json.dumps(got, indent=1, ensure_ascii=False))
        return 0
    for g in got:
        print(f"  [wiring {g['check']}] {g['finding']}  ({g['where']})")
    print(f"  [wiring] {len(got)} finding(s) — warnings (brief Part F6; a refusal after the founder's review)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
