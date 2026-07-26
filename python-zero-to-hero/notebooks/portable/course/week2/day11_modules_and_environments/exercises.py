"""Day 11 exercises — Modules and environments.

Today's exercises are the tooling you would write to *reason about* imports and
dependencies: requirement parsing, version checks, relative-import resolution,
module lookup, and cycle detection. They are all pure functions, so you can test
your understanding without a package manager involved.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

Grade your work from the course root:

    python check.py day11
    python check.py day11 -v      # show full failure detail
"""

from __future__ import annotations

# The comparison operators a requirement line may use. Two-character operators
# come first, because "==" must be recognised before "=" -like single characters.
OPERATORS = ("==", ">=", "<=", "~=", ">", "<")


# ---------------------------------------------------------------------------
# Exercise 1 — parse one requirements.txt line
# ---------------------------------------------------------------------------
def parse_requirement(line: str) -> tuple[str, str, str] | None:
    """Split one requirements.txt line into (name, operator, version).

    Rules:
      * Everything from a "#" onwards is a comment and is discarded.
      * A line that is empty after that is not a requirement -> return None.
      * A line starting with "-" is a pip option, e.g. "-r other.txt" -> None.
      * The name is lowercased and stripped. Package names are case-insensitive.
      * Look for the operators in OPERATORS. Everything after the operator is
        the version text, kept as-is (so a range stays in one piece).
      * No operator at all means unpinned: operator and version are both "".

    Args:
        line: one raw line from a requirements file.

    Returns:
        A (name, operator, version) tuple, or None for a line that declares
        no package.

    Raises:
        ValueError: when there is an operator but no name, with the message
            f"cannot parse requirement: {line!r}".

    Examples:
        parse_requirement("requests==2.31.0") -> ("requests", "==", "2.31.0")
        parse_requirement("pytest >= 8.0") -> ("pytest", ">=", "8.0")
        parse_requirement("Rich") -> ("rich", "", "")
        parse_requirement("rich>=13.0,<14") -> ("rich", ">=", "13.0,<14")
        parse_requirement("pytest==8.2.0  # for tests") -> ("pytest", "==", "8.2.0")
        parse_requirement("# a comment") -> None
        parse_requirement("   ") -> None
        parse_requirement("-r dev-requirements.txt") -> None
        parse_requirement("==1.0") -> raises ValueError
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: parse_requirement")


# ---------------------------------------------------------------------------
# Exercise 2 — parse a whole file
# ---------------------------------------------------------------------------
def parse_requirements(text: str) -> dict[str, str]:
    """Turn the text of a requirements file into {name: spec}.

    `spec` is the operator and version joined back together ("==2.31.0"), or ""
    for an unpinned package. Skip every line that `parse_requirement` calls
    None. If a name appears twice, the last line wins.

    Args:
        text: the whole file contents, newlines included.

    Returns:
        A dict mapping package name to spec string.

    Examples:
        text = "# runtime\\nrequests==2.31.0\\n\\nrich\\npytest>=8.0\\n"
        parse_requirements(text) ->
            {"requests": "==2.31.0", "rich": "", "pytest": ">=8.0"}

        parse_requirements("") -> {}
        parse_requirements("pytest==8.0\\npytest==8.2\\n") -> {"pytest": "==8.2"}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: parse_requirements")


# ---------------------------------------------------------------------------
# Exercise 3 — does an installed version satisfy a spec?
# ---------------------------------------------------------------------------
def version_satisfies(installed: str, spec: str) -> bool:
    """Return True when version `installed` satisfies `spec`.

    A spec is one or more comma-separated comparisons, e.g. ">=13.0,<14".
    Every comparison must hold. An empty spec accepts anything.

    Compare versions component by component as integers, padding the shorter
    one with zeros — so "8.0" and "8.0.0" are equal, and "1.10" is greater than
    "1.9" (10 > 9, which string comparison would get wrong).

    Operators: "==", ">=", "<=", ">", "<", and "~=" (compatible release).
    "~=1.4.2" means "at least 1.4.2, and the components before the last one
    must still match" — so 1.4.9 satisfies it and 1.5.0 does not.

    Args:
        installed: a dotted version string, e.g. "2.31.0".
        spec: the comparison(s) to check, e.g. ">=2.0" or "" for no constraint.

    Returns:
        True if every comparison holds.

    Raises:
        ValueError: if a comparison does not start with a known operator, or a
            version component is not a whole number.

    Examples:
        version_satisfies("2.31.0", "==2.31.0") -> True
        version_satisfies("2.31.0", "") -> True
        version_satisfies("8.1", ">=8.0") -> True
        version_satisfies("7.4", ">=8.0") -> False
        version_satisfies("1.10", ">=1.9") -> True
        version_satisfies("8.0", "==8.0.0") -> True
        version_satisfies("13.5", ">=13.0,<14") -> True
        version_satisfies("14.1", ">=13.0,<14") -> False
        version_satisfies("1.4.9", "~=1.4.2") -> True
        version_satisfies("1.5.0", "~=1.4.2") -> False
        version_satisfies("1.0", "!!1.0") -> raises ValueError
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: version_satisfies")


# ---------------------------------------------------------------------------
# Exercise 4 — what is wrong with this environment?
# ---------------------------------------------------------------------------
def missing_requirements(
    required: dict[str, str], installed: dict[str, str]
) -> list[str]:
    """Report every requirement that the installed packages fail to meet.

    Check the required packages in alphabetical order by name, and produce
    exactly these messages:
        not installed at all  -> f"{name} is not installed"
        wrong version         -> f"{name} {installed_version} does not satisfy {spec}"
    Packages that are installed but not required are none of your business.

    Args:
        required: {name: spec} as produced by parse_requirements.
        installed: {name: version} of what is actually present.

    Returns:
        A list of problem messages, ordered by package name. Empty when the
        environment is fine.

    Examples:
        required = {"pytest": ">=8.0", "requests": "==2.31.0", "rich": ""}
        installed = {"pytest": "7.4.0", "rich": "13.7.1"}
        missing_requirements(required, installed) ->
            ["pytest 7.4.0 does not satisfy >=8.0",
             "requests is not installed"]

        missing_requirements({}, {"pytest": "8.0"}) -> []
        missing_requirements({"rich": ""}, {"rich": "1.0"}) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: missing_requirements")


# ---------------------------------------------------------------------------
# Exercise 5 — what `pip freeze` prints
# ---------------------------------------------------------------------------
def freeze_lines(installed: dict[str, str]) -> list[str]:
    """Return `pip freeze` style lines for the installed packages.

    One "name==version" line per package, sorted case-insensitively by name so
    the output is stable between runs (which is what makes it diffable).

    Args:
        installed: {name: version}.

    Returns:
        A list of exactly pinned requirement lines.

    Examples:
        freeze_lines({"pytest": "8.2.0", "iniconfig": "2.0.0"}) ->
            ["iniconfig==2.0.0", "pytest==8.2.0"]
        freeze_lines({"Rich": "13.7.1", "attrs": "23.2.0"}) ->
            ["attrs==23.2.0", "Rich==13.7.1"]
        freeze_lines({}) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: freeze_lines")


# ---------------------------------------------------------------------------
# Exercise 6 — resolve a relative import by hand
# ---------------------------------------------------------------------------
def resolve_relative_import(current_module: str, relative: str) -> str:
    """Turn a relative import into the absolute module name it refers to.

    One leading dot means "the package this module lives in"; each extra dot
    goes one package further up. The text after the dots, if any, is appended.

    Args:
        current_module: the dotted name of the module doing the import,
            e.g. "pkg.sub.mod".
        relative: the relative target, e.g. ".helpers", "..util", ".".

    Returns:
        The absolute dotted module name.

    Raises:
        ValueError: if `relative` does not start with a dot
            (f"not a relative import: {relative!r}"), or if the dots go above
            the top-level package ("too many leading dots").

    Examples:
        resolve_relative_import("pkg.sub.mod", ".helpers") -> "pkg.sub.helpers"
        resolve_relative_import("pkg.sub.mod", "..util") -> "pkg.util"
        resolve_relative_import("pkg.sub.mod", ".") -> "pkg.sub"
        resolve_relative_import("pkg.sub.mod", "..") -> "pkg"
        resolve_relative_import("pkg.mod", ".a.b") -> "pkg.a.b"
        resolve_relative_import("pkg.mod", "...x") -> raises ValueError
        resolve_relative_import("pkg.mod", "other") -> raises ValueError
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: resolve_relative_import")


# ---------------------------------------------------------------------------
# Exercise 7 — simulate the sys.path search
# ---------------------------------------------------------------------------
def module_search_order(
    sys_path: list[str], module: str, present: dict[str, list[str]]
) -> str | None:
    """Return the directory Python would import `module` from — first match wins.

    This is the search from LESSON.md section 6, with the filesystem replaced by
    a dict so it is testable: `present` maps a directory to the module names
    available in it.

    Args:
        sys_path: directories in search order.
        module: the module name being imported.
        present: {directory: [module names available there]}.

    Returns:
        The first directory in `sys_path` that offers `module`, or None when no
        directory does (which is a ModuleNotFoundError in real life).

    Examples:
        path = ["", "/usr/lib/python3.11", "/venv/site-packages"]
        present = {"": ["myapp", "json"], "/usr/lib/python3.11": ["json", "csv"]}
        module_search_order(path, "json", present) -> ""
            # your local json.py shadows the standard library — the classic bug
        module_search_order(path, "csv", present) -> "/usr/lib/python3.11"
        module_search_order(path, "requests", present) -> None
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: module_search_order")


# ---------------------------------------------------------------------------
# Exercise 8 — the hard one: find a circular import
# ---------------------------------------------------------------------------
def find_import_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Find one import cycle in a module dependency graph, or None.

    `graph` maps a module name to the list of modules it imports. A cycle is a
    path that returns to a module it already visited. Return that path,
    including the repeated module at both ends, so it reads like a story:
    ["orders", "customers", "orders"].

    To keep the answer predictable: start from the module names in alphabetical
    order, and follow each module's imports in the order they are listed.
    Return the first cycle you find.

    A module named as an import but absent from `graph` imports nothing.

    Args:
        graph: {module: [modules it imports]}.

    Returns:
        The cycle as a list of module names, first == last, or None when the
        graph is acyclic.

    Examples:
        find_import_cycle({"orders": ["customers"], "customers": ["orders"]}) ->
            ["customers", "orders", "customers"]
            # alphabetical start: "customers" comes before "orders"

        find_import_cycle({"a": ["b"], "b": ["c"], "c": []}) -> None

        find_import_cycle({"app": ["models", "views"],
                           "models": ["utils"],
                           "utils": ["models"],
                           "views": []}) -> ["models", "utils", "models"]

        find_import_cycle({"a": ["a"]}) -> ["a", "a"]
        find_import_cycle({}) -> None
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: find_import_cycle")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(parse_requirement("pytest>=8.0  # for tests"))
    # print(find_import_cycle({"orders": ["customers"], "customers": ["orders"]}))
    print("Run `python check.py day11` from the course root to grade your work.")
