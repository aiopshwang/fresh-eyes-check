"""Sends order and account notifications by email (and, soon, SMS)."""

def send(user, kind: str, body: str) -> None:
    # Currently: always email, at any hour.
    _send_email(user.email, kind, body)

def _send_email(to: str, subject: str, body: str) -> None:
    ...
