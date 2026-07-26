# Glossary

Every term this course uses, defined plainly. `[D8]` means the concept is taught on
Day 8; look there for the full treatment. Terms marked **[pair]** are the ones
beginners most often mix up — the definitions are written side by side on purpose.

Jump: [A](#a) [B](#b) [C](#c) [D](#d) [E](#e) [F](#f) [G](#g) [H](#h) [I](#i)
[J](#j) [K](#k) [L](#l) [M](#m) [N](#n) [O](#o) [P](#p) [Q](#q) [R](#r) [S](#s)
[T](#t) [U](#u) [V](#v) [W](#w) [Y](#y) [Z](#z)

---

## A

**Absolute path** — A path that starts from the root of the filesystem
(`/home/ada/data.csv`, `C:\Users\Ada\data.csv`) and therefore means the same thing
no matter which folder you run your program from. Contrast *relative path*. [D10]

**Argument** **[pair]** — The actual value you pass when you *call* a function.
In `greet("Ada")`, `"Ada"` is the argument. Contrast *parameter*: the parameter is
the name in the definition, the argument is the value at the call. Mnemonic:
**A**rgument at the **A**ctual call. [D8]

**Argparse** — The standard library module for building command-line interfaces:
you declare the options your script accepts and it parses `sys.argv`, validates
types and generates `--help`. [D17]

**Assertion** — A statement of the form `assert condition, "message"` that raises
`AssertionError` if the condition is falsy. Used for internal sanity checks and as
the core of pytest tests. [D9], [D18]

**Async / await** — Keywords for cooperative concurrency. An `async def` function
is a coroutine; `await` suspends it while it waits for something slow, letting other
coroutines run on the same thread. Good for I/O-bound work, useless for CPU-bound
work. [D20]

**Attribute** — A value or function attached to an object and reached with a dot:
`account.balance`, `path.name`. Instance attributes belong to one object; class
attributes are shared by every instance of the class. [D12]

**AttributeError** — The error Python raises when you ask an object for an
attribute it does not have. Usually a typo, a `None` where you expected an object,
or the wrong type entirely. [D9]

---

## B

**Boolean** — The type with exactly two values, `True` and `False`. Comparisons
produce booleans. [D1]

**Bound method** — A method already attached to a specific instance.
`acct.deposit` is bound (it knows its `self`); `Account.deposit` is not. This is why
you can pass `acct.deposit` around as a callable. [D12]

**break** — Leaves the innermost loop immediately. Contrast `continue`, which only
skips the rest of the current iteration. [D4]

**Bug** — Behaviour that differs from what you intended. Not the same as an
*error*: a program can run without errors and still be wrong.

**Bytes** — Raw binary data, written `b"..."`. Files opened in binary mode give you
bytes; text mode gives you `str`. Converting between them requires an *encoding*.
[D10]

---

## C

**Call** — Running a function or method, written with parentheses: `f()`. Without
the parentheses you have the function object itself, not its result. Forgetting the
parentheses is the cause of a lot of confusing output like
`<function f at 0x7f...>`. [D8]

**Callable** — Anything you can call with `()`: functions, methods, classes, and
objects that define `__call__`. [D16]

**Class** **[pair]** — A template that defines what a kind of object holds and what
it can do. `Account` is a class. Contrast *instance*: the class is the blueprint,
the instance is the thing built from it, and you can have many instances of one
class. [D12]

**Classmethod** — A method that receives the class rather than an instance as its
first argument (`cls`), commonly used to build alternative constructors like
`Temp.from_fahrenheit(212)`. [D13]

**Closure** — A function that remembers variables from the scope where it was
defined, even after that scope has finished. The mechanism decorators are built on.
[D16]

**Comment** — Text after `#` that Python ignores. Write comments about *why*, not
*what* — the code already says what. [D1]

**Composition** **[pair]** — Building an object out of other objects it holds as
attributes ("has-a"). Contrast *inheritance* ("is-a"). Composition is usually the
better default because it couples classes more loosely. [D13]

**Comprehension** — A compact expression that builds a list, dict or set from an
iterable: `[x * 2 for x in xs if x > 0]`. [D15]

**Concatenation** — Joining sequences with `+`: `"ab" + "cd"`, `[1] + [2]`. You
cannot concatenate a `str` and an `int`; use an f-string. [D2]

**Concurrency** — Structuring a program so several tasks are in progress at once.
Not necessarily *parallelism*, which is several tasks literally executing at the
same instant on different cores. [D20]

**Conditional expression** — `a if cond else b`, an expression that produces one of
two values. Different from an `if` *statement*, which does not produce a value.
[D3]

**Constructor** — What builds a new instance. In Python you write `__init__`, which
initialises an already-created object; calling `Account("Ada")` runs it. [D12]

**Context manager** — An object usable with `with`, which guarantees setup and
cleanup even if an exception is raised. `with open(...) as f:` closes the file no
matter what. [D10]

**continue** — Skips the rest of the current loop iteration and starts the next
one. [D4]

**Coverage** — The percentage of your code lines executed by your tests. Useful for
finding untested code; a bad target to optimise for on its own. [D18]

**CPU-bound** **[pair]** — Work limited by computation speed (parsing millions of
rows, image processing). Needs multiple *processes* to go faster. Contrast
*I/O-bound*. [D20]

**CSV** — Comma-separated values: a plain-text table format. Every value read from
a CSV is a string until you convert it. [D10]

---

## D

**Dataclass** — A class defined with the `@dataclass` decorator, which generates
`__init__`, `__repr__` and `__eq__` from the annotated fields. Less boilerplate for
data-shaped classes. [D12]

**Debugger** — A tool that pauses a running program so you can inspect variables
and step line by line. Python's built-in one is `pdb`, entered with
`breakpoint()`. [D9]

**Declaration vs definition** — Python has no separate declaration step: a name
exists once you assign to it, and a function exists once its `def` runs.

**Decorator** — A function that wraps another function to add behaviour, applied
with `@name` above a `def`. `@timed`, `@functools.lru_cache`, `@pytest.fixture`.
[D16]

**Default argument** — A value used for a parameter when the caller omits it:
`def greet(name, greeting="Hello")`. Never use a mutable default like `[]` or `{}`
— it is created once and shared across calls. [D8]

**deque** — `collections.deque`, a double-ended queue with cheap appends and pops
at both ends, unlike a list which is slow at the front. [D17]

**Dict (dictionary)** — A mapping from keys to values, written `{"a": 1}`. Lookup
by key is fast regardless of size. Keys must be *hashable*. [D6]

**Docstring** — A string literal as the first statement of a module, function or
class; it becomes `__doc__` and is what `help()` shows. [D8]

**Dunder method** — A method with double underscores on both sides
(`__init__`, `__repr__`, `__len__`). Python calls these for you when you use
built-in syntax like `len(x)` or `a == b`. Also called a magic or special method.
[D13]

**Duck typing** — Caring about what an object can do rather than what class it is:
if it has `.read()`, it is file-like enough. [D13]

---

## E

**Encoding** — The rule mapping characters to bytes. `utf-8` is the answer in
almost every case. Pass `encoding="utf-8"` explicitly when opening text files so
your program behaves the same on every machine. [D10]

**enumerate** — Wraps an iterable to yield `(index, value)` pairs, so you do not
have to maintain a counter by hand. `enumerate(xs, start=1)` for 1-based. [D5]

**Environment variable** — A named value provided by the operating system to your
process, read with `os.environ.get("NAME")`. The normal way to pass secrets such as
API keys. [D19]

**Error** **[pair]** — Loose everyday word for "something went wrong". In Python
the precise term is *exception*: an object raised to signal a problem. Some
exception classes are named `...Error` (`ValueError`), and some are not
(`StopIteration`). "Exception" is the mechanism; "error" is the category of
exceptions that indicate a mistake. [D9]

**Exception** — An object raised to interrupt normal flow and signal a problem.
Uncaught, it stops the program and prints a *traceback*. See
[error_messages.md](error_messages.md). [D9]

**Exception handling** — Using `try` / `except` to react to exceptions you can
sensibly do something about, rather than crashing. [D9]

**Expression** **[pair]** — Code that produces a value: `2 + 2`, `f(x)`,
`[i for i in xs]`, `a if b else c`. Contrast *statement*, which performs an action
and produces nothing. Rule of thumb: if it can go on the right of `=`, it is an
expression. [D1]

---

## F

**f-string** — A string literal prefixed with `f` where `{}` interpolates
expressions: `f"{name} scored {score:.1f}"`. The standard way to build strings in
modern Python. [D2]

**Falsy / truthy** — Values treated as `False` or `True` in a boolean context.
Falsy: `False`, `0`, `0.0`, `""`, `[]`, `()`, `{}`, `set()`, `None`. Everything else
is truthy. [D3]

**Fixture** — In pytest, a function decorated with `@pytest.fixture` that provides
test data or setup; a test requests it by naming it as a parameter. This course's
`day` fixture loads your `exercises.py`. [D18]

**Float** — A number with a fractional part, stored in binary. `0.1 + 0.2` is not
exactly `0.3`, so compare floats with a tolerance. [D1]

**Floor division** — `//`, division rounded down to an integer: `7 // 2 == 3`,
`-7 // 2 == -4`. [D2]

**Function** **[pair]** — A named, reusable block of code that takes arguments and
returns a value, defined with `def`. Contrast *method*: a method is a function that
belongs to a class and is called on an object (`text.upper()`), so it receives that
object as `self`. Every method is a function; not every function is a method. [D8]

**functools** — Standard library module of tools for working with functions:
`wraps`, `lru_cache`, `partial`, `reduce`. [D16]

---

## G

**Generator** — A lazy iterator produced by a function containing `yield`, or by a
generator expression `(x for x in xs)`. It computes values on demand and can be
iterated only once. [D15]

**GIL (Global Interpreter Lock)** — A lock in CPython that lets only one thread
execute Python bytecode at a time. It is why threads speed up waiting but not
computing, and why CPU-bound work needs processes. [D20]

**Global variable** — A name defined at module level. Readable from inside
functions; rebinding one from inside a function needs the `global` keyword and is
usually a design mistake. [D8]

**Guard clause** — An early `return` or `raise` at the top of a function handling
the invalid or trivial case, so the rest of the body deals only with the normal
case. [D8]

---

## H

**Hashable** — An object with a stable hash value, which is what lets it be a dict
key or set element. Immutable built-ins (`int`, `str`, `tuple` of hashables,
`frozenset`) are hashable; `list`, `dict` and `set` are not. Using an unhashable
object as a key raises `TypeError: unhashable type`. [D6]

**HTTP** — The request/response protocol of the web. You send a method (`GET`,
`POST`) to a URL and get back a status code, headers and a body. [D19]

**HTTP status code** — The three-digit result of a request: 2xx success, 3xx
redirect, 4xx you made a mistake, 5xx the server made a mistake. [D19]

---

## I

**Identity vs equality** — `is` asks "the same object in memory?"; `==` asks "the
same value?". Use `is` only with `None`, `True` and `False`. [D3]

**Immutable** **[pair]** — Cannot be changed after creation: `int`, `float`, `str`,
`bool`, `tuple`, `frozenset`. Operations return new objects instead of modifying,
which is why `s.upper()` must be assigned to something. Contrast *mutable*:
`list`, `dict`, `set` and most custom objects can be modified in place, which means
two names for the same object see each other's changes. [D2], [D5]

**Import** — Loading another module's names into your file: `import json`,
`from pathlib import Path`. [D11]

**Indentation** — Leading whitespace, which in Python defines block structure
rather than being cosmetic. Use 4 spaces per level and never mix tabs with spaces.
[D1]

**IndentationError** — Raised when indentation is missing, unexpected, or
inconsistent. [D9]

**Index** — The position of an item in a sequence, starting at 0. Negative indexes
count from the end: `xs[-1]` is the last item. [D2], [D5]

**IndexError** — Raised when a sequence index is out of range. Almost always an
off-by-one mistake or an empty sequence. [D9]

**Inheritance** **[pair]** — Defining a class that extends another
(`class Savings(Account)`), receiving its attributes and methods and optionally
overriding them. Models "is-a". Contrast *composition*. [D13]

**Instance** **[pair]** — A concrete object built from a class.
`Account("Ada")` creates an instance; `Account` is the class. See *class*. [D12]

**int** — A whole number, unbounded in size in Python. [D1]

**I/O-bound** **[pair]** — Work limited by waiting on something external (network,
disk, database). Threads or `asyncio` help. Contrast *CPU-bound*. [D20]

**Iterable** **[pair]** — Anything you can loop over: list, tuple, str, dict, set,
file, generator, `range`. Formally, something you can call `iter()` on. Contrast
*iterator*: an iterable can be looped over repeatedly, while an iterator is the
single-use cursor produced from it, which yields values via `next()` and is
exhausted afterwards. A list is iterable but not an iterator; a generator is both.
[D15]

**Iterator** **[pair]** — An object with `__next__` that produces values one at a
time and raises `StopIteration` when finished. See *iterable*. [D15]

**itertools** — Standard library module of iterator building blocks: `chain`,
`islice`, `groupby`, `combinations`, `product`, `accumulate`. [D17]

---

## J

**JSON** — A text format for nested data (objects, arrays, strings, numbers,
booleans, null) used by nearly every web API. `json.loads` parses, `json.dumps`
serialises. [D10]

**JSONDecodeError** — Raised when text is not valid JSON. Usually an HTML error
page, an empty response, or single quotes where JSON requires double. [D10]

---

## K

**KeyError** — Raised when you look up a dict key that does not exist. Use
`d.get(key)` or `key in d` when absence is expected. [D6]

**Keyword argument** — An argument passed by name: `greet(name="Ada")`. Clearer
than positional arguments at call sites with several parameters. [D8]

---

## L

**lambda** — A one-expression anonymous function: `lambda x: x * 2`. Handy as a
`key=` argument; use `def` for anything longer. [D16]

**Lazy evaluation** — Producing values only when asked, as generators do. Lets you
process data larger than memory. [D15]

**List** — An ordered, mutable sequence: `[1, 2, 3]`. [D5]

**Local variable** — A name assigned inside a function, visible only there and
gone when the function returns. [D8]

**Logging** — Emitting timestamped, level-tagged messages via the `logging` module
rather than `print`, so output can be filtered, routed and kept. [D17]

**lru_cache** — `functools.lru_cache`, a decorator that memoises a function's
results by its arguments. Only valid for pure functions. [D16]

---

## M

**Method** **[pair]** — A function defined inside a class and called on an object,
receiving that object as `self`. See *function*. [D12]

**Module** **[pair]** — A single `.py` file, importable by its filename without the
extension. Contrast *package*: a package is a directory of modules (traditionally
containing `__init__.py`) that you import with dots, `mypkg.sub.mod`. One file is a
module; a folder of modules is a package. [D11]

**ModuleNotFoundError** — Raised when an import names something Python cannot find.
Usually a missing `pip install`, a typo, an inactive virtualenv, or running from the
wrong directory. A subclass of `ImportError`. [D11]

**Mutable** **[pair]** — Can be changed in place. See *immutable*. [D5]

**Mutation** — Changing an object in place, e.g. `xs.append(1)`. Because a mutable
object can have several names pointing at it, mutation is visible through all of
them. [D5]

**mypy** — A static type checker that reads your type hints and reports
inconsistencies before you run the code. [D18]

---

## N

**Namespace** — A mapping of names to objects. Modules, classes, functions and
instances each have one; `x.y` means "look up `y` in `x`'s namespace". [D11]

**NameError** — Raised when a name has never been assigned in any reachable scope.
Usually a typo, a missing import, or use before assignment. [D9]

**None** — The single value of type `NoneType`, meaning "no value". A function
without an explicit `return` returns it. Test with `x is None`. [D1]

---

## O

**Object** — Any value in Python. Numbers, strings, functions, classes and modules
are all objects with a type and attributes. [D1]

**Off-by-one error** — Being one position out: `range(1, 5)` excludes 5,
`xs[len(xs)]` is out of range, slices exclude their stop. [D4]

**OOP (object-oriented programming)** — Organising code around objects that bundle
data with behaviour. One tool among several — plain functions on plain data are
often better. [D12], [D13]

**Operator** — A symbol performing an operation: `+ - * / // % ** == in and not`.
[D2]

**Override** — Defining a method in a subclass that replaces the parent's version.
Call the original with `super()`. [D13]

---

## P

**Package** **[pair]** — A directory of modules imported with dots. See *module*.
[D11]

**Parameter** **[pair]** — The name in a function definition that receives an
argument. In `def greet(name):`, `name` is the parameter. See *argument*. [D8]

**Parametrize** — `@pytest.mark.parametrize`, which runs one test function over a
table of input/expected pairs, reporting each as a separate test. [D18]

**pathlib** — The modern standard library module for filesystem paths.
`Path("data") / "f.csv"` composes paths portably. [D10]

**pdb** — Python's built-in debugger. Enter it with `breakpoint()`; drive it with
`n`, `s`, `c`, `p`, `l`, `q`. [D9]

**PEP 8** — The style guide for Python code: 4-space indents, `snake_case`
functions and variables, `CapWords` classes, short lines. Tools like `black` and
`ruff` enforce it for you. [D18]

**pip** — Python's package installer. Always invoke it as `python -m pip install X`
so it installs into the interpreter you are actually running. [D11]

**Positional argument** — An argument matched to a parameter by position rather
than name. [D8]

**Process** **[pair]** — An independently running program with its own memory and
its own Python interpreter. Multiple processes sidestep the GIL and are the tool for
CPU-bound work. Contrast *thread*: threads share memory inside one process, which
makes them cheap and good for waiting, but subject to the GIL. [D20]

**Property** — A method exposed as if it were an attribute using `@property`, so
`temp.fahrenheit` computes a value on access. [D13]

**pytest** — The test framework this course is graded with, and the one you learn to
write for yourself on Day 18. Tests are plain functions named `test_*` containing
`assert` statements. [D18]

---

## Q

**Queue** — A first-in-first-out collection. `collections.deque` for single-threaded
use, `queue.Queue` for passing work between threads. [D17], [D20]

---

## R

**raise** — Signals an exception: `raise ValueError("expected positive")`. [D9]

**range** — A lazy sequence of integers. `range(stop)`, `range(start, stop)`,
`range(start, stop, step)`; the stop value is excluded. [D4]

**Raw string** — A literal prefixed with `r` where backslashes are literal:
`r"\d+"`. Standard for regular expressions and Windows paths. [D17]

**RecursionError** — Raised when calls nest too deeply, nearly always because a
recursive function has no base case or never approaches it. [D9]

**Reference vs value** **[pair]** — Assignment copies a *reference* to an object,
not the object. `b = a` gives you a second name for the same list, so `b.append(1)`
changes what `a` sees. Rebinding (`b = [9]`) affects only `b`. Immutable objects
make this invisible, which is why the distinction only bites with lists, dicts,
sets and custom objects. Copy explicitly with `list(a)`, `a.copy()` or
`copy.deepcopy(a)`. [D5]

**Regular expression (regex)** — A pattern language for matching text, used through
the `re` module. Powerful and hard to read; prefer string methods when they
suffice. [D17]

**Relative path** — A path interpreted from the current working directory
(`data/notes.txt`). The reason "it works when I run it from the project folder but
not otherwise". [D10]

**REPL** — Read-eval-print loop: the interactive prompt you get by running `python`
with no arguments. The fastest way to test a one-liner. `exit()` leaves it. [D1]

**repr** — The unambiguous developer-facing string for an object, produced by
`repr(x)` and `__repr__`, and what the REPL shows. `str` is the friendly
user-facing version. Define `__repr__` on your classes; it pays for itself the
first time you debug. [D12]

**requests** — The de facto standard third-party library for HTTP in Python.
Always pass `timeout=`. [D19]

**requirements.txt** — A text file listing a project's dependencies, installed with
`python -m pip install -r requirements.txt`. [D11]

**return** — Ends a function and hands a value back to the caller. A function with
no `return` returns `None`. [D8]

**ruff** — A fast linter (and formatter) that flags likely mistakes and style
problems. [D18]

---

## S

**Scope** — The region of code where a name is visible. Python resolves names
local -> enclosing -> global -> builtins (the LEGB rule). [D8]

**self** — The conventional name for a method's first parameter, which receives the
instance the method was called on. Not a keyword, but never call it anything else.
[D12]

**Sequence** — An ordered iterable supporting indexing and `len()`: `str`, `list`,
`tuple`, `range`. [D5]

**Serialisation** — Converting in-memory objects to text or bytes for storage or
transmission (and back). `json.dumps` / `json.loads`. [D10]

**Set** — An unordered collection of unique, hashable elements: `{1, 2, 3}`. Fast
membership tests. `set()` is the empty set; `{}` is an empty dict. [D6]

**Shadowing** — Defining a name that hides an existing one, e.g. naming a variable
`list` or a file `json.py`. Produces baffling errors; avoid built-in and stdlib
names. [D11]

**Shallow vs deep copy** — A shallow copy (`list(xs)`) duplicates the outer
container but shares the inner objects; `copy.deepcopy(xs)` duplicates everything.
Matters for nested structures. [D5]

**Short-circuit evaluation** — `and` stops at the first falsy operand and `or` at
the first truthy one, so the right-hand side may never run. Enables
`if xs and xs[0] == 1`. [D3]

**Slice** — A sub-sequence selected with `xs[start:stop:step]`; `stop` is excluded,
each part is optional. `xs[:]` copies, `xs[::-1]` reverses. [D2], [D5]

**snake_case** — The naming convention for Python variables and functions:
lowercase words joined by underscores. Classes use `CapWords`. [D1]

**sqlite3** — The standard library module for SQLite, a full SQL database stored in
a single file with no server to run. [D19]

**Standard library** — The modules that ship with Python and need no installation:
`json`, `csv`, `pathlib`, `collections`, `itertools`, `datetime`, `re`, `sqlite3`
and hundreds more. Check here before installing anything. [D17]

**Statement** **[pair]** — Code that performs an action rather than producing a
value: assignment, `if`, `for`, `def`, `return`, `import`. See *expression*. [D1]

**Staticmethod** — A method that takes neither `self` nor `cls`; a plain function
living in a class's namespace. [D13]

**StopIteration** — The exception an iterator raises when exhausted. `for` catches
it for you; you only see it when calling `next()` yourself. [D15]

**str** — The text type. Immutable, indexable, iterable. [D1]

**super()** — Calls the parent class's implementation, most often
`super().__init__(...)`. [D13]

**SyntaxError** — Raised before any code runs, when Python cannot parse your file.
The reported line is where Python noticed the problem, often one line after the
actual cause. [D9]

---

## T

**TabError** — Raised when a file mixes tabs and spaces for indentation. Configure
your editor to insert spaces. [D9]

**TDD (test-driven development)** — Write a failing test, write the minimum code to
pass it, refactor, repeat. [D18]

**Thread** **[pair]** — A unit of execution sharing memory with other threads in the
same process. Cheap to create, limited by the GIL for CPU work, effective for
waiting. See *process*. [D20]

**Timeout** — A limit on how long an operation may wait before failing. Every
network call in your code should have one; without it a hung server hangs your
program forever. [D19]

**Traceback** — The report Python prints for an uncaught exception, listing the call
chain from outermost to innermost with the error type and message on the last line.
Read it bottom-up. [D9]

**Truthiness** — See *falsy / truthy*. [D3]

**Tuple** — An ordered, immutable sequence: `(3, 4)`. Hashable if its contents are,
so it can be a dict key. A one-element tuple needs the trailing comma: `(5,)`.
[D5]

**Type hint (annotation)** — A note about expected types:
`def f(xs: list[int]) -> int:`. Ignored at runtime; checked by tools like mypy and
read by humans and editors. [D8]

**TypeError** — Raised when an operation gets the wrong *type* of thing: adding a
str to an int, calling something that is not callable, subscripting something that
does not support `[]`, passing the wrong number of arguments. Contrast
*ValueError*: right type, wrong value. [D9]

---

## U

**UnboundLocalError** — Raised when a function assigns to a name somewhere in its
body and reads it before that assignment. The assignment makes the name local for
the whole function, hiding any global of the same name. A subclass of `NameError`.
[D9]

**UnicodeDecodeError** — Raised when bytes cannot be decoded with the assumed
encoding — reading a Latin-1 or binary file as UTF-8, for instance. [D10]

**Unpacking** — Spreading a collection into separate names or arguments:
`a, b = pair`, `first, *rest = xs`, `f(*args)`, `f(**kwargs)`. [D5], [D8]

**UTF-8** — The dominant text encoding, able to represent every Unicode character.
Pass `encoding="utf-8"` explicitly when opening text files. [D10]

---

## V

**ValueError** — Raised when a value is the right type but unacceptable:
`int("abc")`, `xs.remove(missing)`, unpacking three items into two names. [D9]

**Variable** — A name bound to an object. Created by assignment; not declared, not
typed, and re-bindable to a different type at any time. [D1]

**venv (virtual environment)** — A self-contained folder with its own Python and
its own installed packages, so projects do not interfere with each other. Create
with `python -m venv .venv`, then activate it. [D11]

**View** — The dynamic objects returned by `d.keys()`, `d.values()` and `d.items()`.
They reflect later changes to the dict and are not lists; wrap in `list()` if you
need one. [D6]

---

## W

**Walrus operator** — `:=`, which assigns inside an expression:
`while (line := f.readline()):`. Occasionally useful, easily overused. [D15]

**while loop** — Repeats while a condition stays truthy. Use it when you do not
know the number of iterations in advance; use `for` when you do. [D4]

**with statement** — Runs a block under a context manager, guaranteeing cleanup.
`with open(path) as f:` is the canonical example. [D10]

**wraps** — `functools.wraps`, the decorator you apply to your wrapper function so
the decorated function keeps its name and docstring. [D16]

---

## Y

**yield** — Turns a function into a generator, producing a value and pausing until
the next value is requested. [D15]

---

## Z

**ZeroDivisionError** — Raised by `x / 0`, `x // 0` and `x % 0`. Guard the divisor
or handle the exception. [D9]

**zip** — Pairs up items from several iterables, stopping at the shortest:
`zip(names, scores)`. `itertools.zip_longest` pads instead of stopping. [D5]

---

Related: [error_messages.md](error_messages.md) ·
[debugging_playbook.md](debugging_playbook.md) ·
[../CHEATSHEET.md](../CHEATSHEET.md) · [../SYLLABUS.md](../SYLLABUS.md)
