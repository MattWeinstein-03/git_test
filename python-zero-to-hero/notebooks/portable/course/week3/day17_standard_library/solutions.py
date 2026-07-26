"""Day 17 reference solutions.

Same signatures and docstrings as exercises.py. `# why:` comments mark the
choices that are not obvious.
"""

from __future__ import annotations

import argparse
import logging
import re
from collections import Counter, defaultdict, deque
from collections.abc import Iterable
from datetime import datetime, timezone
from itertools import groupby, pairwise
from typing import Any

# why: compiled once at import time rather than on every call, and named so the
# pattern can be read on its own.
LOG_LINE_RE = re.compile(
    r"""
    ^\s*
    (?P<timestamp>\S+)             # ISO timestamp, no spaces inside
    \s+
    (?P<level>[A-Z]+)              # WARNING, INFO, ...
    \s+
    (?P<logger>[\w.]+)             # dotted logger name
    :\s
    (?P<message>.*?)               # lazy: let the trailing \s* take the spaces
    \s*$
    """,
    re.VERBOSE,
)

EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
STRIP_CHARS = ".,!?;:'\""


def top_words(text: str, limit: int) -> list[tuple[str, int]]:
    """Return the `limit` most frequent words with their counts.

    Examples:
        >>> top_words("the cat, the dog. THE cat!", 2)
        [('the', 3), ('cat', 2)]
    """
    words = (word.lower().strip(STRIP_CHARS) for word in text.split())
    counts = Counter(word for word in words if word)
    # why: most_common breaks ties by insertion order, which is not reproducible;
    # sorting on (-count, word) is.
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ordered[:limit]


def group_by_initial(words: Iterable[str]) -> dict[str, list[str]]:
    """Group words by their lowercased first letter.

    Examples:
        >>> group_by_initial(["apple", "beet"]) == {"a": ["apple"], "b": ["beet"]}
        True
    """
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        if not word:
            continue
        groups[word[0].lower()].append(word)
    # why: returning a plain dict stops callers relying on missing-key insertion
    return dict(groups)


def last_n_events(events: Iterable[str], limit: int) -> list[str]:
    """Return at most the last `limit` events, using a bounded buffer.

    Examples:
        >>> last_n_events(["a", "b", "c"], 2)
        ['b', 'c']
    """
    # why: deque(maxlen=n) evicts from the left automatically, so memory is
    # bounded no matter how long the stream is.
    buffer: deque[str] = deque(events, maxlen=limit) if limit > 0 else deque()
    return list(buffer)


def group_ids_by_status(records: list[dict[str, Any]]) -> dict[str, list[int]]:
    """Group record ids by status using `itertools.groupby`.

    Examples:
        >>> group_ids_by_status([{"status": "ok", "id": 1}]) == {"ok": [1]}
        True
    """

    def key(record: dict[str, Any]) -> str:
        return str(record["status"])

    # why: groupby only groups CONSECUTIVE equal keys, so sorting by the same key
    # first is mandatory, not an optimisation.
    ordered = sorted(records, key=key)
    return {
        status: sorted(int(record["id"]) for record in group)
        for status, group in groupby(ordered, key=key)
    }


def biggest_swing(readings: list[tuple[str, float]]) -> tuple[str, str, float]:
    """Find the consecutive pair of readings with the largest absolute change.

    Examples:
        >>> biggest_swing([("a", 1.0), ("b", 3.0)])
        ('a', 'b', 2.0)
    """
    if len(readings) < 2:
        raise ValueError(f"need at least two readings, got {len(readings)}")

    best: tuple[str, str, float] | None = None
    for (earlier_label, earlier), (later_label, later) in pairwise(readings):
        delta = later - earlier
        # why: strict > keeps the earliest pair on a tie
        if best is None or abs(delta) > abs(best[2]):
            best = (earlier_label, later_label, delta)
    assert best is not None  # unreachable: len >= 2 guarantees one pair
    return best


def parse_timestamp(text: str) -> datetime:
    """Parse an ISO-8601 timestamp into an **aware** datetime in UTC.

    Examples:
        >>> parse_timestamp("2024-03-15T13:45:00Z").isoformat()
        '2024-03-15T13:45:00+00:00'
    """
    # why: fromisoformat only accepts "Z" from 3.11; normalising keeps this
    # working on 3.10 as well.
    normalised = text.strip().replace("Z", "+00:00").replace("z", "+00:00")
    parsed = datetime.fromisoformat(normalised)
    if parsed.tzinfo is None:
        # why: the spec says naive input means UTC. Attaching the zone is not the
        # same as converting: replace() relabels, astimezone() shifts.
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def busiest_hour(timestamps: Iterable[str]) -> tuple[int, int]:
    """Return the UTC hour with the most events, and how many that was.

    Examples:
        >>> busiest_hour(["2024-03-15T13:00:00Z"])
        (13, 1)
    """
    hours: Counter[int] = Counter()
    for text in timestamps:
        try:
            hours[parse_timestamp(text).hour] += 1
        except ValueError:
            continue  # unparseable timestamps are ignored, per the spec
    if not hours:
        return (-1, 0)
    # why: (-count, hour) makes the smaller hour win a tie, deterministically
    hour, total = min(hours.items(), key=lambda item: (-item[1], item[0]))
    return (hour, total)


def parse_log_line(line: str) -> dict[str, str] | None:
    """Parse one log line with a regular expression and named groups.

    Examples:
        >>> parse_log_line("garbage") is None
        True
    """
    match = LOG_LINE_RE.match(line)
    if match is None:
        return None
    return match.groupdict()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for a fictional report tool.

    Examples:
        >>> build_parser().parse_args(["d.csv"]).limit
        10
    """
    parser = argparse.ArgumentParser(
        prog="report", description="Summarise a CSV export."
    )
    parser.add_argument("source", help="path to the input file")
    parser.add_argument(
        "-l", "--limit", type=int, default=10,
        help="rows to show (default: %(default)s)",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    # why: default=[] with action="append" is safe here because argparse replaces
    # the list rather than mutating the default.
    parser.add_argument("--tag", action="append", default=[], help="repeatable tag")
    return parser


def summarise_log(
    lines: Iterable[str], logger: logging.Logger, limit: int = 3
) -> dict[str, Any]:
    """Turn a stream of log lines into a summary, logging what you could not read.

    Examples:
        >>> summarise_log(["rubbish"], logging.getLogger("x"))["bad"]
        1
    """
    total = 0
    bad = 0
    levels: Counter[str] = Counter()
    stamps: list[str] = []
    recent: deque[str] = deque(maxlen=limit) if limit > 0 else deque()

    for line in lines:
        total += 1
        parsed = parse_log_line(line)
        if parsed is None:
            bad += 1
            # why: %s formatting is deferred, and the logger belongs to the
            # caller — this function never configures logging.
            logger.warning("unparseable line: %s", line)
            continue
        levels[parsed["level"]] += 1
        stamps.append(parsed["timestamp"])
        recent.append(EMAIL_RE.sub("<redacted>", parsed["message"]))

    ordered_levels = dict(
        sorted(levels.items(), key=lambda item: (-item[1], item[0]))
    )
    return {
        "total": total,
        "bad": bad,
        "levels": ordered_levels,
        "busiest": busiest_hour(stamps),
        "recent": list(recent),
    }


if __name__ == "__main__":
    print("Solutions module. Run `python check.py day17` to grade exercises.py.")
