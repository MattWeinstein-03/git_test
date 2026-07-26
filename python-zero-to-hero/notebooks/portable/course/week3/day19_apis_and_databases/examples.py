"""Day 19 — runnable demonstrations of HTTP and SQLite.

Run it:

    python course/week3/day19_apis_and_databases/examples.py

Section 2 attempts exactly ONE real network request. If `requests` is missing, or
there is no network, or the call fails for any reason, it falls back to a canned
payload and carries on — so this script always exits 0, online or offline.
Everything else is entirely local: SQLite in a tmp/ folder that is deleted at the
end.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import time
from collections.abc import Iterator
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode, urljoin

# Third-party imports are allowed from Day 19, and they are import-guarded so
# this file runs for a learner who has not installed anything.
try:
    import requests
except ImportError:  # pragma: no cover - depends on the learner's environment
    requests = None  # type: ignore[assignment]

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]

TMP = Path(__file__).parent / "tmp"

# The canned payload used when the network is unavailable. Same shape as the real
# endpoint, so every later section behaves identically online and offline.
CANNED_PAYLOAD: dict[str, Any] = {
    "userId": 1,
    "id": 1,
    "title": "canned offline payload",
    "completed": False,
}


def banner(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


# ---------------------------------------------------------------------------
banner("1. Anatomy of a request and a response")
# ---------------------------------------------------------------------------

print("A request you might send:")
print("""    GET /v1/readings?page=2&limit=50 HTTP/1.1
    Host: api.example.com
    Authorization: Bearer sk_live_***redacted***
    Accept: application/json""")
print("\nThe response you might get:")
print("""    HTTP/1.1 200 OK
    Content-Type: application/json
    X-RateLimit-Remaining: 47

    {"items": [...], "next": "/v1/readings?page=3"}""")

# Building URLs by hand is where encoding bugs live. Let the library do it.
base = "https://api.example.com/v1/"
query = urlencode({"page": 2, "limit": 50, "q": "temp sensor"})
print("\nurljoin + urlencode:", urljoin(base, "readings") + "?" + query)
print("note the space became '+' and nothing else was mangled")

STATUS_MEANING = {
    200: "OK - parse the body",
    201: "Created - read the Location header",
    204: "No Content - success, nothing to parse",
    400: "Bad Request - your payload; retrying will not help",
    401: "Unauthorized - missing/invalid credentials",
    404: "Not Found - wrong URL",
    429: "Too Many Requests - slow down, read Retry-After",
    500: "Server Error - their bug, retry cautiously",
    503: "Unavailable - transient, retry with backoff",
}
print("\nstatus code cheat sheet:")
for code, meaning in STATUS_MEANING.items():
    family = {2: "success", 3: "redirect", 4: "your fault", 5: "their fault"}[code // 100]
    print(f"  {code}  [{family:<11}] {meaning}")


# ---------------------------------------------------------------------------
banner("2. One real request, with a guaranteed offline fallback")
# ---------------------------------------------------------------------------

REAL_URL = "https://jsonplaceholder.typicode.com/todos/1"


def fetch_live_or_canned(url: str, timeout: float = 5.0) -> tuple[dict[str, Any], str]:
    """Try the network once. Degrade to a canned payload on ANY failure.

    Returns (payload, source) so the caller can report which path was taken.
    """
    if requests is None:
        return CANNED_PAYLOAD, "canned (requests not installed)"
    try:
        # timeout is NOT optional: without it this call can block forever.
        response = requests.get(url, timeout=timeout, headers={"Accept": "application/json"})
        response.raise_for_status()          # 4xx/5xx become exceptions here
        return response.json(), f"live HTTP {response.status_code}"
    except Exception as error:  # noqa: BLE001 - a demo must never crash offline
        return CANNED_PAYLOAD, f"canned (network unavailable: {type(error).__name__})"


payload, source = fetch_live_or_canned(REAL_URL)
print("requests installed:", requests is not None)
print("httpx installed   :", httpx is not None, "(same API shape, plus async - Day 20)")
print("source            :", source)
print("payload           :", json.dumps(payload, sort_keys=True)[:120])
print("\nEverything below this line is offline, deterministic, and testable.")


# ---------------------------------------------------------------------------
banner("3-4. Timeouts and the four failure modes")
# ---------------------------------------------------------------------------

print("requests.get(url, timeout=10)          # one value: connect AND read")
print("requests.get(url, timeout=(3.05, 27))  # (connect, read)")
print()
print("The four failures that actually happen, and the right response:")
for name, response in [
    ("Timeout", "retry with backoff"),
    ("ConnectionError", "retry slowly; DNS/refused/network down"),
    ("HTTPError 429/5xx", "retry with backoff"),
    ("HTTPError 4xx", "do NOT retry; fix the request"),
    ("ValueError from .json()", "do not retry; log the first 200 chars of the body"),
]:
    print(f"  {name:<24} -> {response}")


# A fake transport lets us exercise error handling with zero network. This is the
# same trick the exercises and tests use.
class FakeResponse:
    """The three attributes of a response that our logic cares about."""

    def __init__(self, status_code: int, payload: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text or json.dumps(payload)

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("Expecting value: line 1 column 1 (char 0)")
        return self._payload


def describe(response: FakeResponse) -> str:
    """Classify a response the way real error handling does."""
    if 200 <= response.status_code < 300:
        try:
            response.json()
        except ValueError:
            return "2xx but the body is not JSON -> log the body, do not retry"
        return "success -> parse the body"
    if response.status_code in {429, 500, 502, 503, 504}:
        return "transient -> retry with backoff"
    return "client error -> fix the request, do not retry"


for fake in [
    FakeResponse(200, {"ok": True}),
    FakeResponse(200, None, text="<html>maintenance</html>"),
    FakeResponse(404, {"error": "not found"}),
    FakeResponse(503, {"error": "unavailable"}),
]:
    print(f"  HTTP {fake.status_code}: {describe(fake)}")


# ---------------------------------------------------------------------------
banner("5. Pagination with an injected fetch")
# ---------------------------------------------------------------------------

PAGES: dict[str, dict[str, Any]] = {
    "/v1/readings": {
        "items": [{"sensor": "s1", "value": 21.5}, {"sensor": "s2", "value": 19.0}],
        "next": "/v1/readings?cursor=abc",
    },
    "/v1/readings?cursor=abc": {
        "items": [{"sensor": "s3", "value": 25.5}],
        "next": "/v1/readings?cursor=def",
    },
    "/v1/readings?cursor=def": {"items": [{"sensor": "s4", "value": 30.0}], "next": None},
}

fetch_log: list[str] = []


def fake_fetch(url: str) -> dict[str, Any]:
    """A 'transport' that returns canned dicts. No network, no mocking library."""
    fetch_log.append(url)
    return PAGES[url]


def iter_all(fetch: Callable[[str], dict[str, Any]], first_url: str, max_pages: int = 100) -> Iterator[dict[str, Any]]:
    """Yield every item across pages. Lazy, and bounded so a server bug cannot hang us."""
    url: str | None = first_url
    pages = 0
    while url and pages < max_pages:
        payload = fetch(url)
        yield from payload.get("items", [])
        url = payload.get("next")
        pages += 1


all_items = list(iter_all(fake_fetch, "/v1/readings"))
print("items collected :", len(all_items), "->", [item["sensor"] for item in all_items])
print("urls fetched    :", fetch_log)

# Laziness pays off: stopping early stops fetching.
fetch_log.clear()
first = next(iter_all(fake_fetch, "/v1/readings"))
print("early exit      :", first["sensor"], "after", len(fetch_log), "request(s)")

# The bound is what stops an infinite `next` loop from running forever.
fetch_log.clear()
LOOPING = {"/loop": {"items": [{"n": 1}], "next": "/loop"}}
bounded = list(iter_all(lambda url: LOOPING[url], "/loop", max_pages=4))
print("looping server  :", len(bounded), "items then stopped by max_pages=4")


# ---------------------------------------------------------------------------
banner("6. Retries with exponential backoff")
# ---------------------------------------------------------------------------

RETRYABLE = {429, 500, 502, 503, 504}


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Delay before retry number `attempt` (1-based), capped."""
    return min(base * 2 ** (attempt - 1), cap)


def should_retry(status: int, attempt: int, max_attempts: int) -> bool:
    if attempt >= max_attempts:
        return False
    return status in RETRYABLE


print("backoff schedule (base=1.0, cap=30):")
print("  ", [backoff_delay(a) for a in range(1, 8)])
print("backoff schedule (base=0.25, cap=2):")
print("  ", [backoff_delay(a, base=0.25, cap=2.0) for a in range(1, 7)])
print()
for status in (200, 404, 429, 503):
    print(f"  should_retry({status}, attempt=1, max=3) -> {should_retry(status, 1, 3)}")
print("  should_retry(503, attempt=3, max=3) ->", should_retry(503, 3, 3), "(bound reached)")

# A retry loop with the sleep injected, so a test can run it instantly.
responses = [FakeResponse(503), FakeResponse(503), FakeResponse(200, {"ok": True})]
slept: list[float] = []


def flaky_fetch(url: str) -> FakeResponse:
    return responses.pop(0)


def fetch_with_retries(
    fetch: Callable[[str], FakeResponse],
    url: str,
    max_attempts: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    for attempt in range(1, max_attempts + 1):
        response = fetch(url)
        if 200 <= response.status_code < 300:
            return response.json()
        if not should_retry(response.status_code, attempt, max_attempts):
            raise RuntimeError(f"giving up on HTTP {response.status_code}")
        sleep(backoff_delay(attempt, base=0.5, cap=8.0))
    raise RuntimeError("exhausted retries")


result = fetch_with_retries(flaky_fetch, "/x", max_attempts=4, sleep=slept.append)
print("\nrecovered after two 503s:", result)
print("delays that WOULD have been slept:", slept, "(the test never waits)")
print("injecting `sleep` is why this demo finishes in microseconds")


# ---------------------------------------------------------------------------
banner("7-8. Rate limits and secrets")
# ---------------------------------------------------------------------------

headers = {
    "X-RateLimit-Limit": "100",
    "X-RateLimit-Remaining": "3",
    "X-RateLimit-Reset": "1710510000",
    "Retry-After": "12",
}
remaining = int(headers["X-RateLimit-Remaining"])
print("remaining calls :", remaining)
print("decision        :", "throttle now" if remaining < 10 else "carry on")
print("Retry-After     :", headers["Retry-After"], "seconds - obey it exactly, do not guess")

os.environ["PZH_DEMO_API_KEY"] = "sk_live_super_secret_value"
api_key = os.environ.get("PZH_DEMO_API_KEY")
print("\nkey loaded from environment:", api_key is not None)


def redact(value: str | None, keep: int = 4) -> str:
    """What must happen to a secret before it can appear in a log line."""
    if not value:
        return "<unset>"
    return value[:keep] + "*" * (len(value) - keep)


print("safe to log     :", redact(api_key))
print("NEVER log       : the raw value, or the whole headers dict")
missing = os.environ.get("PZH_DEMO_MISSING_KEY")
print("missing secret  :", missing, "-> fail loudly at startup, not at 3am")
del os.environ["PZH_DEMO_API_KEY"]


# ---------------------------------------------------------------------------
banner("9. sqlite3: schema, insert, select, update, transactions")
# ---------------------------------------------------------------------------

TMP.mkdir(exist_ok=True)
db_path = TMP / "readings.db"

with closing(sqlite3.connect(db_path)) as connection:
    connection.row_factory = sqlite3.Row        # rows behave like dicts
    connection.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor TEXT    NOT NULL,
            value  REAL    NOT NULL,
            taken  TEXT    NOT NULL,
            UNIQUE(sensor, taken)
        )
    """)
    connection.commit()
    print("schema created  :", db_path.name)

    rows = [
        ("s1", 21.5, "2024-03-15T13:00:00+00:00"),
        ("s2", 19.0, "2024-03-15T13:00:00+00:00"),
        ("s3", 25.5, "2024-03-15T13:00:00+00:00"),
    ]
    with connection:                             # one transaction for all inserts
        connection.executemany(
            "INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)", rows
        )
    print("inserted        :", len(rows), "rows in ONE transaction")

    selected = connection.execute(
        "SELECT sensor, value FROM readings WHERE value > ? ORDER BY value DESC",
        (20.0,),                                 # a one-element tuple needs the comma
    ).fetchall()
    print("value > 20      :", [(row["sensor"], row["value"]) for row in selected])

    connection.execute("UPDATE readings SET value = ? WHERE sensor = ?", (22.0, "s1"))
    connection.commit()
    updated = connection.execute(
        "SELECT value FROM readings WHERE sensor = ?", ("s1",)
    ).fetchone()
    print("after UPDATE    : s1 =", updated["value"])

    # Idempotent re-run: the UNIQUE key plus ON CONFLICT means running the same
    # load twice converges instead of duplicating.
    before = connection.execute("SELECT count(*) AS n FROM readings").fetchone()["n"]
    with connection:
        connection.executemany("""
            INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)
            ON CONFLICT(sensor, taken) DO UPDATE SET value = excluded.value
        """, rows)
    after = connection.execute("SELECT count(*) AS n FROM readings").fetchone()["n"]
    print(f"re-ran the load : {before} rows -> {after} rows (idempotent)")
    restored = connection.execute(
        "SELECT value FROM readings WHERE sensor = ?", ("s1",)
    ).fetchone()["value"]
    print("upsert updated  : s1 back to", restored, "(excluded.value won)")

    # A failing transaction rolls back everything inside the block.
    try:
        with connection:
            connection.execute(
                "INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)",
                ("s9", 1.0, "2024-03-15T14:00:00+00:00"),
            )
            connection.execute("INSERT INTO readings (sensor) VALUES (?)", ("broken",))
    except sqlite3.IntegrityError as error:
        rolled_back = connection.execute(
            "SELECT count(*) AS n FROM readings WHERE sensor = ?", ("s9",)
        ).fetchone()["n"]
        print("failed txn      :", type(error).__name__, "-> s9 rows present:", rolled_back)


# ---------------------------------------------------------------------------
banner("10. SQL injection, demonstrated")
# ---------------------------------------------------------------------------

with closing(sqlite3.connect(db_path)) as connection:
    connection.row_factory = sqlite3.Row

    hostile = "x' OR '1'='1"

    # WRONG: the value becomes part of the statement.
    unsafe_sql = f"SELECT sensor FROM readings WHERE sensor = '{hostile}'"
    print("unsafe SQL      :", unsafe_sql)
    leaked = connection.execute(unsafe_sql).fetchall()
    print("rows returned   :", len(leaked), "<- the WHOLE table leaked")

    # RIGHT: the value travels beside the statement and is never parsed as SQL.
    safe = connection.execute(
        "SELECT sensor FROM readings WHERE sensor = ?", (hostile,)
    ).fetchall()
    print("parameterised   :", len(safe), "rows (the literal string matches nothing)")

    # The destructive variant. sqlite3.execute refuses multiple statements, which
    # is a safety net you should never rely on.
    destructive = "x'; DROP TABLE readings; --"
    try:
        connection.execute(f"SELECT * FROM readings WHERE sensor = '{destructive}'")
    except (sqlite3.Warning, sqlite3.Error) as error:
        # Python's sqlite3 refuses two statements in one execute(); the exact
        # exception type has changed between versions, hence the broad tuple.
        print("multi-statement :", type(error).__name__, "-", str(error)[:60])
    still_there = connection.execute(
        "SELECT count(*) AS n FROM readings"
    ).fetchone()["n"]
    print("table survived  :", still_there, "rows - but only because of the driver")
    print("the OR '1'='1' leak above needed no multiple statements at all")

    # Named placeholders read better once there are several parameters.
    named = connection.execute(
        "SELECT sensor FROM readings WHERE value > :floor AND sensor != :skip",
        {"floor": 20.0, "skip": "s3"},
    ).fetchall()
    print("named params    :", [row["sensor"] for row in named])


# ---------------------------------------------------------------------------
banner("12. The three layers, wired together")
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Reading:
    """LOGIC layer: a validated record, independent of HTTP and SQL."""

    sensor: str
    value: float
    taken: str


def parse_items(items: list[dict[str, Any]]) -> tuple[list[Reading], list[dict[str, Any]]]:
    """Split raw payload items into good records and quarantined junk."""
    good: list[Reading] = []
    bad: list[dict[str, Any]] = []
    for item in items:
        try:
            good.append(
                Reading(
                    sensor=str(item["sensor"]),
                    value=float(item["value"]),
                    taken=str(item.get("taken", "2024-03-15T13:00:00+00:00")),
                )
            )
        except (KeyError, TypeError, ValueError):
            bad.append(item)                     # quarantine, never crash
    return good, bad


def save(connection: sqlite3.Connection, records: list[Reading]) -> int:
    """STORAGE layer: parameterised, batched, idempotent."""
    with connection:
        connection.executemany("""
            INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)
            ON CONFLICT(sensor, taken) DO UPDATE SET value = excluded.value
        """, [(r.sensor, r.value, r.taken) for r in records])
    return len(records)


def sync(fetch: Callable[[str], dict[str, Any]], connection: sqlite3.Connection, url: str) -> dict[str, int]:
    """The whole pipeline. `fetch` is a parameter, so this is testable offline."""
    items = list(iter_all(fetch, url))
    good, bad = parse_items(items)
    return {"fetched": len(items), "saved": save(connection, good), "quarantined": len(bad)}


DIRTY_PAGES = {
    "/v1/dirty": {
        "items": [
            {"sensor": "s10", "value": "21.5"},        # a string that parses: fine
            {"sensor": "s11"},                          # missing value: quarantine
            {"sensor": "s12", "value": "abc"},          # unparseable: quarantine
            {"sensor": "s13", "value": 30.0},
        ],
        "next": None,
    }
}

with closing(sqlite3.connect(db_path)) as connection:
    summary = sync(lambda url: DIRTY_PAGES[url], connection, "/v1/dirty")
    print("sync summary    :", summary)
    summary_again = sync(lambda url: DIRTY_PAGES[url], connection, "/v1/dirty")
    total = connection.execute("SELECT count(*) AS n FROM readings").fetchone()[0]
    print("ran it again    :", summary_again, "-> table still has", total, "rows")
    print("that property is idempotence, and Day 21 requires it")

# Clean up: no files left behind, so this script can be run any number of times.
shutil.rmtree(TMP)
print()
print("removed tmp/    :", not TMP.exists())
print("Done. Now open exercises.py in this folder.")
