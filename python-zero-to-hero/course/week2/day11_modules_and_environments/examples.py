"""Day 11 — Modules and environments: runnable demonstrations.

Run me from the course root:

    python course/week2/day11_modules_and_environments/examples.py

I import the `textkit/` package that ships next to me, and I build a throwaway
package inside `tmp/` to show sys.path and circular imports for real. Everything
in tmp/ is deleted on the way out. Section numbers match LESSON.md.
"""

import importlib
import sys

# Do this BEFORE importing anything of our own: no __pycache__ folders get
# written, so this demo leaves the repository byte-for-byte unchanged.
sys.dont_write_bytecode = True

from pathlib import Path  # noqa: E402 - after the line above, on purpose

import textkit  # noqa: E402 - the package that ships in this folder
import textkit.stats  # noqa: E402
from textkit.cleaning import normalize  # noqa: E402
from textkit.cleaning import normalize as clean  # noqa: E402

HERE = Path(__file__).parent
TMP = HERE / "tmp"


def path_depth(path: Path) -> int:
    """How many parts a path has. Used as a sort key, so deepest is deleted first."""
    return len(path.parts)


def cleanup(folder: Path) -> None:
    """Delete `folder` and everything inside it (files, then dirs, deepest first)."""
    if not folder.exists():
        return
    children = sorted(folder.rglob("*"), key=path_depth, reverse=True)
    for child in children:
        if child.is_file():
            child.unlink()
        else:
            child.rmdir()
    folder.rmdir()


def has_version_operator(text: str) -> bool:
    """True when a requirement line pins a version with a comparison operator."""
    for operator in ("==", ">=", "<=", "~=", ">", "<"):
        if operator in text:
            return True
    return False


def section(number: str, title: str) -> None:
    print()
    print("=" * 70)
    print(f"{number}. {title}")
    print("=" * 70)


def main() -> None:
    # -----------------------------------------------------------------------
    # 1. A module is a file that runs once and becomes an object
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("1. Modules are objects")
    print("=" * 70)

    print("textkit               ->", textkit)
    print("type(textkit)         ->", type(textkit).__name__)
    print("textkit.__name__      ->", textkit.__name__)
    print("textkit.__version__   ->", textkit.__version__)
    print("textkit.__file__      ->", Path(textkit.__file__).name, "(the package's __init__.py)")
    public_names = []
    for name in dir(textkit):
        if not name.startswith("_"):
            public_names.append(name)
    print("dir(textkit) (public) ->", public_names)

    # The import is cached: importing again does not re-run the file.
    print()
    print("'textkit' in sys.modules ->", "textkit" in sys.modules)
    print("'textkit.stats' in sys.modules ->", "textkit.stats" in sys.modules)
    # Importing again produces no new work. Note the alias: a plain
    # `import textkit` HERE would make `textkit` a local name inside main() and
    # break every use above it with UnboundLocalError — Day 8's scope rule,
    # applied to imports.
    import textkit as textkit_again

    print("re-importing did nothing new; the module object is the same:",
          sys.modules["textkit"] is textkit_again is textkit)

    # -----------------------------------------------------------------------
    # 2. The import forms
    # -----------------------------------------------------------------------
    section("2", "The import forms, all reaching the same function")

    sample = "  The cat, the DOG.   The cat!  "
    print("import textkit           ->", textkit.normalize(sample))
    print("import textkit.cleaning  ->", textkit.cleaning.normalize(sample))
    print("from ... import normalize->", normalize(sample))
    print("... import ... as clean  ->", clean(sample))
    print("all four are the same object ->",
          textkit.normalize is normalize is clean is textkit.cleaning.normalize)
    print()
    print("Prefer `import textkit` / `textkit.normalize(...)`: the prefix tells a")
    print("reader where the name came from, and nothing local can shadow it.")

    # -----------------------------------------------------------------------
    # 3. __name__
    # -----------------------------------------------------------------------
    section("3", '__name__ and the "__main__" guard')

    print("this file's __name__        ->", repr(__name__))
    print("textkit.stats.__name__      ->", repr(textkit.stats.__name__))
    print("So `if __name__ == \"__main__\":` is true here and false in stats.py,")
    print("which is why importing textkit.stats did not print its demo output.")
    print("Run it as a program instead:  python -m textkit.stats")

    # -----------------------------------------------------------------------
    # 4/5. Packages, __init__.py, relative imports
    # -----------------------------------------------------------------------
    section("4/5", "Packages, __init__.py and relative imports")

    print("textkit/ contains:")
    for child in sorted((HERE / "textkit").iterdir()):
        if child.suffix == ".py":
            print(f"  {child.name:<14}{child.stat().st_size:>5} bytes")

    print()
    print("stats.py says `from .cleaning import normalize` — one dot = my own package.")
    print("textkit.stats.word_counts(sample) ->", textkit.stats.word_counts(sample))
    print("textkit.top_words(sample, 2)      ->", textkit.top_words(sample, 2))
    print()
    print("__init__.py re-exported those names, which is why both of these work:")
    print("  textkit.word_counts ->", textkit.word_counts.__name__)
    print("  textkit.stats.word_counts ->", textkit.stats.word_counts.__name__)
    print("It also did `from . import stats`; without that line, `textkit.stats`")
    print("would raise AttributeError even though the file exists.")

    # -----------------------------------------------------------------------
    # 6. sys.path: how Python finds modules
    # -----------------------------------------------------------------------
    section("6", "sys.path — first match wins")

    print("sys.path, in search order:")
    for index, entry in enumerate(sys.path):
        label = ""
        if index == 0:
            label = "  <- the directory of the script you ran"
        elif "site-packages" in entry:
            label = "  <- where pip installs things"
        print(f"  [{index}] {entry!r}{label}")

    print()
    import json

    print("json.__file__ ->", json.__file__)
    print("If that path ever points inside your project, you have a file called")
    print("json.py shadowing the standard library. That is the whole bug.")

    # Build a throwaway package in tmp/ and put it on sys.path by hand.
    TMP.mkdir(parents=True, exist_ok=True)
    package = TMP / "sandbox_pkg"
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text(
        '"""A package created at runtime, purely to prove a point."""\n'
        "ORIGIN = 'tmp/sandbox_pkg'\n",
        encoding="utf-8",
    )
    (package / "tools.py").write_text(
        "def shout(text: str) -> str:\n"
        '    """Return text in capitals with an exclamation mark."""\n'
        "    return text.upper() + '!'\n",
        encoding="utf-8",
    )

    # Python caches which files each directory holds, so after CREATING modules
    # at runtime you must invalidate that cache or the import will not see them.
    importlib.invalidate_caches()

    print()
    print("created tmp/sandbox_pkg/ at runtime; importing it before touching sys.path:")
    try:
        import sandbox_pkg  # noqa: F401
    except ModuleNotFoundError as error:
        print("  ->", type(error).__name__ + ":", error)
        print("  (tmp/ is not on sys.path, so Python cannot see it)")

    sys.path.insert(0, str(TMP))  # a last resort in real code; fine for a demo
    import sandbox_pkg
    import sandbox_pkg.tools

    print("  after sys.path.insert(0, tmp): imported", sandbox_pkg.ORIGIN)
    print("  sandbox_pkg.tools.shout('hi') ->", sandbox_pkg.tools.shout("hi"))
    print("  ModuleNotFoundError is an ImportError? ->",
          issubclass(ModuleNotFoundError, ImportError))

    # -----------------------------------------------------------------------
    # 7. Circular imports, for real
    # -----------------------------------------------------------------------
    section("7", "A circular import, caused and then fixed")

    (TMP / "orders.py").write_text(
        "from customers import find_customer\n"
        "\n"
        "def order_total(order):\n"
        "    customer = find_customer(order['customer_id'])\n"
        "    return order['amount'] * customer['discount']\n",
        encoding="utf-8",
    )
    (TMP / "customers.py").write_text(
        "from orders import order_total\n"
        "\n"
        "CUSTOMERS = {1: {'discount': 0.9}}\n"
        "\n"
        "def find_customer(customer_id):\n"
        "    return CUSTOMERS[customer_id]\n",
        encoding="utf-8",
    )

    importlib.invalidate_caches()  # the two files above were just created
    print("orders.py does `from customers import find_customer`")
    print("customers.py does `from orders import order_total`")
    try:
        import orders  # noqa: F401
    except ImportError as error:
        print("importing orders ->", type(error).__name__ + ":")
        print("  ", error)
        print("  'partially initialized' is the tell: orders.py was half-executed")
        print("  when customers.py asked it for a name that did not exist yet.")

    # Fix 3 from the lesson: import the MODULE, look the name up at call time.
    # Both sides have to stop asking for NAMES at import time — binding a
    # half-built module object is fine, reaching inside it is not.
    for name in ("orders", "customers"):
        sys.modules.pop(name, None)  # forget the failed attempt
    (TMP / "orders.py").write_text(
        "import customers          # not `from customers import ...`\n"
        "\n"
        "def order_total(order):\n"
        "    # customers.find_customer is looked up when this RUNS, by which\n"
        "    # time both modules are fully loaded.\n"
        "    customer = customers.find_customer(order['customer_id'])\n"
        "    return order['amount'] * customer['discount']\n",
        encoding="utf-8",
    )
    (TMP / "customers.py").write_text(
        "import orders             # the module object only\n"
        "\n"
        "CUSTOMERS = {1: {'discount': 0.9}}\n"
        "\n"
        "def find_customer(customer_id):\n"
        "    return CUSTOMERS[customer_id]\n"
        "\n"
        "def customer_value(customer):\n"
        "    total = 0.0\n"
        "    for order in customer['orders']:\n"
        "        total += orders.order_total(order)   # resolved at CALL time\n"
        "    return total\n",
        encoding="utf-8",
    )
    importlib.invalidate_caches()  # both files were just rewritten
    import orders

    print()
    print("after switching BOTH files to `import module` + late attribute lookup:")
    print("  orders.order_total({'customer_id': 1, 'amount': 100}) ->",
          orders.order_total({"customer_id": 1, "amount": 100}))
    print("  (the better fix is usually to extract the shared code into a third")
    print("   module that neither of them depends on — see LESSON.md section 7)")

    # -----------------------------------------------------------------------
    # 8/9. Environments and requirements
    # -----------------------------------------------------------------------
    section("8/9", "Environments, pip and requirements.txt")

    print("sys.executable ->", sys.executable)
    print("sys.prefix     ->", sys.prefix)
    print("sys.base_prefix->", sys.base_prefix)
    in_venv = sys.prefix != sys.base_prefix
    print("inside a virtual environment? ->", in_venv,
          "(they differ when you are in one)")
    print()
    print("The four commands that make any project reproducible:")
    print("  python -m venv .venv")
    print("  source .venv/bin/activate          # .venv\\Scripts\\activate on Windows")
    print("  python -m pip install -r requirements.txt")
    print("  python -m pytest")

    # Parsing a requirements file is today's exercise material, so here is the
    # shape of the data you will be working with.
    requirements_text = "\n".join([
        "# runtime",
        "requests==2.31.0",
        "rich>=13.0,<14",
        "",
        "# tooling",
        "pytest==8.2.0",
        "ruff",
        "-r dev-requirements.txt",
    ])
    print()
    print("a realistic requirements.txt:")
    for number, line in enumerate(requirements_text.split("\n"), start=1):
        kind = "package"
        stripped = line.strip()
        if not stripped:
            kind = "blank   (ignored)"
        elif stripped.startswith("#"):
            kind = "comment (ignored)"
        elif stripped.startswith("-"):
            kind = "option  (not a package)"
        elif not has_version_operator(stripped):
            kind = "package (UNPINNED)"
        print(f"  line {number}: {line!r:<30} {kind}")

    print()
    print("pinned (==) means reproducible; unpinned means 'whatever exists today'.")
    print("Applications pin exactly. Libraries specify ranges.")
    print("`pip freeze` prints every installed package, including ones you never")
    print("asked for (pytest drags in pluggy, iniconfig, packaging).")

    print()
    print("files created during this demo (all inside tmp/, about to be deleted):")
    for child in sorted(TMP.rglob("*")):
        marker = "/" if child.is_dir() else ""
        print(f"  {child.relative_to(HERE)}{marker}")


if __name__ == "__main__":
    try:
        main()
    finally:
        # Undo the sys.path edit and delete tmp/, whatever happened above.
        if str(TMP) in sys.path:
            sys.path.remove(str(TMP))
        cleanup(TMP)
        print()
        print("tmp/ removed and sys.path restored — the repository is unchanged.")
        print("Done. Now do LESSON.md section 10 by hand, then open exercises.py.")
