"""Validation schemas — the coaching grader's, and those of the `validation_stack` node's layers (2b-2d).

There is no Layer 2a coherence middleware (ADR-0083): its purpose is served before the
coach by the input guard and the planner's judgment (`gates.md`).
"""
from __future__ import annotations

from backend.validation.schemas import CoachingGraderVerdict

__all__ = ["CoachingGraderVerdict"]
