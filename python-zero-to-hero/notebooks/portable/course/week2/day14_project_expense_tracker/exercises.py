"""Day 14 — Project 2: a persistent Expense Tracker.

This file holds the graded API. Read LESSON.md first: it is the project brief,
and it specifies every message and return value the tests check.

Work milestone by milestone and grade as you go — partial credit is visible from
M1 onwards:

    python check.py day14
    python check.py day14 -v

Run the app itself with:

    python course/week2/day14_project_expense_tracker/exercises.py

House rules from Week 2 still apply: standard library only, `encoding="utf-8"`
on every file, `newline=""` for csv, and never write anywhere except a path you
were given.
"""

from __future__ import annotations

import csv  # noqa: F401 - M5 needs it
import json  # noqa: F401 - M3 needs it
from dataclasses import dataclass, field  # noqa: F401 - M1 needs these
from pathlib import Path

DEFAULT_DATA_FILE = "expenses.json"
REQUIRED_CSV_FIELDS = ("amount", "category", "date")


# ---------------------------------------------------------------------------
# GIVEN TO YOU — the project's one custom exception. Raise this for every
# rejected value, so callers can write `except ValidationError:` and catch all
# of them without catching unrelated ValueErrors from elsewhere.
# ---------------------------------------------------------------------------
class ValidationError(Exception):
    """Raised when data offered to the tracker is not acceptable."""


# ---------------------------------------------------------------------------
# A helper you may find useful. You can also write your own.
# ---------------------------------------------------------------------------
def is_iso_date(text: object) -> bool:
    """True when `text` has the shape "YYYY-MM-DD" with a plausible month/day.

    This checks the SHAPE only — no calendar knowledge, so "2024-02-31" passes.
    Real date handling arrives with `datetime` on Day 17.

    Examples:
        is_iso_date("2024-03-01") -> True
        is_iso_date("2024-13-01") -> False
        is_iso_date("1 March 2024") -> False
        is_iso_date("24-3-1") -> False
        is_iso_date(20240301) -> False
    """
    if not isinstance(text, str):
        return False
    parts = text.split("-")
    if len(parts) != 3:
        return False
    year, month, day = parts
    if len(year) != 4 or len(month) != 2 or len(day) != 2:
        return False
    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        return False
    return 1 <= int(month) <= 12 and 1 <= int(day) <= 31


# ===========================================================================
# MILESTONE 1 — the Expense dataclass
# ===========================================================================
class Expense:
    """One expense. Make this a @dataclass — see LESSON.md, milestone 1.

    Fields, in this order:
        amount: float
        category: str
        date: str            ISO "YYYY-MM-DD"
        note: str = ""

    Validate in __post_init__ and raise ValidationError with exactly these
    messages:
        amount not a number (a bool or a str is not) ->
            f"amount must be a number, got {type(amount).__name__}"
        amount <= 0 ->
            f"amount must be positive, got {amount}"
        category blank once stripped ->
            "category must not be empty"
        date not shaped like YYYY-MM-DD ->
            f"date must be YYYY-MM-DD, got {date!r}"

    Then normalise: amount becomes a float, category is stripped and
    lowercased, note is stripped.

    Members:
        month: a @property returning the "YYYY-MM" part of the date.
        to_dict(): {"amount", "category", "date", "note"} — ready for json.
        from_dict(data): a @classmethod building an Expense from such a dict.
            A missing key raises ValidationError(f"missing field: {name}").
            Check amount, category, date in that order; a missing note is "".

    Examples:
        e = Expense(12.5, "  Food ", "2024-03-01")
        e.amount -> 12.5
        e.category -> "food"
        e.note -> ""
        e.month -> "2024-03"
        e.to_dict() -> {"amount": 12.5, "category": "food",
                        "date": "2024-03-01", "note": ""}
        Expense.from_dict(e.to_dict()) == e -> True
        repr(e) -> "Expense(amount=12.5, category='food', date='2024-03-01', note='')"

        Expense(-5, "food", "2024-03-01")     -> ValidationError
        Expense(0, "food", "2024-03-01")      -> ValidationError
        Expense("12", "food", "2024-03-01")   -> ValidationError
        Expense(True, "food", "2024-03-01")   -> ValidationError
        Expense(5, "   ", "2024-03-01")       -> ValidationError
        Expense(5, "food", "1 March 2024")    -> ValidationError
        Expense.from_dict({"amount": 5})      -> ValidationError("missing field: category")
    """

    # TODO: your code here — add @dataclass above the class, replace this
    # __init__ with the annotated fields, and write __post_init__.
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError("M1: Expense")

    @property
    def month(self) -> str:
        # TODO: your code here
        raise NotImplementedError("M1: Expense.month")

    def to_dict(self) -> dict:
        # TODO: your code here
        raise NotImplementedError("M1: Expense.to_dict")

    @classmethod
    def from_dict(cls, data: dict) -> Expense:
        # TODO: your code here
        raise NotImplementedError("M1: Expense.from_dict")


# ===========================================================================
# MILESTONES 2-5 — the store
# ===========================================================================
class ExpenseStore:
    """A collection of Expenses, with persistence, import, and reports.

    Keep the expenses in one internal list, `self._expenses`.

    M2 — the container:
        __init__(expenses=None): start empty by default, and COPY a list you
            are given so callers cannot bypass add() later.
        add(expense): append it. TypeError if it is not an Expense, and a
            rejected value must not be stored.
        remove(index): remove and return the expense at that position.
            IndexError if the index is out of range.
        all(): a COPY of the list of expenses.
        __len__: how many expenses (so an empty store is falsy).
        __iter__: iterate the expenses in order.

    M3 — persistence:
        save(path): write a JSON array of to_dict() records with indent=2 and
            encoding="utf-8", creating the parent directory if needed. Returns
            how many records were written.
        load(path): a @classmethod returning a NEW ExpenseStore.
            * missing file -> an empty store (a first run is not an error)
            * invalid JSON -> ValidationError(f"{path} is not valid JSON")
            * JSON that is not a list ->
                  ValidationError(f"{path} must contain a list of expenses")
            * a record that fails validation -> let from_dict's ValidationError
              reach the caller.

    M4 — reporting. These return data; they never print and never touch disk:
        total(): every amount added up, rounded to 2 decimals. 0.0 when empty.
        total_by_category(): {category: total}, each rounded to 2 decimals,
            keys in alphabetical order.
        top_categories(n): the n biggest categories as (category, total) pairs,
            largest first, ties broken alphabetically. [] when n <= 0.
        monthly_totals(): {"YYYY-MM": total} rounded to 2 decimals, keys in
            chronological order.

    M5 — csv import:
        import_csv(path): read a CSV with a header row, add every usable row,
            and return (added, problems).
            * a required field (amount, category, date — in that order) absent
              or blank -> skip, record f"row {n}: missing {field}"
            * Expense(...) rejects it -> skip, record f"row {n}: {error}"
            * rows are numbered from 1, not counting the header
            * a missing file lets FileNotFoundError propagate
            One bad row must never stop the import.

    Examples:
        store = ExpenseStore()
        len(store) -> 0
        store.add(Expense(12.5, "food", "2024-03-01"))
        store.add(Expense(30.0, "transport", "2024-03-02"))
        len(store) -> 2
        store.total() -> 42.5
        store.total_by_category() -> {"food": 12.5, "transport": 30.0}
        store.top_categories(1) -> [("transport", 30.0)]
        store.monthly_totals() -> {"2024-03": 42.5}
        store.save(tmp_path / "expenses.json") -> 2
        ExpenseStore.load(tmp_path / "expenses.json").all() == store.all() -> True
        ExpenseStore.load(tmp_path / "missing.json") -> an empty store
        store.remove(0).category -> "food"
        store.import_csv(path) -> (3, ["row 2: missing amount"])
    """

    # --- M2 ---------------------------------------------------------------
    def __init__(self, expenses: list[Expense] | None = None) -> None:
        # TODO: your code here
        raise NotImplementedError("M2: ExpenseStore.__init__")

    def add(self, expense: Expense) -> None:
        # TODO: your code here
        raise NotImplementedError("M2: ExpenseStore.add")

    def remove(self, index: int) -> Expense:
        # TODO: your code here
        raise NotImplementedError("M2: ExpenseStore.remove")

    def all(self) -> list[Expense]:
        # TODO: your code here
        raise NotImplementedError("M2: ExpenseStore.all")

    def __len__(self) -> int:
        # TODO: your code here
        raise NotImplementedError("M2: ExpenseStore.__len__")

    def __iter__(self):
        # TODO: your code here
        raise NotImplementedError("M2: ExpenseStore.__iter__")

    # --- M3 ---------------------------------------------------------------
    def save(self, path: Path) -> int:
        # TODO: your code here
        raise NotImplementedError("M3: ExpenseStore.save")

    @classmethod
    def load(cls, path: Path) -> ExpenseStore:
        # TODO: your code here
        raise NotImplementedError("M3: ExpenseStore.load")

    # --- M4 ---------------------------------------------------------------
    def total(self) -> float:
        # TODO: your code here
        raise NotImplementedError("M4: ExpenseStore.total")

    def total_by_category(self) -> dict[str, float]:
        # TODO: your code here
        raise NotImplementedError("M4: ExpenseStore.total_by_category")

    def top_categories(self, n: int) -> list[tuple[str, float]]:
        # TODO: your code here
        raise NotImplementedError("M4: ExpenseStore.top_categories")

    def monthly_totals(self) -> dict[str, float]:
        # TODO: your code here
        raise NotImplementedError("M4: ExpenseStore.monthly_totals")

    # --- M5 ---------------------------------------------------------------
    def import_csv(self, path: Path) -> tuple[int, list[str]]:
        # TODO: your code here
        raise NotImplementedError("M5: ExpenseStore.import_csv")


# ===========================================================================
# The menu — the only place that prints or reads input
# ===========================================================================
MENU = """
Expense Tracker
  1  add an expense
  2  list expenses
  3  report
  4  save
  5  load
  6  import a csv
  q  quit"""


def main(store: ExpenseStore | None = None, data_path: Path | None = None) -> int:
    """Run the text menu until the user quits. Returns the exit code, 0.

    Both arguments are optional so that tests (and you, from the REPL) can pass
    a prepared store and a temporary path:
        store defaults to an empty ExpenseStore()
        data_path defaults to Path("expenses.json")

    Requirements from LESSON.md:
      * print MENU, then read a choice with input("> ")
      * "1" add, "2" list, "3" report, "4" save, "5" load, "6" import a csv,
        "q" quit
      * catch ValidationError in the add flow, print the message, keep going
      * an unknown choice prints f"unknown choice: {choice}"
      * EOFError or KeyboardInterrupt ends the loop cleanly — never a traceback
      * return 0

    Examples:
        main()                      # interactive
        main(store, tmp_path / "expenses.json")
    """
    # TODO: your code here
    raise NotImplementedError("main")


if __name__ == "__main__":
    raise SystemExit(main())
