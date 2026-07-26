# Expense Tracker

A small command-line expense tracker: record what you spent, save it to JSON,
import a CSV export, and print reports. Built for Day 14 of python-zero-to-hero
using the standard library only.

This README is a model — replace it with your own once your version runs.

## Requirements

- Python 3.10 or newer (`python --version`)
- pytest, only for grading: `python -m pip install pytest`

No third-party packages are needed to run the app.

## Run it

From the course root:

```bash
python course/week2/day14_project_expense_tracker/exercises.py
```

Or from inside the project folder:

```bash
cd course/week2/day14_project_expense_tracker
python exercises.py
```

You get a menu:

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

A first session looks like this:

```
> 1
amount: 12.50
category: food
date (YYYY-MM-DD): 2024-03-01
note (optional): lunch
added. 1 expense(s) recorded.
> 4
saved 1 expense(s) to expenses.json
> q
bye
```

Data is written to `expenses.json` in the directory you ran the command from.
Start again and press `5` to load it back.

## Importing a CSV

The file needs a header row with `amount`, `category` and `date`, and may have a
`note` column:

```csv
amount,category,date,note
12.50,food,2024-03-01,lunch
30,transport,2024-03-02,
```

Choose `6` and give the path. Rows that are unusable are skipped and reported
individually — the good rows are still imported:

```
> 6
csv path: march.csv
imported 2 row(s), skipped 1
  row 3: amount 'n/a' is not a number
```

## What counts as valid

| Field | Rule |
|---|---|
| `amount` | a number greater than 0 |
| `category` | not blank; stored stripped and lowercased |
| `date` | `YYYY-MM-DD` |
| `note` | optional, stored stripped |

Anything else is refused with a message naming the problem, and the session
carries on.

## Grade it

From the course root:

```bash
python check.py day14          # milestone-by-milestone progress
python check.py day14 -v       # with full failure detail
```

Or with pytest directly:

```bash
python -m pytest course/week2/day14_project_expense_tracker -q
```

## Use it as a library

The API is plain Python, so the reporting works without the menu:

```python
from pathlib import Path

from exercises import Expense, ExpenseStore

store = ExpenseStore.load(Path("expenses.json"))
store.add(Expense(12.5, "food", "2024-03-01", "lunch"))
print(store.total())
print(store.total_by_category())
print(store.top_categories(3))
print(store.monthly_totals())
store.save(Path("expenses.json"))
```

## Files

| File | What it is |
|---|---|
| `LESSON.md` | the project brief: milestones M1–M5, hints, done-checklist |
| `exercises.py` | your implementation, and the app entry point |
| `solutions.py` | the reference implementation — read it after your attempt |
| `examples.py` | the same design demonstrated on a different app (a reading log) |
| `test_exercises.py` | the graded checks, `test_m1_*` … `test_m5_*` |
