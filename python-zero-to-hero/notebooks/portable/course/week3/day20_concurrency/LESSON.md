# Day 20 — Concurrency: Threads, Processes, and asyncio

> **Time:** ~4 hours  |  **Prerequisites:** Day 19

## What you'll be able to do after today
- Decide whether a workload is CPU-bound or I/O-bound, and pick threads, processes, async or nothing at all on purpose.
- State accurately what the GIL does and does not prevent, without repeating folklore.
- Run work in parallel with `ThreadPoolExecutor` and `ProcessPoolExecutor`, and explain the pickling rules that limit the second.
- Produce a race condition on demand, then fix it with a lock, and explain why the bug is intermittent.
- Write `async def` code: `await`, `asyncio.run`, `gather`, `TaskGroup`, timeouts.
- Recognise the blocking-call-in-async trap in a code review and fix it with `to_thread`.

## Why this matters

A script that fetches 200 URLs one at a time takes 200 round trips of waiting. The
same script with a thread pool takes about as long as the slowest few. That is not
a micro-optimisation; it is the difference between a job that runs in 3 seconds and
one that runs in 5 minutes.

The other reason is defensive. Concurrency introduces the worst class of bug you
will meet: intermittent, load-dependent, and gone when you look at it. A shared
counter that is wrong 1 time in 10,000 will not reproduce on your laptop and will
corrupt data in production. Today you produce that bug deliberately, so you
recognise its shape forever.

And there is a cultural reason: "Python can't do concurrency because of the GIL" is
repeated everywhere by people who cannot say what the GIL is. After today you can,
and you will know which of the three tools applies.

---

## 1. The only question that matters first: what is it waiting for?

Every slow program is slow for one of two reasons.

**I/O-bound**: your CPU is idle, waiting for something outside the process — a
network response, a disk read, a database query, another service. The CPU sits at
2% while wall-clock time passes.

**CPU-bound**: your CPU is at 100% doing arithmetic — hashing, image processing,
parsing millions of rows, model inference, brute-force search.

```python
# I/O-bound: 99.9% of this is waiting for the network.
data = requests.get(url, timeout=10).json()

# CPU-bound: 100% of this is your CPU adding numbers.
total = sum(n * n for n in range(50_000_000))
```

Diagnose before you optimise: run the code and watch the CPU. At 100% of one
core, it is CPU-bound. Near 0%, it is waiting. `time.perf_counter` around the
suspect section, or `cProfile`, tells you which line.

This single question picks your tool:

| Bound by | Use | Why |
|---|---|---|
| I/O, tens of tasks | `ThreadPoolExecutor` | waiting happens in parallel; simplest change |
| I/O, hundreds/thousands | `asyncio` | thousands of threads cost memory; tasks cost almost nothing |
| CPU | `ProcessPoolExecutor` | separate interpreters use separate cores |
| Nothing measurable | leave it alone | concurrency is a real complexity cost |

---

## 2. The GIL, accurately

The **Global Interpreter Lock** is a mutex inside CPython that allows only one
thread to execute Python bytecode at a time.

What that means, precisely:

**The GIL does prevent:**
- Two threads running Python bytecode simultaneously. Pure-Python CPU work does
  not get faster with threads; with contention it can get slightly slower.

**The GIL does not prevent:**
- Threads from being useful for I/O. A thread **releases** the GIL while it waits
  on a socket, a file, or `time.sleep`. Ten threads waiting on ten HTTP requests
  wait simultaneously — that is real, useful concurrency.
- C extensions from using multiple cores. NumPy, `hashlib`, compression and most
  serious numeric libraries release the GIL around their C loops, so they *do*
  parallelise across threads.
- Processes from using all cores. Each process has its own interpreter and its own
  GIL.
- **Race conditions.** This is the one people get wrong. The GIL protects the
  interpreter's internal state, not yours. A thread can be suspended between any
  two bytecodes, including in the middle of `counter += 1`. See section 6.

Two more facts worth having: `sys.setswitchinterval` (default 5 ms) controls how
often the interpreter considers switching threads, and Python 3.13 ships an
experimental free-threaded build with no GIL — worth knowing about, not worth
depending on yet. In 3.12+ some things (per-interpreter GILs) are moving; the
model above is the one to reason with today.

---

## 3. `threading`

```python
import threading
import time


def worker(name: str, results: list[str]) -> None:
    time.sleep(0.1)                 # stands in for a network call
    results.append(name)


results: list[str] = []
threads = [
    threading.Thread(target=worker, args=(f"t{i}", results))
    for i in range(5)
]
for thread in threads:
    thread.start()                  # begins running concurrently
for thread in threads:
    thread.join()                   # wait for it to finish

print(len(results))                 # 5, after ~0.1s total, not 0.5s
```

`start()` runs the target concurrently; `join()` waits. Threads share memory,
which is what makes them convenient and dangerous.

Details worth knowing: `daemon=True` threads do not keep the process alive, so use
them for background loops you are happy to kill; a thread that raises prints a
traceback and dies without affecting the others, which means **you can lose errors
silently**; and there is no way to kill a thread from outside — you ask it to stop
with a flag or an `Event`.

In practice you rarely write `Thread` by hand, because you almost always want
results and error propagation, and that is what the executor gives you.

---

## 4. `concurrent.futures`: the API to actually use

One interface, two backends. This is the most valuable thing in today's lesson.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch(url: str) -> str:
    ...                             # some I/O-bound work


urls = [f"https://example.com/{n}" for n in range(20)]

with ThreadPoolExecutor(max_workers=8) as pool:
    # map: results in INPUT order, exceptions raised when you reach that item
    for result in pool.map(fetch, urls):
        print(result)
```

`submit` gives you a `Future` per task and lets you handle failures individually:

```python
with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(fetch, url): url for url in urls}
    for future in as_completed(futures):        # COMPLETION order, fastest first
        url = futures[future]
        try:
            print(url, future.result())          # re-raises the worker's exception
        except Exception as error:
            print(f"{url} failed: {error}")      # one failure does not sink the rest
```

The rules:

- `pool.map` preserves input order; `as_completed` yields whichever finishes first.
- An exception inside a worker is stored in the future and re-raised by
  `future.result()`. If you never call `.result()`, **the error disappears**.
- The `with` block waits for everything to finish (`shutdown(wait=True)`).
- `max_workers` for threads: I/O-bound, so 8–32 is usually right; more threads
  than sockets you can usefully have open is waste.

Switching to processes is one word:

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as pool:      # was ThreadPoolExecutor
    totals = list(pool.map(count_primes, ranges))
```

Same API, different physics: each worker is a separate OS process with its own
interpreter and its own GIL, so CPU-bound work scales with cores.

---

## 5. `multiprocessing` and the pickling constraint

Processes do not share memory, so arguments and return values are **pickled**,
sent through a pipe, and unpickled on the other side. That has consequences you
will hit within your first hour:

```python
import pickle

pickle.dumps(lambda x: x)         # PicklingError: Can't pickle <lambda>
```

What cannot cross a process boundary: lambdas, locally-defined functions and
classes, open file handles, sockets, database connections, generators, and
anything holding a lock. What can: module-level functions and classes, and plain
data.

Consequences to design around:

1. **The worker function must be defined at module level** so the child can import
   it by name.
2. **On Windows and macOS** (spawn start method) the child re-imports your
   `__main__` module, so any top-level code runs again. Guard your entry point:
   ```python
   if __name__ == "__main__":
       main()
   ```
   Without that guard you get an infinite process explosion. On Linux the default
   is fork and you will not notice — until CI runs on macOS.
3. **Data transfer costs.** Sending a 500 MB DataFrame to four workers copies it
   four times. If the work per item is small, pickling dominates and the parallel
   version is slower than the sequential one. Send indices or file paths, and let
   the worker load its own slice.
4. **Chunk your work.** 1,000,000 tiny tasks means 1,000,000 pickle round trips.
   Split the range into as many chunks as workers and hand each worker a range.

`multiprocessing` itself gives you the lower-level pieces — `Process`, `Queue`,
`Pool`, `Value`, `Manager`, and shared memory. Reach for `ProcessPoolExecutor`
first; drop to `multiprocessing` when you need long-lived workers with queues.

---

## 6. Race conditions, produced then fixed

`counter += 1` is not one operation. It is: read `counter`, add one, store the
result. If a thread is suspended between the read and the write, another thread's
increment disappears — a **lost update**.

```python
import threading

counter = 0


def increment_many(times: int) -> None:
    global counter
    for _ in range(times):
        counter += 1                   # read, add, write - three steps


threads = [threading.Thread(target=increment_many, args=(200_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)          # expected 800000
```

Run that on CPython 3.11 or newer and it will usually print exactly `800000`,
which teaches the wrong lesson unless you know why: this interpreter checks
whether to switch threads only at certain bytecodes (loop jumps, calls), and none
of them sit inside those three steps. On older CPython, on other
implementations, and in the free-threaded build, the same code loses updates. It
is an implementation detail of one version of one interpreter. **Never design
around it.**

The moment anything sits between the read and the write — a function call, a log
line, a property, an `await` — the switch becomes possible and the race is real.
That is the **check-then-act** shape, and it is everywhere: "if there is stock,
take one", "if the file does not exist, create it", "if the balance is positive,
withdraw".

```python
import threading
import time

balance = 100
overdrafts = 0


def withdraw(times: int) -> None:
    global balance, overdrafts
    for _ in range(times):
        if balance > 0:              # CHECK
            time.sleep(0)            # any call here permits a thread switch
            balance -= 1             # ACT, possibly on stale information
            if balance < 0:
                overdrafts += 1


threads = [threading.Thread(target=withdraw, args=(40,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(balance, overdrafts)    # e.g. -3 3 : the account went negative
```

Four threads each checked "is the balance above zero?", all saw `1`, and all
withdrew. The balance is now negative, which the code explicitly tried to
prevent. This is why "the GIL makes Python thread-safe" is false: the GIL keeps
the interpreter's own structures coherent, it does not make *your* multi-step
operations atomic.

The fix is a **lock** — only one thread may hold it at a time — held across the
whole check-and-act:

```python
lock = threading.Lock()


def withdraw(times: int) -> None:
    global balance
    for _ in range(times):
        with lock:                     # acquire, and release even on exception
            if balance > 0:
                balance -= 1

# balance lands on exactly 0, every single run
```

What to remember:

- The lock must cover the **whole** read-modify-write. Locking only the
  subtraction fixes nothing, because the stale check already happened.
- The critical section should be as **small** as possible while still covering
  that: a lock held during a network call serialises your whole program and you
  have lost the concurrency you were paying for.
- Two locks acquired in different orders by different threads is a **deadlock**.
  Always acquire in a documented, consistent order.
- `with lock:` rather than `lock.acquire()`/`release()`, so an exception cannot
  leave it held forever.
- Better than locking: **do not share mutable state.** Have each worker return a
  value and combine the results in the main thread. `pool.map` encourages exactly
  that.
- `queue.Queue` is already thread-safe, and is the right way to hand work between
  threads.
- `threading.Lock` is not reentrant: acquiring it twice in the same thread
  deadlocks. Use `threading.RLock` when a locked function calls another locked
  function.

Race conditions are intermittent because they depend on where the interpreter
happens to switch threads, which depends on timing, load and luck. That is
precisely why you cannot test them into submission — you have to design them out.

---

## 7. `asyncio`: one thread, thousands of waits

Threads let the operating system switch between waiting tasks. `asyncio` lets
*your program* switch, at points you mark, in a single thread. There is one **event
loop** running many **coroutines**; each one runs until it hits an `await`, then
hands control back so another can run.

```python
import asyncio


async def work(name: str, seconds: float) -> str:
    print(f"{name} starting")
    await asyncio.sleep(seconds)        # yields control; does NOT block the loop
    print(f"{name} done")
    return name.upper()


async def main() -> list[str]:
    # gather runs them concurrently and returns results in ARGUMENT order
    return await asyncio.gather(
        work("a", 0.03),
        work("b", 0.01),
        work("c", 0.02),
    )


print(asyncio.run(main()))     # ['A', 'B', 'C'] after ~0.03s, not 0.06s
```

The vocabulary, precisely:

- `async def` defines a **coroutine function**. Calling it returns a coroutine
  object and runs **nothing**.
- `await` runs an awaitable and suspends the current coroutine until it finishes.
- `asyncio.run(main())` starts the event loop, runs one coroutine to completion,
  and shuts the loop down. Call it **once**, at the top of your program.
- A **task** (`asyncio.create_task(coro)`) schedules a coroutine to run
  concurrently right now.

> **Gotcha:** `work("a", 1)` without `await` produces
> `RuntimeWarning: coroutine 'work' was never awaited` and does nothing at all.
> Forgetting `await` is the most common asyncio bug, and it fails quietly.

### `gather` versus `TaskGroup`

```python
results = await asyncio.gather(*coros, return_exceptions=True)
```

`gather` collects results in argument order. By default the first exception
propagates while the other tasks keep running unattended;
`return_exceptions=True` puts exception objects in the result list instead, which
is usually what a batch job wants.

`asyncio.TaskGroup` (3.11+) is the modern, safer replacement:

```python
async def main():
    async with asyncio.TaskGroup() as group:       # Python 3.11+
        task_a = group.create_task(work("a", 0.03))
        task_b = group.create_task(work("b", 0.01))
    # on exit: every task is finished
    return task_a.result(), task_b.result()
```

If one task fails, the group **cancels the others** and raises an
`ExceptionGroup` — no orphaned tasks quietly continuing after an error, which is
`gather`'s worst behaviour. Use `TaskGroup` for new code on 3.11+; know `gather`
because it is everywhere.

### Timeouts

```python
try:
    result = await asyncio.wait_for(slow(), timeout=0.05)
except asyncio.TimeoutError:            # TimeoutError in 3.11+, aliased
    result = "gave up"

async with asyncio.timeout(0.05):       # 3.11+, applies to a whole block
    await step_one()
    await step_two()
```

A cancelled coroutine receives `asyncio.CancelledError` at its `await` point, so
cleanup belongs in `finally`. Never swallow `CancelledError`.

### The blocking-call trap

This is the mistake that makes people conclude "asyncio is slow":

```python
async def broken(url: str):
    return requests.get(url, timeout=10).json()   # BLOCKS the whole event loop
```

`requests` is synchronous. While it waits, the single thread running the event
loop is stuck, and **every other coroutine is frozen**. Your concurrent program
became sequential, plus overhead. The same applies to `time.sleep`, `open().read()`,
`sqlite3`, and any CPU-heavy loop.

Three correct options:

```python
# 1. Use an async-native library.
async with httpx.AsyncClient() as client:
    response = await client.get(url, timeout=10)

# 2. Push the blocking call to a thread (3.9+).
data = await asyncio.to_thread(requests.get, url, timeout=10)

# 3. For CPU-bound work, push it to a process pool.
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(process_pool, heavy_function, arg)
```

Rule of thumb: inside `async def`, every call that touches the network, the disk,
or takes longer than a millisecond should be `await`ed or handed to a thread.

### Limiting concurrency

Firing 10,000 requests at once will get you rate-limited or run you out of file
descriptors. A `Semaphore` caps how many run at a time:

```python
async def fetch_all(urls: list[str], limit: int = 10) -> list[str]:
    semaphore = asyncio.Semaphore(limit)

    async def one(url: str) -> str:
        async with semaphore:              # at most `limit` inside this block
            return await fetch(url)

    return await asyncio.gather(*(one(url) for url in urls))
```

---

## 8. Choosing: the decision flowchart

```
                    Is it actually slow? (measure it)
                              |
                    no -------+------- yes
                    |                   |
             leave it alone        What is it waiting for?
                                        |
                        +---------------+----------------+
                        |                                |
                   THE NETWORK / DISK                 THE CPU
                   (I/O-bound)                        (CPU-bound)
                        |                                |
              How many tasks?                    Is the hot loop in
                        |                        C (numpy/hashlib)?
          +-------------+-------------+                  |
          |                           |            +-----+------+
    tens (< ~100)            hundreds/thousands    |            |
          |                           |           yes          no
  ThreadPoolExecutor            asyncio            |            |
  (simplest; keep your      (needs async-native   threads    ProcessPool
   sync libraries)           libraries all the    release    Executor
                             way down)            the GIL    (+ chunk the
                                                             work; mind
                                                             pickling)
```

Extra checks before you add concurrency at all:

- Can you do **less work** instead? A better algorithm, a cache, an index, one
  batched API call instead of 200 — all beat parallelism, and none of them add
  race conditions.
- Are you allowed? Rate limits and database connection pools cap useful
  parallelism regardless of your machine.
- Concurrency costs you: harder debugging, nondeterministic tests, and a class of
  bug that only appears under load. Pay it deliberately.

---

## 9. Testing concurrent code

Concurrency is where flaky tests come from, so be strict:

- **Test the logic, not the scheduler.** Partitioning, retry decisions, result
  merging and error collection are pure functions — test those exhaustively.
- Keep sleeps tiny (≤ 0.02 s) and never assert on how long something took.
- Assert on **invariants**: every task ran exactly once, the total is exact,
  results are in input order, at most N ran concurrently.
- To check a concurrency limit, have the fake worker record the current number of
  in-flight calls and assert the maximum observed.
- To prove a lock works, run enough iterations that the unlocked version would
  almost certainly fail, and assert the locked total is **exact**.
- `asyncio.run(coro)` is all you need to test coroutines from a normal test
  function; `pytest-asyncio` only becomes useful for async fixtures.

Today's graded tests follow all of that: no sleep over 0.02 s, no timing
assertions, no processes.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Threads for CPU-bound work | No speed-up, sometimes slower | `ProcessPoolExecutor` |
| Processes for tiny tasks | Slower than sequential | Chunk the work, or use threads |
| Never calling `future.result()` | Exceptions vanish silently | Always consume results |
| `counter += 1` from threads | Total is slightly wrong, intermittently | `with lock:` or return values |
| Lock held across I/O | Concurrency gone, no error | Shrink the critical section |
| Two locks, two orders | Deadlock; the program just stops | One documented acquisition order |
| `pool.map(lambda x: ..., xs)` with processes | `PicklingError: Can't pickle <lambda>` | Module-level function |
| No `if __name__ == "__main__":` | Process explosion on macOS/Windows | Guard the entry point |
| `requests.get` inside `async def` | Everything serialises; asyncio "is slow" | `httpx`, or `asyncio.to_thread` |
| Forgetting `await` | `RuntimeWarning: coroutine was never awaited` | `await` it, or `create_task` |
| `asyncio.run` called twice / nested | `RuntimeError: This event loop is already running` | One `run` at the top; `await` inside |
| Unbounded `gather` over 10k urls | Rate limits, socket exhaustion | `asyncio.Semaphore(limit)` |
| Swallowing `CancelledError` | Tasks that refuse to stop | Let it propagate; clean up in `finally` |
| Asserting on elapsed time in tests | Flaky suite | Assert invariants instead |

---

## Mental model

Three kitchens.

```
SEQUENTIAL              THREADS                      ASYNCIO                 PROCESSES
one cook,               several cooks,               one very attentive      several separate
one dish at a time      one hob (the GIL)            cook who never waits    kitchens
                                                     idly
[boil] wait...          [boil][chop][boil]           [start boil] -> [chop]  [kitchen 1: chop]
[chop] wait...          all three wait at once,      -> [start oven] ->      [kitchen 2: chop]
[bake] wait...          only one may stir            [stir when a timer      [kitchen 3: chop]
                        the pot at a time            rings]                  truly parallel

good for: nothing slow  good for: waiting            good for: thousands     good for: chopping
                        (I/O), tens of tasks         of waits, one thread    (CPU), N cores
```

The GIL is the single hob: it stops two cooks stirring simultaneously, but it does
not stop three pots boiling simultaneously. Waiting is what parallelises for free;
stirring is not.

And the async rule in one line: **inside `async def`, anything that waits must be
`await`ed, or the whole kitchen stops.**

---

## Practice

1. Run the demo. It shows the race condition failing, the GIL's effect on threads
   versus processes, and a full asyncio tour — in under two seconds:
   ```bash
   python course/week3/day20_concurrency/examples.py
   ```
   Run it twice and notice the unlocked counter differs each time. That is the
   lesson.
2. Implement the ten exercises in `exercises.py`: 1 is the decision model, 2–4 are
   threads and locks, 5–6 are the process/pickling constraints, 7–10 are asyncio,
   ending with an async paginated crawl.
3. Grade from the course root:
   ```bash
   python check.py day20
   ```
4. Then run the grader repeatedly — `for i in 1 2 3; do python check.py day20; done`
   — because concurrent code that passes only sometimes has not passed.

---

## Recall check

1. How do you tell whether a workload is I/O-bound or CPU-bound?
2. What exactly does the GIL prevent, and what does it not prevent?
3. Why do threads help with 50 HTTP requests but not with 50 million multiplications?
4. What is the difference between `pool.map` and `as_completed`?
5. Where do exceptions raised inside a worker go?
6. Why are `counter += 1` and check-then-act unsafe across threads even though the GIL exists?
7. Give two ways to avoid needing a lock at all.
8. Name three things that cannot be sent to a process worker, and why.
9. What does `asyncio.run` do, and how many times should it appear in a program?
10. What breaks when you call `requests.get` inside `async def`, and what are the two fixes?
11. Why is `TaskGroup` safer than `gather`?
12. How do you test that a concurrency limit of 5 is respected, without timing anything?

<details>
<summary>Answers</summary>

1. Measure. If one core sits at 100%, it is CPU-bound; if the CPU is near idle
   while wall-clock time passes, it is waiting on I/O. `cProfile` or a
   `perf_counter` around the suspect section tells you which line.
2. It prevents two threads from executing Python bytecode at the same time. It
   does not prevent parallel *waiting* (threads release it during I/O), does not
   stop C extensions from using multiple cores, does not apply across processes,
   and does not make your read-modify-write operations atomic.
3. HTTP requests spend their time waiting, and a thread releases the GIL while it
   waits, so the waits overlap. Multiplications need the interpreter, and only one
   thread may run bytecode at a time, so they take turns instead of overlapping.
4. `map` yields results in input order, blocking until each is ready.
   `as_completed` yields futures in completion order, fastest first, which lets you
   handle each result and each failure as soon as it happens.
5. Into the `Future`. They are re-raised when you call `future.result()` (or when
   `map`'s iterator reaches that item). If you never consume the result, the
   exception is never seen.
6. Because both are multi-step: read/add/store, or check/then/act. The GIL only
   guarantees that one thread runs bytecode at a time; it does not make your
   sequence of steps atomic, so another thread can act on the value you already
   read. (On CPython 3.11+ the bare `counter += 1` case usually survives because
   of where the interpreter checks for thread switches — an implementation detail
   to never rely on. Put any call between the read and the write and the race
   appears immediately.)
7. Have each worker return a value and combine results in the main thread (e.g.
   `pool.map`); or pass work through a `queue.Queue`, which is already
   thread-safe. Both remove shared mutable state instead of guarding it.
8. Lambdas and locally-defined functions (they cannot be looked up by name in the
   child), open sockets/file handles and database connections (OS resources that
   do not survive the trip), and generators or objects holding locks. Everything
   crossing a process boundary must be picklable.
9. It creates an event loop, runs the given coroutine until it finishes, then
   closes the loop. It should appear once, at the top level of the program; inside
   async code you `await` instead.
10. `requests` is synchronous, so it blocks the single thread running the event
    loop and freezes every other coroutine. Fix with an async-native client
    (`httpx.AsyncClient`) or by moving the call off the loop with
    `asyncio.to_thread`.
11. If one task fails, `TaskGroup` cancels the siblings and raises an
    `ExceptionGroup`, so no task is left running unattended. Plain `gather`
    propagates the first exception while the other tasks continue in the
    background, unobserved.
12. Make the fake worker increment a counter of in-flight calls on entry and
    decrement it on exit, recording the maximum ever seen. Assert that the maximum
    is exactly the limit (or at most the limit). No timing involved, so no
    flakiness.

</details>
