"""The defect register, `docs/defects.json` — founder, 2026-09-27.

Moved from the archived procedure's Appendix G. One entry per defect: id,
symptom, requirement, feature, lane — and NO status field: a defect's status is
its feature's test outcome. These tests keep the register honest against the
one file that also names the gap-feature links, `docs/define_features.json`
(`provenance.gaps`), so neither can drift from the other.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

_DOCS = Path(__file__).resolve().parents[2] / "docs"
FIELDS = {"id", "symptom", "requirement", "feature", "lane"}
#: Founder 2026-09-30 (review of ea2d265): a TOOLING gap — a defect in the harness, not in a Define
#: feature — has no feature and no requirement, lane ["tooling"], and names the `control` that now
#: prevents it recurring.
TOOLING = ["tooling"]


def _tooling(d: dict) -> bool:
    return d["lane"] == TOOLING


@pytest.fixture(scope="module")
def defects() -> list[dict]:
    return json.loads((_DOCS / "defects.json").read_text(encoding="utf-8"))["defects"]


@pytest.fixture(scope="module")
def features() -> dict[str, dict]:
    fs = json.loads((_DOCS / "define_features.json").read_text(encoding="utf-8"))["features"]
    return {f["id"]: f for f in fs}


def test_every_defect_has_the_founders_fields_and_no_status(defects) -> None:
    for d in defects:
        want = FIELDS | {"control"} if _tooling(d) else FIELDS
        assert set(d) == want, (d["id"], set(d) ^ want)
        assert re.fullmatch(r"G-\d+", d["id"]), d["id"]
        assert d["symptom"].strip(), d["id"]
        for k in ("requirement", "feature", "lane"):
            assert isinstance(d[k], list), (d["id"], k)


def test_ids_are_unique_and_none_was_lost_in_the_move(defects) -> None:
    ids = [d["id"] for d in defects]
    assert len(ids) == len(set(ids))
    numbers = sorted(int(i[2:]) for i in ids)
    assert numbers == list(range(1, max(numbers) + 1)), "a G number is missing from the register"


def test_the_feature_links_agree_with_the_feature_list_both_ways(defects, features) -> None:
    by_gap: dict[str, set[str]] = {}
    for f in features.values():
        for g in f["provenance"]["gaps"]:
            by_gap.setdefault(g.upper(), set()).add(f["id"])
    for d in defects:
        assert set(d["feature"]) == by_gap.get(d["id"], set()), d["id"]
        if _tooling(d):
            continue
        linked = [features[i] for i in d["feature"]]
        assert set(d["requirement"]) == {f["requirement"] for f in linked}, d["id"]
        assert set(d["lane"]) == {f["lane"] for f in linked}, d["id"]
    assert set(by_gap) <= {d["id"] for d in defects}, "a feature cites a gap the register lacks"


def test_a_new_defect_carries_one_failing_feature_and_one_lane(defects) -> None:
    """From 2026-09-27 a defect is registered with its feature and owner in the same commit."""
    new = {d["id"]: d for d in defects if int(d["id"][2:]) >= 112}
    # Brief Part A4 (2026-09-27): DEF-073 folded into DEF-060, which now cites T23.
    assert new["G-112"]["feature"] == ["DEF-060"] and new["G-112"]["lane"] == ["B"]
    assert new["G-112"]["requirement"] == ["T23"]
    assert new["G-113"]["feature"] == ["DEF-074"] and new["G-113"]["lane"] == ["C"]
    assert new["G-113"]["requirement"] == ["W6"]
    for d in new.values():
        if _tooling(d):
            # A tooling gap: no feature, no requirement, and the control that prevents recurrence.
            assert d["feature"] == [] and d["requirement"] == [], d["id"]
            assert len(d["control"].strip()) >= 20, d["id"]
            continue
        assert len(d["feature"]) == 1 and len(d["lane"]) == 1, d["id"]
