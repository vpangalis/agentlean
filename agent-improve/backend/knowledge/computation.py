"""The twenty DMAIC computation tools — procedure steps 5.3 and 5.4.

Canonical: **§69** (S-F37–S-F56, the twenty interfaces), **§60.6 — S-F24** (the
group entry and the EARS behaviours binding on all twenty), **§31** (arg
schemas). Architecture §30 (per-phase binding), §7 (the typing law), §43.1 (the
seven-step coaching pattern).

    Define 1 · Measure 8 · Analyse 5 · Improve 1 · Control 5  =  20

That line is the file's structure, not a comment on it:
`COMPUTATION_TOOLS_BY_PHASE` (step 5.4) is the partition, and the flat
`COMPUTATION_TOOLS` is derived from it. Each phase executor binds the universal
seven (§29.2) plus its own subset — 8 / 15 / 12 / 8 / 12, no phase over §30's
ceiling of 16.

WHAT EVERY ONE OF THEM IS
-------------------------
**A pure function** — deterministic, no LLM call, no I/O (B1). §14 calls these
the one place synchronous code is unambiguously correct, and that is why they
are the only `def` in this codebase that is not `async`.

**A separately named `@tool` with its own `args_schema=`** (B4, §31).
**Parameterised grouping is BANNED**: there is no `calculate_cpk(mode="post")`,
which is why `post_improvement_cpk` is its own entry despite sharing the
formula. The two share a private helper, `_cpk_values`. That is explicitly
permitted — *"The two MAY share a private helper; they are two `@tool`s"* — and
the difference is the contract, not the arithmetic: `post_improvement_cpk` also
takes `baseline_cpk` and returns `improvement_delta`, which is the number
Control's `post_improvement_metrics` is graded against.

EVERY RESULT VALUE IS A STRING
------------------------------
§7's typing law, restated by §69.1: a numeric like `cpk: 0.62` is stored as
`"result": {"cpk": "0.62", …}`. Each tool returns the **`result` sub-dict**;
the executor wraps it in §7's full `{"tool", "inputs", "result", "turn",
"phase"}` shape and writes it to `artifacts["computation_results"]` (B6) — the
turn and phase are not knowable here.

A TOOL THAT CANNOT PARSE ITS INPUT ASKS; IT DOES NOT RAISE OR GUESS
-------------------------------------------------------------------
**B3.** Every captured field is a `str` (§7), so `"12.3% invoice error rate,
measured over Q2 2026"` is what actually arrives where a spec says `mean`. The
scalar args are therefore `str` in `tool_args.py` and are parsed here by
`_num()`, which returns a plain-language reformatting request rather than
raising — a `ValidationError` would surface as a tool-call failure the Belt
never sees phrased in their own terms.

**Preconditions are business and methodology preconditions** (§69.1) — what must
be true of the project before the tool should be called. They are NOT argument
validation. `calculate_cpk`'s stability precondition is enforced by the grader
(§35, §41), not here; what IS enforced here is the arithmetic's own
requirements — at least two steps for RTY, expected cell counts ≥ 5 for
chi-square — and those return requests too.

THE FORMULAS ARE STANDARDS, NOT LIBRARY PATTERNS
------------------------------------------------
§69.1 is explicit that the trusted-source rule differs here: AIAG MSA-4 for
GR&R, Shewhart's constant tables, the standard hypothesis tests, and the 1.5σ
long-term-shift convention. **They do not drift the way a package API does**,
so the check is "matches the standard method as taught in the ingested BB
eBook", not a version lookup. Applying `/verify-current-version` to a Shewhart
constant table would be a category error.

`scipy` and `numpy` are pinned, declared dependencies (`requirements.txt`
1.13.0 / 1.26.4), used for the reference distributions rather than hand-rolled
approximations of them.
"""
from __future__ import annotations

import math
import re
from typing import Any

import numpy as np
from langchain_core.tools import BaseTool, tool
from scipy import stats

from backend.knowledge.tool_args import (
    AnovaArgs,
    CChartArgs,
    ChiSquareArgs,
    CpkArgs,
    DoeMainEffectsArgs,
    DpmoArgs,
    ExpectedSavingsArgs,
    FtqArgs,
    GrrArgs,
    ImrArgs,
    LinearRegressionArgs,
    PChartArgs,
    PearsonArgs,
    PostImprovementCpkArgs,
    SampleSizeMeanArgs,
    SampleSizeProportionArgs,
    SigmaLevelArgs,
    TTestArgs,
    XbarRArgs,
    YieldRtyArgs,
)

Result = dict[str, str]

#: Shewhart control-chart constants by subgroup size (n = 2…10), from the
#: standard table. A2 sets the X-bar limits, D3/D4 the range limits. These are
#: fixed values from the method, not parameters — an n outside this range gets
#: a reformatting request rather than an extrapolation.
SHEWHART: dict[int, dict[str, float]] = {
    2:  {"A2": 1.880, "D3": 0.000, "D4": 3.267, "d2": 1.128},
    3:  {"A2": 1.023, "D3": 0.000, "D4": 2.574, "d2": 1.693},
    4:  {"A2": 0.729, "D3": 0.000, "D4": 2.282, "d2": 2.059},
    5:  {"A2": 0.577, "D3": 0.000, "D4": 2.114, "d2": 2.326},
    6:  {"A2": 0.483, "D3": 0.000, "D4": 2.004, "d2": 2.534},
    7:  {"A2": 0.419, "D3": 0.076, "D4": 1.924, "d2": 2.704},
    8:  {"A2": 0.373, "D3": 0.136, "D4": 1.864, "d2": 2.847},
    9:  {"A2": 0.337, "D3": 0.184, "D4": 1.816, "d2": 2.970},
    10: {"A2": 0.308, "D3": 0.223, "D4": 1.777, "d2": 3.078},
}

#: I-MR uses the n=2 moving-range constants: E2 = 3/d2(2) = 2.66, D4 = 3.267.
IMR_E2 = 2.660
IMR_D4 = 3.267

#: The long-term shift convention (§69.1). Stated in every sigma result so the
#: number is comparable — a "sigma level" without it is ambiguous by 1.5.
SIGMA_SHIFT = 1.5

_NUMBER = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


class _NeedsReformatting(Exception):
    """Internal: an input could not be parsed. Converted to a `result` by the
    tool, never propagated — B3 forbids raising at the Belt."""

    def __init__(self, request: str) -> None:
        super().__init__(request)
        self.request = request


def _num(value: str | float | None, label: str,
         required: bool = True) -> float | None:
    """Pull a number out of whatever the Belt wrote, or ask for a rewrite.

    **B2's parse-at-the-point-of-use, and B3's ask-rather-than-raise.** Captured
    fields are prose: `"12.3% invoice error rate, measured over Q2 2026"` is a
    perfectly good `baseline_estimate` and contains exactly one number. Commas
    are stripped so `"120,000"` reads; a bare `%` does not change the value,
    because whether the Belt is working in percent or in fractions is their
    unit choice and the tool must not silently rescale it.

    Returns `None` for an absent optional value. Raises `_NeedsReformatting`,
    which every tool converts into a `result` — the exception never leaves this
    module.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise _NeedsReformatting(
                f"I need a number for {label} and did not get one. Could you "
                f"give me just the figure — for example '12.3'?"
            )
        return None
    if isinstance(value, (int, float)):
        return float(value)

    match = _NUMBER.search(value.replace(",", ""))
    if match is None:
        if required:
            raise _NeedsReformatting(
                f"I could not find a number in {label} — you wrote "
                f"'{value.strip()[:60]}'. Could you give me just the figure?"
            )
        return None
    return float(match.group())


def _fmt(x: float, places: int = 4) -> str:
    """Render a number as a string (§7's typing law) without float noise."""
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return "undefined"
    rounded = round(float(x), places)
    if rounded == int(rounded) and abs(rounded) < 1e15:
        return str(int(rounded))
    return f"{rounded:g}"


def _asks(request: str) -> Result:
    """The B3 return shape: a reformatting request, not an exception.

    One key, `reformatting_request`, so a caller can tell a request from a
    computed result by looking for it rather than by parsing prose.
    """
    return {"reformatting_request": request}


def _significant(p_value: float, alpha: float = 0.05) -> str:
    """§69's `significant` key — `"yes"` / `"no"` at α = 0.05."""
    return "yes" if p_value < alpha else "no"


def _as_fraction(y: float) -> float:
    """A yield given as 98 means 0.98; given as 0.98 it means 0.98.

    The >1 test is safe because a yield above 1.0 is not a yield.
    """
    return y / 100.0 if y > 1.0 else y


# ══════════════════════════════════════════════════════════════════════════
# DEFINE — 1 tool
# ══════════════════════════════════════════════════════════════════════════


@tool(args_schema=ExpectedSavingsArgs)
def calculate_expected_savings(
    baseline_value: str, target_value: str, unit_cost: str, annual_volume: str
) -> Result:
    """Expected savings — what closing the baseline-to-target gap is worth over a year, in money.

    Use this once the team has agreed where they are (baseline) and where they
    want to be (target), and knows roughly what one defect costs. It turns the
    improvement into the number a sponsor will actually ask for.

    Returns the annual figure AND the multiplication used, because a Belt has to
    be able to defend it at the gate — a savings number nobody can reconstruct
    is a savings number nobody will approve.

    If the team has not worked out a cost basis yet, say so and ask for it. Do
    not invent a unit cost.
    """
    try:
        base = _num(baseline_value, "the baseline value")
        target = _num(target_value, "the target value")
        cost = _num(unit_cost, "the cost per defect or per unit of the gap")
        volume = _num(annual_volume, "the annual volume")
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert base is not None and target is not None
    assert cost is not None and volume is not None

    gap = base - target
    savings = gap * volume * cost
    return {
        "annual_savings": _fmt(savings, 2),
        "currency": "as supplied in unit_cost",
        "calculation_note": (
            f"({_fmt(base)} baseline − {_fmt(target)} target) "
            f"× {_fmt(volume)} units/year × {_fmt(cost)} per unit "
            f"= {_fmt(savings, 2)}. Check the units agree: if the gap is in "
            f"percentage points, the volume and unit cost must be on the same "
            f"basis."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# MEASURE — 8 tools
# ══════════════════════════════════════════════════════════════════════════


def _dpmo_value(defects: float, units: float, opportunities: float) -> float:
    """Defects per million opportunities. Shared by two tools by arithmetic,
    not by contract — they remain two `@tool`s (B4)."""
    return (defects / (units * opportunities)) * 1_000_000.0


@tool(args_schema=SigmaLevelArgs)
def calculate_sigma_level(
    defects: str = "", units: str = "", opportunities_per_unit: str = "1",
    dpmo: str = "",
) -> Result:
    """Defect rate on a common scale (sigma level) — how good the process is, expressed so any process compares to any other.

    A sigma level lets a call centre and a machine shop be compared on the same
    axis. Higher is better; roughly, 3 sigma is 66,800 defects per million and
    6 sigma is 3.4.

    Give either the raw counts or a DPMO you already have. Uses the standard
    1.5 sigma long-term shift, and says so in the result — a sigma level without
    that convention stated is ambiguous by a whole 1.5.
    """
    try:
        if dpmo.strip():
            dpmo_value = _num(dpmo, "the DPMO")
        else:
            d = _num(defects, "the number of defects")
            u = _num(units, "the number of units")
            o = _num(opportunities_per_unit, "the opportunities per unit")
            assert d is not None and u is not None and o is not None
            if u <= 0 or o <= 0:
                return _asks(
                    "Units and opportunities per unit both need to be greater "
                    "than zero. How many units were inspected?"
                )
            dpmo_value = _dpmo_value(d, u, o)
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert dpmo_value is not None
    if dpmo_value <= 0:
        sigma = 6.0 + SIGMA_SHIFT
    elif dpmo_value >= 1_000_000:
        sigma = 0.0
    else:
        yield_fraction = 1.0 - (dpmo_value / 1_000_000.0)
        sigma = float(stats.norm.ppf(yield_fraction)) + SIGMA_SHIFT

    return {
        "sigma_level": _fmt(sigma, 2),
        "dpmo": _fmt(dpmo_value, 1),
        "shift_assumption": "1.5σ long-term shift applied",
    }


def _cpk_values(mean: float, std_dev: float,
                usl: float | None, lsl: float | None) -> dict[str, Any]:
    """Cpk, Cp and the binding side. Shared by `calculate_cpk` and
    `post_improvement_cpk` — §69.6 permits the shared helper explicitly."""
    cpu = (usl - mean) / (3 * std_dev) if usl is not None else None
    cpl = (mean - lsl) / (3 * std_dev) if lsl is not None else None

    candidates = [(c, side) for c, side in ((cpu, "upper"), (cpl, "lower"))
                  if c is not None]
    cpk, binding = min(candidates, key=lambda pair: pair[0])
    cp = ((usl - lsl) / (6 * std_dev)
          if usl is not None and lsl is not None else None)
    return {"cpk": cpk, "cp": cp, "binding_limit": binding}


@tool(args_schema=CpkArgs)
def calculate_cpk(
    mean: str, std_dev: str, usl: str = "", lsl: str = ""
) -> Result:
    """Process capability (Cpk) — can the process meet spec as it runs today, given both where it sits and how much it varies.

    Cpk answers "will this process produce what the customer asked for?" and
    punishes two different problems: being off-centre, and being too variable.
    Rough reading: below 1.0 the process cannot hold spec, 1.33 is the usual
    minimum, 1.67 or better is strong.

    CHECK STABILITY FIRST. A capability figure computed across an unstable
    process is an average of two different processes and means nothing. If
    stability_assessment does not read "stable", coach that first.

    Give at least one spec limit. With both, you also get Cp, and the gap
    between Cp and Cpk is the centring problem.
    """
    try:
        m = _num(mean, "the process mean")
        sd = _num(std_dev, "the standard deviation")
        u = _num(usl, "the upper spec limit", required=False)
        low = _num(lsl, "the lower spec limit", required=False)
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert m is not None and sd is not None
    if sd <= 0:
        return _asks(
            "The standard deviation needs to be greater than zero — with zero "
            "variation there is no capability to compute. What spread did the "
            "measurements show?"
        )
    if u is None and low is None:
        return _asks(
            "I need at least one spec limit to compute capability. What is the "
            "upper or lower limit the customer requires?"
        )

    values = _cpk_values(m, sd, u, low)
    result: Result = {
        "cpk": _fmt(values["cpk"], 3),
        "binding_limit": values["binding_limit"],
    }
    if values["cp"] is not None:
        result["cp"] = _fmt(values["cp"], 3)
    return result


@tool(args_schema=DpmoArgs)
def calculate_dpmo(
    defects: str, units: str, opportunities_per_unit: str = "1"
) -> Result:
    """Defect rate per million chances (DPMO) — defects scaled so processes of different volume and complexity compare fairly.

    Counting defects alone is misleading: 50 defects in 100 forms is very
    different from 50 in 100,000, and a form with 20 fields has 20 chances to be
    wrong while a form with 3 has 3. DPMO normalises both.

    Count opportunities honestly. Inflating them is the classic way to make a
    process look better than it is.
    """
    try:
        d = _num(defects, "the number of defects")
        u = _num(units, "the number of units")
        o = _num(opportunities_per_unit, "the opportunities per unit")
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert d is not None and u is not None and o is not None
    if u <= 0 or o <= 0:
        return _asks(
            "Units and opportunities per unit both need to be greater than "
            "zero. How many units were inspected, and how many chances to be "
            "wrong does each one have?"
        )
    return {"dpmo": _fmt(_dpmo_value(d, u, o), 1)}


@tool(args_schema=YieldRtyArgs)
def calculate_yield_rty(
    step_yields: list[float] | None = None,
    step_units_and_defects: list[list[float]] | None = None,
) -> Result:
    """End-to-end yield (RTY, rolled throughput yield) — the share of work that clears every step first time, with no rework anywhere.

    This is the number that exposes the hidden factory. Each step can look
    excellent on its own and the end-to-end result still be poor, because the
    yields multiply: five steps at 95% is 77%, not 95%.

    Returns RTY beside the simple average of the step yields, and the gap
    between them. That gap IS the point of the tool — it is the rework nobody
    was counting.

    Needs at least two steps; a single step is just its own yield.
    """
    yields: list[float] = []
    if step_yields:
        yields = [_as_fraction(float(y)) for y in step_yields]
    elif step_units_and_defects:
        for pair in step_units_and_defects:
            if len(pair) != 2 or pair[0] <= 0:
                return _asks(
                    "Each step needs a [units, defects] pair with units above "
                    "zero. Could you give me the counts for each step in order?"
                )
            units, defects = float(pair[0]), float(pair[1])
            yields.append((units - defects) / units)
    else:
        return _asks(
            "I need either the yield of each step, or a [units, defects] pair "
            "per step. Which do you have?"
        )

    if len(yields) < 2:
        return _asks(
            "Rolled throughput yield needs at least two steps — with one step "
            "it is just that step's yield. What are the other steps in the "
            "process?"
        )
    if any(y < 0 or y > 1 for y in yields):
        return _asks(
            "One of the step yields is outside 0–100%. Could you check the "
            "figures?"
        )

    rty = float(np.prod(yields))
    simple = float(np.mean(yields))
    return {
        "rty": _fmt(rty, 4),
        "simple_average_yield": _fmt(simple, 4),
        "hidden_factory_gap": _fmt(simple - rty, 4),
        "step_count": str(len(yields)),
    }


@tool(args_schema=FtqArgs)
def calculate_ftq(
    units_processed: str, units_reworked_or_defective: str
) -> Result:
    """First-time quality at one step (FTQ) — the share that step gets right without rework.

    FTQ is per step. Chain the steps together with rolled throughput yield to
    see what the customer actually experiences.

    Count rework as a miss. A unit that came out right only because someone
    fixed it did not pass first time, and treating it as a pass is how the
    hidden factory stays hidden.
    """
    try:
        processed = _num(units_processed, "the units processed")
        bad = _num(units_reworked_or_defective, "the units reworked or defective")
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert processed is not None and bad is not None
    if processed <= 0:
        return _asks(
            "The number of units processed needs to be greater than zero. How "
            "many units went through the step?"
        )
    if bad > processed:
        return _asks(
            f"More units were reworked ({_fmt(bad)}) than processed "
            f"({_fmt(processed)}). Could you check those two figures?"
        )
    return {"ftq": _fmt((processed - bad) / processed, 4)}


@tool(args_schema=GrrArgs)
def calculate_grr(
    data_type: str = "variable",
    readings: list[list[list[float]]] | None = None,
    agreement_matrix: list[list[str]] | None = None,
) -> Result:
    """Measurement trust (Gage R&R) — how much of the variation you can see is the process, and how much is the measuring.

    Run this BEFORE trusting any baseline. If the measurement system is noisy,
    every number after it inherits the noise, and the team can spend weeks
    chasing variation that was never in the process.

    Two parts: repeatability is one person measuring the same thing twice;
    reproducibility is two people measuring the same thing.

    AIAG bands on percent study variation: under 10% acceptable, 10-30%
    marginal (usable if the cost of improving it is high), over 30%
    unacceptable — fix the measurement system before continuing.
    """
    if data_type.strip().lower().startswith("attr"):
        if not agreement_matrix:
            return _asks(
                "For attribute data I need the ratings each part received, one "
                "list per part. What did each appraiser call each part?"
            )
        agreed = sum(1 for ratings in agreement_matrix
                     if ratings and len(set(r.strip().lower() for r in ratings)) == 1)
        pct = (agreed / len(agreement_matrix)) * 100.0
        verdict = ("acceptable" if pct >= 90 else
                   "marginal" if pct >= 70 else "unacceptable")
        return {
            "pct_agreement": _fmt(pct, 1),
            "parts_in_full_agreement": str(agreed),
            "parts_assessed": str(len(agreement_matrix)),
            "verdict": verdict,
        }

    if not readings:
        return _asks(
            "For variable data I need the readings as operator by part by "
            "trial. Could you give me each operator's measurements of each "
            "part?"
        )

    try:
        data = np.array(readings, dtype=float)
    except (ValueError, TypeError):
        return _asks(
            "The readings need to be a rectangular set: every operator "
            "measuring every part the same number of times. Could you send "
            "them in that shape?"
        )
    if data.ndim != 3 or min(data.shape) < 1:
        return _asks(
            "The readings need three levels — operator, then part, then trial. "
            "Could you send them nested that way?"
        )

    n_op, n_part, n_trial = data.shape
    if n_trial < 2:
        return _asks(
            "Repeatability needs at least two trials per operator per part — "
            "one measurement cannot show whether it repeats. Could each "
            "appraiser measure each part at least twice?"
        )

    # AIAG MSA-4 ANOVA method.
    grand = data.mean()
    ss_total = float(((data - grand) ** 2).sum())
    ss_op = float(n_part * n_trial * ((data.mean(axis=(1, 2)) - grand) ** 2).sum())
    ss_part = float(n_op * n_trial * ((data.mean(axis=(0, 2)) - grand) ** 2).sum())
    cell = data.mean(axis=2)
    ss_cells = float(n_trial * ((cell - grand) ** 2).sum())
    ss_inter = ss_cells - ss_op - ss_part
    ss_err = ss_total - ss_cells

    df_op, df_part = n_op - 1, n_part - 1
    df_inter = df_op * df_part
    df_err = n_op * n_part * (n_trial - 1)

    ms_op = ss_op / df_op if df_op else 0.0
    ms_part = ss_part / df_part if df_part else 0.0
    ms_inter = ss_inter / df_inter if df_inter else 0.0
    ms_err = ss_err / df_err if df_err else 0.0

    var_rep = max(ms_err, 0.0)
    var_inter = max((ms_inter - ms_err) / n_trial, 0.0) if df_inter else 0.0
    var_op = (max((ms_op - ms_inter) / (n_part * n_trial), 0.0)
              if df_op else 0.0)
    var_reprod = var_op + var_inter
    var_grr = var_rep + var_reprod
    var_part = (max((ms_part - ms_inter) / (n_op * n_trial), 0.0)
                if df_part else 0.0)
    var_total = var_grr + var_part

    if var_total <= 0:
        return _asks(
            "These readings show no variation at all, so there is nothing to "
            "apportion between the process and the measurement. Could you "
            "check the data?"
        )

    pct_study = math.sqrt(var_grr / var_total) * 100.0
    verdict = ("acceptable" if pct_study < 10 else
               "marginal" if pct_study <= 30 else "unacceptable")
    return {
        "pct_study_variation": _fmt(pct_study, 1),
        "repeatability_pct": _fmt(math.sqrt(var_rep / var_total) * 100.0, 1),
        "reproducibility_pct": _fmt(math.sqrt(var_reprod / var_total) * 100.0, 1),
        "verdict": verdict,
    }


@tool(args_schema=SampleSizeProportionArgs)
def calculate_sample_size_proportion(
    expected_proportion: str, margin_of_error: str, confidence_level: str = "0.95"
) -> Result:
    """How many to sample, for a percentage — the count needed to pin a proportion within a stated margin.

    Use this when the thing being measured is a share: percent defective,
    percent on time, percent complete.

    If you have no idea what the proportion is, use 0.5. It gives the largest
    sample, which is the safe direction to be wrong in.
    """
    try:
        p = _num(expected_proportion, "the expected proportion")
        e = _num(margin_of_error, "the margin of error")
        conf = _num(confidence_level, "the confidence level")
    except _NeedsReformatting as e_:
        return _asks(e_.request)

    assert p is not None and e is not None and conf is not None
    p = _as_fraction(p) if p > 1 else p
    e = _as_fraction(e) if e > 1 else e
    conf = _as_fraction(conf) if conf > 1 else conf

    if not 0 < p < 1:
        return _asks(
            "The expected proportion needs to be between 0 and 1 (or 0% and "
            "100%). Roughly what share do you expect to be defective?"
        )
    if e <= 0:
        return _asks(
            "The margin of error needs to be greater than zero. How close does "
            "the estimate need to be — plus or minus how much?"
        )
    if not 0 < conf < 1:
        return _asks("The confidence level should be a fraction such as 0.95.")

    z = float(stats.norm.ppf(1 - (1 - conf) / 2))
    n = (z ** 2) * p * (1 - p) / (e ** 2)
    return {"required_n": str(math.ceil(n))}


@tool(args_schema=SampleSizeMeanArgs)
def calculate_sample_size_mean(
    estimated_std_dev: str, detectable_difference: str,
    confidence_level: str = "0.95", power: str = "0.80",
) -> Result:
    """How many to sample, for an average — the count needed to detect a difference of a stated size.

    Use this when comparing two averages: before and after, or line A against
    line B. It answers "how many do we need so that if the change is real, we
    will see it?"

    Returns the count PER GROUP for a two-sample comparison. The smaller the
    difference you want to catch, the more you need — halving the difference
    quadruples the sample.
    """
    try:
        sd = _num(estimated_std_dev, "the estimated standard deviation")
        delta = _num(detectable_difference, "the difference worth detecting")
        conf = _num(confidence_level, "the confidence level")
        pwr = _num(power, "the power")
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert sd is not None and delta is not None
    assert conf is not None and pwr is not None
    conf = _as_fraction(conf) if conf > 1 else conf
    pwr = _as_fraction(pwr) if pwr > 1 else pwr

    if sd <= 0:
        return _asks(
            "The standard deviation needs to be greater than zero. Roughly how "
            "much does the measurement vary?"
        )
    if delta <= 0:
        return _asks(
            "The difference worth detecting needs to be greater than zero. How "
            "big a change would matter to the customer?"
        )
    if not 0 < conf < 1 or not 0 < pwr < 1:
        return _asks(
            "Confidence and power should each be fractions such as 0.95 and "
            "0.80."
        )

    z_alpha = float(stats.norm.ppf(1 - (1 - conf) / 2))
    z_beta = float(stats.norm.ppf(pwr))
    n = 2 * ((sd ** 2) * ((z_alpha + z_beta) ** 2)) / (delta ** 2)
    return {"required_n": str(math.ceil(n))}


# ══════════════════════════════════════════════════════════════════════════
# ANALYSE — 5 tools
# ══════════════════════════════════════════════════════════════════════════


@tool(args_schema=TTestArgs)
def t_test(
    sample1: list[float], sample2: list[float],
    paired: bool = False, equal_variance: bool = False,
) -> Result:
    """Is the gap between two averages real? (t-test) — or could it just be noise.

    Use this when the team has two sets of measurements and wants to know
    whether the difference between them is worth acting on: before and after, or
    two operators, or two shifts.

    Runs Welch's t-test by default, which does not assume the two groups vary by
    the same amount. Only set equal_variance if the Belt has actually checked
    that. Set paired when the values come in matched pairs — the same units
    measured twice.

    A significant result says the difference is probably real. It does NOT say
    the difference is big enough to matter — that is the Belt's judgement, and
    it is a separate question from this number.
    """
    if len(sample1) < 2 or len(sample2) < 2:
        return _asks(
            "Each group needs at least two measurements for a t-test. How many "
            "readings do you have for each?"
        )
    if paired and len(sample1) != len(sample2):
        return _asks(
            f"A paired test needs the same number of values in each group — I "
            f"have {len(sample1)} and {len(sample2)}. Should this be an "
            f"unpaired comparison instead?"
        )

    a, b = np.array(sample1, dtype=float), np.array(sample2, dtype=float)
    if paired:
        outcome = stats.ttest_rel(a, b)
        df = float(len(a) - 1)
        method = "paired t-test"
    else:
        outcome = stats.ttest_ind(a, b, equal_var=equal_variance)
        df = float(getattr(outcome, "df", len(a) + len(b) - 2))
        method = "Student's t-test (equal variance assumed)" if equal_variance \
            else "Welch's t-test"

    p = float(outcome.pvalue)
    return {
        "t_statistic": _fmt(float(outcome.statistic), 4),
        "degrees_of_freedom": _fmt(df, 2),
        "p_value": _fmt(p, 6),
        "significant": _significant(p),
        "method": method,
    }


@tool(args_schema=ChiSquareArgs)
def chi_square_test(contingency_table: list[list[float]]) -> Result:
    """Are two categories related? (chi-square test) — association between two categorical variables.

    Use this when both things being compared are categories rather than
    measurements: shift against defect type, supplier against pass/fail.

    Needs expected counts of at least 5 in every cell. Below that the test is
    unreliable and the tool will say so rather than return a number the Belt
    would quote.

    Association is not causation. A significant result says the two vary
    together, not that one causes the other.
    """
    if len(contingency_table) < 2 or any(len(r) < 2 for r in contingency_table):
        return _asks(
            "A chi-square test needs at least two rows and two columns. Could "
            "you give me the counts as a table?"
        )
    lengths = {len(r) for r in contingency_table}
    if len(lengths) != 1:
        return _asks(
            "Every row of the table needs the same number of columns. Could "
            "you check the counts?"
        )

    table = np.array(contingency_table, dtype=float)
    if (table < 0).any():
        return _asks("Counts cannot be negative — could you check the table?")
    if table.sum() == 0:
        return _asks("The table is all zeros; there is nothing to test.")

    chi2, p, dof, expected = stats.chi2_contingency(table)
    if (expected < 5).any():
        smallest = float(expected.min())
        return _asks(
            f"This table has an expected count of {_fmt(smallest, 2)} in at "
            f"least one cell, and chi-square needs at least 5 everywhere to be "
            f"reliable. Could you collect more data, or combine some "
            f"categories?"
        )

    return {
        "chi_square_statistic": _fmt(float(chi2), 4),
        "degrees_of_freedom": str(int(dof)),
        "p_value": _fmt(float(p), 6),
        "significant": _significant(float(p)),
    }


@tool(args_schema=AnovaArgs)
def anova(groups: list[list[float]]) -> Result:
    """Do three or more groups differ? (ANOVA, analysis of variance)

    Use this instead of running several t-tests. Comparing three groups pairwise
    takes three tests, and each one carries its own chance of a false positive —
    ANOVA asks the question once.

    A significant result says at least one group differs from the others. It
    does not say which. That takes a follow-up comparison.
    """
    if len(groups) < 3:
        return _asks(
            f"ANOVA compares three or more groups and I have {len(groups)}. For "
            f"two groups, use the t-test instead."
        )
    if any(len(g) < 2 for g in groups):
        return _asks(
            "Each group needs at least two measurements. How many readings do "
            "you have per group?"
        )

    arrays = [np.array(g, dtype=float) for g in groups]
    outcome = stats.f_oneway(*arrays)
    k = len(arrays)
    n_total = sum(len(g) for g in arrays)
    p = float(outcome.pvalue)
    return {
        "f_statistic": _fmt(float(outcome.statistic), 4),
        "df_between": str(k - 1),
        "df_within": str(n_total - k),
        "p_value": _fmt(p, 6),
        "significant": _significant(p),
    }


@tool(args_schema=PearsonArgs)
def pearson_correlation(x_values: list[float], y_values: list[float]) -> Result:
    """Do two numbers move together? (Pearson correlation) — strength and direction, not cause.

    Use this to check whether a suspected driver actually tracks the outcome.

    CORRELATION IS NOT CAUSATION, and this is the tool most often misread as
    proving it. A strong r says the two move together; it says nothing about
    which drives which, or whether a third thing drives both. A root cause needs
    a stated mechanism as well as a number.

    Wants at least 10 paired points. Below that it still returns a result, with
    a warning — the Belt decides whether to trust it, not the tool.
    """
    if len(x_values) != len(y_values):
        return _asks(
            f"The two lists need to be the same length and paired by position "
            f"— I have {len(x_values)} and {len(y_values)}."
        )
    if len(x_values) < 3:
        return _asks(
            "Correlation needs at least three paired points. How many pairs do "
            "you have?"
        )

    x, y = np.array(x_values, dtype=float), np.array(y_values, dtype=float)
    if x.std() == 0 or y.std() == 0:
        return _asks(
            "One of the two sets is a constant — it never changes — so there is "
            "no relationship to measure. Could you check the data?"
        )

    r, p = stats.pearsonr(x, y)
    r = float(r)
    magnitude = abs(r)
    strength = ("negligible" if magnitude < 0.1 else
                "weak" if magnitude < 0.3 else
                "moderate" if magnitude < 0.5 else "strong")

    result: Result = {
        "r": _fmt(r, 4),
        "r_squared": _fmt(r * r, 4),
        "p_value": _fmt(float(p), 6),
        "strength_label": strength,
    }
    if len(x_values) < 10:
        result["sample_size_warning"] = (
            f"Only {len(x_values)} paired points. The methodology floor is 10; "
            f"below it the correlation is unstable and can move a lot with one "
            f"more observation. Treat this as indicative and say so."
        )
    return result


@tool(args_schema=LinearRegressionArgs)
def linear_regression(x_values: list[float], y_values: list[float]) -> Result:
    """How much does Y change when X changes? (simple linear regression, OLS) — fits Y = a + bX.

    Correlation says whether two things move together; regression says by how
    much. Use it after pearson_correlation, on the same pair, when the team
    needs to predict or to size an effect.

    The slope is the practical number: "every extra hour of queue adds 0.4
    defects". R-squared is the share of the variation the line explains — a
    strong slope with a low R-squared means the relationship is real but
    something else is driving most of the outcome.
    """
    if len(x_values) != len(y_values):
        return _asks(
            f"The two lists need to be the same length and paired by position "
            f"— I have {len(x_values)} and {len(y_values)}."
        )
    if len(x_values) < 3:
        return _asks(
            "Regression needs at least three paired points. How many pairs do "
            "you have?"
        )

    x, y = np.array(x_values, dtype=float), np.array(y_values, dtype=float)
    if x.std() == 0:
        return _asks(
            "Every x value is the same, so there is no change in the driver to "
            "regress against. Could you check the data?"
        )

    fit = stats.linregress(x, y)
    slope, intercept = float(fit.slope), float(fit.intercept)
    sign = "+" if intercept >= 0 else "−"
    result: Result = {
        "slope": _fmt(slope, 4),
        "intercept": _fmt(intercept, 4),
        "r_squared": _fmt(float(fit.rvalue) ** 2, 4),
        "equation_string": (
            f"y = {_fmt(slope, 4)}x {sign} {_fmt(abs(intercept), 4)}"
        ),
        "p_value": _fmt(float(fit.pvalue), 6),
    }
    if len(x_values) < 10:
        result["sample_size_warning"] = (
            f"Only {len(x_values)} paired points, against a methodology floor "
            f"of 10. Treat the fit as indicative and say so."
        )
    return result


# ══════════════════════════════════════════════════════════════════════════
# IMPROVE — 1 tool
# ══════════════════════════════════════════════════════════════════════════

#: The two level labels a design matrix may use, normalised to low/high. A
#: designed experiment runs each factor at two settings; which words the Belt
#: used for them is not something to make them re-enter.
_LOW_LABELS = {"low", "lo", "-", "-1", "−1", "0", "a", "minus"}
_HIGH_LABELS = {"high", "hi", "+", "+1", "1", "b", "plus"}


@tool(args_schema=DoeMainEffectsArgs)
def calculate_doe_main_effects(
    factors: list[str], design_matrix: list[list[str]], responses: list[float]
) -> Result:
    """Which factor actually mattered? (DOE main effects) — the effect of each factor from a designed experiment.

    Use this after the team has run a designed experiment: several factors,
    each set high or low, in a planned pattern of runs.

    The main effect of a factor is the average response when it ran high minus
    the average when it ran low. Ranked largest first, this tells the team where
    to spend their effort — and often shows that a factor everyone argued about
    barely moves the outcome.

    Only for a real DOE. If the team ran one factor at a time, or reasoned from
    root cause without experimenting, that is a legitimate choice and this is
    not the tool for it.
    """
    if not factors or not design_matrix or not responses:
        return _asks(
            "I need the factor names, the design matrix and the measured "
            "response for each run. Which of those do you have?"
        )
    if len(design_matrix) != len(responses):
        return _asks(
            f"There are {len(design_matrix)} runs in the design but "
            f"{len(responses)} responses. Could you check they line up?"
        )
    if any(len(row) != len(factors) for row in design_matrix):
        return _asks(
            f"Every run needs one level per factor — {len(factors)} columns to "
            f"match {', '.join(factors)}. Could you check the design matrix?"
        )

    y = np.array(responses, dtype=float)
    effects: dict[str, float] = {}
    for i, name in enumerate(factors):
        highs, lows = [], []
        for run, response in zip(design_matrix, y):
            label = str(run[i]).strip().lower()
            if label in _HIGH_LABELS:
                highs.append(response)
            elif label in _LOW_LABELS:
                lows.append(response)
            else:
                return _asks(
                    f"I did not recognise the level '{run[i]}' for factor "
                    f"'{name}'. Could you use low/high, -/+ or -1/1?"
                )
        if not highs or not lows:
            return _asks(
                f"Factor '{name}' only ran at one level, so its effect cannot "
                f"be separated. Was it held constant across every run?"
            )
        effects[name] = float(np.mean(highs) - np.mean(lows))

    ranked = sorted(effects, key=lambda n: abs(effects[n]), reverse=True)
    return {
        "main_effects": "; ".join(f"{n}: {_fmt(effects[n], 4)}" for n in ranked),
        "ranked_factors": ", ".join(ranked),
        "largest_effect": ranked[0],
    }


# ══════════════════════════════════════════════════════════════════════════
# CONTROL — 5 tools
# ══════════════════════════════════════════════════════════════════════════


@tool(args_schema=XbarRArgs)
def xbar_r_chart_limits(subgroups: list[list[float]]) -> Result:
    """Control limits for batched measurements (X-bar R chart) — the lines that separate normal variation from a real signal.

    Use this when the team measures several units at a time: five parts an hour,
    four calls a shift.

    Control limits are NOT spec limits. They say what this process does when
    nothing unusual is happening; spec limits say what the customer wants. A
    process can be perfectly in control and still fail spec.

    If the team has one measurement per period, use imr_chart_limits instead.
    Never coach them into inventing subgroups to fit this chart — subgroups that
    were not collected as subgroups give meaningless limits.
    """
    if len(subgroups) < 2:
        return _asks(
            "I need at least two subgroups to work out the limits. How many "
            "periods of data do you have?"
        )
    sizes = {len(g) for g in subgroups}
    if len(sizes) != 1:
        return _asks(
            f"Every subgroup needs the same number of measurements — I see "
            f"sizes {sorted(sizes)}. If the batch size varies, a p-chart or an "
            f"I-MR chart may be the right choice instead."
        )

    n = sizes.pop()
    if n < 2:
        return _asks(
            "A subgroup needs at least two measurements. With one measurement "
            "per period, use the I-MR chart instead — that is what it is for."
        )
    if n not in SHEWHART:
        return _asks(
            f"Subgroup size {n} is outside the standard constant table (2 to "
            f"10). Could you use a smaller subgroup, or an I-MR chart?"
        )

    const = SHEWHART[n]
    data = np.array(subgroups, dtype=float)
    x_bar_bar = float(data.mean())
    r_bar = float((data.max(axis=1) - data.min(axis=1)).mean())

    return {
        "x_bar_bar": _fmt(x_bar_bar, 4),
        "ucl_x": _fmt(x_bar_bar + const["A2"] * r_bar, 4),
        "lcl_x": _fmt(x_bar_bar - const["A2"] * r_bar, 4),
        "r_bar": _fmt(r_bar, 4),
        "ucl_r": _fmt(const["D4"] * r_bar, 4),
        "lcl_r": _fmt(const["D3"] * r_bar, 4),
        "subgroup_size": str(n),
    }


@tool(args_schema=ImrArgs)
def imr_chart_limits(values: list[float]) -> Result:
    """Control limits for one-at-a-time measurements (I-MR, individuals and moving range).

    THIS IS THE DEFAULT CHOICE whenever the team has one measurement per period
    — which is most service and transactional work: one invoice error rate a
    week, one cycle time a day.

    The moving range between consecutive points is what stands in for
    within-subgroup variation when there are no subgroups.

    Do not coach a team into grouping their data to use an X-bar R chart
    instead. Subgroups that were not collected as subgroups produce limits that
    look authoritative and mean nothing.
    """
    if len(values) < 2:
        return _asks(
            "I need at least two measurements to compute a moving range. How "
            "many periods of data do you have?"
        )

    x = np.array(values, dtype=float)
    x_bar = float(x.mean())
    moving_ranges = np.abs(np.diff(x))
    mr_bar = float(moving_ranges.mean())

    return {
        "x_bar": _fmt(x_bar, 4),
        "ucl_i": _fmt(x_bar + IMR_E2 * mr_bar, 4),
        "lcl_i": _fmt(x_bar - IMR_E2 * mr_bar, 4),
        "mr_bar": _fmt(mr_bar, 4),
        "ucl_mr": _fmt(IMR_D4 * mr_bar, 4),
        "point_count": str(len(values)),
    }


@tool(args_schema=PChartArgs)
def p_chart_limits(subgroups: list[dict]) -> Result:
    """Control limits for a pass/fail rate (p-chart) — for when the batch size changes between periods.

    Use this when the team counts how many of a batch were defective and the
    batch size varies: 200 invoices one week, 340 the next.

    THE LIMITS ARE NOT A SINGLE PAIR OF LINES. They move with the batch size —
    a small batch has wider limits because a small batch is noisier. This tool
    returns the centre line, the formula, and the limits for each period.

    Present it as a stepped chart, never as two flat lines, or the team will
    read a normal small-batch result as a signal.
    """
    if len(subgroups) < 2:
        return _asks(
            "I need at least two periods to work out a p-chart. How many "
            "batches do you have?"
        )

    total_defectives = 0.0
    total_n = 0.0
    parsed: list[tuple[float, float]] = []
    for i, row in enumerate(subgroups, 1):
        try:
            d = float(row["defectives"])
            n = float(row["n"])
        except (KeyError, TypeError, ValueError):
            return _asks(
                f"Period {i} needs a 'defectives' count and an 'n' batch size. "
                f"Could you give me both for each period?"
            )
        if n <= 0:
            return _asks(f"Period {i} has a batch size of zero — could you check it?")
        if d > n:
            return _asks(
                f"Period {i} has more defectives ({_fmt(d)}) than units "
                f"({_fmt(n)}). Could you check those figures?"
            )
        parsed.append((d, n))
        total_defectives += d
        total_n += n

    p_bar = total_defectives / total_n
    spread = math.sqrt(p_bar * (1 - p_bar))
    per_subgroup = []
    for i, (_d, n) in enumerate(parsed, 1):
        margin = 3 * spread / math.sqrt(n)
        ucl = min(1.0, p_bar + margin)
        lcl = max(0.0, p_bar - margin)
        per_subgroup.append(
            f"n={_fmt(n)}: UCL {_fmt(ucl, 4)}, LCL {_fmt(lcl, 4)}"
        )

    return {
        "p_bar": _fmt(p_bar, 4),
        "ucl_note": (
            f"Limits vary by batch size: p̄ ± 3·√(p̄(1−p̄)/n). With p̄ = "
            f"{_fmt(p_bar, 4)} the limits per period are — "
            + "; ".join(per_subgroup)
        ),
        "period_count": str(len(parsed)),
    }


@tool(args_schema=CChartArgs)
def c_chart_limits(counts: list[float]) -> Result:
    """Control limits for defect counts (c-chart) — for when the area of opportunity is constant.

    Use this when the team counts defects rather than defective units, and the
    thing being inspected is the same size every time: scratches per panel,
    errors per report, complaints per week.

    If the area of opportunity changes between periods — a report that is 3
    pages one week and 30 the next — this is the wrong chart, because a higher
    count may just mean a bigger opportunity.

    The lower limit is clipped at zero: a negative defect count does not exist.
    """
    if len(counts) < 2:
        return _asks(
            "I need at least two periods to work out the limits. How many "
            "periods of counts do you have?"
        )
    values = np.array(counts, dtype=float)
    if (values < 0).any():
        return _asks("Defect counts cannot be negative — could you check them?")

    c_bar = float(values.mean())
    spread = 3 * math.sqrt(c_bar)
    return {
        "c_bar": _fmt(c_bar, 4),
        "ucl": _fmt(c_bar + spread, 4),
        "lcl": _fmt(max(0.0, c_bar - spread), 4),
        "period_count": str(len(counts)),
    }


@tool(args_schema=PostImprovementCpkArgs)
def post_improvement_cpk(
    mean: str, std_dev: str, baseline_cpk: str,
    usl: str = "", lsl: str = "",
) -> Result:
    """Capability after the fix (post-improvement Cpk) — the same capability figure on the new data, set against the baseline.

    Use this in Control, on data collected after the improvement is in place, to
    show what actually changed.

    Re-check stability first, exactly as in Measure. If the new process is not
    yet stable, a capability figure on it means no more than one computed on an
    unstable baseline did.

    Returns the improvement delta against the baseline Cpk — that difference is
    the number the Control gate is graded on, not the new Cpk on its own.
    """
    try:
        m = _num(mean, "the post-improvement mean")
        sd = _num(std_dev, "the post-improvement standard deviation")
        base = _num(baseline_cpk, "the baseline Cpk")
        u = _num(usl, "the upper spec limit", required=False)
        low = _num(lsl, "the lower spec limit", required=False)
    except _NeedsReformatting as e:
        return _asks(e.request)

    assert m is not None and sd is not None and base is not None
    if sd <= 0:
        return _asks(
            "The standard deviation needs to be greater than zero. What spread "
            "did the post-improvement measurements show?"
        )
    if u is None and low is None:
        return _asks(
            "I need at least one spec limit to compute capability. What is the "
            "upper or lower limit the customer requires?"
        )

    values = _cpk_values(m, sd, u, low)
    cpk = values["cpk"]
    result: Result = {
        "cpk": _fmt(cpk, 3),
        "improvement_delta": _fmt(cpk - base, 3),
        "meets_target": "yes" if cpk >= 1.33 else "no",
        "binding_limit": values["binding_limit"],
    }
    if values["cp"] is not None:
        result["cp"] = _fmt(values["cp"], 3)
    return result


# ══════════════════════════════════════════════════════════════════════════
# The inventory, and the per-phase binding
# ══════════════════════════════════════════════════════════════════════════

#: §29.2 — the universal seven, passed to **every** phase executor: the three
#: `rag_lookup_*` tools (step 5.2, `knowledge/tools.py`) plus
#: `propose_template`, `propose_diagram`, `check_gate_status` and
#: `request_human_approval`, which land with the executor at stage 6. The count
#: lives here because §30's ceiling is a statement about the *bound* total, and
#: the partition below is the half of that total this file owns. **When stage 6
#: assembles `UNIVERSAL_TOOLS`, that list must assert its own length against
#: this constant** — otherwise the per-phase totals below stop meaning what
#: they say.
UNIVERSAL_TOOL_COUNT = 7

#: §30 — the ceiling the per-phase binding exists to respect. Tool-selection
#: quality degrades past roughly 10–15 tools per agent, which is the whole
#: reason tool sets are per phase rather than universal. **A new tool that
#: would push a phase past this requires an amendment, not a routine
#: addition.**
PHASE_TOOL_CEILING = 16

#: §30's binding table, restated as the partition itself (§60.6's inventory
#: order within each phase). The executor composes a phase's tools as
#: `UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]` (§18) — so the totals
#: are 8 / 15 / 12 / 8 / 12 and the maximum is Measure's 15, one under the
#: ceiling.
#:
#: **The keys are `PHASE_ORDER`'s five names** (`phases/mappers_common.py`),
#: spelled literally rather than imported: `knowledge/` does not depend on
#: `phases/`, and a test asserts the two agree.
#:
#: **Measure binds no chart-limit tool, and that is a specified absence**
#: (§69.7), not an omission — `stability_assessment` is coached as a visual
#: read, and the chart-limit tools belong to Control.
COMPUTATION_TOOLS_BY_PHASE: dict[str, list[BaseTool]] = {
    "define": [
        calculate_expected_savings,
    ],
    "measure": [
        calculate_sigma_level,
        calculate_cpk,
        calculate_dpmo,
        calculate_yield_rty,
        calculate_ftq,
        calculate_grr,
        calculate_sample_size_proportion,
        calculate_sample_size_mean,
    ],
    "analyse": [
        t_test,
        chi_square_test,
        anova,
        pearson_correlation,
        linear_regression,
    ],
    "improve": [
        calculate_doe_main_effects,
    ],
    "control": [
        xbar_r_chart_limits,
        imr_chart_limits,
        p_chart_limits,
        c_chart_limits,
        post_improvement_cpk,
    ],
}

#: All twenty, in §60.6's inventory order — **derived from the partition rather
#: than restated beside it**, so the flat list and the binding cannot drift
#: into disagreeing about which tool belongs to which phase.
#: 1 + 8 + 5 + 1 + 5 = 20.
COMPUTATION_TOOLS: list[BaseTool] = [
    tool_ for phase_tools in COMPUTATION_TOOLS_BY_PHASE.values()
    for tool_ in phase_tools
]

__all__ = [
    "COMPUTATION_TOOLS",
    "COMPUTATION_TOOLS_BY_PHASE",
    "PHASE_TOOL_CEILING",
    "SHEWHART",
    "SIGMA_SHIFT",
    "UNIVERSAL_TOOL_COUNT",
    "calculate_expected_savings",
    "calculate_sigma_level",
    "calculate_cpk",
    "calculate_dpmo",
    "calculate_yield_rty",
    "calculate_ftq",
    "calculate_grr",
    "calculate_sample_size_proportion",
    "calculate_sample_size_mean",
    "t_test",
    "chi_square_test",
    "anova",
    "pearson_correlation",
    "linear_regression",
    "calculate_doe_main_effects",
    "xbar_r_chart_limits",
    "imr_chart_limits",
    "p_chart_limits",
    "c_chart_limits",
    "post_improvement_cpk",
]
