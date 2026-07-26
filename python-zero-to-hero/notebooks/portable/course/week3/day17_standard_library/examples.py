"""Day 17 — runnable tour of the standard library modules you will use daily.

Run it:

    python course/week3/day17_standard_library/examples.py

Sections match LESSON.md. Nothing here touches the network. Section 10 writes
into a tmp/ folder next to this file and deletes it again.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import sys
from collections import Counter, defaultdict, deque, namedtuple
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from itertools import (
    accumulate,
    chain,
    combinations,
    count,
    cycle,
    dropwhile,
    groupby,
    islice,
    pairwise,
    permutations,
    product,
    takewhile,
    zip_longest,
)
from pathlib import Path
from typing import NamedTuple
from zoneinfo import ZoneInfo

TMP = Path(__file__).parent / "tmp"


def banner(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


# ---------------------------------------------------------------------------
banner("1. collections.Counter")
# ---------------------------------------------------------------------------

text = "the quick brown fox jumps over the lazy dog the end"
counts = Counter(text.split())

print("counts['the']   :", counts["the"], "(expected 3)")
print("missing key     :", counts["nope"], "(0, and no KeyError)")
print("most_common(2)  :", counts.most_common(2))
print("total counted   :", sum(counts.values()), "(expected 11)")
print("distinct words  :", len(counts), "(expected 9)")

letters = Counter("mississippi")
print("letters top 3   :", letters.most_common(3))

# Ties are broken by insertion order, which is rarely what you want in a report.
print("tie order       :", Counter("ba").most_common(), "(insertion order, not alphabetical)")
deterministic = sorted(letters.items(), key=lambda kv: (-kv[1], kv[0]))
print("deterministic   :", deterministic[:3], "(count desc, then letter asc)")

# Counters support arithmetic, which makes stock/diff calculations one-liners.
stock = Counter(apple=3, pear=1)
sold = Counter(apple=1)
print("stock - sold    :", stock - sold)
print("intersection &  :", Counter("aab") & Counter("abb"), "(per-key minimum)")
print("union |         :", Counter("aab") | Counter("abb"), "(per-key maximum)")


# ---------------------------------------------------------------------------
banner("2. collections.defaultdict")
# ---------------------------------------------------------------------------

words = ["apple", "avocado", "beet", "blueberry", "cherry"]

# The plain-dict version needs a guard on every insert.
manual: dict[str, list[str]] = {}
for word in words:
    if word[0] not in manual:
        manual[word[0]] = []
    manual[word[0]].append(word)

groups: defaultdict[str, list[str]] = defaultdict(list)
for word in words:
    groups[word[0]].append(word)          # no guard needed

print("manual dict     :", manual)
print("defaultdict     :", dict(groups))
print("same?           :", manual == dict(groups))

# Counting with defaultdict(int) is the pre-Counter idiom; Counter is better.
tally: defaultdict[str, int] = defaultdict(int)
for char in "banana":
    tally[char] += 1
print("defaultdict(int):", dict(tally))

# The gotcha: reading a missing key CREATES it.
print("len before read :", len(groups))
_ = groups["z"]                            # a read, not a write... apparently
print("len after read  :", len(groups), "<- a phantom 'z': []", dict(groups)["z"])
print("safe lookup     :", groups.get("q"), "(get() does not insert)")


# ---------------------------------------------------------------------------
banner("3. collections.deque")
# ---------------------------------------------------------------------------

queue = deque(["a", "b", "c"])
queue.append("d")
queue.appendleft("z")
print("deque           :", queue)
print("popleft()       :", queue.popleft(), "-> O(1); list.pop(0) is O(n)")
print("pop()           :", queue.pop())

# maxlen gives you a bounded ring buffer for free: "the last 3 events".
recent: deque[str] = deque(maxlen=3)
for event in ["a", "b", "c", "d", "e"]:
    recent.append(event)
print("last 3 of 5     :", list(recent), "(expected ['c', 'd', 'e'])")

queue.rotate(1)
print("rotate(1)       :", queue)
try:
    recent[0:2]                            # slicing is not supported
except TypeError as error:
    print("slicing a deque : TypeError:", error)


# ---------------------------------------------------------------------------
banner("4. namedtuple and typing.NamedTuple")
# ---------------------------------------------------------------------------

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print("point           :", p)
print("by name / index :", p.x, p[0])
print("_replace        :", p._replace(x=10), "(a new tuple; originals are immutable)")
print("_asdict         :", p._asdict())
x, y = p
print("unpacked        :", x, y)


class Reading(NamedTuple):
    """The modern spelling: same tuple, with type hints and defaults."""

    sensor: str
    value: float
    ok: bool = True


r = Reading("s1", 21.5)
print("typed namedtuple:", r, "-> ok defaulted to", r.ok)
print("comparable      :", Reading("s1", 21.5) == r, "(value equality, like tuples)")


# ---------------------------------------------------------------------------
banner("5. itertools")
# ---------------------------------------------------------------------------

print("chain           :", list(chain([1, 2], (3,), "ab")))
print("chain.from_iter :", list(chain.from_iterable([[1, 2], [3]])))
print("product         :", list(product([1, 2], "ab")))
print("product repeat=2:", list(product([0, 1], repeat=2)))
print("combinations    :", list(combinations("abc", 2)), "(order irrelevant)")
print("permutations    :", list(permutations("abc", 2))[:3], "... (order matters)")
print("pairwise        :", list(pairwise([10, 13, 20])), "(3.10+)")
print("cycle + islice  :", list(islice(cycle("ab"), 5)))
print("count + islice  :", list(islice(count(10, 5), 3)))
print("accumulate      :", list(accumulate([1, 2, 3, 4])))
print("takewhile       :", list(takewhile(lambda n: n < 3, [1, 2, 9, 1])), "(stops at 9)")
print("dropwhile       :", list(dropwhile(lambda n: n < 3, [1, 2, 9, 1])))
print("zip_longest     :", list(zip_longest("ab", [1], fillvalue="?")))

# groupby: THE trap. Unsorted input gives you one group per consecutive run.
records = [
    {"status": "ok", "id": 1},
    {"status": "fail", "id": 2},
    {"status": "ok", "id": 3},
]


def by_status(record: dict[str, object]) -> str:
    return str(record["status"])


print("unsorted groupby:", [(k, [r["id"] for r in g]) for k, g in groupby(records, by_status)])
print("   ^ three groups, and 'ok' appears twice. Almost never what you wanted.")

ordered = sorted(records, key=by_status)
print("sorted groupby  :", [(k, [r["id"] for r in g]) for k, g in groupby(ordered, by_status)])

# Second trap: groups are lazy views that expire when you move to the next one.
stale = list(groupby(ordered, by_status))
print("kept for later  :", [(k, list(g)) for k, g in stale], "<- all groups empty")
print("materialise now :", {k: [r['id'] for r in g] for k, g in groupby(ordered, by_status)})

# For plain grouping of in-memory data, defaultdict is clearer than sort+groupby.
simple: defaultdict[str, list[int]] = defaultdict(list)
for record in records:
    simple[str(record["status"])].append(int(record["id"]))
print("defaultdict way :", dict(simple), "(no sorting required)")


# ---------------------------------------------------------------------------
banner("6. datetime: naive vs aware, ISO, timedelta")
# ---------------------------------------------------------------------------

print("date            :", date(2024, 3, 15))
print("datetime        :", datetime(2024, 3, 15, 13, 45, 30))

naive = datetime(2024, 3, 15, 13, 45)
aware = datetime(2024, 3, 15, 13, 45, tzinfo=timezone.utc)
print("naive tzinfo    :", naive.tzinfo, "<- 13:45 somewhere. A bug in waiting.")
print("aware tzinfo    :", aware.tzinfo)

try:
    _ = naive < aware
except TypeError as error:
    print("naive < aware   : TypeError:", error)

# Store UTC, convert only to display.
instant = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
london = instant.astimezone(ZoneInfo("Europe/London"))
tokyo = instant.astimezone(ZoneInfo("Asia/Tokyo"))
print("same instant UTC:", instant.isoformat())
print("   in London    :", london.isoformat(), "(BST = UTC+1 in June)")
print("   in Tokyo     :", tokyo.isoformat())
print("still equal?    :", instant == london, "(same moment, different wall clocks)")

parsed = datetime.fromisoformat("2024-03-15T13:45:00+00:00")
print("fromisoformat   :", parsed, "->", parsed.isoformat())
print("strftime        :", parsed.strftime("%Y-%m-%d %H:%M"), "|", parsed.strftime("%A %d %b"))
print("strptime        :", datetime.strptime("15/03/2024", "%d/%m/%Y"))

# A 'Z' suffix is only accepted by fromisoformat from 3.11; normalise it yourself.
raw = "2024-03-15T13:45:00Z"
print("Z normalised    :", datetime.fromisoformat(raw.replace("Z", "+00:00")).isoformat())

start = datetime(2024, 3, 15, 9, 0, tzinfo=timezone.utc)
end = datetime(2024, 3, 15, 17, 30, tzinfo=timezone.utc)
worked = end - start
print("duration        :", worked, "->", worked.total_seconds() / 3600, "hours")
print("tomorrow -2h    :", (start + timedelta(days=1, hours=-2)).isoformat())
print("over 8 hours?   :", worked > timedelta(hours=8))

long_gap = timedelta(hours=25)
print("25h .seconds    :", long_gap.seconds, "<- WRONG for a duration (day component split off)")
print("25h .total_secs :", long_gap.total_seconds(), "-> hours:", long_gap.total_seconds() / 3600)


# ---------------------------------------------------------------------------
banner("7. re: regular expressions")
# ---------------------------------------------------------------------------

print("search 'cat'    :", re.search(r"cat", "concatenate").span())
print("findall digits  :", re.findall(r"\d+", "a1 bb22 c333"))
print("4-letter words  :", re.findall(r"\b\w{4}\b", "this is a test"))
print("groups          :", re.findall(r"(\w+)@(\w+)\.com", "a@x.com b@y.com"))

log_pattern = re.compile(r"(?P<level>[A-Z]+) (?P<code>\d{3}): (?P<message>.+)")
match = log_pattern.search("ERROR 404: not found")
print("named group     :", match.group("level"), match.group("code"))
print("groupdict       :", match.groupdict())
print("group(0)        :", match.group(0), "(the whole match)")

sample = "id=7 name=ada id=9 name=bo"
print("search          :", re.search(r"id=(\d+)", sample).group(1), "(first, anywhere)")
print("match           :", re.match(r"name=", sample), "(None: not at position 0)")
print("findall         :", re.findall(r"id=(\d+)", sample))
print("finditer spans  :", [m.span() for m in re.finditer(r"id=\d+", sample)])
print("sub             :", re.sub(r"id=\d+", "id=X", sample))
print("split           :", re.split(r"\s+", "a  b   c"))

print("backreference   :", re.sub(r"(?P<user>\w+)@\w+\.com", r"\g<user>@redacted", "a@x.com"))
print("sub w/ function :", re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "a1 b2"))

html = "<b>bold</b> and <i>italic</i>"
print("greedy <.+>     :", re.findall(r"<.+>", html), "<- one huge match")
print("lazy   <.+?>    :", re.findall(r"<.+?>", html))
print("explicit <[^>]+>:", re.findall(r"<[^>]+>", html), "(clearest and fastest)")

verbose = re.compile(
    r"""
    (?P<ip>\d+\.\d+\.\d+\.\d+)   # client address
    \s+-\s+
    (?P<code>\d{3})              # HTTP status
    """,
    re.VERBOSE,
)
print("re.VERBOSE      :", verbose.search("10.0.0.7 - 503 ...").groupdict())

# When NOT to use regex: fixed-format text splits faster and reads better.
line = "s1,temp,21.5"
print("regex parse     :", re.match(r"(\w+),(\w+),([\d.]+)", line).groups())
print("split parse     :", tuple(line.split(",")), "<- prefer this")


# ---------------------------------------------------------------------------
banner("8. argparse")
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="report", description="Summarise a CSV export.")
    parser.add_argument("source", help="path to the input file")
    parser.add_argument("-l", "--limit", type=int, default=10,
                        help="rows to show (default: %(default)s)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    parser.add_argument("--tag", action="append", default=[], help="repeatable")
    return parser


parser = build_parser()
args = parser.parse_args(["data.csv", "--limit", "5", "-v", "--tag", "a", "--tag", "b"])
print("parsed          :", vars(args))
print("defaults        :", vars(parser.parse_args(["only.csv"])))

# Bad input exits the process. In tests, catch SystemExit.
try:
    parser.parse_args(["data.csv", "--limit", "abc"])
except SystemExit as error:
    print("bad --limit     : SystemExit code", error.code, "(argparse printed usage to stderr)")

# Subcommands: one parser per verb.
top = argparse.ArgumentParser(prog="pipeline")
subs = top.add_subparsers(dest="command", required=True)
run_cmd = subs.add_parser("run", help="run the pipeline")
run_cmd.add_argument("--limit", type=int, default=100)
report_cmd = subs.add_parser("report", help="print a report")
report_cmd.add_argument("--format", choices=["text", "json"], default="text")

print("subcommand run  :", vars(top.parse_args(["run", "--limit", "5"])))
print("subcommand rpt  :", vars(top.parse_args(["report", "--format", "json"])))
print("help text (run) :", run_cmd.format_usage().strip())


# ---------------------------------------------------------------------------
banner("9. logging")
# ---------------------------------------------------------------------------

# Application-level configuration, done ONCE, at the edge. Library modules only
# ever call getLogger(__name__). stdout here so it interleaves with print().
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("   %(levelname)-8s %(name)s: %(message)s"))
logging.basicConfig(level=logging.DEBUG, handlers=[handler], force=True)

logger = logging.getLogger("day17.demo")
logger.debug("cache miss for key=%s", "abc")
logger.info("processed %d rows", 812)
logger.warning("retrying in %.1fs", 0.5)
logger.error("could not write %s", "/tmp/out.csv")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("arithmetic failed")     # error() plus the traceback

print("   ^ five levels. Raising the level filters the noisy ones out:")
logging.getLogger("day17.demo").setLevel(logging.WARNING)
logger.debug("you will not see this")
logger.info("nor this")
logger.warning("but you will see this")

# Deferred formatting: the %s arguments are only rendered if the level is on.
logger.setLevel(logging.INFO)


class Expensive:
    def __str__(self) -> str:
        print("   [Expensive.__str__ ran]")
        return "expensive"


logger.debug("never formatted: %s", Expensive())   # __str__ not called
logger.info("formatted now: %s", Expensive())      # __str__ called

# A handler that collects records is how you test logging without reading files.
records: list[logging.LogRecord] = []


class ListHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        records.append(record)


captured = logging.getLogger("day17.captured")
captured.setLevel(logging.INFO)
captured.addHandler(ListHandler())
captured.propagate = False                # otherwise the root prints it as well
captured.info("row %d done", 7)
captured.warning("disk at %d%%", 91)
print("captured levels :", [(r.levelname, r.getMessage()) for r in records])

logging.disable(logging.CRITICAL)          # quiet for the rest of the script


# ---------------------------------------------------------------------------
banner("10. pathlib, os.environ, shutil")
# ---------------------------------------------------------------------------

TMP.mkdir(exist_ok=True)
data_file = TMP / "input.csv"
data_file.write_text("a,b\n1,2\n", encoding="utf-8")

print("path joining    :", (TMP / "sub" / "f.txt").as_posix())
print("name/stem/suffix:", data_file.name, "|", data_file.stem, "|", data_file.suffix)
print("exists/is_file  :", data_file.exists(), data_file.is_file())
print("read back       :", data_file.read_text(encoding="utf-8").splitlines())
print("glob *.csv      :", [p.name for p in TMP.glob("*.csv")])

# Environment variables: strings only, always converted and validated at the edge.
os.environ["PZH_DEMO_PORT"] = "8080"
port = int(os.environ.get("PZH_DEMO_PORT", "8000"))
print("PORT (set)      :", port, type(port).__name__)
print("PORT (unset)    :", int(os.environ.get("PZH_DEMO_MISSING", "8000")), "(default used)")
print("secret absent   :", os.environ.get("PZH_DEMO_TOKEN"), "(None, so fail loudly at startup)")
try:
    os.environ["PZH_DEMO_MISSING"]
except KeyError as error:
    print("direct index    : KeyError", error)
del os.environ["PZH_DEMO_PORT"]

copied = shutil.copy2(data_file, TMP / "copy.csv")
print("shutil.copy2    :", Path(copied).name)
print("shutil.which    :", "python found:", shutil.which(sys.executable) is not None)
print("disk free (GB)  :", round(shutil.disk_usage(TMP).free / 1e9, 1))


# ---------------------------------------------------------------------------
banner("11. dataclasses + enum for modelling")
# ---------------------------------------------------------------------------


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


record = Record("s1", 21.5, Status.OK, ("indoor",))
print("record          :", record)
print("status value    :", record.status.value)
print("parse from str  :", Status("failed"), "| all:", [s.value for s in Status])

try:
    Status("faild")                       # a typo is caught at the boundary
except ValueError as error:
    print("bad status      : ValueError:", error)

try:
    Record("s2", -1.0)
except ValueError as error:
    print("validation      : ValueError:", error)

try:
    record.value = 99                     # frozen=True
except Exception as error:
    print("frozen          :", type(error).__name__ + ":", error)

print("hashable        :", {record: "usable as a dict key"}[record])


@dataclass
class Batch:
    name: str
    records: list[Record] = field(default_factory=list)   # never `= []`


batch = Batch("morning")
batch.records.append(record)
print("default_factory :", batch.name, "holds", len(batch.records), "record(s)")

# Clean up: leave nothing behind.
shutil.rmtree(TMP)
print()
print("removed tmp/    :", not TMP.exists())
print("Done. Now open exercises.py in this folder.")
