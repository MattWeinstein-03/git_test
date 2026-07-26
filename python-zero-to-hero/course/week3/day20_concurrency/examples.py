"""Day 20 — runnable demonstrations of threads, processes and asyncio.

Run it:

    python course/week3/day20_concurrency/examples.py

Total runtime is about two seconds. Run it twice: the unlocked counter in
section 6 gives a different wrong answer each time, which is the point.

The process-pool section is guarded so it degrades gracefully in restricted
environments; everything else always runs.
"""

from __future__ import annotations

import asyncio
import hashlib
import pickle
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any

# Module-level worker functions: required for ProcessPoolExecutor, because a
# child process looks the function up by name. Locals and lambdas cannot travel.
CHUNK = 3_000_000


def cpu_work(n: int) -> int:
    """Deliberately CPU-bound: pure Python arithmetic, no waiting."""
    total = 0
    for value in range(n):
        total += value * value
    return total


def io_work(seconds: float) -> str:
    """Deliberately I/O-bound: sleeping is what waiting on a socket looks like."""
    time.sleep(seconds)          # time.sleep RELEASES the GIL while it waits
    return f"waited {seconds}s"


def cpu_count_up(n: int) -> int:
    """Counts to n and returns its own total - no shared state to race over."""
    total = 0
    for _ in range(n):
        total += 1
    return total


def hash_work(n: int) -> str:
    """CPU-bound work that happens inside C, which releases the GIL."""
    data = b"x" * 100_000
    digest = b""
    for _ in range(n):
        digest = hashlib.sha256(data + digest).digest()
    return digest.hex()[:12]


def banner(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


def timed(label: str, func, *args, **kwargs) -> tuple[Any, float]:
    """Run something, print how long it took, return (result, seconds)."""
    started = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - started
    print(f"  {label:<34} {elapsed:6.3f}s")
    return result, elapsed


# ---------------------------------------------------------------------------
banner("1-2. I/O-bound vs CPU-bound, and what the GIL does")
# ---------------------------------------------------------------------------

print("Four 0.1s I/O tasks (sleep = waiting = the GIL is released):")
_, seq_io = timed("sequential", lambda: [io_work(0.1) for _ in range(4)])
with ThreadPoolExecutor(max_workers=4) as pool:
    _, thr_io = timed("4 threads", lambda: list(pool.map(io_work, [0.1] * 4)))
print(f"  -> threads were {seq_io / thr_io:.1f}x faster. Waiting parallelises.")

print("\nFour CPU-bound tasks in pure Python (the GIL is held while executing):")
_, seq_cpu = timed("sequential", lambda: [cpu_work(CHUNK) for _ in range(4)])
with ThreadPoolExecutor(max_workers=4) as pool:
    _, thr_cpu = timed("4 threads", lambda: list(pool.map(cpu_work, [CHUNK] * 4)))
print(f"  -> threads gave {seq_cpu / thr_cpu:.2f}x. No real gain: one bytecode at a time.")

print("\nCPU-bound work inside a C extension (hashlib releases the GIL):")
_, seq_hash = timed("sequential", lambda: [hash_work(60) for _ in range(4)])
with ThreadPoolExecutor(max_workers=4) as pool:
    _, thr_hash = timed("4 threads", lambda: list(pool.map(hash_work, [60] * 4)))
print(f"  -> {seq_hash / thr_hash:.2f}x: C code that releases the GIL DOES use cores.")
print("\nSo 'the GIL means threads are useless' is wrong. It means threads are")
print("useless for pure-Python CPU work, and excellent for waiting.")


# ---------------------------------------------------------------------------
banner("3. threading by hand")
# ---------------------------------------------------------------------------

results: list[str] = []


def worker(name: str) -> None:
    time.sleep(0.05)
    results.append(name)           # list.append happens to be atomic; see section 6


threads = [threading.Thread(target=worker, args=(f"t{i}",)) for i in range(5)]
started = time.perf_counter()
for thread in threads:
    thread.start()                 # concurrent from here
for thread in threads:
    thread.join()                  # wait for completion
elapsed = time.perf_counter() - started
print(f"5 threads x 0.05s took {elapsed:.3f}s (sequential would be 0.25s)")
print("results collected:", sorted(results))
print("active threads now:", threading.active_count(), "(just the main thread)")


# A thread that raises does NOT crash your program - and that is a hazard.
def explodes() -> None:
    raise RuntimeError("this traceback is printed, then ignored")


# A real program prints the worker's traceback to stderr and carries on. We
# install a quieter hook here only so this script's output stays readable.
threading.excepthook = lambda args: print(
    f"   [thread {args.thread.name} died: {args.exc_type.__name__}: {args.exc_value}]"
)
print("\nStarting a thread that raises:")
noisy = threading.Thread(target=explodes)
noisy.start()
noisy.join()
print("main thread still running:", True, "<- errors in bare threads are easy to lose")
print("(normally the traceback goes to stderr and nothing else happens: silent loss)")


# ---------------------------------------------------------------------------
banner("4. concurrent.futures: map, submit, as_completed, errors")
# ---------------------------------------------------------------------------

URLS = {f"/item/{n}": 0.02 * (n % 3 + 1) for n in range(6)}


def fake_fetch(url: str) -> str:
    """Pretend network call. Fails for one specific URL, on purpose."""
    time.sleep(URLS[url])
    if url.endswith("3"):
        raise ConnectionError(f"connection reset for {url}")
    return f"payload of {url}"


with ThreadPoolExecutor(max_workers=4) as pool:
    # map keeps INPUT order, and re-raises at the item that failed.
    ordered: list[str] = []
    try:
        for result in pool.map(fake_fetch, list(URLS)):
            ordered.append(result)
    except ConnectionError as error:
        print("map stopped at the first failure:", error)
    print("results before the failure:", len(ordered))

with ThreadPoolExecutor(max_workers=4) as pool:
    # submit + as_completed: completion order, and per-task error handling.
    futures = {pool.submit(fake_fetch, url): url for url in URLS}
    ok: list[str] = []
    failed: dict[str, str] = {}
    for future in as_completed(futures):
        url = futures[future]
        try:
            ok.append(future.result())      # re-raises the worker's exception here
        except Exception as error:          # noqa: BLE001 - collect, do not crash
            failed[url] = f"{type(error).__name__}: {error}"
    print("succeeded:", len(ok), " failed:", failed)
    print("one bad task no longer sinks the batch - that is why submit exists")

# The silent-failure trap: never calling .result() throws the error away.
with ThreadPoolExecutor(max_workers=2) as pool:
    pool.submit(explodes)                   # nobody consumes this future
print("submitted a failing task and ignored its future -> error vanished silently")


# ---------------------------------------------------------------------------
banner("5. Processes and the pickling constraint")
# ---------------------------------------------------------------------------

print("What can and cannot cross a process boundary:")
for label, value in [
    ("module-level function", cpu_work),
    ("plain data", {"a": [1, 2, 3]}),
    ("lambda", lambda x: x),
    ("generator", (n for n in range(3))),
    ("thread lock", threading.Lock()),
]:
    try:
        pickle.dumps(value)
        print(f"  picklable     : {label}")
    except Exception as error:  # noqa: BLE001
        print(f"  NOT picklable : {label:<22} ({type(error).__name__})")

print("\nSame four CPU-bound tasks, now in separate processes:")
try:
    with ProcessPoolExecutor(max_workers=4) as pool:
        _, proc_cpu = timed("4 processes", lambda: list(pool.map(cpu_work, [CHUNK] * 4)))
    print(f"  -> {seq_cpu / proc_cpu:.2f}x versus sequential ({seq_cpu:.3f}s).")
    print("     Separate interpreters, separate GILs, real cores.")
except (OSError, RuntimeError, PermissionError) as error:  # pragma: no cover
    print(f"  process pool unavailable in this environment ({type(error).__name__})")
    print("  the API is identical to ThreadPoolExecutor - only the physics differ")

print("\nRules that follow from pickling:")
print("  - worker functions must live at module level")
print("  - guard your entry point with `if __name__ == \"__main__\":`")
print("    (spawn-based platforms re-import __main__ in every child)")
print("  - chunk the work: 1e6 tiny tasks means 1e6 pickle round trips")
print("  - sending 500MB to 4 workers copies it 4 times; send paths or indices")


# ---------------------------------------------------------------------------
banner("6. A race condition, then a lock")
# ---------------------------------------------------------------------------

INCREMENTS = 200_000
THREADS = 4
expected = INCREMENTS * THREADS

unsafe_counter = 0


def increment_unsafe(times: int) -> None:
    global unsafe_counter
    for _ in range(times):
        unsafe_counter += 1          # read, add, write - three separate steps


workers = [threading.Thread(target=increment_unsafe, args=(INCREMENTS,)) for _ in range(THREADS)]
for w in workers:
    w.start()
for w in workers:
    w.join()

print(f"plain += from {THREADS} threads : {unsafe_counter:,} (expected {expected:,})")
print("On CPython 3.11+ this usually comes out right, and that is a TRAP: the")
print("interpreter happens to check for thread switches only at certain bytecodes,")
print("and none of them sit inside `counter += 1`. It is an implementation detail")
print("of one version of one interpreter. Never design around it.")


# The moment anything sits between the read and the write - a function call, an
# attribute lookup that triggers code, a log line - the switch becomes possible
# and the race is real. This is the check-then-act shape, which is everywhere:
# "if there is stock, take one", "if the file is absent, create it".
balance = 100
overdrafts = 0


def withdraw_unsafe(times: int) -> None:
    global balance, overdrafts
    for _ in range(times):
        if balance > 0:              # CHECK
            time.sleep(0)            # any call here allows a thread switch
            balance -= 1             # ACT, on information that may be stale
            if balance < 0:
                overdrafts += 1


workers = [threading.Thread(target=withdraw_unsafe, args=(40,)) for _ in range(THREADS)]
for w in workers:
    w.start()
for w in workers:
    w.join()

print(f"\ncheck-then-act  : balance {balance} from a starting balance of 100")
print(f"                  overdrawn {overdrafts} time(s) - the account went negative")
print("run this script again: the numbers change. Intermittent, load-dependent,")
print("and impossible to reproduce on demand. That is the bug class to fear.")

# The fix: hold a lock across the whole read-modify-write.
balance = 100
lock = threading.Lock()
safe_overdrafts = 0


def withdraw_safe(times: int) -> None:
    global balance, safe_overdrafts
    for _ in range(times):
        with lock:                   # check AND act inside one critical section
            if balance > 0:
                time.sleep(0)
                balance -= 1
                if balance < 0:
                    safe_overdrafts += 1


workers = [threading.Thread(target=withdraw_safe, args=(40,)) for _ in range(THREADS)]
for w in workers:
    w.start()
for w in workers:
    w.join()

print(f"\nwith a lock     : balance {balance}, overdrawn {safe_overdrafts} times")
print("                  exact, every run: the check and the act cannot be split")

# A counter guarded by a lock is exact too, on every interpreter and version.
safe_counter = 0
counter_lock = threading.Lock()


def increment_safe(times: int) -> None:
    global safe_counter
    for _ in range(times):
        with counter_lock:
            safe_counter += 1


workers = [threading.Thread(target=increment_safe, args=(INCREMENTS,)) for _ in range(THREADS)]
for w in workers:
    w.start()
for w in workers:
    w.join()

print(f"\nlocked counter  : {safe_counter:,} (expected {expected:,})")

# Better than locking: do not share mutable state at all.
with ThreadPoolExecutor(max_workers=THREADS) as pool:
    totals = list(pool.map(cpu_count_up, [INCREMENTS] * THREADS))
print(f"no sharing      : {sum(totals):,} (workers returned values; nothing to race)")
print("Locks are the fallback. Returning values is the design.")


# ---------------------------------------------------------------------------
banner("7. asyncio: run, gather, TaskGroup, timeouts, semaphores")
# ---------------------------------------------------------------------------

trace: list[str] = []


async def async_work(name: str, seconds: float) -> str:
    trace.append(f"{name} start")
    await asyncio.sleep(seconds)      # yields to the loop; does not block it
    trace.append(f"{name} end")
    return name.upper()


async def gather_demo() -> list[str]:
    return await asyncio.gather(
        async_work("a", 0.03),
        async_work("b", 0.01),
        async_work("c", 0.02),
    )


started = time.perf_counter()
gathered = asyncio.run(gather_demo())     # ONE asyncio.run, at the top level
elapsed = time.perf_counter() - started
print("gather results  :", gathered, "(argument order, not completion order)")
print("interleaving    :", trace)
print(f"elapsed         : {elapsed:.3f}s for 0.03+0.01+0.02s of sleeping")

# A coroutine that is never awaited does nothing at all.
coro = async_work("never", 0.01)
print("\ncalling an async def returns:", type(coro).__name__, "- the body has not run")
coro.close()                              # tidy up, so no RuntimeWarning is printed
print("forgetting `await` is the most common asyncio bug, and it is silent")


async def failing() -> str:
    raise ValueError("task b failed")


async def gather_with_errors() -> list[Any]:
    return await asyncio.gather(async_work("ok", 0.01), failing(), return_exceptions=True)


mixed = asyncio.run(gather_with_errors())
print("\nreturn_exceptions=True ->", [type(item).__name__ for item in mixed])
print("without it, the first exception propagates and the siblings run unattended")

if sys.version_info >= (3, 11):
    async def taskgroup_demo() -> tuple[str, str]:
        async with asyncio.TaskGroup() as group:
            first = group.create_task(async_work("tg1", 0.01))
            second = group.create_task(async_work("tg2", 0.02))
        return first.result(), second.result()

    print("\nTaskGroup       :", asyncio.run(taskgroup_demo()))

    async def taskgroup_failure() -> str:
        outcome = "no error"
        try:
            async with asyncio.TaskGroup() as group:
                group.create_task(async_work("survivor", 0.05))
                group.create_task(failing())
        except* ValueError as group_error:  # except* unpacks an ExceptionGroup
            # `return` is not allowed inside an except* block, so record instead.
            outcome = f"ExceptionGroup with {len(group_error.exceptions)} error(s)"
        return outcome

    print("TaskGroup fail  :", asyncio.run(taskgroup_failure()), "-> siblings cancelled")
else:  # pragma: no cover - only on 3.10
    print("\nTaskGroup requires Python 3.11+; you are on", sys.version.split()[0])


async def timeout_demo() -> tuple[str, str]:
    fast = await asyncio.wait_for(async_work("fast", 0.01), timeout=0.2)
    try:
        await asyncio.wait_for(async_work("slow", 0.2), timeout=0.02)
        slow = "finished"
    except asyncio.TimeoutError:
        slow = "timed out and was cancelled"
    return fast, slow


print("timeouts        :", asyncio.run(timeout_demo()))


async def semaphore_demo() -> tuple[int, int]:
    """Cap concurrency, and measure the cap without timing anything."""
    in_flight = 0
    peak = 0
    semaphore = asyncio.Semaphore(3)

    async def one(index: int) -> None:
        nonlocal in_flight, peak
        async with semaphore:
            in_flight += 1
            peak = max(peak, in_flight)
            await asyncio.sleep(0.01)
            in_flight -= 1

    await asyncio.gather(*(one(i) for i in range(12)))
    return peak, in_flight


peak, leftover = asyncio.run(semaphore_demo())
print(f"semaphore(3)    : peak concurrency {peak}, in flight at the end {leftover}")


# ---------------------------------------------------------------------------
banner("7b. The blocking-call-in-async trap")
# ---------------------------------------------------------------------------


def blocking_call(seconds: float) -> str:
    """A synchronous function - like requests.get or sqlite3."""
    time.sleep(seconds)
    return "done"


async def wrong() -> list[str]:
    """Calls a blocking function directly: the event loop freezes."""
    return [blocking_call(0.05) for _ in range(4)]


async def right() -> list[str]:
    """Hands the blocking calls to threads, so the loop keeps running."""
    return list(await asyncio.gather(*(asyncio.to_thread(blocking_call, 0.05) for _ in range(4))))


started = time.perf_counter()
asyncio.run(wrong())
wrong_time = time.perf_counter() - started

started = time.perf_counter()
asyncio.run(right())
right_time = time.perf_counter() - started

print(f"blocking inside async : {wrong_time:.3f}s  <- sequential, plus overhead")
print(f"asyncio.to_thread     : {right_time:.3f}s  <- concurrent again")
print("Inside `async def`, anything that waits must be awaited or moved to a thread.")


# ---------------------------------------------------------------------------
banner("8. The decision flowchart, applied")
# ---------------------------------------------------------------------------

DECISIONS = [
    ("fetch 30 URLs", "I/O", 30, "ThreadPoolExecutor - simplest, keeps sync libraries"),
    ("fetch 5,000 URLs", "I/O", 5000, "asyncio - 5,000 threads is 5,000 stacks of memory"),
    ("hash 10,000 files", "CPU in C", 10000, "threads: hashlib releases the GIL"),
    ("parse 40 large CSVs in Python", "CPU", 40, "ProcessPoolExecutor - real cores"),
    ("one 2ms function", "either", 1, "nothing: concurrency costs more than it saves"),
]
for task, kind, count, verdict in DECISIONS:
    print(f"  {task:<32} [{kind:<8} x{count:<5}] -> {verdict}")

print("\nBefore reaching for any of them: can you do LESS work instead?")
print("A cache, an index, or one batched API call beats parallelism and adds no races.")

print()
print("Done. Now open exercises.py in this folder.")
