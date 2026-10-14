"""Validation schemas and, from stage 7, the three-layer stack (2b-2d).

Layers 2b-2d land in the `validation_stack` node at steps 7.1 and 7.2. Layer 2a,
the coherence middleware, is retired (ADR-0083): its purpose is served before the
coach by the input guard and the planner's judgment (gates.md §9.2).

Step 6.5 creates this package for the two schemas S-C22 and S-C23 assign to it.
"""
from __future__ import annotations

from backend.validation.schemas import CoachingGraderVerdict

__all__ = ["CoachingGraderVerdict"]
