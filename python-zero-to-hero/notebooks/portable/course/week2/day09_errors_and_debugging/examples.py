"""Day 09 — Errors and debugging: runnable demonstrations.

Run me from the course root:

    python course/week2/day09_errors_and_debugging/examples.py

Every failure below is deliberate and caught, so the script exits cleanly (0).
Section numbers match LESSON.md.

Worth doing by hand afterwards, from this folder:

    python -m pdb -c continue examples.py
    (Pdb) where / args / p row / q
"""

import traceback  # only used in section 5 to show a full traceback without dying

# ---------------------------------------------------------------------------
# 1. Exceptions are control flow
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. An exception travels UP the call stack")
print("=" * 70)


def parse_units(text: str) -> int:
    """Detects the problem: int() raises ValueError on junk."""
    return int(text)


def load_row(row: dict) -> int:
    """Decides what to do about it: junk counts as zero here."""
    try:
        return parse_units(row["units"])
    except ValueError:
        return 0


print("load_row({'units': '7'})   ->", load_row({"units": "7"}))
print("load_row({'units': 'n/a'}) ->", load_row({"units": "n/a"}), "(handled, not fatal)")

# An exception object is just a value with a type and a message.
error_object = ValueError("bad input")
print("type(error_object) ->", type(error_object).__name__)
print("str(error_object)  ->", str(error_object))


# ---------------------------------------------------------------------------
# 2. Reading a traceback bottom-up
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. A real multi-frame traceback")
print("=" * 70)

SALES = [
    {"region": "north", "units": "12", "price": "9.99"},
    {"region": "south", "units": "7", "price": "12.50"},
    {"region": "east", "units": "n/a", "price": "3.00"},  # <- the poison row
]


def line_revenue(row: dict) -> float:
    units = int(row["units"])  # <- this is where it will blow up
    price = float(row["price"])
    return units * price


def total_revenue(rows: list[dict]) -> float:
    total = 0.0
    for row in rows:
        total += line_revenue(row)
    return total


def report() -> None:
    print(f"total: {total_revenue(SALES):.2f}")


try:
    report()
except ValueError:
    # traceback.format_exc() gives us the text Python would have printed.
    print("Python would have printed this and exited:")
    print()
    print(traceback.format_exc().rstrip())
    print()
    print("Read it like this:")
    print("  1. LAST line       -> ValueError + the offending value 'n/a'")
    print("  2. innermost frame -> line_revenue, the line `units = int(row['units'])`")
    print("  3. frame above     -> total_revenue: the row came from a loop")
    print("  4. frame above     -> report: the data came from SALES")
    print("  5. bottom frame    -> <module>, i.e. top level of the file")


# ---------------------------------------------------------------------------
# 3. The built-in exceptions you will actually meet
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. What causes what")
print("=" * 70)


def show_failure(label: str) -> None:
    """Run one deliberately broken snippet and report its exception type."""
    try:
        if label == "int('n/a')":
            int("n/a")
        elif label == "'a' + 1":
            "a" + 1  # noqa: B018
        elif label == "len(5)":
            len(5)
        elif label == "{'a': 1}['b']":
            {"a": 1}["b"]
        elif label == "[1, 2][5]":
            [1, 2][5]
        elif label == "None.strip()":
            None.strip()
        elif label == "1 / 0":
            1 / 0
        elif label == "next(iter([]))":
            next(iter([]))
    except Exception as error:  # broad ON PURPOSE: this is a demo that reports
        print(f"  {label:<16} -> {type(error).__name__}: {error}")


for snippet in (
    "int('n/a')",
    "'a' + 1",
    "len(5)",
    "{'a': 1}['b']",
    "[1, 2][5]",
    "None.strip()",
    "1 / 0",
    "next(iter([]))",
):
    show_failure(snippet)

print()
print("The hierarchy lets one handler cover a family:")
print("  KeyError is a LookupError? ", issubclass(KeyError, LookupError))
print("  IndexError is a LookupError?", issubclass(IndexError, LookupError))
print("  FileNotFoundError is an OSError?", issubclass(FileNotFoundError, OSError))
print("  KeyboardInterrupt is an Exception?", issubclass(KeyboardInterrupt, Exception))
print("  ^ that False is why `except Exception` still lets Ctrl-C through")


# ---------------------------------------------------------------------------
# 4. try / except / else / finally
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. try / except / else / finally, in execution order")
print("=" * 70)


def read_units(row: dict) -> int:
    try:
        units = int(row["units"])  # keep the try SMALL: one risky line
    except KeyError:
        print("  except KeyError: no 'units' column")
        return 0
    except ValueError as error:  # `as error` binds the exception object
        print(f"  except ValueError: {error}")
        return 0
    else:
        print("  else: try finished with no exception")
        return units
    finally:
        print("  finally: always runs (even after a return)")


print("read_units({'units': '7'})   ->", read_units({"units": "7"}))
print("read_units({'units': 'n/a'}) ->", read_units({"units": "n/a"}))
print("read_units({})               ->", read_units({}))

print()
print("Several types in ONE handler (note the parentheses: it is a tuple):")
for candidate in ({"units": "5"}, {"units": "x"}, {}):
    try:
        value = int(candidate["units"])
    except (KeyError, ValueError) as error:
        print(f"  skipping {candidate!r}: {type(error).__name__}: {error}")
    else:
        print(f"  parsed {candidate!r} -> {value}")


# ---------------------------------------------------------------------------
# 5. Why bare except: is a bug
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. Bare except: hides your own typos")
print("=" * 70)

row = {"units": "12", "price": "9.99"}


def total_with_bare_except(data: dict) -> float:
    try:
        return int(data["units"]) * float(data["prise"])  # typo: 'prise'
    except:  # noqa: E722 - deliberately wrong, for teaching
        return 0.0


def total_with_specific_except(data: dict) -> float:
    try:
        return int(data["units"]) * float(data["prise"])  # same typo
    except ValueError as error:
        print(f"  reported: {error}")
        return 0.0


print("bare except      ->", total_with_bare_except(row), " <- a silent 0.0, no clue why")
try:
    print("specific except  ->", total_with_specific_except(row))
except KeyError as error:
    print(f"specific except  -> KeyError {error} escaped, so the typo is VISIBLE")


# ---------------------------------------------------------------------------
# 6. raise, re-raise, raise ... from, custom exceptions
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Raising on purpose")
print("=" * 70)


def set_age(age: object) -> int:
    if not isinstance(age, int):
        raise TypeError(f"age must be an int, got {type(age).__name__}")
    if age < 0:
        raise ValueError(f"age must not be negative, got {age}")
    if age > 130:
        raise ValueError(f"age {age} is implausible")
    return age


for candidate in (30, -4, "forty", 999):
    try:
        print(f"  set_age({candidate!r}) -> {set_age(candidate)}")
    except (TypeError, ValueError) as error:
        print(f"  set_age({candidate!r}) -> {type(error).__name__}: {error}")


# A custom exception is three lines. Day 12 explains `class` properly.
class AppError(Exception):
    """Base class for every error this demo raises on purpose."""


class ConfigError(AppError):
    """Raised when a configuration value cannot be used."""


def load_port(text: str) -> int:
    try:
        return int(text)
    except ValueError as error:
        # Translate a low-level failure into a meaningful one, keeping the cause.
        raise ConfigError(f"port must be a whole number, got {text!r}") from error


print()
print("load_port('8080') ->", load_port("8080"))
try:
    load_port("http")
except ConfigError as error:
    print("load_port('http') raised:", type(error).__name__, "-", error)
    print("  original cause preserved as __cause__:", type(error.__cause__).__name__)

# Catching the BASE class catches every deliberate error of this app.
try:
    load_port("nope")
except AppError as error:
    print("caught via the base class AppError:", type(error).__name__)


def must_exist(mapping: dict, key: str) -> str:
    try:
        return mapping[key]
    except KeyError:
        print(f"  noting that {key!r} is missing, then letting it fly")
        raise  # bare raise: same exception, original traceback intact


try:
    must_exist({"a": "1"}, "b")
except KeyError as error:
    print("re-raised KeyError reached the caller:", error)


# ---------------------------------------------------------------------------
# 7. assert
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. assert is for YOUR invariants, not user input")
print("=" * 70)


def apply_split(total: float, shares: int) -> float:
    # An internal invariant: this function is only ever called with shares > 0.
    assert shares > 0, f"shares must be positive, got {shares}"
    return total / shares


print("apply_split(100, 4) ->", apply_split(100, 4))
try:
    apply_split(100, 0)
except AssertionError as error:
    print("apply_split(100, 0) raised AssertionError:", error)

print("Remember: `python -O` strips asserts out entirely, so user input needs")
print("an explicit `if ...: raise ValueError(...)` instead.")

# The classic silent mistake: a tuple is always truthy, so this never fires.
# Python even printed a SyntaxWarning about it above, before this script ran:
#   SyntaxWarning: assertion is always true, perhaps remove parentheses?
assert (1 == 2, "this message never appears")  # noqa: B011,F631
print("`assert (cond, 'msg')` did NOT fail above — that is the parenthesis trap.")
print("Scroll up: Python warned about it with a SyntaxWarning at import time.")


# ---------------------------------------------------------------------------
# 8. EAFP vs LBYL
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. EAFP vs LBYL on the same data")
print("=" * 70)

candidates = [{"units": "12"}, {"units": "12.5"}, {"units": " 7"}, {"units": "x"}, {}]


def units_lbyl(data: dict) -> int:
    """Look before you leap — and miss cases you did not think of."""
    if "units" in data and data["units"].isdigit():
        return int(data["units"])
    return 0


def units_eafp(data: dict) -> int:
    """Ask forgiveness — int() itself defines what is acceptable."""
    try:
        return int(data["units"])
    except (KeyError, ValueError):
        return 0


print(f"{'input':<18}{'LBYL':>6}{'EAFP':>6}")
for data in candidates:
    print(f"{str(data):<18}{units_lbyl(data):>6}{units_eafp(data):>6}")
print("' 7' is a real number to int() but isdigit() says no: the LBYL guard was")
print("a GUESS at int()'s rules. EAFP asks int() itself.")


# ---------------------------------------------------------------------------
# 9. Debugging methodology
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. Isolate, then print-debug properly")
print("=" * 70)

print("Isolation: call the innermost function with the smallest failing input.")
try:
    line_revenue({"region": "east", "units": "n/a", "price": "3.00"})
except ValueError as error:
    print(f"  one-line reproduction -> {type(error).__name__}: {error}")


def line_revenue_debug(row: dict, index: int) -> float:
    """The same function with useful prints: labelled, !r, and typed."""
    print(f"  [line_revenue row {index}] row={row!r}")
    units_text = row["units"]
    print(f"  [line_revenue row {index}] units_text={units_text!r} "
          f"type={type(units_text).__name__}")
    units = int(units_text)
    return units * float(row["price"])


for index, row in enumerate(SALES):
    try:
        value = line_revenue_debug(row, index)
    except ValueError as error:
        print(f"  [line_revenue row {index}] FAILED: {error}")
        print(f"  -> row {index} is the culprit; '{row['units']}' is not a number")
    else:
        print(f"  [line_revenue row {index}] ok -> {value:.2f}")

print()
print("Bisecting the data: which half fails?")
first_half, second_half = SALES[:2], SALES[2:]
for label, chunk in (("first half", first_half), ("second half", second_half)):
    try:
        total_revenue(chunk)
    except ValueError:
        print(f"  {label}: FAILS -> search here next")
    else:
        print(f"  {label}: ok")

print()
print("Where a real debugger would go (do this by hand, it is the whole point):")
print("  def line_revenue(row):")
print("      breakpoint()          # then: l, a, p row, p type(row['units']), n, c")
print("Or post-mortem, with no code edits at all:")
print("  python -m pdb -c continue examples.py")

print()
print("Done. Now open exercises.py in this folder.")
