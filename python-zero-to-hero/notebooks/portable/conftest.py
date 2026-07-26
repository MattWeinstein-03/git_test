"""Pytest harness for the course.

You almost never need to read or edit this file. It does one job: when a day's
`test_exercises.py` asks for the `day` fixture, this loads *your* `exercises.py`
from that same folder and hands it over to the tests.

Set PZH_SOLUTIONS=1 to grade `solutions.py` instead of `exercises.py`. That is
how the course itself is verified, and it is also a handy way to prove to
yourself that a test suite is passable when you are stuck.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.resolve()


def _load_module(path: Path) -> ModuleType:
    """Import a .py file by path, without needing it to be on sys.path."""
    # A unique module name per file keeps days from shadowing each other.
    mod_name = f"pzh_{path.parent.name}_{path.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    # Let the day folder import its own sibling helper files if it has any.
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


@pytest.fixture
def day(request: pytest.FixtureRequest) -> ModuleType:
    """The module under test for the current day's folder."""
    folder = Path(request.node.fspath).parent
    use_solutions = os.environ.get("PZH_SOLUTIONS") == "1"
    filename = "solutions.py" if use_solutions else "exercises.py"
    target = folder / filename

    if not target.exists():
        pytest.fail(
            f"Expected to find {filename} in {folder.name}/ but it is missing."
        )
    return _load_module(target)


def pytest_configure(config: pytest.Config) -> None:
    if os.environ.get("PZH_SOLUTIONS") == "1":
        print("\n[pzh] grading solutions.py (verification mode)\n")


def pytest_report_header(config: pytest.Config) -> str:
    return "python-zero-to-hero: run `python check.py` to see your progress"
