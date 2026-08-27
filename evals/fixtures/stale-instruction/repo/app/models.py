import json
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    display_name: str | None
    metadata: dict          # parsed from users.metadata JSON
    created_at: str

def load_user(row) -> User:
    return User(row["id"], row["email"], row["display_name"],
                json.loads(row["metadata"] or "{}"), row["created_at"])
