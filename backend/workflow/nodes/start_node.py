from __future__ import annotations


class StartNode:
    def run(self) -> dict[str, bool]:
        return {
            "operational_escalated": False,
            "strategy_escalated": False,
        }


__all__ = ["StartNode"]
