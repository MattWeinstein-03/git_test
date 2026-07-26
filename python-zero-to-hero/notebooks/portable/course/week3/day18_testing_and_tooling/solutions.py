"""Day 18 reference solutions.

Same signatures and docstrings as exercises.py. `# why:` comments mark the
choices that are not obvious. Exercises 6 and 7 are the interesting ones: they
are test suites written as plain functions, which is what a test framework is
underneath.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from itertools import groupby
from pathlib import Path
from typing import Any, Callable

TRUE_WORDS = {"yes", "y", "true", "t", "1", "on"}
FALSE_WORDS = {"no", "n", "false", "f", "0", "off"}


def median(values: Sequence[float]) -> float:
    """Return the median of `values` without modifying the input.

    Examples:
        >>> median([1, 2, 3, 4])
        2.5
    """
    if not values:
        raise ValueError("cannot take the median of an empty sequence")
    # why: sorted() copies, so the caller's list is untouched. values.sort()
    # would mutate an argument, which is the fault class 3 in find_median_bugs.
    ordered = sorted(values)
    count = len(ordered)
    middle = count // 2
    if count % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def parse_bool(text: str) -> bool:
    """Convert a human-written truth value into a bool.

    Examples:
        >>> parse_bool("YES")
        True
    """
    cleaned = text.strip().lower()
    if cleaned in TRUE_WORDS:
        return True
    if cleaned in FALSE_WORDS:
        return False
    # why: include the original text so the caller can see what was rejected;
    # a bare "invalid boolean" costs someone twenty minutes.
    raise ValueError(f"cannot parse {text!r} as a boolean")


def rle_encode(text: str) -> str:
    """Run-length encode a string: each run of a character becomes char + count.

    Examples:
        >>> rle_encode("aaabbc")
        'a3b2c1'
    """
    # why: groupby groups CONSECUTIVE equal items, which is exactly a run. This
    # is the refactored version from the lesson; the loop version passed the same
    # tests, which is what made the rewrite safe.
    return "".join(f"{char}{len(list(group))}" for char, group in groupby(text))


def rle_decode(encoded: str) -> str:
    """Reverse `rle_encode`, so `rle_decode(rle_encode(text)) == text`.

    Examples:
        >>> rle_decode("a12")
        'aaaaaaaaaaaa'
    """
    out: list[str] = []
    index = 0
    while index < len(encoded):
        char = encoded[index]
        if char.isdigit():
            raise ValueError(f"unexpected digit at position {index} in {encoded!r}")
        index += 1
        start = index
        while index < len(encoded) and encoded[index].isdigit():
            index += 1  # why: read ALL the digits, so "a12" means twelve a's
        if start == index:
            raise ValueError(f"missing count after {char!r} in {encoded!r}")
        out.append(char * int(encoded[start:index]))
    return "".join(out)


def print_table(rows: Sequence[tuple[str, Any]]) -> None:
    """Print a two-column table with aligned columns. Returns None.

    Examples:
        >>> print_table([("x", "yes")])
        x  yes
    """
    if not rows:
        return  # why: an empty table prints nothing, not an empty line
    label_width = max(len(label) for label, _ in rows)
    value_width = max(len(str(value)) for _, value in rows)
    for label, value in rows:
        print(f"{label.ljust(label_width)}  {str(value).rjust(value_width)}")


def find_median_bugs(candidate: Callable[[Sequence[float]], float]) -> list[str]:
    """Test a candidate `median` implementation and describe every fault found.

    Examples:
        >>> find_median_bugs(median)
        []
    """
    problems: list[str] = []

    def check(values: Sequence[float], want: float, label: str) -> None:
        """Call the candidate defensively and compare with the expected answer."""
        try:
            got = candidate(list(values))
        except Exception as error:  # noqa: BLE001 - a checker must survive anything
            problems.append(f"{label}: raised {type(error).__name__}: {error}")
            return
        # why: abs tolerance rather than == because medians of even counts divide
        if got is None or abs(got - want) > 1e-9:
            problems.append(f"{label}: got {got!r}, want {want!r}")

    check([7], 7, "single value")
    check([3, 1, 2], 2, "odd count, unsorted")          # catches "assumes sorted"
    check([1, 2, 3, 4], 2.5, "even count")              # catches "lower middle"
    check([4, 3, 2, 1], 2.5, "even count, reversed")
    check([-5, -1, -3], -3, "negative values")
    check([2.5, 1.5], 2.0, "floats")

    # Fault class 3: the caller's sequence must survive the call.
    original = [3, 1, 2]
    copy = list(original)
    try:
        candidate(original)
    except Exception:  # noqa: BLE001 - already reported above
        pass
    if original != copy:
        problems.append(f"mutated its argument: {copy} became {original}")

    # Fault classes 4 and 5: empty input must raise ValueError specifically.
    try:
        result = candidate([])
    except ValueError:
        pass  # correct
    except Exception as error:  # noqa: BLE001
        problems.append(f"empty input raised {type(error).__name__}, want ValueError")
    else:
        problems.append(f"empty input returned {result!r} instead of raising ValueError")

    return problems


def find_wrap_bugs(candidate: Callable[[str, int], list[str]]) -> list[str]:
    """Test a candidate `word_wrap` implementation and describe every fault found.

    Examples:
        >>> find_wrap_bugs(word_wrap)
        []
    """
    problems: list[str] = []

    def call(text: str, width: int, label: str) -> list[str] | None:
        """Call the candidate defensively; report structural faults immediately."""
        try:
            got = candidate(text, width)
        except Exception as error:  # noqa: BLE001 - a checker must survive anything
            problems.append(f"{label}: raised {type(error).__name__}: {error}")
            return None
        # why: fault class 5 - a string is iterable, so every later check would
        # "work" while comparing characters. Catch the wrong type up front.
        if not isinstance(got, list) or not all(isinstance(line, str) for line in got):
            problems.append(f"{label}: expected list[str], got {type(got).__name__}: {got!r}")
            return None
        return got

    cases = [
        ("the quick brown fox", 10, ["the quick", "brown fox"]),
        ("a  b\n\nc", 3, ["a b", "c"]),
        ("unsplittable", 4, ["unsplittable"]),
        ("   ", 5, []),
        ("one two three", 3, ["one", "two", "three"]),
        ("", 5, []),
    ]
    for text, width, want in cases:
        got = call(text, width, f"wrap({text!r}, {width})")
        if got is None:
            continue
        if got != want:
            problems.append(f"wrap({text!r}, {width}): got {got!r}, want {want!r}")

    # Structural laws, checked on a longer sample: they catch bugs the fixed
    # examples above might miss.
    sample = "alpha beta gamma delta epsilon zeta eta theta"
    words = sample.split()
    for width in (6, 10, 20):
        got = call(sample, width, f"wrap(sample, {width})")
        if got is None:
            continue
        if " ".join(got).split() != words:
            problems.append(f"width {width}: words changed: {got!r}")
        for line in got:
            if not line:
                problems.append(f"width {width}: produced an empty line")
            if "  " in line or line != line.strip():
                problems.append(f"width {width}: whitespace not collapsed in {line!r}")
            # a line may only exceed the width when it is a single long word
            if len(line) > width and " " in line:
                problems.append(f"width {width}: line too long: {line!r} ({len(line)} chars)")

    # Fault class 4: an impossible width must be rejected, not guessed at.
    for bad_width in (0, -3):
        try:
            result = candidate("a b", bad_width)
        except ValueError:
            pass  # correct
        except Exception as error:  # noqa: BLE001
            problems.append(f"width {bad_width} raised {type(error).__name__}, want ValueError")
        else:
            problems.append(f"width {bad_width} returned {result!r} instead of raising")

    return problems


def summarise_file(path: Path) -> dict[str, Any]:
    """Summarise a text file: line count, word count, and the longest line.

    Examples:
        >>> summarise_file(Path("nope.txt"))    # doctest: +SKIP
        FileNotFoundError
    """
    # why: read_text lets FileNotFoundError propagate, which is what the spec
    # wants - the caller knows what to do about a missing file, this does not.
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()  # why: no trailing empty line, unlike split("\n")
    longest = ""
    for line in lines:
        if len(line) > len(longest):  # strict > keeps the earliest on a tie
            longest = line
    return {
        "lines": len(lines),
        "words": sum(len(line.split()) for line in lines),
        "longest": longest,
    }


def get_setting(name: str, default: str, cast: Callable[[str], Any] = str) -> Any:
    """Read a setting from the process environment, with a default and a cast.

    Examples:
        >>> get_setting("PZH_DOES_NOT_EXIST", "7", int)
        7
    """
    raw = os.environ.get(name, default)
    try:
        return cast(raw)
    except Exception as error:  # noqa: BLE001 - any cast failure is a config error
        # why: name AND value in the message, because the person reading this log
        # line is looking at a deployment, not at this source file.
        raise ValueError(f"invalid value for {name}: {raw!r} ({error})") from error


def word_wrap(text: str, width: int) -> list[str]:
    """Wrap `text` into lines of at most `width` characters, greedily.

    Examples:
        >>> word_wrap("the quick brown fox", 10)
        ['the quick', 'brown fox']
    """
    if width < 1:
        raise ValueError(f"width must be at least 1, got {width}")

    lines: list[str] = []
    current: list[str] = []
    length = 0
    # why: split() with no argument collapses every run of whitespace, which is
    # most of the specification handled in one call.
    for word in text.split():
        # +1 per existing word for the joining space
        if current and length + len(current) + len(word) > width:
            lines.append(" ".join(current))
            current = []
            length = 0
        current.append(word)
        length += len(word)
    if current:
        lines.append(" ".join(current))
    return lines


if __name__ == "__main__":
    print("Solutions module. Run `python check.py day18` to grade exercises.py.")
