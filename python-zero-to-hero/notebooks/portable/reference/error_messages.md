# Error message decoder

Python's error messages are terse but honest. Once you can read them, most bugs
take a minute instead of an hour. Every message below is quoted as Python 3.11+
actually prints it.

How to use this file: copy the last line of your traceback, search this page for
the distinctive part of it (skip the variable names), read "What it means" and
"Usual causes", then apply the fix. If you cannot find your message here, the
process in [debugging_playbook.md](debugging_playbook.md) works on anything.

**First, read the traceback correctly.** The last line is the error type and
message. The line above it is the code that failed. Above that is the chain of
calls that got you there, outermost first. Start at the bottom and walk up until
you reach a file you wrote.

```
Traceback (most recent call last):
  File "report.py", line 12, in <module>     <- your program's entry point
    print(average(scores))
  File "report.py", line 8, in average       <- the function that broke
    return total / len(values)
ZeroDivisionError: division by zero          <- what actually went wrong
```

Contents:
[SyntaxError](#syntaxerror) ·
[IndentationError](#indentationerror-expected-an-indented-block-after-if-statement-on-line-1) ·
[TabError](#taberror-inconsistent-use-of-tabs-and-spaces-in-indentation) ·
[NameError](#nameerror-name-x-is-not-defined) ·
[UnboundLocalError](#unboundlocalerror-cannot-access-local-variable-x-where-it-is-not-associated-with-a-value) ·
[TypeError](#typeerror-can-only-concatenate-str-not-int-to-str) ·
[ValueError](#valueerror-invalid-literal-for-int-with-base-10-abc) ·
[IndexError](#indexerror-list-index-out-of-range) ·
[KeyError](#keyerror-b) ·
[AttributeError](#attributeerror-str-object-has-no-attribute-push) ·
[ImportError](#modulenotfounderror-no-module-named-requests) ·
[ZeroDivisionError](#zerodivisionerror-division-by-zero) ·
[RecursionError](#recursionerror-maximum-recursion-depth-exceeded) ·
[FileNotFoundError](#filenotfounderror-errno-2-no-such-file-or-directory-datacsv) ·
[PermissionError](#permissionerror-errno-13-permission-denied-outcsv) ·
[UnicodeDecodeError](#unicodedecodeerror-utf-8-codec-cant-decode-byte-0xff-in-position-0-invalid-start-byte) ·
[JSONDecodeError](#jsondecodeerror-expecting-value-line-1-column-1-char-0) ·
[AssertionError](#assertionerror) ·
[StopIteration](#stopiteration)

---

## SyntaxError

SyntaxError is special: it happens *before your program runs*, while Python is
parsing the file. Nothing executed. The line number Python reports is where it
noticed the problem, which is frequently one or more lines *after* the real
mistake — an unclosed bracket on line 10 is often reported on line 11 or 12.

### `SyntaxError: '(' was never closed`

**What it means:** you opened a bracket and never closed it. Python read to the end
of the file still waiting for the `)`.

**Usual causes:** a missing closing parenthesis, bracket or brace; a long call
split across lines with one `)` too few.

```python
x = ("a"
y = 2
# SyntaxError: '(' was never closed
```

**Fix:** go to the line the message names — that is where the *opening* bracket is,
which is genuinely helpful — and count your brackets. Editors match them for you if
you put the cursor on one.

### `SyntaxError: invalid syntax`

**What it means:** Python cannot make sense of the code at all. The most generic
parse failure.

**Usual causes:** a stray or missing symbol; using a reserved word as a variable
name (`class = 5`, `for = 1`); a missing operator; Python 2 syntax such as
`print "hi"`.

```python
if x == 1 print("yes")
# SyntaxError: invalid syntax
```

**Fix:** read the whole reported line character by character, then read the line
above it. Check for a reserved word used as a name: `and as assert async await
break class continue def del elif else except False finally for from global if
import in is lambda None nonlocal not or pass raise return True try while with
yield`.

### `SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?`

**What it means:** you used the assignment operator `=` where a comparison `==`
belongs.

```python
if x = 1:
    pass
# SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

**Fix:** `if x == 1:`. One `=` stores a value, two `=` compare values. Related
variant on the left of an assignment: `SyntaxError: cannot assign to literal here.
Maybe you meant '==' instead of '='?` from writing `5 = x`.

### `SyntaxError: expected ':'`

**What it means:** a block-opening statement is missing its colon.

```python
if True
    pass
# SyntaxError: expected ':'
```

**Fix:** add the `:`. Every `if`, `elif`, `else`, `for`, `while`, `def`, `class`,
`try`, `except`, `finally` and `with` ends with a colon.

### `SyntaxError: unterminated string literal (detected at line N)`

**What it means:** a quote was opened and not closed on the same line.

```python
name = "Ada
# SyntaxError: unterminated string literal (detected at line 1)
```

**Fix:** close the quote. If the text itself contains a quote, either use the other
quote style (`'He said "hi"'`), escape it (`"He said \"hi\""`), or use triple
quotes for genuinely multi-line text. The related
`SyntaxError: unterminated triple-quoted string literal` means a `"""` block was
never closed.

### `SyntaxError: 'return' outside function`

**What it means:** a `return` appears at module level, not inside a `def`.

**Usual causes:** wrong indentation, so a line you intended to be part of a
function is not; or a `return` where you wanted `print` or `sys.exit()`.

```python
return 5
# SyntaxError: 'return' outside function
```

**Fix:** indent it into the function, or use `print`/`sys.exit()` at top level.
Siblings of this error: `'break' outside loop`, `'continue' not properly in loop`.

### `SyntaxError: leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers`

**What it means:** you wrote a number like `007`. Leading zeros used to mean octal,
so Python rejects them.

**Fix:** write `7`. If you want a zero-padded *string*, that is formatting:
`f"{7:03d}"` gives `"007"`.

---

## `IndentationError: expected an indented block after 'if' statement on line 1`

**What it means:** you opened a block with a colon and then did not indent the next
line.

**Usual causes:** forgetting to indent after `if`/`for`/`def`; deleting the only
line of a block and leaving the header behind.

```python
if True:
pass
# IndentationError: expected an indented block after 'if' statement on line 1
```

**Fix:** indent the body by 4 spaces. If you want a deliberately empty block, put
`pass` in it — indented.

**Variants:**

- `IndentationError: unexpected indent` — a line is indented with no block to
  belong to.
- `IndentationError: unindent does not match any outer indentation level` — you
  dedented to a level that no enclosing block uses, e.g. going from 4 spaces to 2.

```python
x = 1
  y = 2
# IndentationError: unexpected indent
```

**Fix for all three:** use exactly 4 spaces per level, consistently, and let your
editor show whitespace.

---

## `TabError: inconsistent use of tabs and spaces in indentation`

**What it means:** the same file indents with tabs in some places and spaces in
others. Python refuses to guess what you meant.

**Usual causes:** copy-pasting code from a web page into a file you had been
indenting with spaces; an editor configured to insert tabs.

```python
if True:
    x = 1     # 4 spaces
	y = 2     # a tab -> TabError
```

**Fix:** convert the file to spaces only. In VS Code: "Convert Indentation to
Spaces" from the command palette, and set `"editor.insertSpaces": true` with
`"editor.tabSize": 4`. Running `black .` also normalises it. This is the single
best argument for typing code by hand rather than pasting it.

---

## `NameError: name 'x' is not defined`

**What it means:** you used a name Python has never seen assigned in any scope it
can reach.

**Usual causes:** a typo; using a variable before assigning it; forgetting an
`import`; expecting a variable created inside a function or `if` branch to exist
outside it; quoting problems, so text was read as a name
(`print(hello)` instead of `print("hello")`).

```python
print(usrename)
# NameError: name 'usrename' is not defined
```

**Fix:** check the spelling against the assignment (Python is case-sensitive:
`Print` is not `print`). Confirm the assignment actually runs before this line —
a name assigned only inside `if cond:` does not exist when `cond` was false. If it
is a library name, add the import.

---

## `UnboundLocalError: cannot access local variable 'x' where it is not associated with a value`

**What it means:** inside this function, `x` is a *local* variable — because
somewhere in the body you assign to it — and you read it before that assignment
ran. The global `x` is invisible as a result.

**Usual causes:** an accumulator you forgot to initialise; `count = count + 1`
where `count` is a module-level variable.

```python
count = 0

def bump():
    print(count)      # reading...
    count = count + 1 # ...but this assignment makes `count` local for the whole body

bump()
# UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

**Fix:** the good fix is to pass the value in and return the new one:

```python
def bump(count: int) -> int:
    return count + 1

count = bump(count)
```

The blunt fix is `global count` as the first line of the function. It works, and it
makes the function harder to test and reason about. Prefer the first version.

---

## `TypeError: can only concatenate str (not "int") to str`

**What it means:** you used `+` between a string and something that is not a
string. Python will not silently convert.

```python
age = 30
print("I am " + age)
# TypeError: can only concatenate str (not "int") to str
```

**Fix:** use an f-string, which converts for you:

```python
print(f"I am {age}")
print("I am " + str(age))     # also correct, less readable
```

The mirror-image message `TypeError: unsupported operand type(s) for +: 'int' and
'str'` means the same thing with the operands the other way round — the classic
cause is forgetting that `input()` returns a string:

```python
n = input("number: ")   # "5", a str
total = n + 1           # TypeError
total = int(n) + 1      # fix
```

The list version is `TypeError: can only concatenate list (not "str") to list`.

### `TypeError: 'int' object is not callable`

**What it means:** you put `()` after something that is not a function. Calling is
what `()` does, and an `int` cannot be called.

**Usual causes:** shadowing a function name with a value (`sum = 10`, then
`sum(xs)`); a missing operator (`2(3 + 4)` where you meant `2 * (3 + 4)`);
accidentally calling a variable.

```python
x = 5
x()
# TypeError: 'int' object is not callable
```

**Fix:** rename the variable so it stops shadowing the function, or remove the
parentheses. Never name a variable `list`, `dict`, `str`, `sum`, `max`, `min`,
`type`, `id`, `input` or `len`. `'str' object is not callable` and
`'list' object is not callable` are the same mistake with other types.

### `TypeError: 'int' object is not subscriptable`

**What it means:** you used `[]` on an object that does not support indexing.
"Subscript" is the formal name for `x[...]`.

**Usual causes:** indexing a number; indexing the result of a function that
returned `None`; calling a function with `[]` instead of `()`.

```python
x = 5
x[0]
# TypeError: 'int' object is not subscriptable
```

**Fix:** check what the object really is with `print(type(x), x)`. The
`'NoneType' object is not subscriptable` variant almost always means an earlier
function returned `None` — usually because it had no `return`, or because you
assigned the result of a mutating method: `xs = xs.sort()` sets `xs` to `None`. Use
`xs.sort()` alone, or `ys = sorted(xs)`.

`'function' object is not subscriptable` means you wrote `f[0]` where `f(0)` was
intended.

### `TypeError: unhashable type: 'list'`

**What it means:** you tried to use a mutable object as a dict key or a set
element. Those containers need a stable hash, and mutable objects cannot promise
one.

```python
seen = {}
seen[[1, 2]] = "x"
# TypeError: unhashable type: 'list'
```

**Fix:** convert to an immutable equivalent — `tuple([1, 2])` for a list,
`frozenset({...})` for a set:

```python
seen[(1, 2)] = "x"
```

`unhashable type: 'dict'` and `unhashable type: 'set'` are the same problem.

### `TypeError: f() missing 1 required positional argument: 'b'`

**What it means:** you called a function with fewer arguments than it requires.

```python
def f(a, b): ...
f(1)
# TypeError: f() missing 1 required positional argument: 'b'
```

**Fix:** pass the missing argument, or give the parameter a default in the
definition (`def f(a, b=0)`).

**A special case worth memorising:** if the message names `self` when you called a
method on an instance, you probably defined the method without `self`:

```python
class Counter:
    def bump(value):      # missing self
        return value + 1

Counter().bump(1)
# TypeError: Counter.bump() takes 1 positional argument but 2 were given
```

Every instance method takes `self` first.

**Related messages:**

- `TypeError: f() takes 1 positional argument but 2 were given` — too many
  arguments.
- `TypeError: f() got an unexpected keyword argument 'b'` — a keyword name that is
  not a parameter. Check spelling against the definition.

### `TypeError: object of type 'int' has no len()`

**What it means:** `len()` needs something with a length: a string, list, tuple,
dict, set. Numbers do not have one.

```python
len(5)
# TypeError: object of type 'int' has no len()
```

**Fix:** to count digits, use `len(str(n))`. If the message says `'NoneType'`, an
earlier function returned `None`.

### `TypeError: 'NoneType' object is not iterable`

**What it means:** you tried to loop over, unpack, or `list()` something that is
`None`.

**Usual causes:** a function that forgot to `return`; the return value of a mutating
method (`.sort()`, `.append()`, `.update()` all return `None`).

```python
def evens(xs):
    result = [x for x in xs if x % 2 == 0]
    # forgot: return result

for x in evens([1, 2, 3]):
    print(x)
# TypeError: 'NoneType' object is not iterable
```

**Fix:** add the `return`. `'int' object is not iterable` is the same shape of
mistake: `for x in 5` should be `for x in range(5)`.

### `TypeError: '<' not supported between instances of 'str' and 'int'`

**What it means:** you compared or sorted values of types Python has no ordering
rule for.

**Usual causes:** sorting a list with mixed types; comparing a number to a string
read from `input()`, a CSV, or a JSON payload.

```python
sorted([1, "a"])
# TypeError: '<' not supported between instances of 'str' and 'int'
```

**Fix:** normalise the types first — `sorted(xs, key=str)` or
`sorted(int(x) for x in xs)` — and convert input at the boundary of your program,
so the inside only ever handles real numbers.

---

## `ValueError: invalid literal for int() with base 10: 'abc'`

**What it means:** the type was right (a string) but the *value* cannot be
interpreted as an integer. That distinction is exactly what separates ValueError
from TypeError.

**Usual causes:** user input that is not a number; an empty string; a stray space
or currency symbol; `int("3.5")` — `int()` will not parse a decimal point.

```python
int("abc")     # ValueError: invalid literal for int() with base 10: 'abc'
int("3.5")     # ValueError: invalid literal for int() with base 10: '3.5'
```

**Fix:** `int(float("3.5"))` for decimal text; `.strip()` first; and validate
input rather than assuming:

```python
raw = input("age: ").strip()
try:
    age = int(raw)
except ValueError:
    print(f"{raw!r} is not a whole number")
```

### `ValueError: too many values to unpack (expected 2)`

**What it means:** the number of names on the left of `=` does not match the number
of items on the right.

```python
a, b = [1, 2, 3]
# ValueError: too many values to unpack (expected 2)
```

**Fix:** match the counts, or absorb the rest with `*`:

```python
a, b, *rest = [1, 2, 3]
```

The other direction is `ValueError: not enough values to unpack (expected 3, got
2)`. A common real-world source is splitting a line that does not have the shape
you assumed — use `line.split(",", 1)` or `maxsplit` to control it.

### Other common ValueErrors

| Message | Cause | Fix |
|---|---|---|
| `ValueError: list.remove(x): x not in list` | removing a value that is absent | check `if x in xs:` first |
| `ValueError: 5 is not in list` | `.index()` on an absent value | use `if x in xs` or catch the error |
| `ValueError: math domain error` | `math.sqrt(-1)`, `math.log(0)` | validate the argument first |
| `ValueError: I/O operation on closed file` | using a file object outside its `with` block | move the work inside the `with` |

---

## `IndexError: list index out of range`

**What it means:** the index you asked for does not exist. Valid indexes for a
sequence of length n are `0` to `n - 1`, plus `-1` to `-n`.

**Usual causes:** off-by-one (`xs[len(xs)]`); assuming a list is non-empty;
`row[3]` on a CSV line with three fields.

```python
xs = [1, 2]
xs[5]
# IndexError: list index out of range
```

**Fix:** guard before indexing (`if xs:`, `if len(row) > 3:`), iterate with `for x
in xs` instead of manual indexing, or slice — slicing never raises, `xs[5:9]`
simply gives `[]`.

**Variants:** `IndexError: string index out of range`,
`IndexError: tuple index out of range`, `IndexError: pop from empty list`.

---

## `KeyError: 'b'`

**What it means:** the dict has no such key. The message is just the key, with no
explanation, which makes it look cryptic the first time.

**Usual causes:** a typo in the key; a key that is genuinely optional; a case or
whitespace difference (`"Name"` vs `"name"`, `"a "` vs `"a"`); an integer key where
the dict has string keys, or the reverse — `d[1]` and `d["1"]` are different keys.

```python
d = {"a": 1}
d["b"]
# KeyError: 'b'
```

**Fix:** pick the tool that matches your intent:

```python
d.get("b")            # None when absent
d.get("b", 0)         # a default
if "b" in d: ...      # explicit check
d.setdefault("b", []) # insert-if-absent, then use
from collections import defaultdict
counts = defaultdict(int)   # every key springs into existence at 0
```

Print `sorted(d.keys())` when you cannot see the difference — it is usually
whitespace or case. `KeyError` also comes from `d.pop(k)` on a missing key and from
`os.environ["MISSING"]`; use `os.environ.get("NAME")` for the latter.

---

## `AttributeError: 'str' object has no attribute 'push'`

**What it means:** the object does not have the attribute or method you asked for.

**Usual causes:** a method from another language (`push` is JavaScript; Python
lists use `append`); a typo; using a method of the wrong type
(`"abc".append("d")`); the object being `None`; the object being a module rather
than what you expected.

```python
"abc".push("d")
# AttributeError: 'str' object has no attribute 'push'
```

**Fix:** the message names the type — check that type's real methods with
`print(type(x))` then `dir(x)` or `help(type(x))`.

**The most important variant:**

```python
name = None
name.strip()
# AttributeError: 'NoneType' object has no attribute 'strip'
```

`'NoneType' object has no attribute ...` almost never means the line it points at
is wrong. It means something *earlier* produced `None`: a function with no
`return`, a `.get()` that missed, a regex `search` that did not match, or an
assignment from a mutating method. Walk backwards to where the value was created.

**Other variants:**

- `AttributeError: module 'json' has no attribute 'load_string'` — the function
  does not exist under that name (it is `json.loads`). Also produced when your own
  file shadows a stdlib module: a file named `json.py` in your folder gets imported
  instead of the real one. Rename your file and delete `__pycache__/`.
- `AttributeError: 'Account' object has no attribute 'blance'` — a typo in an
  attribute name, or an attribute never assigned in `__init__`.

---

## `ModuleNotFoundError: No module named 'requests'`

**What it means:** Python could not find that module anywhere on its import path.
`ModuleNotFoundError` is a subclass of `ImportError`.

**Usual causes:** the package is not installed; it is installed into a *different*
Python than the one running your code; a virtualenv you forgot to activate; a typo
(`reqeusts`); or you are running from the wrong directory so your own module is not
importable.

```python
import reqeusts
# ModuleNotFoundError: No module named 'reqeusts'
```

**Fix, in order:**

1. Check the spelling.
2. Install with the `-m` form, which guarantees the right interpreter:
   `python -m pip install requests`
3. If you use a virtualenv, activate it *first*
   (`source .venv/bin/activate`), then install.
4. Compare interpreters when it still fails:

```bash
python -c "import sys; print(sys.executable)"
python -m pip -V
```

Both should point into the same folder. If they do not, that is your bug.

For `No module named 'pytest'` specifically, see the troubleshooting table in
[../SETUP.md](../SETUP.md).

**Related:** `ImportError: cannot import name 'loadz' from 'json'` — the module was
found, but it has no such name. Check the spelling and the module's documentation.
Also: `ImportError: attempted relative import with no known parent package` means
you ran a file inside a package directly; run it as a module from the project root
with `python -m mypkg.module` instead [D11].

---

## `ZeroDivisionError: division by zero`

**What it means:** you divided by zero. `/` gives `division by zero`, `//` gives
`integer division or modulo by zero`, `%` gives `integer modulo by zero`, and
dividing a float gives `float division by zero`.

**Usual causes:** computing an average of an empty collection; a denominator that
comes from data; a percentage where the total is zero.

```python
def average(values):
    return sum(values) / len(values)

average([])
# ZeroDivisionError: division by zero
```

**Fix:** decide what the empty case *means* and say so explicitly:

```python
def average(values: list[float]) -> float:
    if not values:
        return 0.0        # or raise ValueError("average of no values")
    return sum(values) / len(values)
```

---

## `RecursionError: maximum recursion depth exceeded`

**What it means:** a function called itself (directly or in a cycle) about a
thousand times deep and Python stopped it before the process ran out of stack.

**Usual causes:** a recursive function with no base case; a base case that is never
reached because the argument does not shrink; a `__getattr__` or property that
refers to itself; two functions that call each other.

```python
def countdown(n):
    print(n)
    countdown(n - 1)    # never stops

countdown(3)
# RecursionError: maximum recursion depth exceeded
```

**Fix:** add a base case that certainly gets hit, and make sure each call moves
towards it:

```python
def countdown(n: int) -> None:
    if n <= 0:
        return
    print(n)
    countdown(n - 1)
```

Do not raise the recursion limit to make the symptom go away. If the depth is
genuinely large, rewrite the function as a loop. A property that returns
`self.value` where `value` is the property itself is the sneakiest version of this
error — look for a name that refers to itself.

---

## `FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'`

**What it means:** nothing exists at that path, relative to the *current working
directory* of the process — not relative to the file containing the code.

**Usual causes:** running the script from a different folder than you assume; a
typo or wrong case in the filename; a relative path in code that is invoked from
elsewhere; the file not created yet; opening for reading (`"r"`) a file you meant
to create (`"w"`).

```python
open("data.csv")
# FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'
```

**Fix:** find out where you actually are, then build the path deliberately.

```python
from pathlib import Path
print(Path.cwd())                     # where am I?
print(sorted(p.name for p in Path.cwd().iterdir()))   # what is here?

HERE = Path(__file__).parent          # the folder containing this .py file
data = HERE / "data.csv"              # stable regardless of where you run from
if not data.exists():
    raise SystemExit(f"expected a data file at {data}")
```

**Neighbours:** `IsADirectoryError: [Errno 21] Is a directory: '.'` (you passed a
folder to `open`), `NotADirectoryError`, and `FileExistsError` (mode `"x"` on a
file that already exists).

---

## `PermissionError: [Errno 13] Permission denied: 'out.csv'`

**What it means:** the path exists (or its folder does) but your user is not
allowed to do what you asked.

**Usual causes:** writing to a system folder or a location owned by another user;
the file open in another program that locks it (common on Windows with Excel and
CSVs); trying to `open()` a directory for writing; a read-only file.

```python
open("/etc/hosts", "w")
# PermissionError: [Errno 13] Permission denied: '/etc/hosts'
```

**Fix:** write somewhere you own — inside your project folder, or a `tmp/`
directory you create. Close the file in the other program. Do not run Python with
`sudo` to work around this; it hides the real problem and creates root-owned files
you cannot clean up later.

---

## `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`

**What it means:** you opened a file as UTF-8 text, but its bytes are not valid
UTF-8. Python will not guess an encoding for you.

**Usual causes:** the file is actually a binary file (image, zip, `.xlsx`, SQLite
db); it was saved in a legacy encoding such as `cp1252` or `latin-1` by a Windows
program; it is a CSV exported from Excel.

```python
b"\xff\xfe\x00".decode("utf-8")
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
```

**Fix:** decide what the file really is.

```python
# binary data: read bytes, do not decode
data = Path("image.png").read_bytes()

# legacy text encoding
text = Path("legacy.csv").read_text(encoding="cp1252")

# Excel CSVs often carry a UTF-8 byte order mark
text = Path("export.csv").read_text(encoding="utf-8-sig")

# last resort when a few bad bytes are acceptable to lose
text = Path("messy.txt").read_text(encoding="utf-8", errors="replace")
```

Write UTF-8 yourself, always, and pass `encoding=` explicitly on every text open.
The mirror error, `UnicodeEncodeError`, means the target encoding cannot represent
a character you are writing — the fix is the same: use UTF-8.

---

## `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

**What it means:** what you handed to `json.loads` is not JSON. Column 1 char 0
specifically means it went wrong at the very first character, so it is usually not
JSON at all.

**Usual causes:** an empty string or empty file; an HTML error page from a failed
HTTP request; a plain-text error body; a response you forgot to check the status
code of; passing a filename where the *contents* were expected.

```python
import json
json.loads("")                    # JSONDecodeError: Expecting value: line 1 column 1 (char 0)
json.loads("<html>error</html>")  # same message
```

**Fix:** look at the raw text before parsing it.

```python
print(repr(response.text[:200]))     # what did the server actually send?
response.raise_for_status()           # fail loudly on 4xx/5xx before parsing
```

**Variants and their causes:**

| Message | Cause | Fix |
|---|---|---|
| `Expecting property name enclosed in double quotes` | single quotes (a Python dict repr, not JSON), or a trailing comma before `}` | use `"` for all keys and strings; remove trailing commas |
| `Expecting ',' delimiter` | a missing comma between items | add it |
| `Extra data: line 1 column N` | two JSON documents in one string, e.g. JSON Lines | parse line by line: `[json.loads(l) for l in text.splitlines() if l]` |
| `Expecting ':' delimiter` | a key with no value | fix the object |

Remember `json.loads` takes a *string* and `json.load` takes a *file object*.
Passing the wrong one is a common source of confusion; the `s` stands for string.

---

## `AssertionError`

**What it means:** an `assert` statement's condition was falsy. If you wrote
`assert x, "message"`, the message appears after the colon; with no message you get
a bare `AssertionError` and have to look at the line.

```python
total = -5
assert total >= 0, f"total went negative: {total}"
# AssertionError: total went negative: -5
```

**In your own code:** an assert documents an invariant you believe is always true.
Reaching it means your belief was wrong; find out why rather than deleting the
assert.

**In pytest:** an AssertionError is just a failing test. pytest rewrites the
assertion so it shows both sides of the comparison — read the `assert 3 == 4`
section of the output, and the `E` lines below it, to see what your function
returned versus what was expected. Note that `assert` statements are skipped
entirely when Python runs with `-O`, so never use them for input validation in
production code; `raise ValueError(...)` for that.

---

## `StopIteration`

**What it means:** an iterator has no more values. `for` loops catch this
internally, which is why you normally never see it; you see it when you call
`next()` yourself.

```python
g = iter([])
next(g)
# StopIteration
```

**Fix:** supply a default, which turns exhaustion into a value:

```python
first = next((x for x in xs if x > 10), None)
```

Also remember a generator is exhausted after one pass. If a second loop over the
same generator produces nothing, that is not a bug in the loop — materialise it
with `list(...)` first if you need it twice [D15].

---

## Still stuck?

The error you cannot find is usually a variant of one above with different type or
variable names. Strip out the names and search again. If that fails, work through
[debugging_playbook.md](debugging_playbook.md) — the process there does not depend
on recognising the message.

Related: [glossary.md](glossary.md) · [../CHEATSHEET.md](../CHEATSHEET.md) ·
[../SETUP.md](../SETUP.md)
