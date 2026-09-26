"""Is the board a true picture of the features? — the commit guard's rule 10. Step 6.67.

Reads the page's embedded `progress-data` and recomputes it from
`define_features.json` + `test-results.json`: the headline, every feature's
status and the next failing feature per lane must agree, and CONTINUITY.md's
headline must be the board's. Refuses a page that disagrees — it is generated,
so a disagreement means it was not regenerated or was edited by hand.

    python tools/control_board/check_board.py [--staged]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import build_control_board as bcb  # noqa: E402
import features  # noqa: E402

CONTINUITY = features.PROJECT / "docs" / "CONTINUITY.md"
_DATA = re.compile(r'<script type="application/json" id="progress-data">(.*?)</script>', re.S)
_CONT_HEAD = re.compile(r"^\| \*\*Headline\*\* \| (.*) \|$", re.M)


def check(page: str, continuity: str | None) -> list[str]:
    m = _DATA.search(page)
    if not m:
        return ["the page carries no progress-data"]
    got = json.loads(m.group(1).replace("<\\/", "</"))
    want = bcb.model()
    bad = []
    if got.get("headline") != want["headline"]:
        bad.append(f"the headline reads {got.get('headline')!r}; the features give {want['headline']!r}")
    for fid, st in sorted(want["statuses"].items()):
        if got.get("statuses", {}).get(fid) != st:
            bad.append(f"{fid} is {got.get('statuses', {}).get(fid)!r} on the page; its test gives {st!r}")
    if {k: (v or {}).get("id") for k, v in (got.get("next") or {}).items()} != \
            {k: (v or {}).get("id") for k, v in want["next"].items()}:
        bad.append("the next failing feature per lane differs from the features")
    if continuity is not None:
        c = _CONT_HEAD.search(continuity)
        if not c or c.group(1) != want["headline"]:
            bad.append(f"CONTINUITY.md's headline is {c.group(1) if c else None!r}; the board's is {want['headline']!r}")
    return bad


def main() -> int:
    page = bcb.OUT.read_text(encoding="utf-8") if bcb.OUT.is_file() else ""
    cont = CONTINUITY.read_text(encoding="utf-8") if CONTINUITY.is_file() else None
    bad = check(page, cont)
    for b in bad:
        print(f"  !! {b}")
    print(f"board check: {'PASS' if not bad else 'FAIL'} — {len(bad)} disagreement(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
