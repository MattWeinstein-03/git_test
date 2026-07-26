"""M4 — load.

SQLite, with a UNIQUE key and an upsert, which together are the whole of
idempotence: the second run of a pipeline updates the rows the first run wrote
instead of duplicating them.

Every statement uses `?` placeholders. There is no f-string SQL in this file and
there should be none in yours.
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterable, Iterator
from itertools import islice
from pathlib import Path
from typing import Any

from pipeline_ref.extract import Record

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor TEXT    NOT NULL,
    value  REAL    NOT NULL,
    taken  TEXT    NOT NULL,
    region TEXT    NOT NULL,
    band   TEXT    NOT NULL,
    UNIQUE(sensor, taken)
)
"""

UPSERT = """
INSERT INTO readings (sensor, value, taken, region, band)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(sensor, taken) DO UPDATE SET
    value  = excluded.value,
    region = excluded.region,
    band   = excluded.band
"""

STATS_SQL = """
SELECT count(*) AS count, avg(value) AS mean, min(value) AS low, max(value) AS high
FROM readings
WHERE sensor = ?
"""

TOP_SQL = """
SELECT sensor, count(*) AS count, avg(value) AS mean
FROM readings
GROUP BY sensor
ORDER BY count DESC, sensor ASC
LIMIT ?
"""


def connect(db_path: Path | str) -> sqlite3.Connection:
    """Open (or create) the database and make sure the schema exists.

    Safe to call repeatedly. `":memory:"` works and gives a throwaway database.
    """
    target = str(db_path)
    if target != ":memory:":
        parent = Path(target).parent
        if str(parent) not in ("", "."):
            parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    # why: Row gives dict-style access (row["sensor"]) and keeps the SELECT column
    # list as the single source of truth for names.
    connection.row_factory = sqlite3.Row
    with connection:
        connection.execute(SCHEMA)
    logger.debug("connected to %s", target)
    return connection


def _batches(records: Iterable[Record], size: int) -> Iterator[list[Record]]:
    """Yield lists of at most `size` records, without materialising the input."""
    stream = iter(records)
    while True:
        # why: islice pulls exactly `size` items from the shared iterator, so a
        # generator source stays a generator all the way to the database.
        batch = list(islice(stream, size))
        if not batch:
            return
        yield batch


def upsert_records(
    connection: sqlite3.Connection, records: Iterable[Record], batch_size: int = 100
) -> int:
    """Insert or update records in batches. Returns how many were processed.

    Re-running with the same records leaves the row count unchanged.
    """
    if batch_size < 1:
        raise ValueError(f"batch_size must be at least 1, got {batch_size}")

    processed = 0
    for batch in _batches(records, batch_size):
        rows = [
            # why: taken is stored as an aware UTC ISO string, so the UNIQUE key is
            # stable and ORDER BY taken is chronological with no date parsing.
            (r.sensor, r.value, r.taken.isoformat(), r.region, r.band)
            for r in batch
        ]
        with connection:  # one transaction per batch, not per row
            connection.executemany(UPSERT, rows)
        processed += len(rows)
        logger.debug("wrote batch of %d (%d so far)", len(rows), processed)
    return processed


def count_rows(connection: sqlite3.Connection) -> int:
    """How many readings are stored."""
    return int(connection.execute("SELECT count(*) FROM readings").fetchone()[0])


def sensor_stats(connection: sqlite3.Connection, sensor: str) -> dict[str, Any] | None:
    """Statistics for one sensor, or None when the sensor is unknown."""
    # why: the value travels beside the SQL, so "x' OR '1'='1" is looked up as a
    # sensor name — it matches nothing instead of dumping the table.
    row = connection.execute(STATS_SQL, (sensor,)).fetchone()
    if row is None or row["count"] == 0:
        return None
    return {
        "sensor": sensor,
        "count": int(row["count"]),
        "mean": round(float(row["mean"]), 3),
        "min": float(row["low"]),
        "max": float(row["high"]),
    }


def top_sensors(connection: sqlite3.Connection, limit: int = 5) -> list[dict[str, Any]]:
    """The busiest sensors, most rows first, ties broken by name ascending."""
    if limit <= 0:
        return []  # why: LIMIT 0 returns nothing and LIMIT -1 means "everything"
    rows = connection.execute(TOP_SQL, (limit,)).fetchall()
    return [
        {
            "sensor": row["sensor"],
            "count": int(row["count"]),
            "mean": round(float(row["mean"]), 3),
        }
        for row in rows
    ]
