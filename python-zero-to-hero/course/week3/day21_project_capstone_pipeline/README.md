# sensorpipe

A command-line ETL tool for sensor readings: fetch paginated JSON from an HTTP
source, quarantine the rows that are unusable, stream the rest through
filter/enrich/aggregate stages, store them in SQLite so that re-running changes
nothing, and report on what is stored.

Built for Day 21 of python-zero-to-hero. Standard library only, except for
`requests`, which is imported lazily and only when a command actually has to talk
to a network.

This README describes the reference implementation. Replace it with your own once
your version runs — a stranger should be able to follow it without reading the
code.

## Requirements

- Python 3.10 or newer (`python --version`)
- pytest, for grading: `python -m pip install pytest`
- `requests`, only if you want `run` to fetch over real HTTP:
  `python -m pip install requests`

Everything except a live `run` works without `requests` installed, including the
whole test suite.

## Configuration

Every knob is an environment variable, read once at startup and validated
immediately. An invalid value stops the program with a message naming the
variable and the value — not a traceback.

| Variable | Default | Meaning |
|---|---|---|
| `SENSORPIPE_URL` | `https://example.invalid/v1/readings` | first page of the source; must start with `http://` or `https://` |
| `SENSORPIPE_DB` | `sensorpipe.db` | SQLite file; parent directories are created |
| `SENSORPIPE_BATCH_SIZE` | `100` | rows per transaction, 1–10000 |
| `SENSORPIPE_MAX_PAGES` | `10` | how many pages one `run` may fetch, at least 1 |
| `SENSORPIPE_MIN_VALUE` | `0.0` | readings below this are dropped by the transform |
| `SENSORPIPE_VERBOSE` | `0` | `1/true/yes/on` for DEBUG logging |

```bash
export SENSORPIPE_URL="http://127.0.0.1:8731/v1/readings"
export SENSORPIPE_DB="/tmp/sensorpipe.db"
```

## Run it

From the course root, with your own implementation:

```bash
python course/week3/day21_project_capstone_pipeline/exercises.py run
```

or the reference:

```bash
python course/week3/day21_project_capstone_pipeline/solutions.py run
```

Three subcommands, plus a global `-v/--verbose` that goes before the subcommand.

### `run` — fetch, transform, store

```
$ python solutions.py run
INFO     pipeline_ref.extract: extracted 5 records from 2 page(s), quarantined 2
INFO     sensorpipe: stored 5 record(s); 5 row(s) in the database
metric       value
-----------  -----
fetched          5
written          5
stored           5
quarantined      2
errors           0

band    count
------  -----
normal      3
high        1
low         1

window: 2024-03-15T12:00:00+00:00 .. 2024-03-16T00:30:00+00:00
```

`--limit N` stores at most N records (0, the default, means all of them).

Run it again and nothing changes — that is the point:

```
$ python solutions.py run
...
stored           5
```

Exit codes: `0` success, `1` extraction failed and nothing was stored, `2`
configuration error.

### `report` — the busiest sensors

```
$ python solutions.py report --limit 3
sensor  count   mean
------  -----  -----
s1          3  20.25
s2          1   19.0
s3          1   12.5
```

### `stats` — one sensor

```
$ python solutions.py stats --sensor s1
sensor  count   mean   min   max
------  -----  -----  ----  ----
s1          3  20.25  9.25  30.0

$ python solutions.py stats --sensor nope
ERROR    sensorpipe: unknown sensor: nope
$ echo $?
2
```

### `-v` — say what you are doing

```
$ python solutions.py -v run
DEBUG    sensorpipe: settings: Settings(source_url='http://127.0.0.1:8731/v1/readings', ...)
DEBUG    pipeline_ref.extract: page http://127.0.0.1:8731/v1/readings: 2 ok, 2 quarantined
DEBUG    pipeline_ref.load: wrote batch of 5 (5 so far)
```

Diagnostics go through `logging` (stderr), data goes through `print` (stdout), so
`python solutions.py report > report.txt` captures the table and nothing else.

## Architecture

```
              environment variables
                       |
                 [ M1 config ]   Settings: frozen, validated once
                       |
  fetch(url) --> [ M2 extract ]  retries + backoff + pagination
  (injected)           |         raw dicts -> Record, bad rows -> quarantine
                       v
                [ M3 transform ] generators: filter -> enrich -> aggregate
                       |
                       v
                 [ M4 load ]     SQLite: UNIQUE(sensor, taken) + upsert
                       |
                       v
              [ M5 report + CLI ] argparse subcommands, tables, exit codes
```

Four decisions carry the whole design:

1. **The transport is a parameter.** `fetch(url) -> (status, payload)` arrives as
   an argument, so the tests replace it with a dict lookup. No network, no
   credentials, no mocking library.
2. **Configuration is a parameter too.** `load_settings(env)` reads a mapping,
   defaulting to `os.environ`. Nothing else in the project looks at the
   environment.
3. **The transform stages are generators.** Peak memory does not depend on how
   many records the source has, and a `list(records)` anywhere in a stage would
   destroy that.
4. **`UNIQUE(sensor, taken)` plus `ON CONFLICT DO UPDATE`.** That, and storing
   `taken` as an aware UTC ISO string, is the whole of idempotence: a second run
   updates the same rows instead of inserting new ones.

Timestamps are always converted to UTC on the way in and stored as ISO-8601
strings, so they sort chronologically as text and the UNIQUE key is stable
regardless of where the process runs.

## Where the code lives

| Path | What it is |
|---|---|
| `LESSON.md` | the project brief: milestones M1–M5, hints, done-checklist |
| `exercises.py` | your implementation and the app entry point (the graded API) |
| `pipeline/` | your package: `config.py`, `extract.py`, `transform.py`, `load.py`, `report.py`, `cli.py` — you create this |
| `my_tests.py` | your own tests, at least eight, not graded — you create this |
| `solutions.py` | the reference: a thin re-export of `pipeline_ref/` |
| `pipeline_ref/` | the reference package, one module per milestone |
| `examples.py` | the same architecture on a different dataset (bird sightings) |
| `test_exercises.py` | the graded checks, `test_m1_*` … `test_m5_*` |

## Grade it

```bash
python check.py day21          # milestone-by-milestone progress
python check.py day21 -v       # with full failure detail
```

Or pytest directly, from the course root:

```bash
python -m pytest course/week3/day21_project_capstone_pipeline -q
python -m pytest course/week3/day21_project_capstone_pipeline -q -k m3   # one milestone
PZH_SOLUTIONS=1 python -m pytest course/week3/day21_project_capstone_pipeline -q
```

The last command grades `solutions.py` instead of your file, which is how you
prove the suite is passable when a check looks impossible. The whole suite runs
offline in under a second; if yours needs the network, something is imported that
should have been injected.

Run the demo any time — it exits 0, needs nothing installed, and cleans up after
itself:

```bash
python course/week3/day21_project_capstone_pipeline/examples.py
```

## Use it as a library

The graded API is plain Python, so every layer works on its own:

```python
from solutions import (
    connect,
    extract_records,
    load_settings,
    run_transform,
    top_sensors,
    upsert_records,
)

pages = {
    "https://example.invalid/v1/readings": (
        200,
        {"items": [{"sensor": "s1", "value": "21.5", "taken": "2024-03-15T13:00:00Z"}], "next": None},
    )
}
settings = load_settings({"SENSORPIPE_DB": "/tmp/demo.db"})
records, quarantined, errors = extract_records(pages.__getitem__, settings)
kept, summary = run_transform(records, settings.min_value)

connection = connect(settings.db_path)
upsert_records(connection, kept, batch_size=settings.batch_size)
print(summary["sensors"], top_sensors(connection, 5))
connection.close()
```

## Trying `run` against a real HTTP source

You do not need a public API. Serve two pages of JSON locally, point
`SENSORPIPE_URL` at it, and `run` goes over real HTTP through `requests`:

```python
# serve.py — run with `python serve.py`, stop with Ctrl-C
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE = "http://127.0.0.1:8731/v1/readings"
PAGES = {
    "/v1/readings": {
        "items": [{"sensor": "s1", "value": "21.5", "taken": "2024-03-15T13:00:00Z", "region": "eu"}],
        "next": BASE + "?cursor=p2",
    },
    "/v1/readings?cursor=p2": {
        "items": [{"sensor": "s1", "value": 30.0, "taken": "2024-03-15T14:00:00Z", "region": "eu"}],
        "next": None,
    },
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(PAGES.get(self.path, {})).encode()
        self.send_response(200 if self.path in PAGES else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


HTTPServer(("127.0.0.1", 8731), Handler).serve_forever()
```

Note that the `next` cursor is an absolute URL. Relative cursors would need
`urllib.parse.urljoin`, which is a fine stretch goal.
