"""GitHub Copilot model pricing helpers.

Source: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
Fetched: 2026-06-06. Prices are USD per 1M tokens and must be reviewed every two months.
"""
from __future__ import annotations

from dataclasses import dataclass

PRICING_SOURCE_URL = "https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing"
PRICING_FETCHED_DATE = "2026-06-06"
PRICING_REVIEW_INTERVAL_MONTHS = 2


@dataclass(frozen=True)
class ModelRate:
    input: float
    cached_input: float
    output: float
    cache_write: float | None = None

    def as_dict(self) -> dict[str, float]:
        values = {
            "input": self.input,
            "cached_input": self.cached_input,
            "output": self.output,
        }
        if self.cache_write is not None:
            values["cache_write"] = self.cache_write
        return values


@dataclass(frozen=True)
class TieredModelRate:
    default: ModelRate
    long_context: ModelRate
    long_context_threshold: int

    def rate_for(self, input_tokens: int) -> ModelRate:
        return self.long_context if input_tokens > self.long_context_threshold else self.default

    def as_dict(self) -> dict[str, float | int]:
        values: dict[str, float | int] = {
            "input": self.default.input,
            "cached_input": self.default.cached_input,
            "output": self.default.output,
        }
        if self.default.cache_write is not None:
            values["cache_write"] = self.default.cache_write
        values["long_context_threshold"] = self.long_context_threshold
        values["long_context_input"] = self.long_context.input
        values["long_context_cached_input"] = self.long_context.cached_input
        values["long_context_output"] = self.long_context.output
        return values


SONNET_RATE = ModelRate(input=3.00, cached_input=0.30, cache_write=3.75, output=15.00)
OPUS_RATE = ModelRate(input=5.00, cached_input=0.50, cache_write=6.25, output=25.00)

MODEL_PRICING: dict[str, ModelRate | TieredModelRate] = {
    "copilot-default": SONNET_RATE,
    "gpt-5-mini": ModelRate(input=0.25, cached_input=0.025, output=2.00),
    "openai/gpt-5-mini": ModelRate(input=0.25, cached_input=0.025, output=2.00),
    "gpt-5.3-codex": ModelRate(input=1.75, cached_input=0.175, output=14.00),
    "openai/gpt-5.3-codex": ModelRate(input=1.75, cached_input=0.175, output=14.00),
    "gpt-5.4": TieredModelRate(
        default=ModelRate(input=2.50, cached_input=0.25, output=15.00),
        long_context=ModelRate(input=5.00, cached_input=0.50, output=22.50),
        long_context_threshold=272_000,
    ),
    "openai/gpt-5.4": TieredModelRate(
        default=ModelRate(input=2.50, cached_input=0.25, output=15.00),
        long_context=ModelRate(input=5.00, cached_input=0.50, output=22.50),
        long_context_threshold=272_000,
    ),
    "gpt-5.4-mini": ModelRate(input=0.75, cached_input=0.075, output=4.50),
    "openai/gpt-5.4-mini": ModelRate(input=0.75, cached_input=0.075, output=4.50),
    "gpt-5.4-nano": ModelRate(input=0.20, cached_input=0.02, output=1.25),
    "openai/gpt-5.4-nano": ModelRate(input=0.20, cached_input=0.02, output=1.25),
    "gpt-5.5": TieredModelRate(
        default=ModelRate(input=5.00, cached_input=0.50, output=30.00),
        long_context=ModelRate(input=10.00, cached_input=1.00, output=45.00),
        long_context_threshold=272_000,
    ),
    "openai/gpt-5.5": TieredModelRate(
        default=ModelRate(input=5.00, cached_input=0.50, output=30.00),
        long_context=ModelRate(input=10.00, cached_input=1.00, output=45.00),
        long_context_threshold=272_000,
    ),
    "claude-haiku-4.5": ModelRate(input=1.00, cached_input=0.10, cache_write=1.25, output=5.00),
    "claude-sonnet-4": SONNET_RATE,
    "claude-sonnet-4.5": SONNET_RATE,
    "claude-sonnet-4.6": SONNET_RATE,
    "claude-opus-4.5": OPUS_RATE,
    "claude-opus-4.6": OPUS_RATE,
    "claude-opus-4.7": OPUS_RATE,
    "claude-opus-4.8": OPUS_RATE,
    "gemini-2.5-pro": ModelRate(input=1.25, cached_input=0.125, output=10.00),
    "google/gemini-2.5-pro": ModelRate(input=1.25, cached_input=0.125, output=10.00),
    "gemini-3-flash": ModelRate(input=0.50, cached_input=0.05, output=3.00),
    "google/gemini-3-flash": ModelRate(input=0.50, cached_input=0.05, output=3.00),
    "gemini-3.1-pro": TieredModelRate(
        default=ModelRate(input=2.00, cached_input=0.20, output=12.00),
        long_context=ModelRate(input=4.00, cached_input=0.40, output=18.00),
        long_context_threshold=200_000,
    ),
    "google/gemini-3.1-pro": TieredModelRate(
        default=ModelRate(input=2.00, cached_input=0.20, output=12.00),
        long_context=ModelRate(input=4.00, cached_input=0.40, output=18.00),
        long_context_threshold=200_000,
    ),
    "gemini-3.5-flash": ModelRate(input=1.50, cached_input=0.15, output=9.00),
    "google/gemini-3.5-flash": ModelRate(input=1.50, cached_input=0.15, output=9.00),
    "raptor-mini": ModelRate(input=0.25, cached_input=0.025, output=2.00),
    "github/raptor-mini": ModelRate(input=0.25, cached_input=0.025, output=2.00),
    "mai-code-1-flash": ModelRate(input=0.75, cached_input=0.075, output=4.50),
    "microsoft/mai-code-1-flash": ModelRate(input=0.75, cached_input=0.075, output=4.50),
}

MODEL_RATES = {model: pricing.as_dict() for model, pricing in MODEL_PRICING.items()}


def get_model_rate(model: str, input_tokens: int) -> dict[str, float] | None:
    pricing = MODEL_PRICING.get(model)
    if pricing is None:
        return None
    if isinstance(pricing, TieredModelRate):
        return pricing.rate_for(input_tokens).as_dict()
    return pricing.as_dict()


def estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> float | None:
    threshold_input_tokens = input_tokens + cached_input_tokens + cache_write_tokens
    rates = get_model_rate(model, threshold_input_tokens)
    if rates is None:
        return None
    total = (
        input_tokens * rates["input"]
        + cached_input_tokens * rates["cached_input"]
        + cache_write_tokens * rates.get("cache_write", rates["input"])
        + output_tokens * rates["output"]
    ) / 1_000_000
    return round(total, 6)
