"""Day 20 exercises — threads, processes and asyncio.

Everything here is deterministic and fast: no exercise needs a sleep longer than
a few milliseconds, and none of them spawns a process (the pickling rules are
exercised with `pickle` directly instead, which is where the constraint actually
lives).

Exercises 7-10 are coroutines. Test them — and try them yourself — with
`asyncio.run(...)`.

Grade yourself from the course root with:

    python check.py day20
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Awaitable, Iterable, Sequence
from typing import Any, Callable


def choose_approach(bound: str, tasks: int, native_async: bool = False) -> str:
    """Recommend a concurrency approach, following the lesson's flowchart.

    Decision rules, applied in this order:
      1. `tasks` of 1 or less -> "sequential": there is nothing to overlap.
      2. `bound == "cpu"` -> "processes": separate interpreters, separate GILs.
      3. `bound == "cpu_c"` (the hot loop is in a C extension that releases the
         GIL, like hashlib or numpy) -> "threads".
      4. `bound == "io"` -> "asyncio" when there are more than 100 tasks AND
         `native_async` is True (you have async-native libraries all the way
         down); otherwise "threads".
      5. anything else, including an unrecognised `bound` -> "sequential".

    Args:
        bound: "io", "cpu", "cpu_c", or anything else.
        tasks: how many units of work there are.
        native_async: whether async-native libraries are available.

    Returns:
        One of "sequential", "threads", "processes", "asyncio".

    Examples:
        >>> choose_approach("io", 30)
        'threads'
        >>> choose_approach("io", 5000, native_async=True)
        'asyncio'
        >>> choose_approach("io", 5000, native_async=False)
        'threads'
        >>> choose_approach("cpu", 40)
        'processes'
        >>> choose_approach("cpu_c", 40)
        'threads'
        >>> choose_approach("io", 1)
        'sequential'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: choose_approach")


def threaded_map(
    func: Callable[[Any], Any], items: Sequence[Any], max_workers: int = 4
) -> list[Any]:
    """Apply `func` to every item using a thread pool, keeping INPUT order.

    Use `concurrent.futures.ThreadPoolExecutor`. If `func` raises for some item,
    let the exception propagate — this function is the honest one; exercise 3 is
    the forgiving one.

    Args:
        func: the callable to apply.
        items: the inputs.
        max_workers: pool size, at least 1.

    Returns:
        A list of results, in the same order as `items`.

    Raises:
        ValueError: if `max_workers` is less than 1.

    Examples:
        >>> threaded_map(str.upper, ["a", "b", "c"])
        ['A', 'B', 'C']
        >>> threaded_map(lambda n: n * 2, [1, 2, 3], max_workers=2)
        [2, 4, 6]
        >>> threaded_map(str.upper, [])
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: threaded_map")


def threaded_fetch_all(
    fetch: Callable[[str], Any], urls: Sequence[str], max_workers: int = 4
) -> dict[str, Any]:
    """Fetch every url concurrently; record failures instead of raising.

    Use a thread pool with `submit`, and consume every future so no exception is
    lost. For a url that succeeded, store the returned value. For a url whose
    fetch raised, store the string f"{type(exc).__name__}: {exc}".

    Duplicate urls in the input are fetched once each but collapse into one key,
    which is fine — do not special-case it.

    Args:
        fetch: the injected transport; called once per url.
        urls: the urls to fetch.
        max_workers: pool size, at least 1.

    Returns:
        A dict of url -> result-or-error-string.

    Examples:
        >>> def fetch(url):
        ...     if url == "/bad":
        ...         raise ConnectionError("reset")
        ...     return f"payload {url}"
        >>> threaded_fetch_all(fetch, ["/a", "/bad"]) == {
        ...     "/a": "payload /a", "/bad": "ConnectionError: reset"}
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: threaded_fetch_all")


class SafeCounter:
    """A counter that is exact when many threads use it at once.

    The naive version fails because `self.value += 1` reads, adds and writes, and
    `bump_if_below` is a check-then-act pair. Guard both with one
    `threading.Lock` held for the whole operation.

    Required interface:
      - `SafeCounter()` starts at 0; `SafeCounter(10)` starts at 10.
      - `.value` -> the current count as an int.
      - `.increment(amount=1)` -> add and return the new value.
      - `.bump_if_below(limit)` -> if the current value is strictly below `limit`,
        increment by 1 and return True; otherwise leave it alone and return False.
        This must be atomic: with 8 threads hammering it and a limit of 50, the
        value must never exceed 50.

    Examples:
        >>> counter = SafeCounter()
        >>> counter.increment()
        1
        >>> counter.increment(5)
        6
        >>> counter.value
        6
        >>> counter.bump_if_below(7)
        True
        >>> counter.bump_if_below(7)
        False
        >>> counter.value
        7
    """

    def __init__(self, start: int = 0) -> None:
        # TODO: your code here (store the value and create a lock)
        raise NotImplementedError("exercise 4: SafeCounter.__init__")

    @property
    def value(self) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 4: SafeCounter.value")

    def increment(self, amount: int = 1) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 4: SafeCounter.increment")

    def bump_if_below(self, limit: int) -> bool:
        # TODO: your code here
        raise NotImplementedError("exercise 4: SafeCounter.bump_if_below")


def picklable_names(candidates: dict[str, Any]) -> list[str]:
    """Return the names of the candidates that could be sent to a process worker.

    Anything sent to a `ProcessPoolExecutor` is pickled, so this is exactly the
    test for "can this cross a process boundary". Use `pickle.dumps` and catch
    the failures — several different exception types are possible (`TypeError`,
    `pickle.PicklingError`, `AttributeError`), so catch `Exception`.

    Args:
        candidates: name -> object to test.

    Returns:
        The names that pickled successfully, sorted alphabetically.

    Examples:
        >>> picklable_names({"data": [1, 2], "lambda": lambda x: x})
        ['data']
        >>> picklable_names({"lock": __import__("threading").Lock()})
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: picklable_names")


def chunk_ranges(total: int, workers: int) -> list[tuple[int, int]]:
    """Split `range(total)` into `workers` contiguous (start, stop) slices.

    This is how you feed a process pool: one big chunk per worker instead of a
    million tiny tasks, because every task costs a pickle round trip.

    Rules:
      - the slices are contiguous, in order, and cover exactly 0..total
      - `stop` is exclusive, so the slices tile: [(0, 3), (3, 6), ...]
      - when `total` does not divide evenly, the earlier chunks are the larger
        ones and the sizes differ by at most 1
      - empty chunks are never returned, so fewer than `workers` slices come back
        when `total < workers`
      - `total` of 0 returns []

    Args:
        total: how many items there are.
        workers: how many chunks to aim for, at least 1.

    Returns:
        A list of (start, stop) tuples.

    Raises:
        ValueError: if `workers` is less than 1 or `total` is negative.

    Examples:
        >>> chunk_ranges(9, 3)
        [(0, 3), (3, 6), (6, 9)]
        >>> chunk_ranges(10, 3)
        [(0, 4), (4, 7), (7, 10)]
        >>> chunk_ranges(2, 4)
        [(0, 1), (1, 2)]
        >>> chunk_ranges(0, 4)
        []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: chunk_ranges")


async def gather_in_order(
    fetch: Callable[[str], Awaitable[Any]], urls: Sequence[str]
) -> list[Any]:
    """Await every fetch concurrently and return results in INPUT order.

    `fetch` is an async function: calling it returns a coroutine you must await.
    Use `asyncio.gather` (or a TaskGroup) so the awaits overlap — awaiting them
    one at a time in a loop is sequential and the tests detect it by measuring
    peak concurrency, not time.

    Args:
        fetch: async callable taking a url.
        urls: the urls to fetch.

    Returns:
        The results, in the same order as `urls`.

    Examples:
        >>> import asyncio
        >>> async def fetch(url):
        ...     await asyncio.sleep(0)
        ...     return url.upper()
        >>> asyncio.run(gather_in_order(fetch, ["/a", "/b"]))
        ['/A', '/B']
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: gather_in_order")


async def with_timeout(awaitable: Awaitable[Any], seconds: float, default: Any) -> Any:
    """Await something, returning `default` if it takes longer than `seconds`.

    Use `asyncio.wait_for` and catch the timeout (`asyncio.TimeoutError`, which is
    `TimeoutError` on 3.11+). A timed-out awaitable is cancelled for you — do not
    swallow `asyncio.CancelledError` yourself.

    Any other exception raised by the awaitable must propagate: a timeout is not
    the same as a failure and must not hide one.

    Args:
        awaitable: the coroutine or future to await.
        seconds: the timeout.
        default: what to return when the timeout fires.

    Returns:
        The awaited result, or `default`.

    Examples:
        >>> import asyncio
        >>> async def quick():
        ...     return "fast"
        >>> async def slow():
        ...     await asyncio.sleep(1)
        ...     return "never"
        >>> asyncio.run(with_timeout(quick(), 0.05, "gave up"))
        'fast'
        >>> asyncio.run(with_timeout(slow(), 0.01, "gave up"))
        'gave up'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: with_timeout")


async def bounded_gather(
    work: Callable[[Any], Awaitable[Any]], items: Sequence[Any], limit: int
) -> list[Any]:
    """Run `work(item)` for every item, at most `limit` at a time, in input order.

    Use `asyncio.Semaphore(limit)`: unbounded concurrency is how you get
    rate-limited or run out of sockets. Results come back in the order of `items`,
    not in completion order.

    Args:
        work: async callable applied to each item.
        items: the inputs.
        limit: maximum number of concurrent calls, at least 1.

    Returns:
        The results in input order.

    Raises:
        ValueError: if `limit` is less than 1.

    Examples:
        >>> import asyncio
        >>> async def double(n):
        ...     await asyncio.sleep(0)
        ...     return n * 2
        >>> asyncio.run(bounded_gather(double, [1, 2, 3], limit=2))
        [2, 4, 6]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: bounded_gather")


async def crawl_pages(
    fetch: Callable[[str], Awaitable[dict[str, Any]]],
    first_url: str,
    max_pages: int = 10,
    timeout: float = 0.05,
) -> dict[str, Any]:
    """Follow an async paginated API, collecting items and surviving failures.

    Each `await fetch(url)` returns `{"items": [...], "next": "<url or None>"}`.
    Walk the chain from `first_url` until "next" is missing/None/empty or
    `max_pages` fetches have been made.

    Failure handling, per page:
      - if the fetch takes longer than `timeout` seconds, record the url as timed
        out and STOP crawling (a stalled endpoint should not be hammered)
      - if the fetch raises any other exception, record the url and the exception
        type name, and stop crawling
      - a page whose "items" is missing contributes nothing and is not an error

    Args:
        fetch: async callable taking a url.
        first_url: where to start.
        max_pages: hard limit on fetches, at least 1.
        timeout: per-page timeout in seconds.

    Returns:
        A dict with exactly these keys:
          "items"  -> list, every item collected, in order
          "pages"  -> int, how many fetches completed successfully
          "errors" -> list[str], one entry per failure, formatted as
                      f"{url}: timeout" or f"{url}: {type(exc).__name__}"

    Raises:
        ValueError: if `max_pages` is less than 1.

    Examples:
        >>> import asyncio
        >>> pages = {"/a": {"items": [1, 2], "next": "/b"},
        ...          "/b": {"items": [3], "next": None}}
        >>> async def fetch(url):
        ...     return pages[url]
        >>> asyncio.run(crawl_pages(fetch, "/a")) == {
        ...     "items": [1, 2, 3], "pages": 2, "errors": []}
        True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: crawl_pages")


if __name__ == "__main__":
    print("Run `python check.py day20` from the course root to grade your work.")
