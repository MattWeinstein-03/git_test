"""Day 10 graded checks — Files and data.

Every test uses pytest's `tmp_path` fixture: a fresh, empty directory that
pytest creates for the test and cleans up afterwards. No test ever writes into
the repository.
"""

import json

import pytest


# --- Exercise 1: write_text_file ------------------------------------------
def test_write_text_file_writes_content(day, tmp_path):
    path = tmp_path / "a.txt"
    written = day.write_text_file(path, "hello")
    assert written == 5
    assert path.read_text(encoding="utf-8") == "hello"


def test_write_text_file_overwrites(day, tmp_path):
    path = tmp_path / "a.txt"
    day.write_text_file(path, "first")
    day.write_text_file(path, "second")
    assert path.read_text(encoding="utf-8") == "second"


def test_write_text_file_creates_missing_directories(day, tmp_path):
    path = tmp_path / "deep" / "deeper" / "b.txt"
    assert day.write_text_file(path, "hi") == 2
    assert path.read_text(encoding="utf-8") == "hi"


def test_write_text_file_handles_empty_text(day, tmp_path):
    path = tmp_path / "empty.txt"
    assert day.write_text_file(path, "") == 0
    assert path.read_text(encoding="utf-8") == ""


def test_write_text_file_uses_utf8(day, tmp_path):
    path = tmp_path / "accents.txt"
    day.write_text_file(path, "café £5")
    assert path.read_bytes() == "café £5".encode()


# --- Exercise 2: read_lines ----------------------------------------------
def test_read_lines_strips_newlines(day, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("a\nb\n", encoding="utf-8")
    assert day.read_lines(path) == ["a", "b"]


def test_read_lines_keeps_blank_lines_and_last_line(day, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("a\n\nb", encoding="utf-8")
    assert day.read_lines(path) == ["a", "", "b"]


def test_read_lines_empty_file(day, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("", encoding="utf-8")
    assert day.read_lines(path) == []


def test_read_lines_missing_file_raises(day, tmp_path):
    with pytest.raises(FileNotFoundError):
        day.read_lines(tmp_path / "nope.txt")


# --- Exercise 3: append_line ---------------------------------------------
def test_append_line_creates_the_file(day, tmp_path):
    path = tmp_path / "log.txt"
    assert day.append_line(path, "first") == 1
    assert path.read_text(encoding="utf-8") == "first\n"


def test_append_line_keeps_existing_content(day, tmp_path):
    path = tmp_path / "log.txt"
    day.append_line(path, "first")
    count = day.append_line(path, "second")
    assert count == 2
    assert path.read_text(encoding="utf-8") == "first\nsecond\n", (
        "mode 'a' appends; mode 'w' would have destroyed the first line"
    )


def test_append_line_counts_pre_existing_lines(day, tmp_path):
    path = tmp_path / "log.txt"
    path.write_text("a\nb\n", encoding="utf-8")
    assert day.append_line(path, "c") == 3


# --- Exercise 4: count_words ---------------------------------------------
def test_count_words_is_case_insensitive(day, tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("the cat\nThe dog\n", encoding="utf-8")
    assert day.count_words(path) == {"the": 2, "cat": 1, "dog": 1}


def test_count_words_empty_file(day, tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("", encoding="utf-8")
    assert day.count_words(path) == {}


def test_count_words_splits_on_any_whitespace(day, tmp_path):
    path = tmp_path / "words.txt"
    path.write_text("a\t b\n\n  a  \n", encoding="utf-8")
    assert day.count_words(path) == {"a": 2, "b": 1}


# --- Exercise 5: write_csv -----------------------------------------------
def test_write_csv_writes_header_and_rows(day, tmp_path):
    path = tmp_path / "out.csv"
    rows = [{"name": "Ada", "amount": "12.50"}, {"name": "Grace", "amount": "7"}]
    assert day.write_csv(path, rows, ["name", "amount"]) == 2
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines == ["name,amount", "Ada,12.50", "Grace,7"], f"got {lines!r}"


def test_write_csv_header_only(day, tmp_path):
    path = tmp_path / "out.csv"
    assert day.write_csv(path, [], ["name", "amount"]) == 0
    assert path.read_text(encoding="utf-8").splitlines() == ["name,amount"]


def test_write_csv_missing_key_becomes_empty_cell(day, tmp_path):
    path = tmp_path / "out.csv"
    assert day.write_csv(path, [{"name": "Ada"}], ["name", "amount"]) == 1
    assert path.read_text(encoding="utf-8").splitlines()[1] == "Ada,"


def test_write_csv_quotes_fields_containing_commas(day, tmp_path):
    path = tmp_path / "out.csv"
    day.write_csv(path, [{"note": "a, b"}], ["note"])
    assert path.read_text(encoding="utf-8").splitlines()[1] == '"a, b"'


def test_write_csv_has_no_blank_rows(day, tmp_path):
    path = tmp_path / "out.csv"
    day.write_csv(path, [{"a": "1"}, {"a": "2"}], ["a"])
    raw = path.read_bytes()
    assert b"\r\r\n" not in raw and b"\n\n" not in raw, (
        f"blank rows between records — did you pass newline='' to open()? {raw!r}"
    )
    assert path.read_text(encoding="utf-8").splitlines() == ["a", "1", "2"]


# --- Exercise 6: read_csv_rows -------------------------------------------
def test_read_csv_rows_returns_dicts(day, tmp_path):
    path = tmp_path / "in.csv"
    path.write_text("name,amount\nAda,12.50\n", encoding="utf-8")
    assert day.read_csv_rows(path) == [{"name": "Ada", "amount": "12.50"}]


def test_read_csv_rows_header_only(day, tmp_path):
    path = tmp_path / "in.csv"
    path.write_text("name,amount\n", encoding="utf-8")
    assert day.read_csv_rows(path) == []


def test_read_csv_rows_keeps_everything_as_strings(day, tmp_path):
    path = tmp_path / "in.csv"
    path.write_text("name,amount\nAda,12\n", encoding="utf-8")
    row = day.read_csv_rows(path)[0]
    assert row["amount"] == "12"
    assert isinstance(row["amount"], str), "csv values are text, not numbers"


def test_read_csv_rows_handles_quoted_commas(day, tmp_path):
    path = tmp_path / "in.csv"
    path.write_text('name,note\nAda,"owes 3, maybe 4"\n', encoding="utf-8")
    assert day.read_csv_rows(path) == [{"name": "Ada", "note": "owes 3, maybe 4"}]


# --- Exercise 7: save_json -----------------------------------------------
def test_save_json_round_trips(day, tmp_path):
    path = tmp_path / "data.json"
    day.save_json(path, {"b": 1, "a": [1, 2]})
    assert json.loads(path.read_text(encoding="utf-8")) == {"b": 1, "a": [1, 2]}


def test_save_json_is_indented_and_sorted(day, tmp_path):
    path = tmp_path / "data.json"
    day.save_json(path, {"b": 1, "a": 2})
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "{"
    assert lines[1] == '  "a": 2,', f"expected indent=2 and sort_keys=True, got {lines!r}"


def test_save_json_creates_missing_directories(day, tmp_path):
    path = tmp_path / "nested" / "data.json"
    day.save_json(path, [1, 2, 3])
    assert json.loads(path.read_text(encoding="utf-8")) == [1, 2, 3]


# --- Exercise 8: load_json -----------------------------------------------
def test_load_json_reads_a_document(day, tmp_path):
    path = tmp_path / "data.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    assert day.load_json(path) == [1, 2, 3]


def test_load_json_missing_file_returns_default(day, tmp_path):
    assert day.load_json(tmp_path / "nope.json") is None
    assert day.load_json(tmp_path / "nope.json", {}) == {}


def test_load_json_corrupt_file_returns_default(day, tmp_path):
    path = tmp_path / "half.json"
    path.write_text('{"name": "Ada", ', encoding="utf-8")
    assert day.load_json(path, {}) == {}


def test_load_json_does_not_hide_other_errors(day, tmp_path):
    # A directory is not a file: this must not be silently swallowed.
    with pytest.raises(OSError):
        day.load_json(tmp_path)


# --- Exercise 9: clean_rows ----------------------------------------------
def test_clean_rows_keeps_good_rows_and_strips(day):
    good, problems = day.clean_rows([{"name": "  Ada ", "amount": "12.50"}], ["name"])
    assert good == [{"name": "Ada", "amount": "12.50"}]
    assert problems == []


def test_clean_rows_reports_every_kind_of_missing(day):
    rows = [
        {"name": "  Ada ", "amount": "12.50"},
        {"name": "", "amount": "7"},
        {"amount": "3"},
        {"name": "Grace", "amount": None},
    ]
    good, problems = day.clean_rows(rows, ["name", "amount"])
    assert good == [{"name": "Ada", "amount": "12.50"}]
    assert problems == [
        "row 2: missing name",
        "row 3: missing name",
        "row 4: missing amount",
    ], f"got {problems!r}"


def test_clean_rows_lists_several_missing_fields_together(day):
    good, problems = day.clean_rows([{"other": "x"}], ["name", "amount"])
    assert good == []
    assert problems == ["row 1: missing name, amount"], f"got {problems!r}"


def test_clean_rows_does_not_mutate_input(day):
    rows = [{"name": "  Ada "}]
    day.clean_rows(rows, ["name"])
    assert rows == [{"name": "  Ada "}], "build new dicts; leave the caller's rows alone"


def test_clean_rows_empty_cases(day):
    assert day.clean_rows([], ["name"]) == ([], [])
    assert day.clean_rows([{"a": "1"}], []) == ([{"a": "1"}], [])


# --- Exercise 10: csv_to_json --------------------------------------------
def test_csv_to_json_converts_and_reports(day, tmp_path):
    source = tmp_path / "sales.csv"
    source.write_text("name,amount\nAda,12.50\nGrace,n/a\n,3\n", encoding="utf-8")
    target = tmp_path / "sales.json"

    written, problems = day.csv_to_json(source, target, ["amount"])
    assert written == 2, f"rows 1 and 3 are usable; got {written}"
    assert problems == ["row 2: amount 'n/a' is not a number"], f"got {problems!r}"

    records = json.loads(target.read_text(encoding="utf-8"))
    assert records[0] == {"name": "Ada", "amount": 12.5}
    assert isinstance(records[0]["amount"], float), "numeric fields must be numbers"
    assert records[1] == {"name": "", "amount": 3.0}


def test_csv_to_json_reports_missing_numeric_field(day, tmp_path):
    source = tmp_path / "sales.csv"
    source.write_text("name,amount\nAda,\nGrace,7\n", encoding="utf-8")
    target = tmp_path / "sales.json"

    written, problems = day.csv_to_json(source, target, ["amount"])
    assert written == 1
    assert problems == ["row 1: missing amount"], f"got {problems!r}"


def test_csv_to_json_writes_empty_array_for_header_only_file(day, tmp_path):
    source = tmp_path / "sales.csv"
    source.write_text("name,amount\n", encoding="utf-8")
    target = tmp_path / "sales.json"

    assert day.csv_to_json(source, target, ["amount"]) == (0, [])
    assert json.loads(target.read_text(encoding="utf-8")) == []


def test_csv_to_json_handles_several_numeric_fields(day, tmp_path):
    source = tmp_path / "sales.csv"
    source.write_text(
        "name,units,price\nAda,2,9.99\nGrace,two,1.00\n", encoding="utf-8"
    )
    target = tmp_path / "sales.json"

    written, problems = day.csv_to_json(source, target, ["units", "price"])
    assert written == 1
    assert problems == ["row 2: units 'two' is not a number"], f"got {problems!r}"
    assert json.loads(target.read_text(encoding="utf-8")) == [
        {"name": "Ada", "units": 2.0, "price": 9.99}
    ]


def test_csv_to_json_missing_source_raises(day, tmp_path):
    with pytest.raises(FileNotFoundError):
        day.csv_to_json(tmp_path / "nope.csv", tmp_path / "out.json", ["amount"])
