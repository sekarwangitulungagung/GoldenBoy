import json
import sqlite3
from pathlib import Path
from typing import Any


class ConfigStore:
    """SQLite-backed key/value store for persistent application configuration."""

    def __init__(self, db_path: str = "goldenboy_config.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def set_value(self, key: str, value: Any) -> None:
        encoded = json.dumps(value)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO app_config (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, encoded),
            )
            conn.commit()

    def get_value(self, key: str, default: Any = None) -> Any:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM app_config WHERE key = ?",
                (key,),
            ).fetchone()

        if row is None:
            return default

        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return default

    def get_many(self, defaults: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, default in defaults.items():
            result[key] = self.get_value(key, default)
        return result
