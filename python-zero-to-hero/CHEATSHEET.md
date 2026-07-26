# Cheatsheet

Lookup reference for the whole course. Not a tutorial — if a section does not make
sense yet, the day that teaches it is noted in brackets. Terms are defined in
[reference/glossary.md](reference/glossary.md).

Contents: [types](#types-and-conversion) · [strings](#strings) ·
[f-strings](#f-string-format-specs) · [operators](#operators) ·
[lists](#lists) · [tuples](#tuples) · [dicts](#dicts) · [sets](#sets) ·
[which collection](#which-collection-should-i-use) ·
[control flow](#control-flow) · [comprehensions](#comprehensions-and-generators) ·
[functions](#functions) · [exceptions](#exceptions) · [classes](#classes) ·
[files](#files-and-paths) · [json/csv](#json-and-csv) ·
[stdlib](#stdlib-one-liners) · [pytest](#pytest)

---

## Types and conversion

```python
x = 42              # int
y = 3.14            # float
s = "text"          # str
flag = True         # bool  (True/False, capitalised)
nothing = None      # NoneType — the absence of a value

type(x)             # <class 'int'>
isinstance(x, int)  # True   — prefer this over type(x) == int
```

```python
int("42")        # 42          int("42.0") raises ValueError
int(3.99)        # 3           truncates toward zero, does not round
float("3.14")    # 3.14
str(42)          # "42"
bool("")         # False
round(3.567, 2)  # 3.57
```

Falsy values: `False 0 0.0 "" [] () {} set() None`. Everything else is truthy.

Type hints [D8] — annotations, not enforcement:

```python
def total(prices: list[float], tax: float = 0.2) -> float: ...
name: str = "Ada"
maybe: str | None = None          # either a str or None
from typing import Any, Callable, Iterable, Iterator, Optional
```

---

## Strings

```python
s = "Hello, World"
len(s)              # 12
s[0]                # "H"        first character
s[-1]               # "d"        last character
s[0:5]              # "Hello"    [start:stop) — stop is excluded
s[7:]               # "World"
s[:5]               # "Hello"
s[::-1]             # "dlroW ,olleH"   reversed
s[::2]              # "Hlo ol"         every 2nd char
```

Strings are immutable: every method returns a *new* string.

| Method | Result on `s = " Hello, World "` |
|---|---|
| `s.strip()` | `"Hello, World"` — also `.lstrip()`, `.rstrip()` |
| `s.lower()` / `.upper()` | case conversion |
| `s.title()` / `.capitalize()` | `"Hello, World"` / `" hello, world "` |
| `s.replace("l", "L")` | replace all occurrences; `.replace(a, b, 1)` for first only |
| `s.split(",")` | `[" Hello", " World "]`; `.split()` with no args splits on any whitespace |
| `s.strip().split()` | most common parsing idiom |
| `", ".join(["a", "b"])` | `"a, b"` — joiner goes first |
| `s.find("World")` | index or `-1`; `.index()` raises ValueError instead |
| `s.count("l")` | `3` |
| `s.startswith("He")` / `.endswith("ld")` | bool |
| `s.isdigit()` / `.isalpha()` / `.isspace()` | bool |
| `s.zfill(5)` | left-pad with zeros |
| `s.center(20, "-")` / `.ljust(10)` / `.rjust(10)` | padding |
| `s.splitlines()` | split on newlines |
| `"a" in s` | membership test, bool |

```python
"a\tb\nc"                   # \t tab, \n newline, \\ backslash, \" quote
r"C:\new\table"             # raw string: backslashes are literal
"""multi
line"""                     # triple quotes keep newlines
"ab" * 3                    # "ababab"
"a" + "b"                   # "ab" — but use f-strings for mixing types
```

---

## F-string format specs

```python
name, n, pi = "Ada", 7, 3.14159
f"{name} has {n} items"          # Ada has 7 items
f"{n + 1}"                       # any expression works
f"{name!r}"                      # 'Ada'  — repr instead of str
f"{pi=}"                         # pi=3.14159 — debug form, prints the expression
f"{{literal braces}}"            # {literal braces}
```

Spec syntax: `f"{value:[fill][align][sign][width][,][.precision][type]}"`

| Spec | Input | Output |
|---|---|---|
| `f"{pi:.2f}"` | 3.14159 | `3.14` |
| `f"{pi:10.3f}"` | 3.14159 | `     3.142` (width 10, right) |
| `f"{pi:<10.3f}"` | 3.14159 | `3.142     ` (left) |
| `f"{name:^11}"` | "Ada" | `    Ada    ` (centred) |
| `f"{name:*^11}"` | "Ada" | `****Ada****` (fill char) |
| `f"{1234567:,}"` | 1234567 | `1,234,567` |
| `f"{1234567:_}"` | 1234567 | `1_234_567` |
| `f"{0.256:.1%}"` | 0.256 | `25.6%` |
| `f"{255:b}"` / `:o` / `:x` / `:X` | 255 | `11111111` / `377` / `ff` / `FF` |
| `f"{1234.5:e}"` | 1234.5 | `1.234500e+03` |
| `f"{42:+d}"` | 42 | `+42` |
| `f"{42:05d}"` | 42 | `00042` |
| `f"{width}"` in spec | `f"{pi:.{d}f}"` | precision from a variable |

Aligning a table:

```python
for name, qty in [("apples", 3), ("bananas", 12)]:
    print(f"{name:<12}{qty:>5}")
# apples          3
# bananas        12
```

---

## Operators

```python
7 + 2   # 9        7 - 2   # 5        7 * 2   # 14
7 / 2   # 3.5      always float
7 // 2  # 3        floor division; -7 // 2 == -4
7 % 2   # 1        remainder; useful for "every Nth" and even/odd
7 ** 2  # 49       power; 2 ** 0.5 for square root
divmod(7, 2)       # (3, 1)
abs(-3)            # 3
x += 1             # also -= *= /= //= %= **=
```

```python
==  !=  <  >  <=  >=            # comparison, returns bool
1 < x < 10                      # chaining works
and  or  not                    # boolean; short-circuit left to right
is  is not                      # identity — only use with None: if x is None
in  not in                      # membership
x if cond else y                # conditional expression (ternary)
a, b = b, a                     # tuple unpacking swap
value = maybe or "default"      # falls back when maybe is falsy
```

Careful: `0.1 + 0.2 != 0.3` (binary floating point). Compare with a tolerance, or
use `decimal.Decimal` for money.

---

## Lists

Ordered, mutable, allows duplicates, indexable.

```python
xs = [3, 1, 2]
xs = list("abc")            # ['a', 'b', 'c']
xs[0]; xs[-1]; xs[1:3]      # index, last, slice
len(xs); 3 in xs
```

| Method | Effect | Returns |
|---|---|---|
| `xs.append(4)` | add one item to the end | None |
| `xs.extend([4, 5])` | add every item of an iterable | None |
| `xs.insert(0, 9)` | insert at index | None |
| `xs.pop()` / `xs.pop(0)` | remove and return last / at index | the item |
| `xs.remove(3)` | remove first matching *value* (ValueError if absent) | None |
| `xs.index(3)` | index of first match (ValueError if absent) | int |
| `xs.count(3)` | occurrences | int |
| `xs.sort()` | sort **in place** | None |
| `xs.sort(key=len, reverse=True)` | sort by a computed key | None |
| `xs.reverse()` | reverse in place | None |
| `xs.clear()` | empty it | None |
| `xs.copy()` | shallow copy (same as `xs[:]`) | new list |

```python
sorted(xs)                          # new sorted list, original untouched
sorted(words, key=str.lower)        # case-insensitive
sorted(rows, key=lambda r: r[1])    # by second field  [D16 for lambda]
sorted(d.items(), key=lambda kv: -kv[1])   # dict by value, descending
min(xs); max(xs); sum(xs)
any(xs); all(xs)
reversed(xs)                        # iterator, wrap in list() to see it
list(enumerate(xs))                 # [(0, 3), (1, 1), (2, 2)]
list(enumerate(xs, start=1))        # 1-based
list(zip(names, scores))            # pair up two sequences
a, b, c = [1, 2, 3]                 # unpack
first, *rest = [1, 2, 3]            # first=1, rest=[2, 3]
nested = [[0] * 3 for _ in range(3)]   # NOT [[0]*3]*3 — that shares one row
```

Gotcha: `ys = xs` makes another name for the same list. Use `xs.copy()`,
`list(xs)` or `copy.deepcopy(xs)` for nested structures.

---

## Tuples

Ordered, **immutable**, indexable. Use for fixed-shape records and dict keys.

```python
point = (3, 4)
x, y = point                 # unpacking
single = (5,)                # trailing comma required; (5) is just 5
empty = ()
point[0]                     # 3   — but point[0] = 9 raises TypeError
lat, lon = 51.5, -0.1        # parentheses optional
```

`namedtuple` and `NamedTuple` [D17] give you fields with names:

```python
from collections import namedtuple
Point = namedtuple("Point", "x y")
p = Point(3, 4); p.x    # 3
```

---

## Dicts

Key -> value mapping. Keys must be hashable (immutable). Insertion-ordered.

```python
d = {"a": 1, "b": 2}
d = dict(a=1, b=2)
d = dict([("a", 1), ("b", 2)])
d["a"]              # 1      — KeyError if missing
d.get("z")          # None   — no error
d.get("z", 0)       # 0      — with default
d["c"] = 3          # add or overwrite
"a" in d            # True   — checks keys
len(d); del d["a"]
```

| Method | Effect |
|---|---|
| `d.keys()` / `d.values()` / `d.items()` | views for iteration |
| `d.get(k, default)` | safe lookup |
| `d.setdefault(k, [])` | get, inserting the default if absent |
| `d.pop(k)` / `d.pop(k, default)` | remove and return |
| `d.popitem()` | remove and return the last pair |
| `d.update(other)` | merge `other` in |
| `d.copy()` | shallow copy |
| `d.clear()` | empty it |

```python
for key in d: ...                      # iterates keys
for key, value in d.items(): ...       # the usual loop
{**d1, **d2}                           # merge, d2 wins
d1 | d2                                # merge (3.9+)
{v: k for k, v in d.items()}           # invert  [D15]
max(d, key=d.get)                      # key with the largest value
```

Counting and grouping:

```python
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1

groups = {}
for r in records:
    groups.setdefault(r["kind"], []).append(r)

# same thing with the stdlib  [D17]
from collections import Counter, defaultdict
Counter(words).most_common(3)
groups = defaultdict(list)
for r in records:
    groups[r["kind"]].append(r)
```

---

## Sets

Unordered, no duplicates, fast membership. Elements must be hashable.

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])       # {1, 2, 3}
empty = set()               # {} is an empty dict, not a set
s.add(4); s.discard(9)      # discard is safe; remove raises KeyError
2 in s                      # fast, regardless of size
```

```python
a | b   a.union(b)                  # in either
a & b   a.intersection(b)           # in both
a - b   a.difference(b)             # in a only
a ^ b   a.symmetric_difference(b)   # in exactly one
a <= b  a.issubset(b)
list(set(xs))                       # de-duplicate (order lost)
dict.fromkeys(xs)                   # de-duplicate, order kept
frozenset({1, 2})                   # immutable set, usable as a dict key
```

---

## Which collection should I use?

| You need | Use | Why |
|---|---|---|
| An ordered sequence you will change | `list` | append/pop cheap at the end, indexable |
| A fixed record with positional meaning | `tuple` | immutable, hashable, unpackable |
| Lookup by name or id | `dict` | O(1) by key |
| Membership tests, de-duplication | `set` | O(1) `in`, no duplicates |
| Counting occurrences | `collections.Counter` | `.most_common()` built in |
| Grouping into lists | `collections.defaultdict(list)` | no `setdefault` boilerplate |
| Queue / adding to both ends | `collections.deque` | O(1) at both ends; lists are O(n) at the front |
| A record with named fields, immutable | `NamedTuple` / frozen `dataclass` | readable and hashable |
| A record with named fields plus behaviour | `class` / `dataclass` | data and methods together |
| Rows of homogeneous data | `list[dict]` or `list[dataclass]` | matches CSV/JSON shape |
| More data than fits in memory | generator | lazy, constant memory |

Rough cost model: `x in list` scans everything; `x in set` and `x in dict` do not.
If a membership test is inside a loop, use a set.

---

## Control flow

```python
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "F"

if not items:                       # idiomatic "is it empty"
    return None
```

```python
for i in range(5):          # 0 1 2 3 4
for i in range(2, 10, 3):   # 2 5 8         start, stop, step
for i in range(10, 0, -1):  # countdown
for ch in "abc": ...
for x in xs: ...
for i, x in enumerate(xs): ...
for a, b in zip(xs, ys): ...
for k, v in d.items(): ...
for _ in range(3): ...      # _ means "value not used"
```

```python
while queue:                # loop until falsy
    item = queue.pop()

while True:
    line = get_line()
    if line is None:
        break               # leave the loop
    if not line.strip():
        continue            # skip to the next iteration
```

```python
for x in xs:
    if x == target:
        break
else:
    print("never found it")     # for/else: runs only if no break happened
```

```python
match command.split():          # structural pattern matching (3.10+)
    case ["quit"]:
        return
    case ["add", item]:
        add(item)
    case _:
        print("unknown")
```

---

## Comprehensions and generators

[D15] Build a collection from an iterable in one expression.

```python
[x * 2 for x in xs]                     # list
[x for x in xs if x > 0]                # with filter
[x if x > 0 else 0 for x in xs]         # conditional value
{w: len(w) for w in words}              # dict
{w.lower() for w in words}              # set
(x * 2 for x in xs)                     # generator expression — lazy
[y for row in matrix for y in row]      # flatten; loops read left to right
[[y * 2 for y in row] for row in matrix]  # nested result
```

```python
sum(x ** 2 for x in xs)                 # no brackets needed as a sole argument
any(x < 0 for x in xs)
max((s for s in strings if s), key=len, default="")
```

Generator functions — `yield` produces values one at a time:

```python
def countdown(n: int):
    while n > 0:
        yield n
        n -= 1

for i in countdown(3): ...      # 3 2 1
list(countdown(3))              # [3, 2, 1]
next(gen)                       # pull one value; StopIteration when exhausted
```

```python
def read_big(path):             # constant memory, any file size
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")
```

A generator is consumed once. Iterating a second time yields nothing.

---

## Functions

```python
def greet(name: str, greeting: str = "Hello") -> str:
    """Return a greeting for name.

    >>> greet("Ada")
    'Hello, Ada!'
    """
    return f"{greeting}, {name}!"

greet("Ada")                       # positional
greet("Ada", greeting="Hi")        # keyword — clearer at call sites
```

```python
def f(*args, **kwargs):            # any positionals, any keywords
    print(args)                    # tuple
    print(kwargs)                  # dict

f(1, 2, a=3)                       # (1, 2) {'a': 3}
f(*[1, 2], **{"a": 3})             # unpack at the call site

def g(a, b=2, *, key=None):        # key is keyword-only
def h(a, b, /):                    # a, b are positional-only
```

```python
def bad(items: list = []):    ...  # BUG: one shared list across all calls
def good(items: list | None = None):
    items = [] if items is None else items
```

Scope: names assigned inside a function are local. Read outer values freely;
rebinding needs `global` (module level) or `nonlocal` (enclosing function) — both
are usually a sign to restructure and return a value instead.

Functions are values [D16]:

```python
ops = {"add": lambda a, b: a + b}       # lambda: a one-expression function
sorted(rows, key=lambda r: r["age"])
list(map(str.upper, words))             # a comprehension is usually clearer
list(filter(None, values))              # drop falsy values
```

Decorators [D16]:

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)                # keeps fn.__name__ and docstring
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter() - t0:.3f}s")
    return wrapper

@timed
def work(): ...

@functools.lru_cache(maxsize=None)      # memoise a pure function
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

from functools import partial, reduce
add10 = partial(lambda a, b: a + b, 10)
reduce(lambda a, b: a * b, [1, 2, 3, 4])    # 24
```

---

## Exceptions

```python
try:
    value = int(text)
except ValueError as exc:            # catch what you can actually handle
    print(f"bad number: {exc}")
    value = 0
except (KeyError, IndexError):       # several types at once
    value = 0
else:
    print("no exception happened")   # runs only when try succeeded
finally:
    print("always runs")             # cleanup, even on exception or return
```

```python
raise ValueError(f"expected positive, got {n}")
raise ValueError("context") from exc      # keep the original cause

class ConfigError(Exception):
    """Raised when configuration is invalid."""

assert total >= 0, f"total went negative: {total}"   # internal sanity check
```

Handle it, do not hide it:

```python
except Exception:      # too broad; catches typos and bugs too
    pass               # and this throws the evidence away
```

Common built-ins, by what they mean: `ValueError` right type wrong value ·
`TypeError` wrong type · `KeyError` missing dict key · `IndexError` sequence index
out of range · `AttributeError` no such attribute · `FileNotFoundError`,
`PermissionError` filesystem · `ZeroDivisionError` · `StopIteration` generator
exhausted. Full decoder: [reference/error_messages.md](reference/error_messages.md).

---

## Classes

```python
class Account:
    """A bank account."""

    currency = "GBP"                       # class attribute, shared

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        self.owner = owner                 # instance attributes
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

    def __repr__(self) -> str:             # what you see when debugging
        return f"Account(owner={self.owner!r}, balance={self.balance!r})"

acct = Account("Ada", 100.0)
acct.deposit(50)
isinstance(acct, Account)      # True
```

```python
class Savings(Account):                    # inheritance: Savings IS-A Account
    def __init__(self, owner, balance=0.0, rate=0.02):
        super().__init__(owner, balance)    # run the parent's __init__
        self.rate = rate

    def deposit(self, amount):              # override
        super().deposit(amount * 1.0)
```

```python
class Temp:
    def __init__(self, c): self._c = c

    @property                              # read like an attribute
    def fahrenheit(self) -> float:
        return self._c * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self._c = (value - 32) * 5 / 9

    @classmethod                           # alternative constructor
    def from_f(cls, f): return cls((f - 32) * 5 / 9)

    @staticmethod                          # no self, no cls; just namespaced
    def is_freezing(c): return c <= 0
```

Dunder methods worth knowing: `__init__` `__repr__` `__str__` `__eq__` `__lt__`
`__len__` `__getitem__` `__contains__` `__iter__` `__next__` `__call__`
`__enter__`/`__exit__` (context manager).

Dataclasses — less boilerplate for data-shaped classes:

```python
from dataclasses import dataclass, field

@dataclass
class Expense:
    amount: float
    category: str
    tags: list[str] = field(default_factory=list)   # never `= []`
    note: str = ""

    def with_tax(self, rate: float = 0.2) -> float:
        return self.amount * (1 + rate)

e = Expense(9.99, "food")
e                                  # Expense(amount=9.99, category='food', ...)
e == Expense(9.99, "food")         # True — __eq__ generated for you

@dataclass(frozen=True, slots=True)     # immutable and hashable
class Point:
    x: float
    y: float
```

Use a plain function when there is no state to keep. A class with one method and
no attributes should have been a function.

---

## Files and paths

```python
from pathlib import Path

p = Path("data") / "notes.txt"      # / joins portably; no backslash worries
p.exists(); p.is_file(); p.is_dir()
p.name          # 'notes.txt'
p.stem          # 'notes'
p.suffix        # '.txt'
p.parent        # Path('data')
p.resolve()     # absolute path
Path.cwd(); Path.home()
p.parent.mkdir(parents=True, exist_ok=True)
list(Path("data").glob("*.csv"))
list(Path("data").rglob("*.py"))    # recursive
p.stat().st_size
p.unlink(missing_ok=True)           # delete
```

```python
p.read_text(encoding="utf-8")               # whole file as one string
p.write_text("hello", encoding="utf-8")     # overwrites
p.read_bytes(); p.write_bytes(b"...")
```

```python
with open(p, encoding="utf-8") as f:        # `with` closes the file for you
    for line in f:                          # streams; safe for huge files
        print(line.rstrip("\n"))

with open(p, "w", encoding="utf-8") as f:   # "w" truncates immediately
    f.write("line 1\n")
    f.writelines([f"{x}\n" for x in xs])

with open(p, "a", encoding="utf-8") as f:   # append
    f.write("another\n")
```

Modes: `r` read (default) · `w` write, truncate · `a` append · `x` create, fail if
exists · `r+` read/write · add `b` for bytes (`rb`, `wb`). Text mode gives `str`
and needs an encoding; binary mode gives `bytes` and must not have one.

---

## JSON and CSV

```python
import json

data = json.loads('{"a": 1}')                  # str  -> dict
text = json.dumps(data, indent=2, sort_keys=True)   # dict -> str

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)               # dict -> file
with open("in.json", encoding="utf-8") as f:
    data = json.load(f)                        # file -> dict
```

JSON maps: object->dict, array->list, string->str, number->int/float,
true/false->bool, null->None. Sets, tuples-as-keys, dataclasses and `datetime` are
not JSON; convert first (`dataclasses.asdict`, `.isoformat()`).

```python
import csv

with open("in.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):          # each row is a dict keyed by header
        print(row["name"], row["amount"])  # values are ALWAYS strings

with open("out.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "amount"])
    w.writeheader()
    w.writerows(rows)
```

Always pass `newline=""` when opening a CSV file, or you get blank lines on
Windows. Convert numbers yourself: `int(row["amount"])`.

---

## Stdlib one-liners

```python
from collections import Counter, defaultdict, deque, namedtuple
Counter("mississippi").most_common(2)      # [('i', 4), ('s', 4)]
Counter(a) - Counter(b)                    # multiset difference
defaultdict(int); defaultdict(list); defaultdict(set)
deque(maxlen=100)                          # ring buffer; .appendleft/.popleft
```

```python
import itertools as it
it.chain(xs, ys)                    # one stream from several
it.islice(gen, 10)                  # first 10 of anything, lazily
it.product("ab", repeat=2)          # aa ab ba bb
it.combinations(xs, 2); it.permutations(xs, 2)
it.groupby(sorted(rows, key=k), key=k)     # MUST sort by the same key first
it.count(1); it.cycle("ab"); it.repeat(0, 3)
it.accumulate([1, 2, 3])            # 1, 3, 6
it.zip_longest(xs, ys, fillvalue=0)
```

```python
from datetime import date, datetime, timedelta, timezone
datetime.now(); datetime.now(timezone.utc)          # prefer aware UTC
date.today().isoformat()                            # '2024-05-01'
datetime.fromisoformat("2024-05-01T10:00:00")
datetime.strptime("01/05/2024", "%d/%m/%Y")         # parse
dt.strftime("%Y-%m-%d %H:%M")                       # format
date.today() + timedelta(days=7)
(d2 - d1).days
```

```python
import re
re.search(r"\d+", s)                 # first match anywhere -> Match or None
re.match(r"\d+", s)                  # anchored at the start
re.findall(r"\w+@\w+\.\w+", s)       # list of all matches
re.sub(r"\s+", " ", s)               # collapse whitespace
re.split(r"[,;]\s*", s)
m = re.search(r"(?P<year>\d{4})-(\d{2})", s)
m.group(0); m.group(1); m.group("year"); m.groups()
# \d digit  \w word char  \s whitespace  .  any  ^ $ anchors
# * 0+   + 1+   ? 0-1   {n,m} range   [] set   | or   () group
```

```python
import argparse
p = argparse.ArgumentParser(description="what this tool does")
p.add_argument("path")                                  # required positional
p.add_argument("-n", "--limit", type=int, default=10)
p.add_argument("--verbose", action="store_true")
args = p.parse_args()
args.path, args.limit, args.verbose
```

```python
import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)
log.debug("detail"); log.info("normal"); log.warning("suspicious")
log.error("broken"); log.exception("broken, with traceback")
```

```python
import os, sys, random, math, statistics, textwrap, time
os.environ.get("API_KEY")
sys.argv; sys.exit(1)
random.seed(0); random.randint(1, 6); random.choice(xs); random.shuffle(xs)
math.sqrt(16); math.ceil(1.2); math.floor(1.8); math.inf
statistics.mean(xs); statistics.median(xs)
textwrap.dedent(block); textwrap.fill(text, width=72)
time.perf_counter()                     # for timing, not time.time()
```

```python
import sqlite3                                          # [D19]
with sqlite3.connect("app.db") as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, n TEXT)")
    conn.execute("INSERT INTO t (n) VALUES (?)", ("Ada",))   # ? placeholders
    rows = conn.execute("SELECT id, n FROM t WHERE n = ?", ("Ada",)).fetchall()
```

```python
import requests                                         # [D19]
r = requests.get(url, params={"q": "python"}, timeout=10)
r.raise_for_status()                # raise on 4xx/5xx
r.status_code; r.json(); r.text
requests.post(url, json=payload, timeout=10)
```

```python
from concurrent.futures import ThreadPoolExecutor       # [D20] I/O-bound
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(fetch, urls))

import asyncio                                          # [D20]
async def main():
    results = await asyncio.gather(*(fetch(u) for u in urls))
asyncio.run(main())
```

---

## pytest

[D18] Run from the course root.

```bash
python -m pytest                         # everything under testpaths
python -m pytest course/week1 -q         # one week, quiet
python -m pytest path/to/test_x.py::test_name    # one test
python -m pytest -k "greet and not empty"        # by name substring
python -m pytest -x                      # stop at the first failure
python -m pytest -v                      # one line per test
python -m pytest --tb=long               # full tracebacks
python -m pytest -s                      # let print() through
python -m pytest --lf                    # only last-failed
```

```python
import pytest
from mymodule import parse, divide

def test_parse_returns_int():
    assert parse("42") == 42

def test_parse_rejects_text():
    with pytest.raises(ValueError):
        parse("abc")

def test_error_message():
    with pytest.raises(ValueError, match="expected positive"):
        parse("-1")

def test_float_comparison():
    assert divide(1, 3) == pytest.approx(0.3333, abs=1e-4)

@pytest.fixture
def sample_rows():
    return [{"name": "a", "amount": 1}]

def test_uses_fixture(sample_rows):
    assert len(sample_rows) == 1

@pytest.mark.parametrize("text,want", [("1", 1), ("42", 42), ("-3", -3)])
def test_parse_cases(text, want):
    assert parse(text) == want

def test_writes_file(tmp_path):          # built-in per-test temp directory
    p = tmp_path / "out.txt"
    p.write_text("hi", encoding="utf-8")
    assert p.read_text(encoding="utf-8") == "hi"

def test_prints(capsys):
    print("hello")
    assert capsys.readouterr().out.strip() == "hello"

@pytest.mark.skip(reason="not yet")
@pytest.mark.skipif(sys.version_info < (3, 11), reason="needs 3.11")
def test_later(): ...
```

Course-specific: day tests receive your `exercises.py` through the `day` fixture
defined in the root `conftest.py`. Set `PZH_SOLUTIONS=1` to grade `solutions.py`
instead:

```bash
PZH_SOLUTIONS=1 python -m pytest course/week1 -q     # macOS / Linux
$env:PZH_SOLUTIONS=1; python -m pytest course/week1 -q   # PowerShell
```

Tooling [D18]:

```bash
python -m pytest --cov=. --cov-report=term-missing   # needs pytest-cov
ruff check .          # lint
ruff check . --fix    # autofix
black .               # format
mypy .                # type check
```

---

## Debugging quick reference

```python
print(f"{value=} {type(value)=}")     # fastest possible probe
breakpoint()                          # drop into pdb at this line
```

pdb commands: `l` list source · `n` next line · `s` step into · `c` continue ·
`p expr` print · `pp expr` pretty-print · `w` where (stack) · `u`/`d` move up/down
the stack · `q` quit.

```python
import traceback; traceback.print_exc()      # print a traceback from except
import inspect; print(inspect.signature(fn)) # what arguments does it take
dir(obj); help(obj); vars(obj); obj.__dict__ # what is on this object
```

Full process: [reference/debugging_playbook.md](reference/debugging_playbook.md).
