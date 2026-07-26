# Day 15 — Comprehensions and Generators

> **Time:** ~4 hours  |  **Prerequisites:** Day 14

## What you'll be able to do after today
- Rewrite a build-a-list loop as a list, dict, or set comprehension, and explain the one rule for when you must not.
- Describe what a `for` loop actually does under the hood, and implement the iterator protocol (`__iter__`/`__next__`) yourself.
- Write generator functions with `yield` and generator expressions, and say precisely when each is the right shape.
- Measure the memory difference between building a list and streaming a generator, instead of guessing.
- Build an infinite generator and consume a bounded slice of it without hanging your program.
- Chain generators into a streaming pipeline that processes a file larger than your RAM.

## Why this matters

Two thirds of professional Python is "take a sequence of things, keep some, change
some, summarise the rest". Weeks 1 and 2 gave you loops, which do this correctly
but verbosely. Comprehensions make the intent visible in one line; generators make
it possible at all when the data does not fit in memory.

The failure mode you are avoiding is concrete. A colleague writes
`rows = f.read().splitlines()` on a 12 GB export, the process is killed by the
operating system at 3 a.m., and nobody knows why because the code "worked on the
sample file". Generators are how you write code that does not care how big the
input is. This is also the day where reading other people's Python stops being a
struggle, because comprehensions are everywhere and until now they looked like
punctuation soup.

---

## 1. The loop you have been writing since Day 4

Here is the pattern you already know:

```python
numbers = [1, 2, 3, 4, 5, 6]

doubled = []                 # 1. make an empty list
for n in numbers:            # 2. walk the input
    doubled.append(n * 2)    # 3. append a transformed value

print(doubled)
```

Prints `[2, 4, 6, 8, 10, 12]`.

Three of those four lines are bookkeeping. Only `n * 2` says anything about your
problem. A **list comprehension** keeps the meaning and deletes the bookkeeping:

```python
doubled = [n * 2 for n in numbers]
print(doubled)               # [2, 4, 6, 8, 10, 12]
```

Read it out loud in the order it is written: "a list of `n * 2`, for each `n` in
`numbers`". The expression comes first because the expression is the point.

The general shape:

```
[  EXPRESSION   for  VARIABLE  in  ITERABLE  ]
```

A comprehension always produces a **new** object. It never modifies the input.

> **Gotcha:** a comprehension is an expression, so it has a value. That means
> `[print(n) for n in numbers]` "works" but is wrong: you get a list of five
> `None` values as a side effect of printing. If you are not keeping the result,
> use a plain `for` loop. A comprehension whose value you throw away is a lie
> about your intent.

---

## 2. Filtering: the `if` clause

Add `if CONDITION` at the end to skip items:

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8]

evens = [n for n in numbers if n % 2 == 0]
print(evens)                 # [2, 4, 6, 8]

even_squares = [n * n for n in numbers if n % 2 == 0]
print(even_squares)          # [4, 16, 36, 64]
```

The reading order is: for each `n`, if the condition holds, evaluate the
expression and keep it. So the filter runs before the transformation, even
though it is written after it.

You can also put a **conditional expression** in the expression slot, which is a
different thing entirely:

```python
labels = ["even" if n % 2 == 0 else "odd" for n in numbers]
print(labels)   # ['odd', 'even', 'odd', 'even', 'odd', 'even', 'odd', 'even']
```

Compare the two carefully:

| Position | Syntax | Effect |
|---|---|---|
| After the `for` | `[n for n in xs if cond]` | **drops** items |
| Before the `for` | `[a if cond else b for n in xs]` | **replaces** items, keeps the count |

If you write `[n if n % 2 == 0 for n in numbers]` you get a `SyntaxError`,
because an `if` without an `else` is not an expression and cannot sit in the
expression slot.

---

## 3. Dict and set comprehensions

Same idea, different brackets.

```python
words = ["pipeline", "yield", "lazy"]

lengths = {w: len(w) for w in words}
print(lengths)               # {'pipeline': 8, 'yield': 5, 'lazy': 4}

initials = {w[0] for w in words}
print(initials)              # {'p', 'y', 'l'}  (set: order not guaranteed)
```

A dict comprehension needs `KEY: VALUE`. A set comprehension looks like a list
comprehension with `{}` and, like any set, removes duplicates and has no order.

Two idioms worth memorising:

```python
# invert a dict
codes = {"gb": 44, "us": 1, "de": 49}
by_number = {number: country for country, number in codes.items()}
print(by_number)             # {44: 'gb', 1: 'us', 49: 'de'}

# normalise keys while filtering values
raw = {" Name ": "Ada", "role": "", "City": "London"}
clean = {k.strip().lower(): v for k, v in raw.items() if v}
print(clean)                 # {'name': 'Ada', 'city': 'London'}
```

> **Gotcha:** `{}` on its own is an empty **dict**, never an empty set. For an
> empty set you must write `set()`. A comprehension is unambiguous because the
> `:` tells Python which one you meant.

---

## 4. Nesting: two loops, and the order that surprises everyone

Two `for` clauses in one comprehension read **left to right, outer to inner** —
exactly the order you would write nested loops:

```python
matrix = [[1, 2, 3], [4, 5, 6]]

flat = [value for row in matrix for value in row]
print(flat)                  # [1, 2, 3, 4, 5, 6]
```

The equivalent loop, for calibration:

```python
flat = []
for row in matrix:           # first for clause
    for value in row:        # second for clause
        flat.append(value)   # the expression
```

Nesting a comprehension **inside** the expression slot is a different structure
and produces a list of lists:

```python
transposed = [[row[i] for row in matrix] for i in range(3)]
print(transposed)            # [[1, 4], [2, 5], [3, 6]]
```

You can filter at either level:

```python
pairs = [(x, y) for x in range(3) for y in range(3) if x != y]
print(len(pairs))            # 6 — the 9 pairs minus the 3 where x == y
```

### The readability rule (this is the opinionated part)

**Go back to a loop when any of these is true:**

1. You need more than two `for` clauses.
2. You need more than one `if` clause, or the condition does not fit on the line.
3. The expression is longer than about 40 characters or calls more than one
   function you had to go and look up.
4. You cannot read it out loud as one English sentence.
5. You want to `print`, log, or debug inside it. You cannot, so it must be a loop.

This is not style pedantry; it is about the debugger. You cannot set a breakpoint
inside a comprehension, and a traceback from one points at the whole line. Here
is a comprehension that has crossed the line:

```python
# Don't. Nobody can review this.
result = [transform(v) for k, sub in data.items() if k not in SKIP
          for v in sub if v is not None and v.status == "ok" and v.score > cutoff]
```

Rewritten so that a human — including you, in six months — can read it:

```python
result = []
for key, sub in data.items():
    if key in SKIP:
        continue
    for value in sub:
        if value is None:
            continue
        if value.status == "ok" and value.score > cutoff:
            result.append(transform(value))
```

The loop is longer and better. "Shorter" is not the goal; "obvious" is.

---

## 5. What `for` actually does

You have used `for` for eleven days without knowing the mechanism. Here it is.

`for x in thing:` performs three steps:

1. Calls `iter(thing)` to get an **iterator**.
2. Calls `next(iterator)` over and over, binding each result to `x`.
3. Stops when `next` raises `StopIteration`.

You can drive it by hand:

```python
letters = ["a", "b"]
it = iter(letters)           # a list_iterator object
print(next(it))              # a
print(next(it))              # b
print(next(it))              # raises StopIteration
```

Vocabulary that people use imprecisely and you should not:

- **Iterable**: something you can call `iter()` on. Lists, strings, dicts, files,
  sets, ranges. Reusable.
- **Iterator**: something with a `__next__` method that yields one value at a
  time and is **consumed as it goes**. Single use.

Any object becomes iterable if you implement `__iter__`. It becomes an iterator
if it also implements `__next__` and returns itself from `__iter__`:

```python
class Countdown:
    """Counts down from start to 1."""

    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> "Countdown":
        return self                      # I am my own iterator

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration          # the only way to say "done"
        self.current -= 1
        return self.current + 1


print(list(Countdown(3)))    # [3, 2, 1]
for n in Countdown(2):
    print(n)                 # 2 then 1
```

> **Gotcha:** `Countdown` is exhausted after one pass, because it mutates its own
> state. `c = Countdown(3); list(c); list(c)` gives `[3, 2, 1]` then `[]`. That is
> normal iterator behaviour — the same thing happens with a file object — but it
> is a real bug source when a function takes an "iterable" and loops over it
> twice. If a function must iterate twice, it should call `list()` first and say
> so in its docstring.

---

## 6. Generators: iterators without the ceremony

That class was 12 lines for a countdown. A **generator function** does the same
job in four. Any function containing `yield` is a generator function:

```python
from collections.abc import Iterator


def countdown(start: int) -> Iterator[int]:
    while start > 0:
        yield start          # hand a value out, then freeze
        start -= 1


print(list(countdown(3)))    # [3, 2, 1]
```

Calling `countdown(3)` runs **none** of the body. It returns a generator object.
Each `next()` thaws the function, runs to the next `yield`, hands the value back
and freezes again — local variables intact. When the function returns (falls off
the end or hits `return`), Python raises `StopIteration` for you.

Watch the pause happen:

```python
def noisy() -> Iterator[str]:
    print("  starting")
    yield "first"
    print("  woke up again")
    yield "second"
    print("  finishing")


gen = noisy()                # prints nothing at all
print(next(gen))             #   starting  / first
print(next(gen))             #   woke up again / second
```

`yield` versus `return`:

| | `return` | `yield` |
|---|---|---|
| Number of values | one | as many as you like |
| Function state after | discarded | frozen and resumable |
| Cost of 10 million values | 10 million in memory | one at a time |

A bare `return` inside a generator means "stop"; the returned value is not part
of the stream (it ends up on the `StopIteration`, which you can ignore).

### Validate before you yield

Because the body does not run until the first `next()`, argument checking inside
a generator fires late — often in a different function, minutes later:

```python
def batches(items, size):
    if size < 1:
        raise ValueError("size must be positive")   # NOT raised at call time
    batch = []
    for item in items:
        ...

gen = batches([1, 2, 3], 0)   # no error here, which is the problem
print("still fine")           # this prints
list(gen)                     # ValueError finally surfaces, far from the bug
```

The fix is the standard two-function pattern: a plain function that validates
immediately and returns an inner generator.

```python
def batches(items, size):
    if size < 1:
        raise ValueError("size must be positive")   # runs at call time

    def generate():                                  # this one holds the yield
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) == size:
                yield batch
                batch = []
        if batch:
            yield batch

    return generate()


batches([1, 2, 3], 0)   # ValueError immediately, at the line with the mistake
print(list(batches([1, 2, 3], 2)))   # [[1, 2], [3]]
```

`batches` has no `yield`, so it is a normal function; it runs eagerly and hands
back the lazy part. You will write this pattern any time a generator takes
arguments that can be wrong.

---

## 7. Generator expressions

A generator expression is a comprehension with `()` instead of `[]`, and it is
lazy:

```python
numbers = range(1, 6)

squares_list = [n * n for n in numbers]      # computes all 5 now
squares_gen = (n * n for n in numbers)       # computes nothing yet

print(squares_list)                          # [1, 4, 9, 16, 25]
print(squares_gen)                           # <generator object ...>
print(sum(squares_gen))                      # 55
print(sum(squares_gen))                      # 0  <-- already consumed
```

That second `sum` returning `0` is the single most common generator bug. A
generator is a one-shot stream, not a collection.

When a generator expression is the only argument to a function, drop the extra
parentheses:

```python
words = ["alpha", "bee", "gamma"]
print(sum(len(w) for w in words))            # 13
print(any(len(w) > 4 for w in words))        # True
print(max((w for w in words if len(w) > 3), key=len))   # 'alpha'
```

Choosing between the three:

- Need to index it, keep it, or loop twice -> **list comprehension**.
- Feeding a consumer once (`sum`, `any`, `max`, `join`, a `for` loop) -> **generator expression**.
- Logic needs multiple statements, `try`, or a `while` -> **generator function**.

---

## 8. Laziness and memory, measured

Do not take this on faith. `sys.getsizeof` reports the memory of the object
itself:

```python
import sys

list_of_million = [n * n for n in range(1_000_000)]
gen_of_million = (n * n for n in range(1_000_000))

print(sys.getsizeof(list_of_million))   # ~8_448_728 bytes (about 8 MB)
print(sys.getsizeof(gen_of_million))    # ~200 bytes, regardless of the count
```

The list holds a million integer references. The generator holds a paused stack
frame — a recipe, not a result. Change `1_000_000` to `1_000_000_000` and the
generator does not get bigger; the list gets you killed by the OS.

Laziness buys three separate things:

1. **Memory that does not scale with input size.**
2. **Time to first result.** A list comprehension over 10 million rows produces
   nothing for 20 seconds. A generator hands you row 1 immediately, which matters
   when something downstream might fail fast.
3. **The ability to stop early.** If you only need the first match, a list
   comprehension still computed all 10 million.

`sum(n * n for n in range(10_000_000))` runs in constant memory. The list version
allocates roughly 400 MB first. Both give the same number.

> **Gotcha:** laziness is not free. Generators are marginally slower per item
> than a list comprehension, and you cannot `len()` them, index them, or reuse
> them. For 100 items, build the list; the clarity is worth more than the bytes.
> For unknown or unbounded sizes, stream.

---

## 9. Infinite generators and taking a slice

Because nothing is computed until asked for, a generator may be endless:

```python
from collections.abc import Iterator


def naturals(start: int = 0) -> Iterator[int]:
    n = start
    while True:              # no exit condition, on purpose
        yield n
        n += 1
```

`list(naturals())` hangs forever and eventually dies. You must bound it. The
standard tool is `itertools.islice`, which is "slicing for iterators":

```python
from itertools import islice

print(list(islice(naturals(), 5)))          # [0, 1, 2, 3, 4]
print(list(islice(naturals(), 2, 6)))       # [2, 3, 4, 5]
print(list(islice(naturals(), 0, 10, 3)))   # [0, 3, 6, 9]
```

`islice` is lazy too, so `islice(naturals(), 5)` never asks for a sixth value.
Writing it yourself is a five-line exercise and worth doing once:

```python
def take(iterable, n):
    result = []
    for item in iterable:
        if len(result) >= n:
            break            # stop pulling: this is what makes it safe
        result.append(item)
    return result
```

The `break` is load-bearing. Without it you consume the infinite source forever.

Other endless patterns you will meet: `itertools.cycle(["a", "b"])` repeats a
sequence forever, `itertools.count(10, 5)` counts 10, 15, 20, ... and
`itertools.repeat("x")` yields the same value forever. Day 17 covers the rest of
`itertools`.

---

## 10. `yield from`: delegating to another iterable

Inside a generator, `yield from other_iterable` yields every item of that
iterable, one at a time. It replaces a loop:

```python
def chained(a, b):
    for item in a:           # the long way
        yield item
    for item in b:
        yield item


def chained2(a, b):
    yield from a             # the same thing
    yield from b


print(list(chained2([1, 2], "xy")))     # [1, 2, 'x', 'y']
```

Where it earns its keep is recursion over nested structures:

```python
def flatten_deep(nested):
    """Yield every non-list value at any depth, left to right."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten_deep(item)   # recurse, yielding as we go
        else:
            yield item


print(list(flatten_deep([1, [2, [3, [4]], 5], 6])))   # [1, 2, 3, 4, 5, 6]
```

Try writing that without `yield from` and you will build intermediate lists at
every level, which defeats the point.

---

## 11. Streaming pipelines over a large file

This is the technique that makes today worth four hours. Each stage is a
generator that takes an iterator and yields an iterator. Nothing accumulates.

```python
from collections.abc import Iterator
from pathlib import Path


def read_lines(path: Path) -> Iterator[str]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:           # a file object is already a lazy iterator
            yield line.rstrip("\n")


def skip_blank(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:
        if line.strip():
            yield line


def parse(lines: Iterator[str]) -> Iterator[dict]:
    for line in lines:
        parts = line.split(",")
        if len(parts) != 3:
            continue                  # quarantine the junk, do not crash
        name, sensor, value = parts
        try:
            yield {"name": name, "sensor": sensor, "value": float(value)}
        except ValueError:
            continue


def only_high(records: Iterator[dict], cutoff: float) -> Iterator[dict]:
    for record in records:
        if record["value"] > cutoff:
            yield record


# Wire the stages together. Still zero rows read at this point.
rows = only_high(parse(skip_blank(read_lines(Path("readings.csv")))), 20.0)

# The `for` is what pulls data through the whole chain, one row at a time.
total = 0.0
count = 0
for row in rows:
    total += row["value"]
    count += 1
print(f"{count} readings above cutoff, mean {total / count:.2f}")
```

Properties worth naming:

- Peak memory is one line, whether the file is 3 KB or 300 GB.
- Each stage does one thing and is testable on a list of strings — no file needed.
- Adding a stage is one function and one wrapping call.
- If you `break` out of the loop early, upstream stages stop reading. The file is
  never fully read.

> **Gotcha:** `read_lines` opens the file inside the generator, so the file stays
> open until the generator is exhausted or garbage-collected. Consume it fully,
> or wrap the consumption in `contextlib.closing`. Never return a bare file
> iterator out of a `with` block — the file closes on the way out and every read
> afterwards raises `ValueError: I/O operation on closed file`.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Reusing a generator | Second pass is empty; `sum()` returns 0 | Store `list(gen)` if you need it twice |
| `[n if cond for n in xs]` | `SyntaxError: invalid syntax` | Filter goes after the `for`: `[n for n in xs if cond]` |
| `{x for x in ...}` when you wanted a dict | Set of keys, values gone | Write `{k: v for ...}` |
| `len(gen)` | `TypeError: object of type 'generator' has no len()` | `sum(1 for _ in gen)`, which consumes it |
| `list(infinite_generator())` | Process hangs, then MemoryError | Bound it: `islice(gen, n)` |
| Returning a file iterator from a `with` block | `ValueError: I/O operation on closed file` | `yield` inside the `with`, as `read_lines` does |
| Comprehension used for side effects | A list of `None` you ignore | Use a plain `for` loop |
| Forgetting `raise StopIteration` in `__next__` | Infinite loop | Raise it when there is nothing left |
| Modifying the list you are comprehending over | Wrong or missing items | Build a new list; never mutate the source |

---

## Mental model

A list is a **bucket of water**. A generator is a **tap**.

```
LIST COMPREHENSION                 GENERATOR PIPELINE
------------------                 ------------------
[all rows in memory]               read ->  strip ->  parse ->  filter ->  sum
        |                            .        .         .         .         |
   fill the whole bucket             \________\_________\_________\_________/
   before anyone drinks                    one drop travels the whole
                                           chain, then the next drop

cost = O(n) memory                 cost = O(1) memory
you can look at it twice           it is gone once it has flowed past
```

`for` is the hand on the tap: it pulls. Nothing in a generator pipeline moves
until a consumer at the end (`for`, `sum`, `list`, `join`, `max`) asks for the
next drop. If your pipeline "does nothing", you forgot to consume it.

---

## Practice

1. Run the demo and read the output next to the source:
   ```bash
   python course/week3/day15_comprehensions_and_generators/examples.py
   ```
2. Open `exercises.py` in that folder and implement the ten functions top to
   bottom. They escalate: 1–4 are comprehensions, 5–6 are the iterator protocol
   and generators, 7–9 are laziness, 10 is a full streaming aggregation.
3. Grade yourself from the course root:
   ```bash
   python check.py day15
   ```
4. When a check fails, read the assertion message before touching the code.
   `python check.py day15 -v` shows the full traceback.
5. Only after your own attempt, compare with `solutions.py`. Every difference is
   a question worth answering: is mine wrong, or different?

---

## Recall check

1. What does `for x in thing:` call, in order, and which exception ends the loop?
2. What is the difference between an iterable and an iterator?
3. Why does `sum(gen)` return `0` the second time you call it?
4. Where does the filter go in a comprehension, and where does a conditional
   expression go?
5. Name three situations where you must abandon a comprehension for a loop.
6. Why is `sys.getsizeof` on a generator roughly the same for 10 items and 10
   billion?
7. What does `yield from` do that a `for ... yield` loop does not do better?
8. Why does `take(naturals(), 5)` need a `break` rather than just a length check
   at the end?

<details>
<summary>Answers</summary>

1. It calls `iter(thing)` once to get an iterator, then `next(iterator)`
   repeatedly. `StopIteration` ends the loop, and `for` swallows it for you.
2. An iterable can produce an iterator via `iter()` and is usually reusable
   (list, str, dict). An iterator produces values one at a time via `next()`,
   remembers its position, and is exhausted after one pass.
3. A generator is a one-shot stream. The first `sum` consumed every value and
   left the generator exhausted, so the second sees an empty stream and the sum
   of nothing is `0`.
4. The filter (`if cond`) goes after the `for` clause and drops items. A
   conditional expression (`a if cond else b`) goes in the expression slot before
   the `for` and replaces items, keeping the count the same.
5. More than two `for` clauses; more than one `if` or a condition too long for
   the line; needing to log or debug inside the body; an expression you cannot
   read aloud as a sentence; needing `try`/`except` per item.
6. The generator object stores a paused stack frame — the recipe — not the
   values. Values are computed on demand and discarded, so its size is
   independent of how many it will eventually produce.
7. It delegates to a sub-iterable (including a recursive call) without an
   intermediate loop variable or intermediate list, which makes recursive
   flattening readable and keeps it lazy. It also forwards `send`/`throw` to the
   sub-generator, which matters for coroutines.
8. Because the source is infinite. Checking the length after the loop never
   happens — the loop never ends. The `break` is what stops pulling from the tap.

</details>
