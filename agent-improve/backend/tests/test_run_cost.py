"""DEF-164 — R12's cost ceiling (founder ruling 2026-09-30): a completed Define run-through costs at
most USD 1.50 in model usage; a run above it fails the acceptance test. The cost comes from the
tokens the run recorded per model and ONE dated price file, config/model_prices.json."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import run_cost
from scripts.define_runthrough import exit_code

PRICES = run_cost.load_prices()


def _tokens(premium_in: int, premium_out: int = 0, mini_in: int = 0, mini_out: int = 0) -> dict:
    return {"gpt-4o-2024-11-20": {"calls": 1, "input_tokens": premium_in, "output_tokens": premium_out},
            "gpt-4o-mini-2024-07-18": {"calls": 1, "input_tokens": mini_in, "output_tokens": mini_out}}


def test_a_run_over_the_ceiling_fails() -> None:
    over = run_cost.run_cost(_tokens(600_000, 10_000), PRICES)      # 1.50 + 0.10
    assert over["usd"] > run_cost.CEILING_USD and over["within_ceiling"] is False, over
    assert exit_code({"cost": over}, []) == 4
    under = run_cost.run_cost(_tokens(300_000, 10_000, 60_000, 3_000), PRICES)
    assert under["within_ceiling"] is True and exit_code({"cost": under}, []) == 0, under


def test_the_ceiling_is_r12s_and_the_cost_is_priced_per_model() -> None:
    assert run_cost.CEILING_USD == 1.50
    c = run_cost.run_cost(_tokens(1_000_000, 1_000_000, 1_000_000, 1_000_000), PRICES)
    m = PRICES["models"]
    assert c["by_model"] == {k: m[k]["input"] + m[k]["output"] for k in m}, c


def test_an_unpriced_model_with_tokens_fails_the_run_and_one_without_costs_nothing() -> None:
    with pytest.raises(run_cost.UnpricedModel):
        run_cost.run_cost({"gpt-5-unpriced": {"input_tokens": 10, "output_tokens": 0}}, PRICES)
    assert run_cost.run_cost({"?": {"calls": 1, "input_tokens": 0, "output_tokens": 0}}, PRICES)["usd"] == 0
    assert exit_code({"cost": {"usd": None, "within_ceiling": False, "error": "no price"}}, []) == 4


def test_the_price_file_is_dated_sourced_and_prices_every_model_the_runs_used() -> None:
    assert PRICES["taken"] and PRICES["source"].startswith("https://prices.azure.com/api/retail/prices")
    for model in PRICES["models"].values():
        assert model["input"] > 0 and model["output"] > 0 and model["meters"], model
    records = sorted((run_cost.PROJECT / "docs" / "runthrough").glob("define_runthrough_*.json"))
    for record in records:
        summary = next(e for e in reversed(json.loads(record.read_text(encoding="utf-8")))
                       if e.get("kind") == "summary")
        for model, used in ((summary.get("tokens") or {}).get("by_model") or {}).items():
            assert model in PRICES["models"] or not (used.get("input_tokens") or used.get("output_tokens")), (
                record.name, model)


def test_no_price_is_written_in_code() -> None:
    """The prices live in the one config file; the scripts read it."""
    for script in ("run_cost.py", "define_runthrough.py"):
        text = (Path(run_cost.__file__).parent / script).read_text(encoding="utf-8")
        assert "2.50" not in text and "10.00" not in text and "0.15" not in text, script
