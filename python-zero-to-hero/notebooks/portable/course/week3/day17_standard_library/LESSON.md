# Day 17 — The Standard Library That Earns Its Keep

> **Time:** ~4 hours  |  **Prerequisites:** Day 16

## What you'll be able to do after today
- Replace hand-rolled counting, grouping and queue code with `collections` types that are shorter and faster.
- Combine iterators with `itertools` — including `groupby`, whose sorting requirement traps everyone once.
- Handle timestamps without the naive-versus-aware bug: parse ISO strings, convert time zones, and do arithmetic with `timedelta`.
- Write regular expressions from scratch: classes, quantifiers, groups, named groups, and `sub` — and recognise when regex is the wrong tool.
- Give a script a real command-line interface with `argparse`, including types, defaults, and subcommands.
- Replace every `print` in a library with `logging` configured properly at the edges.
- Model data with `dataclasses` plus `enum` so invalid states are unrepresentable.

## Why this matters

The standard library is the difference between a Python programmer and someone
who writes Java in Python. Every function you write by hand that already exists
in the standard library is code you must test, debug, document and maintain,
which is a bad trade. `Counter` is not a shortcut — it is the version that is
already correct, already fast, and already understood by every reader.

The failures this day prevents are specific and expensive: the report that is
wrong by one hour twice a year because you compared a naive datetime to an aware
one; the `groupby` that silently drops half the data because the input was not
sorted; the debugging session that requires editing production code because you
used `print` instead of `logging`; the CLI whose arguments are parsed by hand
from `sys.argv` and break the first time someone passes them in a different
order.

This day is a tour of six modules, aimed at the 20% of each that covers 95% of
real work. Read `examples.py` alongside it — every section here has a runnable
counterpart there.

---

## 1. `collections.Counter` — counting, done

You have counted things with a dict since Day 6:

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
```

`Counter` is that, plus a dozen useful operations:

```python
from collections import Counter

text = "the quick brown fox jumps over the lazy dog the end"
counts = Counter(text.split())

print(counts["the"])            # 3
print(counts["missing"])        # 0  — no KeyError, ever
print(counts.most_common(2))    # [('the', 3), ('quick', 1)]
print(sum(counts.values()))     # 11 — total items counted
print(len(counts))              # 9  — distinct items
```

Useful behaviours worth knowing:

```python
letters = Counter("mississippi")
print(letters.most_common(3))       # [('i', 4), ('s', 4), ('p', 2)]
print(sorted(letters.elements()))   # every letter repeated by its count

stock = Counter(apple=3, pear=1)
sold = Counter(apple=1)
print(stock - sold)                 # Counter({'apple': 2, 'pear': 1})
print(stock + sold)                 # Counter({'apple': 4, 'pear': 1})
print(Counter("aab") & Counter("abb"))   # Counter({'a': 1, 'b': 1}) — min
print(Counter("aab") | Counter("abb"))   # Counter({'a': 2, 'b': 2}) — max
```

> **Gotcha 1:** `most_common` breaks ties by *insertion order*, not
> alphabetically. `Counter("ba").most_common()` gives `[('b', 1), ('a', 1)]`. If
> you need a deterministic tie-break — and in a test you always do — sort
> explicitly: `sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))`.
>
> **Gotcha 2:** a missing key returns `0` but does **not** get stored, unlike
> `defaultdict`. However `counts["x"] -= 1` does store `-1`. Counters allow
> negative and zero counts; `+counts` drops the non-positive ones.

---

## 2. `defaultdict` — grouping, done

Grouping with a plain dict needs a guard clause on every insert:

```python
groups = {}
for word in words:
    if word[0] not in groups:      # the line you forget
        groups[word[0]] = []
    groups[word[0]].append(word)
```

`defaultdict` takes a zero-argument factory and calls it whenever a key is
missing:

```python
from collections import defaultdict

groups = defaultdict(list)
for word in ["apple", "avocado", "beet"]:
    groups[word[0]].append(word)        # no guard needed

print(groups)          # defaultdict(<class 'list'>, {'a': ['apple', 'avocado'], 'b': ['beet']})
print(dict(groups))    # {'a': ['apple', 'avocado'], 'b': ['beet']}
```

Common factories: `list`, `set`, `int` (counting), `dict` (nesting). Pass the
factory itself, not a call — `defaultdict(list)`, never `defaultdict(list())`.

> **Gotcha:** merely *reading* a missing key creates it.
> `if groups["z"]:` leaves `'z': []` behind, which corrupts later `len(groups)`
> checks and equality assertions. Use `groups.get("z")` to look without touching,
> or convert to `dict(groups)` before returning it from a function — which also
> stops callers depending on the defaulting behaviour.

The alternative when you do not want defaulting at all is
`dict.setdefault("a", []).append(...)`, which is fine but noisier.

---

## 3. `deque` — a list that is fast at both ends

`list.pop(0)` and `list.insert(0, x)` are O(n): every remaining element shifts.
`deque` (double-ended queue) is O(1) at both ends.

```python
from collections import deque

queue = deque(["a", "b", "c"])
queue.append("d")          # right
queue.appendleft("z")      # left
print(queue)               # deque(['z', 'a', 'b', 'c', 'd'])
print(queue.popleft())     # z
print(queue.pop())         # d
```

The killer feature is `maxlen`: a bounded buffer that discards from the far end
automatically. This is how you keep "the last 100 log lines" without any
bookkeeping:

```python
recent = deque(maxlen=3)
for event in ["a", "b", "c", "d", "e"]:
    recent.append(event)
print(list(recent))        # ['c', 'd', 'e']
```

`deque` also does `rotate`, and it is the right structure for
breadth-first search and for producer/consumer queues (it is thread-safe for
appends and pops, which matters on Day 20).

> **Gotcha:** indexing the middle of a deque (`d[500]`) is O(n), and slicing is
> not supported at all — `d[1:3]` raises `TypeError`. Use `itertools.islice` if
> you need a window. If you index randomly more than you push and pop at the
> ends, you wanted a list.

---

## 4. `namedtuple` — and when a dataclass is better

`namedtuple` builds a tuple subclass with named fields:

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p[0])           # 3 3  — both work
print(p)                   # Point(x=3, y=4)
x, y = p                   # unpacks like a tuple
print(p._replace(x=10))    # Point(x=10, y=4) — returns a new one
print(p._asdict())         # {'x': 3, 'y': 4}
```

It is immutable, memory-cheap, comparable, and unpacks — which makes it perfect
for return values with two or three parts, and for rows read from a CSV.

Choosing between the three record types you now know:

| Need | Use |
|---|---|
| Small immutable value, tuple behaviour, minimal memory | `namedtuple` / `typing.NamedTuple` |
| Mutable fields, defaults, methods, validation | `@dataclass` (Day 12) |
| Real behaviour, inheritance, invariants | a plain class (Day 13) |
| Arbitrary keys not known ahead of time | `dict` |

`typing.NamedTuple` is the modern spelling, because it takes type hints:

```python
from typing import NamedTuple


class Reading(NamedTuple):
    sensor: str
    value: float
    ok: bool = True
```

---

## 5. `itertools` — the iterator toolkit

Everything here is lazy (Day 15), so it composes without allocating.

```python
from itertools import chain, combinations, count, cycle, groupby, islice, pairwise, product

# chain: treat several iterables as one stream
print(list(chain([1, 2], (3,), "ab")))        # [1, 2, 3, 'a', 'b']
print(list(chain.from_iterable([[1, 2], [3]])))  # [1, 2, 3] — flatten one level

# product: nested loops as a flat iterator (the cartesian product)
print(list(product([1, 2], "ab")))            # [(1,'a'), (1,'b'), (2,'a'), (2,'b')]
print(list(product([0, 1], repeat=2)))        # [(0,0), (0,1), (1,0), (1,1)]

# combinations / permutations: choose k, order irrelevant / relevant
print(list(combinations("abc", 2)))           # [('a','b'), ('a','c'), ('b','c')]

# pairwise (3.10+): consecutive overlapping pairs — perfect for deltas
print(list(pairwise([10, 13, 20])))           # [(10, 13), (13, 20)]

# cycle + islice: repeat forever, bounded at the point of use
print(list(islice(cycle("ab"), 5)))           # ['a','b','a','b','a']
print(list(islice(count(10, 5), 3)))          # [10, 15, 20]
```

### `groupby` and its one trap

`groupby` yields `(key, group)` pairs for **consecutive** runs of equal keys. It
does not sort, and it does not collect scattered matches:

```python
records = [
    {"status": "ok", "id": 1},
    {"status": "fail", "id": 2},
    {"status": "ok", "id": 3},
]

for status, group in groupby(records, key=lambda r: r["status"]):
    print(status, [r["id"] for r in group])
```

Prints three groups, not two:

```
ok [1]
fail [2]
ok [3]
```

**You must sort by the same key first.**

```python
by_status = lambda r: r["status"]                      # noqa: E731
ordered = sorted(records, key=by_status)
for status, group in groupby(ordered, key=by_status):
    print(status, [r["id"] for r in group])
# fail [2]
# ok [1, 3]
```

Second trap: each `group` is a lazy iterator that becomes invalid as soon as you
advance to the next group. `list(groupby(...))` gives you groups that are all
empty. Materialise inside the loop: `{k: list(g) for k, g in groupby(...)}`.

Honestly: when you just want "all records grouped by status", `defaultdict(list)`
is clearer and does not need sorting. `groupby` wins on already-sorted streams
that do not fit in memory — a sorted log file, database output with `ORDER BY`.

### Other members worth remembering

```python
from itertools import accumulate, dropwhile, takewhile, tee, zip_longest

print(list(accumulate([1, 2, 3, 4])))              # [1, 3, 6, 10] running total
print(list(takewhile(lambda n: n < 3, [1, 2, 9, 1])))   # [1, 2] — stops at 9
print(list(dropwhile(lambda n: n < 3, [1, 2, 9, 1])))   # [9, 1]
print(list(zip_longest("ab", [1], fillvalue="?")))      # [('a',1), ('b','?')]
a, b = tee([1, 2, 3])                                    # two independent passes
```

`tee` buffers everything the slower branch has not consumed, so two full passes
over a huge stream can hold the whole thing in memory. Prefer reading twice from
the source when you can.

---

## 6. `datetime`: the naive-versus-aware trap

Three classes matter: `date` (no time), `time` (no date), `datetime` (both), plus
`timedelta` for durations and `timezone` for offsets.

```python
from datetime import date, datetime, timedelta, timezone

print(date(2024, 3, 15))                        # 2024-03-15
print(datetime(2024, 3, 15, 13, 45, 30))        # 2024-03-15 13:45:30
```

A `datetime` is **naive** if `tzinfo` is None and **aware** if it has one. Naive
means "13:45 somewhere, who knows where" — a bug waiting for a deployment to a
different region.

```python
naive = datetime(2024, 3, 15, 13, 45)
aware = datetime(2024, 3, 15, 13, 45, tzinfo=timezone.utc)
print(naive.tzinfo, aware.tzinfo)     # None  UTC

naive < aware      # TypeError: can't compare offset-naive and offset-aware datetimes
```

That `TypeError` is the good outcome. The bad outcome is subtler: naive
datetimes compare and subtract happily with each other while representing
different zones, and your report is quietly off by hours.

**The rule: store and compute in UTC, aware; convert to local time only for
display.**

```python
from zoneinfo import ZoneInfo                   # standard library since 3.9

now = datetime.now(timezone.utc)                # aware. Never datetime.utcnow()
london = ZoneInfo("Europe/London")
print(now.astimezone(london))                   # same instant, local wall clock
```

`datetime.utcnow()` is a trap and is deprecated in 3.12: it returns a naive
datetime holding UTC values, which is the worst of both worlds. Use
`datetime.now(timezone.utc)`.

### ISO parsing and formatting

```python
stamp = datetime.fromisoformat("2024-03-15T13:45:00+00:00")
print(stamp.isoformat())              # 2024-03-15T13:45:00+00:00
print(stamp.strftime("%Y-%m-%d %H:%M"))   # 2024-03-15 13:45
print(datetime.strptime("15/03/2024", "%d/%m/%Y"))   # for non-ISO input
```

`fromisoformat` is fast, strict and the right default. On Python 3.11+ it accepts
a trailing `Z`; on 3.10 it does not, so normalise first:
`text.replace("Z", "+00:00")`. Format codes you will actually use: `%Y` 4-digit
year, `%m` month, `%d` day, `%H` 24-hour, `%M` minute, `%S` second, `%z` offset,
`%A` weekday name, `%b` short month.

### `timedelta` arithmetic

```python
start = datetime(2024, 3, 15, 9, 0, tzinfo=timezone.utc)
end = datetime(2024, 3, 15, 17, 30, tzinfo=timezone.utc)

worked = end - start                      # a timedelta
print(worked)                             # 8:30:00
print(worked.total_seconds() / 3600)      # 8.5
print(start + timedelta(days=1, hours=-2))   # 2024-03-16 07:00:00+00:00
print((end - start) > timedelta(hours=8))    # True
```

`timedelta` exposes `.days`, `.seconds` and `.microseconds` only — there is no
`.hours`. Use `.total_seconds()` and divide, or you will produce the classic bug
where a duration of 25 hours reports as 1 hour.

> **Gotcha:** adding `timedelta(days=1)` to an aware datetime adds exactly 24
> hours, which is not "the same time tomorrow" across a daylight-saving
> boundary. For calendar arithmetic across DST, convert to the local zone, add,
> and re-normalise — or accept the 24-hour definition and document it.

---

## 7. Regular expressions, properly

A regex is a small pattern language for describing text. Learn it as five
building blocks, not as a wall of syntax.

**Always use a raw string** for patterns: `r"\d+"`. In a normal string `"\d"`
survives by accident today and becomes a `SyntaxWarning`, then an error, in
future versions. `\b` in a normal string is a backspace character.

### 7.1 Literals and classes

```python
import re

print(re.search(r"cat", "concatenate"))     # matches at index 3
```

Character classes match one character out of a set:

| Pattern | Matches |
|---|---|
| `.` | any character except newline |
| `\d` / `\D` | digit / non-digit |
| `\w` / `\W` | word character `[a-zA-Z0-9_]` / non-word |
| `\s` / `\S` | whitespace / non-whitespace |
| `[abc]` | one of a, b, c |
| `[a-z0-9]` | one lowercase letter or digit |
| `[^abc]` | anything except a, b, c |
| `\b` | word boundary (zero width) |
| `^` / `$` | start / end of string (or line with `re.MULTILINE`) |

### 7.2 Quantifiers

| Pattern | Meaning |
|---|---|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 (optional) |
| `{3}` | exactly 3 |
| `{2,4}` | 2 to 4 |
| `{2,}` | 2 or more |

```python
print(re.findall(r"\d+", "a1 bb22 c333"))         # ['1', '22', '333']
print(re.findall(r"\b\w{4}\b", "this is a test")) # ['this', 'test']
```

### 7.3 Groups and named groups

Parentheses capture. `findall` returns the groups instead of the whole match once
you have any:

```python
print(re.findall(r"(\w+)@(\w+)\.com", "a@x.com b@y.com"))
# [('a', 'x'), ('b', 'y')]
```

Named groups turn a match into something readable:

```python
pattern = r"(?P<level>[A-Z]+) (?P<code>\d{3}): (?P<message>.+)"
match = re.search(pattern, "ERROR 404: not found")
print(match.group("level"))     # ERROR
print(match.groupdict())        # {'level': 'ERROR', 'code': '404', 'message': 'not found'}
print(match.group(0))           # the whole match
```

Use `(?:...)` for a group you need for grouping but do not want captured.

### 7.4 The four functions

```python
text = "id=7 name=ada id=9 name=bo"

re.search(r"id=(\d+)", text)      # first match anywhere, or None
re.match(r"id=(\d+)", text)       # only at the START of the string, or None
re.findall(r"id=(\d+)", text)     # ['7', '9'] — list of strings/tuples
re.finditer(r"id=(\d+)", text)    # lazy iterator of match objects (positions!)
re.sub(r"id=\d+", "id=X", text)   # 'id=X name=ada id=X name=bo'
re.split(r"\s+", text)            # split on a pattern
```

`re.sub` accepts backreferences and a function:

```python
print(re.sub(r"(?P<user>\w+)@\w+\.com", r"\g<user>@redacted", "a@x.com"))
# a@redacted
print(re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "a1 b2"))
# a2 b4
```

Compile a pattern you use in a loop: `pat = re.compile(r"\d+")` then
`pat.findall(line)`. It is clearer and avoids repeated cache lookups.

### 7.5 Greedy versus lazy

Quantifiers are greedy: they take as much as possible and then back off.

```python
html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.+>", html))    # ['<b>bold</b> and <i>italic</i>'] — one huge match
print(re.findall(r"<.+?>", html))   # ['<b>', '</b>', '<i>', '</i>'] — lazy
print(re.findall(r"<[^>]+>", html)) # same, and faster: "not a > " is explicit
```

Add `?` after a quantifier to make it lazy. Better still, describe what you mean
with a negated class (`[^>]+`), which cannot over-match at all.

### 7.6 When regex is the wrong tool

- **HTML/XML** — use an HTML parser. Nesting is not expressible in a regex.
- **JSON/CSV** — use `json` / `csv`. Quoted commas and escapes will defeat you.
- **Email address validation** — the real grammar is thousands of characters
  long. Check for one `@` with something on each side, then send a confirmation
  email. That is what "validation" means in practice.
- **Fixed-format text** — `str.split`, `str.startswith`, slicing and `partition`
  are faster and far more readable. `line.split(",")` beats a regex every time.
- **Anything you cannot read a week later** — a five-line parser with comments
  beats a 200-character regex, always.

Regex earns its place in semi-structured text: log lines, free-form user input,
scraping fields out of prose, bulk find-and-replace. If your pattern grows past
about 60 characters, use `re.VERBOSE` and comment it:

```python
pattern = re.compile(
    r"""
    (?P<ip>\d+\.\d+\.\d+\.\d+)   # client address
    \s+-\s+
    (?P<code>\d{3})              # HTTP status
    """,
    re.VERBOSE,
)
```

---

## 8. `argparse`: real command-line interfaces

Reading `sys.argv` by hand means writing your own help text, your own type
conversion, and your own error messages. `argparse` does all three.

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="report",
        description="Summarise a CSV export.",
    )
    parser.add_argument("source", help="path to the input file")            # positional
    parser.add_argument("-l", "--limit", type=int, default=10,
                        help="rows to show (default: %(default)s)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print debug logging")
    return parser


args = build_parser().parse_args(["data.csv", "--limit", "5", "-v"])
print(args.source, args.limit, args.format, args.verbose)
# data.csv 5 text True
```

Points that matter:

- `type=int` converts and rejects: a bad value exits with status 2 and a usage
  message. `type=Path` works too, as does any one-argument callable.
- `dest` is derived from the long option with dashes turned into underscores:
  `--dry-run` becomes `args.dry_run`.
- `action="store_true"` makes a flag default to `False`.
- `nargs="+"` collects a list; `nargs="?"` makes a positional optional.
- `required=True` on an option when there is no sensible default.
- Passing an explicit list to `parse_args(argv)` is what makes a CLI testable.
  Write `def main(argv: list[str] | None = None)` and call
  `parser.parse_args(argv)`; `None` means "use `sys.argv[1:]`".

### Subcommands

```python
parser = argparse.ArgumentParser(prog="pipeline")
subs = parser.add_subparsers(dest="command", required=True)

run = subs.add_parser("run", help="run the pipeline")
run.add_argument("--limit", type=int, default=100)

report = subs.add_parser("report", help="print a report")
report.add_argument("--format", choices=["text", "json"], default="text")

args = parser.parse_args(["run", "--limit", "5"])
print(args.command, args.limit)        # run 5
```

> **Gotcha:** `parse_args` calls `sys.exit` on bad input, which raises
> `SystemExit`. In tests, assert on that:
> `with pytest.raises(SystemExit): parser.parse_args(["--limit", "abc"])`.
> Also note `parser.error("msg")` is the correct way to reject a combination of
> otherwise-valid arguments; it prints usage and exits 2.

For anything larger, `click` and `typer` are the popular third-party choices, but
`argparse` is in the standard library and handles everything up to a fairly large
tool.

---

## 9. `logging` done right

`print` has four problems: you cannot turn it off without editing code, you
cannot filter it by importance, you cannot route it (file, syslog, stderr), and
it carries no context (time, module, level, traceback).

```python
import logging

logger = logging.getLogger(__name__)      # module-level, named after the module

logger.debug("cache miss for %s", key)    # developer detail
logger.info("processed %d rows", count)   # normal operation
logger.warning("retrying in %.1fs", delay)  # something is off, still working
logger.error("could not write %s", path)  # this operation failed
logger.critical("out of disk, aborting")  # the process cannot continue
logger.exception("import failed")         # like error(), plus the traceback
```

Two rules that separate people who understand logging from people who copy
snippets:

1. **Libraries and modules get a logger and never configure it.**
   `logging.getLogger(__name__)` at module level, no handlers, no
   `basicConfig`. Configuration is the application's job, done once, in `main()`.
2. **Use `%s` placeholders, not f-strings.** `logger.debug("row %s", row)` only
   formats the string if DEBUG is enabled; `logger.debug(f"row {row}")` formats
   it every time, which is real cost in a hot loop and can also raise inside the
   log call.

Configuring at the edge:

```python
def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    ...
```

Output:

```
14:02:11 INFO     report: processed 812 rows
14:02:11 WARNING  report.fetch: retrying in 0.5s
```

Anatomy: a **logger** is what you call; a **handler** decides where records go
(`StreamHandler`, `FileHandler`, `RotatingFileHandler`); a **formatter** decides
what each line looks like; **levels** exist on both loggers and handlers, and a
record must pass both.

> **Gotcha 1:** `basicConfig` does nothing if the root logger already has a
> handler. Calling it twice is silently ignored — pass `force=True` if you must
> reconfigure.
>
> **Gotcha 2:** log records propagate up the name hierarchy
> (`app.fetch.http` -> `app.fetch` -> `app` -> root). Adding a handler to both a
> child and the root gives you every line twice. Set `logger.propagate = False`
> or, better, only configure the root.
>
> **Gotcha 3:** never log secrets. Redact tokens before they reach the logger;
> log files get shipped to third-party services.

`print` remains correct for one thing: the actual output of a command-line tool,
the thing a user pipes into another program. Diagnostics go to logging (stderr);
results go to stdout.

---

## 10. `pathlib`, `os.environ`, `shutil` — the ten-minute refresher

You met `pathlib` on Day 10. The parts that matter today:

```python
from pathlib import Path

here = Path(__file__).parent
data = here / "data" / "input.csv"      # / joins, on every OS
print(data.name, data.stem, data.suffix)      # input.csv input .csv
print(data.exists(), data.is_file())
data.parent.mkdir(parents=True, exist_ok=True)
for path in here.glob("*.py"):
    print(path.name)
print(list(here.rglob("*.csv")))        # recursive
```

Environment variables are how configuration and secrets reach a program:

```python
import os

port = int(os.environ.get("PORT", "8000"))      # default, then convert
token = os.environ.get("API_TOKEN")             # None if unset
if token is None:
    raise RuntimeError("API_TOKEN is required")  # fail loudly at startup
```

`os.environ["MISSING"]` raises `KeyError`; `.get` returns `None`. Values are
always strings, so convert and validate at the boundary, once. Never hardcode a
secret and never commit an `.env` file.

`shutil` is high-level file operations:

```python
import shutil

shutil.copy2(src, dst)          # copy with metadata
shutil.move(src, dst)           # move/rename, across filesystems
shutil.rmtree(directory)        # recursive delete — no undo, be careful
print(shutil.disk_usage("/").free)
print(shutil.which("git"))      # None if not on PATH
```

---

## 11. `dataclasses` + `enum` for modelling

Day 12 gave you dataclasses. Combine them with `enum` and invalid states stop
being representable:

```python
from dataclasses import dataclass, field
from enum import Enum, auto


class Status(Enum):
    OK = "ok"
    FAILED = "failed"
    QUARANTINED = "quarantined"


@dataclass(frozen=True, slots=True)
class Record:
    sensor: str
    value: float
    status: Status = Status.OK
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"value must be >= 0, got {self.value}")


r = Record("s1", 21.5, Status.OK)
print(r)                    # Record(sensor='s1', value=21.5, status=<Status.OK: 'ok'>, ...)
print(r.status.value)       # ok
print(Status("failed"))     # Status.FAILED — parse from a string
print([s.value for s in Status])   # ['ok', 'failed', 'quarantined']
```

Why this beats `status: str`: a typo like `"faild"` is caught at the boundary
instead of silently never matching; the set of valid values is discoverable and
iterable; and comparisons are identity checks rather than string comparisons.

Details worth knowing:

- `frozen=True` makes instances immutable and hashable — safe as dict keys.
- `slots=True` (3.10+) cuts memory and blocks typos on attribute assignment.
- Mutable defaults need `field(default_factory=list)`; a bare `[]` raises
  `ValueError: mutable default` at class creation.
- `__post_init__` is where validation goes.
- `dataclasses.asdict(r)` gives a plain dict for JSON, but enums come out as enum
  members — convert with `.value` yourself.
- `Enum` with `auto()` gives arbitrary integer values; use explicit string values
  whenever the value is serialised.
- `StrEnum` (3.11+) makes members usable directly as strings.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `groupby` without sorting | Duplicate keys, half the data missing | `sorted(items, key=k)` with the same key |
| Keeping `groupby` groups for later | Empty groups | Materialise inside the loop: `list(group)` |
| Reading a missing `defaultdict` key | Phantom entries appear | `.get(key)`, or return `dict(d)` |
| `defaultdict(list())` | `TypeError: first argument must be callable` | Pass the factory: `defaultdict(list)` |
| `d[1:3]` on a deque | `TypeError: sequence index must be integer` | `itertools.islice(d, 1, 3)` |
| Comparing naive and aware datetimes | `TypeError: can't compare offset-naive and offset-aware` | Make everything aware UTC at the boundary |
| `datetime.utcnow()` | Naive datetime holding UTC; deprecated in 3.12 | `datetime.now(timezone.utc)` |
| `timedelta(...).seconds` for a duration | 25 hours reports as 1 hour | `.total_seconds()` |
| `"\d+"` instead of `r"\d+"` | `SyntaxWarning: invalid escape sequence` | Raw strings for every pattern |
| `re.match` when you meant `search` | `None` for matches in the middle | `re.search` |
| Greedy `<.+>` | One match spanning the whole line | `<.+?>` or `<[^>]+>` |
| `print` in library code | Cannot silence, filter or route it | `logging.getLogger(__name__)` |
| `basicConfig` inside a module | Application logging config silently ignored/overridden | Configure only in `main()` |
| f-strings in log calls | Formatting cost even when disabled | `logger.info("x=%s", x)` |
| Mutable dataclass default `[]` | `ValueError: mutable default` | `field(default_factory=list)` |

---

## Mental model

Think of today as a toolbox with six drawers, each replacing code you would
otherwise write badly:

```
        WHAT YOU HAVE                    WHAT TO OPEN
  ------------------------------  ->  --------------------
  "how many of each?"                 collections.Counter
  "group these by X"                  defaultdict(list) (sorted + groupby if streaming)
  "last N things" / queue             collections.deque(maxlen=N)
  "combine/pair/product of streams"   itertools
  "when did this happen?"             datetime, aware, in UTC
  "pull fields out of messy text"     re  (structured text? use a parser)
  "let a human drive my script"       argparse
  "tell me what happened at runtime"  logging
  "shape of my data"                  dataclass + Enum
```

The unifying idea: **push the mess to the boundary**. Parse strings, resolve
time zones, read environment variables, validate arguments once, at the edge —
then work with well-typed objects (dataclasses holding enums and aware
datetimes) everywhere inside. Bugs cluster at boundaries; make the boundary thin
and explicit.

---

## Practice

1. Run the demo — it is long, and each section prints its own expectations:
   ```bash
   python course/week3/day17_standard_library/examples.py
   ```
2. Implement the ten exercises in `exercises.py`. 1–4 are `collections` and
   `itertools`; 5–7 add `datetime` and grouping; 8–9 are regex; 10 combines
   `argparse`, `logging`, `re`, `datetime` and `Counter` in one function.
3. Grade from the course root:
   ```bash
   python check.py day17
   ```
4. Read `solutions.py` afterwards, especially exercise 10 — compare how you
   handled the malformed lines.

---

## Recall check

1. What does `Counter.most_common()` do on ties, and how do you make it deterministic?
2. Why can reading a `defaultdict` key be a bug?
3. Give two things `deque` does better than `list` and one thing it does worse.
4. What must you do to the input before calling `itertools.groupby`, and why?
5. What is the difference between a naive and an aware datetime, and which do you store?
6. Why is `timedelta.seconds` the wrong way to get a duration in seconds?
7. What is the difference between `re.match`, `re.search` and `re.findall`?
8. Why must regex patterns be raw strings?
9. Name two situations where regex is the wrong tool and say what to use instead.
10. Why should a library module never call `logging.basicConfig`?
11. Why `logger.info("x=%s", x)` rather than an f-string?

<details>
<summary>Answers</summary>

1. Ties are broken by first-insertion order, which depends on input order. Sort
   explicitly for determinism:
   `sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))`.
2. Any lookup of a missing key inserts it with a default value, so simply
   inspecting a key changes the dict — breaking `len`, iteration and equality
   assertions later.
3. Better: O(1) `appendleft`/`popleft`, and a `maxlen` bounded buffer that evicts
   automatically. Worse: random access to the middle is O(n) and slicing is
   unsupported.
4. Sort it by the same key function. `groupby` only groups *consecutive* equal
   keys, so unsorted input yields one group per run and repeats keys.
5. Naive has `tzinfo is None` and represents an unspecified zone; aware carries a
   `tzinfo`. Store and compute aware UTC; convert to local only for display.
6. `.seconds` is the seconds-within-the-day component (0–86399); a 25-hour
   duration has `.days == 1` and `.seconds == 3600`. Use `.total_seconds()`.
7. `match` anchors at the start of the string; `search` finds the first match
   anywhere; `findall` returns every match as a list of strings, or of tuples if
   the pattern has groups.
8. Backslash sequences like `\d` and `\b` mean something different in Python
   string literals (`\b` is a backspace); raw strings pass the backslash through
   to the regex engine and avoid escape-sequence warnings and errors.
9. HTML/XML (use a parser — nesting is not regular) and CSV/JSON (use `csv` /
   `json` — quoting and escaping will defeat you). Also fixed-format text, where
   `str.split` is clearer.
10. Logging configuration is a global, application-level decision. A library that
    calls `basicConfig` either does nothing (a handler already exists) or hijacks
    the application's configuration. Get a logger, add no handlers.
11. `%s` formatting is deferred: if that level is disabled, the string is never
    built. An f-string is formatted at the call site every time, costing work in
    hot loops and risking an exception inside a log statement.

</details>
