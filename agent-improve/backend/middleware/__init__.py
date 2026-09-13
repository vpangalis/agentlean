"""The coaching agent's middleware stack — procedure steps 6.3 to 6.5.

Canonical: reference **§19** (the eight, in order), **§61** (the five custom
class specs). Positions 1-3 landed at step 6.3, 4-5 at 6.4, 6-8 at 6.5. Three are
LangChain core (3, 4, 5); five are custom and live here.

**The list in `create_agent(middleware=[...])` is NESTING order, outermost-first;
the position numbers are EXECUTION order, and for `after_*` hooks the two are
opposite** (§19, ARCHITECTURE.md). LangChain applies three separate clauses:
`before_*` fire first-to-last, `after_*` fire LAST-to-first, and `wrap_*` nest
with the first declared enclosing all the others. So the trio below is declared
grader, coherence, contradiction in order to execute contradiction, coherence,
grader. `test_middleware_execution_order.py` OBSERVES that on a real graph;
`test_the_declared_middleware_list_is_the_ratified_layering` checks the declared
list, which is a different property and was misnamed until 2026-09-13 (G-52). The order is binding either way; what is
not cosmetic is the distinction.
"""
from __future__ import annotations

from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.contradiction import ContradictionDetectionMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.middleware.skills import DMAICSkillsMiddleware
from backend.middleware.state_injection import BeforeModelStateInjection

__all__ = [
    "BeforeModelStateInjection",           # declared 1
    "DMAICSkillsMiddleware",               # declared 2
    "DMAICGraderMiddleware",               # declared 6, executes 8
    "CoherenceMiddleware",                 # declared 7, executes 7
    "ContradictionDetectionMiddleware",    # declared 8, executes 6
]
