# Day 11 — Modules and Environments

> **Time:** ~4 hours  |  **Prerequisites:** Day 10

## What you'll be able to do after today
- Split a program across several files and import between them using the right form of `import`.
- Explain what `if __name__ == "__main__":` does, why it exists, and what breaks without it.
- Build a small package with `__init__.py`, and choose between absolute and relative imports with a reason.
- Trace how Python finds a module through `sys.path`, and diagnose "why is it importing the wrong thing" and `ModuleNotFoundError`.
- Recognise a circular import from its error message and break it three different ways.
- Create and use a virtual environment, install packages with `pip`, and write a `requirements.txt` a stranger can install from.

## Why this matters

Every program you have written so far lives in one file. Real projects do not: they have a data layer, a reporting layer, a command-line entry point, and a test suite, and they need to share code between them without copy-paste. Modules are the unit of that sharing, and they are also the unit of *naming* — the reason two libraries can both have a `parse` function without colliding.

The environment half is not administrivia. "It works on my machine" is almost always a dependency story: you installed something globally last March, your colleague did not, and the app crashes on their laptop. A virtual environment plus a pinned `requirements.txt` is the difference between a project someone can run in 30 seconds and a project they give up on. Hiring managers notice which one you produce.

---

## 1. What a module is

A module is a `.py` file. That is the whole definition. When you `import` it, Python runs it top to bottom, once, and hands you a module object whose attributes are the names it defined.

Two files, side by side:

```python
# greetings.py
GREETING = "Hello"

def greet(name):
    return f"{GREETING}, {name}!"

print("greetings.py is being run")     # deliberately noisy, for the demo
```

```python
# app.py
import greetings

print(greetings.greet("Ada"))
print(greetings.GREETING)
```

Running `python app.py` prints:

```
greetings.py is being run
Hello, Ada!
Hello
```

Three things happened, in order:

1. Python found `greetings.py`.
2. It **executed the entire file** — which is why "greetings.py is being run" appeared *before* anything in `app.py`'s body after the import.
3. It bound the resulting module object to the name `greetings`, so `greetings.greet` reaches inside it.

Two consequences to internalise now:

**Import runs code.** A module with `print(...)`, a network call, or a file write at the top level does that work every time someone imports it. Top-level code in a module should define things, not do things.

**Import happens once.** The second `import greetings`, anywhere in your program, does not re-run the file; Python reuses the cached module from `sys.modules`.

```python
import greetings
import greetings          # no output the second time — already imported
import sys
print("greetings" in sys.modules)     # True
```

That cache is why a module is a natural place for shared state, and why editing a module while an interactive session is running has no effect until you restart it.

> **Gotcha:** never name your file after a module you want to use. A file called `json.py` in your project shadows the standard library's `json`, and the error you get (`AttributeError: module 'json' has no attribute 'loads'`) points nowhere near the cause. Same for `random.py`, `csv.py`, `email.py`, `test.py`, `types.py`.

---

## 2. The import forms

```python
import textkit                              # 1. the module object
import textkit.stats                         # 2. a submodule
import numpy as np                           # 3. with an alias
from textkit import stats                    # 4. one name out of a package
from textkit.cleaning import normalize       # 5. one name out of a module
from textkit.cleaning import normalize as clean   # 6. imported name, aliased
from textkit import *                        # 7. everything — do not do this
```

What each gives you, and when to use it:

| Form | You then write | Use it when |
|---|---|---|
| `import module` | `module.thing()` | Default. The prefix says where `thing` came from. |
| `import package.module` | `package.module.thing()` | Same, for a submodule. |
| `import module as alias` | `alias.thing()` | The real name is long or conventional (`np`, `pd`). |
| `from module import thing` | `thing()` | You use `thing` constantly and its origin is obvious. |
| `from module import thing as other` | `other()` | Two modules export the same name. |
| `from module import *` | everything | Never, in code you keep. |

Why `import module` is the default choice: `stats.mean(values)` tells the reader where `mean` came from, and it cannot be silently shadowed by a local function called `mean`. `from module import *` is worse than verbose — it dumps unknown names into your namespace, so a reader cannot tell what `normalize` is, and a new version of the module can break your code by adding a name that collides with yours.

```python
from textkit.cleaning import normalize
print(normalize("  Hello, WORLD  "))     # hello, world

import textkit.cleaning
print(textkit.cleaning.normalize("  Hi  "))    # hi   — same function, clearer origin
```

Alias conventions you should follow because everyone else does: `import numpy as np`, `import pandas as pd`, `import matplotlib.pyplot as plt`. Do not invent your own aliases for well-known libraries.

Style, from PEP 8: imports go at the **top** of the file, one per line, in three groups separated by blank lines — standard library, third-party, then your own code:

```python
import csv
import json
from pathlib import Path

import pytest

from textkit.cleaning import normalize
from textkit.stats import word_counts
```

> **Gotcha:** `from module import thing` copies a *reference* at import time. If the module later rebinds `thing`, your name still points at the old object. This is why `from settings import DEBUG` gives you a stale value when something reassigns `settings.DEBUG` at runtime, while `settings.DEBUG` always reads the current one.

---

## 3. `if __name__ == "__main__":`

Every module has a `__name__`. Python sets it to `"__main__"` for the file you *ran*, and to the module's own dotted name for anything you *imported*.

```python
# demo.py
print(f"demo.py sees __name__ == {__name__!r}")

def main():
    print("doing the real work")

if __name__ == "__main__":
    main()
```

```bash
$ python demo.py
demo.py sees __name__ == '__main__'
doing the real work
```

```python
>>> import demo
demo.py sees __name__ == 'demo'
# main() did NOT run
```

So the idiom means exactly: **run this only when this file is the program, not when it is a library.** Without it, importing a module to reuse one function also launches its command-line behaviour — which is how you get a test suite that unexpectedly starts a web server, or a module that prompts for input during import.

The full professional shape:

```python
def main() -> int:
    """The entry point. Returns the process exit code."""
    ...
    return 0

if __name__ == "__main__":
    raise SystemExit(main())     # exit code 0 on success, non-zero on failure
```

Why `main()` as a function rather than code under the `if`: it is testable (a test can call `main()`), its variables are local rather than global, and the exit code becomes explicit. `raise SystemExit(main())` is the compact, portable way to set that code.

> **Gotcha:** the string is `"__main__"` with two underscores on each side, and `__name__` likewise. A typo here makes the block silently never run, which looks exactly like "my script does nothing".

---

## 4. Packages and `__init__.py`

A **package** is a directory of modules. The presence of `__init__.py` makes it a regular package, and running `__init__.py` is what "importing the package" means.

You will build this today (section 10) and it ships in this folder as `textkit/` for comparison:

```
day11_modules_and_environments/
    textkit/
        __init__.py        # marks the directory as a package; sets up the public API
        cleaning.py        # normalize(), strip_punctuation()
        stats.py           # word_counts(), top_words()
    examples.py
```

```python
# textkit/cleaning.py
PUNCTUATION = ".,!?;:\"'()[]"

def strip_punctuation(word: str) -> str:
    """Return `word` without leading/trailing punctuation."""
    return word.strip(PUNCTUATION)

def normalize(text: str) -> str:
    """Return `text` lowercased with runs of whitespace collapsed to one space."""
    return " ".join(text.lower().split())
```

```python
# textkit/stats.py
from .cleaning import normalize, strip_punctuation      # relative import

def word_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for raw_word in normalize(text).split():
        word = strip_punctuation(raw_word)
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts
```

```python
# textkit/__init__.py
"""textkit — small text-cleaning helpers."""

from .cleaning import normalize, strip_punctuation
from .stats import top_words, word_counts

__version__ = "0.1.0"
__all__ = ["normalize", "strip_punctuation", "word_counts", "top_words"]
```

Now the package has a flat, friendly surface, while the code stays in separate files:

```python
import textkit

print(textkit.normalize("  Hello,   WORLD "))     # hello, world
print(textkit.word_counts("the cat the dog"))      # {'the': 2, 'cat': 1, 'dog': 1}
print(textkit.__version__)                          # 0.1.0
```

What `__init__.py` is for:

1. **Marking** the directory as a package (see the namespace-package note below).
2. **Curating a public API** — re-export the handful of names users need so they write `textkit.normalize` instead of `textkit.cleaning.normalize`.
3. Declaring package-level metadata such as `__version__`.
4. Declaring `__all__`, which lists the public names (and is what `from textkit import *` would use).

What it is *not* for: real work. Anything expensive in `__init__.py` runs on every import of anything in the package.

Since Python 3.3, a directory *without* `__init__.py` can still be imported as a "namespace package". It works, and it will also silently let a typo'd directory name become a package, and it disables the API-curation above. Write the `__init__.py`. An empty one is fine.

Subpackages nest the same way: `textkit/formats/__init__.py`, imported as `textkit.formats`.

> **Gotcha:** `import textkit` does not automatically give you `textkit.stats` unless `__init__.py` imported it. Without that line, `textkit.stats.word_counts(...)` raises `AttributeError: module 'textkit' has no attribute 'stats'` — you need `import textkit.stats` explicitly.

---

## 5. Absolute vs relative imports

**Absolute** imports name the full path from the top-level package:

```python
from textkit.cleaning import normalize
import textkit.stats
```

**Relative** imports are written from the current module's position, using dots:

```python
from . import cleaning              # the same package as me
from .cleaning import normalize     # a sibling module
from .. import config               # one package up
from ..formats.csvio import read    # up one, then down another branch
```

Reading the dots: **one dot = "this package"**, each extra dot = one level further up. The dots refer to *packages*, not files, and they are counted from the module's package, not from the filesystem root.

| Inside module | Written | Resolves to |
|---|---|---|
| `pkg.sub.mod` | `from .helpers import x` | `pkg.sub.helpers` |
| `pkg.sub.mod` | `from ..util import x` | `pkg.util` |
| `pkg.sub.mod` | `from . import other` | `pkg.sub.other` |
| `pkg.mod` | `from ...x import y` | `ImportError` — above the top-level package |

Which to use:

- **Inside a package, referring to its own modules:** relative is good. It states "these files belong together", and renaming the package does not require editing every file. This is why `textkit/stats.py` says `from .cleaning import normalize`.
- **Everywhere else:** absolute. It is unambiguous and greppable.
- Implicit relative imports (`import cleaning` inside a package, meaning the sibling) were Python 2 behaviour and **do not work** in Python 3. If you see it in old code, that is why it fails.

The error that confuses everyone:

```
ImportError: attempted relative import with no known parent package
```

It means you ran a file *inside* a package directly — `python textkit/stats.py`. Run as a script, `stats.py` has `__name__ == "__main__"` and no package context, so `.cleaning` refers to nothing. Two fixes:

```bash
python -m textkit.stats        # run it AS a module of the package (correct)
python -c "import textkit.stats"
```

`python -m package.module` is the general answer whenever a file lives inside a package and needs to be run.

> **Gotcha:** more than two dots is a design smell. `from ...core.utils import thing` says your package hierarchy is deeper than your ideas. Flatten it.

---

## 6. How Python finds a module: `sys.path`

When you write `import textkit`, Python looks, in order:

1. **`sys.modules`** — already imported? Use the cached object. Nothing else happens.
2. **built-in modules** — `sys`, `builtins`, and friends, compiled into the interpreter.
3. **each directory in `sys.path`, in order** — first match wins.

`sys.path` is a plain list of strings you can inspect and modify:

```python
import sys
for entry in sys.path:
    print(repr(entry))
```

```
''                                        <- the script's own directory (or cwd for the REPL)
'/usr/lib/python311.zip'
'/usr/lib/python3.11'
'/usr/lib/python3.11/lib-dynload'
'/home/you/project/.venv/lib/python3.11/site-packages'    <- where pip installs
```

The critical entry is the first one. When you run `python app.py`, `sys.path[0]` is the **directory containing `app.py`** — not your current directory. When you run `python -m app`, `sys.path[0]` is the current directory instead. That difference explains most "it imports here but not there" confusion.

Because it is first-match-wins and your own directory is first, a local file **shadows** anything later, including the standard library:

```
project/
    json.py            <- your file, first on sys.path
    app.py             <- import json  gets YOUR file, not the stdlib
```

Diagnosis tool: every module knows where it came from.

```python
import json
print(json.__file__)         # /usr/lib/python3.11/json/__init__.py  (or YOUR json.py)
```

When an import fails you get:

```
ModuleNotFoundError: No module named 'requests'
```

`ModuleNotFoundError` is a subclass of `ImportError`. The checklist, in order:

1. Is it a typo? (`reqeusts`, `dateutil` vs `python-dateutil`.)
2. Is it installed **in the interpreter you are running**? Check with `python -m pip list`, using the *same* `python` you run the app with.
3. Is your virtual environment active? (Section 8. This is the answer 80% of the time.)
4. Is the module in a directory that is on `sys.path` at all?
5. Is something local shadowing it, or is there a stray `__pycache__` from a renamed file?

You *can* append to `sys.path` at runtime, and you will see it in scripts:

```python
import sys
sys.path.insert(0, "/some/other/place")     # works; a last resort
```

Prefer running from the right directory, using `python -m`, or installing your package properly (`pip install -e .`). Editing `sys.path` is a workaround that hides the real layout problem, and it breaks for anyone who imports your module rather than running it.

> **Gotcha:** `__pycache__` holds compiled `.pyc` files. It is generated, never edited, and belongs in `.gitignore`. It is not the cause of your bug — except in the rare case where a `.py` file was deleted and a stale `.pyc` lingers; deleting the folder is a safe reset.

---

## 7. Circular imports and how to break them

A circular import is two modules that each need the other at import time.

```python
# orders.py
from customers import find_customer          # runs customers.py right now

def order_total(order):
    customer = find_customer(order["customer_id"])
    return order["amount"] * customer["discount"]
```

```python
# customers.py
from orders import order_total               # ...which imports orders.py again

def customer_value(customer):
    return sum(order_total(o) for o in customer["orders"])
```

`python orders.py` gives:

```
ImportError: cannot import name 'find_customer' from partially initialized module
'customers' (most likely due to a circular import)
```

Read that message literally: **partially initialized**. Python was halfway through executing `orders.py` when it started `customers.py`, which asked for a name from `orders.py` that had not been defined yet. There is no way to satisfy both at once, so it fails. Note the asymmetry that makes this maddening: whether it breaks can depend on which file you ran first, and on where in the file the import sits.

Four ways to break the cycle, best first:

**1. Extract the shared thing into a third module.** The cycle usually means both files depend on a concept that has no home yet.

```python
# pricing.py — depends on nothing
def apply_discount(amount, discount):
    return amount * discount

# orders.py     -> imports pricing
# customers.py  -> imports pricing and orders
```

**2. Reverse a dependency.** Often one direction is wrong: does `customers` really need to know how to total an order, or should the caller pass the total in? Dependencies should flow one way — usually from "outer" toward "inner".

**3. Import the module, not the name, and use it late.** `import customers` at the top only binds the module object; attribute lookup happens when the function runs, by which time both modules are fully loaded.

```python
# orders.py
import customers                            # not `from customers import find_customer`

def order_total(order):
    customer = customers.find_customer(order["customer_id"])   # resolved at CALL time
    return order["amount"] * customer["discount"]
```

**4. Import inside the function.** The last resort, and legitimate for genuinely rare paths or heavy optional dependencies.

```python
def order_total(order):
    from customers import find_customer      # runs on first call, not at import
    ...
```

It hides a dependency from anyone reading the top of the file and moves the failure from startup to runtime — so use it knowingly, with a comment saying why.

> **Gotcha:** type hints can create cycles all by themselves, purely for annotations. `from __future__ import annotations` (top of file) makes all annotations lazy strings, which removes that class of cycle entirely. That is one reason this course puts that line in every file.

---

## 8. Virtual environments

A virtual environment is a private folder holding its own copy of the Python interpreter's site-packages. It exists because global installs do not scale:

- Project A needs `requests` 2.25; project B needs 2.31. Globally, only one can win.
- `sudo pip install` can overwrite a package your operating system depends on.
- Six months later you have 90 globally installed packages and no idea which project needs which — so you cannot tell anyone how to run your code.

Creating and using one:

```bash
python -m venv .venv                 # create it (the folder name .venv is conventional)

source .venv/bin/activate            # activate: macOS / Linux
.venv\Scripts\activate               # activate: Windows PowerShell or cmd

python -m pip install pytest         # installs INTO .venv, no sudo, no global effect
deactivate                           # leave it
```

What "activation" actually does — no magic, just two edits to your shell:

1. It puts `.venv/bin` (or `.venv\Scripts`) at the front of `PATH`, so `python` and `pip` mean the ones inside the environment.
2. It sets `VIRTUAL_ENV` and usually decorates your prompt with `(.venv)`.

Proving where you are:

```bash
which python                # /home/you/project/.venv/bin/python
python -c "import sys; print(sys.prefix, sys.base_prefix, sep='\n')"
# different paths => you are inside a venv
```

Habits that avoid an entire genre of confusion:

- **Always `python -m pip install ...`**, not bare `pip`. It guarantees you install into the interpreter you just ran, which is the one thing bare `pip` cannot promise.
- One venv per project, in the project folder, named `.venv`.
- Add `.venv/` to `.gitignore`. Never commit an environment — it is large, machine-specific, and reproducible from `requirements.txt`.
- Not activating is fine if you are explicit: `.venv/bin/python app.py` works without activation.
- `python -m venv --clear .venv` rebuilds from scratch when something is broken beyond diagnosis.

(This course's `check.py doctor` reports whether a venv is active, and Day 11 is where that warning stops being a warning.)

---

## 9. `pip`, `requirements.txt`, and pinning

`pip` installs packages from PyPI, the Python Package Index.

```bash
python -m pip install pytest              # latest version
python -m pip install "pytest==8.2.0"     # exactly this version
python -m pip install "pytest>=8,<9"      # a range
python -m pip install --upgrade pytest    # upgrade
python -m pip uninstall pytest
python -m pip list                        # what is installed here
python -m pip show pytest                 # version, location, dependencies
```

A `requirements.txt` records what your project needs, one requirement per line:

```
# requirements.txt
pytest==8.2.0            # exact pin: reproducible
requests>=2.31,<3        # compatible range
rich                     # unpinned: whatever is latest today
```

```bash
python -m pip install -r requirements.txt
```

The line format is `name` then an optional comparison and version: `==` exact, `>=` at least, `<=` at most, `>` / `<` strict, `~=` "compatible release" (`~=1.4.2` means `>=1.4.2, <1.5.0`). Blank lines and `#` comments are ignored; lines beginning with `-` are options (such as `-r other.txt`), not packages.

### Pinning: the actual tradeoff

| | Pinned (`==2.31.0`) | Unpinned (`requests`) |
|---|---|---|
| Reproducible | Yes — same bytes for everyone, forever | No — depends on the day you install |
| Security fixes | You must act to get them | Arrive automatically |
| Breakage risk | Low and predictable | A new major version can break you overnight |
| Right for | applications, deployments, CI | libraries, where you must allow a range |

The professional convention: **applications pin exactly; libraries specify ranges.** An unpinned application is a time bomb — it worked in March and fails in June because a dependency released 3.0.

`pip freeze` writes the exact state of the current environment:

```bash
python -m pip freeze
```

```
iniconfig==2.0.0
packaging==24.1
pluggy==1.5.0
pytest==8.2.0
```

```bash
python -m pip freeze > requirements.txt      # snapshot everything
```

Note what `freeze` gives you: *every* installed package, including things you never asked for (`iniconfig`, `pluggy` are pytest's dependencies), with no comments and no distinction between what you need and what came along for the ride. That is fine for reproducing a deployment and poor as a description of intent. Hence the common two-file pattern:

```
requirements.in     # what I actually want:  pytest, requests
requirements.txt    # the frozen, complete, exact result
```

(Tools like `pip-tools` and `uv`, and packaging metadata in `pyproject.toml`, formalise this. Same idea: separate intent from the resolved snapshot.)

Reproducing an environment from scratch — the four commands that should be in every project's README:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

> **Gotcha:** the import name and the install name are often different. `pip install PyYAML` gives you `import yaml`; `pip install python-dateutil` gives `import dateutil`; `pip install beautifulsoup4` gives `import bs4`. `ModuleNotFoundError` after a successful install usually means you looked up the wrong one of the two names.

---

## 10. Hands-on: build a mini-package

Do this now, by hand, in this folder. It takes fifteen minutes and it is the part of today you will actually remember. A finished `textkit/` package sits in this folder already — build yours as `mytools/` first, then compare.

**Step 1.** Make the directory and an empty marker file:

```bash
cd course/week2/day11_modules_and_environments
mkdir mytools
touch mytools/__init__.py            # New-Item mytools/__init__.py  on Windows
```

**Step 2.** `mytools/cleaning.py`:

```python
"""Text tidying helpers."""

PUNCTUATION = ".,!?;:\"'"


def strip_punctuation(word: str) -> str:
    """Return `word` without leading or trailing punctuation."""
    return word.strip(PUNCTUATION)


def normalize(text: str) -> str:
    """Return `text` lowercased, with runs of whitespace collapsed to one space."""
    return " ".join(text.lower().split())
```

**Step 3.** `mytools/stats.py`, which imports its sibling *relatively*:

```python
"""Counting helpers built on top of cleaning."""

from .cleaning import normalize, strip_punctuation


def word_counts(text: str) -> dict[str, int]:
    """Return {word: count} for `text`, cleaned and lowercased."""
    counts: dict[str, int] = {}
    for raw_word in normalize(text).split():
        word = strip_punctuation(raw_word)
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts
```

**Step 4.** Try to run it directly, so you meet the error on purpose:

```bash
python mytools/stats.py
# ImportError: attempted relative import with no known parent package
```

Now run it the correct way, as a module of the package:

```bash
python -m mytools.stats             # no output, but no error either
```

**Step 5.** Give the package a public API in `mytools/__init__.py`:

```python
"""mytools — my first package."""

from .cleaning import normalize, strip_punctuation
from .stats import word_counts

__version__ = "0.1.0"
__all__ = ["normalize", "strip_punctuation", "word_counts"]
```

**Step 6.** Use it from a script in the same directory, `demo.py`:

```python
import mytools

print(mytools.__version__)
print(mytools.normalize("  Hello,   WORLD  "))
print(mytools.word_counts("The cat, the DOG. The cat!"))
```

```bash
python demo.py
# 0.1.0
# hello, world
# {'the': 3, 'cat': 2, 'dog': 1}
```

**Step 7.** Prove three claims from today, at the interactive prompt:

```bash
python -c "import mytools; print(mytools.__file__)"                 # where it came from
python -c "import sys; print(sys.path[0])"                          # first search location
python -c "import mytools; print(mytools.stats)"                    # AttributeError? why?
```

The third one raises `AttributeError` unless `__init__.py` imported the submodule — go back and read section 4's gotcha, then fix it by adding `from . import stats`.

**Step 8.** Add an entry point to `mytools/stats.py` and see `__name__` do its job:

```python
def main() -> int:
    print(word_counts("the cat the dog"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```bash
python -m mytools.stats      # prints the counts
python -c "import mytools.stats"   # prints nothing: main() did not run
```

**Step 9.** Delete `mytools/` and `demo.py` when you are done, or keep them — they are yours, and nothing grades them. Do delete any `__pycache__` folders you created; they are noise.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| A file named after a stdlib module | `AttributeError: module 'json' has no attribute 'loads'` | Rename your `json.py`; delete `__pycache__` |
| Work at a module's top level | Slow, surprising side effects on import | Put it in `main()` behind `if __name__ == "__main__":` |
| Missing `if __name__` guard | Importing your module runs its script | Add the guard |
| `python textkit/stats.py` | `ImportError: attempted relative import with no known parent package` | `python -m textkit.stats` |
| Expecting `import pkg` to give submodules | `AttributeError: module 'pkg' has no attribute 'sub'` | `import pkg.sub`, or import it in `__init__.py` |
| `from module import *` | Unknown names, silent collisions | Import the module, or specific names |
| Circular import | `ImportError: cannot import name X from partially initialized module` | Extract a third module; or `import mod` and use `mod.X` late |
| `pip install` outside a venv | Global clutter, version conflicts, permission errors | `python -m venv .venv`, activate, then install |
| Bare `pip` with several Pythons | Installs somewhere you are not running | `python -m pip install ...` |
| Unpinned app dependencies | Worked in March, broken in June | Pin exactly in `requirements.txt` |
| Committing `.venv/` | Huge, machine-specific repository | `.gitignore` it; commit `requirements.txt` |
| Install name vs import name | `ModuleNotFoundError: No module named 'yaml'` after installing PyYAML | Check the package's documented import name |

---

## Mental model

**Imports: a name-resolution search.**

```
   import textkit
        |
        v
   1. sys.modules      already imported? -> hand back the cached object, stop.
        |
        v
   2. built-ins        compiled into python itself (sys, builtins)
        |
        v
   3. sys.path[0]      the directory of the script you ran  <- YOUR files, first
      sys.path[1..]    stdlib directories
      sys.path[-1]     .../site-packages   <- where pip puts things
        |
        v
   first match wins    -> run the file top to bottom, ONCE
                       -> cache it in sys.modules
                       -> bind the module object to the name
```

**Environments: a workshop per project.**

```
   global python      the building's shared toolbox. Touch it and every
                      project changes. (This is why `sudo pip` is a smell.)

   .venv/             your project's own bench, with its own copy of the
                      tools. Activation = putting this bench's drawer at the
                      front of PATH so `python` means THIS python.

   requirements.txt   the parts list. Pinned = "these exact parts", which is
                      what makes a stranger's build identical to yours.

   pip freeze         a photograph of the whole bench, including tools that
                      came bundled with other tools.
```

One sentence each: *a module is a file that runs once and becomes an object*; *a package is a directory with an `__init__.py` that curates what the outside sees*; *a virtual environment is a per-project bench so projects cannot break each other*.

---

## Practice

1. Run the demo. It uses the `textkit/` package that ships in this folder, and it builds a throwaway package inside `tmp/` to show `sys.path` and circular imports for real, then deletes it:

   ```bash
   python course/week2/day11_modules_and_environments/examples.py
   ```

2. Do section 10 by hand. All nine steps, including the two deliberate errors. Reading about `ImportError: attempted relative import with no known parent package` is not the same as causing it.

3. Then do the environment half for real, in a scratch directory outside this repository:

   ```bash
   mkdir /tmp/venv-practice && cd /tmp/venv-practice
   python -m venv .venv
   source .venv/bin/activate          # .venv\Scripts\activate on Windows
   which python                       # confirm it is the one inside .venv
   python -m pip list                 # nearly empty — this is a clean room
   python -m pip install pytest
   python -m pip freeze > requirements.txt
   cat requirements.txt               # note the dependencies you never asked for
   deactivate
   ```

4. Open `exercises.py`. Today's exercises are the tooling you would write to *reason about* imports and requirements — no file I/O, all pure functions. Exercise 8 is the hard one.

5. Grade from the course root:

   ```bash
   python check.py day11
   python check.py day11 -v
   ```

---

## Recall check

1. What exactly happens, in order, when Python executes `import textkit` for the first time?
2. What is the difference between `import textkit.stats` and `from textkit.stats import word_counts`, in terms of the names you end up with?
3. What is `__name__` set to for the file you ran, and for a file you imported? What does that let you do?
4. Give two real jobs for `__init__.py`, and one thing it should not contain.
5. Inside `pkg.sub.mod`, what does `from ..util import x` resolve to, and how do you count the dots?
6. Your program imports the wrong `json`. How do you confirm that in one line, and what is the fix?
7. You get `ImportError: cannot import name 'find_customer' from partially initialized module 'customers'`. What is happening, and what are two ways to fix it properly?
8. Why is `python -m pip install X` preferred over `pip install X`, and why in a venv at all?
9. When should a `requirements.txt` pin exact versions, and when should it use ranges?

<details>
<summary>Answers</summary>

1. Python checks `sys.modules` for a cached module and returns it if present; otherwise it searches built-ins then each `sys.path` entry in order, takes the first match, executes that file top to bottom exactly once, caches the resulting module object in `sys.modules`, and binds it to the local name `textkit`.
2. `import textkit.stats` binds the name `textkit` in your namespace (and you reach the function as `textkit.stats.word_counts`). `from textkit.stats import word_counts` binds only `word_counts`, with no record in your file of which module it came from.
3. `"__main__"` for the file you ran; the module's dotted name (e.g. `"textkit.stats"`) when imported. It lets one file be both a runnable program and an importable library: put the script behaviour behind `if __name__ == "__main__":`.
4. Marking the directory as a regular package, and curating the public API by re-exporting names (plus metadata like `__version__` and `__all__`). It should not contain real work — expensive code there runs on every import of anything in the package.
5. `pkg.util`. One dot means the module's own package (`pkg.sub`); each additional dot goes one level up, so two dots means `pkg`, and the name after the dots is looked up there.
6. `python -c "import json; print(json.__file__)"` — if it prints a path inside your project you have a shadowing file. Rename your `json.py` (and delete stale `__pycache__`).
7. Two modules import each other at import time, so one of them is asked for a name while it is still half-executed. Proper fixes: extract the shared code into a third module that neither depends on, or reverse the wrong dependency direction. A workable third option is `import customers` plus late attribute access (`customers.find_customer(...)`) inside the function.
8. `python -m pip` installs into the interpreter you just named, removing all ambiguity when several Pythons exist; bare `pip` may belong to a different installation. The venv gives the project its own site-packages so version conflicts, global clutter, and permission problems disappear.
9. Applications and deployments pin exactly (`==`) so every machine and every CI run is identical. Libraries specify ranges (`>=2.31,<3`) so they can coexist with whatever else the consuming application installs.

</details>
