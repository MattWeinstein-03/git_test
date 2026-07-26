"""Day 18 exercises — testing and tooling.

Two flavours today.

*Implementations* (1-5, 8, 9, 10): write the function. The graded tests probe
edge cases that the docstrings point at without spelling out every case, so read
the failure messages — a good failure message *is* the specification.

*Your own tests* (6-7): `find_median_bugs` and `find_wrap_bugs` are test suites
written as functions. Each receives a candidate implementation and returns a list
describing every problem it found. They are graded by being handed one correct
implementation (you must return an empty list) and several subtly broken ones
(you must catch every one). This is how your test-writing gets graded.

Grade yourself from the course root with:

    python check.py day18
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Callable


def median(values: Sequence[float]) -> float:
    """Return the median of `values` without modifying the input.

    The median is the middle value once sorted; with an even number of values it
    is the mean of the two middle ones. The input is not necessarily sorted, and
    the caller's sequence must be left untouched (so no `values.sort()`).

    Args:
        values: numbers, in any order, at least one.

    Returns:
        The median as a float.

    Raises:
        ValueError: if `values` is empty. The message must contain the word
            "empty".

    Examples:
        >>> median([3, 1, 2])
        2
        >>> median([1, 2, 3, 4])
        2.5
        >>> median([7])
        7
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: median")


def parse_bool(text: str) -> bool:
    """Convert a human-written truth value into a bool.

    True:  "yes", "y", "true", "t", "1", "on"
    False: "no", "n", "false", "f", "0", "off"

    Case and surrounding whitespace are irrelevant: " YES " is True.

    Args:
        text: the string to interpret.

    Returns:
        True or False.

    Raises:
        ValueError: for anything else. The message must contain the offending
            text so the caller can see what was rejected.

    Examples:
        >>> parse_bool("YES")
        True
        >>> parse_bool(" off ")
        False
        >>> parse_bool("maybe")
        Traceback (most recent call last):
        ValueError: cannot parse 'maybe' as a boolean
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: parse_bool")


def rle_encode(text: str) -> str:
    """Run-length encode a string: each run of a character becomes char + count.

    This is the feature the lesson builds with red-green-refactor. Counts are
    written in full, so a run of 12 becomes "12" — which is why the decoder has
    to read digits greedily.

    Args:
        text: any string, possibly empty. Digits in the input are not supported
            and you do not need to handle them.

    Returns:
        The encoded string.

    Examples:
        >>> rle_encode("aaabbc")
        'a3b2c1'
        >>> rle_encode("")
        ''
        >>> rle_encode("a")
        'a1'
        >>> rle_encode("aabaa")
        'a2b1a2'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: rle_encode")


def rle_decode(encoded: str) -> str:
    """Reverse `rle_encode`, so `rle_decode(rle_encode(text)) == text`.

    Each character is followed by a decimal count of one or more digits. Read all
    consecutive digits, not just one, or "a12" decodes as "a" * 1 + "2" instead
    of "a" * 12.

    Args:
        encoded: a string produced by `rle_encode`.

    Returns:
        The original text.

    Raises:
        ValueError: if `encoded` is malformed — a character with no digits after
            it, or a leading digit.

    Examples:
        >>> rle_decode("a3b2c1")
        'aaabbc'
        >>> rle_decode("a12")
        'aaaaaaaaaaaa'
        >>> rle_decode("")
        ''
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: rle_decode")


def print_table(rows: Sequence[tuple[str, Any]]) -> None:
    """Print a two-column table with aligned columns. Returns None.

    Layout, exactly:
      - the label is left-justified to the width of the longest label
      - then two spaces
      - then the value, right-justified to the width of the longest value once
        every value has been converted with `str`
      - one row per line, in the order given, each ended by a newline
      - printing nothing at all for an empty `rows`

    This is the one exercise about output, so it is graded with pytest's `capsys`
    fixture.

    Args:
        rows: (label, value) pairs.

    Examples:
        >>> print_table([("ada", 3), ("bo", 12)])
        ada   3
        bo   12
        >>> print_table([("x", "yes")])
        x  yes
        >>> print_table([])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: print_table")


def find_median_bugs(candidate: Callable[[Sequence[float]], float]) -> list[str]:
    """Test a candidate `median` implementation and describe every fault found.

    You are writing a test suite as a function. Return a list of short strings,
    one per problem found — the exact wording is yours, only the count matters
    (empty means "no problems"). A correct implementation must produce `[]`.

    Your checker MUST detect all of these fault classes, because the grader feeds
    you one broken implementation for each:
      1. returns the lower of the two middle values for even-length input
      2. assumes the input is already sorted
      3. sorts the caller's sequence in place (mutates the argument)
      4. returns something for an empty input instead of raising ValueError
      5. raises the wrong exception type for an empty input
      6. is broken outright and raises on every call

    Your checker must never raise, whatever the candidate does — a test runner
    that crashes on a broken candidate is useless. Wrap calls in try/except.

    Do not check the return *type*: both `2` and `2.0` are acceptable answers for
    a median of 2, so a type check would produce false alarms.

    Args:
        candidate: the implementation to check.

    Returns:
        A list of problem descriptions; empty if the candidate looks correct.

    Examples:
        >>> import statistics
        >>> def good(values):
        ...     if not values:
        ...         raise ValueError("empty")
        ...     return statistics.median(values)
        >>> find_median_bugs(good)
        []
        >>> len(find_median_bugs(lambda values: 0.0)) > 0
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: find_median_bugs")


def find_wrap_bugs(candidate: Callable[[str, int], list[str]]) -> list[str]:
    """Test a candidate `word_wrap` implementation and describe every fault found.

    Same idea as `find_median_bugs`, one level harder because the specification
    (see `word_wrap` below) has more corners. Return a list of problem
    descriptions; `[]` means the candidate passed everything you checked.

    Fault classes you must detect — one broken implementation each:
      1. a returned line is longer than `width` even though it could have been
         broken at a space
      2. words are dropped, duplicated, or reordered
      3. runs of whitespace are not collapsed (a line contains a double space,
         or an empty line appears)
      4. a `width` below 1 does not raise ValueError
      5. the return value is a plain string instead of a list of strings
      6. it raises on every call

    Your checker must never raise, whatever the candidate does.

    Args:
        candidate: the implementation to check.

    Returns:
        A list of problem descriptions; empty if the candidate looks correct.

    Examples:
        >>> find_wrap_bugs(word_wrap)
        []
        >>> len(find_wrap_bugs(lambda text, width: [text])) > 0
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: find_wrap_bugs")


def summarise_file(path: Path) -> dict[str, Any]:
    """Summarise a text file: line count, word count, and the longest line.

    Read the file as UTF-8 text. Lines are split on newlines and the trailing
    newline does not create an extra empty line. Words are whitespace-separated.
    "Longest" means the most characters; on a tie the earliest line wins. Blank
    lines still count as lines.

    Args:
        path: the file to read.

    Returns:
        A dict with exactly the keys "lines", "words" (both int) and "longest"
        (str, the line itself with no trailing newline).

    Raises:
        FileNotFoundError: if the path does not exist — do not catch this.

    Examples:
        >>> from pathlib import Path
        >>> p = Path("example.txt")           # doctest: +SKIP
        >>> summarise_file(p)                 # doctest: +SKIP
        {'lines': 2, 'words': 3, 'longest': 'a b'}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: summarise_file")


def get_setting(name: str, default: str, cast: Callable[[str], Any] = str) -> Any:
    """Read a setting from the process environment, with a default and a cast.

    Look `name` up in `os.environ`. If it is missing, use `default`. Either way,
    pass the string through `cast` before returning it, so callers get an int or
    a bool rather than a string. An empty environment value counts as present.

    If `cast` raises, re-raise as ValueError whose message contains both the
    setting name and the offending value — a bad setting must fail loudly at
    startup, not produce a mysterious `None` three layers deeper.

    Args:
        name: the environment variable name.
        default: the string to use when the variable is unset.
        cast: a one-argument converter, `str` by default.

    Returns:
        The converted value.

    Raises:
        ValueError: if `cast` fails on the value.

    Examples:
        >>> import os
        >>> os.environ["PZH_DOCTEST_LIMIT"] = "42"
        >>> get_setting("PZH_DOCTEST_LIMIT", "10", int)
        42
        >>> get_setting("PZH_DOCTEST_MISSING", "7", int)
        7
        >>> del os.environ["PZH_DOCTEST_LIMIT"]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: get_setting")


def word_wrap(text: str, width: int) -> list[str]:
    """Wrap `text` into lines of at most `width` characters, greedily.

    Rules, in full — this is the specification your `find_wrap_bugs` checks
    other implementations against:
      - split the input on any whitespace, discarding runs of it, so tabs,
        newlines and double spaces all behave like a single space
      - fill each line with as many words as fit, joined by single spaces
      - never split a word: a word longer than `width` gets a line to itself and
        that line is allowed to exceed `width`
      - never emit an empty line; text with no words returns an empty list
      - keep the original word order

    Args:
        text: the text to wrap.
        width: the maximum line length, at least 1.

    Returns:
        A list of lines, no trailing newlines.

    Raises:
        ValueError: if `width` is less than 1.

    Examples:
        >>> word_wrap("the quick brown fox", 10)
        ['the quick', 'brown fox']
        >>> word_wrap("a  b\\n\\nc", 3)
        ['a b', 'c']
        >>> word_wrap("unsplittable", 4)
        ['unsplittable']
        >>> word_wrap("   ", 5)
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: word_wrap")


if __name__ == "__main__":
    print("Run `python check.py day18` from the course root to grade your work.")
