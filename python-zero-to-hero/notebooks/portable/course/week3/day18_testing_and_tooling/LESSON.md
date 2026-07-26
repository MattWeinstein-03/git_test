# Day 18 — Testing and Tooling

> **Time:** ~4 hours  |  **Prerequisites:** Day 17

## What you'll be able to do after today
- Justify testing in money and time, not in virtue, and decide what not to test.
- Write pytest tests with plain `assert`, `pytest.raises`, fixtures, and `parametrize`.
- Use `tmp_path`, `monkeypatch` and `capsys` to test code that touches files, the environment, and stdout.
- Drive a small feature with red-green-refactor and feel why the order matters.
- Read a coverage report without being fooled by it.
- Configure `ruff`, `black`, `mypy` and pre-commit in one `pyproject.toml` and know what each one catches.
- Write tests that will still be useful after you refactor the implementation.

## Why this matters

You have been running `python check.py` for seventeen days. Those are tests
someone wrote to grade you. Today you cross to the other side of that line,
because the difference between a hobbyist and a professional is not knowing more
syntax — it is being able to change a 20,000-line codebase without fear.

The concrete failure you are avoiding: you fix a bug on Friday, and on Monday
three other things are broken and nobody notices for a week. Every change to
untested code is a bet that you fully understood the code. Tests are how you stop
betting. They are also how you stop *manually* re-checking behaviour, which is
the expensive, boring thing you would otherwise do dozens of times per day.

---

## 1. The economic argument

Ignore "testing is good practice". Here is the arithmetic.

A bug costs more the later it is found:

| Found | Typical cost to fix |
|---|---|
| While you type it (type checker, linter) | seconds |
| Test run on your machine | a minute |
| CI, before merge | 10 minutes, and nobody else is affected |
| Code review | 30 minutes of two people's time |
| Staging | hours, plus a redeploy |
| Production | hours to days, plus wrong data to clean up, plus lost trust |

The ratio between the first and last row is commonly cited at 10x–100x. You do
not need the exact multiplier; you need to notice it is not 1x.

Second piece of arithmetic: **how often will I run this check?** A manual check
that takes 30 seconds, done 20 times while you build a feature, is 10 minutes,
and you will get bored and stop doing it — which is the real cost, because you
stop noticing regressions. Automating it costs 3 minutes once and then 0.2
seconds forever, and it keeps working when you are on holiday.

Third: tests are the only thing that makes refactoring possible. Without them,
"tidy this up" is indistinguishable from "risk breaking it", so codebases calcify
and every change gets more expensive. Teams without tests do not move slowly
because they are bad; they move slowly because they cannot verify anything
cheaply.

### What not to test

Testing is an investment with diminishing returns. Do not test:

- **Third-party code.** You are not testing `requests`. Test *your* use of it.
- **Trivial glue.** A one-line getter with no logic. If it breaks, everything
  breaks loudly.
- **Exact log strings or `print` output**, unless output is the product.
- **Implementation details** — private helpers, call counts, internal ordering.
  These tests fail every refactor without catching a single bug, and they teach
  the team that failing tests are normal. That is the worst outcome.
- **Things the type checker already proves.** `mypy` catches "you passed a str
  where an int was expected" for free.

Do test: branches (`if`/`except`), boundaries (0, 1, empty, one-off-the-end),
anything you got wrong once, and every bug you fix — write the failing test
first, then fix it, and it can never come back silently.

---

## 2. pytest structure

A test is a function whose name starts with `test_`, in a file named
`test_*.py`, that asserts something. There is no class to inherit, no
`assertEqual`, no boilerplate.

```python
# test_math_utils.py
from math_utils import median


def test_median_of_odd_count():
    assert median([3, 1, 2]) == 2


def test_median_of_even_count_averages_the_middle_two():
    assert median([1, 2, 3, 4]) == 2.5
```

Run it:

```bash
python -m pytest                  # everything it can discover
python -m pytest -q               # quiet: one character per test
python -m pytest -v               # verbose: one line per test with its name
python -m pytest test_math.py::test_median_of_odd_count    # exactly one test
python -m pytest -k median        # every test whose name contains "median"
python -m pytest -x               # stop at the first failure
python -m pytest --lf             # re-run only last failures
python -m pytest -s               # do not capture stdout (see your prints)
```

Structure each test in three beats — arrange, act, assert:

```python
def test_discount_applies_to_total():
    basket = [Item("book", 10.0), Item("pen", 2.0)]      # arrange
    total = checkout(basket, discount=0.1)               # act
    assert total == 10.8                                 # assert
```

Naming: `test_<thing>_<behaviour>`. When it fails, you should know what broke
from the name alone, without reading the body. `test_median` is a bad name;
`test_median_raises_on_empty_input` is a good one.

One logical behaviour per test. Five assertions about one call is fine; testing
three unrelated behaviours in one function means a failure tells you less and
stops at the first problem.

---

## 3. Plain `assert`, and why pytest's is special

`assert expression` raises `AssertionError` when the expression is falsy. Python
does that; pytest adds **assertion rewriting**, which reports the actual values:

```python
def test_lists_match():
    got = [1, 2, 4]
    assert got == [1, 2, 3]
```

```
E       assert [1, 2, 4] == [1, 2, 3]
E         At index 2 diff: 4 != 3
```

You get that for free from `==` on lists, dicts, sets and strings. Add a message
when the comparison is not self-explanatory:

```python
assert total == 10.8, f"discount applied wrongly to {basket!r}"
```

Two rules:

- **Compare floats with tolerance.** `0.1 + 0.2 == 0.3` is `False`. Use
  `pytest.approx`: `assert value == pytest.approx(0.3)`, or
  `pytest.approx(0.3, abs=1e-9)`.
- **Never `assert True` / `assert function_ran`.** If you cannot state the
  expected value, you do not yet know what the function should do.

---

## 4. `pytest.raises`: testing failure

Error paths are where bugs hide, because nobody exercises them by hand.

```python
import pytest


def test_median_rejects_empty_input():
    with pytest.raises(ValueError):
        median([])
```

If the block does not raise, the test fails. Match the message when the
distinction matters, and capture the exception when you need to inspect it:

```python
def test_median_error_message_mentions_empty():
    with pytest.raises(ValueError, match="empty"):     # match is a regex search
        median([])


def test_error_carries_the_offending_value():
    with pytest.raises(ValueError) as info:
        parse_bool("maybe")
    assert "maybe" in str(info.value)
```

> **Gotcha:** put exactly one call inside the `with` block. Two calls, and you
> cannot tell which raised — and if the first raises, the second never runs.
>
> **Gotcha 2:** `pytest.raises(Exception)` passes for almost any bug, including
> `AttributeError` from a typo in your test. Name the specific exception.

`pytest.warns` does the same job for warnings.

---

## 5. Fixtures and scope

A fixture is a function that builds something a test needs. Ask for it by putting
its name in the test's parameter list:

```python
import pytest


@pytest.fixture
def basket():
    """A basket with two items."""
    return [Item("book", 10.0), Item("pen", 2.0)]


def test_total_without_discount(basket):
    assert checkout(basket) == 12.0


def test_total_with_discount(basket):
    assert checkout(basket, discount=0.5) == 6.0
```

Each test gets a **fresh** `basket`, because the fixture function runs again for
each one. That isolation is the point: tests that share mutable state fail in
mysterious, order-dependent ways.

Fixtures that need cleanup use `yield`:

```python
@pytest.fixture
def db_connection():
    connection = sqlite3.connect(":memory:")
    yield connection            # the test runs here
    connection.close()          # runs afterwards, even if the test failed
```

`scope` controls how often a fixture is rebuilt:

| Scope | Rebuilt |
|---|---|
| `function` (default) | for every test — the safe choice |
| `class` | once per test class |
| `module` | once per test file |
| `session` | once per pytest run |

Wider scope is faster and more dangerous: a `session` fixture that returns a
mutable object lets test 3 corrupt test 40, and the failure looks impossible.
Use wide scopes only for expensive, read-only things.

Fixtures can use other fixtures, and `conftest.py` shares them across files
without imports. That is exactly what this course does: the `day` fixture in the
root `conftest.py` loads your `exercises.py` and hands the module to every test.

---

## 6. `@pytest.mark.parametrize`

Same logic, many cases. Instead of six near-identical tests:

```python
import pytest


@pytest.mark.parametrize(
    "text, expected",
    [
        ("yes", True),
        ("YES", True),
        ("true", True),
        ("no", False),
        ("0", False),
    ],
)
def test_parse_bool(text, expected):
    assert parse_bool(text) == expected
```

That is five separate tests. Each gets its own name in the output
(`test_parse_bool[yes-True]`), each passes or fails independently, and adding a
case is one line. Compare it to a `for` loop inside one test, which stops at the
first failure and hides which case broke.

Combine with fixtures freely — parameters and fixtures can appear in the same
signature, in any order:

```python
@pytest.mark.parametrize("width, expected_lines", [(5, 2), (20, 1)])
def test_wrap_line_count(sample_text, width, expected_lines):
    assert len(word_wrap(sample_text, width)) == expected_lines
```

Stacking two `parametrize` decorators multiplies the cases (2 x 3 = 6 tests).
`pytest.param(..., id="empty string")` names an ugly case readably, and
`pytest.param(..., marks=pytest.mark.xfail)` records a known bug without a
failing suite.

> **Gotcha:** never build parametrize values from the code under test —
> `@pytest.mark.parametrize("case", generate_cases())` means a bug in
> `generate_cases` silently reduces you to zero tests, and a green run proves
> nothing. Parameter lists are literals.
>
> That is also why this course's own graded tests never parametrize over the
> learner's module: collection happens before your `exercises.py` is loaded, so
> the values would have to come from somewhere else anyway. The tests you write
> yourself today are free to parametrize over literals.

---

## 7. `tmp_path`: testing code that touches files

Never write test files into your project directory: parallel runs collide,
failures leave litter, and CI has a different working directory. `tmp_path` is a
per-test `Path` to an empty directory that pytest creates and cleans up.

```python
def test_summarise_file_counts_lines(tmp_path):
    target = tmp_path / "data.txt"                  # does not exist yet
    target.write_text("a\nb\nc\n", encoding="utf-8")

    summary = summarise_file(target)

    assert summary["lines"] == 3
```

`tmp_path_factory` gives you a session-scoped version. `tmp_path` also lets you
test the *absence* of a file (`assert not (tmp_path / "out.csv").exists()`) and
error handling on unreadable paths.

For SQLite, this is how you get a real database with no cleanup code:
`sqlite3.connect(tmp_path / "test.db")`. Day 19 and 21 use exactly that.

---

## 8. `monkeypatch`: replacing the world, temporarily

`monkeypatch` sets attributes, dict entries, and environment variables, and undoes
every change when the test ends.

```python
def test_get_setting_reads_environment(monkeypatch):
    monkeypatch.setenv("APP_LIMIT", "42")
    assert get_setting("APP_LIMIT", "10") == "42"


def test_get_setting_falls_back_when_unset(monkeypatch):
    monkeypatch.delenv("APP_LIMIT", raising=False)
    assert get_setting("APP_LIMIT", "10") == "10"
```

Without `monkeypatch`, that first test would leak `APP_LIMIT` into every later
test — the classic order-dependent failure.

The other three uses:

```python
monkeypatch.setattr(module, "CONSTANT", 5)                # replace an attribute
monkeypatch.setattr(time, "sleep", lambda seconds: None)  # make a test instant
monkeypatch.chdir(tmp_path)                               # change directory safely
```

Replacing `time.sleep` is the standard trick for testing retry logic: the retry
code is unchanged, the test takes microseconds instead of seven seconds.

> **Gotcha:** patch where the name is *used*, not where it is defined. If
> `my_app.fetch` does `from time import sleep`, then `my_app.fetch.sleep` is the
> name to patch; patching `time.sleep` afterwards has no effect on the reference
> already imported.

---

## 9. `capsys`: testing output

Only for code whose job is printing — a CLI's output, a formatted report.

```python
def test_print_table_aligns_columns(capsys):
    print_table([("ada", 3), ("bo", 12)])

    output = capsys.readouterr().out
    lines = output.strip().splitlines()
    assert lines == ["ada  3", "bo   12"]      # names padded to the widest name
```

`readouterr()` returns a `(out, err)` pair and resets the capture, so call it
once and keep the result. `capfd` captures at the file-descriptor level, which
catches output from subprocesses too.

Prefer functions that **return** strings over functions that print them: the
return value is trivially testable and the printing happens in one place at the
edge of your program. `capsys` is for that edge.

---

## 10. A real red-green-refactor walkthrough

TDD in three steps, repeated: write a failing test (**red**), write the least code
that passes it (**green**), then improve the code with the test protecting you
(**refactor**).

Feature: run-length encoding. `"aaabbc"` becomes `"a3b2c1"`.

### Red

```python
# test_rle.py
from rle import rle_encode


def test_encode_empty_string():
    assert rle_encode("") == ""
```

```
E   ImportError: cannot import name 'rle_encode' from 'rle'
```

That failure is progress: the test is running and it is telling the truth.

### Green

```python
# rle.py
def rle_encode(text: str) -> str:
    return ""
```

Passing. That implementation is obviously a lie, and that is fine — the next test
is what forces honesty.

### Red

```python
def test_encode_single_character():
    assert rle_encode("a") == "a1"
```

Fails: got `""`, want `"a1"`.

### Green

```python
def rle_encode(text: str) -> str:
    if not text:
        return ""
    return f"{text[0]}1"
```

### Red

```python
def test_encode_repeated_characters():
    assert rle_encode("aaa") == "a3"


def test_encode_runs_of_different_characters():
    assert rle_encode("aaabbc") == "a3b2c1"
```

Both fail. Faking is no longer cheaper than solving, which is precisely the
signal TDD is designed to produce.

### Green

```python
def rle_encode(text: str) -> str:
    if not text:
        return ""
    result = ""
    current = text[0]
    count = 0
    for char in text:
        if char == current:
            count += 1
        else:
            result += current + str(count)
            current = char
            count = 1
    result += current + str(count)
    return result
```

Four tests pass. The code works and is ugly: string concatenation in a loop, a
duplicated flush, three loop variables.

### Refactor

```python
from itertools import groupby


def rle_encode(text: str) -> str:
    """Encode runs of repeated characters: 'aaabbc' -> 'a3b2c1'."""
    return "".join(f"{char}{len(list(group))}" for char, group in groupby(text))
```

Same four tests, still green, in one line — using Day 17's `groupby`, whose
consecutive-runs behaviour is exactly right here. Note what happened: the
refactor was safe *because* the tests existed, and the tests did not change
because they described behaviour, not implementation. If your tests had asserted
on an internal `result` variable, this refactor would have "broken" them.

Next, `rle_decode`, and one property worth asserting:

```python
def test_decode_round_trips():
    for text in ["", "a", "aaabbc", "xyz"]:
        assert rle_decode(rle_encode(text)) == text
```

A round-trip test is worth ten example tests, because it states a *law* the pair
must obey rather than a single data point.

### When not to TDD

TDD needs a known specification. When you are exploring — "what shape is this
API's response?" — write throwaway code first, learn, then write the tests and
the real implementation. TDD is a tool for building known things carefully, not a
religion.

---

## 11. Coverage, and how it is misused

```bash
python -m pip install pytest-cov
python -m pytest --cov=my_package --cov-report=term-missing
```

```
Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
my_package/etl.py        84      7    92%   45-48, 91, 103-104
```

Coverage tells you which lines **ran** during the test suite. That is genuinely
useful in one direction: the "Missing" column shows code no test touches, which
is where undiscovered bugs live. Look at those lines and ask whether they matter.

It is misused in the other direction. Coverage says nothing about whether your
assertions are any good:

```python
def test_everything_covered():
    process_order(sample_order())      # 100% coverage of process_order
```

That test asserts nothing. It fails only if the code raises. You can hit 100%
coverage with a suite that verifies nothing at all — and teams with a 100%
coverage target end up writing exactly those tests, because the number is what is
measured.

Sane practice:

- Use the "Missing" column as a to-do list of unexercised branches.
- Set a floor (say 70–80%) to catch untested new modules, not a target of 100%.
- Never let coverage be the metric a team is judged on. It measures execution,
  not verification.
- Prefer `--cov-branch`: line coverage counts an `if` as covered when only the
  true side ran.

The honest question is not "what percentage?" but "if I broke this on purpose,
would a test fail?" That is called mutation testing, and it is what coverage
pretends to measure.

---

## 12. Mocking, judiciously

A mock is a stand-in that records how it was called. Use it when the real thing is
slow, unavailable, non-deterministic, or has side effects you do not want (sending
email, charging cards, calling an API).

```python
from unittest.mock import MagicMock


def test_notify_sends_one_message():
    sender = MagicMock()

    notify(sender, "hello")

    sender.send.assert_called_once_with("hello")
```

`unittest.mock.patch` can replace things by name, and `pytest-mock` wraps it in a
`mocker` fixture.

The costs, which are real:

1. **Mocks test your assumptions, not reality.** If the API returns
   `{"data": ...}` and your mock returns `{"result": ...}`, your tests pass and
   production fails. Mocks freeze a snapshot of a contract you do not control.
2. **Over-mocked tests test the mock.** If every collaborator is a mock, you have
   asserted that your function calls the functions you wrote it to call. That is
   a tautology; it breaks on every refactor and catches nothing.
3. **`MagicMock` accepts everything.** `mock.no_such_method()` succeeds and
   returns another mock, so typos and removed methods go unnoticed. Use
   `autospec=True` or `create_autospec` to make the mock match the real signature.

The alternative, which is almost always better: **dependency injection**. Pass
the collaborator in as an argument, and pass a small honest fake in your tests.

```python
def fetch_all(pages: int, fetch=requests.get):     # injected, with a real default
    return [fetch(f"/items?page={n}").json() for n in range(pages)]


def test_fetch_all_reads_every_page():
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return SimpleNamespace(json=lambda: {"page": url})

    assert len(fetch_all(2, fetch=fake_fetch)) == 2
    assert calls == ["/items?page=0", "/items?page=1"]
```

No patching, no magic, and the seam is visible in the signature. This is the
pattern Day 19 and the Day 21 project are built on, and it is why their tests
never touch the network.

---

## 13. Tooling: ruff, black, mypy, pre-commit

Four tools, four different jobs. None of them replaces tests.

### `ruff` — the linter (and now formatter)

Catches unused imports, undefined names, shadowed variables, mutable default
arguments, `except:` with no exception class, and hundreds more, in milliseconds.

```bash
python -m pip install ruff
ruff check .            # report problems
ruff check --fix .      # fix the mechanical ones
ruff format .           # format (black-compatible)
```

### `black` — the formatter

Reformats your code to one canonical style. The point is not that black's style is
optimal; it is that **the argument ends**. No more review comments about line
breaks, no more diffs full of whitespace.

```bash
python -m pip install black
black .                 # rewrite files
black --check --diff .  # CI mode: fail if anything is unformatted
```

### `mypy` — the type checker

Reads your type hints and finds contradictions without running anything.

```bash
python -m pip install mypy
mypy my_package
```

```
etl.py:41: error: Argument 1 to "median" has incompatible type "str"; expected "list[float]"
etl.py:88: error: Item "None" of "Path | None" has no attribute "read_text"
```

That second one is the valuable class of error: the `None` you forgot to handle.
Start lenient on an existing codebase and tighten gradually (`--strict` on new
modules first).

### `pre-commit` — running them automatically

A git hook manager. Checks run on `git commit`, on changed files only.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
```

```bash
python -m pip install pre-commit
pre-commit install          # once per clone; wires up .git/hooks
pre-commit run --all-files  # run everything now
```

Do not put the full test suite in a pre-commit hook if it takes more than a few
seconds; people start using `--no-verify` and then the hooks are theatre. Fast
checks locally, full suite in CI.

### `pyproject.toml` — one file to configure them all

```toml
[project]
name = "my-package"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["requests>=2.31"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov", "ruff", "black", "mypy"]

[tool.pytest.ini_options]
addopts = "-q --tb=short"
testpaths = ["tests"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]      # errors, pyflakes, imports, upgrades, bugbear, simplify

[tool.black]
line-length = 88

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
warn_unused_ignores = true
```

`pyproject.toml` is the modern, standard home for both packaging metadata and
tool settings. This course's own root `pyproject.toml` is a working example —
read it.

The order to adopt these on a real project: **formatter first** (mechanical, no
arguments), **linter second** (catches real bugs, mostly auto-fixable), **type
checker third** (highest value, most work), **pre-commit last** (once the others
are quiet, so nobody's first commit is a wall of errors).

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `assert 0.1 + 0.2 == 0.3` | Fails; floats are binary approximations | `pytest.approx(0.3)` |
| Two calls inside one `pytest.raises` | Passing test that proves nothing | One call per `raises` block |
| `pytest.raises(Exception)` | Passes on a typo in your own test | Name the specific exception |
| Session-scoped mutable fixture | Tests pass alone, fail together | Default `function` scope |
| Writing test files into the repo | Litter, and failures in CI | `tmp_path` |
| `os.environ["X"] = "1"` in a test | Later tests behave strangely | `monkeypatch.setenv` |
| Patching where a name is defined | Patch appears to do nothing | Patch where it is *used* |
| Asserting on log/print text | Breaks on every wording change | Assert on return values |
| Testing private helpers | Every refactor is red | Test the public behaviour |
| Parametrizing over generated values | Silently zero tests | Literal parameter lists |
| Chasing 100% coverage | Assertion-free tests, false confidence | Use "Missing" as a to-do list |
| `MagicMock` everywhere | Green tests, broken production | Inject a small honest fake |
| Tests depending on each other's order | "Works on my machine" | Fresh fixtures, no shared state |

---

## Mental model

Tests are a **ratchet**. Each one you write locks in a behaviour so it cannot
silently slip back.

```
 confidence
     ^
     |                                        ,--- refactor freely here
     |                            ,-----------'
     |                ,-----------'   each test = one tooth on the ratchet
     |    ,-----------'
     |----'
     +----------------------------------------------> tests written

 Without the ratchet, every change can slide you back to zero.
```

And the tool stack is a **series of sieves**, coarse to fine, each catching what
the previous one cannot:

```
  black   -> formatting noise            (no bugs, but no arguments either)
  ruff    -> dead code, obvious mistakes (seconds)
  mypy    -> impossible types, None bugs (no execution needed)
  pytest  -> wrong behaviour             (the only one that runs your code)
  review  -> wrong design                (the only one that needs a human)
```

Anything that reaches production got through all five.

---

## Practice

1. Run the demo, which is itself a small test suite plus a live TDD walkthrough:
   ```bash
   python course/week3/day18_testing_and_tooling/examples.py
   ```
2. `exercises.py` has ten exercises, and today they come in two flavours:
   - **Implementations** (1–5, 8–10): write the function; the graded tests check
     behaviour including edge cases the docstring hints at but does not spell out
     exhaustively. Read failures carefully; the failure message *is* the spec.
   - **Your own tests** (6–7): you write the checking logic. `find_median_bugs`
     and `find_wrap_bugs` receive a candidate implementation and must return a
     list of the problems they find. They are graded by being handed a correct
     implementation (your checker must return an empty list) and several subtly
     broken ones (your checker must catch every single one). This is the closest
     thing to being graded on test quality.
3. Also write a real pytest file of your own for practice — put it in
   `my_tests.py` in the day folder and run
   `python -m pytest course/week3/day18_testing_and_tooling/my_tests.py`. Use
   `parametrize`, `tmp_path` and `monkeypatch` at least once each. Nothing grades
   it; do it anyway, because writing tests you were not told to write is the
   actual skill.
4. Grade from the course root:
   ```bash
   python check.py day18
   ```
5. Optional but recommended: install the tools and point them at your own code.
   ```bash
   python -m pip install ruff black mypy
   ruff check course/week3/day18_testing_and_tooling/exercises.py
   black --check --diff course/week3/day18_testing_and_tooling/exercises.py
   mypy course/week3/day18_testing_and_tooling/exercises.py
   ```

---

## Recall check

1. Give the economic argument for automated tests in two sentences, without using
   the words "good practice".
2. Name four things you should not write tests for.
3. Why does pytest's `assert` give better failure output than plain `assert`?
4. What is wrong with putting two calls inside one `pytest.raises` block?
5. When is a `session`-scoped fixture dangerous?
6. What does `parametrize` give you that a `for` loop inside one test does not?
7. Which fixture do you use for files, which for environment variables, which for
   stdout?
8. In red-green-refactor, why must the test fail first?
9. Explain how a test suite can have 100% coverage and catch nothing.
10. Give two concrete costs of mocking, and the alternative that avoids both.
11. What does each of ruff, black and mypy catch that the others do not?

<details>
<summary>Answers</summary>

1. A bug found while typing costs seconds; the same bug found in production costs
   hours plus corrupted data plus lost trust. Tests move discovery to the cheap
   end and make the check repeatable at near-zero marginal cost, which is also
   the only thing that makes refactoring safe.
2. Third-party libraries, trivial glue with no logic, exact log or print wording,
   private implementation details, and anything a type checker already proves.
3. Assertion rewriting: pytest inspects the expression and reports the actual
   operand values and, for collections, the first differing element — instead of
   a bare `AssertionError`.
4. If the first call raises, the second never runs, and a passing test cannot tell
   you which call raised. It can hide a completely untested code path.
5. When it returns something mutable. One test can modify it and change the
   behaviour of every later test, producing failures that depend on run order and
   disappear when the test runs alone.
6. Independent pass/fail per case, a distinct test name per case, all cases run
   even after one fails, and one-line additions. A loop stops at the first
   failure and reports only one case.
7. `tmp_path` for files and directories, `monkeypatch` for environment variables
   (and attributes), `capsys` for captured stdout/stderr.
8. Seeing it fail proves the test actually exercises the new behaviour and can
   detect its absence. A test that never failed might be asserting nothing, or
   testing a different code path than you think.
9. Coverage measures which lines executed, not whether anything was verified. A
   test that calls every function and asserts nothing achieves full coverage and
   only fails if the code raises.
10. Mocks encode your assumption about a contract you do not control, so they can
    pass while production breaks; and heavily mocked tests assert that your code
    calls the functions you wrote, which breaks on refactors and catches no bugs.
    Dependency injection with a small hand-written fake avoids both.
11. `black` normalises formatting (no bugs, ends style arguments); `ruff` finds
    dead code, unused imports, undefined names and known bug patterns without
    running the code; `mypy` proves type contradictions such as unhandled `None`
    that neither of the others can see. None of them checks behaviour — that is
    pytest.

</details>
