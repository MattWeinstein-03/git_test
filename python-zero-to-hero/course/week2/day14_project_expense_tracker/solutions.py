"""Day 14 solutions — Project 2: a persistent Expense Tracker.

A complete reference implementation. Read it after your own attempt, and pay
attention to the layering rather than the line count:

    Expense       validates, and is the only door into valid data
    ExpenseStore  owns the collection, persists it, and answers questions
    main()        the only function that prints or reads input
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_FILE = "expenses.json"
REQUIRED_CSV_FIELDS = ("amount", "category", "date")


class ValidationError(Exception):
    """Raised when data offered to the tracker is not acceptable."""


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
@dataclass
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

    amount: float
    category: str
    date: str
    note: str = ""

    def __post_init__(self) -> None:
        # why: __post_init__ is the single door into a valid Expense. Every
        # caller — the menu, the csv import, the json load — gets these rules.
        if isinstance(self.amount, bool) or not isinstance(self.amount, (int, float)):
            raise ValidationError(
                f"amount must be a number, got {type(self.amount).__name__}"
            )
        if self.amount <= 0:
            raise ValidationError(f"amount must be positive, got {self.amount}")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValidationError("category must not be empty")
        if not is_iso_date(self.date):
            raise ValidationError(f"date must be YYYY-MM-DD, got {self.date!r}")

        # Normalise once, here, so nothing downstream has to guess.
        self.amount = float(self.amount)
        self.category = self.category.strip().lower()
        self.note = self.note.strip() if isinstance(self.note, str) else ""

    @property
    def month(self) -> str:
        """The "YYYY-MM" this expense belongs to."""
        # why: ISO dates make this a slice instead of date arithmetic.
        return self.date[:7]

    def to_dict(self) -> dict:
        """A plain dict of JSON-safe types."""
        return {
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Expense:
        """Build an Expense from a dict, e.g. one decoded from JSON."""
        for name in ("amount", "category", "date"):
            if name not in data:
                raise ValidationError(f"missing field: {name}")
        # why: cls(...) so a subclass of Expense would rebuild as itself.
        return cls(
            amount=data["amount"],
            category=data["category"],
            date=data["date"],
            note=data.get("note", ""),
        )


def _by_total_then_category(pair: tuple[str, float]) -> tuple[float, str]:
    """Sort key: biggest total first, ties alphabetically. A named function, not
    a lambda — lambdas are Day 16."""
    category, total = pair
    return (-total, category)


def _sorted_dict(raw: dict[str, float]) -> dict[str, float]:
    """Return a new dict with the same items, keys in sorted order, rounded."""
    ordered: dict[str, float] = {}
    for key in sorted(raw):
        ordered[key] = round(raw[key], 2)
    return ordered


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
        # why: None default, real list built here (Day 8), and list(...) copies
        # so the caller's list and ours are independent (Day 13).
        self._expenses: list[Expense] = list(expenses) if expenses is not None else []

    def add(self, expense: Expense) -> None:
        if not isinstance(expense, Expense):
            raise TypeError(f"expected an Expense, got {type(expense).__name__}")
        self._expenses.append(expense)

    def remove(self, index: int) -> Expense:
        # why: list.pop already raises IndexError with a clear message.
        return self._expenses.pop(index)

    def all(self) -> list[Expense]:
        return list(self._expenses)

    def __len__(self) -> int:
        return len(self._expenses)

    def __iter__(self):
        return iter(self._expenses)

    # --- M3 ---------------------------------------------------------------
    def save(self, path: Path) -> int:
        """Write every expense to `path` as a JSON array. Returns the count."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        records = []
        for expense in self._expenses:
            records.append(expense.to_dict())
        with open(path, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=2)
        return len(records)

    @classmethod
    def load(cls, path: Path) -> ExpenseStore:
        """Return a new store read from `path`. A missing file is an empty store."""
        path = Path(path)
        try:
            with open(path, encoding="utf-8") as file:
                records = json.load(file)
        except FileNotFoundError:
            # why: a first run has nothing to read. That is not an error.
            return cls()
        except json.JSONDecodeError as error:
            # why: `from error` keeps the decoder's position info as __cause__.
            raise ValidationError(f"{path} is not valid JSON") from error

        if not isinstance(records, list):
            raise ValidationError(f"{path} must contain a list of expenses")

        store = cls()
        for record in records:
            store.add(Expense.from_dict(record))
        return store

    # --- M4 ---------------------------------------------------------------
    def total(self) -> float:
        total = 0.0
        for expense in self._expenses:
            total += expense.amount
        return round(total, 2)

    def total_by_category(self) -> dict[str, float]:
        raw: dict[str, float] = {}
        for expense in self._expenses:
            # why: the Day 6 grouping pattern — .get with a default.
            raw[expense.category] = raw.get(expense.category, 0.0) + expense.amount
        return _sorted_dict(raw)

    def top_categories(self, n: int) -> list[tuple[str, float]]:
        if n <= 0:
            return []
        pairs = list(self.total_by_category().items())
        pairs.sort(key=_by_total_then_category)
        return pairs[:n]

    def monthly_totals(self) -> dict[str, float]:
        raw: dict[str, float] = {}
        for expense in self._expenses:
            raw[expense.month] = raw.get(expense.month, 0.0) + expense.amount
        # why: ISO months sort chronologically as plain strings.
        return _sorted_dict(raw)

    # --- M5 ---------------------------------------------------------------
    def import_csv(self, path: Path) -> tuple[int, list[str]]:
        """Add every usable row of the CSV at `path`. Returns (added, problems)."""
        added = 0
        problems: list[str] = []

        with open(path, encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for index, row in enumerate(reader):
                number = index + 1

                missing = _first_missing_field(row)
                if missing is not None:
                    problems.append(f"row {number}: missing {missing}")
                    continue

                try:
                    expense = _expense_from_row(row)
                except ValidationError as error:
                    # why: report and move on. One bad row must not end the import.
                    problems.append(f"row {number}: {error}")
                    continue

                self.add(expense)
                added += 1

        return added, problems


def _first_missing_field(row: dict) -> str | None:
    """Return the first required CSV field that is absent or blank, else None."""
    for name in REQUIRED_CSV_FIELDS:
        value = row.get(name)
        if value is None or str(value).strip() == "":
            return name
    return None


def _expense_from_row(row: dict) -> Expense:
    """Build an Expense from a CSV row, translating a bad amount into ValidationError."""
    raw_amount = str(row["amount"]).strip()
    try:
        amount = float(raw_amount)
    except ValueError as error:
        # why: translate the low-level ValueError into the project's own error
        # type, keeping the original as __cause__ (Day 9).
        raise ValidationError(f"amount {raw_amount!r} is not a number") from error
    return Expense(
        amount=amount,
        category=str(row["category"]),
        date=str(row["date"]).strip(),
        note=str(row.get("note") or ""),
    )


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


def format_expenses(store: ExpenseStore) -> str:
    """Return a numbered listing of every expense. Pure: data in, string out."""
    if not len(store):
        return "(nothing recorded yet)"
    lines = []
    for index, expense in enumerate(store):
        note = f"  {expense.note}" if expense.note else ""
        lines.append(
            f"{index:>3}  {expense.date}  {expense.category:<12}"
            f"{expense.amount:>9.2f}{note}"
        )
    return "\n".join(lines)


def format_report(store: ExpenseStore) -> str:
    """Return the full report as a string. Pure, so it is testable and reusable."""
    if not len(store):
        return "(nothing recorded yet)"
    lines = ["by category:"]
    for category, amount in store.total_by_category().items():
        lines.append(f"  {category:<14}{amount:>10.2f}")
    lines.append("by month:")
    for month, amount in store.monthly_totals().items():
        lines.append(f"  {month:<14}{amount:>10.2f}")
    lines.append("top categories:")
    for position, pair in enumerate(store.top_categories(3), start=1):
        lines.append(f"  {position}. {pair[0]} ({pair[1]:.2f})")
    lines.append(f"{'TOTAL':<16}{store.total():>10.2f}")
    return "\n".join(lines)


def _prompt_new_expense() -> Expense:
    """Ask for one expense. Raises ValidationError, which main() reports."""
    amount_text = input("amount: ").strip()
    try:
        amount = float(amount_text)
    except ValueError as error:
        raise ValidationError(f"amount {amount_text!r} is not a number") from error
    category = input("category: ")
    date = input("date (YYYY-MM-DD): ").strip()
    note = input("note (optional): ")
    return Expense(amount=amount, category=category, date=date, note=note)


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
    if store is None:
        store = ExpenseStore()
    if data_path is None:
        data_path = Path(DEFAULT_DATA_FILE)

    while True:
        print(MENU)
        try:
            choice = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # why: a piped or interrupted session should not end in a traceback.
            print()
            print("bye")
            return 0

        if choice == "q":
            print("bye")
            return 0

        try:
            if choice == "1":
                store.add(_prompt_new_expense())
                print(f"added. {len(store)} expense(s) recorded.")
            elif choice == "2":
                print(format_expenses(store))
            elif choice == "3":
                print(format_report(store))
            elif choice == "4":
                written = store.save(data_path)
                print(f"saved {written} expense(s) to {data_path}")
            elif choice == "5":
                loaded = ExpenseStore.load(data_path)
                store = loaded
                print(f"loaded {len(store)} expense(s) from {data_path}")
            elif choice == "6":
                csv_path = Path(input("csv path: ").strip())
                added, problems = store.import_csv(csv_path)
                print(f"imported {added} row(s), skipped {len(problems)}")
                for problem in problems:
                    print(f"  {problem}")
            else:
                print(f"unknown choice: {choice}")
        except ValidationError as error:
            # why: bad input is expected. Report it and keep the session alive.
            print(f"rejected: {error}")
        except FileNotFoundError as error:
            print(f"no such file: {error.filename}")
        except (EOFError, KeyboardInterrupt):
            print()
            print("bye")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
