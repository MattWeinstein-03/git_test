"""Day 20 graded checks — threads, processes and asyncio.

Every test here is deterministic: no sleep longer than 0.02s, no assertion about
elapsed time, no processes. Concurrency is verified with invariants — exact
totals, input ordering, and peak observed concurrency.

The `day` fixture hands these tests your exercises.py (or solutions.py when
PZH_SOLUTIONS=1 is set). Never import exercises directly.
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any

import pytest


def _module_level_function(value: int) -> int:
    """Picklable by name; used by the pickling exercise."""
    return value * 2


# --- exercise 1: choose_approach -----------------------------------------


def test_choose_approach_io_small_uses_threads(day):
    assert day.choose_approach("io", 30) == "threads"


def test_choose_approach_io_large_native_uses_asyncio(day):
    assert day.choose_approach("io", 5000, native_async=True) == "asyncio"


def test_choose_approach_io_large_without_async_libraries_uses_threads(day):
    assert day.choose_approach("io", 5000, native_async=False) == "threads"


def test_choose_approach_cpu_uses_processes(day):
    assert day.choose_approach("cpu", 40) == "processes"


def test_choose_approach_c_extension_uses_threads(day):
    assert day.choose_approach("cpu_c", 40) == "threads"


def test_choose_approach_single_task_is_sequential(day):
    assert day.choose_approach("io", 1) == "sequential"
    assert day.choose_approach("cpu", 1) == "sequential"
    assert day.choose_approach("cpu", 0) == "sequential"


def test_choose_approach_unknown_bound_is_sequential(day):
    assert day.choose_approach("mystery", 500) == "sequential"


def test_choose_approach_boundary_at_100_tasks(day):
    assert day.choose_approach("io", 100, native_async=True) == "threads"
    assert day.choose_approach("io", 101, native_async=True) == "asyncio"


# --- exercise 2: threaded_map --------------------------------------------


def test_threaded_map_preserves_order(day):
    assert day.threaded_map(str.upper, ["a", "b", "c"]) == ["A", "B", "C"]


def test_threaded_map_with_many_items(day):
    got = day.threaded_map(lambda n: n * n, list(range(50)), max_workers=8)
    assert got == [n * n for n in range(50)]


def test_threaded_map_empty_input(day):
    assert day.threaded_map(str.upper, []) == []


def test_threaded_map_runs_concurrently(day):
    lock = threading.Lock()
    state = {"in_flight": 0, "peak": 0}

    def work(item: int) -> int:
        with lock:
            state["in_flight"] += 1
            state["peak"] = max(state["peak"], state["in_flight"])
        # A tiny wait, so the workers genuinely overlap without slowing the suite.
        threading.Event().wait(0.01)
        with lock:
            state["in_flight"] -= 1
        return item

    day.threaded_map(work, list(range(8)), max_workers=4)
    assert state["peak"] > 1, (
        f"peak concurrency was {state['peak']}: the work ran sequentially"
    )
    assert state["peak"] <= 4, f"max_workers=4 was exceeded: peak {state['peak']}"


def test_threaded_map_propagates_exceptions(day):
    def work(item: int) -> int:
        if item == 2:
            raise ValueError("item 2 is bad")
        return item

    with pytest.raises(ValueError, match="item 2"):
        day.threaded_map(work, [1, 2, 3])


def test_threaded_map_rejects_bad_worker_count(day):
    with pytest.raises(ValueError):
        day.threaded_map(str.upper, ["a"], max_workers=0)


# --- exercise 3: threaded_fetch_all --------------------------------------


def test_threaded_fetch_all_collects_results(day):
    got = day.threaded_fetch_all(lambda url: f"payload {url}", ["/a", "/b"])
    assert got == {"/a": "payload /a", "/b": "payload /b"}


def test_threaded_fetch_all_records_errors(day):
    def fetch(url: str) -> str:
        if url == "/bad":
            raise ConnectionError("reset")
        return f"payload {url}"

    got = day.threaded_fetch_all(fetch, ["/a", "/bad"])
    assert got == {"/a": "payload /a", "/bad": "ConnectionError: reset"}, f"got {got}"


def test_threaded_fetch_all_one_failure_does_not_sink_the_batch(day):
    def fetch(url: str) -> str:
        if url.endswith("3"):
            raise TimeoutError("slow")
        return "ok"

    got = day.threaded_fetch_all(fetch, [f"/{n}" for n in range(6)], max_workers=3)
    assert len(got) == 6
    assert sum(1 for value in got.values() if value == "ok") == 5
    assert got["/3"] == "TimeoutError: slow", f"got {got['/3']!r}"


def test_threaded_fetch_all_empty_input(day):
    assert day.threaded_fetch_all(lambda url: url, []) == {}


def test_threaded_fetch_all_calls_fetch_once_per_url(day):
    calls: list[str] = []
    lock = threading.Lock()

    def fetch(url: str) -> str:
        with lock:
            calls.append(url)
        return url

    day.threaded_fetch_all(fetch, ["/a", "/b", "/c"], max_workers=3)
    assert sorted(calls) == ["/a", "/b", "/c"]


def test_threaded_fetch_all_runs_concurrently(day):
    lock = threading.Lock()
    state = {"in_flight": 0, "peak": 0}

    def fetch(url: str) -> str:
        with lock:
            state["in_flight"] += 1
            state["peak"] = max(state["peak"], state["in_flight"])
        threading.Event().wait(0.01)
        with lock:
            state["in_flight"] -= 1
        return url

    day.threaded_fetch_all(fetch, [f"/{n}" for n in range(6)], max_workers=3)
    assert state["peak"] > 1, "the fetches ran one after another"


# --- exercise 4: SafeCounter ---------------------------------------------


def test_safe_counter_starts_at_zero_or_given_value(day):
    assert day.SafeCounter().value == 0
    assert day.SafeCounter(10).value == 10


def test_safe_counter_increment_returns_new_value(day):
    counter = day.SafeCounter()
    assert counter.increment() == 1
    assert counter.increment(5) == 6
    assert counter.value == 6


def test_safe_counter_is_exact_under_contention(day):
    counter = day.SafeCounter()
    per_thread = 20_000
    threads = [
        threading.Thread(target=lambda: [counter.increment() for _ in range(per_thread)])
        for _ in range(4)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    want = per_thread * 4
    assert counter.value == want, (
        f"lost {want - counter.value} increments: the critical section is not protected"
    )


def test_safe_counter_bump_if_below_returns_flag(day):
    counter = day.SafeCounter(6)
    assert counter.bump_if_below(7) is True
    assert counter.value == 7
    assert counter.bump_if_below(7) is False
    assert counter.value == 7


def test_safe_counter_bump_if_below_never_exceeds_limit(day):
    counter = day.SafeCounter()
    limit = 50
    successes: list[bool] = []
    lock = threading.Lock()

    def hammer() -> None:
        for _ in range(200):
            got = counter.bump_if_below(limit)
            with lock:
                successes.append(got)

    threads = [threading.Thread(target=hammer) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert counter.value == limit, (
        f"value reached {counter.value} with a limit of {limit}: check-then-act "
        "must be inside the lock"
    )
    assert sum(successes) == limit, f"{sum(successes)} threads were told they won"


def test_safe_counter_uses_a_lock(day):
    counter = day.SafeCounter()
    locks = [
        value
        for value in vars(counter).values()
        if isinstance(value, (type(threading.Lock()), type(threading.RLock())))
    ]
    assert locks, "SafeCounter should hold a threading.Lock (or RLock)"


# --- exercise 5: picklable_names -----------------------------------------


def test_picklable_names_accepts_plain_data(day):
    got = day.picklable_names({"data": [1, 2], "text": "x", "number": 3.5})
    assert got == ["data", "number", "text"], f"got {got}"


def test_picklable_names_rejects_lambdas(day):
    assert day.picklable_names({"lam": lambda x: x}) == []


def test_picklable_names_rejects_locks_and_generators(day):
    candidates = {"lock": threading.Lock(), "gen": (n for n in range(3))}
    assert day.picklable_names(candidates) == []


def test_picklable_names_accepts_module_level_functions(day):
    got = day.picklable_names({"func": _module_level_function, "lam": lambda x: x})
    assert got == ["func"], f"got {got}"


def test_picklable_names_is_sorted(day):
    got = day.picklable_names({"z": 1, "a": 2, "m": 3})
    assert got == ["a", "m", "z"]


def test_picklable_names_empty_input(day):
    assert day.picklable_names({}) == []


# --- exercise 6: chunk_ranges --------------------------------------------


def test_chunk_ranges_even_split(day):
    assert day.chunk_ranges(9, 3) == [(0, 3), (3, 6), (6, 9)]


def test_chunk_ranges_uneven_split_front_loads(day):
    got = day.chunk_ranges(10, 3)
    assert got == [(0, 4), (4, 7), (7, 10)], f"got {got}"


def test_chunk_ranges_more_workers_than_items(day):
    assert day.chunk_ranges(2, 4) == [(0, 1), (1, 2)]


def test_chunk_ranges_zero_total(day):
    assert day.chunk_ranges(0, 4) == []


def test_chunk_ranges_single_worker(day):
    assert day.chunk_ranges(7, 1) == [(0, 7)]


def test_chunk_ranges_tiles_without_gaps_or_overlaps(day):
    for total in (0, 1, 5, 17, 100):
        for workers in (1, 3, 4, 7):
            chunks = day.chunk_ranges(total, workers)
            covered = [index for start, stop in chunks for index in range(start, stop)]
            assert covered == list(range(total)), (
                f"chunk_ranges({total}, {workers}) -> {chunks} does not tile 0..{total}"
            )
            sizes = [stop - start for start, stop in chunks]
            assert all(size > 0 for size in sizes), f"empty chunk in {chunks}"
            if sizes:
                assert max(sizes) - min(sizes) <= 1, f"unbalanced chunks: {chunks}"


def test_chunk_ranges_validates_arguments(day):
    with pytest.raises(ValueError):
        day.chunk_ranges(10, 0)
    with pytest.raises(ValueError):
        day.chunk_ranges(-1, 2)


# --- exercise 7: gather_in_order -----------------------------------------


def test_gather_in_order_returns_input_order(day):
    async def fetch(url: str) -> str:
        # The later urls sleep less, so completion order differs from input order.
        await asyncio.sleep(0.01 if url == "/a" else 0)
        return url.upper()

    got = asyncio.run(day.gather_in_order(fetch, ["/a", "/b", "/c"]))
    assert got == ["/A", "/B", "/C"], f"got {got}"


def test_gather_in_order_is_concurrent(day):
    state = {"in_flight": 0, "peak": 0}

    async def fetch(url: str) -> str:
        state["in_flight"] += 1
        state["peak"] = max(state["peak"], state["in_flight"])
        await asyncio.sleep(0.01)
        state["in_flight"] -= 1
        return url

    asyncio.run(day.gather_in_order(fetch, [f"/{n}" for n in range(5)]))
    assert state["peak"] == 5, (
        f"peak concurrency {state['peak']}: awaiting in a loop is sequential, "
        "use asyncio.gather or a TaskGroup"
    )


def test_gather_in_order_empty(day):
    async def fetch(url: str) -> str:
        return url

    assert asyncio.run(day.gather_in_order(fetch, [])) == []


def test_gather_in_order_propagates_errors(day):
    async def fetch(url: str) -> str:
        if url == "/bad":
            raise ValueError("bad url")
        await asyncio.sleep(0)
        return url

    with pytest.raises(ValueError):
        asyncio.run(day.gather_in_order(fetch, ["/a", "/bad"]))


# --- exercise 8: with_timeout --------------------------------------------


def test_with_timeout_returns_result_when_fast(day):
    async def quick() -> str:
        await asyncio.sleep(0)
        return "fast"

    assert asyncio.run(day.with_timeout(quick(), 0.05, "gave up")) == "fast"


def test_with_timeout_returns_default_when_slow(day):
    async def slow() -> str:
        await asyncio.sleep(1)
        return "never"

    assert asyncio.run(day.with_timeout(slow(), 0.01, "gave up")) == "gave up"


def test_with_timeout_cancels_the_slow_work(day):
    state = {"cancelled": False}

    async def slow() -> str:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            state["cancelled"] = True
            raise
        return "never"

    async def main() -> Any:
        result = await day.with_timeout(slow(), 0.01, "gave up")
        await asyncio.sleep(0)  # let the cancellation land
        return result

    assert asyncio.run(main()) == "gave up"
    assert state["cancelled"] is True, "wait_for cancels the awaitable it gave up on"


def test_with_timeout_does_not_hide_other_errors(day):
    async def broken() -> str:
        raise KeyError("missing")

    with pytest.raises(KeyError):
        asyncio.run(day.with_timeout(broken(), 0.05, "gave up"))


def test_with_timeout_default_can_be_any_object(day):
    async def slow() -> str:
        await asyncio.sleep(1)
        return "never"

    assert asyncio.run(day.with_timeout(slow(), 0.01, None)) is None


# --- exercise 9: bounded_gather ------------------------------------------


def test_bounded_gather_returns_input_order(day):
    async def double(n: int) -> int:
        await asyncio.sleep(0.01 if n == 1 else 0)
        return n * 2

    assert asyncio.run(day.bounded_gather(double, [1, 2, 3], limit=2)) == [2, 4, 6]


def test_bounded_gather_respects_the_limit(day):
    state = {"in_flight": 0, "peak": 0}

    async def work(n: int) -> int:
        state["in_flight"] += 1
        state["peak"] = max(state["peak"], state["in_flight"])
        await asyncio.sleep(0.01)
        state["in_flight"] -= 1
        return n

    asyncio.run(day.bounded_gather(work, list(range(12)), limit=3))
    assert state["peak"] <= 3, f"limit 3 exceeded: peak was {state['peak']}"
    assert state["peak"] == 3, (
        f"peak was only {state['peak']}: the work should saturate the limit"
    )


def test_bounded_gather_limit_one_is_sequential(day):
    state = {"in_flight": 0, "peak": 0}

    async def work(n: int) -> int:
        state["in_flight"] += 1
        state["peak"] = max(state["peak"], state["in_flight"])
        await asyncio.sleep(0)
        state["in_flight"] -= 1
        return n

    got = asyncio.run(day.bounded_gather(work, [1, 2, 3], limit=1))
    assert got == [1, 2, 3]
    assert state["peak"] == 1, f"limit=1 must serialise; peak was {state['peak']}"


def test_bounded_gather_runs_every_item_once(day):
    seen: list[int] = []

    async def work(n: int) -> int:
        seen.append(n)
        await asyncio.sleep(0)
        return n

    asyncio.run(day.bounded_gather(work, list(range(20)), limit=5))
    assert sorted(seen) == list(range(20))


def test_bounded_gather_empty_input(day):
    async def work(n: int) -> int:
        return n

    assert asyncio.run(day.bounded_gather(work, [], limit=2)) == []


def test_bounded_gather_rejects_bad_limit(day):
    async def work(n: int) -> int:
        return n

    async def main() -> Any:
        return await day.bounded_gather(work, [1], limit=0)

    with pytest.raises(ValueError):
        asyncio.run(main())


# --- exercise 10: crawl_pages --------------------------------------------

PAGES: dict[str, dict[str, Any]] = {
    "/a": {"items": [1, 2], "next": "/b"},
    "/b": {"items": [3], "next": "/c"},
    "/c": {"items": [4], "next": None},
}


def test_crawl_pages_follows_the_chain(day):
    async def fetch(url: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        return PAGES[url]

    got = asyncio.run(day.crawl_pages(fetch, "/a"))
    assert got == {"items": [1, 2, 3, 4], "pages": 3, "errors": []}, f"got {got}"


def test_crawl_pages_respects_max_pages(day):
    calls: list[str] = []

    async def fetch(url: str) -> dict[str, Any]:
        calls.append(url)
        return {"items": [len(calls)], "next": "/loop"}

    got = asyncio.run(day.crawl_pages(fetch, "/loop", max_pages=3))
    assert len(calls) == 3, f"made {len(calls)} fetches, expected 3"
    assert got["pages"] == 3
    assert got["items"] == [1, 2, 3]


def test_crawl_pages_records_timeout_and_stops(day):
    calls: list[str] = []

    async def fetch(url: str) -> dict[str, Any]:
        calls.append(url)
        if url == "/b":
            await asyncio.sleep(1)
        return PAGES[url]

    got = asyncio.run(day.crawl_pages(fetch, "/a", timeout=0.01))
    assert got["items"] == [1, 2], f"got {got['items']}"
    assert got["pages"] == 1
    assert got["errors"] == ["/b: timeout"], f"got {got['errors']}"
    assert calls == ["/a", "/b"], "crawling must stop after a timeout"


def test_crawl_pages_records_other_errors_and_stops(day):
    async def fetch(url: str) -> dict[str, Any]:
        if url == "/b":
            raise ConnectionError("reset")
        return PAGES[url]

    got = asyncio.run(day.crawl_pages(fetch, "/a"))
    assert got["items"] == [1, 2]
    assert got["errors"] == ["/b: ConnectionError"], f"got {got['errors']}"


def test_crawl_pages_tolerates_missing_items(day):
    async def fetch(url: str) -> dict[str, Any]:
        return {"next": None} if url == "/a" else PAGES[url]

    got = asyncio.run(day.crawl_pages(fetch, "/a"))
    assert got == {"items": [], "pages": 1, "errors": []}, f"got {got}"


def test_crawl_pages_single_page(day):
    async def fetch(url: str) -> dict[str, Any]:
        return {"items": ["only"], "next": None}

    got = asyncio.run(day.crawl_pages(fetch, "/a"))
    assert got == {"items": ["only"], "pages": 1, "errors": []}


def test_crawl_pages_rejects_bad_max_pages(day):
    async def fetch(url: str) -> dict[str, Any]:
        return {"items": [], "next": None}

    async def main() -> Any:
        return await day.crawl_pages(fetch, "/a", max_pages=0)

    with pytest.raises(ValueError):
        asyncio.run(main())
