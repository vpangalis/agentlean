"""Founder 2026-09-30 (ARCHITECTURE.md headroom, A1 and A3): the code layout and the API routes are
generated from the code into docs/code-layout.md and docs/api-routes.md, as §4.2's declarations are
into docs/data-models.md. The pre-commit hook regenerates both; this checks each file equals a fresh
generation, and that ARCHITECTURE.md links them."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT / "tools" / "architecture"
sys.path.insert(0, str(TOOLS))

import generate_define_script  # noqa: E402
import generate_layout  # noqa: E402
import generate_routes  # noqa: E402
import generate_value_keys  # noqa: E402
import generate_middleware_order  # noqa: E402


@pytest.mark.parametrize("gen", [generate_layout, generate_routes, generate_value_keys, generate_middleware_order],
                         ids=["code layout", "api routes", "value keys", "middleware order"])
def test_the_generated_document_is_current(gen) -> None:
    doc = gen.DOC
    text = (PROJECT.parent / doc.doc_rel).read_text(encoding="utf-8")
    assert doc.span(text) is not None, f"{doc.doc_rel} has no generated block"
    assert doc.is_current(text, PROJECT), f"{doc.doc_rel} differs from a fresh generation — run {gen.__name__}.py --write"


def test_architecture_links_both() -> None:
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "(docs/code-layout.md)" in arch and "(docs/api-routes.md)" in arch


def test_every_route_is_listed() -> None:
    body = generate_routes.generate(PROJECT)
    for path in ("/ask", "/upload", "/gate", "/gate/decision", "/cases", "/health"):
        assert f"| `{path}` |" in body, path


def test_the_graph_route_table_names_real_routes() -> None:
    """Founder ruling 2026-10-13 (tables that restate the code): §2.4's route → graph table stays
    hand-written — its cells are prose — but its route column is checked against `gateway/routes.py`:
    every route it names exists, and every handler that runs the graph (`_run_turn`) is in it."""
    import ast
    import re
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    start = arch.index("| Route | Graph input |")
    table = arch[start:arch.index("\n\n", start)]
    named = set(re.findall(r"^\| `(GET|POST|PUT|PATCH|DELETE) ([^`]+)` \|", table, re.M))
    tree = ast.parse((PROJECT / "backend" / "gateway" / "routes.py").read_text(encoding="utf-8"))
    routes, runs_graph = set(), set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                    and isinstance(dec.func.value, ast.Name) and dec.func.value.id == "router"
                    and isinstance(dec.args[0], ast.Constant)):
                route = (dec.func.attr.upper(), str(dec.args[0].value))
                routes.add(route)
                if any(isinstance(n, ast.Name) and n.id == "_run_turn" for n in ast.walk(node)):
                    runs_graph.add(route)
    assert named, "§2.4's route table not found"
    assert named <= routes, f"§2.4 names routes that do not exist: {sorted(named - routes)}"
    assert runs_graph <= named, f"routes that run the graph, missing from §2.4: {sorted(runs_graph - named)}"


def test_the_middleware_table_is_in_the_declared_order() -> None:
    """Founder ruling 2026-10-13: §3.3's order is generated from `_build_executor`; the hand-written
    table of what each middleware does keeps one row per entry, in that order."""
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    start = arch.index("| Middleware | Where, and what it does |")
    rows = [r.split("|")[1] for r in arch[start:arch.index("\n\n", start)].splitlines()[2:]]
    declared = [row for _, row in generate_middleware_order.entries(PROJECT)]
    assert len(rows) == len(declared), f"{len(rows)} table rows, {len(declared)} declared middleware"
    for n, (cell, name) in enumerate(zip(rows, declared), 1):
        assert name in cell, f"row {n} is {cell.strip()!r}; the declared list has {name} there"


def test_the_state_writers_table_names_every_field_once() -> None:
    """Founder ruling 2026-10-13: `SupervisorState`'s fields are generated into docs/data-models.md; §4.1's
    hand-written writers table names each of them exactly once, and nothing else."""
    import ast
    import re
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    start = arch.index("| Field | Writer | Readers |")
    cells = [r.split("|")[1] for r in arch[start:arch.index("\n\n", start)].splitlines()[2:]]
    named = [n for cell in cells for n in re.findall(r"`(\w+)`", cell)]
    tree = ast.parse((PROJECT / "backend" / "core" / "state.py").read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SupervisorState")
    declared = [n.target.id for n in cls.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
    assert sorted(named) == sorted(declared), f"table names {sorted(named)}; SupervisorState has {sorted(declared)}"


#: Classes outside the files .claude/rules/module-layout.md §2 designates, which predate the check (audit A10;
#: founder ruling 2026-10-24, B3). The set may only shrink: a class moved into a designated file, or §2 amended by the
#: founder, removes its entry; a new class elsewhere fails.
KNOWN_OUTSIDE = {
    ("app.py", "RequestIdMiddleware"), ("core/config.py", "Config"), ("core/config.py", "Settings"),
    ("core/diagrams.py", "DiagramError"), ("core/graph.py", "PhaseNotWired"), ("core/logging_setup.py", "_ContextFilter"),
    ("gateway/routes.py", "ClientGone"), ("gateway/routes.py", "TurnDeadline"),
    ("knowledge/computation.py", "_NeedsReformatting"), ("knowledge/fusion.py", "QueryVariants"),
    ("knowledge/tools.py", "_Blank"), ("phases/gate_assembly.py", "GateAssemblyError"),
    ("phases/gate_registry.py", "GateSpec"), ("phases/mappers_common.py", "PriorGateDocumentMissing"),
}


def test_classes_live_only_in_the_files_the_classes_rule_designates() -> None:
    """B3 (audit A10): every class outside module-layout.md §2's files is a known one; a known one that moved is
    taken off the list."""
    found = set(generate_layout.class_violations(PROJECT))
    assert not found - KNOWN_OUTSIDE, f"a class outside module-layout.md §2: {sorted(found - KNOWN_OUTSIDE)}"
    assert not KNOWN_OUTSIDE - found, f"no longer outside — take it off KNOWN_OUTSIDE: {sorted(KNOWN_OUTSIDE - found)}"


def test_the_classes_check_can_fail_and_the_mark_follows_the_rule(tmp_path) -> None:
    """B3: a class in a functions-only file is found, a class in a designated file is not; the layout marks C the
    file the rule designates, not the file that happens to hold a class."""
    project = tmp_path / "agent-improve"
    (project / "backend" / "core").mkdir(parents=True)
    (project / "backend" / "phases" / "define").mkdir(parents=True)
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    (tmp_path / generate_layout.RULE).write_text(
        (PROJECT.parent / generate_layout.RULE).read_text(encoding="utf-8"), encoding="utf-8")
    (project / "backend" / "core" / "llm.py").write_text('"""The factory."""\nclass Sneaky:\n    pass\n', encoding="utf-8")
    (project / "backend" / "core" / "state.py").write_text('"""State."""\nclass SupervisorState:\n    pass\n',
                                                           encoding="utf-8")
    (project / "backend" / "phases" / "define" / "schema.py").write_text('"""Schema."""\nclass DefineOutput:\n    pass\n',
                                                                          encoding="utf-8")
    assert generate_layout.class_violations(project) == [("core/llm.py", "Sneaky")]
    rows = generate_layout.generate(project)
    assert "`state.py` C |" in rows and "`schema.py` C |" in rows, rows
    assert "`llm.py` |" in rows and "`llm.py` C" not in rows, rows


# ── B7 (founder ruling 2026-10-27, item 4): the Define skill, generated from the criteria's owner ──

_DEFINE = PROJECT / "skills" / "dmaic-define-phase"


def test_the_define_script_is_a_fresh_generation_from_its_owner() -> None:
    """B7: "code owns the criteria, their ids and the element order (one owner); the skill text and the welcome are
    generated from it, not parsed." SKILL.md and coaching_script.md (its section 3, byte for byte) equal a fresh
    generation from `phases/define/criteria.py`."""
    assert generate_define_script.stale(PROJECT) == [], "run tools/architecture/generate_define_script.py --write"
    skill = (_DEFINE / "SKILL.md").read_text(encoding="utf-8")
    script = (_DEFINE / "coaching_script.md").read_text(encoding="utf-8")
    assert script.startswith("**[OPENING") and script == generate_define_script.mirror(skill)
    assert ("\n\n" + script + "\n---\n\n## 4.") in skill, "coaching_script.md is SKILL.md's section 3, byte for byte"


def test_the_owners_criteria_order_and_welcome_are_what_the_skill_states() -> None:
    """B7: what the generated skill says — read here with a parser of the test's own, never the product's — is the
    owner's: each element's criteria (id and text, in order), the numbered heads in the owner's order, the element
    table, the [OPENING] block and section F."""
    import re

    from backend.phases.define import criteria as owner
    skill = (_DEFINE / "SKILL.md").read_text(encoding="utf-8")
    blocks = re.findall(r"^\*\*\[(\d+) · (\w+) · [^\]]*\]\*\*\n((?:>.*\n)+)", skill, re.M)
    assert [(int(n), f) for n, f, _ in blocks] == list(enumerate(owner.ELEMENT_ORDER, start=1))
    for _n, field, block in blocks:
        stated = re.findall(r"^> - `([a-z0-9-]+)` — (.+)$", block, re.M)
        assert tuple(stated) == owner.CRITERIA[field], field
    table = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \|$", skill, re.M)
    assert [(int(n), name.strip(), tuple(re.findall(r"`(\w+)`", fields))) for n, name, fields in table] == [
        (n, owner.ELEMENT_NAMES[f], (f, *owner._CAPTURED_INSIDE.get(f, ())))
        for n, f in enumerate(owner.ELEMENT_ORDER, start=1)]
    opening = skill.split("**[OPENING — the welcome]**\n", 1)[1].split("\n\n", 1)[0].splitlines()
    assert opening == [f"> {owner.WELCOME}", *(f"> • **{p}** — {line}" for p, line in owner.PHASES),
                       f"> {owner.HOW_DEFINE_IS_WORKED}"]
    assert "### F — The Define report\n\n" + "\n".join(owner.HOW_DEFINE_ENDS) + "\n\n---" in skill
    assert "**[METRIC LITERACY — field 5," in skill and owner.ELEMENT_ORDER[4] == "baseline_estimate"


def test_every_criterion_id_has_one_named_constant() -> None:
    """B7 (U4): code names a criterion by the owner's constant — one constant per id, every id has one."""
    from backend.phases.define import criteria as owner
    ids = {cid for items in owner.CRITERIA.values() for cid, _ in items}
    named = {v: n for n in dir(owner) if n.isupper() and isinstance(v := getattr(owner, n), str) and v in ids}
    assert set(named) == ids, sorted(ids - set(named))
    assert set(owner.CRITERIA) == set(owner.ELEMENT_ORDER) == set(owner.ELEMENT_NAMES)
    assert all(len({c for c, _ in items}) == len(items) for items in owner.CRITERIA.values()), "an id twice"


def test_the_generation_follows_the_owner_and_refuses_a_skill_without_an_element(tmp_path) -> None:
    """B7, the mutation proof: a criterion reworded and two elements swapped in a copy of the owner and the schema
    regenerate the copy's skill — the criterion line, the numbered heads, the table and METRIC LITERACY's `field n` —
    and a skill with no block for one of the owner's elements is refused."""
    project = tmp_path / "agent-improve"
    for rel in (generate_define_script.OWNER, generate_define_script.SCHEMA, generate_define_script.SKILL):
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text((PROJECT / rel).read_text(encoding="utf-8"), encoding="utf-8")
    owner_py, schema_py = project / generate_define_script.OWNER, project / generate_define_script.SCHEMA
    owner_py.write_text(owner_py.read_text(encoding="utf-8").replace(
        '"exactly one primary metric (p. 58)"', '"exactly one primary metric, named (p. 58)"'), encoding="utf-8")
    text = schema_py.read_text(encoding="utf-8")
    swapped = text.replace('"problem_statement",    # 4', '"baseline_estimate",    # 4').replace(
        '"baseline_estimate",    # 5', '"problem_statement",    # 5')
    assert swapped.count('"baseline_estimate",    # 4') == swapped.count('"problem_statement",    # 5') == 1
    schema_py.write_text(swapped, encoding="utf-8")
    skill = (project / generate_define_script.SKILL).read_text(encoding="utf-8")
    new, script = generate_define_script.generate(project, skill)
    assert "> - `one-primary` — exactly one primary metric, named (p. 58)\n" in new
    assert "**[4 · baseline_estimate · " in new and "**[5 · problem_statement · " in new
    assert "| 4 | Primary metric and baseline | `baseline_estimate`, `metric_definitions` |" in new
    assert "**[METRIC LITERACY — field 4, where the metric gets named]**" in new
    assert script == generate_define_script.mirror(new) and "exactly one primary metric, named" in script
    broken = skill.replace("**[13 · issues_and_barriers · required]**", "**[13 · barriers · required]**")
    with pytest.raises(generate_define_script.GenerationError):
        generate_define_script.generate(project, broken)
