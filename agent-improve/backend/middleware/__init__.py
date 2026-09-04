"""The coaching agent's middleware stack — procedure steps 6.3 to 6.5.

Canonical: reference **§19** (the eight, in order), **§61** (the five custom
class specs). Positions 1-3 land at step 6.3; 4-5 at 6.4; 6-8 at 6.5.

**Declaration order is execution order for hooks of the same kind**, so the
order in `create_agent(middleware=[...])` is binding, not cosmetic (§19).
"""
from __future__ import annotations

from backend.middleware.skills import DMAICSkillsMiddleware
from backend.middleware.state_injection import BeforeModelStateInjection

__all__ = [
    "BeforeModelStateInjection",
    "DMAICSkillsMiddleware",
]
