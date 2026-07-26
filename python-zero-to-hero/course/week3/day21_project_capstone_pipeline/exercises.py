"""Day 21 — Project 3: sensorpipe, a complete data pipeline.

This file is the graded API surface. LESSON.md is the brief and it specifies every
return value, message and ordering the tests check — read it first, and keep it
open.

Work milestone by milestone. Partial credit is visible from M1 onwards:

    python check.py day21
    python check.py day21 -v
    python -m pytest course/week3/day21_project_capstone_pipeline -q -k m3

Run the app itself with:

    SENSORPIPE_DB=sensorpipe.db python course/week3/day21_project_capstone_pipeline/exercises.py report

The brief asks you to put the real code in a `pipeline/` package next to this
file, one module per milestone, and to reduce this file to a re-export:

    from pipeline.config import Settings, load_settings
    from pipeline.extract import Record, extract_records, fetch_page, ...

Either way the graded names must be importable from this module. Filling the stubs
in place works and is graded the same; the package is what makes the result worth
showing someone.

House rules for this project:
  * only `config.py` may look at the environment, and only through its `env`
    parameter (which defaults to `os.environ`)
  * only `main` configures logging, with `logging.basicConfig(level=...)` and
    without `force=True`
  * `requests` is imported lazily, inside the one branch of `main` that needs it
  * every SQL statement uses `?` placeholders — searching this file for `f"SELECT`
    must find nothing
  * store aware UTC timestamps, as ISO-8601 strings
"""

from __future__ import annotations

import argparse
import logging  # noqa: F401 - M5 configures logging
import sqlite3
import time
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace  # noqa: F401 - M1/M2/M3 need these
from datetime import datetime, timezone  # noqa: F401 - M2 needs both
from pathlib import Path
from typing import Any, Callable

# Statuses worth retrying: the server is asking you to come back, not telling you
# the request was wrong. Given to you.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

# A transport is any callable that takes a URL and returns (status, payload).
# Nothing in this file may know more about HTTP than that.
Fetch = Callable[[str], "tuple[int, Mapping[str, Any]]"]

# The band boundaries from the brief. Given to you, so the tests and your code
# cannot disagree about them.
LOW_BAND_BELOW = 10.0
HIGH_BAND_FROM = 25.0


# ===========================================================================
# MILESTONE 1 — configuration (pipeline/config.py)
# ===========================================================================
class Settings:
    """Validated application configuration. Make this a frozen dataclass.

    Declare it as `@dataclass(frozen=True, slots=True)` with these fields, in
    this order:

        source_url: str
        db_path: Path
        batch_size: int
        max_pages: int
        min_value: float
        verbose: bool

    Frozen because configuration must not change while the program runs: an
    attempt to assign to a field must raise `dataclasses.FrozenInstanceError`.

    Examples:
        settings = Settings(
            source_url="https://example.invalid/v1/readings",
            db_path=Path("sensorpipe.db"),
            batch_size=100,
            max_pages=10,
            min_value=0.0,
            verbose=False,
        )
        settings.batch_size -> 100
        settings.db_path -> PosixPath('sensorpipe.db')
        settings.verbose = True -> FrozenInstanceError
    """

    # TODO: your code here — add the decorator above the class, replace this
    # __init__ with the six annotated fields, and delete this method.
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError("M1: Settings")


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build `Settings` from a mapping of environment variables.

    `env=None` means read `os.environ`. Taking the mapping as a parameter is what
    makes configuration testable without patching the process environment: the
    same injection idea as `fetch`.

    Variables, defaults and validation (the full table is in LESSON.md):

        SENSORPIPE_URL         str    https://example.invalid/v1/readings
                                      must start with http:// or https://
        SENSORPIPE_DB          Path   sensorpipe.db
        SENSORPIPE_BATCH_SIZE  int    100     1 <= n <= 10000
        SENSORPIPE_MAX_PAGES   int    10      n >= 1
        SENSORPIPE_MIN_VALUE   float  0.0
        SENSORPIPE_VERBOSE     bool   0       1/true/yes/on, 0/false/no/off

    Args:
        env: mapping of variable names to raw string values, or None for
            `os.environ`.

    Returns:
        A validated, frozen `Settings`.

    Raises:
        ValueError: on any invalid value. The message MUST contain the variable
            name and the offending value, because that message is what somebody
            reads at 3 a.m. instead of your source code.

    Examples:
        load_settings({}).batch_size -> 100
        load_settings({}).db_path -> PosixPath('sensorpipe.db')
        load_settings({"SENSORPIPE_MAX_PAGES": "3"}).max_pages -> 3
        load_settings({"SENSORPIPE_VERBOSE": "yes"}).verbose -> True
        load_settings({"SENSORPIPE_VERBOSE": "off"}).verbose -> False
        load_settings({"SENSORPIPE_URL": "ftp://x"})
            -> ValueError("SENSORPIPE_URL='ftp://x' is invalid: ...")
        load_settings({"SENSORPIPE_BATCH_SIZE": "0"})
            -> ValueError mentioning SENSORPIPE_BATCH_SIZE and '0'
    """
    # TODO: your code here
    raise NotImplementedError("M1: load_settings")


# ===========================================================================
# MILESTONE 2 — extract (pipeline/extract.py)
# ===========================================================================
class Record:
    """One validated reading. Make this a frozen dataclass.

    Declare it as `@dataclass(frozen=True, slots=True)` with these fields, in
    this order:

        sensor: str
        value: float
        taken: datetime      # timezone-aware, in UTC
        region: str          # lowercase, "unknown" when absent
        band: str = ""       # filled in by M3

    Frozen, so the transform stage has to produce new objects with
    `dataclasses.replace` instead of mutating shared state.

    Examples:
        record = Record("s1", 21.5, datetime(2024, 3, 15, 13, tzinfo=timezone.utc), "eu")
        record.band -> ""
        replace(record, band="normal").band -> "normal"
        record.sensor = "s2" -> FrozenInstanceError
        Record("s1", 1.0, t, "eu") == Record("s1", 1.0, t, "eu") -> True
    """

    # TODO: your code here — add the decorator, replace this __init__ with the
    # five annotated fields, and delete this method.
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError("M2: Record")


def normalise_record(raw: Mapping[str, Any]) -> Record:
    """Turn one raw payload item into a `Record`.

    Normalises: `sensor` is stripped; `value` goes through `float`; `taken`
    becomes an aware UTC `datetime` (a "Z" suffix, an explicit offset, and a naive
    timestamp treated as UTC must all work); `region` is stripped and lowercased,
    defaulting to "unknown".

    Args:
        raw: one item from a page's "items" list.

    Returns:
        A `Record` with `band` left as "".

    Raises:
        ValueError: if `sensor` is missing, not a string, or empty after
            stripping; if `value` is missing or `float()` cannot read it; if
            `taken` is missing or is not an ISO-8601 timestamp.

    Examples:
        normalise_record({"sensor": " s1 ", "value": "21.5",
                          "taken": "2024-03-15T13:00:00Z", "region": "EU"})
            -> Record(sensor='s1', value=21.5,
                      taken=datetime(2024, 3, 15, 13, 0, tzinfo=timezone.utc),
                      region='eu', band='')
        normalise_record({"sensor": "s2", "value": 19.0,
                          "taken": "2024-03-15T13:00:00+01:00"}).taken.hour -> 12
        normalise_record({"sensor": "s2", "value": 19.0,
                          "taken": "2024-03-15T13:00:00"}).region -> 'unknown'
        normalise_record({"sensor": "", "value": 5.0, "taken": "..."}) -> ValueError
        normalise_record({"sensor": "s4", "value": "abc", "taken": "..."}) -> ValueError
    """
    # TODO: your code here
    raise NotImplementedError("M2: normalise_record")


def normalise_all(
    raws: Iterable[Mapping[str, Any]],
) -> tuple[list[Record], list[dict[str, Any]]]:
    """Normalise many raw items, quarantining the ones that fail.

    This function never raises: one bad row must not end a nightly run.

    Args:
        raws: the raw items, in source order.

    Returns:
        (records, quarantined). `quarantined` holds the original dicts, unchanged
        and in order.

    Examples:
        good = {"sensor": "s1", "value": 1.0, "taken": "2024-03-15T13:00:00Z"}
        bad = {"sensor": "s4", "value": "abc", "taken": "2024-03-15T13:00:00Z"}
        records, quarantined = normalise_all([good, bad])
        len(records) -> 1
        quarantined -> [{'sensor': 's4', 'value': 'abc', 'taken': '2024-03-15T13:00:00Z'}]
        normalise_all([]) -> ([], [])
    """
    # TODO: your code here
    raise NotImplementedError("M2: normalise_all")


def fetch_page(
    fetch: Fetch,
    url: str,
    max_attempts: int = 3,
    base_delay: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
) -> Mapping[str, Any]:
    """Fetch one page, retrying transient failures with exponential backoff.

    Args:
        fetch: injected transport; returns (status, payload).
        url: the page to fetch.
        max_attempts: total attempts allowed, at least 1.
        base_delay: the first backoff delay in seconds; the delays grow
            exponentially from it. 0.0 means "do not wait", which is what tests
            use.
        sleep: injected sleeper, so a test never actually waits.

    Returns:
        The payload from the first 2xx response.

    Raises:
        RuntimeError: when the attempts are used up, or the status is not
            retryable. The message must mention the status.
        ValueError: if `max_attempts` is less than 1.

    Examples:
        fetch_page(lambda url: (200, {"items": []}), "/a") -> {'items': []}
        fetch_page(lambda url: (404, {}), "/a") -> RuntimeError mentioning 404
        # 503 then 200, with base_delay=0.5, calls sleep(0.5) once and returns
        # the second payload.
    """
    # TODO: your code here
    raise NotImplementedError("M2: fetch_page")


def extract_records(
    fetch: Fetch,
    settings: Settings,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[list[Record], list[dict[str, Any]], list[str]]:
    """Walk every page from `settings.source_url`, normalising as it goes.

    Follow the "next" key of each payload until it is missing or falsy, fetching
    at most `settings.max_pages` pages.

    Args:
        fetch: injected transport; returns (status, payload).
        settings: supplies `source_url` and `max_pages`.
        sleep: passed through to `fetch_page`.

    Returns:
        (records, quarantined, errors). A page-level failure appends
        f"{url}: {message}" to `errors` and stops the walk. It never propagates:
        the records from the pages that did work are still returned.

    Examples:
        pages = {"/a": (200, {"items": [...], "next": "/b"}),
                 "/b": (200, {"items": [...], "next": None})}
        extract_records(pages.__getitem__, settings)  # walks both pages
        # a 500 on the first page -> ([], [], ['/a: fetch failed with status 500'])
    """
    # TODO: your code here
    raise NotImplementedError("M2: extract_records")


# ===========================================================================
# MILESTONE 3 — transform (pipeline/transform.py)
# ===========================================================================
def filter_records(records: Iterable[Record], min_value: float) -> Iterator[Record]:
    """Yield the records whose value is greater than or equal to `min_value`.

    This must be a generator function: it has to work on an endless source and
    must not build a list.

    Args:
        records: the incoming stream.
        min_value: the inclusive floor.

    Returns:
        An iterator over the records that survive.

    Examples:
        list(filter_records([r(5.0), r(15.0)], 10.0)) -> [r(15.0)]
        list(filter_records([r(10.0)], 10.0)) -> [r(10.0)]   # inclusive
        next(filter_records(endless_records(), 0.0))         # returns at once
    """
    # TODO: your code here
    raise NotImplementedError("M3: filter_records")


def enrich_records(records: Iterable[Record]) -> Iterator[Record]:
    """Yield copies of the records with `band` filled in.

    Bands: "low" below 10, "normal" from 10 up to but not including 25, "high" at
    25 and above. `Record` is frozen, so use `dataclasses.replace` — the output is
    a new object, not a mutated input.

    Also a generator function.

    Args:
        records: the incoming stream.

    Returns:
        An iterator of enriched records, in input order.

    Examples:
        [r.band for r in enrich_records([r(9.99), r(10.0), r(24.9), r(25.0)])]
            -> ['low', 'normal', 'normal', 'high']
        source = r(5.0)
        list(enrich_records([source]))[0] is source -> False
        source.band -> ''   # the input is untouched
    """
    # TODO: your code here
    raise NotImplementedError("M3: enrich_records")


def aggregate(records: Iterable[Record]) -> dict[str, Any]:
    """Consume the stream exactly once and summarise it.

    Args:
        records: the enriched stream. It may be a generator, so you get one pass
            over it — accumulate as you go rather than iterating twice.

    Returns:
        {
            "total": int,                        # records seen
            "sensors": {sensor: {"count", "mean", "min", "max"}},
            "bands": {band: count},              # count desc, then band asc
            "regions": {region: count},          # same ordering
            "span": (earliest_iso, latest_iso),  # ("", "") when empty
        }
        `mean` is rounded to 3 decimal places. The ISO strings come from
        `record.taken.isoformat()`. Use `Counter` and `defaultdict` rather than
        `if key not in totals` bookkeeping.

    Examples:
        aggregate([]) -> {'total': 0, 'sensors': {}, 'bands': {}, 'regions': {},
                          'span': ('', '')}
        summary = aggregate([r("s1", 10.0), r("s1", 21.0), r("s2", 5.0)])
        summary["total"] -> 3
        summary["sensors"]["s1"] -> {'count': 2, 'mean': 15.5, 'min': 10.0, 'max': 21.0}
        summary["span"] -> ('2024-03-15T13:00:00+00:00', '2024-03-15T15:00:00+00:00')
    """
    # TODO: your code here
    raise NotImplementedError("M3: aggregate")


def run_transform(
    records: Iterable[Record], min_value: float
) -> tuple[list[Record], dict[str, Any]]:
    """Chain filter -> enrich -> aggregate over a single pass of the input.

    Build the chain lazily, then consume it once. The returned list and the
    summary must both come from that one pass, so a source that can only be read
    once still works.

    Args:
        records: the incoming stream, possibly a generator.
        min_value: the floor passed to `filter_records`.

    Returns:
        (enriched records as a list, the summary dict from `aggregate`).

    Examples:
        kept, summary = run_transform([r(5.0), r(15.0)], 10.0)
        [record.value for record in kept] -> [15.0]
        summary["total"] -> 1
        kept[0].band -> 'normal'
        run_transform(iter([]), 0.0) -> ([], {'total': 0, ...})
    """
    # TODO: your code here
    raise NotImplementedError("M3: run_transform")


# ===========================================================================
# MILESTONE 4 — load (pipeline/load.py)
# ===========================================================================
def connect(db_path: Path | str) -> sqlite3.Connection:
    """Open the database and create the schema if it is missing.

    The schema is in LESSON.md, milestone 4. Copy it exactly: the
    `UNIQUE(sensor, taken)` constraint is what makes re-runs idempotent.

    Args:
        db_path: a path, or ":memory:" for a throwaway database.

    Returns:
        A connection whose `row_factory` is `sqlite3.Row`, so rows support
        `row["sensor"]`. Calling this twice on the same path is safe.

    Examples:
        connection = connect(":memory:")
        connection.row_factory is sqlite3.Row -> True
        count_rows(connect(tmp_path / "a.db")) -> 0
        connect(tmp_path / "a.db") and connect(tmp_path / "a.db")  # no error
    """
    # TODO: your code here
    raise NotImplementedError("M4: connect")


def upsert_records(
    connection: sqlite3.Connection, records: Iterable[Record], batch_size: int = 100
) -> int:
    """Insert or update records in batches, inside transactions.

    Write `record.taken.isoformat()` for the `taken` column. Use `?` placeholders
    and the `ON CONFLICT(sensor, taken) DO UPDATE SET ...` clause from the brief,
    so that writing the same records again updates them in place.

    Args:
        connection: an open connection from `connect`.
        records: the records to write; may be a generator.
        batch_size: how many rows per transaction, at least 1.

    Returns:
        How many records were processed.

    Raises:
        ValueError: if `batch_size` is less than 1.

    Examples:
        upsert_records(connection, [a, b, c], batch_size=2) -> 3
        count_rows(connection) -> 3
        upsert_records(connection, [a, b, c]) -> 3
        count_rows(connection) -> 3          # idempotent, not 6
        upsert_records(connection, []) -> 0
    """
    # TODO: your code here
    raise NotImplementedError("M4: upsert_records")


def count_rows(connection: sqlite3.Connection) -> int:
    """How many readings are stored.

    Args:
        connection: an open connection from `connect`.

    Returns:
        The number of rows in `readings`.

    Examples:
        count_rows(connect(":memory:")) -> 0
        # after upsert_records(connection, [a, b]):
        count_rows(connection) -> 2
    """
    # TODO: your code here
    raise NotImplementedError("M4: count_rows")


def sensor_stats(connection: sqlite3.Connection, sensor: str) -> dict[str, Any] | None:
    """Statistics for one sensor.

    Args:
        connection: an open connection from `connect`.
        sensor: the sensor name to look up, as a bound parameter — hostile input
            must be treated as a name, not as SQL.

    Returns:
        {"sensor", "count", "mean", "min", "max"} with `mean` rounded to 3
        places, or None when the sensor has no rows.

    Examples:
        sensor_stats(connection, "s1")
            -> {'sensor': 's1', 'count': 2, 'mean': 15.5, 'min': 10.0, 'max': 21.0}
        sensor_stats(connection, "nope") -> None
        sensor_stats(connection, "x' OR '1'='1") -> None
    """
    # TODO: your code here
    raise NotImplementedError("M4: sensor_stats")


def top_sensors(connection: sqlite3.Connection, limit: int = 5) -> list[dict[str, Any]]:
    """The busiest sensors, most rows first.

    Args:
        connection: an open connection from `connect`.
        limit: how many to return. Zero or negative returns an empty list.

    Returns:
        A list of {"sensor", "count", "mean"} dicts, highest count first, ties
        broken by sensor name ascending, `mean` rounded to 3 places.

    Examples:
        top_sensors(connection, 2)
            -> [{'sensor': 's1', 'count': 3, 'mean': 21.533},
                {'sensor': 's2', 'count': 1, 'mean': 19.0}]
        top_sensors(connection, 0) -> []
        top_sensors(connect(":memory:")) -> []
    """
    # TODO: your code here
    raise NotImplementedError("M4: top_sensors")


# ===========================================================================
# MILESTONE 5 — report and CLI (pipeline/report.py, pipeline/cli.py)
# ===========================================================================
def format_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Render an aligned plain-text table.

    Rules:
      * every column is padded to the widest cell in that column, header
        included, and columns are joined by exactly two spaces
      * the second line is a rule of hyphens matching each column's width,
        joined the same way
      * a column whose data cells are all numbers (ints or floats, not bools) is
        right-aligned, header included; every other column is left-aligned
      * cells are converted with `str`; floats are not reformatted
      * no line has trailing whitespace, and the result has no trailing newline

    Args:
        headers: the column titles.
        rows: the data rows, each as long as `headers`.

    Returns:
        The table as one string.

    Examples:
        print(format_table(["sensor", "count", "mean"],
                           [["s1", 3, 21.53], ["s2", 1, 19.0]]))
        sensor  count   mean
        ------  -----  -----
        s1          3  21.53
        s2          1   19.0

        format_table(["a", "b"], []) -> 'a  b\\n-  -'
    """
    # TODO: your code here
    raise NotImplementedError("M5: format_table")


def build_parser() -> argparse.ArgumentParser:
    """Build the `sensorpipe` argument parser.

    Program name "sensorpipe", a global `-v/--verbose` flag that works *before*
    the subcommand, and three required subcommands stored in `dest="command"`:

        run     --limit int, default 0 (0 means no limit on records stored)
        report  --limit int, default 5
        stats   --sensor str, required

    Returns:
        The configured parser. Do not parse anything here.

    Examples:
        build_parser().parse_args(["run"]).command -> 'run'
        build_parser().parse_args(["run"]).limit -> 0
        build_parser().parse_args(["-v", "report", "--limit", "3"]).verbose -> True
        build_parser().parse_args(["stats", "--sensor", "s1"]).sensor -> 's1'
        build_parser().parse_args([])          -> SystemExit (no subcommand)
        build_parser().parse_args(["stats"])   -> SystemExit (--sensor required)
    """
    # TODO: your code here
    raise NotImplementedError("M5: build_parser")


def main(
    argv: Sequence[str] | None = None,
    fetch: Fetch | None = None,
    env: Mapping[str, str] | None = None,
) -> int:
    """Run one command and return an exit code. Never call `sys.exit`.

    Steps, in order:
      1. parse `argv` with `build_parser()`
      2. `load_settings(env)`; on `ValueError`, log the message and return 2
      3. configure logging exactly once, here: DEBUG when `--verbose` or
         `settings.verbose`, otherwise INFO
      4. dispatch on `args.command`

    Commands:
        run     extract -> transform -> upsert, then print a summary table.
                Uses the injected `fetch`. Honours `--limit` by storing at most
                that many records (0 means all). Returns 0, or 1 when extraction
                produced errors and nothing was stored. When `fetch` is None it
                may build a real HTTP transport, importing `requests` lazily
                inside that branch so this module imports without it.
        report  print `top_sensors` as a table. Returns 0.
        stats   print one sensor's statistics as a table. Returns 0, or logs an
                error and returns 2 when the sensor is unknown.

    Args:
        argv: the argument list; None means `sys.argv[1:]`.
        fetch: the transport for `run`.
        env: the environment mapping for `load_settings`.

    Returns:
        The process exit code: 0 success, 1 extraction failure, 2 user error.

    Examples:
        main(["run"], fetch=fake_source, env={"SENSORPIPE_DB": "/tmp/x.db"}) -> 0
        main(["run"], fetch=fake_source, env=...) -> 0   # again: same row count
        main(["report", "--limit", "3"], env=...) -> 0
        main(["stats", "--sensor", "nope"], env=...) -> 2
        main(["report"], env={"SENSORPIPE_BATCH_SIZE": "0"}) -> 2
    """
    # TODO: your code here
    raise NotImplementedError("M5: main")


if __name__ == "__main__":
    raise SystemExit(main())
