"""Turn the day's events into the digest email body."""

from __future__ import annotations

from pathlib import Path

PROMPT_PATH = Path(__file__).with_name("prompts") / "summary.md"
SIGNATURE = "-- The notification service"


def call_llm(prompt: str) -> str:
    """Stub for the shared model client.

    Returns a canned digest so the formatter runs locally; the real client
    is wired in at deploy time. The model repeats dates as it received them.
    """
    return (
        "On 2026-8-5 the weekly report was published and two comments landed "
        "on your draft; on 2026-8-4 the build pipeline was restored."
    )


def build_digest_email(events: list[dict], recipient_name: str) -> dict:
    """Build the subject and body of one digest email.

    The model writes the body paragraph directly from the event list; its
    response is used as-is. Dates are passed through exactly as the event
    store provides them.
    """
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8").strip()

    event_lines = []
    for event in events:
        date_text = str(event["date"])
        event_lines.append(f"- {date_text}: {event['title']} ({event['source']})")

    prompt = "\n".join([prompt_template, "", "Events:", *event_lines])
    summary = call_llm(prompt).strip()

    subject = f"Your daily digest ({len(events)} events)"
    body = "\n".join(
        [
            f"Hi {recipient_name},",
            "",
            summary,
            "",
            SIGNATURE,
        ]
    )
    return {"subject": subject, "body": body}
