# Day 16 — Decorators and Functional Python

> **Time:** ~4 hours  |  **Prerequisites:** Day 15

## What you'll be able to do after today
- Pass functions around as values, and say why `sorted(..., key=...)` needs that ability.
- Write `lambda` correctly and name the three cases where it is the wrong choice.
- Explain a closure precisely, and avoid the late-binding bug that bites everyone once.
- Write your own decorators, with and without arguments, and stack them in the right order.
- Use `functools.wraps` and demonstrate exactly what breaks when you forget it.
- Reach for the four decorators you will actually write at work: timing, caching, retry, logging.
- Use `functools.partial`, `lru_cache`, and `reduce` — and know when `reduce` is worse than a loop.

## Why this matters

Every framework you will use is built out of decorators. Flask routes
(`@app.route("/")`), pytest fixtures (`@pytest.fixture`), FastAPI endpoints,
Django's `@login_required`, `@property` from Day 13 — all the same mechanism.
Until you can write one, those are magic incantations you copy from tutorials,
and when they misbehave you have no model for debugging them.

The practical payoff is cross-cutting concerns: timing, caching, retrying,
logging, authorisation. These are needed by dozens of functions and belong to
none of them. Without decorators you paste the same six lines into every
function and then fail to update half of them. With decorators you write it once
and apply it with one line. The cost is that decorators hide control flow, so
today also covers when *not* to use one.

---

## 1. Functions are values

A function name without parentheses is just a variable pointing at an object:

```python
def shout(text: str) -> str:
    return text.upper() + "!"


noisy = shout                # no parentheses: no call, just another name
print(noisy("hello"))        # HELLO!
print(shout.__name__)        # shout
print(type(shout))           # <class 'function'>
```

Because functions are values, you can put them in lists and dicts, pass them as
arguments, and return them from other functions:

```python
def double(n: int) -> int:
    return n * 2


def square(n: int) -> int:
    return n * n


operations = {"double": double, "square": square}
print(operations["square"](7))       # 49

for name, func in operations.items():
    print(name, "->", func(5))       # double -> 10 / square -> 25
```

That dict is the grown-up replacement for a long `if/elif` chain dispatching on a
string. A function that takes or returns another function is called a
**higher-order function**.

> **Gotcha:** `operations = {"square": square()}` is a different and broken
> thing: it calls `square` with no arguments (TypeError) and stores the result.
> Parentheses mean "call now". No parentheses means "hand over the function
> itself". Every single decorator bug traces back to this distinction.

---

## 2. `lambda`: a function with no name

`lambda` builds a small function in one expression:

```python
add = lambda a, b: a + b        # legal, but see below
print(add(2, 3))                # 5
```

The rules: no `def`, no name, no statements, no `return` (the single expression
*is* the return value), and the whole thing is an expression so it can go
anywhere a value can go.

Where it belongs is inline, as an argument:

```python
people = [("Ada", 36), ("Grace", 45), ("Alan", 41)]
by_age = sorted(people, key=lambda person: person[1])
print(by_age)      # [('Ada', 36), ('Alan', 41), ('Grace', 45)]
```

### When `lambda` is the wrong choice

1. **You are assigning it to a name.** `add = lambda a, b: a + b` is a worse
   `def add(a, b): return a + b` — you lose the docstring, you lose type hints,
   and every traceback says `<lambda>` instead of `add`. Linters flag this (ruff
   rule E731). Use `def`.
2. **The body is not obvious at a glance.** If it needs a comment, it needs a
   name and a `def`.
3. **A built-in already does it.** `key=lambda s: s.lower()` should be
   `key=str.lower`. `lambda x: x[1]` should be `operator.itemgetter(1)` when you
   are sorting big data and care. `lambda x: -x[1]` is fine; `lambda r: (-r["score"], r["name"])` is
   also fine because a tuple key is idiomatic and short.

A lambda cannot contain `if/else` statements, loops, `try`, or assignments. It
*can* contain a conditional expression (`a if cond else b`), which is the one
form people forget is legal.

---

## 3. `map` / `filter` versus comprehensions

`map(func, iterable)` applies a function to every item. `filter(func, iterable)`
keeps items where the function returns truthy. Both return lazy iterators, like
Day 15's generators.

```python
numbers = [1, 2, 3, 4, 5, 6]

squares = list(map(lambda n: n * n, numbers))
evens = list(filter(lambda n: n % 2 == 0, numbers))
print(squares)   # [1, 4, 9, 16, 25, 36]
print(evens)     # [2, 4, 6]
```

The comprehension versions:

```python
squares = [n * n for n in numbers]
evens = [n for n in numbers if n % 2 == 0]
```

**Prefer the comprehension.** It is shorter, it reads left to right, and it does
not need `lambda`. The Python community settled this argument years ago.

`map` still earns its place in exactly two situations:

```python
# 1. The function already exists and has a name: no lambda needed, so map wins.
print(list(map(str.strip, [" a ", " b "])))     # ['a', 'b']
print(list(map(int, ["1", "2", "3"])))          # [1, 2, 3]

# 2. Multiple iterables in lockstep.
print(list(map(lambda a, b: a * b, [1, 2, 3], [10, 20, 30])))   # [10, 40, 90]
```

`filter(None, iterable)` is a third: it drops every falsy item.

```python
print(list(filter(None, [0, 1, "", "x", None, [], [2]])))   # [1, 'x', [2]]
```

> **Gotcha:** `map` and `filter` return iterators, not lists. `m = map(...)`
> then `print(m)` shows `<map object at 0x...>`, and `sum(m)` twice gives the
> right answer then `0`, for the Day 15 reason.

---

## 4. `sorted` with `key`

`sorted` takes a `key` function, calls it once per item, and sorts by the
returned value. The items themselves are returned unchanged.

```python
words = ["banana", "kiwi", "apple", "Fig"]

print(sorted(words))                          # ['Fig', 'apple', 'banana', 'kiwi']
print(sorted(words, key=str.lower))           # ['apple', 'banana', 'Fig', 'kiwi']
print(sorted(words, key=len))                 # ['Fig', 'kiwi', 'apple', 'banana']
print(sorted(words, key=len, reverse=True))   # ['banana', 'apple', 'kiwi', 'Fig']
```

Capital `F` sorted first in the default sort because uppercase letters have lower
code points. That is the classic "why is my alphabetical list wrong" bug.

For multi-field sorts, return a **tuple**. Tuples compare element by element:

```python
players = [
    {"name": "ada", "score": 10},
    {"name": "bo", "score": 30},
    {"name": "cy", "score": 10},
]

ranked = sorted(players, key=lambda p: (-p["score"], p["name"]))
print([p["name"] for p in ranked])     # ['bo', 'ada', 'cy']
```

Highest score first (negate the number to reverse just that field), then name
ascending as the tie-break. Negating is why you rarely need `reverse=True` with a
tuple key — and it only works for numbers. For descending strings, sort twice,
relying on the fact that Python's sort is **stable**: equal keys keep their
relative order.

```python
by_name = sorted(players, key=lambda p: p["name"])          # first pass
final = sorted(by_name, key=lambda p: p["score"], reverse=True)  # second pass
```

`min` and `max` take the same `key`. So does `list.sort`, which sorts in place
and returns `None` — assigning its result is a Day 5 mistake worth never
repeating.

---

## 5. Closures

A **closure** is a function that remembers variables from the scope where it was
defined, even after that scope has finished executing.

```python
def make_multiplier(factor: int):
    def multiply(value: int) -> int:
        return value * factor      # `factor` comes from the enclosing scope
    return multiply                # note: no parentheses


triple = make_multiplier(3)
double = make_multiplier(2)
print(triple(10))                  # 30
print(double(10))                  # 20
```

`make_multiplier` has returned long before `triple(10)` runs, yet `factor` is
still there. Python attached it to the inner function:

```python
print(triple.__closure__[0].cell_contents)   # 3
```

Each call to `make_multiplier` creates a fresh cell, so `triple` and `double` do
not interfere. This is the whole mechanism behind decorators, and it is a
lightweight alternative to a one-method class.

To *modify* an enclosing variable rather than read it, you need `nonlocal`:

```python
def make_counter():
    count = 0

    def increment() -> int:
        nonlocal count             # without this: UnboundLocalError
        count += 1
        return count

    return increment


tick = make_counter()
print(tick(), tick(), tick())      # 1 2 3
```

Without `nonlocal`, `count += 1` makes `count` local to `increment`, and reading
it before assignment raises `UnboundLocalError`.

### The late-binding gotcha

This is the bug. Read it, then read the fix, then remember it forever.

```python
adders = []
for offset in [1, 10, 100]:
    adders.append(lambda x: x + offset)     # BUG

print([add(0) for add in adders])           # [100, 100, 100]  not [1, 10, 100]
```

Closures capture the **variable**, not the value it had at definition time. All
three lambdas share the one `offset` variable, and by the time any of them runs,
the loop has finished and `offset` is `100`.

Two correct fixes:

```python
# Fix 1: a default argument, evaluated once at definition time.
adders = [lambda x, offset=offset: x + offset for offset in [1, 10, 100]]
print([add(0) for add in adders])            # [1, 10, 100]


# Fix 2: a factory function, giving each closure its own scope. Clearer.
def make_adder(offset: int):
    def add(x: int) -> int:
        return x + offset
    return add


adders = [make_adder(offset) for offset in [1, 10, 100]]
print([add(0) for add in adders])            # [1, 10, 100]
```

Fix 2 is the one to reach for; the default-argument trick is compact but looks
like a mistake to readers. The same bug appears with `def` inside a loop, with
GUI button callbacks, and with `functools.partial` misuse. If several functions
built in a loop all behave like the last one, this is why.

---

## 6. Your first decorator

A decorator is a function that takes a function and returns a replacement. That
is the entire concept. Start without syntax sugar:

```python
def announce(func):
    def wrapper(*args, **kwargs):        # accepts whatever func accepts
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)   # do the real work
        print(f"{func.__name__} returned {result!r}")
        return result                    # never swallow the return value
    return wrapper


def add(a, b):
    return a + b


add = announce(add)          # rebind the name to the wrapper
print(add(2, 3))
```

Output:

```
calling add
add returned 5
5
```

`@announce` above a `def` means exactly `add = announce(add)`:

```python
@announce
def add(a, b):
    return a + b
```

The four things a well-behaved wrapper must do:

1. Accept `*args, **kwargs`, so it works for any signature.
2. Call the wrapped function.
3. **Return** its result.
4. Preserve the function's identity (next section).

> **Gotcha:** forgetting `return result` inside the wrapper turns every decorated
> function into one that returns `None`. It is the most common decorator bug, and
> the symptom appears far away from the cause.

---

## 7. `functools.wraps`, and what breaks without it

A decorator replaces your function with a different one, and the replacement has
the wrong name, docstring, and signature:

```python
def announce(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@announce
def add(a, b):
    """Add two numbers."""
    return a + b


print(add.__name__)     # wrapper       <- wrong
print(add.__doc__)      # None          <- documentation gone
help(add)               # shows wrapper(*args, **kwargs)
```

`functools.wraps` copies the metadata across:

```python
import functools


def announce(func):
    @functools.wraps(func)               # one line, always
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


print(add.__name__)     # add
print(add.__doc__)      # Add two numbers.
print(add.__wrapped__)  # <function add ...>  the original, kept for you
```

What omitting it actually costs you, beyond tidiness:

- `help()` and IDE tooltips show `wrapper(*args, **kwargs)` for every decorated
  function in your codebase.
- Logs and tracebacks say `wrapper`, so you cannot tell which function failed.
- `pickle` cannot serialise the function (it looks up the name and finds a
  mismatch), which breaks `multiprocessing` on Day 20.
- Sphinx, pydantic, FastAPI and pytest all introspect signatures; without
  `wraps`, they see `(*args, **kwargs)` and behave incorrectly.
- `inspect.signature` lies, and `functools.wraps` is what sets `__wrapped__` so
  it can tell the truth.

Always write `@functools.wraps(func)`. There is no case where you want the
default.

---

## 8. Decorators with arguments

`@repeat(3)` needs one more layer, because `repeat(3)` must *return* a decorator:

```python
import functools


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
            return result            # the last result
        return wrapper

    return decorator


@repeat(3)
def ping() -> str:
    print("ping")
    return "pong"


print(ping())     # ping ping ping then pong
```

Three levels, each with one job:

```
repeat(times)      -> configuration      (runs once, when you write @repeat(3))
  decorator(func)  -> receives function  (runs once, at import time)
    wrapper(*a)    -> receives arguments (runs on every call)
```

Reading a decorator, count the levels: two means no arguments, three means
arguments. `@repeat` without parentheses when it expects them fails confusingly,
because `func` gets bound to `times`, so the error surfaces later as
`TypeError: 'function' object cannot be interpreted as an integer`.

### Stacking

Decorators apply bottom-up, and wrap outermost-first at call time:

```python
@announce          # outer: sees the timed version
@repeat(2)         # inner: closest to the function
def work():
    return "done"

# equivalent to: work = announce(repeat(2)(work))
```

At call time, `announce`'s wrapper runs first, and inside it `repeat`'s wrapper
runs. Order matters in practice: `@app.route` must be outermost in Flask;
`@staticmethod` must be outermost; caching outside retry means you cache
failures... so put `@cache` inside `@retry` if the retry should still happen on a
cache miss only. Think about what each layer sees.

---

## 9. The four decorators you actually write

### Timing

```python
import functools
import time


def timed(func):
    """Record how long each call takes on the function itself."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.perf_counter()        # never time.time() for durations
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - started   # runs even on exception
            wrapper.durations.append(elapsed)
    wrapper.durations = []                   # attribute on the wrapper
    return wrapper


@timed
def slow_sum(n: int) -> int:
    return sum(range(n))


slow_sum(100_000)
slow_sum(200_000)
print(len(slow_sum.durations), "calls timed")   # 2 calls timed
```

`time.perf_counter` is a monotonic high-resolution clock. `time.time()` is
wall-clock, which can jump backwards when NTP adjusts it, producing negative
durations. The `try/finally` means a raised exception is still timed.

### Caching

Do not hand-roll this in production; `functools` ships it:

```python
import functools


@functools.lru_cache(maxsize=128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(35))            # instant; without the cache this is ~30 million calls
print(fib.cache_info())   # CacheInfo(hits=33, misses=36, maxsize=128, currsize=36)
fib.cache_clear()
```

`functools.cache` (3.9+) is `lru_cache(maxsize=None)`: unbounded, slightly
faster, and a memory leak if the argument space is unbounded. Rules for caching:

- Arguments must be **hashable**. A `list` argument raises
  `TypeError: unhashable type: 'list'`. Pass a tuple.
- The function must be **pure**: same arguments, same answer, no side effects.
  Caching a function that reads a file or a database gives you stale data
  forever.
- Cached values live until eviction or process exit. `maxsize=None` on a function
  called with millions of distinct arguments is an unbounded memory leak.
- Methods: `lru_cache` on a method keeps `self` alive in the cache, leaking
  instances. Use `functools.cached_property` for per-instance caching.

Writing it yourself, because you should know what is inside:

```python
def memoize(func):
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    wrapper.cache = cache          # expose it, so tests and humans can look
    return wrapper
```

### Retry

```python
import functools
import time


def retry(attempts: int = 3, delay: float = 0.0, exceptions=(Exception,)):
    """Call again on failure. Re-raise the last error if all attempts fail."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    last_error = error
                    if attempt < attempts and delay:
                        time.sleep(delay * 2 ** (attempt - 1))   # backoff
            raise last_error
        return wrapper
    return decorator
```

Three rules learned the hard way: never retry forever (bound the attempts);
never retry a `ValueError` or any other bug in your own logic (catch the specific
network exceptions); and never retry a non-idempotent operation blindly — a
retried "create payment" can charge twice. Day 19 goes deeper on backoff.

### Logging

```python
import functools
import logging

logger = logging.getLogger(__name__)


def log_calls(level: int = logging.DEBUG):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(level, "%s(%r, %r)", func.__name__, args, kwargs)
            try:
                result = func(*args, **kwargs)
            except Exception:
                logger.exception("%s failed", func.__name__)   # includes traceback
                raise                                          # never swallow it
            logger.log(level, "%s -> %r", func.__name__, result)
            return result
        return wrapper
    return decorator
```

Note the `raise`: a decorator that logs an exception and then hides it converts a
loud failure into a silent wrong answer. Day 17 covers `logging` properly.

---

## 10. `functools.partial` and `reduce`

`partial` freezes some arguments and returns a new callable:

```python
import functools

def power(base: float, exponent: float) -> float:
    return base ** exponent


square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
print(square(5), cube(2))            # 25.0 8.0

# Real use: adapting a function to an API that wants a one-argument callable.
lines = ["10", "0b101", "ff"]
print(list(map(functools.partial(int, base=16), ["ff", "10"])))   # [255, 16]
```

`partial(f, 2)` fills positional arguments left to right; keyword arguments are
usually clearer. A `lambda` does the same job (`lambda b: power(b, 2)`); `partial`
is faster, introspectable via `.func` and `.keywords`, and picklable, which
matters for `ProcessPoolExecutor` on Day 20.

`functools.reduce` folds an iterable into a single value:

```python
from functools import reduce

print(reduce(lambda acc, n: acc + n, [1, 2, 3, 4]))        # 10
print(reduce(lambda acc, n: acc * n, [1, 2, 3, 4], 1))     # 24
```

**Honest note on `reduce`.** Guido van Rossum wanted it removed from the language
and it was demoted from a built-in to `functools` in Python 3. Most `reduce`
calls have a clearer replacement:

| `reduce(...)` | Write this instead |
|---|---|
| `reduce(lambda a, b: a + b, xs)` | `sum(xs)` |
| `reduce(lambda a, b: a * b, xs)` | `math.prod(xs)` |
| `reduce(lambda a, b: a if a > b else b, xs)` | `max(xs)` |
| `reduce(lambda a, b: a + b, list_of_strs)` | `"".join(list_of_strs)` |
| anything with a multi-line accumulator | a `for` loop with an accumulator |

`reduce` is genuinely the right tool when you are folding with a non-obvious
combining function that has no built-in — merging dicts, composing functions,
intersecting many sets (`reduce(set.intersection, sets)`) — and even then, a
three-line loop is often kinder to the next reader. Use it, but do not reach for
it to look clever.

Function composition is the honest use case:

```python
def compose(*funcs):
    """Return f, g, h -> lambda x: h(g(f(x))). Applies left to right."""
    def composed(value):
        return reduce(lambda acc, func: func(acc), funcs, value)
    return composed


clean = compose(str.strip, str.lower, lambda s: s.replace(" ", "-"))
print(clean("  Hello World  "))      # hello-world
```

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `sorted(xs, key=len())` | `TypeError: len() takes exactly one argument (0 given)` | Pass the function, not a call: `key=len` |
| Wrapper without `return result` | Decorated functions all return `None` | `return func(*args, **kwargs)` |
| Forgetting `functools.wraps` | `add.__name__` is `'wrapper'`, help() is useless, pickling breaks | `@functools.wraps(func)` on every wrapper |
| `@repeat` when it needs `@repeat(3)` | `TypeError: 'function' object cannot be interpreted as an integer` | Call the factory: `@repeat(3)` |
| Lambdas built in a loop | Every one behaves like the last | Factory function, or `arg=arg` default |
| `count += 1` in a closure | `UnboundLocalError` | Declare `nonlocal count` |
| `lru_cache` on a function taking a list | `TypeError: unhashable type: 'list'` | Convert to a tuple at the call site |
| `lru_cache` on an impure function | Stale results forever, "but I changed the file" | Do not cache I/O; or clear the cache |
| `x = list.sort()` | `x` is `None` | `sorted(list)` returns a new list |
| Retry catching bare `Exception` | Bugs retried 3 times, then the same crash, 3x slower | Catch the specific exceptions |
| Decorator swallowing exceptions | Silent wrong answers | Log and `raise` |

---

## Mental model

A decorator is a **wrapper around a parcel**. The parcel (your function) is
unchanged inside; the wrapping adds a label, a timer, a receipt.

```
        @timed
        @retry(3)
        def fetch(url): ...

   call fetch("...") enters here
            |
   +--------v-----------------------+
   | timed.wrapper                  |   start clock
   |  +---------------------------+ |
   |  | retry.wrapper             | |   loop up to 3 times
   |  |  +---------------------+  | |
   |  |  |  fetch (your code)  |  | |   the actual work
   |  |  +---------------------+  | |
   |  +---------------------------+ |
   +--------------------------------+   stop clock, record
            |
      result comes back out
```

Bottom decorator = innermost wrapping = closest to your code. Written top to
bottom, applied bottom to top, executed outside in.

And a closure is a **backpack**: when an inner function leaves home, it carries
the variables it needs. Each function that leaves gets its own backpack — but if
they were all handed the *same* backpack (the late-binding case), they all see
whatever ended up in it.

---

## Practice

1. Run the demo:
   ```bash
   python course/week3/day16_decorators_and_functional/examples.py
   ```
   Section 5 and section 7 print the two bugs of the day. Make sure you can
   explain both before continuing.
2. Implement the ten exercises in `exercises.py`. Exercises 1–3 are `key`
   functions and `map`/`filter`; 4–5 are closures and late binding; 6–9 are
   decorators of increasing sophistication; 10 is composition.
3. Grade from the course root:
   ```bash
   python check.py day16
   ```
4. Compare with `solutions.py` only after your own attempt.

---

## Recall check

1. What is the difference between `f` and `f()` when passing a function somewhere?
2. Give three cases where `lambda` is the wrong tool.
3. Why does `[lambda: i for i in range(3)]` produce three functions that all
   return `2`?
4. What exactly does `@decorator` above `def f` do, in one line of equivalent code?
5. Name three concrete things that break when you omit `functools.wraps`.
6. How many nested function levels does a decorator with arguments need, and what
   does each level receive?
7. In `@a` over `@b` over `def f`, which wrapper runs first at call time?
8. Why must a function be pure and take hashable arguments to be `lru_cache`d?
9. When is `functools.reduce` genuinely better than a loop, and when is it worse?

<details>
<summary>Answers</summary>

1. `f` is the function object itself — a value you can store or pass. `f()` calls
   it right now and gives you its return value. Passing `f()` where a callable is
   expected passes the result instead of the function.
2. Assigning it to a name (use `def`); when the body needs a comment or is
   non-obvious; when a named function or built-in already exists
   (`key=str.lower`, `map(int, ...)`).
3. Closures capture the variable `i`, not its value at creation. All three share
   the same `i`, and after the comprehension finishes `i` is `2`. Fix with a
   factory function or a default argument.
4. `f = decorator(f)`.
5. `__name__`/`__doc__` are wrong so logs and `help()` mislead; `inspect.signature`
   reports `(*args, **kwargs)` so frameworks that introspect (pytest, FastAPI,
   Sphinx) misbehave; `pickle` fails, which breaks `ProcessPoolExecutor`.
6. Three: the factory receives the decorator's arguments, the decorator receives
   the function, the wrapper receives the call's arguments.
7. `a`'s wrapper runs first — it is the outermost — and it calls `b`'s wrapper,
   which calls `f`. Application order is bottom-up; execution order is outside-in.
8. Hashable because the arguments become a dict key. Pure because the cache
   returns the first answer forever, so any dependence on time, files, randomness
   or mutable state produces stale or wrong results.
9. Better when folding with a genuinely non-obvious combiner that has no built-in
   equivalent — composing functions, intersecting many sets, merging dicts.
   Worse whenever `sum`, `math.prod`, `max`, `"".join` or a plain accumulator loop
   says the same thing more clearly.

</details>
