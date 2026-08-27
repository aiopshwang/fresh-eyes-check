"""Builds the weekly orders report from the orders table."""

from datetime import date, timedelta


def weekly_report_rows(conn, week_start: date) -> list[dict]:
    """Return one report row per order placed in the week from week_start."""
    week_end = week_start + timedelta(days=7)
    cursor = conn.execute(
        "SELECT id, user_id, total_cents, status, placed_at FROM orders "
        "WHERE placed_at >= ? AND placed_at < ? ORDER BY placed_at",
        (week_start.isoformat(), week_end.isoformat()),
    )
    return [
        {
            "order": row["id"],
            "user": row["user_id"],
            "total": f"{row['total_cents'] / 100:.2f}",
            "status": row["status"],  # printed raw, e.g. "placed"
            "placed_at": row["placed_at"],
        }
        for row in cursor
    ]
