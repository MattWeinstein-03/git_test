"""Day 09 exercises — Errors and debugging.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

Grade your work from the course root:

    python check.py day09
    python check.py day09 -v      # show full failure detail
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# GIVEN TO YOU — the custom exception classes these exercises raise.
# `class` is Day 12's topic; you only need to know that these three lines
# create a new exception type with a name and a docstring.
# ---------------------------------------------------------------------------


class AppError(Exception):
    """Base class for every error these exercises raise on purpose."""


class InvalidAgeError(AppError):
    """Raised when an age value fails validation."""


class ScoreError(AppError):
    """Raised when a score cannot be normalised."""


class ConfigError(AppError):
    """Raised when a configuration line cannot be parsed."""


# ---------------------------------------------------------------------------
# Exercise 1 — catch one specific exception
# ---------------------------------------------------------------------------
def safe_int(text: str, default: int = 0) -> int:
    """Convert `text` to an int, returning `default` when that is impossible.

    Only handle the failure that `int()` actually produces for junk text.
    Surrounding whitespace is fine — `int(" 7 ")` already works.

    Args:
        text: the string to convert.
        default: what to return when conversion fails. Defaults to 0.

    Returns:
        The parsed int, or `default`.

    Examples:
        safe_int("42") -> 42
        safe_int(" 7 ") -> 7
        safe_int("n/a") -> 0
        safe_int("n/a", -1) -> -1
        safe_int("3.5") -> 0          # int() rejects a decimal point
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: safe_int")


# ---------------------------------------------------------------------------
# Exercise 2 — an exception as an expected outcome
# ---------------------------------------------------------------------------
def safe_divide(
    numerator: float, denominator: float, fallback: float | None = None
) -> float | None:
    """Divide `numerator` by `denominator`, returning `fallback` on a zero divisor.

    Catch only ZeroDivisionError. Any other problem (for example dividing a
    string) must be allowed to propagate — that is a bug in the caller, not an
    expected outcome.

    Args:
        numerator: the value to divide.
        denominator: the value to divide by.
        fallback: what to return when `denominator` is 0. Defaults to None.

    Returns:
        The quotient as a float, or `fallback`.

    Examples:
        safe_divide(10, 4) -> 2.5
        safe_divide(10, 0) -> None
        safe_divide(10, 0, 0.0) -> 0.0
        safe_divide("10", 2) -> raises TypeError (do NOT catch this)
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: safe_divide")


# ---------------------------------------------------------------------------
# Exercise 3 — EAFP through nested data
# ---------------------------------------------------------------------------
def get_nested(data: dict, keys: list[str], default: object = None) -> object:
    """Follow `keys` down through nested dicts and return what you find.

    Use EAFP: try the lookups and catch the failures. Three things can go
    wrong and all three mean "not there" — a missing key (KeyError), hitting a
    value that is not a dict at all, e.g. an int (TypeError), and a value that
    is a list indexed by a string (also TypeError).

    Args:
        data: a dict, possibly containing further dicts.
        keys: the chain of keys to follow, outermost first.
        default: what to return when the chain cannot be followed.

    Returns:
        The value at the end of the chain, or `default`.

    Examples:
        data = {"user": {"address": {"city": "Lagos"}}, "count": 3}
        get_nested(data, ["user", "address", "city"]) -> "Lagos"
        get_nested(data, ["user", "email"]) -> None
        get_nested(data, ["user", "email"], "unknown") -> "unknown"
        get_nested(data, ["count", "city"]) -> None    # 3 is not a dict
        get_nested(data, []) -> {"user": ..., "count": 3}   # empty chain, all of it
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: get_nested")


# ---------------------------------------------------------------------------
# Exercise 4 — collect failures instead of crashing
# ---------------------------------------------------------------------------
def parse_numbers(raw_values: list[str]) -> tuple[list[float], list[str]]:
    """Parse every string in `raw_values` as a float, reporting the failures.

    Never crash on a bad value: skip it and record a message. Each message must
    be exactly f"{value!r} is not a number" (note the !r, so strings appear
    with their quotes).

    Args:
        raw_values: strings that are supposed to hold numbers.

    Returns:
        A 2-tuple (numbers, problems):
            numbers  - the successfully parsed floats, in order
            problems - one message per failed value, in order

    Examples:
        parse_numbers(["1", "2.5"]) -> ([1.0, 2.5], [])
        parse_numbers(["1", "n/a", "3"]) -> ([1.0, 3.0], ["'n/a' is not a number"])
        parse_numbers([]) -> ([], [])
        parse_numbers(["", "-4"]) -> ([-4.0], ["'' is not a number"])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: parse_numbers")


# ---------------------------------------------------------------------------
# Exercise 5 — raise your own exception with a useful message
# ---------------------------------------------------------------------------
def validate_age(value: object) -> int:
    """Return `value` unchanged if it is a plausible age, else raise.

    Raise `InvalidAgeError` (given at the top of this file) with these exact
    messages:
        not a whole number -> f"age must be a whole number, got {type(value).__name__}"
        negative           -> f"age must not be negative, got {value}"
        over 130           -> f"age {value} is implausible"

    A bool is not an acceptable age even though Python treats True as 1, so
    reject bools too.

    Args:
        value: anything at all — this is a boundary check.

    Returns:
        The age as an int.

    Raises:
        InvalidAgeError: when `value` is not a whole number 0-130.

    Examples:
        validate_age(30) -> 30
        validate_age(0) -> 0
        validate_age(-4) -> raises InvalidAgeError("age must not be negative, got -4")
        validate_age("forty") -> raises InvalidAgeError("age must be a whole number, got str")
        validate_age(True) -> raises InvalidAgeError("age must be a whole number, got bool")
        validate_age(999) -> raises InvalidAgeError("age 999 is implausible")
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: validate_age")


# ---------------------------------------------------------------------------
# Exercise 6 — prove you know the execution order of try/except/else/finally
# ---------------------------------------------------------------------------
def traced_divide(numerator: float, denominator: float) -> tuple[float | None, list[str]]:
    """Divide, and return a log of which parts of the try statement ran.

    Build the log with these exact strings, appended in the order they happen:
        "try"                        - first thing, always
        "else"                       - the division succeeded
        "except ZeroDivisionError"   - the divisor was 0
        "except TypeError"           - the operands were not numbers
        "finally"                    - last thing, always

    Args:
        numerator: the value to divide.
        denominator: the value to divide by.

    Returns:
        A 2-tuple (result, log). `result` is the quotient, or None if the
        division failed.

    Examples:
        traced_divide(10, 4) -> (2.5, ["try", "else", "finally"])
        traced_divide(1, 0) -> (None, ["try", "except ZeroDivisionError", "finally"])
        traced_divide("a", 2) -> (None, ["try", "except TypeError", "finally"])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: traced_divide")


# ---------------------------------------------------------------------------
# Exercise 7 — read a traceback with code
# ---------------------------------------------------------------------------
def read_last_frame(traceback_text: str) -> tuple[str, int, str]:
    """Pull the crash site out of a traceback, the way your eyes do.

    A traceback's frames look like:

        File "/home/you/reports/report.py", line 11, in line_revenue

    You want the LAST such line (the innermost frame, nearest the crash) and
    the final non-blank line of the whole text (the exception line).

    Ignore any "^^^^" caret lines and any source lines. Use string methods
    only — no regular expressions (that is Day 17).

    Args:
        traceback_text: the full text Python printed, newlines included.

    Returns:
        A 3-tuple (filename, line_number, exception_line):
            filename        - the path inside the quotes, e.g. "report.py"
            line_number     - the int after "line "
            exception_line  - the last non-blank line, stripped, e.g.
                              "ValueError: invalid literal for int() ..."

    Raises:
        ValueError: when the text contains no frame lines at all, with the
            message "no frames found".

    Examples:
        text = '''Traceback (most recent call last):
          File "app.py", line 27, in <module>
            main()
          File "app.py", line 11, in line_revenue
            units = int(row["units"])
                    ^^^^^^^^^^^^^^^^^
        ValueError: invalid literal for int() with base 10: 'n/a'
        '''
        read_last_frame(text) ->
            ("app.py", 11, "ValueError: invalid literal for int() with base 10: 'n/a'")

        read_last_frame("KeyError: 'b'") -> raises ValueError("no frames found")
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: read_last_frame")


# ---------------------------------------------------------------------------
# Exercise 8 — translate a low-level failure, keeping the cause
# ---------------------------------------------------------------------------
def normalize_scores(raw: dict[str, str]) -> dict[str, int]:
    """Convert a dict of name -> score-as-text into name -> score-as-int.

    Two kinds of bad data, handled differently:

    * A value that is not a whole number: catch the ValueError that int()
      raises and translate it with
          raise ScoreError(f"bad score for {name!r}: {value!r}") from error
      so the original ValueError survives as `__cause__`.
    * A number outside 0-100: raise ScoreError yourself with
          f"score for {name!r} out of range: {number}"
      There is no underlying exception here, so there is nothing to chain.

    Stop at the first bad value — this function either returns a fully valid
    dict or raises.

    Args:
        raw: mapping of name to score text.

    Returns:
        A new dict mapping each name to its int score.

    Raises:
        ScoreError: on any unusable value.

    Examples:
        normalize_scores({"ada": "90", "grace": "100"}) -> {"ada": 90, "grace": 100}
        normalize_scores({}) -> {}
        normalize_scores({"ada": "ninety"}) -> raises ScoreError, __cause__ is ValueError
        normalize_scores({"ada": "150"}) -> raises ScoreError, __cause__ is None
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: normalize_scores")


# ---------------------------------------------------------------------------
# Exercise 9 — the hard one: a forgiving parser that reports everything
# ---------------------------------------------------------------------------
def parse_config(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """Parse "key = value" configuration lines, collecting every problem.

    Rules, applied per line (line numbers are 1-based and count every line,
    including the ones you skip):

    * Skip blank or whitespace-only lines.
    * Skip comment lines: the first non-space character is "#".
    * Split on the FIRST "=" only, so "motto = a = b" gives the value "a = b".
    * Strip whitespace from both the key and the value.
    * Lowercase the key, so "DEBUG" and "debug" are the same setting.

    Problems to report (and skip the line):
        no "="        -> f"line {n}: missing '=' in {line!r}"
        empty key     -> f"line {n}: empty key in {line!r}"
        repeated key  -> f"line {n}: duplicate key {key!r}"
    An empty value is allowed: "name =" gives "".

    Hint: write a small helper that raises `ConfigError` for a bad line and
    catch it in the loop. That keeps the validation rules in one place, which
    is the whole point of exceptions.

    Args:
        lines: the raw lines of a config file, without needing "\\n" stripped.

    Returns:
        A 2-tuple (settings, problems) — the parsed settings dict and one
        message per rejected line, in line order.

    Examples:
        parse_config(["debug = true", "# a comment", "", "name=ada"]) ->
            ({"debug": "true", "name": "ada"}, [])

        parse_config(["oops", "DEBUG=1", "debug=0"]) ->
            ({"debug": "1"},
             ["line 1: missing '=' in 'oops'", "line 3: duplicate key 'debug'"])

        parse_config(["  = 5", "motto = a = b"]) ->
            ({"motto": "a = b"}, ["line 1: empty key in '  = 5'"])

        parse_config([]) -> ({}, [])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: parse_config")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(safe_int("n/a", -1))
    # print(parse_numbers(["1", "n/a", "3"]))
    # print(parse_config(["oops", "DEBUG=1", "debug=0"]))
    print("Run `python check.py day09` from the course root to grade your work.")
