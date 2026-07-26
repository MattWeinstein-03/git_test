"""Day 15 exercises — comprehensions, iterators, generators.

Implement each function. Replace the `raise NotImplementedError(...)` line with
your code. Grade yourself from the course root with:

    python check.py day15

Order matters: 1-4 drill comprehensions, 5-6 are the iterator protocol and
generator functions, 7-9 are about laziness, and 10 combines everything into a
streaming aggregation. Do not skip ahead.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator


def squares_of_evens(numbers: Iterable[int]) -> list[int]:
    """Return the square of every even number, in the original order.

    Use one list comprehension with a filter. Odd numbers are dropped, not
    replaced.

    Args:
        numbers: any iterable of integers.

    Returns:
        A list of squares of the even inputs.

    Examples:
        >>> squares_of_evens([1, 2, 3, 4])
        [4, 16]
        >>> squares_of_evens([-2, 0, 7])
        [4, 0]
        >>> squares_of_evens([])
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: squares_of_evens")


def word_lengths(words: Iterable[str]) -> dict[str, int]:
    """Map each word to its length, ignoring words shorter than 3 characters.

    Use one dict comprehension. If the same word appears twice the result has a
    single entry for it (dict keys are unique) — no special handling needed.

    Args:
        words: an iterable of strings.

    Returns:
        A dict of word -> len(word) for words with 3 or more characters.

    Examples:
        >>> word_lengths(["yield", "is", "lazy"])
        {'yield': 5, 'lazy': 4}
        >>> word_lengths(["a", "bb"])
        {}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: word_lengths")


def unique_domains(emails: Iterable[str]) -> set[str]:
    """Return the set of lowercase domains from a list of email addresses.

    The domain is everything after the single "@". Addresses that do not contain
    exactly one "@" are ignored rather than causing an error. One set
    comprehension with a filter is enough.

    Args:
        emails: an iterable of address strings, possibly mixed case.

    Returns:
        A set of lowercase domain strings.

    Examples:
        >>> unique_domains(["a@Example.com", "b@example.com", "c@other.org"]) == {
        ...     "example.com", "other.org"}
        True
        >>> sorted(unique_domains(["bad-address", "x@y.io"]))
        ['y.io']
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: unique_domains")


def flatten_matrix(matrix: Iterable[Iterable[int]]) -> list[int]:
    """Flatten one level of nesting, left to right, keeping only positive values.

    Use a single comprehension with two `for` clauses and one `if`.

    Args:
        matrix: an iterable of iterables of integers.

    Returns:
        A flat list of the positive values in row-major order.

    Examples:
        >>> flatten_matrix([[1, -2, 3], [4, 0]])
        [1, 3, 4]
        >>> flatten_matrix([[], [7]])
        [7]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: flatten_matrix")


class Countdown:
    """An iterator that counts down from `start` to 1, written by hand.

    Implement the iterator protocol: `__iter__` returns the object itself and
    `__next__` returns the next value or raises StopIteration when there is
    nothing left. Do NOT use `yield` here — the point is to feel what a
    generator does for you.

    A Countdown is single-use, like every iterator: once exhausted it yields
    nothing more.

    Examples:
        >>> list(Countdown(3))
        [3, 2, 1]
        >>> list(Countdown(0))
        []
        >>> c = Countdown(2)
        >>> next(c)
        2
        >>> list(c)
        [1]
    """

    def __init__(self, start: int) -> None:
        # TODO: your code here (store whatever state __next__ will need)
        raise NotImplementedError("exercise 5: Countdown.__init__")

    def __iter__(self) -> Countdown:
        # TODO: your code here
        raise NotImplementedError("exercise 5: Countdown.__iter__")

    def __next__(self) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 5: Countdown.__next__")


def running_totals(numbers: Iterable[float]) -> Iterator[float]:
    """Yield the cumulative sum after each input value, lazily.

    Must be a generator function: it has to work on an endless input, so it may
    not build a list of the input first, and calling it must run none of the
    body.

    Args:
        numbers: an iterable of numbers, possibly endless.

    Yields:
        One running total per input value, in order.

    Examples:
        >>> list(running_totals([1, 2, 3]))
        [1, 3, 6]
        >>> list(running_totals([5, -5, 2.5]))
        [5, 0, 2.5]
        >>> list(running_totals([]))
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: running_totals")


def take(iterable: Iterable[object], n: int) -> list[object]:
    """Return the first `n` items as a list, without over-consuming the source.

    This must be safe on an infinite generator, which means you have to stop
    pulling values once you have `n` of them. If the source runs out first,
    return everything it had. `n <= 0` returns an empty list and must not
    consume anything at all.

    Args:
        iterable: any iterable, possibly infinite.
        n: how many items to take.

    Returns:
        A list of at most `n` items.

    Examples:
        >>> take([10, 20, 30], 2)
        [10, 20]
        >>> take("abc", 10)
        ['a', 'b', 'c']
        >>> take([1, 2], 0)
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: take")


def chunked(iterable: Iterable[object], size: int) -> Iterator[list[object]]:
    """Return an iterator of consecutive lists of at most `size` items.

    This streams: it must never hold more than one chunk in memory, because it
    is the function you would use to batch a 40 GB file into 1000-row database
    inserts. The final chunk may be short.

    A `size` below 1 is a programming error and must raise ValueError **when
    `chunked` is called**, not on the first `next()`. That means `chunked`
    itself cannot contain `yield` — see LESSON.md section 6, "validate before
    you yield": write a plain function that validates and then returns an inner
    generator.

    Args:
        iterable: any iterable, possibly endless.
        size: maximum chunk length, at least 1.

    Returns:
        An iterator yielding lists of items.

    Raises:
        ValueError: if `size` is less than 1, at call time.

    Examples:
        >>> list(chunked([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
        >>> list(chunked("abc", 5))
        [['a', 'b', 'c']]
        >>> list(chunked([], 3))
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: chunked")


def flatten_deep(nested: Iterable[object]) -> Iterator[object]:
    """Yield every non-list leaf value at any depth, left to right.

    Use recursion with `yield from`. Only `list` counts as a container to
    descend into: strings and tuples are leaves and must be yielded whole.

    Args:
        nested: a list that may contain lists that may contain lists.

    Yields:
        Leaf values in depth-first, left-to-right order.

    Examples:
        >>> list(flatten_deep([1, [2, [3, [4]], 5], 6]))
        [1, 2, 3, 4, 5, 6]
        >>> list(flatten_deep([[], [[]], [1]]))
        [1]
        >>> list(flatten_deep(["ab", [(1, 2)]]))
        ['ab', (1, 2)]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: flatten_deep")


def stream_report(lines: Iterable[str], cutoff: float) -> dict[str, object]:
    """Aggregate a stream of CSV-ish sensor lines into one summary dict.

    Each line should look like `sensor_id,label,value` where `value` parses as a
    float. Lines that are blank (or whitespace only), have the wrong number of
    fields, or whose value does not parse are *quarantined*: counted as skipped,
    never crashed on.

    Only records whose value is strictly greater than `cutoff` count as "kept";
    well-formed records at or below the cutoff are neither kept nor skipped.

    Build this as a chain over the input: consume `lines` exactly once, never
    index it and never call `list()` on it, because in production it is a 30 GB
    file.

    Args:
        lines: an iterable of raw text lines (trailing newlines are tolerated).
        cutoff: values must exceed this to be kept.

    Returns:
        A dict with exactly these keys:
          "kept"    -> int, how many records passed the cutoff
          "skipped" -> int, how many lines were malformed
          "total"   -> float, sum of kept values
          "mean"    -> float, mean of kept values, or 0.0 if none were kept
          "sensors" -> dict[str, int], kept-record count per sensor_id,
                       containing only sensors with at least one kept record

    Examples:
        >>> data = ["s1,temp,21.5", "", "s1,temp,19.0", "junk", "s2,temp,30.5"]
        >>> stream_report(data, 20.0) == {
        ...     "kept": 2, "skipped": 2, "total": 52.0, "mean": 26.0,
        ...     "sensors": {"s1": 1, "s2": 1}}
        True
        >>> stream_report(["a,b,c"], 0.0) == {
        ...     "kept": 0, "skipped": 1, "total": 0.0, "mean": 0.0, "sensors": {}}
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: stream_report")


if __name__ == "__main__":
    # Scratch space. Try things here; nothing in this block is graded.
    print("Run `python check.py day15` from the course root to grade your work.")
