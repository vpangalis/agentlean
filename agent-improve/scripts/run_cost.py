"""A run-through's model cost, against R12's ceiling (founder ruling 2026-09-30).

R12: a completed Define run-through costs at most USD 1.50 in model usage (1.5 x the measured
~USD 1.00, run of 2026-09-30); a run above the ceiling fails the acceptance test,
`scripts/define_runthrough.py`. The cost is computed from the tokens the run recorded per model
(`summary.tokens.by_model`) and the prices in ONE file, `config/model_prices.json`, with the date
they were taken. A model with tokens and no price fails the run: an unpriced model is never free.

    python -m scripts.run_cost docs/runthrough/define_runthrough_<stamp>.json ...
                                    # each record's cost; exit 1 if any is over or unpriced
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
PRICES = PROJECT / "config" / "model_prices.json"
#: R12 (founder ruling 2026-09-30).
CEILING_USD = 1.50
PER = 1_000_000


class UnpricedModel(ValueError):
    """A model the run used, with tokens, that config/model_prices.json does not price."""


def load_prices(path: Path = PRICES) -> dict[str, Any]:
    return dict(json.loads(path.read_text(encoding="utf-8")))


def run_cost(by_model: dict[str, dict[str, Any]], prices: dict[str, Any]) -> dict[str, Any]:
    """The run's cost in USD, per model and in total, and whether it is within the ceiling."""
    models = prices["models"]
    per_model: dict[str, float] = {}
    for model, used in sorted(by_model.items()):
        tokens_in, tokens_out = int(used.get("input_tokens") or 0), int(used.get("output_tokens") or 0)
        if not tokens_in and not tokens_out:
            continue                            # a call that recorded no usage costs nothing counted
        if model not in models:
            raise UnpricedModel(f"no price for model {model!r} in {PRICES.name} "
                                f"({tokens_in} input, {tokens_out} output tokens)")
        p = models[model]
        per_model[model] = round(tokens_in * p["input"] / PER + tokens_out * p["output"] / PER, 4)
    usd = round(sum(per_model.values()), 4)
    return {"usd": usd, "by_model": per_model, "ceiling_usd": CEILING_USD,
            "within_ceiling": usd <= CEILING_USD, "prices_taken": prices["taken"]}


def record_cost(record: Path, prices: dict[str, Any] | None = None) -> dict[str, Any]:
    """The cost of a recorded run-through (its summary entry's tokens)."""
    entries = json.loads(record.read_text(encoding="utf-8"))
    summary = next(e for e in reversed(entries) if e.get("kind") == "summary")
    tokens = summary.get("tokens") or {}
    if not tokens.get("by_model"):
        raise UnpricedModel(f"{record.name} recorded no tokens per model")
    return run_cost(tokens["by_model"], prices or load_prices())


def main(argv: list[str]) -> int:
    prices, failed = load_prices(), 0
    for arg in argv:
        path = Path(arg)
        try:
            c = record_cost(path, prices)
        except UnpricedModel as exc:
            print(f"{path.name}: FAIL — {exc}")
            failed += 1
            continue
        verdict = "pass" if c["within_ceiling"] else "FAIL"
        print(f"{path.name}: USD {c['usd']:.2f} of {CEILING_USD:.2f} — {verdict} (prices of {c['prices_taken']})")
        failed += not c["within_ceiling"]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
