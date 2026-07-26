"""Day 17 exercises — the standard library.

Implement each function. Replace the `raise NotImplementedError(...)` line with
your code. Grade yourself from the course root with:

    python check.py day17

1-5 are collections and itertools, 6-7 are datetime, 8 is regex, 9 is argparse,
and 10 combines regex, datetime, Counter and logging in one function.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Iterable
from datetime import datetime
from typing import Any


def top_words(text: str, limit: int) -> list[tuple[str, int]]:
    """Return the `limit` most frequent words with their counts.

    Rules:
      - split on whitespace
      - lowercase every word
      - strip the characters .,!?;:'" from both ends of each word
      - drop anything that is empty after stripping
      - order by count descending, then by word ascending, so the result is
        deterministic (this is why you cannot just return `Counter.most_common`)

    Args:
        text: raw input text.
        limit: how many (word, count) pairs to return; a limit of 0 returns [].

    Returns:
        A list of (word, count) tuples, longest-running word first.

    Examples:
        >>> top_words("the cat, the dog. THE cat!", 2)
        [('the', 3), ('cat', 2)]
        >>> top_words("b a b a c", 3)
        [('a', 2), ('b', 2), ('c', 1)]
        >>> top_words("anything", 0)
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: top_words")


def group_by_initial(words: Iterable[str]) -> dict[str, list[str]]:
    """Group words by their lowercased first letter.

    Use `collections.defaultdict`, then return a **plain dict** so callers do not
    inherit the defaulting behaviour. Empty strings are skipped. Words keep their
    original spelling and their input order within each group.

    Args:
        words: an iterable of strings.

    Returns:
        A dict mapping first letter -> list of words.

    Examples:
        >>> group_by_initial(["apple", "Avocado", "beet"]) == {
        ...     "a": ["apple", "Avocado"], "b": ["beet"]}
        True
        >>> group_by_initial(["", "x"]) == {"x": ["x"]}
        True
        >>> type(group_by_initial([])).__name__
        'dict'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: group_by_initial")


def last_n_events(events: Iterable[str], limit: int) -> list[str]:
    """Return at most the last `limit` events, using a bounded buffer.

    The input may be an endless stream and may be far larger than memory, so you
    may not call `list()` on it. Use `collections.deque` with `maxlen`: it keeps
    the newest items and evicts the oldest automatically.

    Args:
        events: an iterable of event strings.
        limit: maximum number of events to keep; 0 returns [].

    Returns:
        A list of the most recent events, oldest first.

    Examples:
        >>> last_n_events(["a", "b", "c", "d", "e"], 3)
        ['c', 'd', 'e']
        >>> last_n_events(["a"], 5)
        ['a']
        >>> last_n_events(["a", "b"], 0)
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: last_n_events")


def group_ids_by_status(records: list[dict[str, Any]]) -> dict[str, list[int]]:
    """Group record ids by status using `itertools.groupby`.

    Each record is a dict with "status" (str) and "id" (int). The input is NOT
    sorted, so you must sort by the same key before grouping — that is the point
    of this exercise. Ids inside each group come out in ascending order.

    Args:
        records: the records to group.

    Returns:
        A dict mapping status -> sorted list of ids.

    Examples:
        >>> group_ids_by_status([{"status": "ok", "id": 3},
        ...                      {"status": "fail", "id": 2},
        ...                      {"status": "ok", "id": 1}]) == {
        ...     "fail": [2], "ok": [1, 3]}
        True
        >>> group_ids_by_status([]) == {}
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: group_ids_by_status")


def biggest_swing(readings: list[tuple[str, float]]) -> tuple[str, str, float]:
    """Find the consecutive pair of readings with the largest absolute change.

    Use `itertools.pairwise`. Each reading is a (label, value) tuple. Compare
    only neighbouring readings, in the order given. On a tie, return the earliest
    pair. The delta is signed: later value minus earlier value.

    Args:
        readings: at least two (label, value) tuples.

    Returns:
        (earlier_label, later_label, signed_delta)

    Raises:
        ValueError: if fewer than two readings are given.

    Examples:
        >>> biggest_swing([("t0", 10.0), ("t1", 12.0), ("t2", 4.0)])
        ('t1', 't2', -8.0)
        >>> biggest_swing([("a", 1.0), ("b", 3.0)])
        ('a', 'b', 2.0)
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: biggest_swing")


def parse_timestamp(text: str) -> datetime:
    """Parse an ISO-8601 timestamp into an **aware** datetime in UTC.

    Three input shapes must work:
      - with a Z suffix:      "2024-03-15T13:45:00Z"
      - with an offset:       "2024-03-15T14:45:00+01:00"  (== 13:45 UTC)
      - naive, no zone:       "2024-03-15T13:45:00"  -> assume it is already UTC

    Whatever comes in, the result must be timezone-aware and expressed in UTC,
    so all three examples above return the same instant. Do not use
    `datetime.utcnow()` anywhere.

    Args:
        text: the timestamp string.

    Returns:
        An aware datetime whose tzinfo is UTC.

    Raises:
        ValueError: if the text is not a parseable timestamp (let
            `datetime.fromisoformat` raise this for you).

    Examples:
        >>> parse_timestamp("2024-03-15T13:45:00Z").isoformat()
        '2024-03-15T13:45:00+00:00'
        >>> parse_timestamp("2024-03-15T14:45:00+01:00").isoformat()
        '2024-03-15T13:45:00+00:00'
        >>> parse_timestamp("2024-03-15T13:45:00").isoformat()
        '2024-03-15T13:45:00+00:00'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: parse_timestamp")


def busiest_hour(timestamps: Iterable[str]) -> tuple[int, int]:
    """Return the UTC hour with the most events, and how many that was.

    Parse each timestamp with your `parse_timestamp`, take the UTC hour
    (0-23), and count. Ties are broken by the smaller hour. Timestamps that fail
    to parse are ignored.

    Args:
        timestamps: ISO-8601 strings in any of the three shapes above.

    Returns:
        (hour, count). If nothing parsed, return (-1, 0).

    Examples:
        >>> busiest_hour(["2024-03-15T13:00:00Z", "2024-03-15T13:59:00Z",
        ...               "2024-03-15T09:00:00Z"])
        (13, 2)
        >>> busiest_hour(["2024-03-15T05:00:00Z", "2024-03-15T04:00:00Z"])
        (4, 1)
        >>> busiest_hour(["nonsense"])
        (-1, 0)
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: busiest_hour")


def parse_log_line(line: str) -> dict[str, str] | None:
    """Parse one log line with a regular expression and named groups.

    The expected format is exactly:

        <iso timestamp> <LEVEL> <logger name>: <message>

    for example:

        2024-03-15T13:45:00Z WARNING api.fetch: retrying in 0.5s

    Rules:
      - LEVEL is one or more uppercase letters
      - the logger name is letters, digits, dots and underscores
      - the message is everything after ": " and may contain colons
      - surrounding whitespace is ignored
      - anything that does not match returns None (do not raise)

    Args:
        line: one raw log line.

    Returns:
        A dict with keys "timestamp", "level", "logger", "message", or None.

    Examples:
        >>> parse_log_line("2024-03-15T13:45:00Z WARNING api.fetch: retry: soon") == {
        ...     "timestamp": "2024-03-15T13:45:00Z", "level": "WARNING",
        ...     "logger": "api.fetch", "message": "retry: soon"}
        True
        >>> parse_log_line("garbage") is None
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: parse_log_line")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for a fictional report tool.

    Required interface:
      - program name "report"
      - positional argument `source` (a string, required)
      - `-l` / `--limit`, an int, default 10
      - `--format`, one of "text" or "json", default "text"
      - `-v` / `--verbose`, a boolean flag defaulting to False
      - `--tag`, repeatable (`action="append"`), default an empty list

    Do not call `parse_args()` here — just return the configured parser so it can
    be tested with explicit argument lists.

    Returns:
        The configured ArgumentParser.

    Examples:
        >>> parser = build_parser()
        >>> args = parser.parse_args(["data.csv"])
        >>> args.source, args.limit, args.format, args.verbose, args.tag
        ('data.csv', 10, 'text', False, [])
        >>> vars(parser.parse_args(["d.csv", "-l", "2", "--tag", "x", "-v"]))["tag"]
        ['x']
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: build_parser")


def summarise_log(
    lines: Iterable[str], logger: logging.Logger, limit: int = 3
) -> dict[str, Any]:
    """Turn a stream of log lines into a summary, logging what you could not read.

    For every line:
      - parse it with `parse_log_line`
      - if it does not parse, call `logger.warning("unparseable line: %s", line)`
        with the original line as the single formatting argument, and count it
      - otherwise count the level, and remember the timestamp

    Email addresses in messages must be redacted before they appear in the
    result: replace every address with the string "<redacted>" using `re.sub`.
    An address here is `\\S+@\\S+\\.\\S+` — deliberately loose, because that is
    what redaction needs (see the lesson on why full email validation with regex
    is a mistake).

    Args:
        lines: raw log lines.
        logger: where to report unparseable lines. Do not configure it, and do
            not call `basicConfig`.
        limit: how many recent messages to keep in "recent".

    Returns:
        A dict with exactly these keys:
          "total"     -> int, lines seen
          "bad"       -> int, lines that did not parse
          "levels"    -> dict[str, int], count per level, ordered by count
                         descending then level name ascending
          "busiest"   -> tuple[int, int], from `busiest_hour` over the parsed
                         timestamps
          "recent"    -> list[str], the last `limit` redacted messages, oldest
                         first (use a bounded buffer)

    Examples:
        >>> import logging
        >>> log = logging.getLogger("doctest")
        >>> lines = [
        ...     "2024-03-15T13:00:00Z INFO api: mail a@b.com queued",
        ...     "2024-03-15T13:30:00Z ERROR api: boom",
        ...     "rubbish",
        ... ]
        >>> summary = summarise_log(lines, log, limit=2)
        >>> summary["total"], summary["bad"]
        (3, 1)
        >>> summary["levels"] == {"ERROR": 1, "INFO": 1}
        True
        >>> summary["busiest"]
        (13, 2)
        >>> summary["recent"]
        ['mail <redacted> queued', 'boom']
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: summarise_log")


if __name__ == "__main__":
    print("Run `python check.py day17` from the course root to grade your work.")
