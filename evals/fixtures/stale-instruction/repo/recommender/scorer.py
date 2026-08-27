"""Score and order candidate items before they reach the ranking prompt."""

from __future__ import annotations

from datetime import date

RECENT_SOURCE_BONUS = 2.0
FRESHNESS_WINDOW_DAYS = 30


def score_item(item: dict, recent_sources: set[str], today: date) -> float:
    """Return a relevance score; higher is better."""
    score = 0.0
    if item["source"] in recent_sources:
        score += RECENT_SOURCE_BONUS
    age_days = (today - item["published"]).days
    score += max(0.0, FRESHNESS_WINDOW_DAYS - age_days) / FRESHNESS_WINDOW_DAYS
    if item.get("dismissed"):
        score = -1.0
    return score


def order_candidates(items: list[dict], recent_sources: set[str], today: date) -> list[dict]:
    """Drop dismissed items and order the rest, best first."""
    scored = [(score_item(item, recent_sources, today), item) for item in items]
    kept = [(score, item) for score, item in scored if score >= 0.0]
    kept.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in kept]
