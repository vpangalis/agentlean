#!/usr/bin/env python3
"""No MUST / NEVER / ALWAYS sentence weakens — rule 14 of the commit-msg guard.

Founder ruling 2026-09-26 on the 6.67 report: the rule files were slimmed
(6.66 part 3, `69e9200`; CLAUDE.md 2.2.45, `e0e4d79`; 2.3.0, `791f139`) and a
hand review found sentences the slimming had dropped or softened (`7ff2e03`).
This makes that review automatic.

A NORMATIVE sentence is one that says must, never or always. For each one in
the OLD corpus, the NEW corpus must hold a sentence that says the same thing
with the same word: at least MATCH of the old sentence's content words, and
the modal kept. Otherwise it is reported —

    dropped    no sentence in the new corpus carries its content
    weakened   its content is there, but not its must / never / always

The corpus is every file that binds how work is done: `agent-improve/CLAUDE.md`,
`.claude/rules/*.md`, `.claude/skills/*/SKILL.md`. A sentence may move between
them — the three-layer conversion moved many — so the whole corpus is compared.

    python .claude/hooks/normative_check.py --since-slim   # old = the corpus before the slimming
    python .claude/hooks/normative_check.py --since-slim --disk   # ... against the working copy
    python .claude/hooks/normative_check.py                # old = HEAD, new = the index (the guard's use)

A sentence the founder ruled out is listed in `.claude/config/normative-retired.json`
with the ruling; nothing else passes a drop. Standard library only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED = ROOT / ".claude" / "config" / "normative-retired.json"
#: The commits BEFORE which the corpus was unslimmed.
PRE_SLIM = {"rules": "69e9200^", "claude": "e0e4d79^"}
MODAL_RE = re.compile(r"\b(must|never|always)\b", re.I)
WORD_RE = re.compile(r"[a-z0-9_.§-]{4,}")
MATCH = 0.6
STOP = {"that", "this", "with", "from", "have", "were", "when", "what", "which", "their",
        "there", "they", "them", "into", "only", "than", "then", "each", "every", "does",
        "will", "your", "also", "must", "never", "always", "been", "being", "here", "these"}


def is_corpus(path: str) -> bool:
    return (path == "agent-improve/CLAUDE.md"
            or (path.startswith(".claude/rules/") and path.endswith(".md"))
            or (path.startswith(".claude/skills/") and path.endswith("/SKILL.md")))


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, encoding="utf-8",
                       errors="replace", timeout=60)
    return r.stdout if r.returncode == 0 else ""


def corpus_at(rev: str | None, paths: list[str] | None = None) -> dict[str, str]:
    """{path: text} at a revision; rev None = the index."""
    if paths is None:
        listing = _git("ls-tree", "-r", "--name-only", rev) if rev else _git("ls-files")
        paths = [p for p in listing.splitlines() if is_corpus(p)]
    spec = (lambda p: f"{rev}:{p}") if rev else (lambda p: f":{p}")
    return {p: t for p in paths if (t := _git("show", spec(p)))}


def sentences(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    out = []
    for block in re.split(r"\n\s*\n|\n(?=\s*(?:[-*|#]|\d+\.)\s)", text):
        flat = re.sub(r"[`*_>#|]", " ", " ".join(block.split()))
        out += [s.strip() for s in re.split(r"(?<=[.;:!?])\s+(?=[A-Z(\"'])", flat) if s.strip()]
    return out


def words(s: str) -> set[str]:
    return {w.strip(".-") for w in WORD_RE.findall(s.lower())} - STOP


def normative(corpus: dict[str, str]) -> list[tuple[str, str]]:
    return [(p, s) for p, t in corpus.items() for s in sentences(t) if MODAL_RE.search(s)]


def compare(old: dict[str, str], new: dict[str, str], retired: set[str] | None = None) -> list[dict]:
    """Every normative sentence of `old` that `new` drops or weakens."""
    retired = retired or set()
    new_sents = [(s, words(s), {m.lower() for m in MODAL_RE.findall(s)})
                 for t in new.values() for s in sentences(t)]
    findings = []
    seen = set()
    for path, s in normative(old):
        key = " ".join(s.split())
        if key in seen or key in retired:
            continue
        seen.add(key)
        w = words(s)
        if len(w) < 3:
            continue
        modals = {m.lower() for m in MODAL_RE.findall(s)}
        best_any = best_modal = 0.0
        for _t, nw, nm in new_sents:
            score = len(w & nw) / len(w)
            best_any = max(best_any, score)
            if modals <= nm:
                best_modal = max(best_modal, score)
        if best_modal >= MATCH:
            continue
        findings.append({"path": path, "sentence": key, "modal": sorted(modals),
                         "verdict": "weakened" if best_any >= MATCH else "dropped",
                         "best": round(max(best_any, best_modal), 2)})
    return findings


def retired_set(disk: bool = False) -> set[str]:
    """The retired list AS STAGED (a retirement lands with its change), else on disk."""
    text = "" if disk else _git("show", ":" + RETIRED.relative_to(ROOT).as_posix())
    try:
        text = text or RETIRED.read_text(encoding="utf-8")
        return {" ".join(r["sentence"].split()) for r in json.loads(text)["retired"]}
    except (OSError, ValueError, KeyError):
        return set()


def corpus_on_disk() -> dict[str, str]:
    return {p: (ROOT / p).read_text(encoding="utf-8")
            for p in _git("ls-files").splitlines() if is_corpus(p) and (ROOT / p).is_file()}


def since_slim(disk: bool = False) -> list[dict]:
    old = corpus_at(PRE_SLIM["rules"])
    old = {p: t for p, t in old.items() if p.startswith(".claude/rules/")}
    old.update(corpus_at(PRE_SLIM["claude"], ["agent-improve/CLAUDE.md"]))
    return compare(old, corpus_on_disk() if disk else corpus_at(None), retired_set(disk))


def staged_check(staged: list[str]) -> list[dict]:
    """HEAD against the index — only when a corpus file is staged."""
    if not any(is_corpus(p) for p in staged):
        return []
    return compare(corpus_at("HEAD"), corpus_at(None), retired_set())


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    found = since_slim("--disk" in argv) if "--since-slim" in argv else staged_check(
        [p for p in _git("diff", "--cached", "--name-only").splitlines()])
    for f in found:
        print(f"{f['verdict']:8} ({'/'.join(f['modal'])}, best {f['best']}) {f['path']}: {f['sentence']}")
    print(f"{len(found)} normative sentence(s) dropped or weakened")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
