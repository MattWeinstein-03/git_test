#!/usr/bin/env python3
"""Generate one Jupyter notebook per course day from that day's ``LESSON.md``.

``LESSON.md`` is the single source of truth. The notebooks under ``notebooks/``
are generated artefacts: never hand-edit them, because the next build discards
your edits. Everything a notebook contains comes from the lesson, plus a small
fixed preamble and postamble that this script adds.

    python tools/build_notebooks.py            regenerate all 21 notebooks
    python tools/build_notebooks.py --day 05   regenerate one day
    python tools/build_notebooks.py --check    exit 1 if a committed notebook is stale
    python tools/build_notebooks.py --verify   execute every notebook, fail on any error

It also generates ``notebooks/portable/``: a single self-contained folder holding
the 21 notebooks plus the grader, the day folders and the reference docs, so it
can be copied to a laptop or an iPad and run offline with nothing else. That
folder is generated too, from the same lessons, so it can never drift.

Conversion, in one paragraph: prose, headings, tables, blockquote callouts and
``<details>`` blocks become markdown cells. A fenced ``python`` block becomes an
executable code cell *only* when it is genuinely runnable given the cells before
it; otherwise it stays a markdown cell (still fenced, so it renders as code but
cannot be run) with a one-line generated note saying why. The reasoning lives in
the named predicates in the DEMOTION PREDICATES section below, so that any
"why is this block not runnable?" question has an auditable answer.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator, Sequence

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "course"
NOTEBOOKS = ROOT / "notebooks"
# The take-it-with-you bundle: one folder, everything inside it, runs offline.
PORTABLE = NOTEBOOKS / "portable"
# Course-root files the bundle needs to be able to grade you on its own.
BUNDLE_ROOT_FILES = ("check.py", "conftest.py", "pyproject.toml", "CHEATSHEET.md", "SYLLABUS.md")
# Per-day files the bundle carries so the notebooks' links and the grader work.
BUNDLE_DAY_FILES = (
    "LESSON.md",
    "examples.py",
    "exercises.py",
    "solutions.py",
    "test_exercises.py",
)

BUILTIN_NAMES = frozenset(dir(builtins)) | {"__name__", "__doc__", "__builtins__"}
STDLIB_MODULES = frozenset(sys.stdlib_module_names)

# nbformat >= 4.5 stamps every cell with a random id, which would make the output
# non-deterministic. We assign ids ourselves instead.
NBFORMAT_MAJOR = 4
NBFORMAT_MINOR = 5


# ---------------------------------------------------------------------------
# discovering days
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Day:
    number: int
    slug: str  # e.g. "day05_lists_and_tuples"
    week: int
    directory: Path

    @property
    def label(self) -> str:
        return f"day{self.number:02d}"

    @property
    def lesson(self) -> Path:
        return self.directory / "LESSON.md"

    @property
    def notebook(self) -> Path:
        return NOTEBOOKS / f"{self.slug}.ipynb"

    @property
    def bundle_notebook(self) -> Path:
        return PORTABLE / f"{self.slug}.ipynb"

    def course_relative(self, filename: str, portable: bool = False) -> str:
        """Link from a notebook back into the day folder.

        ``notebooks/dayNN.ipynb`` sits one level below the course root, while the
        portable bundle keeps its own copy of ``course/`` alongside the notebooks.
        """
        prefix = "" if portable else "../"
        return f"{prefix}course/week{self.week}/{self.slug}/{filename}"


def discover_days() -> list[Day]:
    days: list[Day] = []
    for week_dir in sorted(COURSE.glob("week*")):
        week = int(week_dir.name.removeprefix("week"))
        for day_dir in sorted(week_dir.glob("day*")):
            match = re.fullmatch(r"day(\d{2})_(.+)", day_dir.name)
            if not match or not (day_dir / "LESSON.md").is_file():
                continue
            days.append(
                Day(
                    number=int(match.group(1)),
                    slug=day_dir.name,
                    week=week,
                    directory=day_dir,
                )
            )
    return sorted(days, key=lambda day: day.number)


# ---------------------------------------------------------------------------
# markdown parsing
# ---------------------------------------------------------------------------
FENCE_RE = re.compile(r"^```([A-Za-z0-9+_-]*)\s*$")
HEADING_RE = re.compile(r"^#{1,6} \S")


@dataclass
class Prose:
    text: str


@dataclass
class Fence:
    language: str
    code: str

    @property
    def rendered(self) -> str:
        return f"```{self.language}\n{self.code}\n```"


Node = Prose | Fence


def parse_lesson(markdown: str) -> list[Node]:
    """Split a lesson into prose chunks and top-level fenced code blocks.

    Only fences that start in column 0 and sit outside a ``<details>`` block are
    lifted out as candidates for code cells. Fences indented inside a list item
    or hidden inside ``<details>`` stay embedded in their surrounding markdown,
    because pulling them out would break the structure the author wrote.
    """
    nodes: list[Node] = []
    buffer: list[str] = []

    def flush() -> None:
        for chunk in split_prose("\n".join(buffer)):
            nodes.append(Prose(chunk))
        buffer.clear()

    lines = markdown.splitlines()
    index = 0
    in_details = False
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("<details"):
            in_details = True
        if in_details:
            buffer.append(line)
            if stripped.startswith("</details"):
                in_details = False
            index += 1
            continue

        fence = FENCE_RE.match(line)
        if fence:
            body: list[str] = []
            index += 1
            while index < len(lines) and lines[index].rstrip() != "```":
                body.append(lines[index])
                index += 1
            index += 1  # consume the closing fence
            flush()
            nodes.append(Fence(language=fence.group(1), code="\n".join(body)))
            continue

        buffer.append(line)
        index += 1

    flush()
    return nodes


def split_prose(text: str) -> Iterator[str]:
    """Break a prose chunk into one cell per heading, so cells stay navigable."""
    current: list[str] = []
    for line in text.splitlines():
        if HEADING_RE.match(line) and any(item.strip() for item in current):
            yield "\n".join(current).strip("\n")
            current = [line]
        else:
            current.append(line)
    if any(item.strip() for item in current):
        yield "\n".join(current).strip("\n")


# ---------------------------------------------------------------------------
# static analysis helpers used by the predicates
# ---------------------------------------------------------------------------
@dataclass
class Context:
    """Everything a predicate may know about the block's surroundings."""

    names: set[str] = field(default_factory=set)  # names bound by earlier code cells
    following_output: str = ""  # the unlabelled fence directly after this block, if any


def bound_names(tree: ast.AST, *, nested_scopes: bool = True) -> set[str]:
    """Every name this code binds.

    With ``nested_scopes=True`` the walk is deliberately flat: a name bound
    anywhere — including a function parameter or a comprehension variable —
    counts as defined. That keeps the "undefined name" predicate free of false
    positives inside a single block.

    With ``nested_scopes=False`` only *module-level* bindings count. That is what
    one cell actually leaves behind for the next one: a function's parameters do
    not survive the call, so they must not be treated as notebook-wide names.
    """
    names: set[str] = set()

    def add_target(node: ast.AST) -> None:
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for element in node.elts:
                add_target(element)
        elif isinstance(node, ast.Starred):
            add_target(node.value)

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
            if not nested_scopes:
                return  # the body's locals never reach the enclosing namespace
            names.update(argument_names(node.args))
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
            if not nested_scopes:
                return
        elif isinstance(node, ast.Lambda):
            if not nested_scopes:
                return
            names.update(argument_names(node.args))
        elif isinstance(node, ast.comprehension):
            if nested_scopes:  # a comprehension has its own scope in Python 3
                add_target(node.target)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                add_target(target)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            add_target(node.target)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            add_target(node.target)
        elif isinstance(node, ast.withitem):
            if node.optional_vars is not None:
                add_target(node.optional_vars)
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                names.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            names.update(node.names)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)):
            if node.name:
                names.add(node.name)
        elif isinstance(node, ast.MatchMapping):
            if node.rest:
                names.add(node.rest)

        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return names


def argument_names(args: ast.arguments) -> set[str]:
    every = [
        *args.posonlyargs,
        *args.args,
        *args.kwonlyargs,
        *([args.vararg] if args.vararg else []),
        *([args.kwarg] if args.kwarg else []),
    ]
    return {argument.arg for argument in every}


def loaded_names(tree: ast.AST) -> list[str]:
    return [
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    ]


def attribute_names(tree: ast.AST) -> set[str]:
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def called_functions(tree: ast.AST) -> set[str]:
    """Dotted-ish spellings of everything called, e.g. {"open", "time.sleep"}."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
            if isinstance(target.value, ast.Name):
                names.add(f"{target.value.id}.{target.attr}")
    return names


def imported_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                roots.add(node.module.split(".")[0])
            else:
                roots.add(".")  # a relative import cannot work in a notebook
    return roots


def module_scope_statements(tree: ast.Module) -> Iterator[ast.stmt]:
    """Statements that really run when the cell runs.

    Descends into `if`/`for`/`while`/`with`/`try`/`match` bodies, because those
    execute immediately, but never into a `def` or `class` body, because those
    only execute when something calls them.
    """

    def walk(statements: Sequence[ast.stmt]) -> Iterator[ast.stmt]:
        for statement in statements:
            yield statement
            if isinstance(
                statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                continue
            for field_name in ("body", "orelse", "finalbody"):
                yield from walk(getattr(statement, field_name, []) or [])
            for handler in getattr(statement, "handlers", []) or []:
                yield from walk(handler.body)
            for case in getattr(statement, "cases", []) or []:
                yield from walk(case.body)

    yield from walk(tree.body)


def module_level(tree: ast.Module, kinds: tuple[type, ...]) -> list[ast.stmt]:
    """Every statement of the given kinds that the cell would actually execute."""
    return [node for node in module_scope_statements(tree) if isinstance(node, kinds)]


# ---------------------------------------------------------------------------
# DEMOTION PREDICATES
#
# Each predicate answers one question: "is there a reason this block must not be
# an executable cell?" It returns None to stay silent, or a Demotion carrying a
# machine-readable kind (for the build report) and the one-line note the learner
# sees above the block. The predicates run in the order listed in PREDICATES.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Demotion:
    kind: str
    note: str


def demote_shell_not_python(code: str, tree: ast.Module | None, ctx: Context):
    """Some lessons show `pip install ...` or a `$ python foo.py` session."""
    shell_markers = (
        r"^\s*\$ ",
        r"^\s*[%!]",
        r"^\s*(?:python3?|pip|pip3|pytest|ruff|black|mypy|git|cd|ls|export|source)\b",
        r"^\s*python -m ",
    )
    for line in code.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if any(re.match(marker, line) for marker in shell_markers):
            return Demotion(
                "shell",
                "*Not runnable here — this is a shell command, not Python. "
                "Run it in a terminal.*",
            )
    return None


def demote_repl_transcript(code: str, tree: ast.Module | None, ctx: Context):
    """A `>>>` session is a transcript of typing, not a program to run."""
    for line in code.splitlines():
        if line.startswith((">>> ", "... ")) or line.rstrip() in {">>>", "..."}:
            return Demotion(
                "repl-transcript",
                "*Not runnable here — this is a transcript of a `python` prompt "
                "session. Type the lines yourself at a REPL.*",
            )
    return None


def demote_unparsable(code: str, tree: ast.Module | None, ctx: Context):
    """`ast.parse` failed, so the block is a deliberate SyntaxError-family demo."""
    if tree is None:
        return Demotion(
            "syntax-demo",
            "*Not runnable here — this is a deliberate syntax-error "
            "demonstration. Read it, don't run it.*",
        )
    return None


def demote_interactive_input(code: str, tree: ast.Module | None, ctx: Context):
    """A cell that blocks on stdin is a trap for a beginner."""
    assert tree is not None
    calls = called_functions(tree)
    if "input" in calls or "sys.stdin" in code or "stdin.read" in code:
        return Demotion(
            "interactive-input",
            "*Not runnable here — it waits for typed input, which stalls a "
            "notebook cell. Try it in a terminal.*",
        )
    return None


def demote_debugger(code: str, tree: ast.Module | None, ctx: Context):
    """`breakpoint()` / `pdb` open a prompt the notebook cannot answer."""
    assert tree is not None
    calls = called_functions(tree)
    if calls & {"breakpoint", "set_trace", "pdb.set_trace", "post_mortem", "pdb.post_mortem"}:
        return Demotion(
            "debugger",
            "*Not runnable here — it drops into the interactive debugger. "
            "Run it as a script in a terminal.*",
        )
    return None


def demote_process_exit(code: str, tree: ast.Module | None, ctx: Context):
    """`sys.exit()` and friends would kill the notebook's kernel."""
    assert tree is not None
    calls = called_functions(tree)
    if calls & {"exit", "quit", "sys.exit", "os._exit", "_exit"}:
        return Demotion(
            "exits-interpreter",
            "*Not runnable here — it stops the interpreter, which would kill "
            "this notebook's kernel.*",
        )
    return None


# A comment naming the exception that is *meant* to come out. Case-sensitive on
# purpose: `# ValueError: ...` marks a demo, whereas `except ValueError as error:
# # binds the object` is ordinary prose about a working example.
EXCEPTION_NAME_COMMENT_RE = re.compile(
    r"#[^\n]*?\b(?:[A-Z][A-Za-z]*(?:Error|Exception)|StopIteration|KeyboardInterrupt"
    r"|SystemExit)\b"
)
# Phrases that say "this one blows up", whatever the exception is called.
ERROR_PHRASE_COMMENT_RE = re.compile(
    r"#[^\n]*?\b(?:raises?|crashes?(?:\s+with)?|blows up|boom|fails with|"
    r"traceback|does not work|doesn't work|won't work)\b",
    re.IGNORECASE,
)
TRACEBACK_RE = re.compile(r"Traceback \(most recent call last\)")


def demote_error_demo(code: str, tree: ast.Module | None, ctx: Context):
    """A block whose *point* is the exception it raises.

    Three signals: a pasted traceback, a comment naming the exception that is
    meant to come out (`# ValueError: ...`, `# raises TypeError`), or a `raise`
    /failing `assert` sitting at module level where running it really would
    stop the cell.
    """
    assert tree is not None
    if TRACEBACK_RE.search(code):
        return Demotion("error-demo", ERROR_DEMO_NOTE)
    if EXCEPTION_NAME_COMMENT_RE.search(code) or ERROR_PHRASE_COMMENT_RE.search(code):
        return Demotion("error-demo", ERROR_DEMO_NOTE)
    if module_level(tree, (ast.Raise, ast.Assert)):
        return Demotion("error-demo", ERROR_DEMO_NOTE)
    return None


ERROR_DEMO_NOTE = (
    "*Not runnable here — this is a deliberate error demonstration. "
    "Read it, don't run it.*"
)


EXPECTED_ERROR_OUTPUT_RE = re.compile(
    r"^\s*(?:[A-Za-z_.]*(?:Error|Exception)\b|Traceback \(most recent call last\))",
    re.MULTILINE,
)


def demote_error_demo_by_output(code: str, tree: ast.Module | None, ctx: Context):
    """The lesson's own "Output:" block is a traceback.

    Lessons often show the bad line and put the resulting error in the *next*
    fence rather than in a comment, e.g. `print("Age: " + 36)` followed by a
    block containing `TypeError: ...`. The expected output is the tell.
    """
    if ctx.following_output and EXPECTED_ERROR_OUTPUT_RE.search(ctx.following_output):
        return Demotion("error-demo", ERROR_DEMO_NOTE)
    return None


def demote_fragment(code: str, tree: ast.Module | None, ctx: Context):
    """Pseudo-code: `...` bodies, bare `...`, or `# ...` elision markers."""
    assert tree is not None

    def is_ellipsis(node: ast.stmt) -> bool:
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and node.value.value is Ellipsis
        )

    for node in ast.walk(tree):
        if is_ellipsis(node) if isinstance(node, ast.stmt) else False:
            return Demotion("fragment", FRAGMENT_NOTE)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = [item for item in node.body if not is_docstring(item)]
            if body and all(is_ellipsis(item) for item in body):
                return Demotion("fragment", FRAGMENT_NOTE)
    if re.search(r"^\s*#\s*\.\.\.\s*$", code, re.MULTILINE):
        return Demotion("fragment", FRAGMENT_NOTE)
    return None


FRAGMENT_NOTE = (
    "*Not runnable here — this is an illustrative fragment rather than a "
    "complete program.*"
)


def is_docstring(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def demote_missing_module(code: str, tree: ast.Module | None, ctx: Context):
    """Imports of packages the course installs later, or of the lesson's own
    example modules, which do not exist next to the notebook."""
    assert tree is not None
    for root in sorted(imported_roots(tree)):
        if root in STDLIB_MODULES or root in ALLOWED_PACKAGES or root in ctx.names:
            continue
        return Demotion(
            "missing-module",
            "*Not runnable here — it imports a module that is not installed "
            "beside this notebook. Run it in a terminal once you have it.*",
        )
    return None


# The only non-stdlib import the course guarantees from Day 1 (see pyproject.toml).
# Everything else (requests, httpx, ruff, ...) is installed later, by the lesson
# that needs it, so importing it in a cell would fail today.
ALLOWED_PACKAGES = frozenset({"pytest"})

NETWORK_MODULES = {"requests", "httpx", "urllib", "socket", "http", "ftplib", "smtplib"}


def demote_network_io(code: str, tree: ast.Module | None, ctx: Context):
    """Network calls fail (or hang) on an offline machine."""
    assert tree is not None
    if imported_roots(tree) & NETWORK_MODULES:
        return Demotion("network", NETWORK_NOTE)
    if called_functions(tree) & {"urlopen", "requests.get", "requests.post", "httpx.get"}:
        return Demotion("network", NETWORK_NOTE)
    return None


NETWORK_NOTE = (
    "*Not runnable here — it talks to the network. Run it in a terminal once "
    "the lesson has you install the packages.*"
)


# Methods that only exist on paths, so seeing one is proof of filesystem work.
PATH_METHODS = {
    "write_text",
    "write_bytes",
    "read_text",
    "read_bytes",
    "mkdir",
    "rmdir",
    "unlink",
    "touch",
    "glob",
    "rglob",
    "iterdir",
}
# Names that lists and strings also own (`items.remove(x)`, `text.replace(...)`),
# so they only count when they are spelled out on `os` or `shutil`.
QUALIFIED_FILESYSTEM_CALLS = {
    "os.remove",
    "os.rename",
    "os.replace",
    "os.mkdir",
    "os.makedirs",
    "os.rmdir",
    "os.listdir",
    "os.walk",
    "shutil.copy",
    "shutil.copy2",
    "shutil.copytree",
    "shutil.move",
    "shutil.rmtree",
}


def demote_filesystem_io(code: str, tree: ast.Module | None, ctx: Context):
    """Reading or writing real files beside the notebook.

    Reads usually fail (the lesson's `notes.txt` does not exist) and writes
    would litter `notebooks/`. Blocks that keep to a `tempfile` sandbox are
    allowed through.
    """
    assert tree is not None
    if "tempfile" in imported_roots(tree) or "tempfile" in ctx.names:
        return None
    calls = called_functions(tree)
    if "open" in calls or calls & PATH_METHODS or calls & QUALIFIED_FILESYSTEM_CALLS:
        return Demotion("filesystem", FILESYSTEM_NOTE)
    for node in ast.walk(tree):  # sqlite3.connect("app.db") writes a file
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "connect"
        ):
            first = node.args[0] if node.args else None
            literal = first.value if isinstance(first, ast.Constant) else None
            if literal != ":memory:":
                return Demotion("filesystem", FILESYSTEM_NOTE)
    return None


FILESYSTEM_NOTE = (
    "*Not runnable here — it reads or writes files on disk. Try it in a "
    "scratch folder from a terminal.*"
)


def demote_concurrency(code: str, tree: ast.Module | None, ctx: Context):
    """Threads, processes and event loops behave differently inside a kernel.

    `asyncio.run` in particular raises inside a notebook, because the kernel is
    already running a loop, and `multiprocessing` needs an importable
    `__main__`.
    """
    assert tree is not None
    if imported_roots(tree) & {
        "threading",
        "multiprocessing",
        "asyncio",
        "concurrent",
        "subprocess",
        "signal",
    }:
        return Demotion("concurrency", CONCURRENCY_NOTE)
    if any(
        isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith))
        for node in ast.walk(tree)
    ):
        return Demotion("concurrency", CONCURRENCY_NOTE)
    if called_functions(tree) & {"Thread", "Process", "Popen", "system", "run"} & set(
        attribute_names(tree) | set(loaded_names(tree))
    ):
        return Demotion("concurrency", CONCURRENCY_NOTE)
    return None


CONCURRENCY_NOTE = (
    "*Not runnable here — it starts threads, processes or an event loop, which "
    "a notebook cell handles differently. Run it as a script.*"
)


def demote_slow_sleep(code: str, tree: ast.Module | None, ctx: Context):
    """Anything sleeping longer than 0.1s just stalls the learner."""
    assert tree is not None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        if name != "sleep":
            continue
        first = node.args[0] if node.args else None
        if isinstance(first, ast.Constant) and isinstance(first.value, (int, float)):
            if first.value <= 0.1:
                continue
        return Demotion(
            "sleep",
            "*Not runnable here — it sleeps long enough to stall the notebook. "
            "Run it as a script.*",
        )
    return None


def demote_undefined_names(code: str, tree: ast.Module | None, ctx: Context):
    """Names the lesson never defines: `row`, `use_units(...)`, `__file__`.

    This is the predicate that catches half-written illustrations. It compares
    every name the block reads against the builtins plus everything bound by the
    code cells before it in the same notebook.
    """
    assert tree is not None
    known = BUILTIN_NAMES | ctx.names | bound_names(tree)
    missing: list[str] = []
    for name in loaded_names(tree):
        if name not in known and name not in missing:
            missing.append(name)
    if "__file__" in code and "__file__" not in ctx.names:
        if "__file__" not in missing:
            missing.append("__file__")
    if not missing:
        return None
    listed = ", ".join(f"`{name}`" for name in missing[:3])
    if len(missing) > 3:
        listed += ", …"
    return Demotion(
        "undefined-names",
        f"*Not runnable here — it refers to {listed}, which the lesson never "
        f"defines. Read it, don't run it.*",
    )


ENDLESS_COMMENT_RE = re.compile(
    r"#[^\n]*\b(forever|infinite(?:ly)?|never (?:ends|stops|terminates)|"
    r"runs? until you press|hangs?)\b",
    re.IGNORECASE,
)


def demote_endless_loop(code: str, tree: ast.Module | None, ctx: Context):
    """A loop with no exit would hang the kernel until the learner kills it.

    Two shapes appear in the lessons: `while True:` with no `break`, and the
    "forgot to increment the counter" demo, where the loop test reads a name the
    body never rebinds.
    """
    assert tree is not None
    if ENDLESS_COMMENT_RE.search(code):
        return Demotion("endless-loop", ENDLESS_LOOP_NOTE)
    for node in ast.walk(tree):
        if not isinstance(node, ast.While):
            continue
        if any(
            isinstance(inner, (ast.Break, ast.Return, ast.Raise))
            for inner in ast.walk(node)
        ):
            continue
        test_names = {
            inner.id for inner in ast.walk(node.test) if isinstance(inner, ast.Name)
        }
        body_binds: set[str] = set()
        for statement in node.body:
            body_binds |= bound_names(statement)
        # No name the test depends on ever changes -> the test can never flip.
        if not test_names or not (test_names & body_binds):
            return Demotion("endless-loop", ENDLESS_LOOP_NOTE)
    return None


ENDLESS_LOOP_NOTE = (
    "*Not runnable here — this loop never ends, on purpose. Read it, don't run it.*"
)


def demote_recursion_demo(code: str, tree: ast.Module | None, ctx: Context):
    """A function that calls itself unconditionally is a RecursionError demo."""
    assert tree is not None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        # A base case is an `if`, a `while`, a `try`, or a conditional expression.
        has_guard = any(
            isinstance(inner, (ast.If, ast.IfExp, ast.While, ast.Try, ast.Match))
            for inner in ast.walk(node)
        )
        # Plain `f(...)` only: `super().__init__(...)` inside `__init__` is not
        # recursion, and neither is `self.method()`.
        direct_calls = {
            inner.func.id
            for inner in ast.walk(node)
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
        }
        calls_itself = node.name in direct_calls
        if calls_itself and not has_guard:
            return Demotion(
                "recursion-demo",
                "*Not runnable here — it recurses without a base case on "
                "purpose. Read it, don't run it.*",
            )
    return None


def demote_class_body_only(code: str, tree: ast.Module | None, ctx: Context):
    """`pytest`-style or dataclass-style snippets that need a `pytest` run.

    A block whose only statements are `def test_...` definitions is harmless but
    misleading: nothing happens when you run it. Keep it as prose instead.
    """
    assert tree is not None
    statements = [node for node in tree.body if not is_docstring(node)]
    if not statements:
        return Demotion("empty", FRAGMENT_NOTE)
    if all(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        for node in statements
    ):
        return Demotion(
            "pytest-only",
            "*Not runnable here — these are pytest test functions; run them "
            "with `pytest`, not in a cell.*",
        )
    return None


Predicate = Callable[[str, "ast.Module | None", Context], "Demotion | None"]

PREDICATES: tuple[Predicate, ...] = (
    demote_shell_not_python,
    demote_repl_transcript,
    demote_unparsable,
    demote_interactive_input,
    demote_debugger,
    demote_process_exit,
    demote_error_demo,
    demote_error_demo_by_output,
    demote_fragment,
    demote_missing_module,
    demote_network_io,
    demote_filesystem_io,
    demote_concurrency,
    demote_slow_sleep,
    demote_endless_loop,
    demote_recursion_demo,
    demote_class_body_only,
    demote_undefined_names,
)


def classify(code: str, ctx: Context) -> Demotion | None:
    """Return the first reason this block cannot be an executable cell."""
    try:
        tree: ast.Module | None = ast.parse(code)
    except SyntaxError:
        tree = None
    if tree is None:
        # No syntax tree, so only the text-only predicates can speak. Ask them in
        # order, then fall back to the deliberate-syntax-error verdict.
        for predicate in (demote_shell_not_python, demote_repl_transcript):
            verdict = predicate(code, tree, ctx)
            if verdict is not None:
                return verdict
        return demote_unparsable(code, tree, ctx)
    for predicate in PREDICATES:
        verdict = predicate(code, tree, ctx)
        if verdict is not None:
            return verdict
    return None


# ---------------------------------------------------------------------------
# notebook assembly
# ---------------------------------------------------------------------------
TITLE_RE = re.compile(r"^# (Day (\d{2}) [—-] .+)$")
TIME_RE = re.compile(r"^> \*\*Time:\*\*\s*(~?[^|]+?)\s*(?:\||$)")


@dataclass
class BuildStats:
    day: Day
    code_cells: int = 0
    markdown_cells: int = 0
    demotions: dict[str, int] = field(default_factory=dict)

    @property
    def total_cells(self) -> int:
        return self.code_cells + self.markdown_cells


def lesson_title(markdown: str, day: Day) -> str:
    for line in markdown.splitlines():
        match = TITLE_RE.match(line)
        if match:
            return match.group(1)
    return f"Day {day.number:02d}"


def lesson_time(markdown: str) -> str:
    for line in markdown.splitlines():
        match = TIME_RE.match(line)
        if match:
            return match.group(1).strip()
    return ""


def preamble_cells(day: Day, title: str, time_estimate: str, portable: bool) -> list[str]:
    estimate = f"**Time:** {time_estimate}  |  " if time_estimate else ""
    link = lambda name: day.course_relative(name, portable)  # noqa: E731
    title_cell = "\n".join(
        [
            f"# {title}",
            "",
            f"{estimate}**Lesson:** [`LESSON.md`]({link('LESSON.md')})"
            f"  |  **Exercises:** [`exercises.py`]({link('exercises.py')})"
            f"  |  **Solutions:** [`solutions.py`]({link('solutions.py')})",
            "",
            "*Generated from the lesson by `tools/build_notebooks.py`. Do not edit "
            "this notebook: edit the lesson and rebuild.*",
        ]
    )
    how_to = "\n".join(
        [
            "## How to use this notebook",
            "",
            "- Click a code cell and press **Shift+Enter** to run it. The output "
            "appears underneath.",
            "- Edit anything and run it again. Break it on purpose. You cannot "
            "damage the course; rebuilding restores this file.",
            "- Cells run **top to bottom** and share state, so run them in order. "
            "If things get tangled, use *Kernel -> Restart and Run All*.",
            "- **Nothing in this notebook is graded.** The graded work is in "
            f"[`exercises.py`]({link('exercises.py')}), and the "
            "last cell here runs the grader for you.",
            "- Some blocks from the lesson appear as text rather than runnable "
            "cells — interactive input, deliberate errors, network calls. Each "
            "one says why on the line above it.",
        ]
    )
    return [title_cell, how_to]


def postamble_cells(day: Day, portable: bool) -> list[tuple[str, str]]:
    """(cell_type, source) pairs appended to every notebook."""
    link = lambda name: day.course_relative(name, portable)  # noqa: E731
    graded = "\n".join(
        [
            "## Now do the graded work",
            "",
            f"1. Open [`exercises.py`]({link('exercises.py')}) "
            "beside this notebook (drag its tab to the right so you can see both).",
            "2. Replace each `raise NotImplementedError(...)` with your "
            "implementation. The docstring says exactly what each function must do.",
            "3. Run the cell below to grade yourself. Repeat until every check "
            "passes.",
            "4. Only then read "
            f"[`solutions.py`]({link('solutions.py')}) and compare.",
            "",
            "You can experiment in this notebook as much as you like, but the "
            "grader only ever reads `exercises.py`.",
        ]
    )
    grade_code = "\n".join(
        [
            "# Grade this day. Works from wherever this notebook happens to run:",
            "# it walks up the folders until it finds the course root's check.py.",
            "import subprocess",
            "import sys",
            "from pathlib import Path",
            "",
            "root = Path.cwd().resolve()",
            'while not (root / "check.py").exists() and root != root.parent:',
            "    root = root.parent",
            "",
            "result = subprocess.run(",
            f'    [sys.executable, str(root / "check.py"), "{day.label}"],',
            "    cwd=root,",
            "    text=True,",
            "    capture_output=True,",
            ")",
            "print(result.stdout or result.stderr)",
        ]
    )
    scratch = "\n".join(
        [
            "# Scratch space. Try anything you like here — nothing in this",
            "# notebook is graded, and you can always rebuild it.",
            "",
        ]
    )
    return [("markdown", graded), ("code", grade_code), ("code", scratch)]


def drop_lesson_header(text: str) -> str:
    """Remove the lesson's own `# Day NN — Title` and `> **Time:** ...` lines.

    Not a rewrite of the author's words: the generated title cell reproduces both
    verbatim a few lines above, and printing them twice looks like a bug.
    """
    kept = [
        line
        for line in text.splitlines()
        if not TITLE_RE.match(line) and not TIME_RE.match(line)
    ]
    return "\n".join(kept).strip("\n")


def classify_lesson(nodes: Sequence[Node]) -> dict[int, Demotion | None]:
    """Decide, for every python fence in a lesson, code cell or markdown cell.

    Two passes. First the static predicates, in order, with each block seeing the
    names the promoted blocks before it defined. Then a dry run of the surviving
    blocks in sequence (see ``dry_run_failures``), which demotes anything that
    still raises — the belt to the static predicates' braces, and the reason
    ``--verify`` can be relied on.
    """
    verdicts: dict[int, Demotion | None] = {}
    ctx = Context()
    for position, node in enumerate(nodes):
        if not isinstance(node, Fence) or node.language != "python":
            continue
        ctx.following_output = expected_output(nodes, position)
        verdict = classify(node.code, ctx)
        verdicts[position] = verdict
        if verdict is None:
            # Only module-level bindings survive into the next cell.
            ctx.names |= bound_names(ast.parse(node.code), nested_scopes=False)

    promoted = [position for position, verdict in verdicts.items() if verdict is None]
    for position, demotion in dry_run_failures(nodes, promoted).items():
        verdicts[position] = demotion
    return verdicts


DRY_RUN_DRIVER = r'''
"""Run a day's candidate code blocks in order and report the first failure.

Called by tools/build_notebooks.py. argv: <blocks.json> <result.json>
"""
import contextlib
import io
import json
import sys

blocks = json.loads(open(sys.argv[1], encoding="utf-8").read())
namespace = {"__name__": "__main__"}
result = {"index": None, "error": None}
for index, code in enumerate(blocks):
    print(index, file=sys.stderr, flush=True)  # progress, so a hang is traceable
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(code, f"<block {index}>", "exec"), namespace)
    except BaseException as failure:  # noqa: BLE001 - reporting, not handling
        result = {"index": index, "error": type(failure).__name__}
        break
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(result))
'''


def dry_run_failures(
    nodes: Sequence[Node], promoted: Sequence[int]
) -> dict[int, Demotion]:
    """Execute the promoted blocks in order; demote whichever one raises.

    Repeats until a clean pass, because removing one block can change what the
    blocks after it see. Runs in a throwaway directory with a timeout, so a block
    that hangs is demoted rather than hanging the build.
    """
    import json
    import subprocess
    import tempfile

    failures: dict[int, Demotion] = {}
    remaining = list(promoted)
    with tempfile.TemporaryDirectory(prefix="pzh-dryrun-") as workdir:
        work = Path(workdir)
        driver = work / "driver.py"
        driver.write_text(DRY_RUN_DRIVER, encoding="utf-8")
        blocks_file = work / "blocks.json"
        result_file = work / "result.json"
        sandbox = work / "cwd"
        sandbox.mkdir()

        for _ in range(len(remaining) + 1):
            codes = [nodes[position].code for position in remaining]  # type: ignore[union-attr]
            blocks_file.write_text(json.dumps(codes), encoding="utf-8")
            if result_file.exists():
                result_file.unlink()
            try:
                finished = subprocess.run(
                    [sys.executable, str(driver), str(blocks_file), str(result_file)],
                    cwd=sandbox,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                progress = finished.stderr
            except subprocess.TimeoutExpired as expired:
                progress = (expired.stderr or b"").decode("utf-8", "replace")
                index = last_progress_index(progress)
                if index is None:
                    break
                position = remaining.pop(index)
                failures[position] = Demotion(
                    "dry-run-hang",
                    "*Not runnable here — it does not finish. Read it, don't run "
                    "it.*",
                )
                continue

            if not result_file.exists():  # the driver itself died; stop guessing
                break
            outcome = json.loads(result_file.read_text(encoding="utf-8"))
            if outcome["index"] is None:
                break
            position = remaining.pop(outcome["index"])
            failures[position] = Demotion(
                "dry-run-failure",
                f"*Not runnable here — running it in order raises "
                f"`{outcome['error']}`, which is the point the lesson is making. "
                f"Read it, don't run it.*",
            )
    return failures


def last_progress_index(progress: str) -> int | None:
    numbers = [line.strip() for line in progress.splitlines() if line.strip().isdigit()]
    return int(numbers[-1]) if numbers else None


def expected_output(nodes: Sequence[Node], position: int) -> str:
    """The unlabelled fence that follows a python block, i.e. its shown output.

    "Follows" tolerates one short prose bridge such as "Output:" or "prints:".
    """
    for node in nodes[position + 1 : position + 3]:
        if isinstance(node, Fence):
            return node.code if node.language in {"", "text", "output"} else ""
        if len(node.text.strip()) > 80:  # a real paragraph, not a caption
            return ""
    return ""


def build_notebook(day: Day, portable: bool = False) -> tuple[nbformat.NotebookNode, BuildStats]:
    markdown = day.lesson.read_text(encoding="utf-8")
    title = lesson_title(markdown, day)
    stats = BuildStats(day=day)
    sources: list[tuple[str, str]] = []

    for cell in preamble_cells(day, title, lesson_time(markdown), portable):
        sources.append(("markdown", cell))

    nodes = parse_lesson(markdown)
    verdicts = classify_lesson(nodes)
    seen_prose = False

    for position, node in enumerate(nodes):
        if isinstance(node, Prose):
            text = node.text
            if not seen_prose:
                # The title cell above already carries the H1 and the time line.
                text = drop_lesson_header(text)
                seen_prose = True
            if text.strip():
                sources.append(("markdown", text))
            continue

        if node.language != "python":
            # Output samples, diagrams, shell sessions, JSON/TOML/YAML: prose.
            sources.append(("markdown", node.rendered))
            continue

        verdict = verdicts[position]
        if verdict is None:
            sources.append(("code", node.code))
        else:
            stats.demotions[verdict.kind] = stats.demotions.get(verdict.kind, 0) + 1
            sources.append(("markdown", f"{verdict.note}\n\n{node.rendered}"))

    sources.extend(postamble_cells(day, portable))

    notebook = new_notebook()
    notebook.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "file_extension": ".py",
            "mimetype": "text/x-python",
        },
    }
    notebook.nbformat = NBFORMAT_MAJOR
    notebook.nbformat_minor = NBFORMAT_MINOR
    notebook.cells = []
    for index, (kind, source) in enumerate(sources, start=1):
        text = source.strip("\n")
        if not text.strip():
            continue
        if kind == "code":
            cell = new_code_cell(text)
            cell["execution_count"] = None
            cell["outputs"] = []
            stats.code_cells += 1
        else:
            cell = new_markdown_cell(text)
            stats.markdown_cells += 1
        cell["metadata"] = {}
        cell["id"] = f"cell-{index:04d}"  # deterministic: no random ids
        notebook.cells.append(cell)

    return notebook, stats


def serialise(notebook: nbformat.NotebookNode) -> str:
    return nbformat.writes(notebook, version=NBFORMAT_MAJOR).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# notebooks/README.md
# ---------------------------------------------------------------------------
def notebooks_readme(days: Sequence[Day]) -> str:
    rows = "\n".join(
        f"| {day.number:02d} | [`{day.slug}.ipynb`]({day.slug}.ipynb) | "
        f"[lesson]({day.course_relative('LESSON.md')}) |"
        for day in days
    )
    return f"""# Notebooks (generated — do not edit)

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
python tools/build_notebooks.py            # rebuild all {len(days)} notebooks
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
{rows}

## Taking it with you

`portable/` is the same {len(days)} notebooks packaged as one self-contained
folder — grader, day folders and reference docs included — for copying to a
laptop or an iPad. See `portable/README.md`. It is generated by the same build,
so it cannot drift either.
"""


# ---------------------------------------------------------------------------
# notebooks/portable/ — the one-folder, take-it-anywhere bundle
# ---------------------------------------------------------------------------
def bundle_readme(days: Sequence[Day]) -> str:
    return f"""# Python Zero to Hero — portable notebooks

This one folder is the whole course as notebooks: {len(days)} days of lesson text
with runnable code, plus the exercises, the reference solutions and the grader.
Copy it anywhere. Nothing outside it is needed.

Like everything under `notebooks/`, this folder is **generated** from
`course/weekN/dayNN_slug/LESSON.md` by `tools/build_notebooks.py`. Edit lessons,
not notebooks.

## What is in here

```
day01_getting_started.ipynb ... day21_project_capstone_pipeline.ipynb
course/weekN/dayNN_slug/      LESSON.md, examples.py, exercises.py,
                              solutions.py, test_exercises.py
reference/                    glossary, error messages, debugging playbook
check.py, conftest.py         the grader (pytest under the hood)
CHEATSHEET.md, SYLLABUS.md    lookup reference and the 21-day plan
requirements.txt              what to install
```

## Running it on a laptop

```bash
cd portable
python -m pip install -r requirements.txt
python -m jupyterlab           # or: python -m notebook
```

Open `day01_getting_started.ipynb` and work down the page. Shift+Enter runs a
cell. The last code cell of each notebook grades that day by running
`check.py dayNN` from this folder, so grading works here exactly as it does in
the full repository.

You can also grade from a terminal without Jupyter at all:

```bash
python check.py day01
python check.py            # progress across all {len(days)} days
```

## Running it on an iPad

Any app that runs a real CPython kernel works — Juno, Carnets, a-Shell, or a
remote JupyterLab you reach through Safari. Copy this folder in (Files, iCloud
Drive, git clone in a-Shell), then open a notebook.

Two honest caveats on tablets:

- The **notebooks** run anywhere with a Python 3.10+ kernel.
- The **grading cell** additionally needs `pytest` and the ability to start a
  subprocess. Where an app forbids subprocesses, grade in a terminal app instead,
  or `import pytest; pytest.main(["course/week1/day01_getting_started"])` from a
  cell.

Blocks that need the network or the filesystem are already marked "not runnable
here" in the notebooks, so an offline tablet loses nothing.

## Editing your answers

`exercises.py` files in here are yours to fill in — this is a copy, so your work
stays in this folder. If you also work in the main repository, keep to one of the
two, because a rebuild of this bundle overwrites these copies with fresh stubs
from the course.
"""


def bundle_requirements() -> str:
    return """# Everything the portable notebooks need.
# The course itself only needs pytest; the rest is the Jupyter runtime.
pytest>=8.0
jupyterlab>=4.0
ipykernel>=6.0
"""


def bundle_payload(days: Sequence[Day]) -> dict[str, str]:
    """The complete portable bundle as {path relative to portable/: text}.

    Built in memory so that both the writer and ``--check`` see the same bytes.
    """
    payload: dict[str, str] = {}
    for day in days:
        notebook, _ = build_notebook(day, portable=True)
        payload[f"{day.slug}.ipynb"] = serialise(notebook)
        for filename in BUNDLE_DAY_FILES:
            source = day.directory / filename
            if source.is_file():
                payload[f"course/week{day.week}/{day.slug}/{filename}"] = source.read_text(
                    encoding="utf-8"
                )
    for filename in BUNDLE_ROOT_FILES:
        source = ROOT / filename
        if source.is_file():
            payload[filename] = source.read_text(encoding="utf-8")
    for source in sorted((ROOT / "reference").glob("*.md")):
        payload[f"reference/{source.name}"] = source.read_text(encoding="utf-8")
    payload["README.md"] = bundle_readme(days)
    payload["requirements.txt"] = bundle_requirements()
    return payload


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------
def select_days(days: Sequence[Day], wanted: str | None) -> list[Day]:
    if wanted is None:
        return list(days)
    text = wanted.lower().removeprefix("day").lstrip("0") or "0"
    if not text.isdigit():
        raise SystemExit(f"build_notebooks: cannot understand --day {wanted!r}")
    number = int(text)
    matches = [day for day in days if day.number == number]
    if not matches:
        raise SystemExit(f"build_notebooks: no day {number:02d} under {COURSE}")
    return matches


def command_build(days: Sequence[Day], all_days: Sequence[Day]) -> int:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    stats: list[BuildStats] = []
    for day in days:
        notebook, day_stats = build_notebook(day)
        day.notebook.write_text(serialise(notebook), encoding="utf-8")
        stats.append(day_stats)
    (NOTEBOOKS / "README.md").write_text(notebooks_readme(all_days), encoding="utf-8")

    # The portable bundle is always rebuilt whole: it is a shippable folder, and
    # half of it being stale would be worse than useless.
    written = 0
    for relative, text in bundle_payload(all_days).items():
        target = PORTABLE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        written += 1

    report(stats)
    print(f"\nwrote {len(stats)} notebook(s) + README.md to {NOTEBOOKS.relative_to(ROOT)}/")
    print(f"wrote {written} files to {PORTABLE.relative_to(ROOT)}/ (the take-anywhere bundle)")
    return 0


def command_check(days: Sequence[Day], all_days: Sequence[Day]) -> int:
    stale: list[str] = []
    for day in days:
        notebook, _ = build_notebook(day)
        expected = serialise(notebook)
        if not day.notebook.exists():
            stale.append(f"{day.notebook.name}: missing")
            continue
        actual = day.notebook.read_text(encoding="utf-8")
        if actual != expected:
            stale.append(
                f"{day.notebook.name}: stale "
                f"(on disk {digest(actual)}, expected {digest(expected)})"
            )
    readme = NOTEBOOKS / "README.md"
    expected_readme = notebooks_readme(all_days)
    if not readme.exists() or readme.read_text(encoding="utf-8") != expected_readme:
        stale.append("README.md: stale or missing")

    payload = bundle_payload(all_days)
    for relative, expected_text in payload.items():
        target = PORTABLE / relative
        if not target.is_file():
            stale.append(f"portable/{relative}: missing")
        elif is_learner_owned(relative):
            # exercises.py in the bundle is a seeded stub the learner writes into.
            # A rebuild reseeds it, but a learner's answers must not fail CI.
            continue
        elif target.read_text(encoding="utf-8") != expected_text:
            stale.append(f"portable/{relative}: stale")
    if PORTABLE.is_dir():
        for existing in sorted(PORTABLE.rglob("*")):
            if existing.is_dir() or is_transient(existing):
                continue
            relative = existing.relative_to(PORTABLE).as_posix()
            if relative not in payload:
                stale.append(f"portable/{relative}: not part of the bundle any more")

    if stale:
        print("Notebooks are out of date with the lessons:")
        for line in stale:
            print(f"  {line}")
        print("\nRun: python tools/build_notebooks.py")
        return 1
    print(
        f"up to date: {len(days)} notebook(s) and the portable bundle "
        f"({len(payload)} files) match their lessons"
    )
    return 0


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def is_learner_owned(relative: str) -> bool:
    return relative.endswith("/exercises.py")


TRANSIENT = {".pzh_progress.json", "__pycache__", ".ipynb_checkpoints", ".pytest_cache"}


def is_transient(path: Path) -> bool:
    """Caches and grader state that appear when the bundle is used, not built."""
    return any(part in TRANSIENT for part in path.parts) or path.suffix in {".pyc", ".pyo"}


def command_verify(days: Sequence[Day]) -> int:
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError, CellTimeoutError

    targets: list[tuple[str, Path, Path]] = []
    for day in days:
        targets.append((day.notebook.name, day.notebook, NOTEBOOKS))
        targets.append((f"portable/{day.bundle_notebook.name}", day.bundle_notebook, PORTABLE))

    def run_one(target: tuple[str, Path, Path]) -> tuple[str, int, int, str | None]:
        label, path, workdir = target
        if not path.exists():
            return label, 0, 0, "missing; run the build first"
        notebook = nbformat.read(path, as_version=NBFORMAT_MAJOR)
        code_cells = sum(1 for cell in notebook.cells if cell.cell_type == "code")
        markdown_cells = sum(1 for cell in notebook.cells if cell.cell_type == "markdown")
        client = NotebookClient(
            notebook,
            timeout=120,
            kernel_name="python3",
            allow_errors=False,
            # Run with the notebook's own folder as the working directory, exactly
            # as a learner's Jupyter session would.
            resources={"metadata": {"path": str(workdir)}},
        )
        try:
            client.execute()
        except (CellExecutionError, CellTimeoutError) as error:
            source = first_error_source(notebook)
            if source == "?":  # a timeout produces no error output, but does
                source = timeout_preview(str(error))  # quote the cell it hung on
            return label, code_cells, markdown_cells, f"{summarise(error)}\n      cell: {source}"
        return label, code_cells, markdown_cells, None

    failures: list[str] = []
    executed_total = 0
    markdown_total = 0
    print(f"{'notebook':44} {'code':>5} {'md':>5}")
    with ThreadPoolExecutor(max_workers=4) as pool:  # one kernel per worker
        for label, code_cells, markdown_cells, problem in pool.map(run_one, targets):
            if problem is not None:
                failures.append(f"{label}: {problem}")
                print(f"{'FAIL ' + label:44} {code_cells:>5} {markdown_cells:>5}")
                continue
            executed_total += code_cells
            markdown_total += markdown_cells
            print(f"{label:44} {code_cells:>5} {markdown_cells:>5}")

    if failures:
        print("\nCell errors:")
        for line in failures:
            print(f"  {line}")
        return 1
    print(
        f"\nall {len(targets)} notebook(s) executed cleanly: "
        f"{executed_total} code cells run, {markdown_total} markdown cells"
    )
    return 0


def first_error_source(notebook: nbformat.NotebookNode) -> str:
    """The source of the cell that produced the first error output, for the report."""
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                return cell.source.strip().replace("\n", " ⏎ ")[:160]
    return "?"


def timeout_preview(message: str) -> str:
    body = message.split("-------------------")
    if len(body) >= 2:
        return " ⏎ ".join(line for line in body[1].splitlines() if line.strip())[:160]
    return "?"


def summarise(error: Exception) -> str:
    lines = [line.strip() for line in str(error).splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"(Error|Exception|timed out)", line):
            return line
    return lines[-1] if lines else str(error)


def command_explain(days: Sequence[Day]) -> int:
    """List every demoted block and the predicate responsible for it."""
    for day in days:
        nodes = parse_lesson(day.lesson.read_text(encoding="utf-8"))
        verdicts = classify_lesson(nodes)
        print(f"\n{day.slug}")
        for position, verdict in sorted(verdicts.items()):
            if verdict is None:
                continue
            first = next(
                (
                    line
                    for line in nodes[position].code.splitlines()  # type: ignore[union-attr]
                    if line.strip()
                ),
                "",
            )
            print(f"  {verdict.kind:18} {first.strip()[:90]}")
    return 0


def report(stats: Sequence[BuildStats]) -> None:
    print(f"{'notebook':44} {'code':>5} {'md':>5} {'demoted':>8}")
    totals = {"code": 0, "md": 0, "demoted": 0}
    demotions: dict[str, int] = {}
    for item in stats:
        demoted = sum(item.demotions.values())
        print(
            f"{item.day.slug + '.ipynb':44} {item.code_cells:>5} "
            f"{item.markdown_cells:>5} {demoted:>8}"
        )
        totals["code"] += item.code_cells
        totals["md"] += item.markdown_cells
        totals["demoted"] += demoted
        for kind, count in item.demotions.items():
            demotions[kind] = demotions.get(kind, 0) + count
    print(
        f"{'TOTAL':44} {totals['code']:>5} {totals['md']:>5} {totals['demoted']:>8}"
    )
    if demotions:
        print("\ndemoted python blocks by predicate:")
        for kind, count in sorted(demotions.items(), key=lambda pair: -pair[1]):
            print(f"  {kind:20} {count:>4}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the course notebooks from each day's LESSON.md.",
    )
    parser.add_argument("--day", help="only this day, e.g. 05, day05, 5")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any committed notebook differs from a fresh build",
    )
    mode.add_argument(
        "--verify",
        action="store_true",
        help="execute every notebook and fail on the first cell error",
    )
    mode.add_argument(
        "--explain",
        action="store_true",
        help="list every demoted code block and the predicate that demoted it",
    )
    args = parser.parse_args(argv)

    all_days = discover_days()
    if not all_days:
        print(f"build_notebooks: no day folders under {COURSE}", file=sys.stderr)
        return 1
    days = select_days(all_days, args.day)

    if args.check:
        return command_check(days, all_days)
    if args.verify:
        return command_verify(days)
    if args.explain:
        return command_explain(days)
    return command_build(days, all_days)


if __name__ == "__main__":
    raise SystemExit(main())
