"""THE SHAPE OF IT — the architecture diagram, read from the code. Step 6.63.

Founder ruling 2026-09-25: *"Every number, label, diagram element and status
colour on the board is derived from the tree, never typed by hand."* Until
6.63 the diagram was `system_view.py` and `arch_view.py`: typed text, with a
frozen caption ("47 of 90 · 22 Sep 2026") and typed provenance claims
("VERIFIED by me", "RELAYED"). Both are deleted; this reads the code itself.

WHAT EACH ELEMENT IS READ FROM
    containers, nodes, edges   the REAL compiled graphs — the turn graph the
                               route invokes (`get_graph`, persistence off) and
                               the phase subgraph (`build_phase_subgraph`)
    the middleware boxes       the `middleware=[...]` list of the
                               `create_agent` call in `_build_executor`, by AST,
                               in its real order; each box's hooks from the
                               class itself; "always on" when the list element
                               is unconditional in the code
    the skills label           a PROBE: the real `DMAICSkillsMiddleware` is
                               run on a request, and the label says what it
                               actually delivered
    the coach's input sections a PROBE: the real position-1 and position-2
                               wraps are run in their real order over the real
                               system prompt; each section is named from the
                               text the code composed, and marked "when
                               present" if an empty case leaves it out
    the tools                  `_executor_tools` for the phase, plus the
                               tools a middleware registers

Needs the project's venv (it imports `backend`). No model is called and no
trace is sent: tracing is switched off before `backend` is imported, and the
probes call middleware methods directly, never a runnable.
"""
from __future__ import annotations

import ast
import inspect
import os
import re
import sys
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[2]
NODES_COMMON = PROJECT / "backend" / "phases" / "nodes_common.py"

HOOKS = ("before_agent", "before_model", "wrap_model_call", "after_model",
         "after_agent", "wrap_tool_call")


def _tracing_off() -> None:
    for name in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING_V2",
                 "LANGSMITH_TRACING", "LANGCHAIN_TRACING"):
        os.environ[name] = "false"
    if str(PROJECT) not in sys.path:
        sys.path.insert(0, str(PROJECT))
    from langsmith.run_trees import configure
    configure(enabled=False)


# ══ graphs ═══════════════════════════════════════════════════════════════════


def _graph(g: Any) -> dict:
    nodes = [n for n in g.nodes if n not in ("__start__", "__end__")]
    edges = [{"from": e.source, "to": e.target, "conditional": bool(e.conditional)}
             for e in g.edges]
    return {"nodes": nodes, "edges": edges}


def turn_graph(phase: str) -> dict:
    """The graph `POST /ask` invokes — compiled with persistence OFF, so
    reading its shape opens no connection."""
    from backend.core import graph as graph_mod
    real = graph_mod._persistence
    graph_mod._persistence = lambda: (None, None)
    try:
        return _graph(graph_mod.get_graph.__wrapped__(phase).get_graph())
    finally:
        graph_mod._persistence = real


def phase_graph(phase: str) -> dict:
    from backend.phases.subgraph_common import build_phase_subgraph
    return _graph(build_phase_subgraph(phase).get_graph())


# ══ the middleware list, by AST, and each class's hooks ══════════════════════


def _executor_call() -> tuple[ast.FunctionDef, ast.Call]:
    tree = ast.parse(NODES_COMMON.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_build_executor")
    call = next(n for n in ast.walk(fn) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == "create_agent")
    return fn, call


def _hooks(cls: type) -> list[str]:
    from langchain.agents.middleware import AgentMiddleware
    out = []
    for h in HOOKS:
        for name in (h, "a" + h):
            impl = getattr(cls, name, None)
            base = getattr(AgentMiddleware, name, None)
            if impl is not None and impl is not base and h not in out:
                out.append(h)
    return out


def middleware() -> list[dict]:
    """The boxes, in the order the code declares them."""
    import backend.phases.nodes_common as nc
    fn, call = _executor_call()
    assigned = {t.id: n.value for n in ast.walk(fn) if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name)}
    lst = next(k.value for k in call.keywords if k.arg == "middleware")
    assert isinstance(lst, ast.List), "the middleware argument is not a literal list"
    boxes = []
    for pos, el in enumerate(lst.elts, start=1):
        always = isinstance(el, (ast.Call, ast.Name))
        node = assigned.get(el.id) if isinstance(el, ast.Name) else el
        if not isinstance(node, ast.Call):
            raise ValueError(f"middleware position {pos} is not a constructor call")
        cls_name = ast.unparse(node.func)
        cls = getattr(nc, cls_name)
        config = []
        for k in node.keywords:
            src = ast.unparse(k.value)
            val = getattr(nc, src, None) if re.fullmatch(r"[A-Z_][A-Z0-9_]*", src) else None
            config.append(f"{k.arg}={val!r}" if val is not None and not callable(val) else f"{k.arg}={src}")
        boxes.append({"position": pos, "class": cls_name, "hooks": _hooks(cls),
                      "config": config, "always_on": always,
                      "on": "always on" if always else "conditional",
                      "source": f"backend/phases/nodes_common.py:{el.lineno}"})
    return boxes


# ══ probes — run the real code, report what it did ═══════════════════════════


class _Req:
    """The one attribute and one method the two wraps use of a ModelRequest."""

    def __init__(self, system_message: Any) -> None:
        self.system_message = system_message

    def override(self, **kw: Any) -> "_Req":
        return _Req(kw.get("system_message", self.system_message))


def _texts(req: _Req) -> list[str]:
    return [b.get("text", "") for b in req.system_message.content_blocks]


def skills(phase: str) -> dict:
    """What `DMAICSkillsMiddleware` delivers, by running it."""
    from langchain_core.messages import SystemMessage
    from backend.middleware.skills import DMAICSkillsMiddleware, SKILL_DIRS, instructions
    delivered: list[dict] = []
    mw = DMAICSkillsMiddleware(phase, on_delivery=delivered.append)
    mw.before_agent({}, None)
    first = _texts(mw._append_catalogue(_Req(SystemMessage(content="P"))))
    second = _texts(mw._append_catalogue(_Req(SystemMessage(content="P"))))
    script = instructions(phase)
    every_call = script in first and script in second
    label = (f"{SKILL_DIRS[phase]} SKILL.md ({len(script):,} chars) on every model call, "
             f"then the catalogue of {len(SKILL_DIRS)} skill descriptions"
             if every_call else
             f"{SKILL_DIRS[phase]} SKILL.md NOT delivered by the wrap — "
             f"only on a load_skill call")
    return {"label": label, "every_call": every_call, "script_chars": len(script),
            "deliveries_in_two_calls": len(delivered),
            "tools": [t.name for t in mw.tools],
            "source": "backend/middleware/skills.py::DMAICSkillsMiddleware._append_catalogue"}


_HEAD = re.compile(r"^([A-Z][A-Z0-9 ’'/—–-]{3,}?)(?:\s+—\s|\s+\(|$)")


def _sections(block: str) -> list[str]:
    return [m[1].strip() for ln in block.split("\n") if (m := _HEAD.match(ln))]


def coach_inputs(phase: str) -> dict:
    """The coach's system message, in order, from running positions 1 and 2."""
    from langchain_core.messages import SystemMessage
    from backend.core.prompts import PHASE_COACH_PROMPT
    from backend.middleware.skills import DMAICSkillsMiddleware, SKILL_DIRS, instructions
    from backend.middleware.state_injection import BeforeModelStateInjection

    def run(state: Any, config: Any, prior: dict) -> list[str]:
        # A probe, not a turn: the two wraps use only `.system_message` and
        # `.override()` of the request, which `_Req` supplies.
        inj = BeforeModelStateInjection(phase, state, config, prior_documents=prior)
        inj.before_agent({}, None)
        sk = DMAICSkillsMiddleware(phase)
        sk.before_agent({}, None)
        req0: Any = _Req(SystemMessage(content=PHASE_COACH_PROMPT[phase]))
        req = sk._append_catalogue(inj._prepend(req0))
        return _texts(req)

    empty = run({"artifacts": {}, "phase_context": ""}, {}, {})
    full = run({"artifacts": {"x": "y"}, "phase_context": "framing",
                "uploads": [{"role": "evidence", "blob_path": "b"}],
                "asks": [{"status": "open", "role": "data"}]},
               {"configurable": {"case_metadata": {"title": "t"}}},
               {p: {"k": "v"} for p in ("define", "measure", "analyse", "improve", "control")})
    script, prompt = instructions(phase), PHASE_COACH_PROMPT[phase]
    always = set(_sections(empty[0]))
    blocks = []
    for text in full:
        if text == prompt:
            blocks.append({"block": "the phase coach prompt", "chars": len(text), "sections": [],
                           "source": "backend/core/prompts.py::PHASE_COACH_PROMPT"})
        elif text == script:
            blocks.append({"block": f"{SKILL_DIRS[phase]} SKILL.md", "chars": len(text), "sections": [],
                           "source": "backend/middleware/skills.py::DMAICSkillsMiddleware"})
        elif text.startswith("AVAILABLE COACHING SKILLS"):
            blocks.append({"block": "the skills catalogue", "chars": len(text), "sections": [],
                           "source": "backend/middleware/skills.py::level_1_catalogue"})
        else:
            blocks.append({"block": "project state", "chars": None,
                           "sections": [{"name": s, "when": "always" if s in always else "when present"}
                                        for s in _sections(text)],
                           "source": "backend/middleware/state_injection.py::BeforeModelStateInjection._compose"})
    return {"blocks": blocks}


def tools(phase: str) -> list[str]:
    from backend.phases.nodes_common import COACH_HOP_BUDGET, _executor_tools
    return [getattr(t, "name", getattr(t, "__name__", str(t)))
            for t in _executor_tools(phase, COACH_HOP_BUDGET, None)]


# ══ what is there, per container — step 6.64 ═════════════════════════════════
#
# The founder's container card has a "what is there" list. Until 6.63 it was
# typed (`system_view.py`'s `have=` lists, marked RELAYED); here each is READ
# from the code. The reader for each container is keyed by its Appendix F
# layer number — that pairing is logic, the names come from the procedure's
# headings, and a container with no reader says so rather than being filled.


def _ls(*patterns: str) -> list[str]:
    """Tracked paths — the tree is `git ls-files`, never a directory listing
    (CLAUDE.md §0.32: the OneDrive mirror does not carry `.claude/`)."""
    import subprocess
    out = subprocess.run(["git", "ls-files", "--", *patterns], cwd=PROJECT.parent,
                         capture_output=True, encoding="utf-8", check=True).stdout
    return sorted(ln for ln in out.splitlines() if ln.strip())


def _routes() -> list[str]:
    """`METHOD /path` for every route decorator under backend/gateway and app.py."""
    out = []
    for path in sorted((PROJECT / "backend" / "gateway").glob("*.py")) + [PROJECT / "backend" / "app.py"]:
        if not path.is_file():
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                            and dec.func.attr in ("get", "post", "put", "patch", "delete")
                            and dec.args and isinstance(dec.args[0], ast.Constant)
                            and isinstance(dec.args[0].value, str)):
                        out.append(f"{dec.func.attr.upper()} {dec.args[0].value}")
    return out


def _functions(path: Path, public_async_only: bool = False) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [n.name for n in tree.body
            if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef))
            and not n.name.startswith("_")
            and (not public_async_only or isinstance(n, ast.AsyncFunctionDef))]


def _c(text: str, source: str) -> dict:
    return {"text": text, "source": source}


def components(sh: dict) -> dict[str, list[dict]]:
    """Container id (``L<n>``) -> what is there, each item read from the code."""
    from backend.core.state import SupervisorState
    from backend.core.substate import CoachingPlan, CoachingResponse, PhaseState
    from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE
    from backend.knowledge.tools import RAG_LOOKUP_TOOLS, UNIVERSAL_TOOLS
    from backend.middleware.skills import SKILL_DIRS
    from backend.phases.gate_registry import GATE_SPECS
    from backend.phases.mappers_common import PHASE_ORDER

    def names(xs: Any) -> str:
        return ", ".join(getattr(x, "name", str(x)) for x in xs)

    ui = _ls("agent-improve/ui")
    hooks = _ls(".claude/hooks/*.py", ".githooks/*")
    board = _ls("agent-improve/tools/control_board/*.py")
    skills = _ls("agent-improve/skills/*/SKILL.md")
    phase_graphs = [p for p in PHASE_ORDER if (PROJECT / "backend" / "phases" / p / "graph.py").is_file()]
    validators = [f for p in PHASE_ORDER
                  for f in _functions(PROJECT / "backend" / "phases" / p / "validate.py")
                  if f.startswith("validate_")]
    gate_nodes = [n for n in sh["phase_graph"]["nodes"] if n.startswith("gate") or n.startswith("validation")]
    return {
        "L0": [_c(f"{len(hooks)} hook(s): " + ", ".join(Path(h).name for h in hooks), ".claude/hooks/ · .githooks/"),
               _c(f"the control board: " + ", ".join(Path(b).name for b in board),
                  "agent-improve/tools/control_board/")],
        "L1": [_c(f"{len(r)} route(s): " + ", ".join(r), "backend/gateway/*.py · backend/app.py")
               for r in [_routes()]]
              + [_c("the Belt's screen: " + ", ".join(Path(u).name for u in ui), "agent-improve/ui/")],
        "L2": [_c("the turn graph: " + " → ".join(sh["turn_graph"]["nodes"]),
                  "backend/core/graph.py::get_graph"),
               _c(f"SupervisorState — {len(SupervisorState.__annotations__)} fields: "
                  + ", ".join(SupervisorState.__annotations__), "backend/core/state.py")],
        "L3": [_c("the phase subgraph: " + " → ".join(sh["phase_graph"]["nodes"]),
                  "backend/phases/subgraph_common.py::build_phase_subgraph"),
               _c(f"{len(phase_graphs)} phase subgraph(s): " + ", ".join(phase_graphs),
                  "backend/phases/<phase>/graph.py"),
               _c(f"PhaseState — {len(PhaseState.__annotations__)} fields", "backend/core/substate.py"),
               _c("CoachingPlan: " + ", ".join(CoachingPlan.model_fields), "backend/core/substate.py")],
        "L4": [_c("the coach — create_agent, response_format CoachingResponse: "
                  + ", ".join(CoachingResponse.model_fields),
                  "backend/phases/nodes_common.py::_build_executor"),
               _c(f"{len(skills)} phase script(s): " + ", ".join(Path(s).parent.name for s in skills),
                  "agent-improve/skills/"),
               _c("the coach's input, in order: " + " · ".join(b["block"] for b in sh["coach_inputs"]["blocks"]),
                  "shape.coach_inputs — the real middleware wraps, run")],
        "L5": [_c(f"{b['position']} {b['class']} — {', '.join(b['hooks'])}", b["source"])
               for b in sh["middleware"]],
        "L6": [_c(f"the {sh['phase']} coach's tools: " + ", ".join(sh["tools"]),
                  "backend/phases/nodes_common.py::_executor_tools"),
               _c(f"{len(UNIVERSAL_TOOLS)} universal tool(s): " + names(UNIVERSAL_TOOLS),
                  "backend/knowledge/tools.py::UNIVERSAL_TOOLS"),
               _c(f"{len(RAG_LOOKUP_TOOLS)} retrieval tool(s): " + names(RAG_LOOKUP_TOOLS),
                  "backend/knowledge/tools.py::RAG_LOOKUP_TOOLS"),
               _c("computation tools per phase: " + " · ".join(
                   f"{p} {len(COMPUTATION_TOOLS_BY_PHASE.get(p, []))}" for p in PHASE_ORDER),
                  "backend/knowledge/computation.py::COMPUTATION_TOOLS_BY_PHASE")],
        "L7": [_c("the gate nodes: " + " → ".join(gate_nodes),
                  "backend/phases/subgraph_common.py::build_phase_subgraph"),
               _c(f"{len(validators)} validator(s): " + ", ".join(validators),
                  "backend/phases/<phase>/validate.py"),
               _c("gate fields per phase: " + " · ".join(
                   f"{p} {len(s.tier_1)} required, {len(s.tier_2)} recommended"
                   for p, s in GATE_SPECS.items()),
                  "backend/phases/gate_registry.py::GATE_SPECS")],
        "L8": [_c("the checkpointer: AzureBlobCheckpointSaver", "backend/core/checkpointer.py"),
               _c("the store: AzureBlobStore", "backend/core/store.py"),
               _c("the case record: " + ", ".join(_functions(PROJECT / "backend" / "storage" / "blob.py",
                                                              public_async_only=True)),
                  "backend/storage/blob.py")],
    }


def _node(n: str) -> str:
    return {"__start__": "START", "__end__": "END"}.get(n, n)


def labels(sh: dict) -> dict[str, str]:
    """Every label the diagram renders, key -> text. The board writes each
    with its `data-key`; `check_board.py` recomputes this from the code and
    refuses a label that disagrees (the brief, item 8)."""
    out: dict[str, str] = {}
    for g in ("turn_graph", "phase_graph"):
        nodes = ["__start__"] + sh[g]["nodes"] + ["__end__"]
        for i, n in enumerate(nodes):
            out[f"g:{g}:n:{i}"] = _node(n)
        for i, e in enumerate(sh[g]["edges"]):
            out[f"g:{g}:e:{i}"] = (f"{_node(e['from'])} → {_node(e['to'])}"
                                   + (" (conditional)" if e["conditional"] else ""))
    for b in sh["middleware"]:
        k = f"mw:{b['position']}"
        out[f"{k}:class"] = b["class"]
        out[f"{k}:on"] = b["on"]
        out[f"{k}:hooks"] = ", ".join(b["hooks"])
        if b["config"]:
            out[f"{k}:config"] = " · ".join(b["config"])
    out["skills:label"] = sh["skills"]["label"]
    out["skills:tools"] = ", ".join(sh["skills"]["tools"])
    for i, blk in enumerate(sh["coach_inputs"]["blocks"]):
        out[f"in:{i}:block"] = blk["block"] + (f" ({blk['chars']:,} chars)" if blk["chars"] else "")
        for j, s in enumerate(blk["sections"]):
            out[f"in:{i}:{j}"] = s["name"] + (" — when present" if s["when"] != "always" else "")
    out["tools"] = ", ".join(sh["tools"])
    for cid, items in sh.get("components", {}).items():
        for i, it in enumerate(items):
            out[f"cmp:{cid}:{i}"] = it["text"]
    return out


def shape(phase: str = "define") -> dict:
    _tracing_off()
    sh = {"phase": phase, "turn_graph": turn_graph(phase), "phase_graph": phase_graph(phase),
          "middleware": middleware(), "skills": skills(phase),
          "coach_inputs": coach_inputs(phase), "tools": tools(phase)}
    sh["components"] = components(sh)
    return sh


if __name__ == "__main__":
    import json
    print(json.dumps(shape(), indent=1, ensure_ascii=False))
