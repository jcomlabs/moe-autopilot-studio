from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from .models import RunRecord
from .paths import data_dir


class StudioStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or data_dir() / "studio.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, updated_at TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def save_run(self, record: RunRecord) -> None:
        payload = json.dumps(record.model_dump(mode="json", exclude_computed_fields=True), separators=(",", ":"))
        with self._lock, self._connect() as connection:
            connection.execute(
                "INSERT INTO runs(id, updated_at, payload) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at, payload=excluded.payload",
                (record.id, record.updated_at.isoformat(), payload),
            )

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE id = ?", (run_id,)).fetchone()
        return RunRecord.model_validate_json(row[0]) if row else None

    def list_runs(self, limit: int = 50) -> list[RunRecord]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM runs ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [RunRecord.model_validate_json(row[0]) for row in rows]

