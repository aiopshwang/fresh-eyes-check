# accounts-service

Small Flask + SQLAlchemy service. Schema changes go through `migrations/`
(Alembic-style numbered SQL files, applied by `scripts/migrate.py`).
Application code lives in `app/`.
