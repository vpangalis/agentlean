#!/usr/bin/env python3
"""The structured values' keys, generated from the code — founder ruling 2026-10-13 (tables that restate
the code are generated). Was hand-written in ARCHITECTURE.md §4.1 ("Structured values inside records and
replies"); now a generated block there.

Each row names a value and the code constant that owns its keys; the keys are read from that constant with
`ast` (nothing is imported). A value whose keys have no owner in code (the reference dicts,
`fields_captured`) stays in the hand-written rows below the block.

    generate_value_keys.py --print | --write | --check | --stage
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import GeneratedDoc, GenerationError  # noqa: E402

#: (value as the table names it, file, constant, how the keys read). `class:` reads a class's annotated fields.
ROWS: tuple[tuple[str, str, str, str], ...] = (
    ("`team`", "backend/phases/define/schema.py", "TEAM_MEMBER_KEYS", "list of {keys}"),
    ("`project_scope`", "backend/phases/define/schema.py", "PROJECT_SCOPE_KEYS", "{keys}"),
    ("`benefits_analysis`", "backend/phases/define/schema.py", "BENEFITS_ANALYSIS_KEYS", "{keys}"),
    ("`process_map_sipoc`", "backend/phases/define/schema.py", "SIPOC_KEYS", "{keys}, `process_performance`"),
    ("`process_map_sipoc.process_steps[]` (ADR-0078)", "backend/phases/define/parse.py", "STEP_KEYS", "{keys}"),
    ("a step's `duration`", "backend/phases/define/parse.py", "DURATION_KEYS", "{keys}, each a MetricValue"),
    ("`process_map_sipoc.process_performance`", "backend/phases/define/parse.py", "PROCESS_PERFORMANCE_KEYS",
     "{keys}, each a MetricValue"),
    ("`critical_to_quality`", "backend/phases/define/schema.py", "CTQ_KEYS", "list of {keys}"),
    ("`problem_5w2h`", "backend/phases/define/schema.py", "FIVE_W_TWO_H_KEYS", "{keys}"),
    ("`metric_definitions`", "backend/phases/define/schema.py", "METRIC_DEFINITION_KEYS",
     "list of {keys}; the first entry is the primary metric"),
    ("`baseline_estimate`, `target_value` (MetricValue, ADR-0071)", "backend/phases/define/schema.py",
     "class:MetricValue", "{keys}"),
    ("`phase_metrics`", "backend/phases/define/schema.py", "PHASE_METRIC_REQUIRED_KEYS",
     "list, one entry per registry metric: {keys}; other keys per phase"),
    ("`detailed_process_map`", "backend/phases/measure/schema.py", "DETAILED_PROCESS_MAP_KEYS", "{keys}"),
    ("`control_plan`", "backend/phases/control/schema.py", "CONTROL_PLAN_KEYS", "{keys}"),
    ("`CoachingResponse.contradiction_flag`", "backend/core/substate.py", "CONTRADICTION_FLAG_KEYS", "{keys}"),
)


def _keys(project: Path, rel: str, name: str) -> tuple[str, ...]:
    tree = ast.parse((project / rel).read_text(encoding="utf-8"), filename=rel)
    if name.startswith("class:"):
        cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name[6:]), None)
        if cls is None:
            raise GenerationError(f"{rel}: no class {name[6:]}")
        return tuple(n.target.id for n in cls.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name))
    for node in tree.body:
        target: ast.expr
        value: ast.expr | None
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        else:
            continue
        if isinstance(target, ast.Name) and target.id == name and value is not None:
            return tuple(ast.literal_eval(value))
    raise GenerationError(f"{rel}: no constant {name}")


def generate(project: Path) -> str:
    rows = ["| Value | Keys | Owned by |", "|---|---|---|"]
    for value, rel, name, form in ROWS:
        keys = ", ".join(f"`{k}`" for k in _keys(project, rel, name))
        owner = f"`{rel.split('/', 1)[1]}::{name.removeprefix('class:')}`"
        rows.append(f"| {value} | {form.format(keys=keys)} | {owner} |")
    return "\n".join(rows) + "\n"


DOC = GeneratedDoc("value keys", "agent-improve/ARCHITECTURE.md", generate)

if __name__ == "__main__":
    sys.exit(DOC.main(sys.argv[1:]))
