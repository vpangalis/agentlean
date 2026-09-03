"""Pydantic arg schemas for the twenty computation tools — procedure step 5.3.

Canonical: **§31** (tool arg schemas and docstrings), **§69** (the twenty
interfaces, S-F37–S-F56), **§60.6 — S-F24** (the EARS behaviours binding on all
twenty). Architecture §30 (per-phase binding), §7 (the typing law).

EVERY TOOL HAS ITS OWN SCHEMA — NO RAW SIGNATURE INFERENCE
----------------------------------------------------------
§31: *"No tools with raw signature inference — inferred schemas produce vague
parameter descriptions, and the parameter description is what the model reads
when deciding how to call."* Twenty tools, twenty schemas, one each.

**Parameterised grouping is BANNED** (§30, S-F24 B4), which is why there are
twenty schemas and not, say, four families. `CpkArgs` and `PostImprovementCpkArgs`
are separate despite sharing three fields, because the two tools are separate.

WHY THE SCALAR INPUTS ARE `str` AND NOT `float`
-----------------------------------------------
This is the load-bearing choice in this file, and it follows from two behaviours
that would otherwise contradict each other:

  * **B2** — *"parse what it needs out of the string at the point of use, since
    every captured field is a `str`"*. §7's typing law makes every captured
    field a string: `baseline_estimate` is `"12.3% invoice error rate, measured
    over Q2 2026"`, not `12.3`.
  * **B3** — *"unable to parse its input, return a clear reformatting request to
    the Belt rather than **raising** or guessing"*.

Declaring `mean: float` would satisfy neither. Pydantic would coerce `"12.3"`
happily and then **raise** a `ValidationError` on `"12.3% error rate"` — the
exact behaviour B3 forbids, at a layer the tool cannot intercept to produce a
plain-language request. So every scalar a Belt might have written as prose is
`str`, and `computation._num()` does the parsing and produces the request.

**Structured collections stay typed.** `subgroups`, `contingency_table`,
`x_values` and the rest are `list[...]`: they are built by the coach from data
it has read, not lifted from a captured-field sentence, and a malformed one is a
genuine call error that Pydantic should reject. The split is *"prose the Belt
typed"* versus *"a table the coach assembled"*, and the semantic checks those
collections need — at least two steps, equal subgroup sizes, expected cell
counts ≥ 5 — are methodology preconditions, which §69.1 says are NOT argument
validation. Those live in the tools and return requests.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# ── Define — 1 tool (S-F37) ───────────────────────────────────────────────


class ExpectedSavingsArgs(BaseModel):
    """Args for `calculate_expected_savings`."""

    baseline_value: str = Field(
        description="Where the metric sits today, as the Belt stated it. "
                    "Example: '12.3' or '12.3% invoice error rate'."
    )
    target_value: str = Field(
        description="Where the metric should be after the improvement. "
                    "Same unit as baseline_value. Example: '5.0'."
    )
    unit_cost: str = Field(
        description="What one defect, or one unit of the gap, costs. "
                    "Example: '45' or '£45 per rework'. If the Belt has not "
                    "established a cost basis, pass what they said — the tool "
                    "will ask for it rather than invent one."
    )
    annual_volume: str = Field(
        description="How many units run through the process in a year. "
                    "Example: '120000'."
    )


# ── Measure — 8 tools (S-F38–S-F45) ───────────────────────────────────────


class SigmaLevelArgs(BaseModel):
    """Args for `calculate_sigma_level`. Give the counts OR the dpmo."""

    defects: str = Field(default="", description="Number of defects found.")
    units: str = Field(default="", description="Number of units inspected.")
    opportunities_per_unit: str = Field(
        default="1", description="Chances to get it wrong on each unit."
    )
    dpmo: str = Field(
        default="",
        description="Defects per million opportunities, if already known. "
                    "Supply this OR the three counts above.",
    )


class CpkArgs(BaseModel):
    """Args for `calculate_cpk`. At least one spec limit is required."""

    mean: str = Field(description="Process average.")
    std_dev: str = Field(description="Process standard deviation.")
    usl: str = Field(default="", description="Upper spec limit, if there is one.")
    lsl: str = Field(default="", description="Lower spec limit, if there is one.")


class DpmoArgs(BaseModel):
    """Args for `calculate_dpmo`."""

    defects: str = Field(description="Number of defects found.")
    units: str = Field(description="Number of units inspected.")
    opportunities_per_unit: str = Field(
        default="1", description="Chances to get it wrong on each unit."
    )


class YieldRtyArgs(BaseModel):
    """Args for `calculate_yield_rty`. Give yields OR units-and-defects."""

    step_yields: list[float] = Field(
        default_factory=list,
        description="First-pass yield of each step, as fractions (0.98) or "
                    "percentages (98). At least 2 steps.",
    )
    step_units_and_defects: list[list[float]] = Field(
        default_factory=list,
        description="Alternative to step_yields: one [units, defects] pair per "
                    "step, in process order.",
    )


class FtqArgs(BaseModel):
    """Args for `calculate_ftq`."""

    units_processed: str = Field(description="Units that entered the step.")
    units_reworked_or_defective: str = Field(
        description="Units that needed rework or were scrapped at this step."
    )


class GrrArgs(BaseModel):
    """Args for `calculate_grr`."""

    data_type: str = Field(
        default="variable",
        description="'variable' for measured readings, 'attribute' for "
                    "pass/fail or category judgements.",
    )
    readings: list[list[list[float]]] = Field(
        default_factory=list,
        description="VARIABLE data, indexed [operator][part][trial]. Every "
                    "operator measures every part the same number of times.",
    )
    agreement_matrix: list[list[str]] = Field(
        default_factory=list,
        description="ATTRIBUTE data, indexed [part][rating]. All ratings for "
                    "one part across every operator and trial.",
    )


class SampleSizeProportionArgs(BaseModel):
    """Args for `calculate_sample_size_proportion`."""

    expected_proportion: str = Field(
        description="Roughly what share you expect to be defective, as a "
                    "fraction (0.12) or a percentage (12%). Use 0.5 if unsure "
                    "— it gives the largest, safest sample."
    )
    margin_of_error: str = Field(
        description="How close the estimate must be, in the same units. "
                    "Example: '0.03' for plus or minus three points."
    )
    confidence_level: str = Field(
        default="0.95", description="Usually 0.95."
    )


class SampleSizeMeanArgs(BaseModel):
    """Args for `calculate_sample_size_mean`."""

    estimated_std_dev: str = Field(
        description="Best estimate of the process standard deviation."
    )
    detectable_difference: str = Field(
        description="The smallest change worth detecting, in the same units."
    )
    confidence_level: str = Field(default="0.95", description="Usually 0.95.")
    power: str = Field(
        default="0.80",
        description="Chance of detecting the difference if it is real. "
                    "Usually 0.80.",
    )


# ── Analyse — 5 tools (S-F46–S-F50) ───────────────────────────────────────


class TTestArgs(BaseModel):
    """Args for `t_test`."""

    sample1: list[float] = Field(description="Raw values from the first group.")
    sample2: list[float] = Field(description="Raw values from the second group.")
    paired: bool = Field(
        default=False,
        description="True when each value in sample1 pairs with the value at "
                    "the same position in sample2 — before/after on the same "
                    "units. False for two independent groups.",
    )
    equal_variance: bool = Field(
        default=False,
        description="Leave False unless the Belt has stated the two groups "
                    "have equal variance. False runs Welch's t-test, which is "
                    "the safe default.",
    )


class ChiSquareArgs(BaseModel):
    """Args for `chi_square_test`."""

    contingency_table: list[list[float]] = Field(
        description="Counts, as rows by columns. Example: "
                    "[[30, 20], [15, 35]] for two categories by two outcomes."
    )


class AnovaArgs(BaseModel):
    """Args for `anova`."""

    groups: list[list[float]] = Field(
        description="One list of raw values per group. At least 3 groups."
    )


class PearsonArgs(BaseModel):
    """Args for `pearson_correlation`."""

    x_values: list[float] = Field(description="The suspected driver.")
    y_values: list[float] = Field(
        description="The outcome. Same length as x_values, paired by position."
    )


class LinearRegressionArgs(BaseModel):
    """Args for `linear_regression`."""

    x_values: list[float] = Field(description="The driver (independent variable).")
    y_values: list[float] = Field(
        description="The outcome (dependent variable). Paired with x_values."
    )


# ── Improve — 1 tool (S-F51) ──────────────────────────────────────────────


class DoeMainEffectsArgs(BaseModel):
    """Args for `calculate_doe_main_effects`."""

    factors: list[str] = Field(
        description="Factor names, in the same column order as design_matrix."
    )
    design_matrix: list[list[str]] = Field(
        description="One row per experimental run; each cell is the level that "
                    "factor ran at. Use 'low'/'high', '-'/'+' or '-1'/'1'."
    )
    responses: list[float] = Field(
        description="The measured output of each run, in the same row order."
    )


# ── Control — 5 tools (S-F52–S-F56) ───────────────────────────────────────


class XbarRArgs(BaseModel):
    """Args for `xbar_r_chart_limits`."""

    subgroups: list[list[float]] = Field(
        description="One list of measurements per subgroup. Every subgroup "
                    "must be the same size, and that size must be at least 2."
    )


class ImrArgs(BaseModel):
    """Args for `imr_chart_limits`."""

    values: list[float] = Field(
        description="One measurement per period, in time order. At least 2."
    )


class PChartArgs(BaseModel):
    """Args for `p_chart_limits`."""

    subgroups: list[dict] = Field(
        description="One {'defectives': n, 'n': m} per period. The batch size "
                    "'n' may differ between periods — that is what a p-chart "
                    "is for."
    )


class CChartArgs(BaseModel):
    """Args for `c_chart_limits`."""

    counts: list[float] = Field(
        description="Defect count per unit or per period, in time order. The "
                    "area of opportunity must be constant across periods."
    )


class PostImprovementCpkArgs(BaseModel):
    """Args for `post_improvement_cpk`."""

    mean: str = Field(description="Process average AFTER the improvement.")
    std_dev: str = Field(
        description="Process standard deviation AFTER the improvement."
    )
    usl: str = Field(default="", description="Upper spec limit, if there is one.")
    lsl: str = Field(default="", description="Lower spec limit, if there is one.")
    baseline_cpk: str = Field(
        description="The Cpk measured before the improvement, so the tool can "
                    "report the delta."
    )


__all__ = [
    "ExpectedSavingsArgs",
    "SigmaLevelArgs",
    "CpkArgs",
    "DpmoArgs",
    "YieldRtyArgs",
    "FtqArgs",
    "GrrArgs",
    "SampleSizeProportionArgs",
    "SampleSizeMeanArgs",
    "TTestArgs",
    "ChiSquareArgs",
    "AnovaArgs",
    "PearsonArgs",
    "LinearRegressionArgs",
    "DoeMainEffectsArgs",
    "XbarRArgs",
    "ImrArgs",
    "PChartArgs",
    "CChartArgs",
    "PostImprovementCpkArgs",
]
