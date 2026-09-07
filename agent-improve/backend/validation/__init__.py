"""Validation schemas and, from stage 7, the four-layer stack.

**Layer 2a lives in middleware, not here** (§34): it fires every coaching turn,
which a gate-boundary node cannot do. Layers 2b-2d land in the
`validation_stack` node at steps 7.1 and 7.2. One conceptual stack, two
mechanisms — do not try to move 2a into the node or 2b-2d into middleware.

Step 6.5 creates this package for the two schemas S-C22 and S-C23 assign to it.
"""
from __future__ import annotations

from backend.validation.schemas import CoachingGraderVerdict, CoherenceResult

__all__ = ["CoachingGraderVerdict", "CoherenceResult"]
