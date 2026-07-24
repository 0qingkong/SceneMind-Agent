from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base


class Database:
    def __init__(self, url: str) -> None:
        self.url = url
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self.engine: Engine = create_engine(url, connect_args=connect_args)
        if url.startswith("sqlite"):
            event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
        )

    @staticmethod
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def create_tables(self) -> None:
        parsed_url = make_url(self.url)
        if parsed_url.get_backend_name() == "sqlite" and parsed_url.database not in {
            None,
            "",
            ":memory:",
        }:
            Path(parsed_url.database).expanduser().resolve().parent.mkdir(
                parents=True, exist_ok=True
            )
        Base.metadata.create_all(self.engine)
        if parsed_url.get_backend_name() == "sqlite":
            self._ensure_sqlite_observation_columns()

    def _ensure_sqlite_observation_columns(self) -> None:
        """Apply the additive Day 9 observation metadata migration to old MVP DBs."""

        existing = {item["name"] for item in inspect(self.engine).get_columns("observations")}
        additions = {
            "source_type": "VARCHAR(50)",
            "source_device_id": "VARCHAR(255)",
            "source_device_name": "VARCHAR(255)",
            "captured_at": "DATETIME",
            "session_id": "VARCHAR(36)",
        }
        with self.engine.begin() as connection:
            for name, sql_type in additions.items():
                if name not in existing:
                    connection.execute(
                        text(f"ALTER TABLE observations ADD COLUMN {name} {sql_type}")
                    )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_observations_session_id "
                    "ON observations (session_id)"
                )
            )

    def sessions(self) -> Iterator[Session]:
        with self.session_factory() as session:
            yield session
