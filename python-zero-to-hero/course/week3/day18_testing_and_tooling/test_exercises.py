"""Day 18 graded checks — testing and tooling.

The `day` fixture hands these tests your exercises.py (or solutions.py when
PZH_SOLUTIONS=1 is set). Never import exercises directly.

Two tests below use `@pytest.mark.parametrize` — with literal values only, never
values pulled out of the module under test. That is the rule the lesson explains:
parameter lists are collected before your code is even imported, so they must not
depend on it.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence

import pytest

# ---------------------------------------------------------------------------
# Candidate implementations used to grade exercises 6 and 7. These live here, in
# the test file, so that grading your *checker* does not depend on grading your
# *implementations*.
# ---------------------------------------------------------------------------


def _good_median(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("empty sequence")
    return statistics.median(values)


def _median_lower_middle(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("empty")
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]  # wrong for even counts


def _median_assumes_sorted(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("empty")
    count = len(values)
    middle = count // 2
    if count % 2 == 1:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def _median_mutates(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("empty")
    values.sort()  # type: ignore[attr-defined]  # mutates the caller's list
    return statistics.median(values)


def _median_no_raise(values: Sequence[float]) -> float:
    if not values:
        return 0.0  # should raise ValueError
    return statistics.median(values)


def _median_wrong_error(values: Sequence[float]) -> float:
    ordered = sorted(values)
    count = len(ordered)
    if count % 2 == 1:
        return ordered[count // 2]
    return (ordered[count // 2 - 1] + ordered[count // 2]) / 2  # IndexError when empty


def _median_broken(values: Sequence[float]) -> float:
    raise RuntimeError("this implementation is simply broken")


BROKEN_MEDIANS = {
    "lower middle on even counts": _median_lower_middle,
    "assumes the input is sorted": _median_assumes_sorted,
    "mutates the caller's list": _median_mutates,
    "returns a value for empty input": _median_no_raise,
    "raises the wrong exception when empty": _median_wrong_error,
    "raises on every call": _median_broken,
}


def _good_wrap(text: str, width: int) -> list[str]:
    if width < 1:
        raise ValueError("width must be at least 1")
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for word in text.split():
        if current and length + len(current) + len(word) > width:
            lines.append(" ".join(current))
            current = []
            length = 0
        current.append(word)
        length += len(word)
    if current:
        lines.append(" ".join(current))
    return lines


def _wrap_never_breaks(text: str, width: int) -> list[str]:
    if width < 1:
        raise ValueError("width")
    words = text.split()
    return [" ".join(words)] if words else []  # lines far longer than width


def _wrap_drops_words(text: str, width: int) -> list[str]:
    lines = _good_wrap(text, width)
    return lines[:-1] if lines else lines  # loses the final line


def _wrap_keeps_whitespace(text: str, width: int) -> list[str]:
    if width < 1:
        raise ValueError("width")
    lines: list[str] = []
    current: list[str] = []
    length = 0
    for word in text.split(" "):  # does not collapse runs of whitespace
        if current and length + len(current) + len(word) > width:
            lines.append(" ".join(current))
            current = []
            length = 0
        current.append(word)
        length += len(word)
    if current:
        lines.append(" ".join(current))
    return lines


def _wrap_ignores_bad_width(text: str, width: int) -> list[str]:
    return _good_wrap(text, max(width, 1))  # silently repairs an invalid width


def _wrap_returns_string(text: str, width: int):
    return "\n".join(_good_wrap(text, width))  # wrong type


def _wrap_broken(text: str, width: int) -> list[str]:
    raise RuntimeError("this implementation is simply broken")


BROKEN_WRAPS = {
    "never breaks lines": _wrap_never_breaks,
    "drops words": _wrap_drops_words,
    "keeps runs of whitespace": _wrap_keeps_whitespace,
    "accepts an invalid width": _wrap_ignores_bad_width,
    "returns a string": _wrap_returns_string,
    "raises on every call": _wrap_broken,
}


# --- exercise 1: median ---------------------------------------------------


def test_median_odd_count_unsorted(day):
    assert day.median([3, 1, 2]) == 2


def test_median_even_count_averages_middle_two(day):
    assert day.median([1, 2, 3, 4]) == 2.5


def test_median_single_value(day):
    assert day.median([7]) == 7


def test_median_does_not_mutate_input(day):
    values = [3, 1, 2]
    day.median(values)
    assert values == [3, 1, 2], "use sorted(values), not values.sort()"


def test_median_handles_negatives_and_floats(day):
    assert day.median([-5, -1, -3]) == -3
    assert day.median([2.5, 1.5]) == pytest.approx(2.0)


def test_median_rejects_empty(day):
    with pytest.raises(ValueError, match="empty"):
        day.median([])


# --- exercise 2: parse_bool ----------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("yes", True),
        ("YES", True),
        (" y ", True),
        ("true", True),
        ("T", True),
        ("1", True),
        ("on", True),
        ("no", False),
        ("N", False),
        ("false", False),
        ("f", False),
        ("0", False),
        (" off ", False),
    ],
)
def test_parse_bool_accepts_known_words(day, text, expected):
    assert day.parse_bool(text) is expected, f"parse_bool({text!r})"


def test_parse_bool_rejects_unknown_with_helpful_message(day):
    with pytest.raises(ValueError, match="maybe"):
        day.parse_bool("maybe")


def test_parse_bool_rejects_empty_string(day):
    with pytest.raises(ValueError):
        day.parse_bool("")


def test_parse_bool_returns_real_bools(day):
    assert isinstance(day.parse_bool("yes"), bool)


# --- exercise 3: rle_encode ---------------------------------------------


def test_rle_encode_runs(day):
    assert day.rle_encode("aaabbc") == "a3b2c1"


def test_rle_encode_empty(day):
    assert day.rle_encode("") == ""


def test_rle_encode_single_character(day):
    assert day.rle_encode("a") == "a1"


def test_rle_encode_repeated_runs_of_same_character(day):
    assert day.rle_encode("aabaa") == "a2b1a2"


def test_rle_encode_long_run_uses_full_number(day):
    got = day.rle_encode("z" * 12)
    assert got == "z12", f"counts are written in full; got {got!r}"


def test_rle_encode_is_case_sensitive(day):
    assert day.rle_encode("aA") == "a1A1"


# --- exercise 4: rle_decode ---------------------------------------------


def test_rle_decode_basic(day):
    assert day.rle_decode("a3b2c1") == "aaabbc"


def test_rle_decode_reads_multi_digit_counts(day):
    got = day.rle_decode("a12")
    assert got == "a" * 12, f"read every digit, not just one; got {got!r}"


def test_rle_decode_empty(day):
    assert day.rle_decode("") == ""


def test_rle_decode_round_trips_with_encode(day):
    for text in ["", "a", "aaabbc", "xyz", "q" * 15, "aabaa"]:
        assert day.rle_decode(day.rle_encode(text)) == text, f"round trip failed for {text!r}"


def test_rle_decode_rejects_missing_count(day):
    with pytest.raises(ValueError):
        day.rle_decode("ab")


def test_rle_decode_rejects_leading_digit(day):
    with pytest.raises(ValueError):
        day.rle_decode("3a")


# --- exercise 5: print_table (capsys) ------------------------------------


def test_print_table_aligns_both_columns(day, capsys):
    day.print_table([("ada", 3), ("bo", 12)])
    lines = capsys.readouterr().out.splitlines()
    assert lines == ["ada   3", "bo   12"], f"got {lines}"


def test_print_table_single_row(day, capsys):
    day.print_table([("x", "yes")])
    assert capsys.readouterr().out == "x  yes\n"


def test_print_table_empty_prints_nothing(day, capsys):
    day.print_table([])
    assert capsys.readouterr().out == "", "an empty table prints nothing at all"


def test_print_table_returns_none(day, capsys):
    assert day.print_table([("a", 1)]) is None
    capsys.readouterr()


def test_print_table_keeps_row_order(day, capsys):
    day.print_table([("zz", 1), ("a", 2)])
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines] == ["zz", "a"]


# --- exercise 6: find_median_bugs ----------------------------------------


def test_find_median_bugs_accepts_a_correct_implementation(day):
    got = day.find_median_bugs(_good_median)
    assert got == [], f"a correct implementation must produce no complaints; got {got}"


def test_find_median_bugs_catches_lower_middle(day):
    assert day.find_median_bugs(_median_lower_middle), (
        "an implementation returning the lower middle value for [1,2,3,4] is wrong"
    )


def test_find_median_bugs_catches_unsorted_assumption(day):
    assert day.find_median_bugs(_median_assumes_sorted), (
        "median([3,1,2]) must be 2; test with unsorted input"
    )


def test_find_median_bugs_catches_mutation(day):
    assert day.find_median_bugs(_median_mutates), (
        "check that the caller's list is unchanged after the call"
    )


def test_find_median_bugs_catches_missing_error(day):
    assert day.find_median_bugs(_median_no_raise), (
        "empty input must raise ValueError; check it with try/except"
    )


def test_find_median_bugs_catches_wrong_error_type(day):
    assert day.find_median_bugs(_median_wrong_error), (
        "empty input raising IndexError instead of ValueError is a fault"
    )


def test_find_median_bugs_survives_a_broken_candidate(day):
    got = day.find_median_bugs(_median_broken)
    assert got, "a candidate that raises on every call has faults to report"
    assert isinstance(got, list) and all(isinstance(item, str) for item in got)


def test_find_median_bugs_catches_every_seeded_bug(day):
    missed = [name for name, func in BROKEN_MEDIANS.items() if not day.find_median_bugs(func)]
    assert missed == [], f"these broken implementations passed your checker: {missed}"


# --- exercise 7: find_wrap_bugs -----------------------------------------


def test_find_wrap_bugs_accepts_a_correct_implementation(day):
    got = day.find_wrap_bugs(_good_wrap)
    assert got == [], f"a correct implementation must produce no complaints; got {got}"


def test_find_wrap_bugs_catches_overlong_lines(day):
    assert day.find_wrap_bugs(_wrap_never_breaks), (
        "an implementation that never breaks a line is wrong"
    )


def test_find_wrap_bugs_catches_dropped_words(day):
    assert day.find_wrap_bugs(_wrap_drops_words), (
        "check that no word is lost: ' '.join(lines).split() == text.split()"
    )


def test_find_wrap_bugs_catches_uncollapsed_whitespace(day):
    assert day.find_wrap_bugs(_wrap_keeps_whitespace), (
        "try input containing a double space and a newline"
    )


def test_find_wrap_bugs_catches_invalid_width_accepted(day):
    assert day.find_wrap_bugs(_wrap_ignores_bad_width), (
        "width 0 must raise ValueError, not be silently repaired"
    )


def test_find_wrap_bugs_catches_wrong_return_type(day):
    assert day.find_wrap_bugs(_wrap_returns_string), (
        "a returned string is not a list of lines"
    )


def test_find_wrap_bugs_survives_a_broken_candidate(day):
    got = day.find_wrap_bugs(_wrap_broken)
    assert got, "a candidate that raises on every call has faults to report"
    assert isinstance(got, list) and all(isinstance(item, str) for item in got)


def test_find_wrap_bugs_catches_every_seeded_bug(day):
    missed = [name for name, func in BROKEN_WRAPS.items() if not day.find_wrap_bugs(func)]
    assert missed == [], f"these broken implementations passed your checker: {missed}"


# --- exercise 8: summarise_file (tmp_path) -------------------------------


def test_summarise_file_counts_lines_and_words(day, tmp_path):
    target = tmp_path / "data.txt"
    target.write_text("a b\nc\n", encoding="utf-8")
    assert day.summarise_file(target) == {"lines": 2, "words": 3, "longest": "a b"}


def test_summarise_file_empty_file(day, tmp_path):
    target = tmp_path / "empty.txt"
    target.write_text("", encoding="utf-8")
    assert day.summarise_file(target) == {"lines": 0, "words": 0, "longest": ""}


def test_summarise_file_counts_blank_lines(day, tmp_path):
    target = tmp_path / "blanks.txt"
    target.write_text("a\n\nb\n", encoding="utf-8")
    got = day.summarise_file(target)
    assert got["lines"] == 3, f"a blank line is still a line; got {got}"
    assert got["words"] == 2


def test_summarise_file_longest_line_prefers_the_earliest(day, tmp_path):
    target = tmp_path / "tie.txt"
    target.write_text("abc\nxyz\nq\n", encoding="utf-8")
    assert day.summarise_file(target)["longest"] == "abc"


def test_summarise_file_no_trailing_newline(day, tmp_path):
    target = tmp_path / "no_newline.txt"
    target.write_text("one two", encoding="utf-8")
    assert day.summarise_file(target) == {"lines": 1, "words": 2, "longest": "one two"}


def test_summarise_file_missing_file_raises(day, tmp_path):
    with pytest.raises(FileNotFoundError):
        day.summarise_file(tmp_path / "nope.txt")


# --- exercise 9: get_setting (monkeypatch) ------------------------------


def test_get_setting_reads_the_environment(day, monkeypatch):
    monkeypatch.setenv("PZH_TEST_LIMIT", "42")
    assert day.get_setting("PZH_TEST_LIMIT", "10") == "42"


def test_get_setting_applies_the_cast(day, monkeypatch):
    monkeypatch.setenv("PZH_TEST_LIMIT", "42")
    got = day.get_setting("PZH_TEST_LIMIT", "10", int)
    assert got == 42
    assert isinstance(got, int)


def test_get_setting_uses_the_default_when_unset(day, monkeypatch):
    monkeypatch.delenv("PZH_TEST_LIMIT", raising=False)
    assert day.get_setting("PZH_TEST_LIMIT", "7", int) == 7


def test_get_setting_treats_empty_value_as_present(day, monkeypatch):
    monkeypatch.setenv("PZH_TEST_NAME", "")
    assert day.get_setting("PZH_TEST_NAME", "fallback") == ""


def test_get_setting_raises_value_error_on_bad_cast(day, monkeypatch):
    monkeypatch.setenv("PZH_TEST_LIMIT", "abc")
    with pytest.raises(ValueError) as info:
        day.get_setting("PZH_TEST_LIMIT", "10", int)
    message = str(info.value)
    assert "PZH_TEST_LIMIT" in message and "abc" in message, (
        f"the message must name the setting and the value; got {message!r}"
    )


def test_get_setting_bad_default_also_raises(day, monkeypatch):
    monkeypatch.delenv("PZH_TEST_LIMIT", raising=False)
    with pytest.raises(ValueError):
        day.get_setting("PZH_TEST_LIMIT", "not-a-number", int)


# --- exercise 10: word_wrap ---------------------------------------------


@pytest.mark.parametrize(
    "text, width, expected",
    [
        ("the quick brown fox", 10, ["the quick", "brown fox"]),
        ("a  b\n\nc", 3, ["a b", "c"]),
        ("unsplittable", 4, ["unsplittable"]),
        ("   ", 5, []),
        ("", 5, []),
        ("one two three", 3, ["one", "two", "three"]),
        ("aaa bbb", 7, ["aaa bbb"]),
        ("aaa bbb", 6, ["aaa", "bbb"]),
    ],
)
def test_word_wrap_cases(day, text, width, expected):
    got = day.word_wrap(text, width)
    assert got == expected, f"word_wrap({text!r}, {width}) -> {got!r}"


def test_word_wrap_rejects_zero_width(day):
    with pytest.raises(ValueError):
        day.word_wrap("a b", 0)


def test_word_wrap_rejects_negative_width(day):
    with pytest.raises(ValueError):
        day.word_wrap("a b", -3)


def test_word_wrap_preserves_all_words(day):
    text = "alpha beta gamma delta epsilon zeta eta theta"
    for width in (6, 10, 20):
        lines = day.word_wrap(text, width)
        assert " ".join(lines).split() == text.split(), f"width {width} changed the words"


def test_word_wrap_lines_fit_unless_a_single_word_is_too_long(day):
    text = "alpha beta gamma delta epsilon zeta eta theta"
    for width in (6, 10, 20):
        for line in day.word_wrap(text, width):
            assert line, f"width {width} produced an empty line"
            if " " in line:
                assert len(line) <= width, f"width {width}: {line!r} is too long"


def test_word_wrap_is_greedy(day):
    # "aa bb cc" at width 5 must be ['aa bb', 'cc'], not ['aa', 'bb cc'].
    assert day.word_wrap("aa bb cc", 5) == ["aa bb", "cc"]
