"""Database interface for the No Pressure app."""

import os
from contextlib import contextmanager
from datetime import date, datetime
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import RealDictCursor


class PostgresDB:
    """Thin wrapper around a PostgreSQL connection for bp readings."""

    def __init__(self, *, db_url: str | None = None) -> None:
        self.db_url = db_url or os.getenv("DB_URL")
        if not self.db_url:
            raise ValueError("DB_URL env var (or db_url) is required")

    @contextmanager
    def connection(self) -> Generator[PGConnection, None, None]:
        """Yield an open psycopg2 connection that auto-closes."""
        conn = psycopg2.connect(self.db_url)
        try:
            yield conn
        finally:
            conn.close()

    def ensure_tables_exist(self) -> None:
        """Create tables if they don't exist (idempotent)."""
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bp_readings (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sys INTEGER NOT NULL,
                    dia INTEGER NOT NULL,
                    hr INTEGER NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_bp_readings_timestamp
                    ON bp_readings(timestamp DESC);
            """)
            conn.commit()

    def insert_reading(
        self, sys: int, dia: int, hr: int, timestamp: date | datetime | None = None
    ) -> int:
        """
        Insert a blood pressure reading into the database.

        Args:
            sys: Systolic blood pressure
            dia: Diastolic blood pressure
            hr: Heart rate
            timestamp: Optional timestamp (defaults to current time)

        Returns:
            The ID of the inserted reading
        """
        with self.connection() as conn, conn.cursor() as cur:
            if timestamp:
                cur.execute(
                    """
                    INSERT INTO bp_readings (timestamp, sys, dia, hr)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (timestamp, sys, dia, hr),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO bp_readings (sys, dia, hr)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (sys, dia, hr),
                )
            reading_id = cur.fetchone()[0]
            conn.commit()
            return reading_id

    def get_recent_readings(self, limit: int = 10) -> list[dict]:
        """
        Get recent blood pressure readings from the database.

        Args:
            limit: Maximum number of readings to return

        Returns:
            List of dictionaries containing reading data
        """
        with (
            self.connection() as conn,
            conn.cursor(cursor_factory=RealDictCursor) as cur,
        ):
            cur.execute(
                """
                SELECT id, timestamp, sys, dia, hr
                FROM bp_readings
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def get_latest_reading(self) -> dict | None:
        """
        Get the most recent blood pressure reading.

        Returns:
            Dictionary containing the latest reading, or None if no readings exist
        """
        readings = self.get_recent_readings(limit=1)
        return readings[0] if readings else None
