# Day 19 — APIs and Databases

> **Time:** ~4 hours  |  **Prerequisites:** Day 18

## What you'll be able to do after today
- Describe an HTTP request and response part by part, and read a status code correctly.
- Call a JSON API with `requests`, always with a timeout, and handle the four failure modes that actually happen.
- Walk a paginated endpoint, retry transient failures with exponential backoff, and respect rate limits.
- Keep credentials out of your source code and out of your logs.
- Store data in SQLite with parameterised queries, and explain SQL injection by showing it.
- Design network code so its logic is testable **offline**, with no mocking library.

## Why this matters

Almost every useful program talks to something else over HTTP and keeps its
results somewhere durable. Those two skills — call an API, persist the answer —
are the bulk of day-to-day backend, data and automation work.

They are also where beginners write their most dangerous code. A request with no
timeout hangs forever and takes your service down with it. A retry loop with no
backoff turns a wobbling dependency into an outage you caused. An f-string in a
SQL query is how customer databases get dumped onto the internet. An API key
committed to git is a credential you must now rotate everywhere, forever, and
GitHub's secret scanners find them within minutes.

One structural note, because it shapes today's exercises: **network code is
testable only if the network is a parameter.** Every function you write today
either takes already-fetched data, or takes the fetching function as an argument.
That is not a testing trick; it is the design that makes the code reviewable,
retryable and reusable. The exercises make no network calls at all, and neither
do the tests.

---

## 1. HTTP in ten minutes

A client sends a **request**; a server sends back a **response**. Both are text
with a defined shape.

```
GET /v1/readings?page=2&limit=50 HTTP/1.1        <- method, path, query, version
Host: api.example.com                            <- headers
Authorization: Bearer sk_live_abc123
Accept: application/json
                                                 <- blank line
(no body for GET)
```

```
HTTP/1.1 200 OK                                  <- status line
Content-Type: application/json                   <- headers
X-RateLimit-Remaining: 47

{"items": [...], "next": "/v1/readings?page=3"}  <- body
```

### Methods

| Method | Means | Has a body | Safe to retry |
|---|---|---|---|
| `GET` | read something | no | yes (idempotent) |
| `POST` | create something / trigger an action | yes | **no** — may double-charge |
| `PUT` | replace a resource wholesale | yes | yes (idempotent by definition) |
| `PATCH` | modify part of a resource | yes | usually |
| `DELETE` | remove a resource | rarely | yes (deleting twice is still deleted) |

"Idempotent" means doing it twice has the same effect as doing it once. It decides
whether a retry is safe, which is why it matters today.

### Status codes

Learn the shape first: **2xx** worked, **3xx** go elsewhere, **4xx** you were
wrong, **5xx** they were wrong.

| Code | Name | What you do about it |
|---|---|---|
| 200 | OK | parse the body |
| 201 | Created | read the `Location` header |
| 204 | No Content | success, and there is no body to parse |
| 301/302 | Moved / Found | follow it (`requests` does this for you) |
| 304 | Not Modified | use your cached copy |
| 400 | Bad Request | fix your payload; retrying will not help |
| 401 | Unauthorized | missing or invalid credentials |
| 403 | Forbidden | authenticated, but not allowed |
| 404 | Not Found | wrong URL or the thing is gone |
| 409 | Conflict | duplicate or concurrent update |
| 422 | Unprocessable | validation failed on their side |
| 429 | Too Many Requests | **slow down** — read `Retry-After` |
| 500 | Internal Server Error | their bug; retry cautiously |
| 502/503/504 | Bad Gateway / Unavailable / Timeout | transient; retry with backoff |

The retry rule falls out of that table: retry **429 and 5xx**, never retry other
**4xx** (you will get the same answer forever, faster).

### Query string versus body

- **Query string** (`?page=2&limit=50`): small, non-secret parameters that
  identify or filter what you want. Visible in logs and browser history, so never
  put a password or token there.
- **Body**: the data you are sending, usually JSON. Requires `POST`/`PUT`/`PATCH`.

### Headers you will actually set

`Content-Type: application/json` (what I am sending),
`Accept: application/json` (what I want back),
`Authorization: Bearer <token>` (who I am),
`User-Agent: my-tool/1.0 (contact@example.com)` (be a good citizen — some APIs
reject unknown agents).

---

## 2. `requests`: the 95% you need

`requests` is not in the standard library; install it with
`python -m pip install requests`. The standard library alternative is
`urllib.request`, which works and is unpleasant.

```python
import requests

response = requests.get(
    "https://api.example.com/v1/readings",
    params={"page": 2, "limit": 50},      # requests builds & encodes the query
    headers={"Accept": "application/json"},
    timeout=10,                            # NEVER omit this
)

print(response.status_code)   # 200
print(response.headers["Content-Type"])
data = response.json()        # parsed JSON -> dict/list
print(response.text[:80])     # the raw body, if you need it
```

Sending JSON:

```python
response = requests.post(
    "https://api.example.com/v1/readings",
    json={"sensor": "s1", "value": 21.5},   # sets Content-Type for you
    timeout=10,
)
```

Use a `Session` when you make more than one call: it reuses the TCP connection
(much faster) and carries shared headers.

```python
with requests.Session() as session:
    session.headers.update({"Authorization": f"Bearer {token}"})
    for page in range(1, 4):
        session.get(url, params={"page": page}, timeout=10)
```

`httpx` is the modern alternative with the same API shape plus async support and
HTTP/2 — `httpx.get(url, timeout=10)` works identically, and
`async with httpx.AsyncClient() as client: await client.get(...)` is what you
reach for once Day 20's asyncio makes sense. Learn `requests` first; the concepts
transfer exactly.

---

## 3. Timeouts are not optional

Without `timeout`, `requests` waits **forever** if the server accepts the
connection and never answers. Not thirty seconds — forever. Your worker thread is
gone, then the next one, and eventually the whole service is wedged on a
dependency that never said no.

```python
requests.get(url, timeout=10)          # 10s for connect AND 10s for read
requests.get(url, timeout=(3.05, 27))  # (connect, read) — the tuple form
```

Rules of thumb: connect timeout small (3–5 s; a healthy server answers the
handshake immediately), read timeout based on the work you are asking for
(10–30 s for an API, longer for a report). Every call in a loop gets a timeout.
There is no exception to this rule.

---

## 4. Error handling: the four failures that happen

```python
import requests


def fetch_json(url: str, timeout: float = 10.0) -> dict:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()        # turn 4xx/5xx into an exception
        return response.json()
    except requests.Timeout:
        raise                             # transient: the caller may retry
    except requests.ConnectionError:
        raise                             # DNS failure, refused, network down
    except requests.HTTPError as error:
        # A real status code came back. 4xx is your bug; 5xx is theirs.
        status = error.response.status_code
        raise
    except ValueError:
        # .json() failed: the body was HTML, empty, or truncated.
        raise
```

Four distinct things, and they need different responses:

1. **Timeout** — retry with backoff.
2. **ConnectionError** — retry, but slowly; something is down.
3. **HTTPError** — inspect the code: 429/5xx retry, 4xx fix your code.
4. **Invalid JSON** — do not retry blindly; log the first 200 characters of the
   body. This is usually an error page or a captive portal.

`response.raise_for_status()` is the line beginners forget. Without it, a 500
response sails on and `response.json()` raises something confusing three lines
later — or worse, the API returns `200` with `{"error": ...}`, so also check the
payload shape, not only the status.

Never write `except requests.RequestException: pass`. Silent failure in a data
pipeline means "yesterday's numbers, forever, and nobody knows".

---

## 5. Pagination

APIs return pages, not everything. The three common shapes:

```python
# 1. Cursor/next-URL: keep following until it is null. The easiest to get right.
{"items": [...], "next": "/v1/readings?cursor=abc123"}

# 2. Page numbers with a total: loop while you have not seen everything.
{"items": [...], "page": 2, "total_pages": 7}

# 3. Offset/limit: increment offset until you get fewer items than you asked for.
{"items": [...], "offset": 100, "limit": 50}
```

A generator is the right shape for this (Day 15), because the caller can stop
early and memory stays flat:

```python
from collections.abc import Iterator


def iter_all(fetch, first_url: str, max_pages: int = 100) -> Iterator[dict]:
    """Yield every item across pages. `fetch` is injected so tests can fake it."""
    url = first_url
    pages = 0
    while url and pages < max_pages:      # the guard prevents an infinite loop
        payload = fetch(url)
        yield from payload.get("items", [])
        url = payload.get("next")
        pages += 1
```

Two details that separate working code from a 3 a.m. incident:

- **Always bound the loop.** A server bug that returns the same `next` URL will
  otherwise spin forever, at full speed, against production.
- **`fetch` is a parameter.** In production you pass a function that calls
  `requests`; in tests you pass one that returns dicts from a list. No mocking
  library, no network, and the pagination logic is fully covered.

---

## 6. Retries with exponential backoff

Retrying immediately, in a tight loop, is worse than not retrying: you add load
to a service that is already struggling. Wait, and wait longer each time.

```
attempt 1 fails -> wait 1s
attempt 2 fails -> wait 2s
attempt 3 fails -> wait 4s
attempt 4 fails -> wait 8s      (capped, e.g. at 30s)
```

```python
def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Delay before retry number `attempt` (1-based), capped."""
    return min(base * 2 ** (attempt - 1), cap)
```

Add **jitter** — a small random amount — in production. Without it, a thousand
clients that failed together retry together, in synchronised waves. That is the
"thundering herd", and jitter is the one-line fix:
`delay * random.uniform(0.5, 1.5)`. Today's exercises keep jitter out so the
tests are deterministic; real code has it.

The complete decision:

```python
RETRYABLE = {429, 500, 502, 503, 504}


def should_retry(status: int, attempt: int, max_attempts: int) -> bool:
    if attempt >= max_attempts:
        return False                  # bound it: no infinite retries
    return status in RETRYABLE
```

And the rule that saves money: **only retry idempotent requests.** Retrying a
`POST /payments` that actually succeeded but timed out on the way back charges the
customer twice. Real APIs solve this with an idempotency key you generate and
send; if you retry with the same key, the server recognises it and does not repeat
the work.

For production Python, `urllib3`'s `Retry` adapter or the `tenacity` library do
this properly. Write it once by hand first, so you know what they are doing.

---

## 7. Rate limits

APIs cap how often you may call them. When you exceed the cap you get `429`, and
often headers describing the budget:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1710510000        (unix timestamp)
Retry-After: 12                      (seconds — obey this, do not guess)
```

Behave well:

- If `Retry-After` is present on a 429 or 503, wait **that long**. It is not a
  suggestion, and ignoring it is how API keys get revoked.
- Throttle proactively when `Remaining` gets low rather than sprinting into the
  wall.
- Batch: one request for 100 records beats 100 requests for one record.
- Cache responses you will need again (`functools.lru_cache` for in-process,
  `Cache-Control`/`ETag` for HTTP).
- Read the docs for the actual limit before you write the loop.

---

## 8. Secrets: environment variables, never source code

```python
import os

API_KEY = os.environ.get("WEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("WEATHER_API_KEY is not set; see README for setup")
```

```bash
export WEATHER_API_KEY=sk_live_abc123      # your shell, or a .env file, or CI secrets
python -m my_tool
```

Non-negotiables:

1. **Never** hardcode a key, not even "temporarily". `git` remembers, and public
   scanners find committed keys in minutes.
2. `.env` files are fine for local development. Add `.env` to `.gitignore` before
   creating it, never after.
3. Never log a secret. `logger.debug("headers=%s", headers)` leaks your token into
   a log aggregator a dozen people can read. Redact before logging.
4. Fail loudly at startup when a required secret is missing, not at 3 a.m. on the
   first request.
5. Prefer `Authorization` headers over query parameters: URLs end up in access
   logs, proxies and browser history.

If a key leaks, rotating it is the only fix. Deleting the commit is not enough —
it is in every clone and in the reflog.

---

## 9. `sqlite3`: a real database with no server

SQLite is a full SQL database in a single file, built into Python. It is the right
default for scripts, local tools, tests and anything under roughly a million rows
with one writer.

```python
import sqlite3

# ":memory:" gives a private database that vanishes when the connection closes -
# perfect for tests, though tests here use tmp_path so they exercise real files.
connection = sqlite3.connect("readings.db")
connection.row_factory = sqlite3.Row      # rows behave like dicts, not tuples

cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor  TEXT    NOT NULL,
        value   REAL    NOT NULL,
        taken   TEXT    NOT NULL,
        UNIQUE(sensor, taken)
    )
""")
connection.commit()
```

Vocabulary: a **connection** is the open database; a **cursor** runs statements
and holds results. `connection.execute(...)` creates a cursor implicitly, which is
fine for one-off statements.

### Insert, select, update

```python
cursor.execute(
    "INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)",
    ("s1", 21.5, "2024-03-15T13:00:00+00:00"),
)
cursor.executemany(
    "INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)",
    [("s2", 19.0, "2024-03-15T13:00:00+00:00"),
     ("s3", 25.5, "2024-03-15T13:00:00+00:00")],
)
connection.commit()                        # nothing is durable until you commit

rows = cursor.execute(
    "SELECT sensor, value FROM readings WHERE value > ? ORDER BY value DESC",
    (20.0,),                               # a ONE-element tuple needs the comma
).fetchall()
for row in rows:
    print(row["sensor"], row["value"])     # thanks to row_factory

cursor.execute("UPDATE readings SET value = ? WHERE sensor = ?", (22.0, "s1"))
connection.commit()
```

`fetchone()` returns one row or `None`; `fetchall()` returns a list; iterating the
cursor streams rows, which is what you want for large results.

### Upserts and idempotent re-runs

A pipeline that is run twice must not duplicate its data. Combine a `UNIQUE`
constraint with `ON CONFLICT`:

```python
cursor.executemany("""
    INSERT INTO readings (sensor, value, taken) VALUES (?, ?, ?)
    ON CONFLICT(sensor, taken) DO UPDATE SET value = excluded.value
""", rows)
```

`excluded` is the row that would have been inserted. `INSERT OR IGNORE` is the
simpler variant when you want to keep the existing row. Either way, re-running
the pipeline converges to the same database instead of growing it — that property
is called idempotence and Day 21 requires it.

### Transactions

```python
try:
    with connection:                       # commit on success, rollback on error
        connection.execute("INSERT INTO readings VALUES (...)")
        connection.execute("INSERT INTO audit VALUES (...)")
except sqlite3.IntegrityError:
    ...                                    # both inserts were rolled back
```

`with connection:` is a transaction, not a "close the connection" block — a
genuinely confusing API. Use `contextlib.closing(connection)` if you also want it
closed. Grouping thousands of inserts into one transaction is also the difference
between 2 seconds and 4 minutes.

---

## 10. SQL injection, shown concretely

The single most exploited class of web vulnerability, and the fix is one
character.

```python
name = "s1"
# WRONG. Never build SQL with string formatting.
cursor.execute(f"SELECT * FROM readings WHERE sensor = '{name}'")
```

Now the input arrives from a user, and it is:

```python
name = "x' OR '1'='1"
```

Your query becomes `SELECT * FROM readings WHERE sensor = 'x' OR '1'='1'`, which
returns **every row in the table**. Or:

```python
name = "x'; DROP TABLE readings; --"
```

With `executescript`, or in any database driver that permits multiple statements,
that deletes the table. `sqlite3.execute` refuses multiple statements, which
saves you here — but it does not save you from the `OR '1'='1'` data leak, and
your next job might use a driver that allows both.

The fix, always:

```python
cursor.execute("SELECT * FROM readings WHERE sensor = ?", (name,))
```

The `?` is a **placeholder**. The driver sends the query and the values
separately, so the value is never parsed as SQL. `"x' OR '1'='1"` is looked up as
a literal sensor name, finds nothing, and returns zero rows — which is exactly
right.

- SQLite uses `?` (positional) or `:name` (named:
  `execute("... WHERE sensor = :s", {"s": name})`).
- Placeholders work for **values only**. Table and column names cannot be
  parameterised; if they must be dynamic, validate them against an allow-list you
  wrote by hand.
- `%s`-style formatting is what psycopg (PostgreSQL) uses as its *placeholder*,
  which confuses people: `cursor.execute("... = %s", (name,))` is parameterised
  and safe; `cursor.execute("... = %s" % name)` is the bug. The difference is the
  comma versus the percent.

> **Gotcha:** `cursor.execute("SELECT ...", (name))` without the trailing comma
> passes a string, not a tuple, and SQLite complains about the parameter count —
> or, for a one-character name, silently works. `(name,)` is the tuple.

---

## 11. ORMs, briefly

An **Object-Relational Mapper** maps rows to objects so you write Python instead
of SQL. SQLAlchemy is the standard; Django has its own; SQLModel wraps SQLAlchemy
with pydantic.

```python
# SQLAlchemy 2.x, for shape only - not installed in this course
session.add(Reading(sensor="s1", value=21.5))
session.commit()
rows = session.scalars(select(Reading).where(Reading.value > 20)).all()
```

Worth it when: many tables with relationships, a schema that changes often
(migrations), multiple databases, or a team that benefits from typed models.

Not worth it when: a script, a handful of tables, or analytical queries where you
want to control the SQL exactly. An ORM is another large dependency, it hides how
many queries you are making (the "N+1 query" problem), and it does not remove the
need to know SQL — it adds a second thing to know.

Learn SQL first. Then an ORM is a convenience rather than a magic box.

---

## 12. Designing network code so it can be tested

This is the day's most transferable idea, and it is why the exercises need no
network.

Split every integration into three layers:

```
  1. TRANSPORT   the only code that touches the network. Tiny, boring,
                 barely tested: fetch(url) -> dict.
  2. LOGIC       URL building, retry decisions, backoff maths, pagination,
                 parsing, validation, quarantining bad records. Pure
                 functions over plain data. 95% of your tests live here.
  3. STORAGE     SQL, against a real SQLite file in tmp_path.
```

Then inject the transport:

```python
def sync(fetch, connection, url):     # `fetch` is a parameter, not an import
    for item in iter_all(fetch, url):
        save(connection, parse(item))
```

Production passes `lambda u: requests.get(u, timeout=10).json()`. Tests pass a
function returning canned dicts. Nobody needs `unittest.mock.patch`, the tests run
in milliseconds, they work on a plane, and they never flake.

Contrast that with the version where `sync` calls `requests.get` directly: now
your tests either hit the network (slow, flaky, requires credentials) or need
patching (brittle, and it verifies your mock more than your code). The design
choice removes the problem.

Where you do need confidence in the transport itself, that is what a small number
of **integration tests** are for: run them separately, mark them
`@pytest.mark.integration`, exclude them from the default run, and accept that
they need the network and credentials.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| No `timeout=` | Process hangs forever; workers exhausted | `timeout=10` on every call |
| No `raise_for_status()` | Confusing JSON errors instead of the real HTTP error | Call it, or check `status_code` |
| Retrying 4xx | Same failure, three times, slower | Retry only 429 and 5xx |
| Retrying without backoff | You DDoS your own dependency | `min(base * 2**(attempt-1), cap)` |
| Retrying a POST blindly | Duplicate orders, double charges | Idempotency keys, or do not retry |
| Ignoring `Retry-After` | Rate limit becomes a ban | Sleep for exactly that long |
| Unbounded pagination loop | Infinite loop against production | `max_pages` guard |
| Hardcoded API key | Credential leak, mandatory rotation | `os.environ`, and `.gitignore` first |
| Logging headers | Token in a log aggregator | Redact before logging |
| f-string SQL | SQL injection; data leak or loss | `?` placeholders every time |
| `execute(sql, (name))` | "Incorrect number of bindings" | `(name,)` — the trailing comma |
| Forgetting `commit()` | Data vanishes when the process exits | `connection.commit()`, or `with connection:` |
| One transaction per insert | 4 minutes instead of 2 seconds | Batch inside one transaction |
| Inserting without a UNIQUE key | Re-running duplicates every row | `UNIQUE(...)` plus `ON CONFLICT` |
| Calling `requests` deep inside logic | Untestable without mocks or network | Inject `fetch` as a parameter |

---

## Mental model

```
   YOUR PROGRAM                                        THE INTERNET
   ------------                                        ------------
   build_url(base, path, params) ------------------.
                                                    \
   fetch(url)  <-- the ONLY networked function ------>  GET /v1/x?page=2
      |  timeout=10, Authorization: Bearer ...      <-  200 + JSON
      v                                                (or 429 / 503 / dead air)
   classify(status) -> retry? --yes--> wait backoff(attempt) --> fetch again
      |
      | no
      v
   parse(payload) -> dataclasses -----> quarantine anything malformed
      |
      v
   save(connection, records)  ---- INSERT ... ON CONFLICT DO UPDATE ---> file.db
                                   (parameterised, one transaction, idempotent)
```

Everything in that diagram except the single `fetch` box is a pure function over
plain data. That is why today's tests need no network: the interesting parts never
had any.

The other picture worth keeping:

```
  ?  = placeholder  = value travels beside the query  = safe
  f" = f-string     = value becomes part of the query = injection
```

---

## Practice

1. Run the demo. It tries exactly one real HTTP request and falls back to a canned
   payload if there is no network, so it works offline:
   ```bash
   python course/week3/day19_apis_and_databases/examples.py
   ```
2. Implement the ten exercises in `exercises.py`. None of them may touch the
   network: 1–4 are URL and retry logic, 5 is parsing and quarantining, 6–7 take
   an injected `fetch`, 8–9 are SQLite, and 10 wires the whole pipeline together.
3. Grade from the course root:
   ```bash
   python check.py day19
   ```
4. Optional, needs network: point `examples.py` at a different public API and
   watch the fallback path disappear.

---

## Recall check

1. What does a 429 mean, what header should you obey, and what do you do?
2. Which status codes are worth retrying, and which are a waste of time?
3. What happens if you omit `timeout=` from a `requests` call?
4. Name the four distinct failure modes of an HTTP call and the right response to each.
5. Why must a pagination loop have a maximum page count?
6. Write the exponential backoff formula, and say what jitter is for.
7. Why is retrying a `POST` dangerous when retrying a `GET` is not?
8. Where do secrets live, and what are the two rules about logging them?
9. Explain SQL injection using `"x' OR '1'='1"`, and give the fix.
10. What makes a pipeline re-run idempotent in SQLite?
11. Why does injecting `fetch` as a parameter matter more than knowing `unittest.mock`?

<details>
<summary>Answers</summary>

1. Too Many Requests: you have exceeded the rate limit. Obey `Retry-After` and
   sleep for exactly that many seconds before trying again; also throttle
   proactively when `X-RateLimit-Remaining` gets low.
2. Retry 429 and 5xx (500, 502, 503, 504) with backoff. Do not retry other 4xx —
   400, 401, 403, 404, 422 will return the same answer every time.
3. The call can block forever. `requests` has no default timeout, so a server that
   accepts the connection and never responds ties up your thread indefinitely.
4. `Timeout` (retry with backoff), `ConnectionError` (retry slowly; something is
   down), `HTTPError` (inspect the code: 429/5xx retry, 4xx fix your request),
   and invalid JSON (do not retry blindly; log the start of the body — it is
   usually an error page).
5. A server bug or a cursor that never advances makes the loop run forever, at
   full speed, against production. The bound turns an outage into a log line.
6. `delay = min(base * 2 ** (attempt - 1), cap)`. Jitter multiplies that by a
   small random factor so that clients which failed simultaneously do not retry
   simultaneously — it breaks up the thundering herd.
7. `GET` is idempotent: repeating it changes nothing. `POST` usually creates or
   charges something, so a request that succeeded but whose response was lost gets
   performed twice. Idempotency keys let the server deduplicate.
8. In environment variables (or a secret manager), read at startup with a loud
   failure if missing. Never log them, and never put them in a URL query string,
   because URLs and log lines are stored and shared.
9. With f-string SQL, the value becomes part of the statement:
   `WHERE sensor = 'x' OR '1'='1'` is always true, so the query returns every row.
   Using `?` placeholders sends the value separately from the SQL, so it is
   treated as a literal string and matches nothing.
10. A `UNIQUE` constraint on the natural key plus `INSERT ... ON CONFLICT DO
    UPDATE` (or `INSERT OR IGNORE`), so a second run updates or skips rather than
    inserting duplicates.
11. Because it changes the design, not just the test. With `fetch` injected, all
    the retry, pagination and parsing logic is pure functions over plain data:
    testable offline, in milliseconds, with no patching, and reusable with a
    different transport. Mocking treats an untestable design as a test problem.

</details>
