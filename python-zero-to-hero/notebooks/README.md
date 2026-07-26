# Notebooks (generated — do not edit)

One notebook per day, so you can read the lesson and run its code in the same
place. Open `day01_getting_started.ipynb` and work down the page: Shift+Enter
runs a cell.

**Every file in this folder is generated.** `tools/build_notebooks.py` reads
`course/weekN/dayNN_slug/LESSON.md` and writes the matching notebook here. If
you edit a notebook, the next build throws your edit away.

## The rule

`LESSON.md` is the single source of truth. Notebooks are artefacts of it.

- Teaching content changes go in `LESSON.md`.
- Changes to how notebooks are built go in `tools/build_notebooks.py`.
- Nothing goes in a notebook by hand.

## Rebuilding

From the course root:

```bash
python tools/build_notebooks.py            # rebuild all 21 notebooks
python tools/build_notebooks.py --day 05   # rebuild one day
python tools/build_notebooks.py --check    # exit 1 if a notebook is out of date
python tools/build_notebooks.py --verify   # execute every notebook, fail on any error
```

`--check` is the CI guard: it rebuilds in memory and compares bytes, so a lesson
edit that was not followed by a rebuild fails the build. Notebooks are committed
with no stored outputs; you produce the outputs by running them.

## Why some code blocks are not runnable

A fenced `python` block from a lesson becomes a runnable cell only when it can
actually run in order, on its own, with no surprises. Blocks that wait on
`input()`, show a `>>>` transcript, demonstrate an error on purpose, contain a
deliberate syntax error, read or write files, need the network, start threads or
processes, or refer to names the lesson never defines stay as text, with a
one-line note saying which of those it was. Read those; don't try to run them.

## Grading

The notebooks are not graded and never will be — they are a reading and
experimenting surface. The graded work is `exercises.py` in each day folder, and
the last code cell of each notebook runs `check.py` for that day.

| Day | Notebook | Lesson |
|---|---|---|
| 01 | [`day01_getting_started.ipynb`](day01_getting_started.ipynb) | [lesson](../course/week1/day01_getting_started/LESSON.md) |
| 02 | [`day02_numbers_and_strings.ipynb`](day02_numbers_and_strings.ipynb) | [lesson](../course/week1/day02_numbers_and_strings/LESSON.md) |
| 03 | [`day03_conditionals.ipynb`](day03_conditionals.ipynb) | [lesson](../course/week1/day03_conditionals/LESSON.md) |
| 04 | [`day04_loops.ipynb`](day04_loops.ipynb) | [lesson](../course/week1/day04_loops/LESSON.md) |
| 05 | [`day05_lists_and_tuples.ipynb`](day05_lists_and_tuples.ipynb) | [lesson](../course/week1/day05_lists_and_tuples/LESSON.md) |
| 06 | [`day06_dicts_and_sets.ipynb`](day06_dicts_and_sets.ipynb) | [lesson](../course/week1/day06_dicts_and_sets/LESSON.md) |
| 07 | [`day07_project_text_toolkit.ipynb`](day07_project_text_toolkit.ipynb) | [lesson](../course/week1/day07_project_text_toolkit/LESSON.md) |
| 08 | [`day08_functions.ipynb`](day08_functions.ipynb) | [lesson](../course/week2/day08_functions/LESSON.md) |
| 09 | [`day09_errors_and_debugging.ipynb`](day09_errors_and_debugging.ipynb) | [lesson](../course/week2/day09_errors_and_debugging/LESSON.md) |
| 10 | [`day10_files_and_data.ipynb`](day10_files_and_data.ipynb) | [lesson](../course/week2/day10_files_and_data/LESSON.md) |
| 11 | [`day11_modules_and_environments.ipynb`](day11_modules_and_environments.ipynb) | [lesson](../course/week2/day11_modules_and_environments/LESSON.md) |
| 12 | [`day12_classes.ipynb`](day12_classes.ipynb) | [lesson](../course/week2/day12_classes/LESSON.md) |
| 13 | [`day13_oop_in_practice.ipynb`](day13_oop_in_practice.ipynb) | [lesson](../course/week2/day13_oop_in_practice/LESSON.md) |
| 14 | [`day14_project_expense_tracker.ipynb`](day14_project_expense_tracker.ipynb) | [lesson](../course/week2/day14_project_expense_tracker/LESSON.md) |
| 15 | [`day15_comprehensions_and_generators.ipynb`](day15_comprehensions_and_generators.ipynb) | [lesson](../course/week3/day15_comprehensions_and_generators/LESSON.md) |
| 16 | [`day16_decorators_and_functional.ipynb`](day16_decorators_and_functional.ipynb) | [lesson](../course/week3/day16_decorators_and_functional/LESSON.md) |
| 17 | [`day17_standard_library.ipynb`](day17_standard_library.ipynb) | [lesson](../course/week3/day17_standard_library/LESSON.md) |
| 18 | [`day18_testing_and_tooling.ipynb`](day18_testing_and_tooling.ipynb) | [lesson](../course/week3/day18_testing_and_tooling/LESSON.md) |
| 19 | [`day19_apis_and_databases.ipynb`](day19_apis_and_databases.ipynb) | [lesson](../course/week3/day19_apis_and_databases/LESSON.md) |
| 20 | [`day20_concurrency.ipynb`](day20_concurrency.ipynb) | [lesson](../course/week3/day20_concurrency/LESSON.md) |
| 21 | [`day21_project_capstone_pipeline.ipynb`](day21_project_capstone_pipeline.ipynb) | [lesson](../course/week3/day21_project_capstone_pipeline/LESSON.md) |

## Taking it with you

`portable/` is the same 21 notebooks packaged as one self-contained
folder — grader, day folders and reference docs included — for copying to a
laptop or an iPad. See `portable/README.md`. It is generated by the same build,
so it cannot drift either.
