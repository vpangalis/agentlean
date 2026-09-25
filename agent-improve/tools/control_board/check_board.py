# -*- coding: utf-8 -*-
"""Is the board a true picture of the tree? — step 6.63's D7.

The 6.63 8D's escape: *"nothing compared two views, or a published copy
against HEAD"*. This compares. It RECOMPUTES every status, every diagram
label and the headline from the tree, and refuses the page if:

    a coloured element has no `data-key`         a status typed by hand
    a key recomputes to another colour or ref    the page disagrees with the tree
    a status has no reference, yet is not red    a claim with nothing behind it
    a recomputed status or label is missing      the page left something out
    a diagram label differs from the code        a label typed by hand
    the container view omits a registered step   a grouping dropped (6.64)
    the headline differs from CONTINUITY.md's    two views of one number
    the plan has a problem                       an unregistered step in Order,
                                                 a step in Order with no
                                                 estimate, a precondition that
                                                 names no step

`.claude/hooks/commit-msg-refactor-guard.py` runs it on every commit (rule
10), on the STAGED page and the staged CONTINUITY.md, with the project venv
(the diagram imports `backend`).

    python check_board.py [--staged]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import progress  # noqa: E402

BOARD_REL = "agent-improve/docs/control-board.html"
CONTINUITY_REL = "agent-improve/docs/CONTINUITY.md"
_COLOUR = re.compile(r"\bc-(" + "|".join(progress.COLOURS) + r")\b")
_VOID = {"br", "img", "meta", "link", "input", "hr", "rect", "line"}


class _Page(HTMLParser):
    """Every element that carries a `data-key` or a colour class, with its text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict] = []
        self._open: list[dict | None] = []
        self.scripts: dict[str, str] = {}
        self._script: str | None = None
        #: 6.64 — the container view's rows: (step, the container it sits under).
        self.cv_rows: list[tuple[str, str | None]] = []
        self._ctr: str | None = None

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        if "data-ctr" in a:
            self._ctr = a["data-ctr"]
        if "data-cv" in a:
            self.cv_rows.append((a["data-cv"], self._ctr))
        if tag == "script" and a.get("id"):
            self._script = a["id"]
            self.scripts[self._script] = ""
        cls = a.get("class") or ""
        colour = _COLOUR.search(cls)
        rec = None
        if "data-key" in a or colour:
            rec = {"tag": tag, "key": a.get("data-key"), "ref": a.get("data-ref"),
                   "colour": colour[1] if colour else None, "cls": cls, "text": "",
                   "line": self.getpos()[0]}
            self.items.append(rec)
        if tag not in _VOID:
            self._open.append(rec)

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID:
            self._open.pop()

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._script = None
        if tag not in _VOID and self._open:
            self._open.pop()

    def handle_data(self, data: str) -> None:
        if self._script:
            self.scripts[self._script] += data
        for rec in self._open:
            if rec is not None:
                rec["text"] += data


def _staged(rel: str) -> str:
    r = subprocess.run(["git", "show", f":{rel}"], cwd=progress.ROOT, capture_output=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise FileNotFoundError(f"{rel} is not in the index")
    return r.stdout


def continuity_headline(text: str) -> str | None:
    m = re.search(r"^\| \*\*Headline\*\* \| (.+?) \|\s*$", text, re.M)
    return m[1].strip() if m else None


def container_view(cv_rows: list[tuple[str, str | None]], p: dict) -> list[str]:
    """6.64 — the container view carries EVERY registered step, once, under the
    container the tree gives it. Rule 10 checked that every status on the page
    is true; a page that dropped a whole grouping passed it (the 6.64 8D)."""
    want = {s: st["container"] for s, st in p["steps"].items() if st["registered"]}
    got: dict[str, list[str | None]] = {}
    for s, c in cv_rows:
        got.setdefault(s, []).append(c)
    bad = [f"the container view omits registered step {s}" for s in sorted(set(want) - set(got))]
    for s, cs in sorted(got.items()):
        if s not in want:
            bad.append(f"the container view shows {s}, which is not a registered step")
        elif len(cs) > 1:
            bad.append(f"the container view shows {s} {len(cs)} times")
        elif cs[0] != want[s]:
            bad.append(f"the container view puts {s} under {cs[0]}; the tree gives {want[s]}")
    return bad


def check(page: str, m: dict, continuity: str | None) -> list[str]:
    """Every way the page disagrees with the tree, as sentences."""
    parsed = _Page()
    parsed.feed(page)
    want_st, want_lb = m["statuses"], m.get("labels", {})
    # The plan's own refusals: an unregistered step in Order, a step in Order
    # with no estimate, a precondition naming no step (`progress.validate`).
    bad: list[str] = [f"the plan: {x}" for x in m["p"]["problems"]]
    seen_st, seen_lb = set(), set()
    for it in parsed.items:
        k = it["key"]
        if it["colour"] and not k:
            bad.append(f"line {it['line']}: a {it['colour']} status with no reference "
                       f"(no data-key) — a colour typed by hand")
            continue
        if k == "headline":
            if it["text"].strip() != m["p"]["headline"]:
                bad.append(f"the headline reads {it['text'].strip()!r}; the tree gives {m['p']['headline']!r}")
            continue
        if it["colour"]:
            seen_st.add(k)
            w = want_st.get(k)
            if w is None:
                bad.append(f"status {k} is on the page and the tree has no such status")
            elif (it["colour"], it["ref"]) != (w["colour"], w["ref"]):
                bad.append(f"status {k} is {it['colour']} ({it['ref']}); the tree gives "
                           f"{w['colour']} ({w['ref']})")
            if not it["ref"] or (it["ref"] == "none" and it["colour"] != "red"):
                bad.append(f"status {k} is {it['colour']} with no reference")
        else:
            seen_lb.add(k)
            w = want_lb.get(k)
            if w is None:
                bad.append(f"label {k} is on the page and the code has no such label")
            elif " ".join(it["text"].split()) != " ".join(w.split()):
                bad.append(f"label {k} reads {it['text'].strip()!r}; the code gives {w!r}")
    bad += [f"status {k} is computed and not on the page" for k in sorted(set(want_st) - seen_st)]
    bad += container_view(parsed.cv_rows, m["p"])
    bad += [f"label {k} is read from the code and not on the page" for k in sorted(set(want_lb) - seen_lb)]
    data = json.loads(parsed.scripts.get("progress-data") or "{}")
    if data.get("headline") != m["p"]["headline"]:
        bad.append("the embedded progress data carries another headline")
    if continuity is not None:
        ch = continuity_headline(continuity)
        if ch != m["p"]["headline"]:
            bad.append(f"CONTINUITY.md's headline is {ch!r}; the board's is {m['p']['headline']!r}")
    return bad


def main(argv: list[str]) -> int:
    import build_control_board as bcb
    staged = "--staged" in argv
    page = _staged(BOARD_REL) if staged else (progress.ROOT / BOARD_REL).read_text(encoding="utf-8")
    cont = _staged(CONTINUITY_REL) if staged else (progress.ROOT / CONTINUITY_REL).read_text(encoding="utf-8")
    bad = check(page, bcb.model(staged=staged), cont)
    for b in bad[:40]:
        print("  " + b)
    if len(bad) > 40:
        print(f"  … and {len(bad) - 40} more")
    print(f"board check: {'FAIL' if bad else 'PASS'} — {len(bad)} disagreement(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
