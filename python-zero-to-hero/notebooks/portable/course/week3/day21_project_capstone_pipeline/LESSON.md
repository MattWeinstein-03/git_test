# Day 21 — Project 3: A Complete Data Pipeline

> **Time:** ~5 hours  |  **Prerequisites:** Days 1–20

## What you'll be able to do after today
- Build a configurable ETL application end to end: config, extract, transform, load, report.
- Inject the network as a parameter so the whole pipeline is testable offline.
- Stream records through generator stages that never hold the dataset in memory.
- Persist to SQLite with parameterised upserts so re-running changes nothing.
- Ship a real CLI with subcommands, formatted output and structured logging.
- Lay a project out as a package, with your own tests and a README a stranger can follow.

## Why this matters

This is the graduation piece. Everything you have learned appears here, and — more
importantly — appears *together*, which is the part no single exercise teaches.

The shape you are building is the most common serious Python job there is. "Pull
data from somewhere, clean it, aggregate it, store it, report on it, run it on a
schedule" describes data engineering, analytics tooling, integration work,
monitoring, billing reconciliation, and most internal tools. Interviewers ask for
it because it exposes everything: error handling, idempotence, testability,
configuration, logging, and whether you can structure code that other people will
maintain.

When you finish, you have a portfolio project you can explain line by line. That is
worth more than ten tutorials.

---

## The brief

Build `sensorpipe`: a command-line ETL and reporting tool for sensor readings.

It fetches paginated JSON from an HTTP source (injected, so tests never touch the
network), normalises raw records into typed objects, quarantines bad ones instead
of crashing, streams the good ones through filter/enrich/aggregate stages,
persists them to SQLite idempotently, and prints reports through an `argparse` CLI
with three subcommands.

### User stories

1. As an operator, I run `sensorpipe run` and the tool loads its configuration
   from environment variables, fetches every page, tells me how many records it
   stored and how many it rejected, and exits 0.
2. As an operator, I run it again and the database does not change, because a
   re-run must be safe.
3. As an analyst, I run `sensorpipe report --limit 5` and see an aligned table of
   the busiest sensors.
4. As an analyst, I run `sensorpipe stats --sensor s1` and see the count, mean,
   minimum and maximum for one sensor.
5. As an on-call engineer, I run any command with `--verbose` and see DEBUG
   logging that tells me which URL was fetched, how many records were quarantined
   and why.
6. As a developer, I run the test suite offline, on a plane, with no credentials,
   and it passes in under two seconds.

### The data

Each page of the source looks like this:

```json
{
  "items": [
    {"sensor": "s1", "value": "21.5", "taken": "2024-03-15T13:00:00Z", "region": "eu"},
    {"sensor": "s2", "value": 19.0,   "taken": "2024-03-15T13:00:00+01:00", "region": "US"},
    {"sensor": "",   "value": 5.0,    "taken": "2024-03-15T13:00:00Z"},
    {"sensor": "s4", "value": "abc",  "taken": "2024-03-15T13:00:00Z", "region": "eu"}
  ],
  "next": "/v1/readings?cursor=abc"
}
```

Real data is like this: values arrive as strings, time zones vary, fields go
missing, and some rows are simply wrong. The last two items above must be
quarantined, not crash the run.

---

## Architecture

```
                 environment variables
                          |
                    [ M1 config ]  Settings (frozen dataclass, validated)
                          |
   fetch(url) ---> [ M2 extract ]  retries + backoff + pagination
   (injected)              |       raw dicts -> Record objects
                          |       bad rows -> quarantine list
                          v
                   [ M3 transform ]  generators: filter -> enrich -> aggregate
                          |
                          v
                    [ M4 load ]     SQLite: schema + parameterised upsert
                          |                 (idempotent re-runs)
                          v
                 [ M5 report + CLI ]  argparse subcommands, tables, logging
```

Every arrow carries plain data. Only the `fetch` box knows what HTTP is, and it
arrives as a function argument — which is why `python -m pytest` needs no network,
no credentials and no mocking library.

### Required layout

Build a package inside this day's folder and re-export the graded names from
`exercises.py`:

```
day21_project_capstone_pipeline/
    LESSON.md            this brief
    README.md            how to install, run, and reason about the app
    examples.py          a runnable end-to-end demo (already written for you)
    exercises.py         THE GRADED API SURFACE - stubs you fill in
    solutions.py         the reference implementation (read it last)
    test_exercises.py    the grader: test_m1_... through test_m5_...
    my_tests.py          YOUR OWN tests - required, not graded
    pipeline/            your package
        __init__.py
        config.py        M1
        extract.py       M2
        transform.py     M3
        load.py          M4
        report.py        M5
        cli.py           M5
    pipeline_ref/        the reference package solutions.py is built from
```

You may write everything directly in `exercises.py` and it will still pass. Do not:
the point of the milestone split is that each layer is separately understandable,
and a 600-line module is how you learn that the hard way. Put the real code in
`pipeline/` and let `exercises.py` be a thin re-export:

```python
# exercises.py
from pipeline.config import Settings, load_settings
from pipeline.extract import extract_records, normalise_all, normalise_record
...
```

`pipeline_ref/` is the reference package: the same layout, fully implemented. Look
at its structure whenever you like; read its code only after your own attempt.

---

## M1 — Configuration (`pipeline/config.py`)

**Goal:** every knob comes from the environment, with defaults, validated once, at
startup.

Graded API:

```python
@dataclass(frozen=True, slots=True)
class Settings:
    source_url: str
    db_path: Path
    batch_size: int
    max_pages: int
    min_value: float
    verbose: bool


def load_settings(env: Mapping[str, str] | None = None) -> Settings: ...
```

Rules:

| Variable | Type | Default | Validation |
|---|---|---|---|
| `SENSORPIPE_URL` | str | `https://example.invalid/v1/readings` | must start with `http://` or `https://` |
| `SENSORPIPE_DB` | Path | `sensorpipe.db` | any path |
| `SENSORPIPE_BATCH_SIZE` | int | `100` | 1 – 10000 |
| `SENSORPIPE_MAX_PAGES` | int | `10` | at least 1 |
| `SENSORPIPE_MIN_VALUE` | float | `0.0` | any float |
| `SENSORPIPE_VERBOSE` | bool | `False` | `1/true/yes/on` are True, `0/false/no/off` are False |

- `env=None` means read `os.environ`. Taking the mapping as a parameter is what
  makes this testable without patching anything — the same injection idea as
  `fetch`.
- Every invalid value raises `ValueError` whose message contains **the variable
  name and the offending value**. That message is what someone reads at 3 a.m.
  while looking at a deployment, not at your source.
- Do not read the environment anywhere else in the project. One boundary.

**Hint:** write one small helper per type (`_int_setting`, `_float_setting`,
`_bool_setting`) so the validation lives in one place. Day 18's `get_setting` is
the seed of it.

---

## M2 — Extract (`pipeline/extract.py`)

**Goal:** get raw records from an unreliable source, and turn them into typed
objects without ever crashing on bad data.

Graded API:

```python
@dataclass(frozen=True, slots=True)
class Record:
    sensor: str
    value: float
    taken: datetime          # timezone-aware, UTC
    region: str              # lowercase; "unknown" when absent
    band: str = ""           # filled in by M3


def normalise_record(raw: Mapping[str, Any]) -> Record: ...
def normalise_all(raws: Iterable[Mapping[str, Any]]) -> tuple[list[Record], list[dict]]: ...
def fetch_page(fetch, url, max_attempts=3, base_delay=0.0, sleep=time.sleep) -> Mapping: ...
def extract_records(fetch, settings, sleep=time.sleep) -> tuple[list[Record], list[dict], list[str]]: ...
```

Rules:

- `normalise_record` raises `ValueError` when: `sensor` is missing, not a string,
  or empty after stripping; `value` is missing or not convertible with `float`;
  `taken` is missing or not an ISO-8601 timestamp. It normalises: `sensor` is
  stripped, `region` is lowercased and defaults to `"unknown"`, and `taken`
  becomes an aware UTC `datetime` (a `Z` suffix and offsets both work; naive input
  is treated as UTC).
- `normalise_all` calls it per record and returns `(records, quarantined)` — never
  raises. Quarantined items are the original dicts, unchanged, in order.
- `fetch_page` wraps `fetch(url)`, which returns `(status, payload)`. It retries
  429 and 5xx up to `max_attempts` with exponential backoff via the injected
  `sleep`, returns the payload on 2xx, and raises `RuntimeError` mentioning the
  status otherwise. This is Day 19's exercise, reused deliberately.
- `extract_records` walks pages from `settings.source_url`, at most
  `settings.max_pages` fetches, normalising as it goes, and returns
  `(records, quarantined, errors)`. A page-level failure appends
  `f"{url}: {message}"` to `errors` and stops the walk — it never propagates.

**Hint:** `taken` is the field that will bite you. Write
`_parse_timestamp(text) -> datetime` first, port Day 17's version, and test it on
all three shapes before wiring anything up.

---

## M3 — Transform (`pipeline/transform.py`)

**Goal:** a streaming pipeline. Nothing here may materialise the dataset; the
stages are generators, and only the aggregate at the end holds a fixed-size
summary.

Graded API:

```python
def filter_records(records: Iterable[Record], min_value: float) -> Iterator[Record]: ...
def enrich_records(records: Iterable[Record]) -> Iterator[Record]: ...
def aggregate(records: Iterable[Record]) -> dict[str, Any]: ...
def run_transform(records: Iterable[Record], min_value: float) -> tuple[list[Record], dict]: ...
```

Rules:

- `filter_records` keeps records whose `value` is **greater than or equal to**
  `min_value`. It must be a generator function.
- `enrich_records` yields records with `band` filled in: `"low"` below 10,
  `"normal"` from 10 up to but not including 25, `"high"` at 25 and above. Use
  `dataclasses.replace`, because `Record` is frozen — this is a new object, not a
  mutation. Also a generator function.
- `aggregate` consumes the stream **once** and returns:
  ```python
  {
      "total": int,                       # records seen
      "sensors": {sensor: {"count": int, "mean": float, "min": float, "max": float}},
      "bands": {band: count},             # ordered by count desc, then band asc
      "regions": {region: count},         # same ordering
      "span": (earliest_iso, latest_iso), # ("", "") when empty
  }
  ```
  `mean` is rounded to 3 decimal places. Use `Counter` and `defaultdict`
  idiomatically — no manual `if key not in dict` bookkeeping.
- `run_transform` chains them: filter, then enrich, then aggregate, returning the
  enriched records as a list plus the summary. It must build the chain lazily and
  consume the input exactly once (`aggregate` and the returned list come from the
  same single pass).

**Hint:** `aggregate` cannot iterate twice, so accumulate as you go: sum and count
per sensor, then divide at the end. `itertools.tee` is a trap here — it buffers.

---

## M4 — Load (`pipeline/load.py`)

**Goal:** persistence that is safe to re-run.

Graded API:

```python
def connect(db_path: Path | str) -> sqlite3.Connection: ...
def upsert_records(connection, records: Iterable[Record], batch_size: int = 100) -> int: ...
def count_rows(connection) -> int: ...
def sensor_stats(connection, sensor: str) -> dict[str, Any] | None: ...
def top_sensors(connection, limit: int = 5) -> list[dict[str, Any]]: ...
```

Rules:

- `connect` returns a connection with `row_factory = sqlite3.Row` and the schema
  created if missing:
  ```sql
  CREATE TABLE IF NOT EXISTS readings (
      id     INTEGER PRIMARY KEY AUTOINCREMENT,
      sensor TEXT NOT NULL,
      value  REAL NOT NULL,
      taken  TEXT NOT NULL,     -- ISO-8601, UTC
      region TEXT NOT NULL,
      band   TEXT NOT NULL,
      UNIQUE(sensor, taken)
  );
  ```
  Calling it twice is safe. `":memory:"` must work as a path.
- `upsert_records` writes in batches of `batch_size` inside transactions, using
  `?` placeholders, with
  `ON CONFLICT(sensor, taken) DO UPDATE SET value = excluded.value, region = excluded.region, band = excluded.band`.
  It returns the number of records processed. Re-running the same records must
  leave the row count unchanged.
- `sensor_stats` returns `{"sensor", "count", "mean", "min", "max"}` for one
  sensor (mean rounded to 3 places) or `None` when the sensor is unknown. It must
  use a bound parameter: hostile input like `"x' OR '1'='1"` returns `None`.
- `top_sensors` returns the sensors with the most rows, highest first, ties broken
  by sensor name ascending, as dicts with `{"sensor", "count", "mean"}`.

**Hint:** `taken` goes in as `record.taken.isoformat()` so ordering and equality
are string-comparable and the UNIQUE key is stable. Store UTC, always.

---

## M5 — Report and CLI (`pipeline/report.py`, `pipeline/cli.py`)

**Goal:** something a human can actually run.

Graded API:

```python
def format_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str: ...
def build_parser() -> argparse.ArgumentParser: ...
def main(argv: Sequence[str] | None = None, fetch=None, env=None) -> int: ...
```

`format_table` rules:

- Every column is padded to the widest cell in that column (header included),
  joined by two spaces, with no trailing spaces on any line.
- A column whose data cells are all numbers (ints or floats, but not bools) is
  right-aligned, header included; every other column is left-aligned. That is why
  `count` and `mean` line up on their digits below and `sensor` does not.
- Row two is a dashed rule: hyphens matching each column's width, joined the same
  way.
- Values are converted with `str`; floats are not reformatted.
- No rows produces the header plus the rule and nothing else.
- The result has no trailing newline.

```
sensor  count   mean
------  -----  -----
s1          3  21.53
s2          1   19.0
```

`build_parser` rules — three subcommands, `dest="command"`, required:

| Command | Options |
|---|---|
| `run` | `--limit` int (default 0, meaning no limit on records stored) |
| `report` | `--limit` int (default 5) |
| `stats` | `--sensor` str, required |

Plus a global `-v/--verbose` flag that works before the subcommand. Program name
`sensorpipe`.

`main` rules:

- Signature `main(argv=None, fetch=None, env=None) -> int`: an exit code, never
  `sys.exit`.
- Loads settings via `load_settings(env)`. Configures logging **once**, here and
  nowhere else: DEBUG when `--verbose` or `settings.verbose`, otherwise INFO.
- `run`: requires `fetch`; extracts, transforms, upserts, prints a summary table
  and logs progress. Returns 0 on success, 1 if extraction produced errors and
  stored nothing.
- `report`: prints `top_sensors` as a table. Returns 0.
- `stats`: prints one sensor's statistics as a table, or logs an error and returns
  2 when the sensor is unknown.
- On a configuration error (`ValueError` from `load_settings`), log the message and
  return 2. A stack trace is not a user interface.
- When `fetch is None` and the command is `run`, `main` may build a real HTTP
  fetcher — but it must import `requests` lazily, inside that branch, so the
  module imports fine without it and the tests never reach that code.

**Hint:** keep `main` short. It should read like the brief: load settings,
dispatch, print. Every non-trivial line belongs in one of the earlier modules.

---

## Your own tests (required)

Write `my_tests.py` in this folder with **at least eight** of your own tests, run
with:

```bash
python -m pytest course/week3/day21_project_capstone_pipeline/my_tests.py -v
```

Cover at least:

1. A `parametrize`d test over several bad `SENSORPIPE_*` values, asserting
   `ValueError` and that the message names the variable.
2. A `tmp_path` test that runs the whole pipeline against a fake fetch and asserts
   the row count.
3. An idempotence test: run it twice, assert the row count is unchanged.
4. A `capsys` test on `format_table` alignment.
5. A test that a quarantined record does not stop the run.
6. A test that `sensor_stats` is injection-proof.
7. A test that `filter_records` is lazy (works on an endless generator).
8. One test for a bug you actually hit while building this. Write it before you
   fix the bug.

Nothing grades `my_tests.py`. Write it anyway: writing tests nobody asked for is
the skill, and by Day 21 you have the tools.

---

## How to know you're done

- [ ] `PZH_SOLUTIONS=1 python -m pytest course/week3/day21_project_capstone_pipeline -q` is green (that grades the reference).
- [ ] `python check.py day21` is green against your own `exercises.py`.
- [ ] `python course/week3/day21_project_capstone_pipeline/examples.py` exits 0 with no network.
- [ ] `python -m pytest course/week3/day21_project_capstone_pipeline -q` twice in a row gives the same result — no order dependence, no flakiness.
- [ ] Your real code lives in `pipeline/`, split by milestone; `exercises.py` is a re-export.
- [ ] `my_tests.py` has at least eight tests of your own and they pass.
- [ ] `README.md` explains install, configuration, all three commands, and the architecture, and a stranger could follow it.
- [ ] Nothing in `pipeline/` reads `os.environ` except `config.py`.
- [ ] Nothing outside the `run` branch of `main` mentions `requests`.
- [ ] Every SQL statement uses `?` placeholders. Search for `f"SELECT` and find nothing.
- [ ] Running `run` twice does not change the row count.
- [ ] `ruff check` and `black --check` are clean, if you installed them.

---

## Stretch goals

Ordered by value, not difficulty. Do them after the checklist is complete.

1. **`--dry-run`** on `run`: do everything except the upsert, and report what
   would have been written. Two lines of code, and the first thing an operator asks
   for.
2. **A quarantine file.** Write rejected records as JSON Lines to
   `settings.db_path.with_suffix(".quarantine.jsonl")` so bad data is inspectable
   instead of counted. Real pipelines live or die on this.
3. **Incremental extraction.** Store the newest `taken` you have seen and pass it
   as a `since` query parameter, so a re-run fetches only new data.
4. **`--format json`** on `report` and `stats`, so the output can be piped into
   `jq`. Diagnostics to stderr, data to stdout.
5. **Concurrent extraction** with `ThreadPoolExecutor` over page URLs when the
   source exposes page numbers rather than opaque cursors. Note honestly in your
   README why cursor pagination cannot be parallelised.
6. **`rich` tables** (optional dependency, import-guarded, falling back to
   `format_table`).
7. **A scheduler entry point**: `python -m pipeline run` via `__main__.py`, plus a
   cron line in the README.
8. **Retry jitter** and a `--max-attempts` flag, with a test proving the delay
   sequence is bounded.

---

## Common traps in this project

| Trap | Symptom | Fix |
|---|---|---|
| Reading `os.environ` deep in the code | Untestable, surprising behaviour | Only `config.py`, only at startup |
| Calling `requests` inside the logic | Tests need network or mocks | Inject `fetch`; import lazily in `main` |
| `list(records)` inside a transform stage | Memory grows with the input | Generators all the way through |
| Iterating the stream twice in `aggregate` | Second pass sees nothing | Accumulate in one pass |
| Mutating a frozen `Record` | `FrozenInstanceError` | `dataclasses.replace` |
| No `UNIQUE(sensor, taken)` | Re-runs duplicate every row | Add the constraint, use `ON CONFLICT` |
| f-string SQL | Injection; the graded tests catch it | `?` placeholders |
| `logging.basicConfig` in a module | Application config ignored or hijacked | Configure once, in `main` |
| `print` for diagnostics | Cannot silence or filter | `logger.debug/info/warning` |
| `sys.exit` inside `main` | Untestable | `return` an exit code |
| Storing local time | Off-by-one-hour bugs twice a year | Aware UTC everywhere |
| Letting one bad record raise | Nightly run dies on one row | Quarantine and count |

---

## Practice

1. Read `README.md` in this folder, then run the demo:
   ```bash
   python course/week3/day21_project_capstone_pipeline/examples.py
   ```
2. Create `pipeline/` and work milestone by milestone. After each one, run just
   that milestone's checks:
   ```bash
   python -m pytest course/week3/day21_project_capstone_pipeline -q -k m1
   ```
3. Write `my_tests.py` as you go, not at the end.
4. When everything is green, read `pipeline_ref/` and `solutions.py` and compare
   decision by decision.

---

## Recall check

1. Why does `fetch` arrive as a parameter instead of being imported?
2. Why is `Settings` frozen, and why does `load_settings` take an `env` mapping?
3. What makes the transform stage "streaming", and which single line would destroy that property?
4. What exactly makes a re-run of `run` idempotent?
5. Why is `taken` stored as an ISO string in UTC rather than a local timestamp?
6. Where does logging get configured, and why only there?
7. Why does `main` return an exit code instead of calling `sys.exit`?
8. A record arrives with `"value": "abc"`. Trace what happens to it, layer by layer.

<details>
<summary>Answers</summary>

1. So the pipeline's logic can be tested offline in milliseconds with no mocking
   library, and so the same code can be reused with a different transport (a file,
   a cache, `httpx`). It also documents the dependency in the signature.
2. Frozen because configuration must not change under the program's feet, and
   frozen dataclasses are hashable and safe to pass anywhere. The `env` parameter
   makes configuration a pure function of its input, so tests pass a dict instead
   of patching the process environment.
3. Each stage is a generator that yields one record at a time, so peak memory is
   independent of the input size. Any `list(records)` inside a stage — or an
   `itertools.tee` — would buffer the whole dataset and destroy it.
4. `UNIQUE(sensor, taken)` plus `INSERT ... ON CONFLICT DO UPDATE`: the second run
   updates the same rows instead of inserting new ones, so the row count is
   unchanged and the values converge.
5. Because an aware UTC ISO string sorts correctly, compares exactly, is unambiguous
   across deployments and time-zone changes, and makes the UNIQUE key stable. Local
   time breaks all four, twice a year.
6. Once, in `main`, because logging configuration is a global, application-level
   decision. A module that calls `basicConfig` either does nothing (a handler
   already exists) or overrides the application's choice.
7. Because a return value is testable: a test calls `main([...])` and asserts on the
   code. `sys.exit` raises `SystemExit`, which every caller then has to catch, and
   it makes `main` unusable as a library function.
8. `normalise_record` calls `float("abc")`, gets `ValueError`, and raises;
   `normalise_all` catches it and appends the raw dict to the quarantine list;
   `extract_records` returns it in `quarantined`; the transform never sees it;
   nothing is written to SQLite; `main` logs the count at DEBUG/INFO and includes it
   in the summary table. Nothing crashes, and the record is still visible as a
   number (or as a line in the quarantine file, if you did stretch goal 2).

</details>
