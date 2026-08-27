"""Fetch the day's events from the upstream event store.

The store serializes ``date`` as an ISO ``YYYY-MM-DD`` string. Events are
passed through to the digest as received.
"""

from __future__ import annotations


SAMPLE_EVENTS = [
    {"date": "2026-08-05", "title": "Weekly report published", "source": "reports"},
    {"date": "2026-08-05", "title": "Two comments on your draft", "source": "docs"},
    {"date": "2026-08-04", "title": "Build pipeline restored", "source": "ci"},
]


def fetch_events(user_id: str) -> list[dict]:
    """Stub for the event store client; returns the sample payload as-is."""
    return [dict(event) for event in SAMPLE_EVENTS]
