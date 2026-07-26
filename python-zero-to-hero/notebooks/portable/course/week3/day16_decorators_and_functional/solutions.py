"""Day 16 reference solutions.

Same signatures and docstrings as exercises.py. `# why:` comments mark the
choices that are not obvious.
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable


def sort_by_length_then_alpha(words: list[str]) -> list[str]:
    """Sort words by length (shortest first), breaking ties case-insensitively.

    Examples:
        >>> sort_by_length_then_alpha(["pear", "fig", "Apple", "kiwi"])
        ['fig', 'kiwi', 'pear', 'Apple']
    """
    # why: a tuple key sorts by the first element, then the second on ties.
    return sorted(words, key=lambda word: (len(word), word.lower()))


def rank_players(players: list[dict[str, Any]]) -> list[str]:
    """Return player names ranked by score descending, then name ascending.

    Examples:
        >>> rank_players([{"name": "bo", "score": 30}])
        ['bo']
    """
    # why: negating the score reverses only that field; reverse=True would also
    # reverse the name tie-break, which is not what the spec asks for.
    ordered = sorted(players, key=lambda player: (-player["score"], player["name"]))
    return [player["name"] for player in ordered]


def _try_float(text: str) -> float | None:
    """Return the float value of `text`, or None when it is not a number."""
    try:
        return float(text)
    except ValueError:
        return None


def parse_and_scale(raw_values: list[str], factor: float) -> list[float]:
    """Convert numeric strings to floats and scale them, dropping unparseable ones.

    Examples:
        >>> parse_and_scale([" 1.5 ", "oops", "2"], 2.0)
        [3.0, 4.0]
    """
    # why: parse once, then filter out the failures. Parsing inside filter and
    # again inside map would do the work twice.
    parsed = map(_try_float, raw_values)
    numbers = filter(lambda value: value is not None, parsed)
    return [value * factor for value in numbers]


def make_running_average() -> Callable[[float], float]:
    """Return a closure that accepts numbers and returns the running mean.

    Examples:
        >>> avg = make_running_average()
        >>> avg(10)
        10.0
    """
    total = 0.0
    count = 0

    def add(value: float) -> float:
        nonlocal total, count  # why: without nonlocal these become locals
        total += value
        count += 1
        return total / count

    return add


def make_adders(offsets: list[int]) -> list[Callable[[int], int]]:
    """Return one adder function per offset, each capturing its OWN offset.

    Examples:
        >>> [add(0) for add in make_adders([1, 10])]
        [1, 10]
    """

    def make_one(offset: int) -> Callable[[int], int]:
        # why: each call to make_one creates a new scope, so each `add` gets its
        # own `offset` cell. A lambda built in the loop would share one cell.
        def add(value: int) -> int:
            return value + offset

        return add

    return [make_one(offset) for offset in offsets]


def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: count calls and record the duration of the most recent one.

    Examples:
        >>> @count_calls
        ... def add(a, b):
        ...     return a + b
        >>> add(1, 2)
        3
    """

    @functools.wraps(func)  # why: keeps __name__/__doc__ so logs and stacking work
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.calls += 1
        started = time.perf_counter()  # why: monotonic clock, never time.time()
        try:
            return func(*args, **kwargs)
        finally:
            # why: finally means failures are counted and timed too
            wrapper.last_duration = time.perf_counter() - started

    wrapper.calls = 0
    wrapper.last_duration = 0.0
    return wrapper


def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: cache results keyed on the positional arguments.

    Examples:
        >>> @memoize
        ... def square(n):
        ...     return n * n
        >>> square(4), square(4)
        (16, 16)
    """
    cache: dict[tuple[Any, ...], Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any) -> Any:
        if args in cache:
            wrapper.hits += 1
            return cache[args]
        wrapper.misses += 1
        # why: store before returning so recursive calls see the memo
        cache[args] = func(*args)
        return cache[args]

    wrapper.cache = cache
    wrapper.hits = 0
    wrapper.misses = 0
    return wrapper


def retry(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: retry a failing call up to `attempts` times.

    Examples:
        >>> @retry(attempts=2, exceptions=(ValueError,))
        ... def ok():
        ...     return 1
        >>> ok()
        1
    """
    if attempts < 1:
        # why: validate in the factory so the error points at the @retry line
        raise ValueError(f"attempts must be at least 1, got {attempts}")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            wrapper.attempts_made = 0
            last_error: BaseException | None = None
            for _ in range(attempts):
                wrapper.attempts_made += 1
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    last_error = error  # keep the newest, re-raise it at the end
            raise last_error  # type: ignore[misc]

        wrapper.attempts_made = 0
        return wrapper

    return decorator


def audited(
    sink: list[str], label: str
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory: append one audit line per call to `sink`.

    Examples:
        >>> log = []
        >>> @audited(log, "api")
        ... def half(n):
        ...     return n // 2
        >>> half(10)
        5
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        name = func.__name__  # why: read once; wraps keeps it right when stacked

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                sink.append(f"{label}:{name}:error:{type(error).__name__}")
                raise  # why: audit then propagate; swallowing hides real bugs
            sink.append(f"{label}:{name}:ok:{result!r}")
            return result

        return wrapper

    return decorator


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Return a single function applying `funcs` left to right.

    Examples:
        >>> compose(str.strip, str.lower)("  HeLLo  ")
        'hello'
    """

    def composed(value: Any) -> Any:
        # why: reduce over the functions is the one fold with no built-in
        # equivalent; the initial value is the argument itself.
        return functools.reduce(lambda acc, func: func(acc), funcs, value)

    return composed


if __name__ == "__main__":
    print("Solutions module. Run `python check.py day16` to grade exercises.py.")
