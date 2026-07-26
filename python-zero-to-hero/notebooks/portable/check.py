#!/usr/bin/env python3
"""The course grader. This is the only command you need to remember.

    python check.py                 show your progress across all 21 days
    python check.py day05           grade Day 5 and tell you what's wrong
    python check.py day05 -v        same, but with full failure detail
    python check.py week2           grade every day in week 2
    python check.py next            grade the first day you haven't finished
    python check.py plan            print the 21-day map
    python check.py doctor          check your Python setup is sane

Nothing here is magic: `check.py dayNN` is a friendly wrapper around
`python -m pytest course/weekN/dayNN_*/test_exercises.py`. Use pytest directly
any time you want.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
COURSE = ROOT / "course"
CACHE = ROOT / ".pzh_progress.json"

# How to spell "run me again" in the hints. The ./run launcher sets this, so the
# advice you are given matches the way you actually started the grader.
CMD = os.environ.get("PZH_LAUNCHER") or "python check.py"

# ----------------------------------------------------------------------------
# tiny terminal styling (degrades gracefully when piped or on dumb terminals)
# ----------------------------------------------------------------------------
_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def green(t: str) -> str:
    return _c(t, "32")


def red(t: str) -> str:
    return _c(t, "31")


def yellow(t: str) -> str:
    return _c(t, "33")


def blue(t: str) -> str:
    return _c(t, "36")


def bold(t: str) -> str:
    return _c(t, "1")


def dim(t: str) -> str:
    return _c(t, "2")


# ----------------------------------------------------------------------------
# discovering days
# ----------------------------------------------------------------------------
@dataclass
class Day:
    number: int
    slug: str
    week: int
    path: Path

    @property
    def key(self) -> str:
        return f"day{self.number:02d}"

    @property
    def title(self) -> str:
        return self.slug.replace("_", " ").title()

    @property
    def test_file(self) -> Path:
        return self.path / "test_exercises.py"

    @property
    def lesson(self) -> Path:
        return self.path / "LESSON.md"


def discover_days() -> list[Day]:
    days: list[Day] = []
    if not COURSE.exists():
        return days
    for week_dir in sorted(COURSE.glob("week*")):
        week_num = int(re.sub(r"\D", "", week_dir.name) or 0)
        for day_dir in sorted(week_dir.glob("day*")):
            m = re.match(r"day(\d+)_?(.*)", day_dir.name)
            if not m:
                continue
            days.append(
                Day(
                    number=int(m.group(1)),
                    slug=m.group(2) or "untitled",
                    week=week_num,
                    path=day_dir,
                )
            )
    return sorted(days, key=lambda d: d.number)


def resolve_targets(selector: str, days: list[Day]) -> list[Day]:
    sel = selector.lower().strip()
    if sel in {"all", ""}:
        return days
    if m := re.fullmatch(r"(?:day)?0*(\d+)", sel):
        n = int(m.group(1))
        return [d for d in days if d.number == n]
    if m := re.fullmatch(r"week0*(\d+)", sel):
        w = int(m.group(1))
        return [d for d in days if d.week == w]
    return []


# ----------------------------------------------------------------------------
# running pytest
# ----------------------------------------------------------------------------
@dataclass
class Result:
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    output: str = ""
    duration: float = 0.0

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.errors + self.skipped

    @property
    def graded(self) -> int:
        return self.passed + self.failed + self.errors

    @property
    def is_complete(self) -> bool:
        return self.graded > 0 and self.failed == 0 and self.errors == 0

    @property
    def pct(self) -> int:
        return round(100 * self.passed / self.graded) if self.graded else 0


_COUNT_RE = re.compile(r"(\d+) (passed|failed|error|errors|skipped|xfailed)")


def run_day(day: Day, verbose: bool = False) -> Result:
    if not day.test_file.exists():
        return Result(output=f"no test_exercises.py in {day.path.name}")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(day.test_file),
        "-p",
        "no:cacheprovider",
        "--no-header",
        "-q",
        "--tb=" + ("long" if verbose else "line"),
    ]
    started = time.time()
    proc = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, env={**os.environ}
    )
    out = proc.stdout + proc.stderr
    res = Result(output=out, duration=time.time() - started)
    for count, label in _COUNT_RE.findall(out):
        n = int(count)
        if label == "passed":
            res.passed = n
        elif label == "failed":
            res.failed = n
        elif label.startswith("error"):
            res.errors = n
        elif label == "skipped":
            res.skipped = n
    return res


# ----------------------------------------------------------------------------
# reporting
# ----------------------------------------------------------------------------
def _bar(pct: int, width: int = 20) -> str:
    filled = round(width * pct / 100)
    body = "#" * filled + "." * (width - filled)
    color = green if pct == 100 else (yellow if pct > 0 else red)
    return color(body)


def _failed_test_names(output: str) -> list[str]:
    names: list[str] = []
    for line in output.splitlines():
        # pytest -q --tb=line prints "path/to/test_exercises.py:12: AssertionError"
        # and a FAILED/ERROR summary line we can mine for readable names.
        if m := re.search(r"(?:FAILED|ERROR)\s+\S+::(\w+)", line):
            names.append(m.group(1))
        elif m := re.search(r"^(?:FAILED|ERROR)\s+(\S+)", line):
            names.append(m.group(1))
    seen: set[str] = set()
    return [n for n in names if not (n in seen or seen.add(n))]


def _not_implemented(output: str) -> list[str]:
    return sorted(set(re.findall(r"NotImplementedError:?\s*(?:exercise\s*)?([^\n]*)", output)))


def report_day(day: Day, res: Result, verbose: bool) -> None:
    header = f"Day {day.number:02d} — {day.title}"
    print()
    print(bold(header))
    print(dim("-" * len(header)))

    if res.graded == 0:
        print(yellow("  No tests ran."))
        if verbose:
            print(dim(res.output))
        return

    status = green("COMPLETE") if res.is_complete else red("NOT YET")
    print(f"  {_bar(res.pct)} {res.passed}/{res.graded} checks passing   {status}")

    if res.is_complete:
        print(green(f"\n  Day {day.number:02d} is done. Move on to the next lesson."))
        return

    todo = _not_implemented(res.output)
    if todo:
        print(dim("\n  Exercises still unimplemented:"))
        for t in todo[:12]:
            print(f"    - {t.strip() or '(unnamed)'}")

    failing = [n for n in _failed_test_names(res.output)]
    if failing:
        print(dim("\n  Failing checks:"))
        for n in failing[:15]:
            print(f"    {red('x')} {n}")
        if len(failing) > 15:
            print(dim(f"    ... and {len(failing) - 15} more"))

    if verbose:
        print(dim("\n--- full pytest output ---"))
        print(res.output)
    else:
        print(
            dim(
                f"\n  See the detail:  {CMD} day{day.number:02d} -v"
                f"\n  Read the lesson: {day.lesson.relative_to(ROOT)}"
            )
        )


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cache(data: dict) -> None:
    # Grading solutions.py must never touch YOUR progress: otherwise one
    # verification run makes a day you have not started look finished.
    if os.environ.get("PZH_SOLUTIONS") == "1":
        return
    try:
        CACHE.write_text(json.dumps(data, indent=2, sort_keys=True))
    except OSError:
        pass


def cmd_progress(days: list[Day], fresh: bool) -> int:
    cache = {} if fresh else load_cache()
    print()
    print(bold("  python-zero-to-hero — progress"))
    print()
    total_pass = total_all = 0
    current_week = 0

    for d in days:
        if d.week != current_week:
            current_week = d.week
            print(bold(f"  Week {current_week}"))
        entry = cache.get(d.key)
        if entry is None:
            res = run_day(d)
            entry = {"passed": res.passed, "graded": res.graded}
            cache[d.key] = entry
        passed, graded = entry["passed"], entry["graded"]
        total_pass += passed
        total_all += graded
        pct = round(100 * passed / graded) if graded else 0
        mark = green("[x]") if graded and passed == graded else "[ ]"
        print(
            f"    {mark} Day {d.number:02d}  {_bar(pct, 16)} "
            f"{str(passed).rjust(3)}/{str(graded).ljust(3)} {dim(d.title)}"
        )
    save_cache(cache)

    overall = round(100 * total_pass / total_all) if total_all else 0
    print()
    print(f"  Overall: {_bar(overall, 30)} {overall}%  ({total_pass}/{total_all} checks)")
    nxt = next((d for d in days if cache.get(d.key, {}).get("passed", 0) < cache.get(d.key, {}).get("graded", 1)), None)
    if nxt:
        print(f"  Up next: {blue(f'{CMD} day{nxt.number:02d}')}  ->  {nxt.lesson.relative_to(ROOT)}")
    else:
        print(green("  Every day is complete. You did the thing."))
    print(dim("\n  (cached; use --fresh to re-grade everything)\n"))
    return 0


def cmd_plan(days: list[Day]) -> int:
    plan_file = ROOT / "SYLLABUS.md"
    if plan_file.exists():
        print(plan_file.read_text())
        return 0
    for d in days:
        print(f"Day {d.number:02d} (week {d.week}): {d.title}")
    return 0


def cmd_doctor() -> int:
    print()
    print(bold("  Setup check"))
    ok = True

    v = sys.version_info
    if v >= (3, 10):
        print(f"  {green('ok')}   Python {v.major}.{v.minor}.{v.micro}")
    else:
        ok = False
        print(f"  {red('bad')}  Python {v.major}.{v.minor} — this course needs 3.10 or newer")

    try:
        import pytest  # noqa: F401

        print(f"  {green('ok')}   pytest {pytest.__version__}")
    except ImportError:
        ok = False
        print(f"  {red('bad')}  pytest not installed — run: python -m pip install pytest")

    days = discover_days()
    if len(days) == 21:
        print(f"  {green('ok')}   found all 21 day folders")
    else:
        ok = False
        print(f"  {red('bad')}  found {len(days)} day folders, expected 21")

    in_venv = sys.prefix != sys.base_prefix
    print(f"  {green('ok') if in_venv else yellow('warn')}   virtualenv active: {in_venv}"
          + ("" if in_venv else dim("  (fine for now; Day 11 explains why you want one)")))

    print()
    print(green("  You're ready. Start with course/week1/day01_*/LESSON.md")
          if ok else red("  Fix the items marked 'bad' above, then re-run."))
    print()
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check.py",
        description="Grade your work in the python-zero-to-hero course.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="progress",
        help="dayNN | weekN | all | next | plan | doctor | progress (default)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="show full pytest output")
    parser.add_argument("--fresh", action="store_true", help="ignore cached progress")
    args = parser.parse_args(argv)

    days = discover_days()
    if not days:
        print(red(f"No day folders found under {COURSE}. Is the course installed?"))
        return 1

    target = args.target.lower()
    if target == "doctor":
        return cmd_doctor()
    if target == "plan":
        return cmd_plan(days)
    if target == "progress":
        return cmd_progress(days, fresh=args.fresh)

    if target == "next":
        cache = load_cache()
        pending = [
            d for d in days
            if cache.get(d.key, {}).get("graded", 1) > cache.get(d.key, {}).get("passed", 0)
        ]
        targets = pending[:1] or days[:1]
    else:
        targets = resolve_targets(target, days)

    if not targets:
        print(red(f"Don't know what '{args.target}' means."))
        print(dim(f"Try: {CMD} day03   |   week2   |   next   |   plan"))
        return 1

    cache = load_cache()
    all_complete = True
    for d in targets:
        res = run_day(d, verbose=args.verbose)
        report_day(d, res, args.verbose)
        cache[d.key] = {"passed": res.passed, "graded": res.graded}
        all_complete &= res.is_complete
    save_cache(cache)
    print()
    return 0 if all_complete else 1


if __name__ == "__main__":
    sys.exit(main())
