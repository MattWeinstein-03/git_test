"""Day 10 exercises — Files and data.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

House rules for this day, and for the rest of your career:

* Every function takes the path it should work on. Never hard-code a path, and
  never write anywhere except a path you were handed.
* Always pass `encoding="utf-8"` explicitly.
* Always use `with` (or Path.read_text/write_text, which close for you).
* Any file you hand to the `csv` module is opened with `newline=""`.

The tests give you pytest's `tmp_path`: a fresh empty directory per test. That
is why running them never leaves anything behind in the repository.

Grade your work from the course root:

    python check.py day10
    python check.py day10 -v      # show full failure detail
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Exercise 1 — write a text file
# ---------------------------------------------------------------------------
def write_text_file(path: Path, text: str) -> int:
    """Write `text` to `path` as UTF-8, overwriting anything already there.

    Create the parent directory (and any missing directories above it) if it
    does not exist yet — writing into a directory that is not there is a
    FileNotFoundError, not something Python fixes for you.

    Args:
        path: where to write.
        text: the exact content to write. Do not add a trailing newline.

    Returns:
        The number of characters written.

    Examples:
        write_text_file(tmp_path / "a.txt", "hello") -> 5
        # then (tmp_path / "a.txt").read_text(encoding="utf-8") == "hello"
        write_text_file(tmp_path / "deep" / "b.txt", "hi") -> 2
        write_text_file(tmp_path / "a.txt", "") -> 0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: write_text_file")


# ---------------------------------------------------------------------------
# Exercise 2 — read a text file line by line
# ---------------------------------------------------------------------------
def read_lines(path: Path) -> list[str]:
    """Return the lines of `path` with their trailing newline removed.

    Read the file line by line rather than all at once, so this would still
    work on a file too big for memory. Blank lines are kept as "". A missing
    file is a real problem here, so let the FileNotFoundError propagate.

    Args:
        path: the file to read.

    Returns:
        A list of lines, without "\\n" endings.

    Examples:
        # file contains "a\\nb\\n"
        read_lines(path) -> ["a", "b"]
        # file contains "a\\n\\nb"     (no final newline)
        read_lines(path) -> ["a", "", "b"]
        # empty file
        read_lines(path) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: read_lines")


# ---------------------------------------------------------------------------
# Exercise 3 — append instead of overwrite
# ---------------------------------------------------------------------------
def append_line(path: Path, line: str) -> int:
    """Append `line` plus a newline to `path`, and return the new line count.

    The file is created if it does not exist. Existing content must survive —
    getting this wrong is the "w" versus "a" mistake that eats data.

    Args:
        path: the file to append to.
        line: the text to add. You add the "\\n" yourself.

    Returns:
        How many lines the file has after the append.

    Examples:
        append_line(new_path, "first") -> 1
        append_line(new_path, "second") -> 2
        # file now contains "first\\nsecond\\n"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: append_line")


# ---------------------------------------------------------------------------
# Exercise 4 — process a file without loading all of it
# ---------------------------------------------------------------------------
def count_words(path: Path) -> dict[str, int]:
    """Count how often each word appears in the text file at `path`.

    Words are separated by any whitespace and compared case-insensitively.
    Do not strip punctuation — "cat." and "cat" count as different words here,
    which keeps the rule simple. Iterate the file line by line.

    Args:
        path: the text file to read.

    Returns:
        A dict mapping each lowercased word to its count.

    Examples:
        # file contains "the cat\\nThe dog\\n"
        count_words(path) -> {"the": 2, "cat": 1, "dog": 1}
        # empty file
        count_words(path) -> {}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: count_words")


# ---------------------------------------------------------------------------
# Exercise 5 — write a CSV with a header
# ---------------------------------------------------------------------------
def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> int:
    """Write `rows` to `path` as CSV using `fieldnames` for the column order.

    Write the header row first. Use csv.DictWriter, and remember `newline=""`
    on the open() call. A row missing one of the fieldnames writes an empty
    cell for it rather than crashing.

    Args:
        path: where to write the CSV.
        rows: one dict per data row.
        fieldnames: column names, in the order they should appear.

    Returns:
        The number of DATA rows written (the header does not count).

    Examples:
        rows = [{"name": "Ada", "amount": "12.50"}, {"name": "Grace", "amount": "7"}]
        write_csv(path, rows, ["name", "amount"]) -> 2
        # file now contains:
        #   name,amount
        #   Ada,12.50
        #   Grace,7
        write_csv(path, [], ["name"]) -> 0        # header only
        write_csv(path, [{"name": "Ada"}], ["name", "amount"]) -> 1   # -> "Ada,"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: write_csv")


# ---------------------------------------------------------------------------
# Exercise 6 — read a CSV by field name
# ---------------------------------------------------------------------------
def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read the CSV at `path` and return one dict per data row.

    Use csv.DictReader so the header row becomes the keys. Every value stays a
    string — converting is a separate decision, made by the caller.

    Args:
        path: the CSV file to read.

    Returns:
        A list of dicts, one per data row, in file order. A file with only a
        header row gives [].

    Examples:
        # file contains "name,amount\\nAda,12.50\\n"
        read_csv_rows(path) -> [{"name": "Ada", "amount": "12.50"}]
        # file contains only "name,amount\\n"
        read_csv_rows(path) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: read_csv_rows")


# ---------------------------------------------------------------------------
# Exercise 7 — save JSON
# ---------------------------------------------------------------------------
def save_json(path: Path, data: object) -> None:
    """Write `data` to `path` as JSON, readable by a human.

    Use indent=2 and sort_keys=True so the file is stable and diff-friendly,
    and encoding="utf-8". Create the parent directory if needed. Overwrite any
    existing file.

    Args:
        path: where to write.
        data: any JSON-serialisable object (dict, list, str, int, float, bool, None).

    Returns:
        None. This function exists for its side effect.

    Examples:
        save_json(path, {"b": 1, "a": 2})
        # file contains:
        #   {
        #     "a": 2,
        #     "b": 1
        #   }
        save_json(path, [1, 2, 3])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: save_json")


# ---------------------------------------------------------------------------
# Exercise 8 — load JSON without crashing on a missing or broken file
# ---------------------------------------------------------------------------
def load_json(path: Path, default: object = None) -> object:
    """Load JSON from `path`, returning `default` when that is not possible.

    Two failures are expected and must both give `default`:
      * the file does not exist (normal on a program's first run);
      * the file exists but is not valid JSON (a half-written file).
    Catch those two specifically. Do not use a bare `except`.

    Args:
        path: the file to read.
        default: what to return when the file is missing or corrupt.

    Returns:
        The decoded object, or `default`.

    Examples:
        load_json(path_that_holds__1_2_3) -> [1, 2, 3]
        load_json(missing_path) -> None
        load_json(missing_path, {}) -> {}
        load_json(path_holding_half_a_document, {}) -> {}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: load_json")


# ---------------------------------------------------------------------------
# Exercise 9 — data hygiene
# ---------------------------------------------------------------------------
def clean_rows(
    rows: list[dict[str, str]], required: list[str]
) -> tuple[list[dict[str, str]], list[str]]:
    """Keep the usable rows, and explain every rejection. Never raise.

    A field counts as missing when its key is absent, its value is None, or its
    value is empty once stripped of whitespace. Check the required fields in
    the order given.

    For a rejected row, append exactly:
        f"row {n}: missing {', '.join(missing_fields)}"
    where `n` is the 1-based position of the row in `rows`.

    For an accepted row, put a NEW dict in the result holding every key the row
    had, with each value converted to a string and stripped. Do not modify the
    input rows.

    Args:
        rows: raw rows, e.g. straight out of csv.DictReader.
        required: the field names a row must have to be usable.

    Returns:
        A 2-tuple (good_rows, problems).

    Examples:
        rows = [{"name": "  Ada ", "amount": "12.50"},
                {"name": "", "amount": "7"},
                {"amount": "3"},
                {"name": "Grace", "amount": None}]
        clean_rows(rows, ["name", "amount"]) ->
            ([{"name": "Ada", "amount": "12.50"}],
             ["row 2: missing name",
              "row 3: missing name",
              "row 4: missing amount"])

        clean_rows([], ["name"]) -> ([], [])
        clean_rows([{"a": "1"}], []) -> ([{"a": "1"}], [])
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: clean_rows")


# ---------------------------------------------------------------------------
# Exercise 10 — the hard one: a full CSV -> JSON pipeline
# ---------------------------------------------------------------------------
def csv_to_json(
    csv_path: Path, json_path: Path, numeric_fields: list[str]
) -> tuple[int, list[str]]:
    """Convert a CSV file into a JSON array of records, converting numbers.

    Steps:
      1. Read `csv_path` with csv.DictReader.
      2. For each row (1-based numbering), check every name in `numeric_fields`
         in order:
           * absent, None, or empty after stripping ->
                 f"row {n}: missing {field}"      (reject the row)
           * present but not a number ->
                 f"row {n}: {field} {value!r} is not a number"   (reject the row)
           * otherwise convert it with float()
      3. Rows that pass become dicts with every original key: the numeric
         fields as floats, every other value as a stripped string.
      4. Write the surviving records to `json_path` as a JSON array with
         indent=2. Write the file even when nothing survived (an empty array).

    A missing `csv_path` is a genuine error — let FileNotFoundError propagate.
    A single bad row must never stop the conversion.

    Args:
        csv_path: the CSV file to read.
        json_path: where to write the JSON array.
        numeric_fields: field names that must be converted to float.

    Returns:
        A 2-tuple (written, problems): how many records were written, and one
        message per rejected row, in row order.

    Examples:
        # sales.csv:
        #   name,amount
        #   Ada,12.50
        #   Grace,n/a
        #   ,3
        csv_to_json(csv_path, json_path, ["amount"]) ->
            (1, ["row 2: amount 'n/a' is not a number"])
        # and sales.json contains: [{"name": "Ada", "amount": 12.5}]
        # (the third row is fine: "name" is not in numeric_fields)

        csv_to_json(header_only_csv, json_path, ["amount"]) -> (0, [])
        # and the json file contains: []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: csv_to_json")


if __name__ == "__main__":
    # Quick manual poking ground: write into a tmp/ folder next to this file,
    # then delete it. Never scatter files into the repository.
    scratch = Path(__file__).parent / "tmp"
    scratch.mkdir(exist_ok=True)
    try:
        print("scratch folder:", scratch)
        # print(write_text_file(scratch / "hello.txt", "hello"))
        print("Run `python check.py day10` from the course root to grade your work.")
    finally:
        for child in scratch.iterdir():
            child.unlink()
        scratch.rmdir()
