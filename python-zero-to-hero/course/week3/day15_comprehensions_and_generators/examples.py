"""Day 15 — runnable demonstrations of comprehensions, iterators, generators.

Run it:

    python course/week3/day15_comprehensions_and_generators/examples.py

Every section number matches a section in LESSON.md. Read the printed output
next to the code that produced it; that pairing is the whole point of this file.
"""

from __future__ import annotations

import shutil
import sys
from collections.abc import Iterable, Iterator
from itertools import count, cycle, islice
from pathlib import Path

# A folder we create and delete again, so this script leaves nothing behind.
TMP = Path(__file__).parent / "tmp"


def banner(text: str) -> None:
    """Print a section header so the output is navigable."""
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


# ---------------------------------------------------------------------------
banner("1. The loop, and the comprehension that replaces it")
# ---------------------------------------------------------------------------

numbers = [1, 2, 3, 4, 5, 6]

# The Day 4 way: empty list, loop, append. Correct but three lines of plumbing.
doubled_loop: list[int] = []
for n in numbers:
    doubled_loop.append(n * 2)

# The comprehension way: expression first, because the expression is the point.
doubled_comp = [n * 2 for n in numbers]

print("input           :", numbers)
print("loop result     :", doubled_loop)
print("comprehension   :", doubled_comp)
print("identical?      :", doubled_loop == doubled_comp, "(expected True)")

# A comprehension never touches the input list. Proof:
print("input unchanged :", numbers, "(expected [1, 2, 3, 4, 5, 6])")


# ---------------------------------------------------------------------------
banner("2. Filtering with `if` versus replacing with `a if c else b`")
# ---------------------------------------------------------------------------

# `if` AFTER the for-clause drops items. 8 in, 4 out.
evens = [n for n in numbers if n % 2 == 0]
print("evens (dropped) :", evens, "-> length", len(evens))

# A conditional expression BEFORE the for-clause replaces items. 6 in, 6 out.
labels = ["even" if n % 2 == 0 else "odd" for n in numbers]
print("labels (mapped) :", labels, "-> length", len(labels))

# Both at once: filter first, then transform what survived.
big_even_squares = [n * n for n in numbers if n % 2 == 0 if n > 2]
print("even squares >2 :", big_even_squares, "(expected [16, 36])")


# ---------------------------------------------------------------------------
banner("3. Dict and set comprehensions")
# ---------------------------------------------------------------------------

words = ["pipeline", "yield", "lazy", "yak"]

# KEY: VALUE makes it a dict comprehension.
lengths = {w: len(w) for w in words}
print("word -> length  :", lengths)

# Same syntax with a single expression makes a set: duplicates collapse.
initials = {w[0] for w in words}          # 'y' appears twice in the input
print("initials (set)  :", sorted(initials), "(y appears once)")

# Inverting a dict is a two-name unpack over .items()
codes = {"gb": 44, "us": 1, "de": 49}
by_number = {number: country for country, number in codes.items()}
print("inverted        :", by_number)

# Cleaning messy keys while filtering out empty values, in one readable line.
raw = {" Name ": "Ada", "role": "", "City": "London"}
clean = {k.strip().lower(): v for k, v in raw.items() if v}
print("cleaned         :", clean, "(the empty 'role' was dropped)")


# ---------------------------------------------------------------------------
banner("4. Nesting, and the line where readability dies")
# ---------------------------------------------------------------------------

matrix = [[1, 2, 3], [4, 5, 6]]

# Two for-clauses read outer-to-inner, exactly like nested loops.
flat = [value for row in matrix for value in row]
print("flattened       :", flat, "(expected [1, 2, 3, 4, 5, 6])")

# A comprehension INSIDE the expression slot builds a list of lists instead.
transposed = [[row[i] for row in matrix] for i in range(3)]
print("transposed      :", transposed, "(expected [[1, 4], [2, 5], [3, 6]])")

# Cartesian product with a filter.
pairs = [(x, y) for x in range(3) for y in range(3) if x != y]
print("distinct pairs  :", pairs)
print("count           :", len(pairs), "(9 combinations minus 3 diagonals)")

# The readability rule, demonstrated rather than asserted. Below is a
# comprehension that has too many clauses; the loop under it is better code.
people = [
    {"name": "ada", "tags": ["eng", "lead"], "active": True},
    {"name": "bo", "tags": [], "active": False},
    {"name": "cy", "tags": ["eng"], "active": True},
]

# Hard to scan, impossible to breakpoint inside:
bad = [f"{p['name']}:{t}" for p in people if p["active"] for t in p["tags"] if t != "lead"]

# Same result, reviewable by a human:
good: list[str] = []
for person in people:
    if not person["active"]:
        continue
    for tag in person["tags"]:
        if tag == "lead":
            continue
        good.append(f"{person['name']}:{tag}")

print("one-liner       :", bad)
print("loop version    :", good)
print("same output?    :", bad == good, "- prefer the loop when it reads better")


# ---------------------------------------------------------------------------
banner("5. What `for` actually does: iter() + next() + StopIteration")
# ---------------------------------------------------------------------------

letters = ["a", "b"]
it = iter(letters)                        # step 1: get an iterator
print("iterator object :", type(it).__name__)
print("next(it)        :", next(it), "(expected a)")
print("next(it)        :", next(it), "(expected b)")
try:
    next(it)                              # step 3: exhaustion signals the end
except StopIteration:
    print("next(it)        : raised StopIteration - this is what ends a for loop")


class Countdown:
    """An iterator implemented by hand, to see the protocol from the inside."""

    def __init__(self, start: int) -> None:
        self.current = start              # mutable state = single use

    def __iter__(self) -> Countdown:
        return self                       # "I am my own iterator"

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration           # the only legal way to say "done"
        self.current -= 1
        return self.current + 1


print("list(Countdown(3)):", list(Countdown(3)), "(expected [3, 2, 1])")

exhausted = Countdown(3)
print("first pass      :", list(exhausted))
print("second pass     :", list(exhausted), "(empty: iterators are one-shot)")


# ---------------------------------------------------------------------------
banner("6. Generator functions: the same iterator, four lines shorter")
# ---------------------------------------------------------------------------


def countdown(start: int) -> Iterator[int]:
    """Yield start, start-1, ... 1. Any function with `yield` is a generator."""
    while start > 0:
        yield start                       # hand a value out, then freeze here
        start -= 1                        # resumes here on the next next()


print("list(countdown(3)):", list(countdown(3)), "(expected [3, 2, 1])")


def noisy() -> Iterator[str]:
    """Prints let you watch the function freeze and thaw."""
    print("   [body] starting")
    yield "first"
    print("   [body] woke up again")
    yield "second"
    print("   [body] finishing")


gen = noisy()
print("after calling noisy(): nothing printed yet, body has not run")
print("next ->", next(gen))
print("next ->", next(gen))
try:
    next(gen)
except StopIteration:
    print("next -> StopIteration (the body ran off the end)")


# ---------------------------------------------------------------------------
banner("7. Generator expressions: comprehension syntax, lazy behaviour")
# ---------------------------------------------------------------------------

squares_list = [n * n for n in range(1, 6)]     # computed immediately
squares_gen = (n * n for n in range(1, 6))      # computed never, so far

print("list  :", squares_list)
print("gen   :", squares_gen)
print("sum   :", sum(squares_gen), "(expected 55)")
print("again :", sum(squares_gen), "(expected 0 - the stream is spent)")

# When the generator expression is the only argument, drop the extra parens.
sample = ["alpha", "bee", "gamma"]
print("total length    :", sum(len(w) for w in sample), "(expected 13)")
print("any long word   :", any(len(w) > 4 for w in sample), "(expected True)")
print("longest 4+ word :", max((w for w in sample if len(w) > 3), key=len))


# ---------------------------------------------------------------------------
banner("8. Laziness measured, not asserted")
# ---------------------------------------------------------------------------

big_list = [n * n for n in range(1_000_000)]
big_gen = (n * n for n in range(1_000_000))

list_bytes = sys.getsizeof(big_list)
gen_bytes = sys.getsizeof(big_gen)

print(f"list of 1,000,000 squares : {list_bytes:>10,} bytes")
print(f"generator of the same     : {gen_bytes:>10,} bytes")
print(f"ratio                     : {list_bytes / gen_bytes:>10,.0f}x smaller")

# The generator's size does not depend on how many values it will produce.
tiny_gen = (n * n for n in range(10))
print("generator over 10 items   :", sys.getsizeof(tiny_gen), "bytes (same object size)")

# Both compute the same answer; only one of them allocates hundreds of MB.
print("sum via generator         :", sum(n for n in range(1_000_000)))
print("sum via list              :", sum([n for n in range(1_000_000)]))

del big_list, big_gen                     # give the memory back before moving on


# ---------------------------------------------------------------------------
banner("9. Infinite generators, bounded with islice")
# ---------------------------------------------------------------------------


def naturals(start: int = 0) -> Iterator[int]:
    """0, 1, 2, 3, ... forever. Safe *because* nobody computes it all."""
    n = start
    while True:
        yield n
        n += 1


print("first 5         :", list(islice(naturals(), 5)))
print("items 2..5      :", list(islice(naturals(), 2, 6)))
print("every 3rd of 10 :", list(islice(naturals(), 0, 10, 3)))
print("count(10, 5)    :", list(islice(count(10, 5), 4)), "(itertools.count)")
print("cycle('ab')     :", list(islice(cycle("ab"), 5)), "(itertools.cycle)")


def take(iterable: Iterable[int], n: int) -> list[int]:
    """islice by hand. The `break` is what makes infinite input survivable."""
    result: list[int] = []
    for item in iterable:
        if len(result) >= n:
            break                         # stop *pulling*; do not just discard
        result.append(item)
    return result


print("hand-rolled take:", take(naturals(100), 4), "(expected [100, 101, 102, 103])")


# ---------------------------------------------------------------------------
banner("10. yield from: delegation and recursive flattening")
# ---------------------------------------------------------------------------


def chained(*iterables: Iterable[object]) -> Iterator[object]:
    """Yield everything from each iterable in turn."""
    for iterable in iterables:
        yield from iterable               # replaces `for x in iterable: yield x`


print("chained         :", list(chained([1, 2], "xy", (True,))))


def flatten_deep(nested: Iterable[object]) -> Iterator[object]:
    """Yield every non-list leaf, at any depth, left to right."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten_deep(item)  # recurse; values stream straight out
        else:
            yield item


messy = [1, [2, [3, [4, [5]]], 6], [], 7]
print("nested input    :", messy)
print("flattened       :", list(flatten_deep(messy)), "(expected [1..7])")


# ---------------------------------------------------------------------------
banner("11. A streaming pipeline over a file")
# ---------------------------------------------------------------------------

TMP.mkdir(exist_ok=True)
data_file = TMP / "readings.csv"

# Build a small file with deliberate junk in it: a blank line, a short row and
# a non-numeric value. Real data always contains all three.
rows = ["r1,temp,21.5", "", "r2,temp,19.0", "broken-row", "r3,temp,not-a-number", "r4,temp,30.25"]
data_file.write_text("\n".join(rows) + "\n", encoding="utf-8")
print("wrote", data_file.name, "with", len(rows), "lines (3 of them are junk)")


def read_lines(path: Path) -> Iterator[str]:
    """Stage 1: yield stripped lines. `yield` stays INSIDE the with-block."""
    with path.open(encoding="utf-8") as handle:
        for line in handle:               # file objects are already lazy
            yield line.rstrip("\n")


def skip_blank(lines: Iterable[str]) -> Iterator[str]:
    """Stage 2: drop whitespace-only lines."""
    for line in lines:
        if line.strip():
            yield line


def parse(lines: Iterable[str]) -> Iterator[dict[str, object]]:
    """Stage 3: turn text into dicts, quarantining anything malformed."""
    for line in lines:
        parts = line.split(",")
        if len(parts) != 3:
            print(f"   [skip] wrong field count: {line!r}")
            continue
        name, sensor, raw_value = parts
        try:
            value = float(raw_value)
        except ValueError:
            print(f"   [skip] unparseable number: {line!r}")
            continue
        yield {"name": name, "sensor": sensor, "value": value}


def above(records: Iterable[dict[str, object]], cutoff: float) -> Iterator[dict[str, object]]:
    """Stage 4: keep only the interesting records."""
    for record in records:
        if float(record["value"]) > cutoff:
            yield record


# Wiring the stages together reads inside-out and costs nothing: no file has
# been opened yet, no line has been read.
pipeline = above(parse(skip_blank(read_lines(data_file))), 20.0)
print("pipeline built  :", type(pipeline).__name__, "- still zero lines read")

# The for-loop is the hand on the tap. This is where everything runs.
total = 0.0
kept = 0
for record in pipeline:
    total += float(record["value"])
    kept += 1

print(f"kept {kept} records above 20.0, mean {total / kept:.2f} (expected 2 records, 25.88)")

# Early exit proves the file is never fully read when you stop asking.
first_only = next(iter(parse(skip_blank(read_lines(data_file)))))
print("first record only:", first_only, "- the rest of the file was never touched")

# Clean up: this script leaves no files behind.
shutil.rmtree(TMP)
print("removed", TMP.name + "/", "- exists?", TMP.exists(), "(expected False)")

print()
print("Done. Now open exercises.py in this folder.")
