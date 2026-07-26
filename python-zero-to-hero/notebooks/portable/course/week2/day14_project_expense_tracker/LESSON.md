# Day 14 — Project 2: Expense Tracker

> **Time:** ~4 hours  |  **Prerequisites:** Days 08–13

## What you'll be able to do after today
- Build a small application that survives being closed and reopened, by saving and loading its own data.
- Validate incoming data at one boundary and reject it with a custom exception that names the problem.
- Model a domain with a dataclass plus a store class, and report on it with functions that do not touch the disk.
- Import a real-world CSV that contains bad rows, without crashing and without silently losing data.
- Ship it with a `README.md` and a text menu somebody else can run.

## The goal

A **persistent Expense Tracker**. You record what you spent, on what, and when; it saves to JSON; it loads again next time; it prints reports; it imports a bank-style CSV export and tells you exactly which rows it refused.

This ties Week 2 together. Every day is in here: functions and decomposition (D8), exceptions and custom error types (D9), `pathlib`/`json`/`csv` (D10), module layout and a `main()` behind `__name__ == "__main__"` (D11), dataclasses and `__repr__` (D12), properties, classmethods and dunders (D13).

Scope: about 250 lines of your own code. Standard library only. No comprehensions, generators, `lambda`, or decorators you wrote yourself — those are Week 3. Using `@dataclass`, `@property` and `@classmethod` is expected.

## User stories

1. As a user, I can record an expense with an amount, a category, a date, and an optional note, and nonsense is refused with a message that tells me what was wrong.
2. As a user, I can list everything I have recorded and see how many entries there are.
3. As a user, I can remove an entry I got wrong.
4. As a user, my expenses are still there after I close the program.
5. As a user, I can see my total, my total per category, my biggest categories, and a month-by-month breakdown.
6. As a user, I can import a CSV exported from somewhere else, and be told which rows were skipped and why — without losing the good rows.
7. As a user, I can do all of the above from a menu without reading the source code.

---

## The graded API

Everything below lives in `exercises.py`. The names and behaviours are fixed, because `test_exercises.py` grades them milestone by milestone: `test_m1_*` through `test_m5_*`, so partial credit is visible from the first milestone onward. Run `python check.py day14` as often as you like — a rising number is the point.

`ValidationError` is given to you at the top of `exercises.py`. Everything else you write.

```
M1  Expense           dataclass with validation
    Expense.month     property -> "YYYY-MM"
    Expense.to_dict() / Expense.from_dict()

M2  ExpenseStore      add / remove / all / __len__ / __iter__

M3  ExpenseStore.save(path)          -> int
    ExpenseStore.load(path)          -> ExpenseStore     (classmethod)

M4  ExpenseStore.total()             -> float
    ExpenseStore.total_by_category() -> dict[str, float]
    ExpenseStore.top_categories(n)   -> list[tuple[str, float]]
    ExpenseStore.monthly_totals()    -> dict[str, float]

M5  ExpenseStore.import_csv(path)    -> tuple[int, list[str]]

    main()            the text menu
```

---

## Milestone 1 — `Expense`, with validation

A `@dataclass` holding one expense, which **cannot exist in an invalid state**.

Fields, in this order: `amount: float`, `category: str`, `date: str`, `note: str = ""`.

Validate in `__post_init__` and raise `ValidationError` with these exact messages:

| Rule | Message |
|---|---|
| amount must be a number (not a `bool`, not a `str`) | `f"amount must be a number, got {type(amount).__name__}"` |
| amount must be greater than 0 | `f"amount must be positive, got {amount}"` |
| category must not be blank | `"category must not be empty"` |
| date must be ISO `YYYY-MM-DD` with a real month and day | `f"date must be YYYY-MM-DD, got {date!r}"` |

Then normalise: `amount` becomes a `float`, `category` is stripped and lowercased, `note` is stripped.

Also:
- `month` — a `@property` returning the first seven characters, `"2024-03"`.
- `to_dict()` — a plain dict with keys `amount`, `category`, `date`, `note`, ready for `json.dump`.
- `from_dict(data)` — a `@classmethod` building an `Expense` from such a dict. A missing key raises `ValidationError(f"missing field: {name}")`.

Date checking without `datetime` (that is Day 17): split on `"-"`, require three parts of length 4, 2, 2, all digits, month 1–12, day 1–31. `"2024-02-31"` passing is acceptable — you are checking the *shape*, and the tests say so.

**Hints.** `__post_init__` runs straight after the generated `__init__`; assign to `self.category` there to normalise it. Reject `bool` explicitly — `isinstance(True, int)` is `True`, and `True` is not an amount.

---

## Milestone 2 — `ExpenseStore`

The container. It owns a list of `Expense` objects and nothing else knows how they are stored.

- `__init__(expenses: list[Expense] | None = None)` — starts empty by default. Copy the list you are given (Day 8's mutable-default lesson, Day 13's defensive-copy lesson).
- `add(expense)` — append it. `TypeError` if it is not an `Expense`; a bad value must not be stored.
- `remove(index)` — remove and return the expense at that position. `IndexError` for an out-of-range index.
- `all()` — a list of the expenses. Return a **copy**, so a caller cannot reach in and mutate your list.
- `__len__` — how many expenses.
- `__iter__` — so `for expense in store:` works. `return iter(...)` over your list.

**Hints.** One internal attribute, `self._expenses`. `__len__` also gives you truthiness for free: an empty store is falsy.

---

## Milestone 3 — JSON persistence

- `save(path)` — write every expense as a JSON array of dicts, `indent=2`, `encoding="utf-8"`. Create the parent directory if it does not exist. Return how many records were written.
- `load(path)` — a `@classmethod` returning a **new `ExpenseStore`**:
  - the file does not exist -> an **empty store** (a first run is not an error);
  - the file is not valid JSON -> `ValidationError(f"{path} is not valid JSON")`;
  - the JSON is not a list -> `ValidationError(f"{path} must contain a list of expenses")`;
  - a record fails validation -> let the `ValidationError` from `from_dict` reach the caller.

Round-tripping must be lossless: `save` then `load` gives a store whose `all()` equals the original. You get that equality for free — `@dataclass` generated `__eq__` in M1.

**Hints.** `json.dump(data, file, indent=2)` takes an open file; `json.dumps` returns a string. `json.JSONDecodeError` is a subclass of `ValueError`. Use `raise ValidationError(...) from error` so the original cause survives.

---

## Milestone 4 — Reporting

Four read-only methods. None of them touch the disk, none of them print — they return data, and the menu decides how to display it.

- `total()` — sum of every amount, rounded to 2 decimals. `0.0` for an empty store.
- `total_by_category()` — `{category: total}`, each total rounded to 2 decimals, keys in alphabetical order. `{}` when empty.
- `top_categories(n)` — the `n` biggest categories as `(category, total)` pairs, largest first, ties broken alphabetically. `[]` for `n <= 0`; fewer than `n` pairs is fine when there are not enough categories.
- `monthly_totals()` — `{"YYYY-MM": total}`, rounded to 2 decimals, keys in chronological order (which for ISO strings is the same as alphabetical order — that is *why* the format is worth using).

**Hints.** `total_by_category` is the Day 6 grouping pattern with `dict.get(key, 0.0)`. For `top_categories`, build a list of pairs and `sort` it with a named key function returning `(-total, category)`; no `lambda` (Day 16). Sorted-key dicts: iterate `sorted(raw)` and insert into a fresh dict.

---

## Milestone 5 — CSV import that survives bad data

`import_csv(path)` reads a CSV with a header row and adds every usable row, returning `(added, problems)`.

Columns: `amount`, `category`, `date`, and optionally `note`. Number data rows from 1.

| Situation | What to do |
|---|---|
| A required field is absent or blank | skip the row, record `f"row {n}: missing {field}"` (check `amount`, `category`, `date`, in that order) |
| `Expense(...)` rejects the row | skip it, record `f"row {n}: {error}"` — the `ValidationError`'s own message |
| The row is fine | add it |
| `path` does not exist | let `FileNotFoundError` propagate — the user named a file that is not there |

One bad row must never stop the import, and a skipped row must never be silently dropped: every skip produces a message.

**Hints.** `csv.DictReader`, `open(..., newline="", encoding="utf-8")`. A short row gives you `None` for the missing columns. Catch `ValidationError` around the construction and turn it into a message.

---

## `main()` — the menu

A tiny text interface, and the only place that prints or reads input.

```
Expense Tracker
  1  add an expense
  2  list expenses
  3  report
  4  save
  5  load
  6  import a csv
  q  quit
>
```

Requirements:

- `main(store=None, data_path=None) -> int` — both optional, so tests can pass a prepared store and a temporary path. Default the store to an empty `ExpenseStore()` and the path to `Path("expenses.json")`.
- Loop until the user types `q` (or `EOFError`/`KeyboardInterrupt` happens — do not let a traceback be your goodbye).
- Return `0`. Call it with `raise SystemExit(main())` under `if __name__ == "__main__":`.
- Catch `ValidationError` in the add flow and print the message, then carry on. A typo must not end the session.
- An unknown choice prints `f"unknown choice: {choice}"`.

This is the part with no automated grading beyond "it starts and quits cleanly", so it is where you get to make it pleasant.

---

## Suggested order of work

1. `Expense` with its four validation rules, then `python check.py day14` — watch `test_m1_*` go green.
2. `month`, `to_dict`, `from_dict`.
3. `ExpenseStore` with `add`/`remove`/`all`/`__len__`/`__iter__`. M2 green.
4. `save`, then `load`, then a round trip by hand in the REPL. M3 green.
5. The four reports. M4 green.
6. `import_csv` with a deliberately dirty CSV of your own. M5 green.
7. `main()`, and run it for real. Add ten expenses, quit, reopen, confirm they are still there.
8. Write the `README.md` (one already exists in this folder as a model — replace it with yours).

## Stretch goals

Not graded. Pick the ones that interest you.

- `remove_where(category=...)` deleting every matching expense and returning the count.
- A `--csv` command-line argument. (`sys.argv` works today; `argparse` is Day 17.)
- Write to a temporary file and `Path.replace()` it into place, so a crash mid-save cannot corrupt your data (Day 10, section 7).
- `Budget` per category, with a report showing over/under.
- `Expense.from_csv_row(row)` as a second alternative constructor.
- An `export_csv(path)` that round-trips with `import_csv`.
- Make `Expense` frozen (`@dataclass(frozen=True)`) and see what breaks and why.
- A `search(text)` matching category or note, case-insensitively.

## How to know you're done

- [ ] `python check.py day14` reports every check passing.
- [ ] `python course/week2/day14_project_expense_tracker/exercises.py` starts the menu and `q` exits without a traceback.
- [ ] Adding an expense, quitting, and restarting shows the expense still there.
- [ ] An amount of `-5`, a category of `"  "`, and a date of `"March 1st"` are each refused with a message naming the problem.
- [ ] A CSV with three good rows and two broken ones imports 3 and reports 2 specific problems.
- [ ] The reports agree with each other: `total()` equals the sum of `total_by_category().values()` and of `monthly_totals().values()`.
- [ ] Nothing writes outside a path the user gave you. No stray files in the repository.
- [ ] Your `README.md` tells a stranger how to run it, in commands they can copy.
- [ ] Every public function has a docstring, and no function is longer than about 20 lines.

---

## Practice

1. Run the demo first. It is a *different* small app — a reading log — built with exactly the same shape (validated dataclass, store, JSON, CSV import, reports), so you can see the pattern without being handed your own answer:

   ```bash
   python course/week2/day14_project_expense_tracker/examples.py
   ```

2. Then work through the milestones in `exercises.py`, grading as you go:

   ```bash
   python check.py day14
   python check.py day14 -v
   ```

3. When it is green, run your app and use it for something real. Then read `solutions.py` and compare decisions — not to check you match it, but to notice where you disagreed and why.

---

## Recall check

1. Why does validation belong in `__post_init__` rather than in the menu code that asks the user for input?
2. Why does `load` return an empty store for a missing file, but raise for a corrupt one?
3. `all()` returns a copy of the list. What breaks if it returns the list itself?
4. Why do the reporting methods return dicts and lists instead of printing?
5. Why must `import_csv` collect problems rather than raise on the first bad row?
6. Why store dates as `"2024-03-01"` strings rather than, say, `"1 March 2024"`?
7. Which of today's classes should be a dataclass, and which should not? Why?

<details>
<summary>Answers</summary>

1. Because `__post_init__` is the only door into an `Expense`, so *every* path — the menu, the CSV import, the JSON load, a future web form — gets the same rules with no duplication. Validation in the menu protects one caller and nothing else.
2. A missing file is the normal state on a first run, so there is nothing to report and an empty store is the correct answer. A corrupt file means data you were told to expect is damaged; silently returning an empty store would look like "you have no expenses" and could then be saved over the top, destroying the evidence.
3. Callers could mutate the store's internals without going through `add`/`remove` — `store.all().clear()` would empty it, bypassing every rule and any bookkeeping you add later.
4. So they can be tested with a single assertion, reused by any interface (menu, CSV export, future web page), and composed with each other. Printing is a side effect that belongs at the edge of the program (Day 8, section 11).
5. Because a 5,000-row import that dies on row 3 is useless. Skipping with a specific message keeps the good rows and still tells the user exactly what was lost — silence would be a data-corruption incident.
6. ISO 8601 sorts chronologically as plain text, which is what makes `monthly_totals()` come out in order with nothing but `sorted()`, and it is unambiguous internationally. It is also what `datetime.fromisoformat` will accept on Day 17.
7. `Expense` should: it is data with a fixed shape, and `__init__`/`__repr__`/`__eq__` are all mechanical (the free `__eq__` is what makes round-trip testing a one-liner). `ExpenseStore` should not: it is behaviour over state — add, remove, save, load, report — which is what plain classes are for.

</details>
