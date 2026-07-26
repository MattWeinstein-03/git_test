"""Day 09 graded checks — Errors and debugging."""

import pytest

TRACEBACK_TEXT = """Traceback (most recent call last):
  File "/home/you/reports/report.py", line 27, in <module>
    main()
  File "/home/you/reports/report.py", line 24, in main
    print(f"total: {total_revenue(SALES):.2f}")
                    ^^^^^^^^^^^^^^^^^^^^
  File "/home/you/reports/report.py", line 19, in total_revenue
    total += line_revenue(row)
             ^^^^^^^^^^^^^^^^^
  File "/home/you/reports/report.py", line 11, in line_revenue
    units = int(row["units"])
            ^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'n/a'
"""

NESTED = {"user": {"address": {"city": "Lagos"}}, "count": 3, "tags": ["a", "b"]}


# --- Exercise 1: safe_int -------------------------------------------------
def test_safe_int_parses_digits(day):
    assert day.safe_int("42") == 42


def test_safe_int_allows_surrounding_space(day):
    assert day.safe_int(" 7 ") == 7


def test_safe_int_returns_default_for_junk(day):
    assert day.safe_int("n/a") == 0
    assert day.safe_int("n/a", -1) == -1


def test_safe_int_rejects_decimal_text(day):
    assert day.safe_int("3.5") == 0


# --- Exercise 2: safe_divide ---------------------------------------------
def test_safe_divide_normal_case(day):
    assert day.safe_divide(10, 4) == 2.5


def test_safe_divide_zero_denominator_returns_none(day):
    assert day.safe_divide(10, 0) is None


def test_safe_divide_zero_denominator_uses_fallback(day):
    assert day.safe_divide(10, 0, 0.0) == 0.0


def test_safe_divide_does_not_swallow_type_errors(day):
    with pytest.raises(TypeError):
        day.safe_divide("10", 2)


# --- Exercise 3: get_nested ----------------------------------------------
def test_get_nested_finds_deep_value(day):
    assert day.get_nested(NESTED, ["user", "address", "city"]) == "Lagos"


def test_get_nested_missing_key_returns_default(day):
    assert day.get_nested(NESTED, ["user", "email"]) is None
    assert day.get_nested(NESTED, ["user", "email"], "unknown") == "unknown"


def test_get_nested_survives_non_dict_value(day):
    assert day.get_nested(NESTED, ["count", "city"]) is None
    assert day.get_nested(NESTED, ["tags", "city"], "nope") == "nope"


def test_get_nested_empty_key_list_returns_everything(day):
    assert day.get_nested(NESTED, []) == NESTED


# --- Exercise 4: parse_numbers -------------------------------------------
def test_parse_numbers_all_good(day):
    assert day.parse_numbers(["1", "2.5"]) == ([1.0, 2.5], [])


def test_parse_numbers_reports_bad_values(day):
    numbers, problems = day.parse_numbers(["1", "n/a", "3"])
    assert numbers == [1.0, 3.0]
    assert problems == ["'n/a' is not a number"], f"got {problems!r}"


def test_parse_numbers_empty_string_is_a_problem(day):
    numbers, problems = day.parse_numbers(["", "-4"])
    assert numbers == [-4.0]
    assert problems == ["'' is not a number"]


def test_parse_numbers_empty_input(day):
    assert day.parse_numbers([]) == ([], [])


# --- Exercise 5: validate_age --------------------------------------------
def test_validate_age_accepts_plausible_ages(day):
    assert day.validate_age(30) == 30
    assert day.validate_age(0) == 0
    assert day.validate_age(130) == 130


def test_validate_age_rejects_negative(day):
    with pytest.raises(day.InvalidAgeError, match="must not be negative, got -4"):
        day.validate_age(-4)


def test_validate_age_rejects_non_int(day):
    with pytest.raises(day.InvalidAgeError, match="whole number, got str"):
        day.validate_age("forty")


def test_validate_age_rejects_bool(day):
    with pytest.raises(day.InvalidAgeError, match="whole number, got bool"):
        day.validate_age(True)


def test_validate_age_rejects_implausible(day):
    with pytest.raises(day.InvalidAgeError, match="implausible"):
        day.validate_age(999)


# --- Exercise 6: traced_divide -------------------------------------------
def test_traced_divide_success_path(day):
    result, log = day.traced_divide(10, 4)
    assert result == 2.5
    assert log == ["try", "else", "finally"], f"got {log!r}"


def test_traced_divide_zero_division_path(day):
    result, log = day.traced_divide(1, 0)
    assert result is None
    assert log == ["try", "except ZeroDivisionError", "finally"], f"got {log!r}"


def test_traced_divide_type_error_path(day):
    result, log = day.traced_divide("a", 2)
    assert result is None
    assert log == ["try", "except TypeError", "finally"], f"got {log!r}"


def test_traced_divide_always_ends_with_finally(day):
    for numerator, denominator in ((6, 3), (6, 0), (None, 3)):
        _, log = day.traced_divide(numerator, denominator)
        assert log[0] == "try"
        assert log[-1] == "finally"


# --- Exercise 7: read_last_frame -----------------------------------------
def test_read_last_frame_finds_innermost_frame(day):
    filename, line_number, exception_line = day.read_last_frame(TRACEBACK_TEXT)
    assert filename == "/home/you/reports/report.py"
    assert line_number == 11, f"the innermost frame is line 11, got {line_number}"
    assert exception_line == (
        "ValueError: invalid literal for int() with base 10: 'n/a'"
    )


def test_read_last_frame_single_frame(day):
    text = 'Traceback (most recent call last):\n  File "app.py", line 3, in <module>\n    boom()\nKeyError: \'b\'\n'
    assert day.read_last_frame(text) == ("app.py", 3, "KeyError: 'b'")


def test_read_last_frame_without_frames_raises(day):
    with pytest.raises(ValueError, match="no frames found"):
        day.read_last_frame("KeyError: 'b'")


# --- Exercise 8: normalize_scores ----------------------------------------
def test_normalize_scores_converts_values(day):
    assert day.normalize_scores({"ada": "90", "grace": "100"}) == {
        "ada": 90,
        "grace": 100,
    }


def test_normalize_scores_empty(day):
    assert day.normalize_scores({}) == {}


def test_normalize_scores_chains_the_original_error(day):
    with pytest.raises(day.ScoreError) as info:
        day.normalize_scores({"ada": "ninety"})
    assert "bad score for 'ada'" in str(info.value)
    assert isinstance(info.value.__cause__, ValueError), (
        "use `raise ScoreError(...) from error` so the ValueError is kept as __cause__"
    )


def test_normalize_scores_range_error_has_no_cause(day):
    with pytest.raises(day.ScoreError) as info:
        day.normalize_scores({"ada": "150"})
    assert "out of range" in str(info.value)
    assert info.value.__cause__ is None


# --- Exercise 9: parse_config --------------------------------------------
def test_parse_config_happy_path(day):
    settings, problems = day.parse_config(
        ["debug = true", "# a comment", "", "name=ada"]
    )
    assert settings == {"debug": "true", "name": "ada"}
    assert problems == []


def test_parse_config_reports_missing_equals_and_duplicates(day):
    settings, problems = day.parse_config(["oops", "DEBUG=1", "debug=0"])
    assert settings == {"debug": "1"}
    assert problems == [
        "line 1: missing '=' in 'oops'",
        "line 3: duplicate key 'debug'",
    ], f"got {problems!r}"


def test_parse_config_empty_key_and_first_split_only(day):
    settings, problems = day.parse_config(["  = 5", "motto = a = b"])
    assert settings == {"motto": "a = b"}
    assert problems == ["line 1: empty key in '  = 5'"], f"got {problems!r}"


def test_parse_config_allows_empty_value_and_strips_newlines(day):
    settings, problems = day.parse_config(["name =\n", "  city = Lagos  \n"])
    assert settings == {"name": "", "city": "Lagos"}
    assert problems == []


def test_parse_config_empty_input(day):
    assert day.parse_config([]) == ({}, [])
