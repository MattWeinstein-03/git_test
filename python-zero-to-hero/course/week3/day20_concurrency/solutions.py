"""Day 20 reference solutions.

Same signatures and docstrings as exercises.py. `# why:` comments mark the
choices that are not obvious.
"""

from __future__ import annotations

import asyncio
import pickle
import threading
from collections.abc import Awaitable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable


def choose_approach(bound: str, tasks: int, native_async: bool = False) -> str:
    """Recommend a concurrency approach, following the lesson's flowchart.

    Examples:
        >>> choose_approach("io", 30)
        'threads'
    """
    if tasks <= 1:
        # why: the first question is always "is there anything to overlap?"
        return "sequential"
    if bound == "cpu":
        return "processes"
    if bound == "cpu_c":
        # why: numpy/hashlib release the GIL inside their C loops, so threads
        # really do use multiple cores here.
        return "threads"
    if bound == "io":
        if tasks > 100 and native_async:
            return "asyncio"
        return "threads"
    return "sequential"


def threaded_map(
    func: Callable[[Any], Any], items: Sequence[Any], max_workers: int = 4
) -> list[Any]:
    """Apply `func` to every item using a thread pool, keeping INPUT order.

    Examples:
        >>> threaded_map(str.upper, ["a", "b"])
        ['A', 'B']
    """
    if max_workers < 1:
        raise ValueError(f"max_workers must be at least 1, got {max_workers}")
    if not items:
        return []  # why: opening a pool for nothing is pure overhead
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        # why: pool.map preserves input order and re-raises worker exceptions
        return list(pool.map(func, items))


def threaded_fetch_all(
    fetch: Callable[[str], Any], urls: Sequence[str], max_workers: int = 4
) -> dict[str, Any]:
    """Fetch every url concurrently; record failures instead of raising.

    Examples:
        >>> threaded_fetch_all(lambda url: url, ["/a"])
        {'/a': '/a'}
    """
    if max_workers < 1:
        raise ValueError(f"max_workers must be at least 1, got {max_workers}")
    results: dict[str, Any] = {}
    if not urls:
        return results
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetch, url): url for url in urls}
        for future in futures:
            url = futures[future]
            try:
                # why: calling .result() is what surfaces a worker's exception.
                # A future whose result is never read swallows the error.
                results[url] = future.result()
            except Exception as error:  # noqa: BLE001 - collect, never crash
                results[url] = f"{type(error).__name__}: {error}"
    return results


class SafeCounter:
    """A counter that is exact when many threads use it at once.

    Examples:
        >>> SafeCounter(5).increment()
        6
    """

    def __init__(self, start: int = 0) -> None:
        self._value = start
        self._lock = threading.Lock()

    @property
    def value(self) -> int:
        with self._lock:  # why: a consistent read, not a torn one
            return self._value

    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value

    def bump_if_below(self, limit: int) -> bool:
        # why: the check AND the act must be inside one critical section. Locking
        # only the += would let two threads both pass a check at limit-1.
        with self._lock:
            if self._value < limit:
                self._value += 1
                return True
            return False


def picklable_names(candidates: dict[str, Any]) -> list[str]:
    """Return the names of the candidates that could be sent to a process worker.

    Examples:
        >>> picklable_names({"data": [1, 2], "lambda": lambda x: x})
        ['data']
    """
    ok: list[str] = []
    for name, value in candidates.items():
        try:
            pickle.dumps(value)
        except Exception:  # noqa: BLE001 - TypeError, PicklingError, AttributeError...
            continue
        ok.append(name)
    return sorted(ok)


def chunk_ranges(total: int, workers: int) -> list[tuple[int, int]]:
    """Split `range(total)` into `workers` contiguous (start, stop) slices.

    Examples:
        >>> chunk_ranges(10, 3)
        [(0, 4), (4, 7), (7, 10)]
    """
    if workers < 1:
        raise ValueError(f"workers must be at least 1, got {workers}")
    if total < 0:
        raise ValueError(f"total must not be negative, got {total}")

    base, remainder = divmod(total, workers)
    chunks: list[tuple[int, int]] = []
    start = 0
    for index in range(workers):
        # why: the first `remainder` chunks take one extra item, so sizes differ
        # by at most 1 and the earlier chunks are the bigger ones.
        size = base + (1 if index < remainder else 0)
        if size == 0:
            continue  # skip empty chunks when total < workers
        chunks.append((start, start + size))
        start += size
    return chunks


async def gather_in_order(
    fetch: Callable[[str], Awaitable[Any]], urls: Sequence[str]
) -> list[Any]:
    """Await every fetch concurrently and return results in INPUT order.

    Examples:
        >>> import asyncio
        >>> async def fetch(url):
        ...     return url
        >>> asyncio.run(gather_in_order(fetch, ["/a"]))
        ['/a']
    """
    # why: gather starts everything immediately and returns results in argument
    # order, which is what the spec asks for. A `for url in urls: await ...` loop
    # would be sequential.
    return list(await asyncio.gather(*(fetch(url) for url in urls)))


async def with_timeout(awaitable: Awaitable[Any], seconds: float, default: Any) -> Any:
    """Await something, returning `default` if it takes longer than `seconds`.

    Examples:
        >>> import asyncio
        >>> async def quick():
        ...     return "fast"
        >>> asyncio.run(with_timeout(quick(), 0.05, "gave up"))
        'fast'
    """
    try:
        return await asyncio.wait_for(awaitable, timeout=seconds)
    except asyncio.TimeoutError:
        # why: only the timeout is handled. Other exceptions propagate, because a
        # failure is not a timeout and must not be disguised as one.
        return default


async def bounded_gather(
    work: Callable[[Any], Awaitable[Any]], items: Sequence[Any], limit: int
) -> list[Any]:
    """Run `work(item)` for every item, at most `limit` at a time, in input order.

    Examples:
        >>> import asyncio
        >>> async def double(n):
        ...     return n * 2
        >>> asyncio.run(bounded_gather(double, [1, 2], limit=1))
        [2, 4]
    """
    if limit < 1:
        raise ValueError(f"limit must be at least 1, got {limit}")

    semaphore = asyncio.Semaphore(limit)

    async def guarded(item: Any) -> Any:
        async with semaphore:  # why: at most `limit` coroutines inside this block
            return await work(item)

    return list(await asyncio.gather(*(guarded(item) for item in items)))


async def crawl_pages(
    fetch: Callable[[str], Awaitable[dict[str, Any]]],
    first_url: str,
    max_pages: int = 10,
    timeout: float = 0.05,
) -> dict[str, Any]:
    """Follow an async paginated API, collecting items and surviving failures.

    Examples:
        >>> import asyncio
        >>> async def fetch(url):
        ...     return {"items": [1], "next": None}
        >>> asyncio.run(crawl_pages(fetch, "/a"))["pages"]
        1
    """
    if max_pages < 1:
        raise ValueError(f"max_pages must be at least 1, got {max_pages}")

    items: list[Any] = []
    errors: list[str] = []
    pages = 0
    url: str | None = first_url

    while url and pages < max_pages:
        try:
            payload = await asyncio.wait_for(fetch(url), timeout=timeout)
        except asyncio.TimeoutError:
            errors.append(f"{url}: timeout")
            break  # why: a stalled endpoint should not be hammered further
        except Exception as error:  # noqa: BLE001 - report and stop, never crash
            errors.append(f"{url}: {type(error).__name__}")
            break
        pages += 1
        items.extend(payload.get("items") or [])
        url = payload.get("next")

    return {"items": items, "pages": pages, "errors": errors}


if __name__ == "__main__":
    print("Solutions module. Run `python check.py day20` to grade exercises.py.")
