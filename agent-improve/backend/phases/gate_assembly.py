"""The two invariants that run before a gate document is constructed.

Canonical: **S-F28** (§62.11) · Architecture **§40.1**. Procedure step 3.4.

Assembly itself lives with each phase's schema, because a `{Phase}Output` and
the code that constructs it share one field vocabulary (§56.1's atomic-unit
rule). What lives here is the part that must be identical across all five: the
two checks S-F28 requires to run FIRST, and both of which RAISE.

WHY THEY RAISE RATHER THAN WARN
    By the time assembly runs, Layer 2b, the constraint check and the rubric
    have all passed and **the Belt has approved**. A failure here is therefore
    a CODE DEFECT, not an incomplete phase — and in the single-authority case
    it is two stores disagreeing about one number, where writing either one
    makes the disagreement permanent. Same reasoning that makes a `KeyError`
    on a gate-required field correct rather than something to defend against.

§0.24: validation and serialisation are Pydantic's. Nothing here re-implements
either — `check_field_coverage` inspects `model_fields`, and construction is a
plain `Model(**values)` so Pydantic raises on a missing or ill-typed field.
"""
from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

from backend.core.metrics import assert_single_authority

TModel = TypeVar("TModel", bound=BaseModel)

#: The same four on all five schemas (§40). Present so a phase cannot quietly
#: omit one and so `check_field_coverage` has a name for them in its message.
GATE_METADATA_FIELDS: tuple[str, ...] = (
    "computation_results", "acknowledged_gaps", "citations", "uploads",
)


class GateAssemblyError(RuntimeError):
    """An assembly invariant failed. Always a code defect (see module docs)."""


def check_field_coverage(model_cls: type[BaseModel], provided: dict[str, Any]) -> None:
    """S-F28 invariant 1 — assembly must reference EVERY field in the schema.

    **A field assembly never sets is a field that silently never reaches the
    Store**, and the omission is invisible until a later phase reads nothing.
    Pydantic will not catch it on its own: a field with a default (all four
    gate-metadata fields have one) constructs happily when omitted.

    G-28 is precisely this risk at scale — "55 field assignments, each
    selecting a tier access pattern, and an omission is silent." This is the
    check that makes it loud.
    """
    declared = set(model_cls.model_fields)
    missing = declared - set(provided)
    extra = set(provided) - declared
    if missing or extra:
        parts = []
        if missing:
            parts.append(
                f"never set by assembly: {sorted(missing)} — each would reach "
                f"the Store as its default and be invisible until a later "
                f"phase read nothing"
            )
        if extra:
            parts.append(f"set but not on the schema: {sorted(extra)}")
        raise GateAssemblyError(
            f"{model_cls.__name__} field coverage (S-F28 invariant 1): "
            + "; ".join(parts)
        )


def build_gate_document(
    model_cls: type[TModel],
    phase: str,
    artifacts: dict[str, Any],
    values: dict[str, Any],
) -> TModel:
    """Run both S-F28 invariants, then construct by Pydantic.

    Order is fixed by S-F28 B1: single authority is checked **before** the
    document is constructed, so a metric mismatch surfaces as itself rather
    than as a downstream validation error.

    There is **no LLM call in this path** (§20, §33) — the values were captured
    turn by turn and approved at the gate; assembly is construction.
    """
    assert_single_authority(phase, artifacts)   # S-F28 invariant 2 / B1-B4
    check_field_coverage(model_cls, values)     # S-F28 invariant 1
    return model_cls(**values)


def tier_1(artifacts: dict[str, Any], field: str) -> Any:
    """Gate-required access. **A `KeyError` here is CORRECT** (§40.1).

    Layer 2b should have blocked the gate, so reaching assembly without the
    field is a bug that must surface loudly. Written as a function rather than
    inlined so the tier is legible at each call site and greppable across the
    five assemblies.
    """
    return artifacts[field]


def tier_2(artifacts: dict[str, Any], field: str, empty: Any = "") -> Any:
    """Rubric-recommended access. An empty value **records that the Belt
    proceeded without it** (§35, §40.1) — it is data, not a failure.

    `empty` takes the right shape per field: `""` for prose, `{}` for a
    cross-phase reference dict, `[]` for a list.
    """
    return artifacts.get(field, empty)


__all__ = [
    "GATE_METADATA_FIELDS", "GateAssemblyError",
    "check_field_coverage", "build_gate_document", "tier_1", "tier_2",
]
