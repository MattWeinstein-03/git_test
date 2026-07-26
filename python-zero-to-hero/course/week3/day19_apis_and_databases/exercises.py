"""Day 19 exercises — HTTP APIs and SQLite, all testable offline.

Nothing here may touch the network. Every function either works on a payload that
has already been fetched, or takes the fetching function as a parameter so a test
can hand it canned data. That is not a testing trick — it is the design that
makes network code reviewable (see LESSON.md section 12).

`Reading` below is given to you; do not change it. Grade yourself from the course
root with:

    python check.py day19
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Callable

# Status codes worth retrying: rate limiting plus the server-side failures.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True, slots=True)
class Reading:
    """One validated sensor reading. Given to you — do not modify.

    Attributes:
        sensor: the sensor id, e.g. "s1".
        value: the measurement as a float.
        taken: an ISO-8601 timestamp string.
    """

    sensor: str
    value: float
    taken: str


def build_url(base: str, path: str, params: Mapping[str, Any] | None = None) -> str:
    """Join a base URL and a path, then append an encoded query string.

    Rules:
      - exactly one "/" between base and path, whatever slashes they carry
      - no trailing "?" when there are no params
      - params are encoded (spaces and "&" must not break the URL) and appear in
        the order given
      - a param whose value is None is omitted entirely
      - values are converted with `str` (so True becomes "True", 2 becomes "2")

    Use `urllib.parse.urlencode`; do not hand-roll the encoding.

    Args:
        base: e.g. "https://api.example.com/v1" or "https://api.example.com/v1/".
        path: e.g. "readings" or "/readings".
        params: query parameters, or None.

    Returns:
        The full URL.

    Examples:
        >>> build_url("https://api.example.com/v1", "readings")
        'https://api.example.com/v1/readings'
        >>> build_url("https://api.example.com/v1/", "/readings", {"page": 2})
        'https://api.example.com/v1/readings?page=2'
        >>> build_url("https://x.io", "search", {"q": "a b", "limit": None})
        'https://x.io/search?q=a+b'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: build_url")


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Return the seconds to wait before retry number `attempt` (1-based).

    Exponential: `base * 2 ** (attempt - 1)`, never more than `cap`. No jitter,
    so the result is deterministic and testable — real code multiplies by
    `random.uniform(0.5, 1.5)`.

    Args:
        attempt: which retry this is; 1 is the first retry.
        base: the delay before the first retry.
        cap: the maximum delay.

    Returns:
        The delay in seconds as a float.

    Raises:
        ValueError: if `attempt` is less than 1.

    Examples:
        >>> [backoff_delay(a) for a in (1, 2, 3, 4)]
        [1.0, 2.0, 4.0, 8.0]
        >>> backoff_delay(9)
        30.0
        >>> backoff_delay(3, base=0.25, cap=2.0)
        1.0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: backoff_delay")


def should_retry(status: int, attempt: int, max_attempts: int) -> bool:
    """Decide whether a request that returned `status` should be retried.

    Retry only the transient statuses in `RETRYABLE_STATUS` (429 and the 5xx
    family listed above), and only while attempts remain: `attempt` is the number
    of the attempt that just failed, so once `attempt >= max_attempts` the answer
    is always False. A 2xx, 3xx or other 4xx is never retried — you would get
    the same answer, only slower.

    Args:
        status: the status code that came back.
        attempt: the 1-based number of the attempt that just completed.
        max_attempts: the total number of attempts allowed.

    Returns:
        True if another attempt should be made.

    Examples:
        >>> should_retry(503, attempt=1, max_attempts=3)
        True
        >>> should_retry(503, attempt=3, max_attempts=3)
        False
        >>> should_retry(404, attempt=1, max_attempts=3)
        False
        >>> should_retry(429, attempt=2, max_attempts=5)
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: should_retry")


def parse_readings(
    payload: Mapping[str, Any], default_taken: str = "1970-01-01T00:00:00+00:00"
) -> tuple[list[Reading], list[dict[str, Any]]]:
    """Turn a fetched payload into `Reading` objects, quarantining bad records.

    The payload looks like `{"items": [ {...}, {...} ]}`. A missing or non-list
    "items" key means no items at all (return two empty lists) rather than an
    error.

    An item is good when it has a non-empty "sensor" that is a string and a
    "value" that `float()` accepts (so the string "21.5" is fine, "abc" is not,
    and None is not). "taken" is optional and defaults to `default_taken`.
    Anything else is quarantined: appended, unchanged, to the second list. Never
    raise because of a bad record — a pipeline that dies on one malformed row is
    a pipeline that dies every night.

    Args:
        payload: the fetched dict.
        default_taken: timestamp to use when an item has no "taken".

    Returns:
        (readings, quarantined) — good `Reading` objects in payload order, and the
        raw dicts that failed.

    Examples:
        >>> good, bad = parse_readings({"items": [
        ...     {"sensor": "s1", "value": "21.5", "taken": "2024-01-01T00:00:00+00:00"},
        ...     {"sensor": "s2"},
        ...     {"sensor": "", "value": 1.0},
        ... ]})
        >>> good
        [Reading(sensor='s1', value=21.5, taken='2024-01-01T00:00:00+00:00')]
        >>> len(bad)
        2
        >>> parse_readings({})
        ([], [])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: parse_readings")


def iter_pages(
    fetch: Callable[[str], Mapping[str, Any]], first_url: str, max_pages: int = 100
) -> Iterator[dict[str, Any]]:
    """Yield every item across a cursor-paginated endpoint, lazily.

    `fetch(url)` returns a payload like
    `{"items": [...], "next": "<url or None>"}`. Follow "next" until it is
    missing, None or empty. Stop after `max_pages` fetches whatever the server
    says — an endpoint that keeps returning the same "next" must not spin
    forever.

    Must be lazy: a caller that takes one item must cause exactly one fetch.

    Args:
        fetch: the injected transport. In production it wraps `requests.get`; in
            tests it returns canned dicts.
        first_url: where to start.
        max_pages: hard limit on the number of fetches.

    Yields:
        The items, page by page, in order.

    Raises:
        ValueError: if `max_pages` is less than 1 (raised when `iter_pages` is
            called, not on the first `next()` — see Day 15, "validate before you
            yield").

    Examples:
        >>> pages = {
        ...     "/a": {"items": [1, 2], "next": "/b"},
        ...     "/b": {"items": [3], "next": None},
        ... }
        >>> list(iter_pages(lambda url: pages[url], "/a"))
        [1, 2, 3]
        >>> list(iter_pages(lambda url: {"items": [1], "next": "/loop"}, "/loop", 3))
        [1, 1, 1]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: iter_pages")


def fetch_with_retries(
    fetch: Callable[[str], tuple[int, Any]],
    url: str,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    cap: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[Any, list[float]]:
    """Call `fetch` until it succeeds, retrying transient failures with backoff.

    `fetch(url)` returns `(status_code, payload)`. On a 2xx, return the payload.
    Otherwise use `should_retry` to decide: if it says yes, sleep for
    `backoff_delay(attempt, base_delay, cap)` using the injected `sleep` and try
    again; if it says no, raise `RuntimeError` whose message contains the final
    status code.

    `sleep` is a parameter so tests run instantly — this is the same injection
    idea as `fetch`.

    Args:
        fetch: injected transport returning (status, payload).
        url: passed straight to `fetch` on every attempt.
        max_attempts: total attempts allowed, at least 1.
        base_delay: first backoff delay.
        cap: maximum backoff delay.
        sleep: called with each delay; default `time.sleep`.

    Returns:
        (payload, delays) where `delays` lists the delays actually slept, in
        order. A first-attempt success returns an empty delay list.

    Raises:
        RuntimeError: when the attempts are exhausted or the status is not
            retryable. The message must contain the status code as text.
        ValueError: if `max_attempts` is less than 1.

    Examples:
        >>> calls = [(503, None), (200, {"ok": True})]
        >>> fetch_with_retries(lambda url: calls.pop(0), "/x", sleep=lambda s: None)
        ({'ok': True}, [1.0])
        >>> fetch_with_retries(lambda url: (404, None), "/x", sleep=lambda s: None)
        Traceback (most recent call last):
        RuntimeError: request to /x failed with status 404
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: fetch_with_retries")


def init_db(connection: sqlite3.Connection) -> None:
    """Create the `readings` table if it does not exist.

    Columns, exactly:
      id      INTEGER PRIMARY KEY AUTOINCREMENT
      sensor  TEXT    NOT NULL
      value   REAL    NOT NULL
      taken   TEXT    NOT NULL
    plus a UNIQUE constraint on (sensor, taken) — that constraint is what makes
    the upsert in `save_readings` idempotent, so it is not optional.

    Calling this twice must not fail.

    Args:
        connection: an open sqlite3 connection.

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> init_db(conn)
        >>> init_db(conn)                       # safe to repeat
        >>> conn.execute("SELECT count(*) FROM readings").fetchone()[0]
        0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: init_db")


def save_readings(connection: sqlite3.Connection, readings: Iterable[Reading]) -> int:
    """Insert or update readings, idempotently, in one transaction.

    Use parameterised SQL (`?` placeholders) — never string formatting. On a
    conflict with the UNIQUE (sensor, taken) key, update `value` to the new one,
    so re-running a load converges instead of duplicating rows.

    Call `init_db` yourself if you like, or assume it has been called; the tests
    always call it first.

    Args:
        connection: an open sqlite3 connection whose schema exists.
        readings: the records to write.

    Returns:
        How many readings were processed (inserted plus updated).

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> init_db(conn)
        >>> r = Reading("s1", 21.5, "2024-01-01T00:00:00+00:00")
        >>> save_readings(conn, [r])
        1
        >>> save_readings(conn, [Reading("s1", 99.0, "2024-01-01T00:00:00+00:00")])
        1
        >>> conn.execute("SELECT count(*), max(value) FROM readings").fetchone()
        (1, 99.0)
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: save_readings")


def find_by_sensor(connection: sqlite3.Connection, sensor: str) -> list[dict[str, Any]]:
    """Return every stored reading for one sensor, newest `taken` first.

    This is the injection exercise. `sensor` is untrusted input, so it MUST reach
    SQLite as a bound parameter: `"... WHERE sensor = ?", (sensor,)`. If you build
    the SQL with an f-string, the hostile value `"x' OR '1'='1"` returns the whole
    table and the graded tests will catch it.

    Args:
        connection: an open sqlite3 connection whose schema exists.
        sensor: the sensor id to look up, from an untrusted source.

    Returns:
        A list of dicts with keys "sensor", "value", "taken", ordered by "taken"
        descending. An unknown sensor gives an empty list.

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> init_db(conn)
        >>> save_readings(conn, [Reading("s1", 1.0, "2024-01-01T00:00:00+00:00")])
        1
        >>> find_by_sensor(conn, "s1")
        [{'sensor': 's1', 'value': 1.0, 'taken': '2024-01-01T00:00:00+00:00'}]
        >>> find_by_sensor(conn, "x' OR '1'='1")
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: find_by_sensor")


def sync_readings(
    fetch: Callable[[str], Mapping[str, Any]],
    connection: sqlite3.Connection,
    first_url: str,
    max_pages: int = 100,
) -> dict[str, int]:
    """Run the whole pipeline: paginate, parse, quarantine, persist.

    Steps, reusing the functions you have already written:
      1. walk every page with `iter_pages`
      2. parse each page's items with `parse_readings` (wrap the items back into
         a `{"items": [...]}` payload, or collect all items and parse once)
      3. store the good records with `save_readings` after `init_db`
      4. return a summary

    Args:
        fetch: injected transport, as in `iter_pages`.
        connection: an open sqlite3 connection.
        first_url: where to start paginating.
        max_pages: passed through to `iter_pages`.

    Returns:
        A dict with exactly these keys:
          "fetched"     -> int, raw items seen across all pages
          "saved"       -> int, good records written
          "quarantined" -> int, malformed items skipped
          "stored"      -> int, total rows in the table afterwards

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(":memory:")
        >>> pages = {"/a": {"items": [
        ...     {"sensor": "s1", "value": 1.0, "taken": "2024-01-01T00:00:00+00:00"},
        ...     {"sensor": "bad"},
        ... ], "next": None}}
        >>> sync_readings(lambda url: pages[url], conn, "/a") == {
        ...     "fetched": 2, "saved": 1, "quarantined": 1, "stored": 1}
        True
        >>> sync_readings(lambda url: pages[url], conn, "/a")["stored"]
        1
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: sync_readings")


if __name__ == "__main__":
    print("Run `python check.py day19` from the course root to grade your work.")
