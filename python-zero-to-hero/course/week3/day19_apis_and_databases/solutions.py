"""Day 19 reference solutions.

Same signatures and docstrings as exercises.py. `# why:` comments mark the
choices that are not obvious. No function here touches the network: the transport
is always a parameter.
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlencode

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor TEXT    NOT NULL,
    value  REAL    NOT NULL,
    taken  TEXT    NOT NULL,
    UNIQUE(sensor, taken)
)
"""

UPSERT = """
INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)
ON CONFLICT(sensor, taken) DO UPDATE SET value = excluded.value
"""


@dataclass(frozen=True, slots=True)
class Reading:
    """One validated sensor reading. Given to you — do not modify."""

    sensor: str
    value: float
    taken: str


def build_url(base: str, path: str, params: Mapping[str, Any] | None = None) -> str:
    """Join a base URL and a path, then append an encoded query string.

    Examples:
        >>> build_url("https://x.io", "search", {"q": "a b"})
        'https://x.io/search?q=a+b'
    """
    # why: strip both sides then rejoin, so "v1/" + "/readings" cannot produce
    # "v1//readings". urljoin would also drop the last path segment of the base.
    url = f"{base.rstrip('/')}/{path.lstrip('/')}"
    if not params:
        return url
    # why: None means "omit", which is different from the empty string
    pairs = [(key, str(value)) for key, value in params.items() if value is not None]
    if not pairs:
        return url
    return f"{url}?{urlencode(pairs)}"


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Return the seconds to wait before retry number `attempt` (1-based).

    Examples:
        >>> [backoff_delay(a) for a in (1, 2, 3)]
        [1.0, 2.0, 4.0]
    """
    if attempt < 1:
        raise ValueError(f"attempt must be at least 1, got {attempt}")
    return float(min(base * 2 ** (attempt - 1), cap))


def should_retry(status: int, attempt: int, max_attempts: int) -> bool:
    """Decide whether a request that returned `status` should be retried.

    Examples:
        >>> should_retry(503, attempt=1, max_attempts=3)
        True
    """
    if attempt >= max_attempts:
        return False  # why: bound the loop before looking at the status
    return status in RETRYABLE_STATUS


def parse_readings(
    payload: Mapping[str, Any], default_taken: str = "1970-01-01T00:00:00+00:00"
) -> tuple[list[Reading], list[dict[str, Any]]]:
    """Turn a fetched payload into `Reading` objects, quarantining bad records.

    Examples:
        >>> parse_readings({})
        ([], [])
    """
    items = payload.get("items")
    if not isinstance(items, list):
        # why: a missing or wrong-typed "items" is a payload we cannot use, but it
        # is not an exception - the caller wants a report, not a crash.
        return [], []

    good: list[Reading] = []
    bad: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            bad.append(item)
            continue
        sensor = item.get("sensor")
        raw_value = item.get("value")
        if not isinstance(sensor, str) or not sensor:
            bad.append(dict(item))
            continue
        try:
            value = float(raw_value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            # why: float(None) raises TypeError, float("abc") raises ValueError;
            # both mean the same thing here.
            bad.append(dict(item))
            continue
        taken = item.get("taken") or default_taken
        good.append(Reading(sensor=sensor, value=value, taken=str(taken)))
    return good, bad


def iter_pages(
    fetch: Callable[[str], Mapping[str, Any]], first_url: str, max_pages: int = 100
) -> Iterator[dict[str, Any]]:
    """Yield every item across a cursor-paginated endpoint, lazily.

    Examples:
        >>> list(iter_pages(lambda url: {"items": [1], "next": None}, "/a"))
        [1]
    """
    if max_pages < 1:
        raise ValueError(f"max_pages must be at least 1, got {max_pages}")

    # why: validation happens in the outer function so it fires at call time, and
    # the generator below stays lazy (Day 15, "validate before you yield").
    def generate() -> Iterator[dict[str, Any]]:
        url: str | None = first_url
        pages = 0
        while url and pages < max_pages:
            payload = fetch(url)
            items = payload.get("items") or []
            yield from items
            url = payload.get("next")
            pages += 1

    return generate()


def fetch_with_retries(
    fetch: Callable[[str], tuple[int, Any]],
    url: str,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    cap: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[Any, list[float]]:
    """Call `fetch` until it succeeds, retrying transient failures with backoff.

    Examples:
        >>> fetch_with_retries(lambda url: (200, "ok"), "/x")
        ('ok', [])
    """
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be at least 1, got {max_attempts}")

    delays: list[float] = []
    status = -1
    for attempt in range(1, max_attempts + 1):
        status, payload = fetch(url)
        if 200 <= status < 300:
            return payload, delays
        if not should_retry(status, attempt, max_attempts):
            break
        delay = backoff_delay(attempt, base=base_delay, cap=cap)
        delays.append(delay)
        sleep(delay)  # why: injected, so tests are instant and deterministic
    raise RuntimeError(f"request to {url} failed with status {status}")


def init_db(connection: sqlite3.Connection) -> None:
    """Create the `readings` table if it does not exist.

    Examples:
        >>> import sqlite3
        >>> init_db(sqlite3.connect(":memory:"))
    """
    with connection:
        connection.execute(SCHEMA)


def save_readings(connection: sqlite3.Connection, readings: Iterable[Reading]) -> int:
    """Insert or update readings, idempotently, in one transaction.

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> init_db(conn)
        >>> save_readings(conn, [Reading("s1", 1.0, "t")])
        1
    """
    rows = [(r.sensor, r.value, r.taken) for r in readings]
    if not rows:
        return 0
    # why: one transaction for the whole batch. A commit per row turns two
    # seconds of work into four minutes.
    with connection:
        connection.executemany(UPSERT, rows)
    return len(rows)


def find_by_sensor(connection: sqlite3.Connection, sensor: str) -> list[dict[str, Any]]:
    """Return every stored reading for one sensor, newest `taken` first.

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> init_db(conn)
        >>> find_by_sensor(conn, "x' OR '1'='1")
        []
    """
    # why: `?` sends the value beside the SQL, so hostile input is treated as a
    # literal sensor name and matches nothing. An f-string here would leak the
    # whole table for "x' OR '1'='1".
    cursor = connection.execute(
        "SELECT sensor, value, taken FROM readings WHERE sensor = ? ORDER BY taken DESC",
        (sensor,),
    )
    return [
        {"sensor": row[0], "value": row[1], "taken": row[2]} for row in cursor.fetchall()
    ]


def sync_readings(
    fetch: Callable[[str], Mapping[str, Any]],
    connection: sqlite3.Connection,
    first_url: str,
    max_pages: int = 100,
) -> dict[str, int]:
    """Run the whole pipeline: paginate, parse, quarantine, persist.

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> pages = {"/a": {"items": [], "next": None}}
        >>> sync_readings(lambda url: pages[url], conn, "/a")["fetched"]
        0
    """
    init_db(connection)
    items = list(iter_pages(fetch, first_url, max_pages=max_pages))
    good, bad = parse_readings({"items": items})
    saved = save_readings(connection, good)
    stored = connection.execute("SELECT count(*) FROM readings").fetchone()[0]
    return {
        "fetched": len(items),
        "saved": saved,
        "quarantined": len(bad),
        "stored": int(stored),
    }


if __name__ == "__main__":
    print("Solutions module. Run `python check.py day19` to grade exercises.py.")
