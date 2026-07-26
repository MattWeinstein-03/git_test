"""Day 16 exercises — functional Python and decorators.

Implement each function. Replace the `raise NotImplementedError(...)` line with
your code. Grade yourself from the course root with:

    python check.py day16

1-3 are `key` functions and map/filter, 4-5 are closures and late binding,
6-9 are decorators of increasing sophistication, 10 is composition.
"""

from __future__ import annotations

from typing import Any, Callable


def sort_by_length_then_alpha(words: list[str]) -> list[str]:
    """Sort words by length (shortest first), breaking ties case-insensitively.

    Return a new list; do not modify the input. Use `sorted` with a tuple key.

    Args:
        words: the words to sort.

    Returns:
        A new sorted list containing the same strings.

    Examples:
        >>> sort_by_length_then_alpha(["pear", "fig", "Apple", "kiwi"])
        ['fig', 'kiwi', 'pear', 'Apple']
        >>> sort_by_length_then_alpha(["bb", "BA", "ab"])
        ['ab', 'BA', 'bb']
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: sort_by_length_then_alpha")


def rank_players(players: list[dict[str, Any]]) -> list[str]:
    """Return player names ranked by score descending, then name ascending.

    Each player is a dict with at least the keys "name" (str) and "score"
    (int or float). One `sorted` call with a tuple key does this.

    Args:
        players: player records.

    Returns:
        A list of names, best first.

    Examples:
        >>> rank_players([{"name": "ada", "score": 10},
        ...               {"name": "bo", "score": 30},
        ...               {"name": "cy", "score": 10}])
        ['bo', 'ada', 'cy']
        >>> rank_players([])
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: rank_players")


def parse_and_scale(raw_values: list[str], factor: float) -> list[float]:
    """Convert numeric strings to floats and scale them, dropping unparseable ones.

    Practise map/filter here even though a comprehension is usually nicer: build
    the result with `map` and `filter` (in either order) rather than a `for`
    loop. Whitespace around a number is fine; anything that is not a number is
    dropped silently.

    Args:
        raw_values: strings that may or may not be numbers.
        factor: multiplier applied to every parsed value.

    Returns:
        A list of scaled floats, in input order.

    Examples:
        >>> parse_and_scale([" 1.5 ", "oops", "2"], 2.0)
        [3.0, 4.0]
        >>> parse_and_scale(["", "x"], 10.0)
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: parse_and_scale")


def make_running_average() -> Callable[[float], float]:
    """Return a closure that accepts numbers and returns the running mean.

    The returned callable keeps its own state between calls (use `nonlocal`).
    Two calls to `make_running_average()` must not share state.

    Returns:
        A function taking one number and returning the mean of everything it has
        been given so far.

    Examples:
        >>> avg = make_running_average()
        >>> avg(10)
        10.0
        >>> avg(20)
        15.0
        >>> avg(0)
        10.0
        >>> make_running_average()(4)
        4.0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: make_running_average")


def make_adders(offsets: list[int]) -> list[Callable[[int], int]]:
    """Return one adder function per offset, each capturing its OWN offset.

    This is the late-binding exercise. The naive loop that appends
    `lambda x: x + offset` returns functions that all add the last offset. Fix
    it with a factory function (preferred) or a default argument.

    Args:
        offsets: the numbers to add.

    Returns:
        A list of single-argument functions, same length and order as `offsets`.

    Examples:
        >>> adders = make_adders([1, 10, 100])
        >>> [add(0) for add in adders]
        [1, 10, 100]
        >>> make_adders([5])[0](2)
        7
        >>> make_adders([])
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: make_adders")


def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: count calls and record the duration of the most recent one.

    The returned wrapper must:
      - work for any signature (`*args, **kwargs`)
      - return whatever the wrapped function returns
      - carry `.calls` (int, starts at 0, increments on every call including
        calls that raise)
      - carry `.last_duration` (float, seconds, starts at 0.0, set after every
        call including calls that raise — use `time.perf_counter`)
      - preserve `__name__` and `__doc__` via `functools.wraps`

    Args:
        func: the function to wrap.

    Returns:
        The wrapper function.

    Examples:
        >>> @count_calls
        ... def add(a, b):
        ...     '''Add.'''
        ...     return a + b
        >>> add(1, 2)
        3
        >>> add(b=1, a=2)
        3
        >>> add.calls
        2
        >>> add.__name__
        'add'
        >>> add.last_duration >= 0
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: count_calls")


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: cache results keyed on the positional arguments.

    Requirements:
      - only positional arguments need to be supported as cache keys; the key is
        the `args` tuple itself
      - expose the cache dict as `.cache` on the wrapper so it can be inspected
        and cleared
      - expose `.hits` and `.misses` counters (ints, starting at 0)
      - the wrapped function must be called exactly once per distinct argument
        tuple
      - preserve metadata with `functools.wraps`

    Args:
        func: a pure function of hashable positional arguments.

    Returns:
        The caching wrapper.

    Examples:
        >>> calls = []
        >>> @memoize
        ... def square(n):
        ...     calls.append(n)
        ...     return n * n
        >>> square(4), square(4), square(5)
        (16, 16, 25)
        >>> calls
        [4, 5]
        >>> square.hits, square.misses
        (1, 2)
        >>> sorted(square.cache)
        [(4,), (5,)]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: memoize")


def retry(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: retry a failing call up to `attempts` times.

    Requirements:
      - `retry(0)` and any `attempts` below 1 raise ValueError immediately, when
        the factory is called
      - only exceptions in `exceptions` are retried; anything else propagates on
        the first failure
      - if every attempt fails, re-raise the exception from the LAST attempt
      - the wrapper carries `.attempts_made` (int): how many times the wrapped
        function was called during the most recent call to the wrapper
      - no sleeping: this decorator must return promptly
      - preserve metadata with `functools.wraps`

    Args:
        attempts: maximum number of calls to the wrapped function, at least 1.
        exceptions: the exception types that should trigger a retry.

    Returns:
        A decorator.

    Examples:
        >>> state = {"fails": 2}
        >>> @retry(attempts=3, exceptions=(ValueError,))
        ... def flaky():
        ...     if state["fails"]:
        ...         state["fails"] -= 1
        ...         raise ValueError("later")
        ...     return "ok"
        >>> flaky()
        'ok'
        >>> flaky.attempts_made
        3
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: retry")


def audited(
    sink: list[str], label: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: append one audit line per call to `sink`.

    On success append exactly:      f"{label}:{func.__name__}:ok:{result!r}"
    On failure append exactly:      f"{label}:{func.__name__}:error:{type(exc).__name__}"
    and then re-raise the exception — an audit trail must never swallow errors.

    The wrapper must preserve metadata (`functools.wraps`) and must stack
    cleanly with `count_calls`, which means `func.__name__` has to be the
    original function's name, not "wrapper".

    Args:
        sink: a list the wrapper appends audit lines to.
        label: a short prefix identifying the audit stream.

    Returns:
        A decorator.

    Examples:
        >>> log = []
        >>> @audited(log, "api")
        ... def half(n):
        ...     return n // 2
        >>> half(10)
        5
        >>> log
        ['api:half:ok:5']
        >>> @audited(log, "api")
        ... def boom():
        ...     raise KeyError("nope")
        >>> boom()
        Traceback (most recent call last):
        KeyError: 'nope'
        >>> log[-1]
        'api:boom:error:KeyError'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: audited")


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Return a single function applying `funcs` left to right.

    `compose(f, g, h)(x)` must equal `h(g(f(x)))`. With no arguments, return an
    identity function (returns its argument unchanged). `functools.reduce` is
    the honest use case here, but a small loop is equally acceptable.

    Args:
        *funcs: single-argument callables.

    Returns:
        A single-argument callable.

    Examples:
        >>> clean = compose(str.strip, str.lower)
        >>> clean("  HeLLo  ")
        'hello'
        >>> compose()(42)
        42
        >>> compose(lambda n: n + 1, lambda n: n * 10)(2)
        30
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: compose")


if __name__ == "__main__":
    print("Run `python check.py day16` from the course root to grade your work.")
