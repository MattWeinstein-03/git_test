"""Day 21 — the pipeline architecture, demonstrated on a DIFFERENT dataset.

Run me from the course root:

    python course/week3/day21_project_capstone_pipeline/examples.py

This is `birdpipe`: bird sightings, not sensor readings. Different domain,
different fields, different bands — the same five layers your project needs:

    M1 config     environment mapping -> a frozen, validated Settings
    M2 extract    an injected fetch, retries, pagination, quarantine
    M3 transform  generator stages: filter -> enrich -> aggregate
    M4 load       SQLite with a UNIQUE key and an upsert, so re-runs are safe
    M5 report     a pure table formatter plus an argparse CLI returning a code

Read it for the SHAPE, then build `sensorpipe` yourself. Nothing here reaches the
network: the "source" is a dict of pages, which is the entire point of passing
`fetch` in as an argument.

Everything is written into a `tmp/` folder next to this file, deleted on the way
out, so the repository is unchanged when the script finishes.
"""

from __future__ import annotations

import argparse
import itertools
import logging
import shutil
import sqlite3
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).parent
TMP = HERE / "tmp"

logger = logging.getLogger("birdpipe")

# A transport is any callable url -> (status, payload). That is all the pipeline
# is allowed to know about the outside world.
Fetch = Callable[[str], "tuple[int, Mapping[str, Any]]"]


# ===========================================================================
# M1 — configuration: one boundary, validated once
# ===========================================================================
DEFAULTS = {"URL": "https://birds.invalid/v1/sightings", "DB": "birdpipe.db", "MIN_COUNT": "1"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated configuration. Frozen: nothing may change it mid-run."""

    source_url: str
    db_path: Path
    min_count: int


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build Settings from a mapping. `None` would mean os.environ in real code.

    The mapping is a parameter, so this whole function is testable with a dict —
    no monkeypatching, no process-wide state, no surprises.
    """
    source = {} if env is None else env

    def raw(name: str) -> str:
        return source.get("BIRDPIPE_" + name, DEFAULTS[name])

    url = raw("URL")
    if not url.startswith(("http://", "https://")):
        # The message names the variable AND the value. That is what somebody
        # reads when a deployment fails, instead of your source code.
        raise ValueError(f"BIRDPIPE_URL={url!r} is invalid: expected http:// or https://")

    text = raw("MIN_COUNT")
    try:
        min_count = int(text)
    except ValueError as error:
        raise ValueError(f"BIRDPIPE_MIN_COUNT={text!r} is invalid: expected an integer") from error
    if min_count < 0:
        raise ValueError(f"BIRDPIPE_MIN_COUNT={text!r} is invalid: expected 0 or more")

    return Settings(source_url=url, db_path=Path(raw("DB")), min_count=min_count)


# ===========================================================================
# M2 — extract: unreliable source in, typed objects out, nothing crashes
# ===========================================================================
RETRYABLE = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True, slots=True)
class Sighting:
    """One validated sighting. `size` is filled in by the transform stage."""

    species: str
    count: int
    seen: datetime  # always timezone-aware, always UTC
    site: str
    size: str = ""


def parse_when(text: str) -> datetime:
    """Parse an ISO-8601 timestamp into an aware UTC datetime."""
    # "Z" is not accepted by fromisoformat before 3.11, so normalise it first.
    parsed = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)  # relabel a naive stamp as UTC
    return parsed.astimezone(timezone.utc)  # shift an offset stamp to UTC


def normalise_sighting(raw: Mapping[str, Any]) -> Sighting:
    """Turn one raw item into a Sighting, or raise ValueError explaining why not."""
    species = raw.get("species")
    if not isinstance(species, str) or not species.strip():
        raise ValueError(f"missing species in {dict(raw)!r}")
    try:
        count = int(raw["count"])  # accepts 3 and "3", rejects "many" and None
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"unusable count in {dict(raw)!r}") from error
    if count <= 0:
        raise ValueError(f"count must be positive in {dict(raw)!r}")
    when = raw.get("seen")
    if not isinstance(when, str):
        raise ValueError(f"missing seen in {dict(raw)!r}")
    try:
        seen = parse_when(when)
    except ValueError as error:
        raise ValueError(f"unusable timestamp {when!r}") from error
    site = raw.get("site")
    site_text = site.strip().lower() if isinstance(site, str) and site.strip() else "unknown"
    return Sighting(species=species.strip().lower(), count=count, seen=seen, site=site_text)


def normalise_all(raws: Iterable[Mapping[str, Any]]) -> tuple[list[Sighting], list[dict]]:
    """Normalise many items. Returns (good, quarantined) and never raises."""
    good: list[Sighting] = []
    quarantined: list[dict] = []
    for raw in raws:
        try:
            good.append(normalise_sighting(raw))
        except (ValueError, TypeError, AttributeError) as error:
            # One bad row must never end the run. Count it, log it, carry on.
            logger.debug("quarantined: %s", error)
            quarantined.append(dict(raw) if isinstance(raw, Mapping) else {"raw": raw})
    return good, quarantined


def fetch_page(
    fetch: Fetch, url: str, max_attempts: int = 3, sleep: Callable[[float], None] = lambda _: None
) -> Mapping[str, Any]:
    """Fetch one page, retrying transient statuses. `sleep` is injected."""
    status = -1
    for attempt in range(1, max_attempts + 1):
        status, payload = fetch(url)
        if 200 <= status < 300:
            return payload
        if status not in RETRYABLE or attempt == max_attempts:
            break  # a 404 will not fix itself; neither will attempt 4 of 3
        delay = 0.5 * 2 ** (attempt - 1)  # exponential backoff: 0.5, 1.0, 2.0...
        logger.warning("HTTP %s from %s, retrying in %.1fs", status, url, delay)
        sleep(delay)
    raise RuntimeError(f"fetch failed with status {status}")


def extract(fetch: Fetch, settings: Settings, max_pages: int = 5):
    """Walk the paginated source. Returns (sightings, quarantined, errors)."""
    sightings: list[Sighting] = []
    quarantined: list[dict] = []
    errors: list[str] = []
    url: str | None = settings.source_url
    pages = 0
    while url and pages < max_pages:
        try:
            payload = fetch_page(fetch, url)
        except RuntimeError as error:
            # Report, do not propagate: the caller wants a summary, not a crash.
            errors.append(f"{url}: {error}")
            break
        pages += 1
        good, bad = normalise_all(payload.get("items") or [])
        sightings.extend(good)
        quarantined.extend(bad)
        url = payload.get("next")
    logger.info("extracted %d sighting(s) from %d page(s)", len(sightings), pages)
    return sightings, quarantined, errors


# ===========================================================================
# M3 — transform: generators, so memory does not grow with the input
# ===========================================================================
def filter_sightings(sightings: Iterable[Sighting], min_count: int) -> Iterator[Sighting]:
    """Yield the sightings of at least `min_count` birds. A generator: no list()."""
    for sighting in sightings:
        if sighting.count >= min_count:
            yield sighting


def enrich_sightings(sightings: Iterable[Sighting]) -> Iterator[Sighting]:
    """Yield copies with `size` filled in. Sighting is frozen, so replace() it."""
    for sighting in sightings:
        if sighting.count == 1:
            size = "single"
        elif sighting.count < 10:
            size = "few"
        else:
            size = "flock"
        yield replace(sighting, size=size)


def aggregate(sightings: Iterable[Sighting]) -> dict[str, Any]:
    """Consume the stream ONCE and return a fixed-size summary of it."""
    total = 0
    birds = 0
    per_species_sum: defaultdict[str, int] = defaultdict(int)
    per_species_rows: Counter[str] = Counter()
    sizes: Counter[str] = Counter()
    earliest: datetime | None = None
    latest: datetime | None = None
    for sighting in sightings:
        # Everything is accumulated here. A second `for sighting in sightings`
        # would find the generator exhausted and report zeros.
        total += 1
        birds += sighting.count
        per_species_sum[sighting.species] += sighting.count
        per_species_rows[sighting.species] += 1
        sizes[sighting.size] += 1
        if earliest is None or sighting.seen < earliest:
            earliest = sighting.seen
        if latest is None or sighting.seen > latest:
            latest = sighting.seen
    species = {
        name: {"rows": per_species_rows[name], "birds": per_species_sum[name]}
        for name in sorted(per_species_rows)
    }
    return {
        "total": total,
        "birds": birds,
        "species": species,
        # Sorted by count descending, then name ascending, so output never depends
        # on the order rows happened to arrive in.
        "sizes": dict(sorted(sizes.items(), key=lambda pair: (-pair[1], pair[0]))),
        "span": ("", "") if earliest is None else (earliest.isoformat(), latest.isoformat()),
    }


def run_transform(sightings: Iterable[Sighting], min_count: int):
    """Chain the stages lazily and consume the input exactly once."""
    kept: list[Sighting] = []

    def tap(stream: Iterable[Sighting]) -> Iterator[Sighting]:
        # The caller wants the records AND a summary, but the stream can only be
        # read once. Collecting as they pass costs one pass, not two.
        for sighting in stream:
            kept.append(sighting)
            yield sighting

    summary = aggregate(tap(enrich_sightings(filter_sightings(sightings, min_count))))
    return kept, summary


# ===========================================================================
# M4 — load: a UNIQUE key plus an upsert is the whole of idempotence
# ===========================================================================
SCHEMA = """
CREATE TABLE IF NOT EXISTS sightings (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    species TEXT    NOT NULL,
    count   INTEGER NOT NULL,
    seen    TEXT    NOT NULL,
    site    TEXT    NOT NULL,
    size    TEXT    NOT NULL,
    UNIQUE(species, seen)
)
"""

UPSERT = """
INSERT INTO sightings (species, count, seen, site, size) VALUES (?, ?, ?, ?, ?)
ON CONFLICT(species, seen) DO UPDATE SET
    count = excluded.count, site = excluded.site, size = excluded.size
"""


def connect(db_path: Path | str) -> sqlite3.Connection:
    """Open the database and create the schema if it is missing. Safe to repeat."""
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row  # rows support row["species"]
    with connection:
        connection.execute(SCHEMA)
    return connection


def upsert(connection: sqlite3.Connection, sightings: Iterable[Sighting], batch_size: int = 50) -> int:
    """Write in batched transactions, with ? placeholders. Returns rows processed."""
    stream = iter(sightings)
    written = 0
    while True:
        batch = list(itertools.islice(stream, batch_size))
        if not batch:
            return written
        rows = [(s.species, s.count, s.seen.isoformat(), s.site, s.size) for s in batch]
        with connection:  # one transaction per batch, not per row
            connection.executemany(UPSERT, rows)
        written += len(rows)


def count_rows(connection: sqlite3.Connection) -> int:
    """How many sightings are stored."""
    return int(connection.execute("SELECT count(*) FROM sightings").fetchone()[0])


def top_species(connection: sqlite3.Connection, limit: int = 3) -> list[dict[str, Any]]:
    """The most-recorded species, most rows first, ties broken by name."""
    rows = connection.execute(
        """
        SELECT species, count(*) AS rows, sum(count) AS birds
        FROM sightings GROUP BY species ORDER BY rows DESC, species ASC LIMIT ?
        """,
        (limit,),  # the value travels beside the SQL, never inside it
    ).fetchall()
    return [{"species": r["species"], "rows": r["rows"], "birds": r["birds"]} for r in rows]


def species_rows(connection: sqlite3.Connection, species: str) -> list[dict[str, Any]]:
    """Every row for one species. A ? placeholder makes injection impossible."""
    rows = connection.execute(
        "SELECT species, count, seen, site FROM sightings WHERE species = ? ORDER BY seen",
        (species,),
    ).fetchall()
    return [dict(row) for row in rows]


# ===========================================================================
# M5 — report and CLI: the only layer that prints
# ===========================================================================
def simple_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """A deliberately simple formatter: everything left-aligned, three spaces.

    Your `format_table` has stricter rules (numeric columns right-aligned, a
    dashed rule, two spaces, no trailing whitespace). Read them in LESSON.md and
    write your own — this one is here to show WHERE the formatter goes, not what
    it should do.
    """
    widths = [len(str(header)) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(str(cell)))
    lines = ["   ".join(str(h).ljust(w) for h, w in zip(headers, widths)).rstrip()]
    for row in rows:
        lines.append("   ".join(str(c).ljust(w) for c, w in zip(row, widths)).rstrip())
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Three subcommands, a global flag, and `dest="command"` to dispatch on."""
    parser = argparse.ArgumentParser(prog="birdpipe", description="Bird sighting pipeline.")
    parser.add_argument("-v", "--verbose", action="store_true")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("run", help="fetch, transform and store sightings")
    report = subcommands.add_parser("report", help="show the most-recorded species")
    report.add_argument("--limit", type=int, default=3)
    show = subcommands.add_parser("show", help="every row for one species")
    show.add_argument("--species", required=True)
    return parser


def main(argv: Sequence[str] | None = None, fetch: Fetch | None = None, env=None) -> int:
    """Run one command and RETURN an exit code. No sys.exit, so tests can call it."""
    args = build_parser().parse_args(argv)
    try:
        settings = load_settings(env)
    except ValueError as error:
        logger.error("configuration error: %s", error)
        return 2  # a user error, not a bug: no traceback

    connection = connect(settings.db_path)
    try:
        if args.command == "run":
            if fetch is None:
                logger.error("run needs a source")
                return 2
            sightings, quarantined, errors = extract(fetch, settings)
            kept, summary = run_transform(sightings, settings.min_count)
            written = upsert(connection, kept)
            if errors and written == 0:
                return 1
            print(
                simple_table(
                    ["metric", "value"],
                    [
                        ["fetched", summary["total"]],
                        ["birds", summary["birds"]],
                        ["written", written],
                        ["stored", count_rows(connection)],
                        ["quarantined", len(quarantined)],
                    ],
                )
            )
            return 0
        if args.command == "report":
            leaders = top_species(connection, args.limit)
            print(
                simple_table(
                    ["species", "rows", "birds"],
                    [[item["species"], item["rows"], item["birds"]] for item in leaders],
                )
            )
            return 0
        rows = species_rows(connection, args.species)
        if not rows:
            logger.error("unknown species: %s", args.species)
            return 2
        print(simple_table(["species", "count", "seen", "site"], [list(r.values()) for r in rows]))
        return 0
    finally:
        connection.close()


# ===========================================================================
# The demo itself
# ===========================================================================
PAGE_TWO = "https://birds.invalid/v1/sightings?cursor=p2"

PAGES: dict[str, tuple[int, dict]] = {
    "https://birds.invalid/v1/sightings": (
        200,
        {
            "items": [
                {"species": "Robin", "count": "3", "seen": "2024-05-01T06:30:00Z", "site": "Hide A"},
                {"species": "swift", "count": 24, "seen": "2024-05-01T07:00:00+01:00"},
                {"species": "", "count": 2, "seen": "2024-05-01T07:10:00Z"},  # no species
                {"species": "wren", "count": "many", "seen": "2024-05-01T07:20:00Z"},  # bad count
            ],
            "next": PAGE_TWO,
        },
    ),
    PAGE_TWO: (
        200,
        {
            "items": [
                {"species": "robin", "count": 1, "seen": "2024-05-02T06:30:00Z", "site": "hide a"},
                {"species": "heron", "count": 1, "seen": "2024-05-02T06:45:00Z", "site": "Lake"},
                {"species": "robin", "count": 12, "seen": "2024-05-03T06:30:00Z", "site": "Lake"},
                {"species": "swift", "count": 8, "seen": "bad timestamp"},  # unusable
            ],
            "next": None,
        },
    ),
}


def flaky_source(fail_times: int) -> Fetch:
    """A source that returns 503 the first `fail_times` calls, then works."""
    state = {"failures": 0}

    def fetch(url: str) -> tuple[int, Mapping[str, Any]]:
        if state["failures"] < fail_times:
            state["failures"] += 1
            return 503, {}
        return PAGES[url]

    return fetch


def source(url: str) -> tuple[int, Mapping[str, Any]]:
    """The whole "network" for this demo: a dict lookup."""
    return PAGES.get(url, (404, {}))


def endless_sightings() -> Iterator[Sighting]:
    """An infinite stream, to prove the transform stages are lazy."""
    for number in itertools.count(1):
        yield Sighting("robin", number, datetime(2024, 5, 1, tzinfo=timezone.utc), "hide a")


def rule(title: str) -> None:
    print()
    print("=" * 74)
    print(title)
    print("=" * 74)


def demo() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    env = {"BIRDPIPE_DB": str(TMP / "birdpipe.db"), "BIRDPIPE_MIN_COUNT": "1"}

    rule("1. Config: one boundary, validated once, injected as a mapping")
    settings = load_settings(env)
    print("load_settings(env) ->", settings)
    print("defaults apply when a variable is absent ->", load_settings({}).source_url)
    for bad in ({"BIRDPIPE_URL": "ftp://birds"}, {"BIRDPIPE_MIN_COUNT": "lots"}):
        try:
            load_settings(bad)
        except ValueError as error:
            print("rejected ->", error)
    print()
    print("Settings is frozen, so nothing can retune the app mid-run:")
    try:
        settings.min_count = 99
    except Exception as error:
        print("  settings.min_count = 99 ->", type(error).__name__)

    rule("2. Extract: injected transport, retries, pagination, quarantine")
    print("The 'network' is a dict of pages. fetch(url) -> (status, payload).")
    waited: list[float] = []
    payload = fetch_page(flaky_source(2), settings.source_url, sleep=waited.append)
    print("two 503s then a 200 -> got", len(payload["items"]), "items after waiting", waited)
    try:
        fetch_page(lambda url: (404, {}), "/gone")
    except RuntimeError as error:
        print("a 404 is not retried ->", error)

    sightings, quarantined, errors = extract(source, settings)
    print()
    print("extract() over both pages:")
    print("  usable      ->", len(sightings))
    print("  quarantined ->", len(quarantined))
    for item in quarantined:
        print("     ", item)
    print("  errors      ->", errors)
    print("normalised   ->", sightings[0])
    print("  'Robin' and 'swift' both arrive lowercased; '3' arrives as an int;")
    print("  07:00+01:00 became", sightings[1].seen.isoformat(), "- stored UTC, always.")

    rule("3. Transform: generator stages, and laziness you can prove")
    lazy = filter_sightings(endless_sightings(), 5)
    print("filter over an ENDLESS source, first three:")
    for sighting in itertools.islice(lazy, 3):
        print("   ", sighting.species, sighting.count)
    print("  that returns instantly: no stage may call list() on its input.")
    print()
    kept, summary = run_transform(sightings, settings.min_count)
    print("run_transform ->", len(kept), "records and one summary, from ONE pass")
    print("  sizes  ->", summary["sizes"], "(count desc, then name asc)")
    print("  species->", summary["species"])
    print("  span   ->", summary["span"])
    print("  bands are new objects; the inputs still have size='':",
          sightings[0].size == "" and kept[0].size != "")

    rule("4. Load: UNIQUE + upsert, therefore idempotent")
    connection = connect(settings.db_path)
    try:
        print("first  upsert ->", upsert(connection, kept), "processed,", count_rows(connection), "rows stored")
        print("second upsert ->", upsert(connection, kept), "processed,", count_rows(connection), "rows stored")
        print("  the row count did not move. UNIQUE(species, seen) plus")
        print("  ON CONFLICT DO UPDATE is the entire trick.")
        changed = replace(kept[0], count=99, size="flock")
        upsert(connection, [changed])
        stored = species_rows(connection, changed.species)[0]
        print("re-writing one row with count=99 UPDATED it in place ->", stored["count"])
        print("stored timestamps are ISO UTC strings, so they sort correctly:")
        for row in species_rows(connection, "robin"):
            print("   ", row["seen"], row["site"])
    finally:
        connection.close()

    rule("5. Report and CLI: the only layer that prints")
    print("main() takes argv, fetch and env as ARGUMENTS and returns an int.")
    print()
    print("$ birdpipe run")
    code = main(["run"], fetch=source, env=env)
    print("exit code ->", code)
    print()
    print("$ birdpipe run   (again — nothing new is stored)")
    code = main(["run"], fetch=source, env=env)
    print("exit code ->", code)
    print()
    print("$ birdpipe report --limit 2")
    main(["report", "--limit", "2"], env=env)
    print()
    print("$ birdpipe show --species heron")
    main(["show", "--species", "heron"], env=env)
    print()
    print("$ birdpipe show --species pelican")
    print("exit code ->", main(["show", "--species", "pelican"], env=env), "(unknown: 2, not a crash)")
    print("$ BIRDPIPE_MIN_COUNT=lots birdpipe report")
    print("exit code ->", main(["report"], env={"BIRDPIPE_MIN_COUNT": "lots"}), "(config error: 2)")

    rule("6. What this bought you")
    print("Nothing above touched a network, a clock, or a real database:")
    print("  fetch  is an argument -> the source is a dict in this file")
    print("  env    is an argument -> configuration is a dict in this file")
    print("  db     is a path      -> it lives in tmp/ and is deleted on exit")
    print("  main   returns a code -> a test asserts on the number")
    print()
    print("That is why the graded tests for sensorpipe run offline in under a")
    print("second, and why yours will too. Now build it: LESSON.md, milestone 1.")


if __name__ == "__main__":
    # INFO to stderr, configured exactly once, in the entry point — never in a
    # module, which is a rule you will see enforced by the graded tests.
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(name)s: %(message)s")
    try:
        demo()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
        print()
        print("tmp/ removed — the repository is unchanged.")
