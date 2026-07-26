"""Day 18 — runnable demonstrations of pytest, TDD and tooling.

Run it:

    python course/week3/day18_testing_and_tooling/examples.py

This script is unusual: it *generates* a small test suite in a temporary
directory and runs pytest on it in-process, so you can see real pytest output —
green, red, parametrized, and with fixtures — without leaving this file.
Everything is cleaned up at the end.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import sqlite3
import sys
import tempfile
from itertools import groupby
from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock, create_autospec

import pytest

WORKDIR = Path(tempfile.mkdtemp(prefix="pzh_day18_"))


def banner(text: str) -> None:
    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


def run_pytest(*paths: Path, extra: tuple[str, ...] = ()) -> int:
    """Run pytest in-process on the given files and return its exit code.

    `-p no:cacheprovider` keeps pytest from writing a .pytest_cache folder;
    `--rootdir` and `-c` keep it from picking up this course's own config.
    """
    args = [
        *[str(p) for p in paths],
        "-p", "no:cacheprovider",
        "--rootdir", str(WORKDIR),
        "--no-header",
        "-q",
        *extra,
    ]
    return int(pytest.main(args))


# ---------------------------------------------------------------------------
banner("1-2. A real pytest run: plain asserts, naming, arrange-act-assert")
# ---------------------------------------------------------------------------

# The code under test. In a real project this lives in your package.
(WORKDIR / "shop.py").write_text(
    '''
"""A tiny module so the demo has something real to test."""


def checkout(prices, discount=0.0):
    """Total of prices with an optional fractional discount."""
    if not 0.0 <= discount < 1.0:
        raise ValueError(f"discount must be in [0, 1), got {discount}")
    return round(sum(prices) * (1 - discount), 2)
''',
    encoding="utf-8",
)

(WORKDIR / "test_shop_pass.py").write_text(
    '''
import pytest

from shop import checkout


def test_checkout_sums_prices():
    prices = [10.0, 2.0]          # arrange
    total = checkout(prices)      # act
    assert total == 12.0          # assert


def test_checkout_applies_discount():
    assert checkout([10.0, 2.0], discount=0.1) == 10.8


def test_checkout_rejects_impossible_discount():
    with pytest.raises(ValueError, match="discount must be"):
        checkout([1.0], discount=1.5)


def test_checkout_of_empty_basket_is_zero():
    assert checkout([]) == 0


@pytest.mark.parametrize(
    "discount, expected",
    [
        (0.0, 100.0),
        (0.25, 75.0),
        (0.5, 50.0),
        pytest.param(0.99, 1.0, id="almost-free"),
    ],
)
def test_checkout_discount_table(discount, expected):
    assert checkout([100.0], discount=discount) == expected
''',
    encoding="utf-8",
)

print("Running: pytest -q test_shop_pass.py\n")
code = run_pytest(WORKDIR / "test_shop_pass.py")
print("\nexit code:", code, "(0 means every test passed)")
print("Note the four parametrized cases counted as four separate tests.")


# ---------------------------------------------------------------------------
banner("3. What a failure looks like: assertion rewriting")
# ---------------------------------------------------------------------------

(WORKDIR / "test_shop_fail.py").write_text(
    '''
import pytest

from shop import checkout


def test_list_comparison_shows_the_difference():
    got = [1, 2, 4]
    assert got == [1, 2, 3]


def test_float_equality_is_a_trap():
    assert 0.1 + 0.2 == 0.3


def test_float_equality_done_right():
    assert 0.1 + 0.2 == pytest.approx(0.3)


def test_failure_message_helps():
    total = checkout([1.0, 2.0])
    assert total == 4.0, f"3.0 expected; a basket of 1.0 and 2.0 gave {total}"
''',
    encoding="utf-8",
)

print("Running: pytest -q test_shop_fail.py   (three of these fail ON PURPOSE)\n")
code = run_pytest(WORKDIR / "test_shop_fail.py", extra=("--tb=short",))
print("\nexit code:", code, "(non-zero: failures are the point of this section)")
print("Read the output: pytest showed the actual values and the differing index.")


# ---------------------------------------------------------------------------
banner("5. Fixtures: isolation, cleanup, and scope")
# ---------------------------------------------------------------------------

(WORKDIR / "test_fixtures.py").write_text(
    '''
import sqlite3

import pytest


@pytest.fixture
def basket():
    """A FRESH list for every test that asks for it."""
    return [10.0, 2.0]


def test_first_test_mutates_the_basket(basket):
    basket.append(99.0)
    assert len(basket) == 3


def test_second_test_gets_a_clean_basket(basket):
    assert len(basket) == 2, "function-scoped fixtures are rebuilt per test"


@pytest.fixture
def connection():
    """yield-style fixture: everything after `yield` is teardown."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (id INTEGER)")
    yield conn
    conn.close()


def test_database_starts_empty(connection):
    assert connection.execute("SELECT count(*) FROM t").fetchone()[0] == 0


def test_database_is_recreated_each_test(connection):
    connection.execute("INSERT INTO t VALUES (1)")
    assert connection.execute("SELECT count(*) FROM t").fetchone()[0] == 1
''',
    encoding="utf-8",
)

print("Running: pytest -v test_fixtures.py\n")
run_pytest(WORKDIR / "test_fixtures.py", extra=("-v",))


# ---------------------------------------------------------------------------
banner("7-9. tmp_path, monkeypatch and capsys")
# ---------------------------------------------------------------------------

(WORKDIR / "app.py").write_text(
    '''
"""Code that touches files, the environment and stdout - all testable."""

import os
import time
from pathlib import Path


def summarise_file(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    return {"lines": len(lines), "words": sum(len(line.split()) for line in lines)}


def get_setting(name, default):
    return os.environ.get(name, default)


def print_table(rows):
    width = max((len(name) for name, _ in rows), default=0)
    for name, value in rows:
        print(f"{name.ljust(width)}  {value}")


def slow_retry(work, attempts=3, delay=1.0):
    """Retries with a real sleep - which tests must not actually wait for."""
    for attempt in range(attempts):
        try:
            return work()
        except ValueError:
            time.sleep(delay)
    raise RuntimeError("gave up")
''',
    encoding="utf-8",
)

(WORKDIR / "test_app.py").write_text(
    '''
import time

import app


def test_summarise_file_counts_lines_and_words(tmp_path):
    target = tmp_path / "data.txt"                 # a fresh empty directory
    target.write_text("a b\\nc\\n", encoding="utf-8")

    assert app.summarise_file(target) == {"lines": 2, "words": 3}


def test_summarise_file_missing_file(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        app.summarise_file(tmp_path / "nope.txt")


def test_get_setting_reads_the_environment(monkeypatch):
    monkeypatch.setenv("PZH_DEMO_LIMIT", "42")
    assert app.get_setting("PZH_DEMO_LIMIT", "10") == "42"


def test_get_setting_falls_back(monkeypatch):
    monkeypatch.delenv("PZH_DEMO_LIMIT", raising=False)
    assert app.get_setting("PZH_DEMO_LIMIT", "10") == "10"


def test_environment_did_not_leak():
    import os

    assert "PZH_DEMO_LIMIT" not in os.environ, "monkeypatch undoes its changes"


def test_retry_without_waiting(monkeypatch):
    slept = []
    monkeypatch.setattr(app.time, "sleep", lambda seconds: slept.append(seconds))

    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("not yet")
        return "ok"

    assert app.slow_retry(flaky, attempts=5, delay=2.0) == "ok"
    assert slept == [2.0, 2.0], "sleep was replaced, so the test is instant"


def test_print_table_aligns_columns(capsys):
    app.print_table([("ada", 3), ("bo", 12)])

    lines = capsys.readouterr().out.strip().splitlines()
    assert lines == ["ada  3", "bo   12"]
''',
    encoding="utf-8",
)

print("Running: pytest -q test_app.py\n")
run_pytest(WORKDIR / "test_app.py")


# ---------------------------------------------------------------------------
banner("10. Red-green-refactor, step by step")
# ---------------------------------------------------------------------------

# Instead of narrating, here are the four implementations the TDD cycle produced,
# checked against the same growing test list. Watch which tests pass at each step.
TESTS: list[tuple[str, str]] = [
    ("", ""),
    ("a", "a1"),
    ("aaa", "a3"),
    ("aaabbc", "a3b2c1"),
]


def step1_return_empty(text: str) -> str:
    """Green for test 1 only. An honest lie: the next test will force more."""
    return ""


def step2_single_char(text: str) -> str:
    """Green for tests 1-2."""
    if not text:
        return ""
    return f"{text[0]}1"


def step3_loop(text: str) -> str:
    """Green for all four. Works, and ugly: three variables and a duplicated flush."""
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


def step4_refactored(text: str) -> str:
    """Same behaviour, one line, using Day 17's groupby. The tests made this safe."""
    return "".join(f"{char}{len(list(group))}" for char, group in groupby(text))


def score(func: Callable[[str], str]) -> str:
    """Report which of the growing test list a given implementation passes."""
    marks = []
    for text, want in TESTS:
        try:
            marks.append("PASS" if func(text) == want else "FAIL")
        except Exception as error:  # noqa: BLE001 - demo wants the label, not the type
            marks.append(f"ERROR({type(error).__name__})")
    return " ".join(m.ljust(5) for m in marks)


print("tests:            ", " ".join(repr(t).ljust(5) for t, _ in TESTS))
print("step 1 (return ''):", score(step1_return_empty))
print("step 2 (first char):", score(step2_single_char))
print("step 3 (loop)      :", score(step3_loop))
print("step 4 (groupby)   :", score(step4_refactored))
print()
print("The refactor from step 3 to step 4 changed every line of the implementation")
print("and zero lines of the tests. That is what 'test behaviour, not internals' buys.")


def rle_decode(encoded: str) -> str:
    """The inverse, so we can assert a law rather than examples."""
    out = []
    index = 0
    while index < len(encoded):
        char = encoded[index]
        index += 1
        digits = ""
        while index < len(encoded) and encoded[index].isdigit():
            digits += encoded[index]
            index += 1
        out.append(char * int(digits))
    return "".join(out)


round_trips = all(rle_decode(step4_refactored(t)) == t for t in ["", "a", "aaabbc", "xyz"])
print("\nround-trip law: decode(encode(text)) == text for every sample ->", round_trips)
print("One law like that is worth ten example tests.")


# ---------------------------------------------------------------------------
banner("11. Coverage: what it does and does not tell you")
# ---------------------------------------------------------------------------

(WORKDIR / "test_coverage_theatre.py").write_text(
    '''
import app


def test_100_percent_coverage_zero_verification(tmp_path):
    """Executes every line of summarise_file and asserts NOTHING useful."""
    target = tmp_path / "f.txt"
    target.write_text("a b\\n", encoding="utf-8")
    app.summarise_file(target)          # covered! verified? no.
    assert True
''',
    encoding="utf-8",
)

print("Running the 'coverage theatre' test:\n")
run_pytest(WORKDIR / "test_coverage_theatre.py")
print()
print("That test passes, covers every line of summarise_file, and would keep")
print("passing if the word count were always 0. Coverage measures execution;")
print("only assertions measure correctness. Use the 'Missing' column as a to-do")
print("list, never a percentage as a target.")
print()
print("With pytest-cov installed you would run:")
print("  python -m pytest --cov=app --cov-branch --cov-report=term-missing")


# ---------------------------------------------------------------------------
banner("12. Mocking versus dependency injection")
# ---------------------------------------------------------------------------


class Mailer:
    """The real collaborator; sending email in a test would be a bad idea."""

    def send(self, address: str, body: str) -> bool:
        raise AssertionError("the real mailer must never run in a test")


def notify(mailer: Mailer, address: str, body: str) -> bool:
    return mailer.send(address, body)


# A MagicMock records calls and accepts anything.
mock_mailer = MagicMock()
notify(mock_mailer, "a@example.com", "hello")
mock_mailer.send.assert_called_once_with("a@example.com", "hello")
print("MagicMock       : call recorded and asserted")

# The cost: a MagicMock accepts calls that do not exist on the real class.
mock_mailer.sned("typo", "silently fine")            # note the typo
print("typo accepted   :", mock_mailer.sned.called, "<- no error, no warning")

# autospec makes the fake match the real signature, so typos fail loudly.
safe_mock = create_autospec(Mailer, instance=True)
try:
    safe_mock.sned("typo", "x")
except AttributeError as error:
    print("autospec        : AttributeError:", error)


# The usually-better option: inject a small honest fake. No patching at all.
class FakeMailer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, address: str, body: str) -> bool:
        self.sent.append((address, body))
        return True


fake = FakeMailer()
notify(fake, "b@example.com", "hi")
print("injected fake   :", fake.sent, "- visible seam, no magic, real signature")


# ---------------------------------------------------------------------------
banner("13. Tooling: what each tool would say about bad code")
# ---------------------------------------------------------------------------

bad_code = '''import os
import json

def total(prices = []):
    result = 0
    for p in prices:
        result += p
    return reslt
'''

print("Consider this file:\n")
print(bad_code)
print("What each tool reports (paraphrased):")
print("  black : reformats spacing around '=' in the default argument,")
print("          adds blank lines, normalises quotes. No opinion on the bug.")
print("  ruff  : F401 'os' imported but unused")
print("          F401 'json' imported but unused")
print("          B006 mutable default argument (prices = [])")
print("          F821 undefined name 'reslt'   <- an actual bug, found statically")
print("  mypy  : error: Name 'reslt' is not defined")
print("          error: Returning Any from function declared to return int (with hints)")
print("  pytest: nothing - it never ran. A linter finds this in 40 milliseconds;")
print("          a test finds it only if you wrote one that calls total().")

# Show that the linters are actually available here, if installed.
for tool in ("ruff", "black", "mypy"):
    location = shutil.which(tool)
    print(f"  {tool:<6}: {'installed at ' + location if location else 'not installed (pip install ' + tool + ')'}")

print()
print("Adoption order: black -> ruff -> mypy -> pre-commit. Configure all four in")
print("pyproject.toml; this course's root pyproject.toml is a working example.")


# ---------------------------------------------------------------------------
banner("Cleanup")
# ---------------------------------------------------------------------------

# Prove the in-memory database trick from section 5 works outside pytest too.
with contextlib.closing(sqlite3.connect(":memory:")) as conn:
    conn.execute("CREATE TABLE t (id INTEGER)")
    print("in-memory sqlite:", conn.execute("SELECT count(*) FROM t").fetchone()[0], "rows")

# Silence pytest's own leftover output streams, then delete the sandbox.
with contextlib.redirect_stdout(io.StringIO()):
    pass
shutil.rmtree(WORKDIR, ignore_errors=True)
print("temp workspace removed:", not WORKDIR.exists())
print("stray files in the day folder:", sorted(
    p.name for p in Path(__file__).parent.iterdir() if p.name not in {
        "LESSON.md", "examples.py", "exercises.py", "solutions.py", "test_exercises.py",
    }
))
print("(an empty list above means this script left nothing behind)")

# capsys has a plain-Python cousin worth knowing: redirect_stdout.
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    print("captured without pytest")
print("redirect_stdout :", buffer.getvalue().strip())

print()
print("Done. Now open exercises.py in this folder.")
print("Working directory unchanged:", os.getcwd() == str(Path.cwd()))
sys.exit(0)
