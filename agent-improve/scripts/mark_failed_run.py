"""Keep a failed live run's records, marked "failed: not counted" (founder, 2026-10-11).

    python -m scripts.mark_failed_run <stamp> "<why it failed, with its G-numbers>"

A run whose acceptance tests fail is evidence, not a deletion: its three records in
docs/runthrough/ (define_runthrough_, validation_repeat_ and wallclock_<stamp>.json) are renamed
with the prefix `failed_`, which no reader's pattern matches — the tests, the control board and the
continuity status read only the latest COUNTED record — and the run-through record gets a closing
`{"kind": "status", "status": "failed: not counted", "reason": …}` entry.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

RECORDS = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
KINDS = ("define_runthrough", "validation_repeat", "wallclock")
PREFIX = "failed_"
STATUS = "failed: not counted"


def mark(stamp: str, reason: str, folder: Path = RECORDS) -> list[Path]:
    """Rename the run's records and mark the run-through record; returns the new paths."""
    if not reason.strip():
        raise ValueError("a failed run is marked with why it failed")
    found = [folder / f"{k}_{stamp}.json" for k in KINDS if (folder / f"{k}_{stamp}.json").exists()]
    if not found:
        raise FileNotFoundError(f"no record of run {stamp} in {folder}")
    out: list[Path] = []
    for path in found:
        if path.name.startswith("define_runthrough_"):
            entries = json.loads(path.read_text(encoding="utf-8"))
            entries.append({"kind": "status", "status": STATUS, "reason": reason.strip(),
                            "marked": dt.date.today().isoformat()})
            path.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        target = path.with_name(PREFIX + path.name)
        path.rename(target)
        out.append(target)
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    for p in mark(argv[0], argv[1]):
        print(f"kept, not counted: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
