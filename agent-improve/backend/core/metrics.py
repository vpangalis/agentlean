"""The metric single-authority invariant.

ARCHITECTURE.md §39.2.3 · §40.1 · §63.8 (S-C38) · §63.9 (S-C39) · CLAUDE.md §10.7.

**`phase_metrics` is the authoritative per-metric store.** The scalar fields —
Define's `baseline_estimate` / `target_value`, Measure's `baseline_mean` /
`baseline_sigma`, Control's `post_improvement_metrics` — are **the primary
metric's mirror**, kept because the gate document renders them and because
Control reads them directly. **Additional metrics live only in `phase_metrics`.**

Two stores holding one value is how they drift. The rule that stops it: the
primary metric's `phase_metrics` entry and the scalar fields **MUST be equal**,
and a mismatch is a defect rather than a preference. It is enforced at
`gate_apply` assembly (§40.1, S-F28), where both are in hand and nothing has
been written yet.

**Why mirror at all rather than read `phase_metrics[0]` everywhere.** The gate
document is a Belt-facing quality record and reads far better with a named
scalar than with an index into a list; Control's target-vs-actual comparison
was specified against the scalars before the registry existed. Mirroring is the
cheaper change, but it is only safe if something checks the mirror — this
module is that something.

Module-level functions only (§2). No LLM call, no I/O — this is arithmetic on
values already captured.
"""
from __future__ import annotations

# Which top-level scalar fields mirror the PRIMARY metric's `phase_metrics`
# entry, per phase. The key in the entry has the same name as the scalar.
#
# Analyse and Improve are deliberately empty: they act on drivers rather than
# outcome values, so their `phase_metrics` entries record LINKAGE (which metric
# a cause or solution targets) and there is no scalar to mirror (§63.9).
PRIMARY_MIRRORED_SCALARS: dict[str, tuple[str, ...]] = {
    "define":  ("baseline_estimate", "target_value"),
    "measure": ("baseline_mean", "baseline_sigma"),
    "analyse": (),
    "improve": (),
    "control": (),          # Control mirrors through a dict — see below
}

# **Control's mirror is shaped differently, and deliberately** (§39.5.3, F-14).
# Its scalar is not a plain string but the cross-phase reference DICT
# `post_improvement_metrics` (S-C32), whose measured value lives under `metric`.
# The `phase_metrics` entry calls the same number `actual`, because there it sits
# beside `baseline`, `target` and `delta` and "actual" is what it is in that row.
#
#   artifacts["post_improvement_metrics"]["metric"]  ==  entry["actual"]
#
# Two different names for one number is exactly the drift this module exists to
# catch, which is why the mapping is written down rather than inferred.
# (dict_field, key_inside_dict, key_in_phase_metrics_entry)
PRIMARY_MIRRORED_DICT: dict[str, tuple[str, str, str]] = {
    "control": ("post_improvement_metrics", "metric", "actual"),
}

# A phase that engaged no metric writes this rather than leaving the list empty
# (§63.9 B2) — an empty list reads the same whether nothing was measured or
# someone forgot to record it, and the second is the failure worth catching.
NONE_THIS_PHASE = "none this phase"


def primary_entry(phase_metrics: list) -> dict | None:
    """The primary metric's entry — the first real entry in `phase_metrics`.

    Returns None when the phase engaged no metric, which is not an error: it is
    the `"none this phase"` case, and Analyse/Improve reach it routinely.
    """
    if not isinstance(phase_metrics, list):
        return None
    for entry in phase_metrics:
        if isinstance(entry, dict) and str(entry.get("name") or "").strip():
            return entry
    return None


def check_single_authority(phase: str, artifacts: dict) -> list[str]:
    """Return a list of invariant defects. Empty list means the mirror holds.

    Called from `gate_apply` assembly (§40.1) **before** the gate document is
    constructed. A non-empty return is a defect in the captured values, not a
    Belt error — it means two stores disagree about one number, and writing
    either one would make the disagreement permanent.
    """
    defects: list[str] = []
    scalars = PRIMARY_MIRRORED_SCALARS.get(phase, ())
    dict_rule = PRIMARY_MIRRORED_DICT.get(phase)
    if not scalars and not dict_rule:
        return defects                      # Analyse / Improve — linkage only

    pm = artifacts.get("phase_metrics")

    # `"none this phase"` is a valid, conscious answer and mirrors nothing.
    if isinstance(pm, str) and pm.strip().lower() == NONE_THIS_PHASE:
        return defects
    if isinstance(pm, list) and len(pm) == 1 and isinstance(pm[0], str) \
            and pm[0].strip().lower() == NONE_THIS_PHASE:
        return defects

    entry = primary_entry(pm or [])
    if entry is None:
        # The phase carries scalars but named no metric: the registry link is
        # missing, so nothing can be traced to it downstream.
        if any(str(artifacts.get(s) or "").strip() for s in scalars):
            defects.append(
                "phase_metrics has no primary entry, but %s carries "
                "%s — the value cannot be traced to a registry metric"
                % (phase, "/".join(scalars))
            )
        return defects

    for scalar in scalars:
        top = str(artifacts.get(scalar) or "").strip()
        inner = str(entry.get(scalar) or "").strip()
        if top != inner:
            defects.append(
                "%s: primary metric %r has %s=%r in phase_metrics but %r at the "
                "top level — phase_metrics is authoritative (§39.2.3)"
                % (phase, entry.get("name"), scalar, inner, top)
            )

    if dict_rule:
        field, inner_key, entry_key = dict_rule
        holder = artifacts.get(field)
        top = ""
        if isinstance(holder, dict):
            top = str(holder.get(inner_key) or "").strip()
        inner = str(entry.get(entry_key) or "").strip()
        if top != inner:
            defects.append(
                "%s: primary metric %r has %s=%r in phase_metrics but "
                "%s[%r]=%r — phase_metrics is authoritative (§39.5.3)"
                % (phase, entry.get("name"), entry_key, inner, field,
                   inner_key, top)
            )
    return defects


def assert_single_authority(phase: str, artifacts: dict) -> None:
    """Raise on any invariant defect. The assembly-time form (§40.1, S-F28).

    **Raising here is correct.** Layer 2b and the rubric run before this; by the
    time `gate_apply` assembles, every value has been captured and approved, so
    a mismatch is a code defect rather than an incomplete phase — exactly the
    class §40.1 already says must surface loudly rather than default quietly.
    """
    defects = check_single_authority(phase, artifacts)
    if defects:
        raise ValueError(
            "metric single-authority invariant violated at %s gate assembly:\n  - %s"
            % (phase, "\n  - ".join(defects))
        )
