"""Controls review, item 4 (founder, 2026-09-30): pattern-4 bans the Saga / compensating-action
CONSTRUCT, not every name holding "compensat". The samples are built by concatenation: the drift
hook scans this file's text too."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
_HOOKS = _REPO / ".claude" / "hooks"
_REGISTRY = _REPO / ".claude" / "config" / "deprecated_patterns.yaml"
SAGA_CLASS = "class Order" + "Saga:"


def _pattern_4() -> re.Pattern:
    pats = {p["id"]: p for p in yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))["patterns"]}
    return re.compile(pats["pattern-4-custom-saga"]["regex"])


@pytest.mark.parametrize("text, banned", [
    (SAGA_CLASS, True),
    ("class " + "Compensation" + "Step(Base):", True),
    ("def " + "compensate(order):", True),
    ("async def _" + "compensate(order):", True),
    ("def run_" + "compensations():", True),
    ("def test_timeout_and_" + "compensation_use_the_engine():", False),
    ("def " + "compensation_rate(df):", False),
    ("def " + "compensates_for_drift():", False),
])
def test_pattern_4_bans_the_construct_not_the_word(text: str, banned: bool) -> None:
    assert bool(_pattern_4().search(text)) is banned
