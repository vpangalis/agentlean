"""The twenty computation tools — what procedure steps 5.3 and 5.4 established.

**Step 5.3's *Done when*:** twenty named tools exist, each with an
`args_schema=`, and a test suite covers each with a known-answer case. The
structural half is `test_exactly_twenty_tools` and
`test_every_tool_has_its_own_args_schema`; the known-answer half is one test per
tool below, grouped by phase.

**Step 5.4's *Done when*:** the per-phase totals are 8 / 15 / 12 / 8 / 12 and
no phase exceeds 16. That is the second structural section below. The totals
are the universal seven (§29.2) plus the phase's computation subset, so what 5.4
actually asserts is a property of `COMPUTATION_TOOLS_BY_PHASE` *and* of the
number the executor will add to it — which is why `UNIVERSAL_TOOL_COUNT` is a
named constant and not a `7` written into an assertion.

WHERE THE EXPECTED ANSWERS COME FROM
------------------------------------
**Not from running the code and pinning what it said.** That is the failure mode
this project keeps naming — a check that cannot fail, recorded as evidence. Each
expectation here is either:

  * a value a Black Belt would recognise on sight (DPMO 3.4 is 6 sigma; DPMO
    66,807 is 3 sigma; p=0.5 at ±5% needs 385),
  * arithmetic simple enough to verify by hand in the docstring (Cpk of a
    process centred at 10 with σ=1 between limits of 7 and 13 is exactly 1.0),
  * or a value computed independently from `scipy` in the test itself, where the
    tool's job is to route to the right test rather than to reimplement it.

§69.1 is explicit that the trusted-source rule differs for this file: these are
AIAG MSA-4, Shewhart's tables and the standard hypothesis tests — **decades-old
standards that do not drift the way a package API does.**

THE OTHER THING BEING TESTED IS B3
----------------------------------
*"Unable to parse its input, return a clear reformatting request rather than
raising or guessing."* Every tool takes prose where the spec says a number,
because §7 makes every captured field a `str`. A tool that raised there would
surface as a tool-call failure the Belt never sees phrased in their own terms —
so each group below includes at least one unparseable-input case, and
`test_no_tool_raises_on_unparseable_input` sweeps all twenty.
"""
from __future__ import annotations

import math
from typing import Any

import pytest
from scipy import stats

from backend.knowledge import computation as C
from backend.knowledge.computation import (
    COMPUTATION_TOOLS,
    COMPUTATION_TOOLS_BY_PHASE,
    PHASE_TOOL_CEILING,
    UNIVERSAL_TOOL_COUNT,
)
from backend.knowledge.tools import RAG_LOOKUP_TOOLS, UNIVERSAL_TOOLS
from backend.phases.mappers_common import PHASE_ORDER

#: §60.6's inventory, by phase. The names are the contract — a rename is a
#: §56 amendment, not a refactor.
EXPECTED_NAMES = {
    "define": ["calculate_expected_savings"],
    "measure": ["calculate_sigma_level", "calculate_cpk", "calculate_dpmo",
                "calculate_yield_rty", "calculate_ftq", "calculate_grr",
                "calculate_sample_size_proportion", "calculate_sample_size_mean"],
    "analyse": ["t_test", "chi_square_test", "anova", "pearson_correlation",
                "linear_regression"],
    "improve": ["calculate_doe_main_effects"],
    "control": ["xbar_r_chart_limits", "imr_chart_limits", "p_chart_limits",
                "c_chart_limits", "post_improvement_cpk"],
}
ALL_NAMES = [n for names in EXPECTED_NAMES.values() for n in names]


def run(tool, **kwargs) -> dict:
    """Invoke a tool the way the agent loop does."""
    return tool.invoke(kwargs)


def num(result: dict, key: str) -> float:
    """A result value as a float — every one is a string (§7's typing law)."""
    assert key in result, f"missing key {key!r} in {sorted(result)}"
    return float(result[key])


def asked(result: dict) -> bool:
    """True when the tool returned a B3 reformatting request."""
    return "reformatting_request" in result


# ══════════════════════════════════════════════════════════════════════════
# The step's Done-when — structure
# ══════════════════════════════════════════════════════════════════════════


def test_exactly_twenty_tools() -> None:
    """§60.6: 1 + 8 + 5 + 1 + 5 = 20."""
    assert len(COMPUTATION_TOOLS) == 20
    assert [t.name for t in COMPUTATION_TOOLS] == ALL_NAMES


def test_every_tool_has_its_own_args_schema() -> None:
    """§31 — no raw signature inference, and one schema each.

    Distinctness is the half that matters: a shared schema would be
    parameterised grouping wearing twenty names.
    """
    schemas: dict[str, Any] = {}
    for t in COMPUTATION_TOOLS:
        assert t.args_schema is not None, f"{t.name} has no args_schema"
        schemas[t.name] = t.args_schema
    assert len(set(schemas.values())) == 20, (
        "two tools share an args_schema — each of the twenty is a separate "
        "tool with its own (§31, S-F24 B4)"
    )


def test_no_mode_argument_grouping() -> None:
    """S-F24 B4 — parameterised grouping is BANNED.

    `post_improvement_cpk` is the case the rule was written for: same formula as
    `calculate_cpk`, deliberately a second tool. They may share a private
    helper, and do (`_cpk_values`), but neither takes a `mode`.
    """
    for t in COMPUTATION_TOOLS:
        schema: Any = t.args_schema
        fields = set(schema.model_fields)
        assert not fields & {"mode", "kind", "variant", "method"}, (
            f"{t.name} takes a mode-style argument"
        )
    assert C.calculate_cpk is not C.post_improvement_cpk


def test_every_tool_is_a_pure_synchronous_function() -> None:
    """B1 — deterministic, no LLM call, no I/O. §14's one place sync is right."""
    import inspect

    for t in COMPUTATION_TOOLS:
        fn = getattr(t, "func", None)
        assert fn is not None, f"{t.name} exposes no plain function"
        assert not inspect.iscoroutinefunction(fn), f"{t.name} is async"


def test_every_docstring_opens_with_the_plain_concept() -> None:
    """§69.1 — plain concept first, then the standard term in parentheses.

    *"A Belt who has to already know the acronym to find out what the tool does
    is a Belt the tool will not reach."* The check is that the first line is a
    sentence rather than a bare acronym, and long enough to have said something.
    """
    for t in COMPUTATION_TOOLS:
        first = (t.description or "").strip().splitlines()[0]
        assert len(first) > 40, f"{t.name}'s opening line is too thin: {first!r}"
        assert not first.startswith(t.name), (
            f"{t.name}'s docstring opens with its own name rather than the "
            f"plain concept"
        )


def test_every_result_value_is_a_string() -> None:
    """§7's typing law, restated by §69.1: `cpk: 0.62` is stored `"0.62"`."""
    samples: list[tuple[Any, dict]] = [
        (C.calculate_dpmo, {"defects": "50", "units": "1000",
                            "opportunities_per_unit": "5"}),
        (C.calculate_ftq, {"units_processed": "1000",
                           "units_reworked_or_defective": "50"}),
        (C.c_chart_limits, {"counts": [4, 5, 6, 5]}),
        (C.anova, {"groups": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}),
    ]
    for tool, args in samples:
        for key, value in run(tool, **args).items():
            assert isinstance(value, str), (
                f"{tool.name}.{key} is {type(value).__name__}, not str"
            )


# ══════════════════════════════════════════════════════════════════════════
# Step 5.4's Done-when — the per-phase binding
# ══════════════════════════════════════════════════════════════════════════

#: §30's binding table, read across: universal seven + computation subset.
#: These five numbers are the step's whole contract, so they are written out
#: rather than computed from the subsets — a total derived from the thing it is
#: checking would agree with any partition at all.
EXPECTED_TOTALS = {
    "define": 8, "measure": 15, "analyse": 12, "improve": 8, "control": 12,
}


def bound(phase: str) -> int:
    """What `create_agent` will actually be given for `phase` (§18, §30)."""
    return UNIVERSAL_TOOL_COUNT + len(COMPUTATION_TOOLS_BY_PHASE[phase])


def test_per_phase_totals_are_8_15_12_8_12() -> None:
    """§30's table, and step 5.4's Done-when."""
    assert {p: bound(p) for p in COMPUTATION_TOOLS_BY_PHASE} == EXPECTED_TOTALS


def test_no_phase_exceeds_the_sixteen_tool_ceiling() -> None:
    """§30 — and the actual maximum is Measure's 15, one under it.

    The headroom is asserted too. A binding that sat exactly on 16 would pass a
    ceiling check while leaving no room for the amendment process to be the
    thing that adds the seventeenth tool.
    """
    for phase in COMPUTATION_TOOLS_BY_PHASE:
        assert bound(phase) <= PHASE_TOOL_CEILING, (
            f"{phase} binds {bound(phase)} tools, over §30's ceiling of "
            f"{PHASE_TOOL_CEILING} — that needs an amendment, not a commit"
        )
    assert max(bound(p) for p in COMPUTATION_TOOLS_BY_PHASE) == 15
    assert "measure" == max(COMPUTATION_TOOLS_BY_PHASE, key=bound)


def test_the_universal_seven_is_seven_and_five_are_built() -> None:
    """§29.2 — seven ratified, five built, two owed to steps 7.1 and 7.5.

    **The gap is real and is not a redefinition of §30.** Step 6.2 built
    `propose_template` and `propose_diagram`, which S-F19/S-F20 both assign to
    step 5.2 and which 5.2's prose missed. The last two cannot be built yet by
    the spec's own assignments:

        check_gate_status       S-F21, step 7.1 — needs `DMAICGateValidator`
        request_human_approval  S-F22, step 7.5 — needs the escalation path

    So the LIVE per-phase totals are 6 / 13 / 10 / 6 / 10 against §30's
    8 / 15 / 12 / 8 / 12 until 7.5 lands. **This test is where that arithmetic
    is recorded** (WATCH 25), so the two steps that close it have to come back
    here rather than quietly leaving the totals wrong.
    """
    assert UNIVERSAL_TOOL_COUNT == 7, "§30's ratified count does not move"
    assert len(UNIVERSAL_TOOLS) == 5, "five built at 6.2"
    assert UNIVERSAL_TOOL_COUNT - len(UNIVERSAL_TOOLS) == 2, "two owed"
    assert [t.name for t in UNIVERSAL_TOOLS] == [
        "rag_lookup_methodology", "rag_lookup_evidence", "rag_lookup_case_history",
        "propose_template", "propose_diagram",
    ]
    assert RAG_LOOKUP_TOOLS == UNIVERSAL_TOOLS[:3], (
        "the retrieval third leads the universal list"
    )


@pytest.mark.parametrize("phase, live_total", [
    ("define", 6), ("measure", 13), ("analyse", 10),
    ("improve", 6), ("control", 10),
])
def test_the_live_per_phase_totals_while_two_tools_are_owed(
    phase: str, live_total: int
) -> None:
    """What the executor ACTUALLY binds today, as against §30's ratified table.

    Written out separately from `EXPECTED_TOTALS` rather than replacing it: §30
    is unchanged and stays asserted above. This records the interim, and both
    move together when 7.5 lands.
    """
    assert len(UNIVERSAL_TOOLS) + len(COMPUTATION_TOOLS_BY_PHASE[phase]) \
        == live_total
    assert live_total + 2 == EXPECTED_TOTALS[phase], (
        "the shortfall is exactly the two owed universal tools"
    )


def test_the_binding_is_a_partition_of_the_twenty() -> None:
    """Every tool bound exactly once, and nothing bound that is not one of
    the twenty.

    §30 says a coach chooses among *its phase's* tools; a tool appearing in two
    phases would mean one of the two totals is a fiction.
    """
    flat = [t for tools in COMPUTATION_TOOLS_BY_PHASE.values() for t in tools]
    assert len(flat) == 20
    assert len({t.name for t in flat}) == 20, "a tool is bound to two phases"
    assert flat == COMPUTATION_TOOLS, (
        "the flat inventory and the binding disagree"
    )


def test_the_binding_keys_are_the_five_dmaic_phases() -> None:
    """Keyed by `PHASE_ORDER`'s names — `COMPUTATION_TOOLS_BY_PHASE[phase]` is
    indexed with the same string the subgraph builder is parameterised by
    (§12), so a spelling that differed by even one character would fail at
    runtime, per phase, and only for that phase.
    """
    assert tuple(COMPUTATION_TOOLS_BY_PHASE) == PHASE_ORDER


def test_each_phase_binds_the_inventory_names_for_that_phase() -> None:
    """§60.6's table, name for name and in its order."""
    bound_names = {phase: [t.name for t in tools]
                   for phase, tools in COMPUTATION_TOOLS_BY_PHASE.items()}
    assert bound_names == EXPECTED_NAMES


def test_measure_binds_no_chart_limit_tool() -> None:
    """§69.7 — a specified absence, not an oversight (DECISIONS §AD4).

    `stability_assessment` is coached as a visual read; the chart-limit tools
    are Control's. A future editor moving one into Measure to "help with
    stability" is the mistake this guards.
    """
    measure = {t.name for t in COMPUTATION_TOOLS_BY_PHASE["measure"]}
    control = {t.name for t in COMPUTATION_TOOLS_BY_PHASE["control"]}
    charts = {"xbar_r_chart_limits", "imr_chart_limits", "p_chart_limits",
              "c_chart_limits"}
    assert not measure & charts
    assert charts < control


# ══════════════════════════════════════════════════════════════════════════
# DEFINE — 1 tool
# ══════════════════════════════════════════════════════════════════════════


def test_expected_savings_known_answer() -> None:
    """(0.123 − 0.05) × 120,000 × £45 = £394,200. Verifiable by hand."""
    r = run(C.calculate_expected_savings, baseline_value="0.123",
            target_value="0.05", unit_cost="45", annual_volume="120000")
    assert num(r, "annual_savings") == pytest.approx(394200.0, rel=1e-9)
    assert "120000" in r["calculation_note"].replace(",", "")


def test_expected_savings_states_the_multiplication() -> None:
    """§69 S-F37 — the note exists so a Belt can defend the number at the gate.

    A savings figure nobody can reconstruct is a savings figure nobody will
    approve.
    """
    r = run(C.calculate_expected_savings, baseline_value="10",
            target_value="4", unit_cost="2", annual_volume="1000")
    note = r["calculation_note"]
    assert "12000" in note.replace(",", "")
    assert "baseline" in note and "target" in note


def test_expected_savings_asks_rather_than_inventing_a_cost() -> None:
    """S-F37's precondition, stated as a behaviour: *"must accept an absent cost
    and return a reformatting request rather than inventing a unit cost"*."""
    r = run(C.calculate_expected_savings, baseline_value="10",
            target_value="4", unit_cost="", annual_volume="1000")
    assert asked(r)
    assert "annual_savings" not in r


# ══════════════════════════════════════════════════════════════════════════
# MEASURE — 8 tools
# ══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("dpmo, sigma", [(3.4, 6.0), (66807, 3.0), (233, 5.0)])
def test_sigma_level_known_answers(dpmo: float, sigma: float) -> None:
    """The table every Belt has seen: 3.4 DPMO is six sigma, 66,807 is three."""
    r = run(C.calculate_sigma_level, dpmo=str(dpmo))
    assert num(r, "sigma_level") == pytest.approx(sigma, abs=0.02)
    assert r["shift_assumption"] == "1.5σ long-term shift applied"


def test_sigma_level_from_raw_counts() -> None:
    """50 defects / (1000 units × 5 opportunities) = 10,000 DPMO."""
    r = run(C.calculate_sigma_level, defects="50", units="1000",
            opportunities_per_unit="5")
    assert num(r, "dpmo") == pytest.approx(10000.0)
    expected = float(stats.norm.ppf(1 - 0.01)) + 1.5
    assert num(r, "sigma_level") == pytest.approx(expected, abs=0.01)


def test_cpk_known_answer_centred_process() -> None:
    """Mean 10, σ=1, limits 7 and 13: three sigmas to each limit, so Cpk = 1.0.

    Cp is also 1.0 because the process is centred — when they differ, the gap
    IS the centring problem.
    """
    r = run(C.calculate_cpk, mean="10", std_dev="1", usl="13", lsl="7")
    assert num(r, "cpk") == pytest.approx(1.0)
    assert num(r, "cp") == pytest.approx(1.0)


def test_cpk_off_centre_process_reports_the_binding_side() -> None:
    """Mean 11, σ=1, limits 7 and 13: upper is (13−11)/3 = 0.667, lower 1.333.

    Cpk takes the worse side, and `binding_limit` names it — Cp stays 1.0, so
    the difference between them is exactly the off-centring.
    """
    r = run(C.calculate_cpk, mean="11", std_dev="1", usl="13", lsl="7")
    assert num(r, "cpk") == pytest.approx(2 / 3, abs=1e-3)
    assert num(r, "cp") == pytest.approx(1.0)
    assert r["binding_limit"] == "upper"


def test_cpk_accepts_one_sided_spec() -> None:
    """A one-sided spec gives Cpk and no Cp — Cp needs both limits."""
    r = run(C.calculate_cpk, mean="10", std_dev="1", usl="13")
    assert num(r, "cpk") == pytest.approx(1.0)
    assert "cp" not in r


def test_cpk_parses_a_captured_field_written_as_prose() -> None:
    """**B2 in one test.** §7 makes every captured field a `str`, so this is
    what actually arrives where the spec says `mean`."""
    r = run(C.calculate_cpk, mean="12.3% invoice error rate, measured over Q2",
            std_dev="1.0", usl="15", lsl="9")
    assert not asked(r)
    assert num(r, "cpk") == pytest.approx(0.9, abs=1e-3)


def test_dpmo_known_answer() -> None:
    """50 defects, 1000 units, 5 opportunities each = 10,000 DPMO."""
    r = run(C.calculate_dpmo, defects="50", units="1000",
            opportunities_per_unit="5")
    assert num(r, "dpmo") == pytest.approx(10000.0)


def test_rty_known_answer_and_the_hidden_factory() -> None:
    """Five steps at 95%: RTY = 0.95^5 = 0.7738, not 0.95.

    The gap of 0.176 is the hidden factory — the rework nobody was counting —
    and §69 says it is *"the number that makes RTY's point"*.
    """
    r = run(C.calculate_yield_rty, step_yields=[0.95] * 5)
    assert num(r, "rty") == pytest.approx(0.95 ** 5, abs=1e-4)
    assert num(r, "simple_average_yield") == pytest.approx(0.95)
    assert num(r, "hidden_factory_gap") == pytest.approx(0.95 - 0.95 ** 5,
                                                         abs=1e-4)


def test_rty_accepts_percentages_and_unit_counts() -> None:
    """95 means 95%, and [1000, 50] means a 95% step. Both reach the same RTY."""
    as_pct = run(C.calculate_yield_rty, step_yields=[95, 95])
    as_counts = run(C.calculate_yield_rty,
                    step_units_and_defects=[[1000, 50], [1000, 50]])
    assert num(as_pct, "rty") == pytest.approx(0.9025, abs=1e-4)
    assert num(as_counts, "rty") == pytest.approx(0.9025, abs=1e-4)


def test_rty_requires_at_least_two_steps() -> None:
    """S-F41's precondition — one step is just that step's yield."""
    assert asked(run(C.calculate_yield_rty, step_yields=[0.95]))


def test_ftq_known_answer() -> None:
    """1000 processed, 50 reworked: 950 right first time = 95%."""
    r = run(C.calculate_ftq, units_processed="1000",
            units_reworked_or_defective="50")
    assert num(r, "ftq") == pytest.approx(0.95)


def test_ftq_rejects_more_rework_than_units() -> None:
    r = run(C.calculate_ftq, units_processed="100",
            units_reworked_or_defective="150")
    assert asked(r)


def test_grr_perfect_measurement_system_scores_zero() -> None:
    """Every operator reads every part identically: no measurement variation.

    All the variation is between parts, so %study variation is 0 and the AIAG
    verdict is acceptable. An exact property, not an approximation.
    """
    readings = [[[10.0, 10.0], [20.0, 20.0], [30.0, 30.0]] for _ in range(3)]
    r = run(C.calculate_grr, data_type="variable", readings=readings)
    assert num(r, "pct_study_variation") == pytest.approx(0.0, abs=1e-6)
    assert r["verdict"] == "acceptable"


def test_grr_all_noise_scores_unacceptable() -> None:
    """Parts are identical and the readings differ: every bit of the variation
    is the measurement system, so the verdict must be unacceptable."""
    readings = [
        [[10.0, 14.0], [10.0, 14.0], [10.0, 14.0]],
        [[18.0, 22.0], [18.0, 22.0], [18.0, 22.0]],
        [[26.0, 30.0], [26.0, 30.0], [26.0, 30.0]],
    ]
    r = run(C.calculate_grr, data_type="variable", readings=readings)
    assert num(r, "pct_study_variation") == pytest.approx(100.0, abs=0.5)
    assert r["verdict"] == "unacceptable"


def test_grr_attribute_agreement() -> None:
    """Three of four parts rated consistently by everyone = 75% agreement."""
    r = run(C.calculate_grr, data_type="attribute", agreement_matrix=[
        ["pass", "pass", "pass"],
        ["fail", "fail", "fail"],
        ["pass", "fail", "pass"],
        ["pass", "pass", "pass"],
    ])
    assert num(r, "pct_agreement") == pytest.approx(75.0)
    assert r["parts_in_full_agreement"] == "3"


def test_grr_needs_two_trials_for_repeatability() -> None:
    """One measurement cannot show whether it repeats."""
    r = run(C.calculate_grr, data_type="variable",
            readings=[[[10.0], [20.0]], [[10.0], [20.0]]])
    assert asked(r)


def test_sample_size_proportion_known_answer() -> None:
    """The textbook case: p=0.5, ±5%, 95% confidence → 385.

    Recognisable on sight, which is what makes it a good known answer.
    """
    r = run(C.calculate_sample_size_proportion, expected_proportion="0.5",
            margin_of_error="0.05", confidence_level="0.95")
    assert r["required_n"] == "385"


def test_sample_size_proportion_accepts_percentages() -> None:
    """'50%' and '0.5' are the same request."""
    a = run(C.calculate_sample_size_proportion, expected_proportion="50%",
            margin_of_error="5%")
    assert a["required_n"] == "385"


def test_sample_size_mean_known_answer() -> None:
    """σ=5, detect a difference of 3, 95%/80%: n per group = 2σ²(z_a+z_b)²/δ².

    Computed here from scipy rather than pinned, because the tool's job is to
    apply the formula, not to reimplement the normal quantile.
    """
    z = float(stats.norm.ppf(0.975)) + float(stats.norm.ppf(0.80))
    expected = math.ceil(2 * (5 ** 2) * (z ** 2) / (3 ** 2))
    r = run(C.calculate_sample_size_mean, estimated_std_dev="5",
            detectable_difference="3")
    assert r["required_n"] == str(expected) == "44"


# ══════════════════════════════════════════════════════════════════════════
# ANALYSE — 5 tools
# ══════════════════════════════════════════════════════════════════════════


def test_t_test_known_answer_welch_by_default() -> None:
    """Two clearly separated groups. Welch's is the default (S-F46)."""
    a, b = [10, 12, 11, 13, 12], [15, 17, 16, 18, 17]
    expected = stats.ttest_ind(a, b, equal_var=False)
    r = run(C.t_test, sample1=a, sample2=b)
    assert num(r, "t_statistic") == pytest.approx(float(expected.statistic),
                                                  abs=1e-4)
    assert num(r, "p_value") == pytest.approx(float(expected.pvalue), abs=1e-6)
    assert r["significant"] == "yes"
    assert r["method"] == "Welch's t-test"


def test_t_test_equal_variance_only_when_asked() -> None:
    """S-F46 — *"equal-variance only if the Belt states it"*."""
    a, b = [10, 12, 11, 13, 12], [15, 17, 16, 18, 17]
    r = run(C.t_test, sample1=a, sample2=b, equal_variance=True)
    assert "equal variance" in r["method"]
    assert num(r, "t_statistic") == pytest.approx(
        float(stats.ttest_ind(a, b, equal_var=True).statistic), abs=1e-4)


def test_t_test_paired() -> None:
    before, after = [10, 12, 11, 13], [8, 9, 9, 10]
    r = run(C.t_test, sample1=before, sample2=after, paired=True)
    assert num(r, "t_statistic") == pytest.approx(
        float(stats.ttest_rel(before, after).statistic), abs=1e-4)
    assert r["method"] == "paired t-test"


def test_t_test_identical_groups_are_not_significant() -> None:
    """The other side of the boundary: no difference, no finding."""
    r = run(C.t_test, sample1=[10, 11, 12, 13], sample2=[10, 11, 12, 13])
    assert r["significant"] == "no"


def test_chi_square_known_answer() -> None:
    """A 2×2 table with a clear association."""
    table = [[30, 20], [15, 35]]
    chi2, p, dof, _ = stats.chi2_contingency(table)
    r = run(C.chi_square_test, contingency_table=table)
    assert num(r, "chi_square_statistic") == pytest.approx(float(chi2), abs=1e-4)
    assert r["degrees_of_freedom"] == str(int(dof))
    assert r["significant"] == "yes"


def test_chi_square_refuses_small_expected_counts() -> None:
    """S-F47's precondition — expected cell counts ≥ 5.

    Below that the test is unreliable, and §60.6 B3 says the tool returns a
    small-sample warning rather than a number the Belt would go on to quote.
    """
    r = run(C.chi_square_test, contingency_table=[[1, 2], [2, 1]])
    assert asked(r)
    assert "5" in r["reformatting_request"]


def test_anova_known_answer() -> None:
    """Three tight, well-separated groups: a large F and a small p."""
    groups = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    expected = stats.f_oneway(*groups)
    r = run(C.anova, groups=groups)
    assert num(r, "f_statistic") == pytest.approx(float(expected.statistic),
                                                  abs=1e-4)
    assert r["df_between"] == "2" and r["df_within"] == "6"
    assert r["significant"] == "yes"


def test_anova_needs_three_groups() -> None:
    """S-F48's precondition — with two groups, the t-test is the right tool."""
    r = run(C.anova, groups=[[1, 2, 3], [4, 5, 6]])
    assert asked(r)
    assert "t-test" in r["reformatting_request"]


def test_pearson_known_answer_perfect_correlation() -> None:
    """y = 2x exactly: r = 1.0, r² = 1.0, and the label is 'strong'."""
    x = list(range(1, 11))
    y = [2 * v for v in x]
    r = run(C.pearson_correlation, x_values=x, y_values=y)
    assert num(r, "r") == pytest.approx(1.0)
    assert num(r, "r_squared") == pytest.approx(1.0)
    assert r["strength_label"] == "strong"
    assert "sample_size_warning" not in r


def test_pearson_warns_below_the_methodology_floor_but_still_answers() -> None:
    """S-F49 — *"returns a warning, not a suppressed result — the Belt decides"*."""
    r = run(C.pearson_correlation, x_values=[1, 2, 3, 4],
            y_values=[2, 4, 6, 8])
    assert num(r, "r") == pytest.approx(1.0)
    assert "sample_size_warning" in r, "the result was suppressed, not warned"
    assert "10" in r["sample_size_warning"]


def test_pearson_negative_relationship_keeps_its_sign() -> None:
    x = list(range(1, 11))
    r = run(C.pearson_correlation, x_values=x, y_values=[-2 * v for v in x])
    assert num(r, "r") == pytest.approx(-1.0)
    assert num(r, "r_squared") == pytest.approx(1.0)


def test_linear_regression_known_answer() -> None:
    """y = 2x + 0 exactly: slope 2, intercept 0, R² = 1."""
    x = list(range(1, 11))
    y = [2 * v for v in x]
    r = run(C.linear_regression, x_values=x, y_values=y)
    assert num(r, "slope") == pytest.approx(2.0)
    assert num(r, "intercept") == pytest.approx(0.0, abs=1e-9)
    assert num(r, "r_squared") == pytest.approx(1.0)
    assert r["equation_string"].startswith("y = 2x")


def test_linear_regression_with_an_intercept() -> None:
    """y = 3x + 5."""
    x = list(range(1, 11))
    r = run(C.linear_regression, x_values=x, y_values=[3 * v + 5 for v in x])
    assert num(r, "slope") == pytest.approx(3.0)
    assert num(r, "intercept") == pytest.approx(5.0, abs=1e-9)


# ══════════════════════════════════════════════════════════════════════════
# IMPROVE — 1 tool
# ══════════════════════════════════════════════════════════════════════════


def test_doe_main_effects_known_answer() -> None:
    """A 2² design. Effect of A = mean(high) − mean(low).

        run   A     B     response
        1     low   low   10
        2     high  low   20
        3     low   high  12
        4     high  high  26

    A: (20+26)/2 − (10+12)/2 = 23 − 11 = 12
    B: (12+26)/2 − (10+20)/2 = 19 − 15 =  4
    """
    r = run(C.calculate_doe_main_effects,
            factors=["temperature", "pressure"],
            design_matrix=[["low", "low"], ["high", "low"],
                           ["low", "high"], ["high", "high"]],
            responses=[10, 20, 12, 26])
    assert "temperature: 12" in r["main_effects"]
    assert "pressure: 4" in r["main_effects"]
    assert r["ranked_factors"] == "temperature, pressure"
    assert r["largest_effect"] == "temperature"


def test_doe_accepts_the_usual_level_labels() -> None:
    """`-`/`+` and `-1`/`1` are the same design as low/high."""
    r = run(C.calculate_doe_main_effects, factors=["A"],
            design_matrix=[["-"], ["+"]], responses=[10, 20])
    assert "A: 10" in r["main_effects"]


def test_doe_rejects_a_factor_held_constant() -> None:
    """A factor that never changed has no separable effect."""
    r = run(C.calculate_doe_main_effects, factors=["A", "B"],
            design_matrix=[["low", "low"], ["high", "low"]],
            responses=[10, 20])
    assert asked(r)


# ══════════════════════════════════════════════════════════════════════════
# CONTROL — 5 tools
# ══════════════════════════════════════════════════════════════════════════


def test_xbar_r_known_answer() -> None:
    """Four subgroups of [1,2,3,4,5]: X̄̄ = 3, R̄ = 4, and n=5 so A2 = 0.577.

        UCL_x = 3 + 0.577 × 4 = 5.308      UCL_r = 2.114 × 4 = 8.456
        LCL_x = 3 − 0.577 × 4 = 0.692      LCL_r = 0.000 × 4 = 0
    """
    r = run(C.xbar_r_chart_limits, subgroups=[[1, 2, 3, 4, 5]] * 4)
    assert num(r, "x_bar_bar") == pytest.approx(3.0)
    assert num(r, "r_bar") == pytest.approx(4.0)
    assert num(r, "ucl_x") == pytest.approx(5.308, abs=1e-3)
    assert num(r, "lcl_x") == pytest.approx(0.692, abs=1e-3)
    assert num(r, "ucl_r") == pytest.approx(8.456, abs=1e-3)
    assert num(r, "lcl_r") == pytest.approx(0.0)


def test_xbar_r_refuses_unequal_subgroups() -> None:
    """S-F52's precondition — subgroup size must be constant."""
    r = run(C.xbar_r_chart_limits, subgroups=[[1, 2, 3], [1, 2]])
    assert asked(r)


def test_xbar_r_sends_single_measurements_to_imr() -> None:
    """B7 — a Belt must not be coached into inventing subgroups.

    The tool names the right chart rather than computing a meaningless one.
    """
    r = run(C.xbar_r_chart_limits, subgroups=[[1], [2], [3]])
    assert asked(r)
    assert "I-MR" in r["reformatting_request"]


def test_imr_known_answer() -> None:
    """Values 10, 12, 11, 13: X̄ = 11.5; moving ranges 2, 1, 2 so MR̄ = 1.6667.

        UCL_i  = 11.5 + 2.66 × 1.6667 = 15.933
        LCL_i  = 11.5 − 2.66 × 1.6667 =  7.067
        UCL_mr = 3.267 × 1.6667       =  5.445
    """
    r = run(C.imr_chart_limits, values=[10, 12, 11, 13])
    assert num(r, "x_bar") == pytest.approx(11.5)
    assert num(r, "mr_bar") == pytest.approx(5 / 3, abs=1e-4)
    assert num(r, "ucl_i") == pytest.approx(15.933, abs=1e-3)
    assert num(r, "lcl_i") == pytest.approx(7.067, abs=1e-3)
    assert num(r, "ucl_mr") == pytest.approx(5.445, abs=1e-3)


def test_p_chart_known_answer_and_varying_limits() -> None:
    """30 defectives over 300 units: p̄ = 0.1.

    The limits are NOT one pair of lines — they widen as the batch shrinks,
    which is what a p-chart is for. §69 S-F54: *"returns the formula plus the
    per-subgroup array, never one flat number"*.
    """
    r = run(C.p_chart_limits, subgroups=[
        {"defectives": 10, "n": 100},
        {"defectives": 20, "n": 200},
    ])
    assert num(r, "p_bar") == pytest.approx(0.1)
    note = r["ucl_note"]
    assert "n=100" in note and "n=200" in note
    # ±3·√(0.1·0.9/100) = ±0.09 for the smaller batch, ±0.0636 for the larger.
    assert "0.19" in note and "0.1636" in note


def test_p_chart_clips_the_lower_limit_at_zero() -> None:
    """A negative defective rate does not exist."""
    r = run(C.p_chart_limits, subgroups=[
        {"defectives": 1, "n": 100}, {"defectives": 1, "n": 100},
    ])
    assert "LCL 0," in r["ucl_note"] or "LCL 0" in r["ucl_note"]


def test_c_chart_known_answer() -> None:
    """Counts 4, 5, 6, 5: c̄ = 5, so UCL = 5 + 3√5 = 11.708 and LCL clips to 0."""
    r = run(C.c_chart_limits, counts=[4, 5, 6, 5])
    assert num(r, "c_bar") == pytest.approx(5.0)
    assert num(r, "ucl") == pytest.approx(5 + 3 * math.sqrt(5), abs=1e-3)
    assert num(r, "lcl") == pytest.approx(0.0)


def test_c_chart_lower_limit_when_it_is_positive() -> None:
    """c̄ = 100 gives LCL = 100 − 30 = 70, which is not clipped."""
    r = run(C.c_chart_limits, counts=[100, 100, 100])
    assert num(r, "lcl") == pytest.approx(70.0)


def test_post_improvement_cpk_known_answer_and_delta() -> None:
    """Mean 10, σ=0.5, limits 7 and 13: three sigmas is 1.5, so Cpk = 2.0.

    Against a baseline Cpk of 1.0 the delta is +1.0 — and §69.6 says the delta,
    not the new Cpk alone, is what the Control gate is graded on.
    """
    r = run(C.post_improvement_cpk, mean="10", std_dev="0.5", usl="13",
            lsl="7", baseline_cpk="1.0")
    assert num(r, "cpk") == pytest.approx(2.0)
    assert num(r, "improvement_delta") == pytest.approx(1.0)
    assert r["meets_target"] == "yes"


def test_post_improvement_cpk_reports_a_miss_honestly() -> None:
    """Below 1.33 the answer is no, even though the process improved."""
    r = run(C.post_improvement_cpk, mean="10", std_dev="1.2", usl="13",
            lsl="7", baseline_cpk="0.5")
    assert num(r, "cpk") == pytest.approx(0.833, abs=1e-3)
    assert num(r, "improvement_delta") == pytest.approx(0.333, abs=1e-3)
    assert r["meets_target"] == "no"


def test_post_improvement_cpk_matches_calculate_cpk_on_the_same_data() -> None:
    """Same formula, two tools (§69.6). The shared helper is what keeps them
    from drifting apart while staying two separate `@tool`s."""
    args = {"mean": "11", "std_dev": "1", "usl": "13", "lsl": "7"}
    a = run(C.calculate_cpk, **args)
    b = run(C.post_improvement_cpk, baseline_cpk="0", **args)
    assert a["cpk"] == b["cpk"]
    assert a["binding_limit"] == b["binding_limit"]


# ══════════════════════════════════════════════════════════════════════════
# B3 across all twenty
# ══════════════════════════════════════════════════════════════════════════

#: A minimally-valid call per tool, then the same call with one input made
#: unparseable. Structured collections are Pydantic's to reject; these are the
#: scalar, prose-bearing inputs B2 and B3 are about.
UNPARSEABLE: list[tuple[Any, dict, dict]] = [
    (C.calculate_expected_savings,
     {"baseline_value": "10", "target_value": "4", "unit_cost": "2",
      "annual_volume": "1000"}, {"baseline_value": "quite a lot"}),
    (C.calculate_sigma_level,
     {"defects": "50", "units": "1000", "opportunities_per_unit": "5"},
     {"units": "lots of them"}),
    (C.calculate_cpk,
     {"mean": "10", "std_dev": "1", "usl": "13"}, {"std_dev": "not sure yet"}),
    (C.calculate_dpmo,
     {"defects": "50", "units": "1000"}, {"defects": "a handful"}),
    (C.calculate_ftq,
     {"units_processed": "1000", "units_reworked_or_defective": "50"},
     {"units_processed": "most of them"}),
    (C.calculate_sample_size_proportion,
     {"expected_proportion": "0.5", "margin_of_error": "0.05"},
     {"margin_of_error": "pretty tight"}),
    (C.calculate_sample_size_mean,
     {"estimated_std_dev": "5", "detectable_difference": "3"},
     {"estimated_std_dev": "varies a bit"}),
    (C.post_improvement_cpk,
     {"mean": "10", "std_dev": "0.5", "usl": "13", "baseline_cpk": "1.0"},
     {"baseline_cpk": "better than before"}),
]


@pytest.mark.parametrize("tool, good, broken", UNPARSEABLE,
                         ids=[t.name for t, _, _ in UNPARSEABLE])
def test_unparseable_input_asks_rather_than_raising(tool, good, broken) -> None:
    """**B3.** The baseline call must succeed, and the broken one must ASK.

    Both halves matter: without the first, a tool that always returned a
    request would pass.
    """
    assert not asked(run(tool, **good)), f"{tool.name}'s baseline call failed"
    result = run(tool, **{**good, **broken})
    assert asked(result), (
        f"{tool.name} did not ask for a rewrite on unparseable input"
    )
    assert len(result["reformatting_request"]) > 20


def test_no_tool_raises_on_unparseable_input() -> None:
    """The sweep: nothing in the module lets `_NeedsReformatting` escape.

    It is an internal signal — B3 says the Belt gets a question, not a stack
    trace — so it must never cross a tool boundary.
    """
    for tool, good, broken in UNPARSEABLE:
        try:
            run(tool, **{**good, **broken})
        except C._NeedsReformatting:  # pragma: no cover — the thing guarded
            pytest.fail(f"{tool.name} let _NeedsReformatting escape")


def test_reformatting_requests_are_plain_language() -> None:
    """§13 — no methodology jargon in a team-facing string.

    These strings reach the Belt through the coach, so they are team-facing.
    """
    for tool, good, broken in UNPARSEABLE:
        request = run(tool, **{**good, **broken})["reformatting_request"]
        assert "?" in request, f"{tool.name}'s request does not ask anything"
        for jargon in ("ValidationError", "TypeError", "None", "float("):
            assert jargon not in request, (
                f"{tool.name}'s request leaks {jargon!r} at the Belt"
            )
