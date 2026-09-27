#!/usr/bin/env python3
"""Is a staged change to a Python file ANNOTATION-ONLY? (founder, 2026-09-27)

Two rules ask it. Rule 15 refuses a `chore(...)` subject on a backend change
that is not annotation-only — a defect fix carries `fix` or `Gap:`. Rule 2b
skips a commit whose watched paths changed only in annotations.

**Annotation-only means: the two versions' syntax trees are identical once
type annotations are removed.** Comments never reach the tree, so they are
free. What is removed:

  * parameter and return annotations of an UNDECORATED function or method;
  * the annotation of an assignment inside a function or at module level
    (`x: T = v` compares as `x = v`; a bare `x: T` there is dropped);
  * `from typing import ...`, `import typing`, `from __future__ import ...`,
    and `if TYPE_CHECKING:` blocks.

What is deliberately KEPT, because there an annotation is behaviour:

  * annotations inside a CLASS body — a Pydantic model, a TypedDict (LangGraph
    state) or a dataclass reads its fields from them;
  * annotations of a DECORATED function — FastAPI parses a route's request from
    them, `@tool` builds its schema from them.

Docstrings are code to this check: a changed docstring is not annotation-only.
Anything that is not Python, or is added or deleted, is not annotation-only.
Python 3.11+, stdlib only.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path


class _Strip(ast.NodeTransformer):
    def __init__(self) -> None:
        self._depth_class = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self._depth_class += 1
        self.generic_visit(node)
        self._depth_class -= 1
        return node

    def _strip_fn(self, node):  # type: ignore[no-untyped-def]
        if not node.decorator_list:
            a = node.args
            for arg in [*a.posonlyargs, *a.args, *a.kwonlyargs, a.vararg, a.kwarg]:
                if arg is not None:
                    arg.annotation = None
            node.returns = None
        saved, self._depth_class = self._depth_class, 0   # a method body is not a class body
        self.generic_visit(node)
        self._depth_class = saved
        return node

    visit_FunctionDef = _strip_fn
    visit_AsyncFunctionDef = _strip_fn

    def visit_AnnAssign(self, node: ast.AnnAssign):  # type: ignore[no-untyped-def]
        if self._depth_class:
            return node
        if node.value is None:
            return None
        return ast.Assign(targets=[node.target], value=node.value, lineno=node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom):  # type: ignore[no-untyped-def]
        return None if node.module in ("typing", "__future__") else node

    def visit_Import(self, node: ast.Import):  # type: ignore[no-untyped-def]
        keep = [a for a in node.names if a.name != "typing"]
        if not keep:
            return None
        node.names = keep
        return node

    def visit_If(self, node: ast.If):  # type: ignore[no-untyped-def]
        t = node.test
        if (isinstance(t, ast.Name) and t.id == "TYPE_CHECKING") or \
           (isinstance(t, ast.Attribute) and t.attr == "TYPE_CHECKING"):
            return None
        self.generic_visit(node)
        return node


def _normal(src: str) -> str:
    tree = _Strip().visit(ast.parse(src))
    return ast.dump(ast.fix_missing_locations(tree), include_attributes=False)


def is_annotation_only(old: str | None, new: str | None) -> bool:
    """True when both versions exist, parse, and differ at most in annotations."""
    if old is None or new is None:
        return False
    try:
        return _normal(old) == _normal(new)
    except SyntaxError:
        return False


def _show(root: str, spec: str) -> str | None:
    r = subprocess.run(["git", "show", spec], cwd=root, capture_output=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL)
    return r.stdout if r.returncode == 0 else None


def staged_is_annotation_only(root: str, path: str) -> bool:
    """HEAD's version against the INDEX's version of `path` (repo-relative)."""
    if not path.endswith(".py"):
        return False
    return is_annotation_only(_show(root, f"HEAD:{path}"), _show(root, f":{path}"))


if __name__ == "__main__":
    import sys
    root = str(Path(__file__).resolve().parents[2])
    for p in sys.argv[1:]:
        print(("annotation-only  " if staged_is_annotation_only(root, p) else "CODE CHANGE      ") + p)
