"""Day 01 graded checks — Getting Started."""


# --- Exercise 1: greeting_line --------------------------------------------
def test_greeting_line_basic(day):
    assert day.greeting_line("Ada") == "Hello, Ada!"


def test_greeting_line_keeps_the_whole_name(day):
    assert day.greeting_line("Grace Hopper") == "Hello, Grace Hopper!"


def test_greeting_line_empty_name(day):
    got = day.greeting_line("")
    assert got == "Hello, !", f"expected 'Hello, !' with nothing added, got {got!r}"


# --- Exercise 2: full_name ------------------------------------------------
def test_full_name_joins_with_one_space(day):
    assert day.full_name("Ada", "Lovelace") == "Ada Lovelace"


def test_full_name_does_not_change_case(day):
    assert day.full_name("grace", "hopper") == "grace hopper"


def test_full_name_empty_last_name_leaves_the_space(day):
    got = day.full_name("Prince", "")
    assert got == "Prince ", f"exactly one space, always: got {got!r}"


# --- Exercise 3: type_name ------------------------------------------------
def test_type_name_int(day):
    got = day.type_name(42)
    assert got == "int", f"expected the name only ('int'), got {got!r}"


def test_type_name_float_and_str(day):
    assert day.type_name(3.14) == "float"
    assert day.type_name("hi") == "str"


def test_type_name_bool_and_none(day):
    assert day.type_name(True) == "bool"
    assert day.type_name(None) == "NoneType"


def test_type_name_returns_a_string(day):
    assert isinstance(day.type_name(1), str)


# --- Exercise 4: to_whole_number ------------------------------------------
def test_to_whole_number_converts_digits(day):
    got = day.to_whole_number("36")
    assert got == 36
    assert isinstance(got, int), f"expected an int, got {type(got).__name__}"


def test_to_whole_number_zero_and_negative(day):
    assert day.to_whole_number("0") == 0
    assert day.to_whole_number("-4") == -4


def test_to_whole_number_tolerates_surrounding_spaces(day):
    assert day.to_whole_number(" 7 ") == 7


# --- Exercise 5: describe_value -------------------------------------------
def test_describe_value_int(day):
    assert day.describe_value(42) == "42 is of type int"


def test_describe_value_float_and_str(day):
    assert day.describe_value(3.5) == "3.5 is of type float"
    assert day.describe_value("hi") == "hi is of type str"


def test_describe_value_bool_and_none(day):
    assert day.describe_value(True) == "True is of type bool"
    assert day.describe_value(None) == "None is of type NoneType"


def test_describe_value_empty_string(day):
    got = day.describe_value("")
    assert got == " is of type str", f"expected ' is of type str', got {got!r}"


# --- Exercise 6: print_row ------------------------------------------------
def test_print_row_uses_pipe_separator(day, capsys):
    day.print_row("a", "b", "c")
    out = capsys.readouterr().out
    assert out == "a | b | c\n", f"expected 'a | b | c' on one line, got {out!r}"


def test_print_row_other_values(day, capsys):
    day.print_row("name", "city", "year")
    out = capsys.readouterr().out
    assert out == "name | city | year\n"


def test_print_row_returns_nothing(day, capsys):
    result = day.print_row("a", "b", "c")
    capsys.readouterr()
    assert result is None, "print_row prints; it should not return a value"


# --- Exercise 7: print_banner ---------------------------------------------
def test_print_banner_underlines_the_text(day, capsys):
    day.print_banner("Report")
    out = capsys.readouterr().out
    assert out == "Report\n------\n", f"got {out!r}"


def test_print_banner_underline_matches_length(day, capsys):
    day.print_banner("Day 01")
    out = capsys.readouterr().out
    lines = out.split("\n")
    assert lines[0] == "Day 01"
    assert lines[1] == "-" * 6, f"underline must be 6 dashes, got {lines[1]!r}"


def test_print_banner_empty_text(day, capsys):
    day.print_banner("")
    out = capsys.readouterr().out
    assert out == "\n\n", f"expected two empty lines, got {out!r}"


# --- Exercise 8: profile_card ---------------------------------------------
def test_profile_card_three_lines(day):
    got = day.profile_card("Ada", "London", 1815)
    want = "Name: Ada\nCity: London\nBorn: 1815"
    assert got == want, f"got:\n{got}\n\nwant:\n{want}"


def test_profile_card_converts_the_year(day):
    got = day.profile_card("Grace", "New York", 1906)
    assert got == "Name: Grace\nCity: New York\nBorn: 1906"


def test_profile_card_has_no_trailing_newline(day):
    got = day.profile_card("Ada", "London", 1815)
    assert not got.endswith("\n"), "join the lines with \\n, do not end with one"
    assert len(got.split("\n")) == 3


# --- Exercise 9: type_report ----------------------------------------------
EXPECTED_MIXED = "\n".join(
    [
        "Type report",
        "-----------",
        "1. 42 is of type int",
        "2. 3.5 is of type float",
        "3. hi is of type str",
    ]
)

EXPECTED_ODDBALLS = "\n".join(
    [
        "Type report",
        "-----------",
        "1. True is of type bool",
        "2. None is of type NoneType",
        "3. 0 is of type int",
    ]
)


def test_type_report_mixed_values(day):
    got = day.type_report(42, 3.5, "hi")
    assert got == EXPECTED_MIXED, f"got:\n{got}\n\nwant:\n{EXPECTED_MIXED}"


def test_type_report_bool_none_and_zero(day):
    got = day.type_report(True, None, 0)
    assert got == EXPECTED_ODDBALLS, f"got:\n{got}\n\nwant:\n{EXPECTED_ODDBALLS}"


def test_type_report_underline_is_eleven_dashes(day):
    lines = day.type_report(1, 2, 3).split("\n")
    assert lines[0] == "Type report"
    assert lines[1] == "-" * 11, f"underline must match the header length, got {lines[1]!r}"


def test_type_report_has_five_lines_and_no_trailing_newline(day):
    got = day.type_report("a", "b", "c")
    assert len(got.split("\n")) == 5, f"expected 5 lines, got {len(got.split(chr(10)))}"
    assert not got.endswith("\n")
