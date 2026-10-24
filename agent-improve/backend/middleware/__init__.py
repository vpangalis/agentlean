"""The coaching agent's middleware stack.

Three positions are LangChain core (3, 4, 5); the custom ones live here.

**The list in `create_agent(middleware=[...])` is NESTING order, outermost-first;
the position numbers are EXECUTION order, and for `after_*` hooks the two are
opposite.** LangChain applies three separate clauses:
`before_*` fire first-to-last, `after_*` fire LAST-to-first, and `wrap_*` nest
with the first declared enclosing all the others. So the pair below is declared
grader, contradiction in order to execute contradiction, then grader (there is no
coherence judge between them, ADR-0083). `test_middleware_execution_order.py` OBSERVES that on a real graph;
`test_the_declared_middleware_list_is_the_ratified_layering` checks the declared
list, which is a different property (G-52). The order is binding either way; what is
not cosmetic is the distinction.
"""
from __future__ import annotations

from backend.middleware.contradiction import ContradictionDetectionMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.middleware.skills import DMAICSkillsMiddleware
from backend.middleware.state_injection import BeforeModelStateInjection

__all__ = [
    "BeforeModelStateInjection",           # declared 1
    "DMAICSkillsMiddleware",               # declared 2
    "DMAICGraderMiddleware",               # declared 6, executes 8
    "ContradictionDetectionMiddleware",    # declared 8, executes 6
]
