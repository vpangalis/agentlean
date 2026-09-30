"""The mechanics a generated document shares — founder, 2026-09-30 (ARCHITECTURE.md headroom, A1 and
A3), after `generate_models.py`: a block between two marker comments, rewritten from the code;
`--check` fails when the file differs from a fresh generation; `--stage` (pre-commit) regenerates
from the STAGED source into the INDEX copy and the working copy. Python 3.11+, stdlib only."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parent


class GenerationError(RuntimeError):
    pass


class GeneratedDoc:
    def __init__(self, name: str, doc_rel: str, generate: Callable[[Path], str]) -> None:
        self.name, self.doc_rel, self.generate = name, doc_rel, generate
        self.begin = f"<!-- BEGIN GENERATED: {name}"
        self.end = f"<!-- END GENERATED: {name} -->"

    def span(self, doc: str) -> tuple[int, int] | None:
        b = doc.find(self.begin)
        if b < 0:
            return None
        start = doc.index("-->", b) + len("-->")
        end = doc.find(self.end, start)
        if end < 0:
            raise GenerationError(f"BEGIN GENERATED: {self.name} has no END marker")
        return start, end

    def replace(self, doc: str, body: str) -> str:
        span = self.span(doc)
        return doc if span is None else doc[:span[0]] + "\n\n" + body + "\n" + doc[span[1]:]

    def is_current(self, doc: str, project: Path = PROJECT) -> bool:
        return doc == self.replace(doc, self.generate(project))

    def stage(self) -> str:
        try:
            staged = _git(["show", f":{self.doc_rel}"])
        except GenerationError:
            return f"no staged {self.doc_rel} — nothing to do"
        if self.span(staged) is None:
            return f"no generated block in {self.doc_rel} — nothing to do"
        sys.path.insert(0, str(REPO / ".claude" / "hooks"))
        import staged_tree
        body = self.generate(staged_tree.sync(REPO) / "agent-improve")
        new = self.replace(staged, body)
        if new == staged:
            return f"{self.name} current"
        sha = _git(["hash-object", "-w", "--stdin"], input_=new).strip()
        mode = _git(["ls-files", "-s", self.doc_rel]).split()[0]
        _git(["update-index", "--cacheinfo", f"{mode},{sha},{self.doc_rel}"])
        work = REPO / self.doc_rel
        work.write_text(self.replace(work.read_text(encoding="utf-8"), body), encoding="utf-8", newline="")
        return f"{self.name} regenerated and staged"

    def main(self, argv: list[str]) -> int:
        ap = argparse.ArgumentParser(description=f"the {self.name} document, generated from the code")
        g = ap.add_mutually_exclusive_group(required=True)
        g.add_argument("--print", action="store_true")
        g.add_argument("--write", action="store_true", help=f"rewrite the block in {self.doc_rel}")
        g.add_argument("--check", action="store_true", help=f"exit 1 if {self.doc_rel} is not current")
        g.add_argument("--stage", action="store_true", help="pre-commit: from the staged tree into the index")
        a = ap.parse_args(argv)
        try:
            if a.stage:
                print(f"  [{self.name}] {self.stage()}", file=sys.stderr)
                return 0
            body = self.generate(PROJECT)
            if a.print:
                sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
                print(body, end="")
                return 0
            path = REPO / self.doc_rel
            doc = path.read_text(encoding="utf-8")
            if a.write:
                path.write_text(self.replace(doc, body), encoding="utf-8", newline="")
                return 0
            if self.is_current(doc):
                print(f"{self.doc_rel}: current")
                return 0
            print(f"{self.doc_rel}: differs from a fresh generation — run with --write")
            return 1
        except GenerationError as exc:
            print(f"{self.name}: {exc}", file=sys.stderr)
            return 2


def _git(args: list[str], input_: str | None = None) -> str:
    """Bytes on the pipes (a text-mode stdin on Windows would stage CRLF)."""
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                       input=None if input_ is None else input_.encode("utf-8"))
    if r.returncode != 0:
        raise GenerationError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
