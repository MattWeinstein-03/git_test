"""Day 11 graded checks — Modules and environments."""

import pytest


# --- Exercise 1: parse_requirement ----------------------------------------
def test_parse_requirement_pinned(day):
    assert day.parse_requirement("requests==2.31.0") == ("requests", "==", "2.31.0")


def test_parse_requirement_handles_spaces_and_case(day):
    assert day.parse_requirement("pytest >= 8.0") == ("pytest", ">=", "8.0")
    assert day.parse_requirement("Rich") == ("rich", "", "")


def test_parse_requirement_keeps_ranges_whole(day):
    assert day.parse_requirement("rich>=13.0,<14") == ("rich", ">=", "13.0,<14")


def test_parse_requirement_drops_comments(day):
    assert day.parse_requirement("pytest==8.2.0  # for tests") == (
        "pytest",
        "==",
        "8.2.0",
    )


def test_parse_requirement_returns_none_for_non_packages(day):
    assert day.parse_requirement("# a comment") is None
    assert day.parse_requirement("   ") is None
    assert day.parse_requirement("") is None
    assert day.parse_requirement("-r dev-requirements.txt") is None


def test_parse_requirement_rejects_missing_name(day):
    with pytest.raises(ValueError, match="cannot parse requirement"):
        day.parse_requirement("==1.0")


# --- Exercise 2: parse_requirements ---------------------------------------
def test_parse_requirements_full_file(day):
    text = "# runtime\nrequests==2.31.0\n\nrich\npytest>=8.0\n"
    assert day.parse_requirements(text) == {
        "requests": "==2.31.0",
        "rich": "",
        "pytest": ">=8.0",
    }


def test_parse_requirements_empty_text(day):
    assert day.parse_requirements("") == {}


def test_parse_requirements_last_line_wins(day):
    assert day.parse_requirements("pytest==8.0\npytest==8.2\n") == {"pytest": "==8.2"}


def test_parse_requirements_skips_options_and_comments(day):
    text = "-r base.txt\n# nothing\n  \nruff\n"
    assert day.parse_requirements(text) == {"ruff": ""}


# --- Exercise 3: version_satisfies ----------------------------------------
def test_version_satisfies_exact(day):
    assert day.version_satisfies("2.31.0", "==2.31.0") is True
    assert day.version_satisfies("2.31.1", "==2.31.0") is False


def test_version_satisfies_empty_spec_accepts_anything(day):
    assert day.version_satisfies("2.31.0", "") is True


def test_version_satisfies_compares_numerically(day):
    assert day.version_satisfies("8.1", ">=8.0") is True
    assert day.version_satisfies("7.4", ">=8.0") is False
    assert day.version_satisfies("1.10", ">=1.9") is True, (
        "compare components as numbers: 10 > 9, even though '1.10' < '1.9' as text"
    )


def test_version_satisfies_pads_short_versions(day):
    assert day.version_satisfies("8.0", "==8.0.0") is True


def test_version_satisfies_handles_ranges(day):
    assert day.version_satisfies("13.5", ">=13.0,<14") is True
    assert day.version_satisfies("14.1", ">=13.0,<14") is False


def test_version_satisfies_compatible_release(day):
    assert day.version_satisfies("1.4.9", "~=1.4.2") is True
    assert day.version_satisfies("1.5.0", "~=1.4.2") is False


def test_version_satisfies_rejects_unknown_operator(day):
    with pytest.raises(ValueError):
        day.version_satisfies("1.0", "!!1.0")


# --- Exercise 4: missing_requirements -------------------------------------
def test_missing_requirements_reports_both_kinds(day):
    required = {"pytest": ">=8.0", "requests": "==2.31.0", "rich": ""}
    installed = {"pytest": "7.4.0", "rich": "13.7.1"}
    assert day.missing_requirements(required, installed) == [
        "pytest 7.4.0 does not satisfy >=8.0",
        "requests is not installed",
    ]


def test_missing_requirements_happy_environment(day):
    assert day.missing_requirements({"rich": ""}, {"rich": "1.0"}) == []
    assert day.missing_requirements({}, {"pytest": "8.0"}) == []


def test_missing_requirements_ignores_extra_installs(day):
    required = {"pytest": ">=8.0"}
    installed = {"pytest": "8.2.0", "iniconfig": "2.0.0", "pluggy": "1.5.0"}
    assert day.missing_requirements(required, installed) == []


def test_missing_requirements_is_sorted_by_name(day):
    required = {"zeta": ">=2", "alpha": ">=2"}
    installed = {}
    assert day.missing_requirements(required, installed) == [
        "alpha is not installed",
        "zeta is not installed",
    ]


# --- Exercise 5: freeze_lines ---------------------------------------------
def test_freeze_lines_sorted_and_pinned(day):
    assert day.freeze_lines({"pytest": "8.2.0", "iniconfig": "2.0.0"}) == [
        "iniconfig==2.0.0",
        "pytest==8.2.0",
    ]


def test_freeze_lines_sorts_case_insensitively(day):
    got = day.freeze_lines({"Rich": "13.7.1", "attrs": "23.2.0"})
    assert got == ["attrs==23.2.0", "Rich==13.7.1"], f"got {got!r}"


def test_freeze_lines_empty(day):
    assert day.freeze_lines({}) == []


# --- Exercise 6: resolve_relative_import ----------------------------------
def test_resolve_relative_import_sibling(day):
    assert day.resolve_relative_import("pkg.sub.mod", ".helpers") == "pkg.sub.helpers"


def test_resolve_relative_import_one_level_up(day):
    assert day.resolve_relative_import("pkg.sub.mod", "..util") == "pkg.util"


def test_resolve_relative_import_bare_dots(day):
    assert day.resolve_relative_import("pkg.sub.mod", ".") == "pkg.sub"
    assert day.resolve_relative_import("pkg.sub.mod", "..") == "pkg"


def test_resolve_relative_import_dotted_tail(day):
    assert day.resolve_relative_import("pkg.mod", ".a.b") == "pkg.a.b"


def test_resolve_relative_import_too_high(day):
    with pytest.raises(ValueError, match="too many leading dots"):
        day.resolve_relative_import("pkg.mod", "...x")


def test_resolve_relative_import_requires_a_dot(day):
    with pytest.raises(ValueError, match="not a relative import"):
        day.resolve_relative_import("pkg.mod", "other")


# --- Exercise 7: module_search_order --------------------------------------
PATH = ["", "/usr/lib/python3.11", "/venv/site-packages"]
PRESENT = {
    "": ["myapp", "json"],
    "/usr/lib/python3.11": ["json", "csv"],
    "/venv/site-packages": ["pytest"],
}


def test_module_search_order_local_file_shadows_stdlib(day):
    assert day.module_search_order(PATH, "json", PRESENT) == "", (
        "first match wins, and the script's own directory is searched first"
    )


def test_module_search_order_finds_stdlib(day):
    assert day.module_search_order(PATH, "csv", PRESENT) == "/usr/lib/python3.11"


def test_module_search_order_finds_site_packages(day):
    assert day.module_search_order(PATH, "pytest", PRESENT) == "/venv/site-packages"


def test_module_search_order_returns_none_when_absent(day):
    assert day.module_search_order(PATH, "requests", PRESENT) is None


def test_module_search_order_tolerates_undescribed_directories(day):
    assert day.module_search_order(["/nowhere", ""], "myapp", PRESENT) == ""


# --- Exercise 8: find_import_cycle ----------------------------------------
def test_find_import_cycle_two_modules(day):
    graph = {"orders": ["customers"], "customers": ["orders"]}
    assert day.find_import_cycle(graph) == ["customers", "orders", "customers"]


def test_find_import_cycle_none_for_acyclic_graph(day):
    assert day.find_import_cycle({"a": ["b"], "b": ["c"], "c": []}) is None


def test_find_import_cycle_deeper_graph(day):
    graph = {
        "app": ["models", "views"],
        "models": ["utils"],
        "utils": ["models"],
        "views": [],
    }
    assert day.find_import_cycle(graph) == ["models", "utils", "models"]


def test_find_import_cycle_self_import(day):
    assert day.find_import_cycle({"a": ["a"]}) == ["a", "a"]


def test_find_import_cycle_empty_graph(day):
    assert day.find_import_cycle({}) is None


def test_find_import_cycle_tolerates_unlisted_modules(day):
    # "csv" is imported but has no entry of its own: it imports nothing.
    assert day.find_import_cycle({"a": ["csv"], "b": ["a"]}) is None
