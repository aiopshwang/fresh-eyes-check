"""Turn the day's events into the digest email body."""

from __future__ import annotations

from pathlib import Path

PROMPT_PATH = Path(__file__).with_name("prompts") / "summary.md"
SIGNATURE = "-- The notification service"


def call_llm(prompt: str) -> str:
    """Stub for the shared model client.

    Returns canned prose so the formatter runs locally; the real client is
    wired in at deploy time.
    """
    # The model tends to rewrite dates in prose.
    return (
        "On Aug 5 the weekly report was published and two comments landed "
        "on your draft; on 8/4 the build pipeline was restored."
    )


def build_digest_email(events: list[dict], recipient_name: str) -> dict:
    """Build the subject and body of one digest email.

    The model composes the body paragraph as free prose from the event
    list; its response is used as the body as-is. Event dates go into the
    prompt exactly as the event store provides them.
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
