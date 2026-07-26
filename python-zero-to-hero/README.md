# python-zero-to-hero

A 21-day, drill-based Python course for one adult beginner with no programming
experience, built for roughly 4-5 focused hours a day. Every day is a lesson you
read, a demo script you run, a set of exercises you write, and an automated grader
that tells you the truth about whether your code works. Here is the honest deal on
the word "hero": in three weeks you will be able to read and write real Python,
structure a program across functions, classes and modules, handle errors, work with
files, JSON, CSV, HTTP APIs and SQLite, write tests, and — the part that actually
matters — teach yourself the next thing from the official documentation. You will
not have five years of experience, an instinct for large system design, or a mental
index of the standard library. You will have the foundation those things are built
on, plus three finished projects you wrote yourself.

## Start here (60 seconds)

Run these from the course root (the folder containing `check.py`).

```bash
python3 --version          # need 3.10 or newer; if this fails, read SETUP.md
python3 -m pip install pytest
python check.py doctor     # confirms Python, pytest, and the 21 day folders
```

If `python` is not a recognised command on your machine, use `python3` (macOS,
Linux) or `py` (Windows) everywhere in this README. [SETUP.md](SETUP.md) explains
that mess in detail.

Then open the first lesson and start reading:

```
course/week1/day01_getting_started/LESSON.md
```

[Day 1 lesson](course/week1/day01_getting_started/LESSON.md)

## How the course works

Every day is the same loop. Do it in order; the order is the method.

1. **Read** `LESSON.md` start to finish. Do not skim the "Why this matters"
   section — it is what makes the syntax stick.
2. **Run** `python examples.py` inside the day folder. Read the output next to the
   code that produced it. Change a line, run it again, see what breaks. This costs
   you two minutes and buys you a mental model.
3. **Fill in** `exercises.py`. Each function has a docstring describing exactly
   what it must do and a `# TODO: your code here` marker. Replace the
   `raise NotImplementedError(...)` line with your implementation.
4. **Grade** with `python check.py day01` (or whichever day) from the course root.
   The grader lists which checks fail and which exercises are still stubs.
5. **Repeat** step 3 and 4 until every check passes.
6. **Then** read `solutions.py` and diff it against what you wrote. You are not
   looking for "was I right" — the tests already answered that. You are looking
   for where the reference solution is shorter, clearer, or handles a case you
   handled clumsily. That comparison is where most of your growth per day happens.

The grader is not magic. `python check.py day05` runs
`python -m pytest course/week1/day05_lists_and_tuples/test_exercises.py` and
formats the result. Use pytest directly whenever you want more control.

## The 21 days

| Day | Topic | Week theme |
|---|---|---|
| 01 | [Getting started](course/week1/day01_getting_started/LESSON.md) | Week 1: the core language |
| 02 | [Numbers and strings](course/week1/day02_numbers_and_strings/LESSON.md) | |
| 03 | [Conditionals](course/week1/day03_conditionals/LESSON.md) | |
| 04 | [Loops](course/week1/day04_loops/LESSON.md) | |
| 05 | [Lists and tuples](course/week1/day05_lists_and_tuples/LESSON.md) | |
| 06 | [Dicts and sets](course/week1/day06_dicts_and_sets/LESSON.md) | |
| 07 | [**Project 1: text toolkit**](course/week1/day07_project_text_toolkit/LESSON.md) | |
| 08 | [Functions](course/week2/day08_functions/LESSON.md) | Week 2: structuring programs |
| 09 | [Errors and debugging](course/week2/day09_errors_and_debugging/LESSON.md) | |
| 10 | [Files and data](course/week2/day10_files_and_data/LESSON.md) | |
| 11 | [Modules and environments](course/week2/day11_modules_and_environments/LESSON.md) | |
| 12 | [Classes](course/week2/day12_classes/LESSON.md) | |
| 13 | [OOP in practice](course/week2/day13_oop_in_practice/LESSON.md) | |
| 14 | [**Project 2: expense tracker**](course/week2/day14_project_expense_tracker/LESSON.md) | |
| 15 | [Comprehensions and generators](course/week3/day15_comprehensions_and_generators/LESSON.md) | Week 3: real-world Python |
| 16 | [Decorators and functional style](course/week3/day16_decorators_and_functional/LESSON.md) | |
| 17 | [Standard library](course/week3/day17_standard_library/LESSON.md) | |
| 18 | [Testing and tooling](course/week3/day18_testing_and_tooling/LESSON.md) | |
| 19 | [APIs and databases](course/week3/day19_apis_and_databases/LESSON.md) | |
| 20 | [Concurrency](course/week3/day20_concurrency/LESSON.md) | |
| 21 | [**Project 3: capstone pipeline**](course/week3/day21_project_capstone_pipeline/LESSON.md) | |

The three project days (07, 14, 21) are graded milestone by milestone, so partial
progress is visible. They are the days you will point at afterwards when someone
asks what you can build. Full detail on each day, including what each one unlocks
later, is in [SYLLABUS.md](SYLLABUS.md).

## check.py command reference

Run all of these from the course root. The single positional argument is the
target; `-v` and `--fresh` are the only flags.

| Command | What it does |
|---|---|
| `python check.py` | Progress across all 21 days, from cache. Same as `progress`. |
| `python check.py progress` | Explicit form of the above. |
| `python check.py --fresh` | Progress, ignoring the cache and re-grading every day. |
| `python check.py day05` | Grade Day 5. Lists failing checks and unimplemented exercises. |
| `python check.py 5` | Same as `day05`. Leading zeros and the `day` prefix are both optional. |
| `python check.py day05 -v` | Same, plus full pytest output and long tracebacks. |
| `python check.py week2` | Grade every day in week 2. |
| `python check.py all` | Grade all 21 days, always re-running the tests. |
| `python check.py next` | Grade the first day that is not yet fully passing. |
| `python check.py plan` | Print `SYLLABUS.md` to the terminal. |
| `python check.py doctor` | Check Python version, pytest, day folders, virtualenv. |
| `python check.py --help` | Argparse usage summary. |

Notes on real behaviour, so nothing surprises you:

- Exit codes: `0` when everything requested passed, `1` when something failed or
  the target was not understood. Useful if you ever script it.
- `--fresh` only affects `progress`. Day, week, `all` and `next` targets always
  run pytest for real.
- `next` uses the cached results in `.pzh_progress.json` to decide which day is
  first-unfinished. If there is no cache yet, it starts at Day 1.
- Progress results are cached in `.pzh_progress.json` at the course root. Deleting
  that file is harmless; it is regenerated.
- If the `course/` folder is missing or empty, every command prints
  `No day folders found under .../course. Is the course installed?` and exits 1.
- While the course content is still being written, `doctor` reports
  `bad  found N day folders, expected 21` and exits 1. That is expected and not
  something you need to fix.
- Colour output turns itself off when piped to a file or when `NO_COLOR` is set.

Two extra commands worth knowing, both straight pytest:

```bash
python -m pytest course/week1 -q                    # grade a whole week yourself
PZH_SOLUTIONS=1 python -m pytest course/week1 -q    # grade solutions.py instead
```

The second one grades the reference solutions rather than your code. Use it when
you suspect a test is impossible — it will prove that it is not.

## Rules of engagement

These are not motivational suggestions. They are the difference between finishing
this course able to write Python and finishing it able to recognise Python.

- **Type every line of code by hand.** Never copy-paste from the lesson into your
  editor. Typing it forces you to read every character, and your typos teach you
  to read error messages, which is a skill you need more than syntax.
- **Do not open `solutions.py` before your tests pass.** Once you have seen the
  answer you cannot unsee it, and the feeling of "I understood that" is not the
  same as being able to produce it. Read solutions after green, always.
- **Timebox being stuck to 20 minutes.** When the timer runs out, stop
  re-reading your own code. Re-read the exercise docstring, re-read the relevant
  numbered section of `LESSON.md`, then work
  [reference/debugging_playbook.md](reference/debugging_playbook.md) top to bottom.
- **Struggling is the mechanism, not a failure.** The 20 minutes you spend
  confused before it clicks is the part that builds the skill. A day that felt
  easy taught you less than a day that felt hard. Expect discomfort daily; treat
  its absence as a sign you are coasting.
- **Read the whole error message.** Beginners glance at errors; competent
  programmers read them like a sentence. Start at the bottom line, then walk up.
  [reference/error_messages.md](reference/error_messages.md) decodes the ~25
  messages you will actually hit.
- **Finish the day you are on.** Do not park a day at 80% and start the next one.
  Every day builds on the one before, and unfinished foundations compound.

## When you fall behind

You will lose a day somewhere. Plan for it rather than panicking. Some days are
load-bearing — later days assume you can do them cold — and some can be
compressed or deferred without breaking anything.

**Do not skip or rush these:**

- **Day 08 (functions)** — everything after it is written in functions.
- **Day 09 (errors and debugging)** — this is the day you stop being helpless when
  something breaks. Skipping it makes every later day slower.
- **Day 12 (classes)** — Day 13, Day 14 and the capstone all assume it.
- **Day 15 (comprehensions and generators)** — the single biggest jump in how
  Pythonic your code looks, and Day 16 builds directly on it.
- **Day 18 (testing and tooling)** — the skill that makes you employable rather
  than merely capable.

**Safe to compress:**

- **Day 17 (standard library)** is a tour, not a dependency. Read `LESSON.md`, run
  `examples.py`, do the first three or four exercises, and come back to the rest
  later. You will absorb `collections`, `itertools`, `datetime` and `re` by
  needing them.
- **Day 20 (concurrency)** is the most advanced and least immediately necessary
  day. Read it for the mental model (threads vs processes vs async, and the GIL),
  skip the hard exercises, revisit after Day 21.
- **Project days (07, 14, 21)** can spill over a day. Get the early milestones
  green, ship something that runs, and treat the stretch goals as optional.

If you are more than two days behind, do not try to catch up by skimming. Cut
Day 17 and Day 20 to half a day each, and keep the load-bearing days intact.

## The rest of the documentation

- [SETUP.md](SETUP.md) — installing Python, virtualenvs, editors, and a
  symptom-to-fix troubleshooting table. Read this first if `python3 --version`
  did not work.
- [SYLLABUS.md](SYLLABUS.md) — the day-by-day plan with concepts, capabilities and
  dependencies. Also printed by `python check.py plan`.
- [CHEATSHEET.md](CHEATSHEET.md) — dense syntax reference for the whole course.
  Optimised for lookup while you are writing code.
- [reference/glossary.md](reference/glossary.md) — every term the course uses,
  defined plainly, with the day it is taught.
- [reference/error_messages.md](reference/error_messages.md) — what Python's error
  messages actually mean, with minimal reproductions and fixes.
- [reference/debugging_playbook.md](reference/debugging_playbook.md) — the
  repeatable process for getting unstuck, plus how to ask a good question.
- [reference/whats_next.md](reference/whats_next.md) — where to go after Day 21,
  by track, with concrete next steps.

## Requirements

Python 3.10 or newer and `pytest`. That is the whole hard dependency list for
Days 1-18. Days 19-21 add `requests` and `httpx`; Day 18's tooling section and a
Day 21 stretch goal use `ruff`, `black`, `mypy` and `rich`. Install them when the
lesson tells you to, not before:

```bash
python -m pip install pytest                # now
python -m pip install requests httpx        # before Day 19
python -m pip install ruff black mypy rich  # before Day 18's tooling section
```
