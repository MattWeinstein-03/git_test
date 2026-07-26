===============================================================================
PYTHON ZERO TO HERO - 21 DAY SYLLABUS
===============================================================================

21 days, ~4-5 focused hours each. Three weeks, three projects. Each day:
read LESSON.md, run examples.py, fill in exercises.py, run `python check.py dayNN`
until green, then read solutions.py and compare it to what you wrote.

Days are strictly cumulative. Nothing is taught before it is needed, and nothing
later assumes a day you have not finished. If you fall behind, see "When you fall
behind" in README.md - Days 08, 09, 12, 15 and 18 are load-bearing; Days 17 and 20
can be skimmed and revisited.

Total: 21 lessons, 6-10 graded exercises per teaching day, 3 milestone-graded
projects.


===============================================================================
WEEK 1 - THE CORE LANGUAGE
===============================================================================

Theme: the irreducible core. Values, decisions, repetition, and the four
collection types that hold almost all data you will ever handle. No functions
yet, no files, no classes - you are learning to think in steps and to be precise.

By Sunday you can: write a 100-line script that reads input, makes decisions,
loops over data, counts and groups it with lists, tuples, dicts and sets, and
prints a formatted report - and you can debug it when it does not work.

-------------------------------------------------------------------------------
Day 01 - Getting Started                                            ~4 hours
-------------------------------------------------------------------------------
Concepts:    variables, int / float / str / bool, print, input, type(), comments
Capability:  You can run a Python file, store values in named variables, read
             input from the user, print results, and say what type any value is.
Unlocks:     Everything. Every later day is variables and function calls.
Watch for:   `input()` always gives you a string, even when the user types 42.

-------------------------------------------------------------------------------
Day 02 - Numbers and Strings                                        ~4 hours
-------------------------------------------------------------------------------
Concepts:    arithmetic (+ - * / // % **), string methods, slicing, f-strings,
             casting with int() / float() / str()
Capability:  You can compute with numbers, transform and inspect text, extract
             substrings by position, and format output precisely.
Unlocks:     Day 07's text toolkit is built almost entirely from these methods.
             f-strings are how you print for the remaining 19 days.
Watch for:   / always gives a float; // floors; strings are immutable, so
             s.upper() returns a new string rather than changing s.

-------------------------------------------------------------------------------
Day 03 - Conditionals                                               ~4 hours
-------------------------------------------------------------------------------
Concepts:    if / elif / else, comparison operators, and / or / not, truthiness
Capability:  You can make your program take different paths based on data, and
             you can combine several conditions correctly.
Unlocks:     Filtering inside loops (Day 04), guard clauses in functions (Day 08),
             except-branch decisions (Day 09).
Watch for:   = assigns, == compares. Empty string, 0, empty list and None are all
             falsy - that is a feature you will use constantly.

-------------------------------------------------------------------------------
Day 04 - Loops                                                      ~4 hours
-------------------------------------------------------------------------------
Concepts:    while, for, range, break, continue, accumulator patterns,
             nested loops
Capability:  You can repeat work over a range or a sequence, accumulate a running
             total or a built-up result, and stop early when a condition is met.
Unlocks:     Every data-processing task in the course. Comprehensions (Day 15) are
             a shorthand for loops you must first be able to write longhand.
Watch for:   range(1, 5) stops at 4. Modifying a list while looping over it will
             bite you.

-------------------------------------------------------------------------------
Day 05 - Lists and Tuples                                           ~4 hours
-------------------------------------------------------------------------------
Concepts:    list, tuple, indexing, slicing, list methods (append, extend, insert,
             pop, remove, sort, reverse), sorted, enumerate, zip
Capability:  You can hold ordered collections of values, index and slice them,
             sort them by a key, and iterate with the index or in parallel.
Unlocks:     Project 1, and the shape of nearly all data you will process later.
Watch for:   list.sort() mutates and returns None; sorted(list) returns a new
             list. Tuples cannot be changed after creation - that is the point.

-------------------------------------------------------------------------------
Day 06 - Dicts and Sets                                             ~4 hours
-------------------------------------------------------------------------------
Concepts:    dict, set, counting and grouping patterns, .get, .items, .keys,
             .values, membership tests
Capability:  You can map keys to values, count occurrences, group records by a
             field, and de-duplicate or intersect collections fast.
Unlocks:     Project 1's word frequency work, JSON handling (Day 10), object
             attributes (Day 12), collections.Counter (Day 17).
Watch for:   d[missing] raises KeyError; d.get(missing) returns None. Sets have no
             order, so do not rely on iteration order.

-------------------------------------------------------------------------------
Day 07 - PROJECT 1: Text Toolkit                                    ~5 hours
-------------------------------------------------------------------------------
Concepts:    consolidation of Days 01-06. No new syntax.
Capability:  You can build a multi-part program from a written brief, staged in
             independently testable milestones, using only core-language tools.
Unlocks:     Proof that Week 1 is real knowledge and not recognition. Graded
             milestone by milestone (test_m1_..., test_m2_...), so partial
             progress is visible.
Watch for:   Read the whole brief before writing anything. Get M1 green before
             starting M2.


===============================================================================
WEEK 2 - STRUCTURING PROGRAMS
===============================================================================

Theme: going from scripts to software. Functions, error handling, persistence,
modules and classes - the four things that let a program grow past 200 lines
without collapsing.

By Sunday you can: design a program as a set of named functions across several
modules, handle failure deliberately instead of crashing, read and write text,
CSV and JSON files, model your domain with classes and dataclasses, and set up an
isolated environment for a project.

-------------------------------------------------------------------------------
Day 08 - Functions                                                  ~5 hours
-------------------------------------------------------------------------------
Concepts:    def, parameters, default arguments, *args / **kwargs, return, scope
             (local vs global), docstrings, type hints
Capability:  You can factor repeated logic into named functions with clear inputs
             and outputs, document them, and annotate their types.
Unlocks:     Every remaining day. LOAD-BEARING - do not compress this day.
Watch for:   A function without an explicit return gives you None. Mutable default
             arguments (def f(x=[])) are a classic trap.

-------------------------------------------------------------------------------
Day 09 - Errors and Debugging                                       ~5 hours
-------------------------------------------------------------------------------
Concepts:    exceptions, try / except / else / finally, raise, reading tracebacks,
             assert, debugging strategy, pdb / breakpoint()
Capability:  You can read a traceback and locate the real cause, handle expected
             failures, raise meaningful errors of your own, and step through code
             in a debugger instead of guessing.
Unlocks:     File I/O (Day 10), API calls (Day 19) and testing (Day 18) all depend
             on handling failure. LOAD-BEARING - this is the day you stop being
             stuck for hours.
Watch for:   Bare `except:` hides bugs; catch the specific exception. See
             reference/error_messages.md and reference/debugging_playbook.md.

-------------------------------------------------------------------------------
Day 10 - Files and Data                                             ~5 hours
-------------------------------------------------------------------------------
Concepts:    pathlib, open() with `with`, read vs write vs append modes,
             text vs bytes, encodings, csv module, json module
Capability:  You can read and write files safely, build portable paths, and move
             data in and out of CSV and JSON.
Unlocks:     Project 2's persistence, Day 19's API payloads, Day 21's pipeline.
Watch for:   Always use `with open(...)`. Always pass encoding="utf-8". Opening a
             file in "w" mode erases it immediately.

-------------------------------------------------------------------------------
Day 11 - Modules and Environments                                   ~4 hours
-------------------------------------------------------------------------------
Concepts:    modules, packages, __init__.py, import forms, sys.path basics,
             virtual environments (venv), pip, requirements.txt
Capability:  You can split code across files and import between them, and you can
             create an isolated environment and install dependencies into it.
Unlocks:     Project 2's multi-file structure, installing requests (Day 19), and
             every real project you touch after this course.
Watch for:   `if __name__ == "__main__":` is about whether a file is run or
             imported. A forgotten `pip install` inside an inactive venv is the
             most common cause of ModuleNotFoundError.

-------------------------------------------------------------------------------
Day 12 - Classes                                                    ~5 hours
-------------------------------------------------------------------------------
Concepts:    class, __init__, instance attributes, methods, self, __repr__,
             dataclasses
Capability:  You can define your own types that bundle data with the operations
             on that data, and print them usefully while debugging.
Unlocks:     Day 13, Project 2's domain model, Day 21's pipeline stages.
             LOAD-BEARING.
Watch for:   `self` is the instance, and it is always the first parameter. Class
             attributes are shared by all instances; instance attributes are not.

-------------------------------------------------------------------------------
Day 13 - OOP in Practice                                            ~5 hours
-------------------------------------------------------------------------------
Concepts:    inheritance, composition, dunder methods, properties,
             classmethod / staticmethod, and when NOT to use OOP
Capability:  You can choose between inheritance and composition, add operator and
             protocol behaviour with dunders, expose computed values as
             attributes, and recognise when a plain function is the better answer.
Unlocks:     Reading other people's code - most real Python libraries are built
             this way.
Watch for:   Inheritance is for "is-a", composition for "has-a". Deep hierarchies
             are a smell, not an achievement.

-------------------------------------------------------------------------------
Day 14 - PROJECT 2: Expense Tracker                                 ~5 hours
-------------------------------------------------------------------------------
Concepts:    consolidation of Days 01-13. No new syntax.
Capability:  You can build a persistent, multi-module application with a domain
             model, file storage, error handling and a command interface, from a
             written brief.
Unlocks:     The first project you can show someone. Graded milestone by
             milestone. A README.md in the day folder explains how to run it.
Watch for:   Design the data model before writing code. Persist early - a tracker
             that forgets everything on exit is not finished.


===============================================================================
WEEK 3 - REAL-WORLD PYTHON
===============================================================================

Theme: the tools that separate someone who knows Python syntax from someone who
ships Python. Idiomatic data transformation, the standard library, tests, the
network, databases, and concurrency.

By Sunday you can: write idiomatic Python that other developers recognise as
idiomatic, test it, lint and type-check it, pull data from HTTP APIs, store it in
SQLite, choose the right concurrency model, and assemble all of it into a working
end-to-end pipeline.

-------------------------------------------------------------------------------
Day 15 - Comprehensions and Generators                              ~5 hours
-------------------------------------------------------------------------------
Concepts:    list / dict / set comprehensions, nested and conditional forms,
             generator expressions, yield, the iterator protocol, laziness
Capability:  You can express filter-and-transform pipelines in one readable line,
             and process data larger than memory by streaming it.
Unlocks:     Day 16's functional tools, Day 17's itertools, Day 21's pipeline.
             LOAD-BEARING - this is the biggest single jump in code quality.
Watch for:   A generator is consumed once. Comprehensions that need a comment to
             explain them should be loops.

-------------------------------------------------------------------------------
Day 16 - Decorators and Functional Style                            ~5 hours
-------------------------------------------------------------------------------
Concepts:    lambda, map / filter, closures, first-class functions, decorators,
             functools (wraps, lru_cache, partial, reduce)
Capability:  You can pass functions as values, capture state in closures, and
             write decorators that add logging, timing, caching or retries
             without touching the decorated function.
Unlocks:     Understanding pytest fixtures (Day 18), retry logic (Day 19), and
             roughly every framework you will ever use.
Watch for:   Decorators run at definition time; the wrapper runs at call time.
             Use @functools.wraps or you lose the original function's name.

-------------------------------------------------------------------------------
Day 17 - Standard Library Tour                                      ~4 hours
-------------------------------------------------------------------------------
Concepts:    collections (Counter, defaultdict, namedtuple, deque), itertools,
             datetime, re, argparse, logging
Capability:  You can reach for a batteries-included solution instead of
             reinventing it, build a real command-line interface, and log instead
             of print.
Unlocks:     Day 21's CLI and logging. COMPRESSIBLE - if you are behind, read the
             lesson, run examples.py, do the first few exercises, revisit later.
Watch for:   datetime naive vs aware is a real source of bugs. Regex is powerful
             and unreadable; use it sparingly and comment it.

-------------------------------------------------------------------------------
Day 18 - Testing and Tooling                                        ~5 hours
-------------------------------------------------------------------------------
Concepts:    pytest, assertions, test design, TDD loop, fixtures, parametrize,
             coverage, ruff / black / mypy
Capability:  You can write your own test suite, drive a feature test-first, share
             setup with fixtures, table-drive cases with parametrize, and keep a
             codebase formatted, linted and type-checked.
Unlocks:     Everything you build after this course. LOAD-BEARING - this is the
             most directly employable day in the syllabus. You have been reading
             pytest output since Day 1; today you write it.
Watch for:   Tests that assert nothing pass happily. Test behaviour, not
             implementation details.

-------------------------------------------------------------------------------
Day 19 - APIs and Databases                                         ~5 hours
-------------------------------------------------------------------------------
Concepts:    HTTP request / response model, status codes, requests library,
             consuming REST + JSON, timeouts, retries and backoff, sqlite3,
             SQL basics, parameterised queries
Capability:  You can call a real web API robustly, parse its JSON, and persist
             results in a relational database you query with SQL.
Unlocks:     Day 21's capstone, and the most common category of professional
             Python work. Needs `pip install requests httpx`.
Watch for:   Always set a timeout. Never build SQL by string concatenation - use
             placeholders. Check response.status_code before trusting the body.

-------------------------------------------------------------------------------
Day 20 - Concurrency                                                ~4 hours
-------------------------------------------------------------------------------
Concepts:    threads vs processes vs async, the GIL, concurrent.futures, asyncio
             (async / await, tasks, gather), choosing a model
Capability:  You can tell whether a workload is I/O-bound or CPU-bound and pick
             the right concurrency tool, and you can fetch 100 URLs in the time
             one used to take.
Unlocks:     Day 21's parallel fetch stage. COMPRESSIBLE - read for the mental
             model, skip the hardest exercises, revisit after Day 21.
Watch for:   Threads help with waiting, processes help with computing. Forgetting
             to await a coroutine silently does nothing.

-------------------------------------------------------------------------------
Day 21 - PROJECT 3: Capstone Pipeline                               ~5+ hours
-------------------------------------------------------------------------------
Concepts:    everything from Days 01-20.
Capability:  You can build an end-to-end application: fetch data from an API,
             validate and transform it, store it in SQLite, expose a CLI, log
             what happens, handle failure, and test the whole thing.
Unlocks:     The portfolio piece, and the answer to "what have you built?".
             Graded milestone by milestone, with a README.md in the day folder.
Watch for:   Ship M1 to M3 working before touching stretch goals. A finished
             narrow tool beats an unfinished broad one.


===============================================================================
AFTER DAY 21
===============================================================================

reference/whats_next.md has branching tracks - backend and web APIs, data
analysis, automation and scripting, machine learning - each with an ordered list
of what to learn next, the canonical libraries, and a first portfolio project.

Support material, available from Day 1:
  SETUP.md                          environment, virtualenvs, troubleshooting
  CHEATSHEET.md                     syntax lookup for the whole course
  reference/glossary.md             every term, defined, with the day taught
  reference/error_messages.md       what Python's errors actually mean
  reference/debugging_playbook.md   the process for getting unstuck
  reference/whats_next.md           where to go after Day 21
