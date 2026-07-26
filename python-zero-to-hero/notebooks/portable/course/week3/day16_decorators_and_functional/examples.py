"""Day 16 — runnable demonstrations of functional Python and decorators.

Run it:

    python course/week3/day16_decorators_and_functional/examples.py

Sections match LESSON.md. Two sections deliberately print *wrong* output first
(late binding in section 5, missing functools.wraps in section 7) so you can see
the bug before the fix.
"""

from __future__ import annotations

import functools
import logging
import operator
import sys
import time
from functools import reduce
from typing import Any, Callable


def banner(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


# ---------------------------------------------------------------------------
banner("1. Functions are values")
# ---------------------------------------------------------------------------


def shout(text: str) -> str:
    return text.upper() + "!"


noisy = shout                     # no parentheses: bind the object, not a call
print("noisy('hello')  :", noisy("hello"), "(expected HELLO!)")
print("shout.__name__  :", shout.__name__)
print("type(shout)     :", type(shout).__name__)


def double(n: int) -> int:
    return n * 2


def square(n: int) -> int:
    return n * n


# A dict of functions replaces a long if/elif dispatch chain.
operations: dict[str, Callable[[int], int]] = {"double": double, "square": square}
print("dispatch square :", operations["square"](7), "(expected 49)")
for name, func in operations.items():
    print(f"  {name}(5) -> {func(5)}")


# ---------------------------------------------------------------------------
banner("2. lambda, and where it does not belong")
# ---------------------------------------------------------------------------

people = [("Ada", 36), ("Grace", 45), ("Alan", 41)]
print("by age          :", sorted(people, key=lambda person: person[1]))

# Assigning a lambda to a name loses the name in tracebacks. Compare:
bad_add = lambda a, b: a + b            # noqa: E731 - shown on purpose
print("lambda __name__ :", bad_add.__name__, "(useless in a traceback)")
print("def __name__    :", double.__name__, "(this is what you want)")

# A built-in beats a lambda whenever one exists.
words = ["Beta", "alpha", "Gamma"]
print("key=lambda      :", sorted(words, key=lambda s: s.lower()))
print("key=str.lower   :", sorted(words, key=str.lower), "(same, clearer)")
print("itemgetter(1)   :", sorted(people, key=operator.itemgetter(1))[0])

# The one statement-ish thing a lambda may contain: a conditional expression.
sign = lambda n: "neg" if n < 0 else "pos"      # noqa: E731
print("conditional     :", sign(-4), sign(4))


# ---------------------------------------------------------------------------
banner("3. map / filter versus comprehensions")
# ---------------------------------------------------------------------------

numbers = [1, 2, 3, 4, 5, 6]

print("map squares     :", list(map(lambda n: n * n, numbers)))
print("comprehension   :", [n * n for n in numbers], "(preferred)")
print("filter evens    :", list(filter(lambda n: n % 2 == 0, numbers)))
print("comprehension   :", [n for n in numbers if n % 2 == 0], "(preferred)")

# Case 1 where map wins: the function already has a name.
print("map(str.strip)  :", list(map(str.strip, [" a ", " b "])))
print("map(int)        :", list(map(int, ["1", "2", "3"])))

# Case 2: two iterables walked in lockstep.
print("map two lists   :", list(map(lambda a, b: a * b, [1, 2, 3], [10, 20, 30])))

# Case 3: filter(None, ...) drops every falsy value.
print("filter(None,..) :", list(filter(None, [0, 1, "", "x", None, [], [2]])))

# map/filter are lazy iterators, with the Day 15 one-shot gotcha.
lazy = map(square, [1, 2, 3])
print("map object      :", lazy)
print("first sum       :", sum(lazy), "(expected 14)")
print("second sum      :", sum(lazy), "(expected 0 - consumed)")


# ---------------------------------------------------------------------------
banner("4. sorted with key: single field, multi field, stability")
# ---------------------------------------------------------------------------

fruit = ["banana", "kiwi", "apple", "Fig"]
print("default sort    :", sorted(fruit), "(capital F first: code points)")
print("key=str.lower   :", sorted(fruit, key=str.lower))
print("key=len         :", sorted(fruit, key=len))
print("len, reversed   :", sorted(fruit, key=len, reverse=True))

players = [
    {"name": "ada", "score": 10},
    {"name": "bo", "score": 30},
    {"name": "cy", "score": 10},
]

# Tuple key: score descending (negated), then name ascending as tie-break.
ranked = sorted(players, key=lambda p: (-p["score"], p["name"]))
print("ranked          :", [p["name"] for p in ranked], "(expected bo, ada, cy)")

# Two stable passes achieve the same for fields you cannot negate.
by_name = sorted(players, key=lambda p: p["name"])
two_pass = sorted(by_name, key=lambda p: p["score"], reverse=True)
print("two stable sorts:", [p["name"] for p in two_pass], "(same answer)")
print("max by score    :", max(players, key=lambda p: p["score"])["name"])


# ---------------------------------------------------------------------------
banner("5. Closures, nonlocal, and the late-binding bug")
# ---------------------------------------------------------------------------


def make_multiplier(factor: int) -> Callable[[int], int]:
    def multiply(value: int) -> int:
        return value * factor         # `factor` survives after the outer return
    return multiply


triple = make_multiplier(3)
double_it = make_multiplier(2)
print("triple(10)      :", triple(10), "(expected 30)")
print("double_it(10)   :", double_it(10), "(expected 20)")
print("captured cell   :", triple.__closure__[0].cell_contents, "(the 3)")


def make_counter() -> Callable[[], int]:
    count = 0

    def increment() -> int:
        nonlocal count                # without this: UnboundLocalError
        count += 1
        return count

    return increment


tick = make_counter()
print("counter         :", tick(), tick(), tick(), "(expected 1 2 3)")
print("independent     :", make_counter()(), "(a fresh closure starts at 1)")

# THE BUG: all three lambdas share one `offset` variable.
broken = []
for offset in [1, 10, 100]:
    broken.append(lambda x: x + offset)
print("broken adders   :", [add(0) for add in broken], "(WRONG: wanted 1,10,100)")

# Fix 1: default argument, evaluated at definition time.
fixed_default = [lambda x, offset=offset: x + offset for offset in [1, 10, 100]]
print("default-arg fix :", [add(0) for add in fixed_default])


# Fix 2: a factory, so each closure gets its own scope. Prefer this.
def make_adder(offset: int) -> Callable[[int], int]:
    def add(x: int) -> int:
        return x + offset
    return add


fixed_factory = [make_adder(offset) for offset in [1, 10, 100]]
print("factory fix     :", [add(0) for add in fixed_factory], "(clearest)")


# ---------------------------------------------------------------------------
banner("6. Writing a decorator, first without the @ sugar")
# ---------------------------------------------------------------------------


def announce(func):
    def wrapper(*args, **kwargs):          # accept any signature
        print(f"   -> calling {func.__name__}")
        result = func(*args, **kwargs)     # do the real work
        print(f"   <- {func.__name__} returned {result!r}")
        return result                      # returning is not optional
    return wrapper


def add(a: int, b: int) -> int:
    return a + b


manual = announce(add)                     # this is all a decorator does
print("manual wrap     :", manual(2, 3))


@announce                                  # identical to add2 = announce(add2)
def add2(a: int, b: int) -> int:
    return a + b


print("@ sugar         :", add2(4, 5))


def forgets_return(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)              # BUG: no return
    return wrapper


print("missing return  :", forgets_return(add)(2, 3), "(None - the classic bug)")


# ---------------------------------------------------------------------------
banner("7. functools.wraps: what breaks without it")
# ---------------------------------------------------------------------------


def naive(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def careful(func):
    @functools.wraps(func)                 # one line, always
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def area(width: float, height: float) -> float:
    """Return the area of a rectangle."""
    return width * height


naive_area = naive(area)
careful_area = careful(area)

print("naive   __name__:", naive_area.__name__, "(wrong)")
print("naive   __doc__ :", naive_area.__doc__, "(documentation lost)")
print("careful __name__:", careful_area.__name__)
print("careful __doc__ :", careful_area.__doc__)
print("careful wrapped :", careful_area.__wrapped__.__name__, "(original kept)")

import inspect  # noqa: E402 - imported here to keep the demo next to its point

print("naive   sig     :", inspect.signature(naive_area), "(a lie)")
print("careful sig     :", inspect.signature(careful_area), "(the truth)")


# ---------------------------------------------------------------------------
banner("8. Decorators with arguments, and stacking")
# ---------------------------------------------------------------------------


def repeat(times: int):
    """Decorator factory: repeat(3) returns a decorator."""
    if times < 1:
        raise ValueError("times must be >= 1")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper

    return decorator


calls: list[str] = []


@repeat(3)
def ping() -> str:
    calls.append("ping")
    return "pong"


print("ping()          :", ping(), "after", len(calls), "actual calls (expected 3)")


# Stacking: written top to bottom, applied bottom to top, run outside in.
order: list[str] = []


def outer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        order.append("outer in")
        result = func(*args, **kwargs)
        order.append("outer out")
        return result
    return wrapper


def inner(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        order.append("inner in")
        result = func(*args, **kwargs)
        order.append("inner out")
        return result
    return wrapper


@outer          # applied second, runs first
@inner          # applied first, runs second
def work() -> str:
    order.append("body")
    return "done"


work()
print("execution order :", order)
print("equivalent to   : work = outer(inner(work))")


# ---------------------------------------------------------------------------
banner("9a. Timing decorator")
# ---------------------------------------------------------------------------


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.perf_counter()       # monotonic; never time.time()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.durations.append(time.perf_counter() - started)
    wrapper.durations = []
    return wrapper


@timed
def slow_sum(n: int) -> int:
    return sum(range(n))


slow_sum(100_000)
slow_sum(200_000)
print("calls timed     :", len(slow_sum.durations), "(expected 2)")
print("both positive   :", all(d >= 0 for d in slow_sum.durations))
print(f"second/first    : {slow_sum.durations[1] / max(slow_sum.durations[0], 1e-9):.1f}x")


@timed
def explodes() -> None:
    raise RuntimeError("boom")


try:
    explodes()
except RuntimeError:
    pass
print("failed call timed:", len(explodes.durations) == 1, "(try/finally earns its keep)")


# ---------------------------------------------------------------------------
banner("9b. Caching: lru_cache, and the hand-rolled version")
# ---------------------------------------------------------------------------

raw_calls = 0


def fib_slow(n: int) -> int:
    global raw_calls
    raw_calls += 1
    return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)


print("fib_slow(22)    :", fib_slow(22), "in", raw_calls, "calls")


@functools.lru_cache(maxsize=128)
def fib_fast(n: int) -> int:
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)


print("fib_fast(22)    :", fib_fast(22))
print("cache_info      :", fib_fast.cache_info())
print("fib_fast(120)   :", fib_fast(120), "(instantly; try that uncached)")
fib_fast.cache_clear()
print("after clear     :", fib_fast.cache_info())


def memoize(func):
    """The 8-line version of lru_cache, so you know what is inside."""
    cache: dict[tuple, Any] = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    wrapper.cache = cache                  # expose it for tests and humans
    return wrapper


work_done = 0


@memoize
def expensive(n: int) -> int:
    global work_done
    work_done += 1
    return n * n


print("expensive(4) x3 :", expensive(4), expensive(4), expensive(4))
print("real work done  :", work_done, "(expected 1)")
print("cache contents  :", expensive.cache)

try:
    fib_fast([1, 2])                       # lists are unhashable
except TypeError as error:
    print("list argument   : TypeError:", error)


# ---------------------------------------------------------------------------
banner("9c. Retry with backoff, and 9d. logging")
# ---------------------------------------------------------------------------


class Flaky(Exception):
    """A pretend transient network error."""


def retry(attempts: int = 3, delay: float = 0.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    last_error = error
                    wrapper.attempts_made = attempt
                    if attempt < attempts and delay:
                        time.sleep(delay * 2 ** (attempt - 1))   # exponential
            raise last_error
        wrapper.attempts_made = 0
        return wrapper
    return decorator


failures_left = 2


@retry(attempts=4, delay=0.0, exceptions=(Flaky,))
def flaky_fetch() -> str:
    global failures_left
    if failures_left > 0:
        failures_left -= 1
        raise Flaky("connection reset")
    return "payload"


print("flaky_fetch()   :", flaky_fetch(), "after", flaky_fetch.attempts_made, "failures")


@retry(attempts=2, exceptions=(Flaky,))
def always_fails() -> str:
    raise Flaky("still down")


try:
    always_fails()
except Flaky as error:
    print("exhausted retry : re-raised", type(error).__name__, "-", error)

# Logging decorator. A real logger, configured to print to stdout for the demo.
# Send log records to stdout so they interleave with print() in a readable order.
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("   [%(levelname)s] %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_handler], force=True)
logger = logging.getLogger("day16")


def log_calls(level: int = logging.INFO):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(level, "%s%r", func.__name__, args)
            try:
                result = func(*args, **kwargs)
            except Exception:
                logger.exception("%s failed", func.__name__)
                raise                       # log AND re-raise; never swallow
            logger.log(level, "%s -> %r", func.__name__, result)
            return result
        return wrapper
    return decorator


@log_calls()
def divide(a: float, b: float) -> float:
    return a / b


divide(10, 4)
try:
    divide(1, 0)
except ZeroDivisionError:
    print("   (exception logged with traceback, then re-raised)")
logging.disable(logging.CRITICAL)           # quiet for the rest of the script


# ---------------------------------------------------------------------------
banner("10. partial, reduce, and composition")
# ---------------------------------------------------------------------------


def power(base: float, exponent: float) -> float:
    return base**exponent


square_p = functools.partial(power, exponent=2)
cube_p = functools.partial(power, exponent=3)
print("partial squares :", square_p(5), cube_p(2), "(expected 25 8)")
print("partial keywords:", square_p.keywords, "and .func ->", square_p.func.__name__)
print("hex parser      :", list(map(functools.partial(int, base=16), ["ff", "10"])))

print("reduce sum      :", reduce(lambda acc, n: acc + n, [1, 2, 3, 4]), "-> use sum()")
print("reduce product  :", reduce(operator.mul, [1, 2, 3, 4], 1), "-> use math.prod()")

# A defensible use of reduce: folding with a combiner that has no built-in.
sets = [{1, 2, 3, 4}, {2, 3, 4}, {3, 4, 9}]
print("intersect many  :", reduce(set.intersection, sets), "(reduce earns its keep)")


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Apply the functions left to right: compose(f, g)(x) == g(f(x))."""
    def composed(value: Any) -> Any:
        return reduce(lambda acc, func: func(acc), funcs, value)
    return composed


clean = compose(str.strip, str.lower, lambda s: s.replace(" ", "-"))
print("composed        :", repr(clean("  Hello World  ")), "(expected 'hello-world')")
print("empty compose   :", repr(compose()("unchanged")), "(identity)")

print()
print("Done. Now open exercises.py in this folder.")
