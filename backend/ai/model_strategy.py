from __future__ import annotations

from backend.config import Settings


class ModelStrategy:
    def __init__(self, settings: Settings):
        self.intent_default = settings.MODEL_INTENT_CLASSIFIER
        self.operational_default = settings.MODEL_OPERATIONAL
        self.operational_premium = settings.MODEL_OPERATIONAL_PREMIUM
        self.strategy_default = settings.MODEL_STRATEGY
        self.strategy_premium = settings.MODEL_STRATEGY_PREMIUM


__all__ = ["ModelStrategy"]
