# Day 09 — Errors and Debugging

> **Time:** ~4 hours  |  **Prerequisites:** Day 08

## What you'll be able to do after today
- Read a multi-frame traceback bottom-up and name the exact line, function, and cause of a failure.
- Choose the right built-in exception type for a failure, and explain what actually triggers `ValueError`, `TypeError`, `KeyError`, `IndexError`, `AttributeError`, `ZeroDivisionError`, `FileNotFoundError`, and `StopIteration`.
- Write `try/except/else/finally` blocks that catch *specific* exceptions, and explain why `except:` and `except Exception:` are usually bugs.
- `raise` your own exceptions, re-raise while preserving the original cause with `raise ... from`, and define a custom exception class.
- Use `assert` for internal invariants and say why it must never validate user input.
- Choose between EAFP ("ask forgiveness") and LBYL ("look before you leap") deliberately.
- Debug an unfamiliar failure with a repeatable method: reproduce, isolate, bisect, print, then `breakpoint()`.

## Why this matters

Your programs will fail. Files go missing, users type "n/a" in a number column, an API returns `null` where you expected a list. The difference between a beginner and a professional is not that the professional's code never breaks; it is that the professional's code breaks *loudly, in the right place, with a message that says what to do*, and that they can find the cause in minutes instead of hours.

There is also a career-shaped reason. Most of your working life is spent reading failures in code you did not write. A traceback is the highest-information-density artifact in software: it tells you the call path, the line, the values, and the category of the problem. If you can read one fluently you are already more useful than someone who scrolls past it and starts guessing.

---

## 1. Exceptions are a control-flow mechanism, not a disaster

When Python cannot continue, it *raises an exception*: it stops the current line, abandons the current function, and hands an exception object up to whoever called it. If nobody catches it, it reaches the top, Python prints a traceback, and the program exits with a non-zero status.

```python
value = int("12")     # fine
value = int("n/a")    # ValueError: invalid literal for int() with base 10: 'n/a'
print("never reached")
```

Three separate ideas, and beginners blur them:

| Thing | What it is |
|---|---|
| An **exception object** | A value, like `ValueError("bad input")`. It has a type and a message. |
| **Raising** | Throwing it upward: `raise ValueError("bad input")`. |
| **Handling** | Catching it on the way up and deciding what to do: `except ValueError:`. |

Exceptions travel *up the call stack*. If `main` calls `total_revenue` which calls `line_revenue`, and `line_revenue` raises, then Python leaves `line_revenue`, leaves `total_revenue`, leaves `main`, and prints. Any of those three could have caught it. That is the power: the code that *detects* a problem does not have to be the code that *decides* what to do about it.

```python
def parse_units(text):
    return int(text)                 # detects: raises ValueError on junk

def load_row(row):
    try:
        return parse_units(row["units"])
    except ValueError:
        return 0                     # decides: junk counts as zero here

print(load_row({"units": "7"}))      # 7
print(load_row({"units": "n/a"}))    # 0
```

This is not "error handling" bolted onto the side of a program. It is a control-flow tool, as ordinary as `if`. Python's own iteration protocol is built on an exception (`StopIteration`), which is how normal `for` loops know when to stop.

> **Gotcha:** an uncaught exception is not a bug in Python and not a punishment. It is the interpreter telling you something true. The wrong reaction is to wrap everything in `try/except` to make the message go away; the message is the most valuable thing you have.

---

## 2. Reading a traceback (bottom-up, line by line)

Here is a real failure from a three-function program:

```python
# report.py
SALES = [
    {"region": "north", "units": "12", "price": "9.99"},
    {"region": "south", "units": "7", "price": "12.50"},
    {"region": "east", "units": "n/a", "price": "3.00"},
]


def line_revenue(row):
    units = int(row["units"])
    price = float(row["price"])
    return units * price


def total_revenue(rows):
    total = 0.0
    for row in rows:
        total += line_revenue(row)
    return total


def main():
    print(f"total: {total_revenue(SALES):.2f}")


main()
```

Running `python report.py` prints:

```
Traceback (most recent call last):
  File "/home/you/reports/report.py", line 27, in <module>
    main()
  File "/home/you/reports/report.py", line 24, in main
    print(f"total: {total_revenue(SALES):.2f}")
                    ^^^^^^^^^^^^^^^^^^^^
  File "/home/you/reports/report.py", line 19, in total_revenue
    total += line_revenue(row)
             ^^^^^^^^^^^^^^^^^
  File "/home/you/reports/report.py", line 11, in line_revenue
    units = int(row["units"])
            ^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'n/a'
```

Now annotated, in the order you should read it:

```
LAST line  -> ValueError: invalid literal for int() with base 10: 'n/a'
             (1) READ THIS FIRST. Type = ValueError (a value of the right type
                 but wrong content). Message names the offending value: 'n/a'.

4th frame  ->   File "/home/you/reports/report.py", line 11, in line_revenue
                  units = int(row["units"])
                          ^^^^^^^^^^^^^^^^^
             (2) READ THIS SECOND. The innermost frame: file, line number,
                 function name, the source line, and carets under the exact
                 sub-expression that blew up. This is where you set a
                 breakpoint. 95% of debugging ends here.

3rd frame  ->   File "/home/you/reports/report.py", line 19, in total_revenue
                  total += line_revenue(row)
             (3) Who called the broken function, and with what. Read upward
                 only if the innermost frame did not explain enough — here it
                 tells you `row` came from a loop, so you want to know WHICH row.

2nd frame  ->   File "/home/you/reports/report.py", line 24, in main
                  print(f"total: {total_revenue(SALES):.2f}")
             (4) Higher still: the data came from SALES.

1st frame  ->   File "/home/you/reports/report.py", line 27, in <module>
                  main()
             (5) `<module>` means top level of the file, not inside any
                 function. The bottom of the ladder, i.e. the start of the call.

Header     -> Traceback (most recent call last)
             (6) The header tells you the ordering convention: OLDEST call at
                 the top, the actual crash site at the bottom. That is why you
                 read from the bottom.
```

Reading procedure, memorise it:

1. **Bottom line:** what type of error, and what does the message say?
2. **Frame just above it:** which file, which line, which function — that is the crash site.
3. **Walk up only as needed** to find where the bad *data* came from.
4. Ignore frames inside libraries you did not write, except to learn which of *your* frames called into them. Your frames are the ones with your file paths.

Two extra shapes you will meet:

**Chained exceptions.** `During handling of the above exception, another exception occurred` means your `except` block itself broke — the *second* traceback is your bug. `The above exception was the direct cause of the following exception` means someone deliberately re-raised with `raise ... from err`, and both halves are relevant.

**SyntaxError.** No frames, because nothing ran. Python points at the token it choked on; the real mistake is often on the *previous* line (an unclosed bracket).

> **Gotcha:** `line 19` is where the failing call *was made*, not necessarily where the wrong value was created. Tracebacks localise the symptom. Finding the origin is section 9's job.

---

## 3. The built-in exceptions you will actually meet

| Exception | What actually causes it | Typical trigger |
|---|---|---|
| `ValueError` | Right type, unusable value | `int("n/a")`, `math.sqrt(-1)` |
| `TypeError` | Wrong type entirely, or wrong arguments | `"a" + 1`, `len(5)`, `f()` missing an argument |
| `KeyError` | Dict key absent | `{"a": 1}["b"]` |
| `IndexError` | Sequence index out of range | `[1, 2][5]` |
| `AttributeError` | Object has no such attribute/method | `"abc".push("d")`, `None.strip()` |
| `ZeroDivisionError` | Division or modulo by zero | `1 / 0`, `7 % 0` |
| `FileNotFoundError` | Path does not exist (a subclass of `OSError`) | `open("nope.txt")` |
| `PermissionError` | Path exists, you may not touch it | writing to a read-only file |
| `NameError` | Name never defined in any visible scope | typo: `pritn("hi")` |
| `UnboundLocalError` | Local read before assignment (subclass of `NameError`) | Day 8's `count = count + 1` trap |
| `ImportError` / `ModuleNotFoundError` | Import failed / module not installed | `import reqeusts` |
| `StopIteration` | An iterator is exhausted | `next(iter([]))` |
| `KeyboardInterrupt` | User pressed Ctrl-C | any long loop |
| `RecursionError` | Too many nested calls | a function that calls itself forever |

```python
print("a" + 1)          # TypeError: can only concatenate str (not "int") to str
print(len(5))           # TypeError: object of type 'int' has no len()
print(int("n/a"))       # ValueError: invalid literal for int() with base 10: 'n/a'
print({"a": 1}["b"])    # KeyError: 'b'
print([1, 2][5])        # IndexError: list index out of range
print(None.strip())     # AttributeError: 'NoneType' object has no attribute 'strip'
```

`ValueError` vs `TypeError` is the distinction people fumble. Ask: *could any value of this type work?* `int("12")` works, so `int("n/a")` is a `ValueError`. `len(5)` can never work for any int, so it is a `TypeError`.

`AttributeError: 'NoneType' object has no attribute ...` deserves special mention: it almost always means a function you called returned `None` — usually a function that mutates in place (`sort()`, `append()`) whose return value you stored by mistake.

The exceptions form a hierarchy. The parts that matter:

```
BaseException
 +-- SystemExit               (sys.exit)          <- do not catch
 +-- KeyboardInterrupt        (Ctrl-C)            <- do not catch
 +-- Exception                                    <- everything you care about
      +-- ArithmeticError -> ZeroDivisionError
      +-- LookupError     -> KeyError, IndexError
      +-- OSError         -> FileNotFoundError, PermissionError, IsADirectoryError
      +-- ValueError      -> UnicodeDecodeError
      +-- TypeError
      +-- AttributeError
      +-- NameError       -> UnboundLocalError
      +-- StopIteration
```

Consequences you can use: `except LookupError` catches both `KeyError` and `IndexError`. `except OSError` catches every filesystem problem. `except Exception` catches everything *except* the two you must never swallow — `KeyboardInterrupt` and `SystemExit` — which is exactly why `except Exception` is less bad than a bare `except:`.

---

## 4. `try` / `except` / `else` / `finally`

```python
def read_units(row):
    try:
        units = int(row["units"])        # code that might fail
    except KeyError:
        print("no 'units' column")       # runs only for a missing key
        return 0
    except ValueError as error:          # `as error` binds the exception object
        print(f"bad units value: {error}")
        return 0
    else:
        print("parsed cleanly")          # runs only if try finished with NO exception
        return units
    finally:
        print("done with this row")      # ALWAYS runs, exception or not, return or not
```

```python
print(read_units({"units": "7"}))
# parsed cleanly
# done with this row
# 7

print(read_units({"units": "n/a"}))
# bad units value: invalid literal for int() with base 10: 'n/a'
# done with this row
# 0
```

Precise rules:

- **`try`** holds the risky code. Keep it as *small* as possible — one or two lines. A ten-line `try` catches failures you never thought about.
- **`except X:`** runs if the raised exception is an instance of `X` (or a subclass). Order matters: the first match wins, so list specific types before general ones.
- **`except (KeyError, IndexError):`** catches several types with one block. A *tuple*, in parentheses.
- **`else:`** runs only when `try` completed without raising. Use it for "the rest of the happy path" so that code is not itself protected by the `except`.
- **`finally:`** always runs — after a normal exit, after a handled exception, after an unhandled one on its way up, and even after a `return`. It is for cleanup: closing files, releasing locks, restoring state.

Why `else` exists, concretely:

```python
# WRONG: the ValueError handler also covers use_units(), hiding bugs in it
try:
    units = int(row["units"])
    use_units(units)              # if THIS raises ValueError you get a wrong message
except ValueError:
    print("bad units")

# RIGHT: the try covers only the risky call
try:
    units = int(row["units"])
except ValueError:
    print("bad units")
else:
    use_units(units)              # failures here are not disguised
```

> **Gotcha:** a `return` in `finally` overrides any earlier `return` or in-flight exception — it silently swallows failures. Never `return` from `finally`.

---

## 5. Catch specific exceptions; bare `except:` is a bug

```python
# NEVER
try:
    total = int(row["units"]) * float(row["price"])
except:                            # catches literally everything
    total = 0
```

What you just did:

- You caught `KeyboardInterrupt`, so Ctrl-C no longer stops your program.
- You caught `SystemExit`, so `sys.exit()` no longer works.
- You caught `NameError`, so a typo — `rwo["units"]` — quietly produces `0` instead of shouting. That bug can live for a year.
- You threw away the exception object, so nobody will ever know what happened.

The rule: **catch the narrowest exception you know how to handle, and only where you can actually do something about it.**

```python
try:
    total = int(row["units"]) * float(row["price"])
except (KeyError, ValueError) as error:
    print(f"skipping row {row!r}: {error}")
    total = 0.0
```

Legitimate broad catches exist, and they always *report*:

```python
# A long-running worker that must not die because one job was bad.
try:
    process(job)
except Exception as error:                       # never bare `except:`
    log_failure(job, error)                      # record it
    # and keep going
```

Two more anti-patterns to recognise on sight:

```python
except ValueError:
    pass            # "silent swallow" — the most expensive four letters in software

except ValueError:
    print("error")  # a message with no information: which value? which row? which file?
```

If you truly want to ignore something, say so loudly with a comment explaining why it is safe.

> **Gotcha:** `except Exception as e: print(e)` prints the message but throws away the traceback, so you lose the line number. When logging, prefer `traceback.print_exc()` (or `logging.exception(...)`, Day 17) so the frames survive.

---

## 6. Raising your own exceptions

Validate at the boundary; refuse to continue with data you know is wrong.

```python
def set_age(age):
    if not isinstance(age, int):
        raise TypeError(f"age must be an int, got {type(age).__name__}")
    if age < 0:
        raise ValueError(f"age must not be negative, got {age}")
    if age > 130:
        raise ValueError(f"age {age} is implausible")
    return age

set_age(-4)     # ValueError: age must not be negative, got -4
```

Message rules that separate juniors from seniors:

- Include the **offending value** (`got -4`), not just the rule.
- Say what was **expected**.
- No blame, no "Error:" prefix, no exclamation marks. The traceback already says it is an error.
- Make it greppable: a distinctive phrase means someone can find the raise site by searching.

### 6.1 Re-raising

Sometimes you want to note the failure and let it continue upward. A bare `raise` re-raises the current exception with its original traceback intact:

```python
def load(path):
    try:
        return read_config(path)
    except FileNotFoundError:
        print(f"config missing at {path}; cannot continue")
        raise                       # same exception, same traceback, still fatal
```

`raise` with no argument only works inside an `except` block. Do not write `raise error` — that works, but it rewrites the traceback to start here and you lose information.

### 6.2 Translating with `raise ... from`

Often you want to convert a low-level failure into a meaningful one for your caller, while keeping the original for the debugger:

```python
class ConfigError(Exception):
    """Raised when a configuration file cannot be used."""


def load_port(text):
    try:
        return int(text)
    except ValueError as error:
        raise ConfigError(f"port must be a whole number, got {text!r}") from error
```

The traceback then shows both, joined by "The above exception was the direct cause of the following exception". The original is available programmatically as `error.__cause__`:

```python
try:
    load_port("http")
except ConfigError as error:
    print(type(error).__name__)              # ConfigError
    print(error)                             # port must be a whole number, got 'http'
    print(type(error.__cause__).__name__)    # ValueError  <- the original
```

Use `from None` to deliberately hide an irrelevant internal cause. Silence is a choice you should have to type.

### 6.3 Custom exception classes

> Forward touch: `class` is Day 12's topic. Today you need only this three-line shape. Day 12 explains what `class`, inheritance, and `__init__` really mean — you are borrowing the syntax, not learning it yet.

```python
class ValidationError(Exception):
    """Raised when input data fails our rules."""
```

That is a complete, useful exception class: a name, a base of `Exception`, and a docstring as the body. Why bother instead of `ValueError`?

- Callers can catch **your** failure precisely: `except ValidationError:` will not accidentally swallow a `ValueError` from unrelated code.
- The type name is documentation in the traceback: `ValidationError` says "your data" while `ValueError` says "something, somewhere".
- You can group related failures under one parent:

```python
class AppError(Exception):
    """Base class for every error this app raises on purpose."""

class ValidationError(AppError):
    """Bad input data."""

class StorageError(AppError):
    """Could not read or write our data file."""
```

Now `except AppError:` catches all of your deliberate failures and nothing else. That is the payoff.

You can also carry data:

```python
class ValidationError(Exception):
    def __init__(self, field, value):
        super().__init__(f"invalid {field}: {value!r}")   # the human message
        self.field = field                                # machine-readable extras
        self.value = value
```

Naming convention: end the name in `Error`. Inherit from `Exception` (not `BaseException`).

---

## 7. `assert` and its correct role

`assert condition, message` raises `AssertionError` when the condition is falsy.

```python
def apply_split(total, shares):
    assert shares > 0, f"shares must be positive, got {shares}"    # internal invariant
    return total / shares
```

The one fact that decides how you use it: **assertions can be turned off.** Running `python -O script.py` removes every `assert` from the compiled code. Some deployment setups do exactly that.

Therefore:

| Use `assert` for | Use `raise` for |
|---|---|
| "This can never happen" sanity checks | Anything a user or file can cause |
| Internal invariants between your own functions | Validating input at a boundary |
| Documenting an assumption while developing | Anything you would write a test for |
| Test suites (pytest is built on `assert`) | Library code others depend on |

```python
# WRONG — with -O this check vanishes and a negative price sails through
assert price > 0, "price must be positive"

# RIGHT
if price <= 0:
    raise ValueError(f"price must be positive, got {price}")
```

> **Gotcha:** `assert (condition, message)` — with parentheses — asserts a *tuple*, which is always truthy, so it never fails. Ruff and other linters flag this. No parentheses.

---

## 8. EAFP vs LBYL

Two philosophies for dealing with things that might not work.

**LBYL** — Look Before You Leap. Check first.

```python
if "units" in row and row["units"].isdigit():
    units = int(row["units"])
else:
    units = 0
```

**EAFP** — Easier to Ask Forgiveness than Permission. Try it, handle the failure.

```python
try:
    units = int(row["units"])
except (KeyError, ValueError):
    units = 0
```

Python idiom leans EAFP, for three concrete reasons:

1. **Completeness.** The LBYL version above still breaks on `"12.5"` (`isdigit()` is False) and `" 7"` and negative numbers. Your checks are a guess at what `int()` rejects; `except ValueError` is exactly what `int()` rejects.
2. **Race conditions.** `if path.exists(): open(path)` can fail anyway — the file may vanish between the two lines. There is no gap in the EAFP version.
3. **Speed in the common case.** A `try` block costs almost nothing when nothing raises; a check costs on every single call.

When LBYL is right:

- The check is cheap, total, and obvious: `if not items: return 0.0`.
- Failure is *expected and frequent* — exceptions are slow when they fire constantly.
- The operation has side effects you cannot undo: check *before* deleting a thousand rows.
- The dict-with-default case, where the stdlib gives you a cleaner tool than either: `row.get("units", "0")`.

```python
# best of both for dicts
units_text = row.get("units", "0")
try:
    units = int(units_text)
except ValueError:
    units = 0
```

> **Gotcha:** EAFP is not "wrap everything in try". It is "let the operation define what failure means, and catch exactly that".

---

## 9. A debugging methodology

Debugging is not staring at code hoping to spot it. It is a search, and you should run it the same way every time.

### 9.1 Reproduce

You cannot fix what you cannot see. Get the failure to happen **on demand**, with the shortest possible command and the smallest possible input. Write it down:

```
python report.py data/march.csv   ->  ValueError on the 3rd row, every time
```

If it only happens sometimes, find what varies (input order, a date, a missing file, an empty list). Intermittent bugs are almost always about state or ordering.

### 9.2 Read the traceback properly

Section 2. Bottom line, then innermost frame. Do not skip this to go look at code you *suspect*: suspicion is how you lose two hours.

### 9.3 Isolate

Shrink the input until the failure disappears, then put back the last thing you removed. Three rows instead of three million. One field instead of forty. Then call the innermost function directly with that value:

```python
>>> line_revenue({"region": "east", "units": "n/a", "price": "3.00"})
ValueError: invalid literal for int() with base 10: 'n/a'
```

Now you have a one-line reproduction. This is also exactly the moment to turn it into a test (Day 18) so it can never come back.

### 9.4 Bisect

When you have no idea where the problem is, halve the search space repeatedly. Ten halvings covers a thousand lines.

- **In the data:** does it fail on the first half of the rows? The second?
- **In the code:** comment out the second half of a pipeline. Still broken? The cause is upstream.
- **In time:** if it worked last week, `git log` and check out a commit from then. (`git bisect` automates this; you will use it eventually.)

Each step must *answer a question*. "I'll change this and see" is not a step.

### 9.5 Print-debug (properly)

`print` is a legitimate debugger. Beginners use it badly: unlabelled values in a wall of output.

```python
def line_revenue(row):
    print(f"[line_revenue] row={row!r}")                   # label the site
    units = int(row["units"])
    print(f"[line_revenue] units={units!r} type={type(units).__name__}")
    ...
```

Rules that make printing effective:

- **Label** every print with the function name. Ten anonymous numbers tell you nothing.
- Use **`!r`** (`repr`) not plain interpolation: `'7'` versus `7` is the whole bug, and `f"{x}"` hides it.
- Print the **type** when you doubt it: `type(x).__name__`.
- Print **inside** loops with the index: `print(f"[row {index}] {row!r}")`.
- Confirm assumptions you would swear are true. The bug is always in one of those.
- Delete them when you are done. (Day 17's `logging` is the grown-up version.)

`vars(obj)` and `dir(obj)` are useful cousins for "what is even in this thing?"

### 9.6 `breakpoint()` and `pdb`

When a value is wrong and printing is turning into an archaeology dig, stop the program and look around. Put this line where you want to pause:

```python
def line_revenue(row):
    breakpoint()                # built in since Python 3.7; drops you into pdb
    units = int(row["units"])
```

Run the program normally. You get a `(Pdb)` prompt at that line, inside that frame, with every local variable live.

The commands worth memorising (six of them):

| Command | Short | Does |
|---|---|---|
| `list` | `l` | show source around the current line |
| `args` | `a` | print the current function's arguments |
| `print expr` | `p` | evaluate an expression: `p row`, `p type(row["units"])` |
| `next` | `n` | run the current line, stay in this function |
| `step` | `s` | run the current line, stepping *into* calls |
| `continue` | `c` | resume until the next breakpoint or the end |

Also: `where` (`w`) prints the stack, `up`/`down` (`u`/`d`) move between frames, `q` quits. Any Python expression typed at the prompt is evaluated in the current frame, so you can poke at data freely.

Two high-value variants:

```bash
python -m pdb -c continue report.py     # run, and drop into pdb AT THE CRASH SITE
```

That is post-mortem debugging: the program runs full speed, and when it dies you are standing in the failing frame with all its locals. No code edits needed.

```python
import pdb; pdb.post_mortem()           # inside an except block, same idea
```

### 9.7 The checklist

```
1. Reproduce it on demand. One command, smallest input.
2. Read the traceback: bottom line, then innermost frame.
3. Form ONE hypothesis you can test in under a minute.
4. Test it (print / pdb / direct call). Write down the answer.
5. Wrong hypothesis? Bisect: halve the code or the data.
6. Found it? Write a failing test FIRST, then fix.
7. Ask: where should this have been caught? Add validation there.
```

Step 7 is what turns a fix into an improvement. If a bad row reached your maths function, the fix is not only "handle 'n/a'" — it is "validate rows at the point where they enter the program".

> **Gotcha:** if you have been stuck for 30 minutes, your model of the code is wrong somewhere you are not questioning. Verify something you are *certain* of: that the function is being called at all, that the file being read is the file you think, that the code you edited is the code that ran.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Reading the traceback top-down | Blaming `main()` for a bug in `line_revenue` | Read the last line, then the frame above it |
| `except:` bare | Ctrl-C stops working; typos silently return defaults | Catch specific types, or `except Exception as error:` and report |
| `except ValueError: pass` | Wrong results, no message, no clue | Handle it or let it propagate; never swallow silently |
| Huge `try` block | A handler fires for a line you never suspected | One or two risky lines per `try`; move the rest to `else` |
| `raise error` instead of bare `raise` | Traceback starts at the re-raise, origin lost | Bare `raise` inside `except`, or `raise New(...) from error` |
| `assert` for user input | Validation disappears under `python -O` | `if bad: raise ValueError(...)` |
| `assert (cond, "msg")` | Never fails, ever | Drop the parentheses |
| Catching `Exception` around one line | Hides `NameError`/`TypeError` from your own typos | Name the exception you expect |
| Error message without the value | "invalid input" — which input? | Interpolate the culprit with `!r` |
| `return` inside `finally` | Exceptions vanish; wrong value returned | Never return from `finally` |
| Chasing a `NoneType` AttributeError upward | `'NoneType' object has no attribute 'x'` | Find the function that returned `None` — often `list.sort()` or a missing `return` |

---

## Mental model

An exception is an **emergency stairwell** in the call stack.

```
   main()                <- 4th floor: could catch, chooses not to
     |
   total_revenue()       <- 3rd floor: could catch, chooses not to
     |
   line_revenue()        <- 2nd floor: FIRE STARTS HERE (raise)
     |
   int("n/a")            <- ground: the actual failing operation

   The exception runs UP the stairwell looking for the first floor with a
   matching `except` door. If none opens, it exits the building and Python
   prints the whole route it took -- newest floor last. That printout is the
   traceback, which is why you read it from the bottom.

   `finally` blocks are the door-closers: they run as the exception rushes
   past, whether or not anyone catches it.
```

And a debugging model: you are doing **binary search on a wrong assumption**. Every print, every breakpoint, every commented-out block is one bit of information that halves the space. Guessing gains zero bits.

---

## Practice

1. Run the demo, slowly, comparing each printed line to the code that produced it:

   ```bash
   python course/week2/day09_errors_and_debugging/examples.py
   ```

2. Then do this by hand, because reading about pdb teaches nothing:

   ```bash
   cd course/week2/day09_errors_and_debugging
   python -m pdb -c continue examples.py     # then type: where, args, p row, q
   ```

3. Open `exercises.py`. Implement top to bottom. Exercises 8 and 9 are the real work.

4. Grade from the course root:

   ```bash
   python check.py day09
   python check.py day09 -v
   ```

5. Deliberate practice, 15 minutes: break something on purpose. Take your Day 7 or Day 8 code, introduce a typo in a variable name, an off-by-one index, and a missing dict key — one at a time. Predict the exception type *before* you run it. Being right is the skill.

---

## Recall check

1. In what order do you read a traceback, and what does the header line tell you about that order?
2. What is the difference between `ValueError` and `TypeError`? Give an example of each.
3. When does `else` run in a `try` statement, and why would you use it instead of putting the code at the end of `try`?
4. Name three specific things that go wrong when you write a bare `except:`.
5. What is the difference between `raise`, `raise error`, and `raise NewError(...) from error`?
6. Why must you never use `assert` to validate user input?
7. Give one situation where LBYL beats EAFP, and one where EAFP beats LBYL.
8. You get `AttributeError: 'NoneType' object has no attribute 'strip'`. What is the most likely cause, and where do you look?

<details>
<summary>Answers</summary>

1. Bottom-up: last line first (exception type and message), then the frame immediately above it (the innermost call — file, line, function), then walk upward only as needed to find where the bad data came from. The header says "most recent call last", which is the convention that makes bottom-up correct.
2. `ValueError`: the type is right but the value is unusable — `int("n/a")`. `TypeError`: the type itself is wrong for the operation — `len(5)` or `"a" + 1`. Test: could *some* value of that type work?
3. `else` runs only when the `try` block completed with no exception. Putting the happy-path continuation there means your `except` handlers cannot accidentally catch failures raised by that continuation, which would give a misleading error message.
4. It catches `KeyboardInterrupt` (Ctrl-C stops working) and `SystemExit` (`sys.exit()` stops working); it hides your own typos such as `NameError`/`AttributeError`; and it discards the exception object so nothing can be logged or diagnosed.
5. Bare `raise` (only inside `except`) re-raises the current exception with its original traceback. `raise error` re-raises the object but restarts the traceback at that line, losing the path. `raise NewError(...) from error` raises a new, more meaningful exception while recording the original as `__cause__`, and the printed traceback shows both.
6. Assertions are removed when Python runs with `-O`, so the validation can silently disappear in production. Input validation must be an explicit `if ...: raise ValueError(...)`.
7. LBYL wins when the operation is destructive or expensive and you must check first (e.g. verifying a path before deleting), or when the guard is cheap and total (`if not items: return 0.0`). EAFP wins for parsing and file access, where the operation itself defines failure precisely (`int()`, `open()`) and where a check-then-act gap can race.
8. Some expression evaluated to `None` when you expected a string — most often a function with a missing `return`, or the return value of an in-place method such as `list.sort()` or `list.append()`. Look at the innermost frame, find which sub-expression produced the `None` (the carets help), then look at what produced *that* value.

</details>
