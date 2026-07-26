"""Day 10 — Files and data: runnable demonstrations.

Run me from the course root:

    python course/week2/day10_files_and_data/examples.py

I create a `tmp/` folder next to this file, do all my work in there, and delete
it again on the way out — including if something goes wrong. Nothing outside
`tmp/` is ever touched. Section numbers match LESSON.md.
"""

import csv
import json
import os.path  # only to compare it with pathlib in section 1.1
from pathlib import Path

# `__file__` is the path of THIS script, so tmp/ lands next to it no matter
# which directory you launched python from.
HERE = Path(__file__).parent
TMP = HERE / "tmp"


def cleanup(folder: Path) -> None:
    """Delete every file in `folder`, then the folder. Only used for our tmp/."""
    if not folder.exists():
        return
    for child in sorted(folder.iterdir()):
        if child.is_file():
            child.unlink()
    folder.rmdir()


def main() -> None:
    # -----------------------------------------------------------------------
    # 1. Paths are objects
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("1. pathlib.Path")
    print("=" * 70)

    sample = Path("/home/you/reports/sales_2024.csv")
    print("path       ->", sample)
    print("  .name    ->", sample.name, "  (file name with extension)")
    print("  .stem    ->", sample.stem, "  (file name without extension)")
    print("  .suffix  ->", sample.suffix, "  (extension, dot included)")
    print("  .parent  ->", sample.parent)
    print("  .parts   ->", sample.parts)
    print("  .is_absolute() ->", sample.is_absolute())

    # The / operator joins parts with the right separator for this OS.
    joined = Path("data") / "raw" / "sales.csv"
    print("Path('data') / 'raw' / 'sales.csv' ->", joined)

    # mkdir: parents=True creates intermediate folders, exist_ok=True means
    # "already there is fine" instead of FileExistsError.
    TMP.mkdir(parents=True, exist_ok=True)
    print("created working folder ->", TMP.name + "/", "exists:", TMP.is_dir())

    print()
    print("--- 1.1 the same job, os.path vs pathlib ---")
    old_style = os.path.join("data", "sales.csv")
    print("os.path.join('data', 'sales.csv')       ->", old_style)
    print("os.path.basename(...)                   ->", os.path.basename(old_style))
    print("os.path.splitext(os.path.basename(...)) ->", os.path.splitext(os.path.basename(old_style))[0])
    new_style = Path("data") / "sales.csv"
    print("Path('data') / 'sales.csv'              ->", new_style)
    print("  .name / .stem                         ->", new_style.name, "/", new_style.stem)
    print("Read os.path fluently; write pathlib.")

    # -----------------------------------------------------------------------
    # 2. open(), modes, and what `with` guarantees
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("2. open(), modes, and `with`")
    print("=" * 70)

    notes = TMP / "notes.txt"

    with open(notes, "w", encoding="utf-8") as file:  # "w" CREATES or TRUNCATES
        file.write("first line\n")  # write() adds no newline of its own
    print("after mode 'w'  ->", repr(notes.read_text(encoding="utf-8")))

    with open(notes, "w", encoding="utf-8") as file:  # "w" again: previous text GONE
        file.write("second line\n")
    print("after mode 'w'  ->", repr(notes.read_text(encoding="utf-8")), " <- 'first' was destroyed")

    with open(notes, "a", encoding="utf-8") as file:  # "a" appends
        file.write("third line\n")
    print("after mode 'a'  ->", repr(notes.read_text(encoding="utf-8")))

    # "x" refuses to touch an existing file. Useful when overwriting is a bug.
    try:
        with open(notes, "x", encoding="utf-8") as file:
            file.write("never happens")
    except FileExistsError as error:
        print("mode 'x' on an existing file ->", type(error).__name__)

    # `with` closes the file even when the block explodes.
    try:
        with open(notes, "a", encoding="utf-8") as file:
            file.write("written before the error\n")
            raise ValueError("boom")
    except ValueError:
        print("after an exception inside `with`, file.closed ->", file.closed)
    print("and the write survived  ->", repr(notes.read_text(encoding="utf-8").splitlines()[-1]))

    # Using the object after the block is a classic error.
    try:
        file.read()
    except ValueError as error:
        print("using a closed file ->", type(error).__name__ + ":", error)

    # -----------------------------------------------------------------------
    # 3. Encoding and newlines
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("3. Encoding and newlines")
    print("=" * 70)

    text = "café"
    print("'café' characters ->", len(text), " bytes in utf-8 ->", len(text.encode("utf-8")))
    print("encoded           ->", text.encode("utf-8"))

    accented = TMP / "accented.txt"
    accented.write_text("café £5\n", encoding="utf-8")
    print("read back as utf-8 ->", repr(accented.read_text(encoding="utf-8")))
    try:
        accented.read_text(encoding="ascii")
    except UnicodeDecodeError as error:
        print("read as ascii      ->", type(error).__name__ + ":", error)
    print("errors='replace'   ->", repr(accented.read_text(encoding="ascii", errors="replace")))
    print("errors='ignore'    ->", repr(accented.read_text(encoding="ascii", errors="ignore")), "<- data DELETED")

    # Universal newlines: whatever the file used, you read "\n".
    crlf_file = TMP / "windows.txt"
    # newline="" on WRITE means "do not translate what I give you".
    with open(crlf_file, "w", encoding="utf-8", newline="") as file:
        file.write("a\r\nb\r\n")
    print("raw bytes on disk  ->", crlf_file.read_bytes())
    with open(crlf_file, encoding="utf-8") as file:
        print("read in text mode  ->", repr(file.read()), "<- \\r\\n became \\n")

    # -----------------------------------------------------------------------
    # 4. Whole file vs line by line
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("4. Whole file vs line by line")
    print("=" * 70)

    log = TMP / "app.log"
    with open(log, "w", encoding="utf-8") as file:
        file.writelines(["INFO start\n", "WARN slow query\n", "INFO done\n"])

    with open(log, encoding="utf-8") as file:
        whole = file.read()
    print("file.read()      ->", repr(whole))

    with open(log, encoding="utf-8") as file:
        print("file.readlines() ->", file.readlines())

    print("iterating (constant memory, any file size):")
    with open(log, encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            print(f"  line {number}: {line.rstrip(chr(10))!r}")

    print("Path.read_text() ->", repr(log.read_text(encoding="utf-8")[:11]) + "...")

    warnings = 0
    with open(log, encoding="utf-8") as file:
        for line in file:
            if line.startswith("WARN"):
                warnings += 1
    print("counted WARN lines without loading the file ->", warnings)

    # -----------------------------------------------------------------------
    # 5. CSV
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("5. csv")
    print("=" * 70)

    positional = TMP / "amounts.csv"
    rows = [["name", "note", "amount"],
            ["Ada", "Owes me 3, maybe 4", "12.50"],  # a comma INSIDE a field
            ["Grace", "paid", "7.00"]]

    # newline="" every time you hand a file to csv. Not optional.
    with open(positional, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(rows[0])
        writer.writerows(rows[1:])

    print("file on disk:")
    for line in positional.read_text(encoding="utf-8").splitlines():
        print("  ", line)
    print("note how csv quoted the field containing a comma, all by itself")

    with open(positional, encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)  # pull the header row off first
        print("header ->", header)
        for row in reader:
            print("row    ->", row)

    print()
    print("naive splitting gets it wrong:")
    bad_line = positional.read_text(encoding="utf-8").splitlines()[1]
    print("  line.split(',') ->", bad_line.split(","), "<- 4 fields, not 3")

    print()
    print("--- DictReader / DictWriter: fields by NAME ---")
    named = TMP / "expenses.csv"
    with open(named, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "category", "amount"])
        writer.writeheader()  # without this, your first record becomes the header
        writer.writerow({"date": "2024-03-01", "category": "food", "amount": "12.50"})
        writer.writerows([
            {"date": "2024-03-02", "category": "transport", "amount": "2.75"},
            {"date": "2024-03-03", "category": "food"},  # missing amount -> empty cell
        ])

    with open(named, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        print("fieldnames ->", reader.fieldnames)
        for row in reader:
            print("row        ->", row)
    print("every value is a str — there are no numbers in a csv file")
    print("'12.50' * 2 ->", "12.50" * 2, " <- convert with float() before doing maths")

    # A short row: DictReader fills the gap with None.
    ragged = TMP / "ragged.csv"
    ragged.write_text("date,category,amount\n2024-03-04,food\n", encoding="utf-8")
    with open(ragged, encoding="utf-8", newline="") as file:
        print("short row  ->", next(csv.DictReader(file)), "<- missing field is None")

    # -----------------------------------------------------------------------
    # 6. JSON
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("6. json")
    print("=" * 70)

    data = {"name": "Ada", "scores": [90, 95], "active": True, "note": None}
    as_text = json.dumps(data)
    print("json.dumps(data) ->", as_text)
    print("  True became true, None became null (JSON spelling, not Python)")
    print("json.loads(text) == data ->", json.loads(as_text) == data)

    doc = TMP / "person.json"
    with open(doc, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
    print("file with indent=2, sort_keys=True:")
    for line in doc.read_text(encoding="utf-8").splitlines():
        print("  ", line)

    with open(doc, encoding="utf-8") as file:
        loaded = json.load(file)
    print("json.load(file)['scores'][1] ->", loaded["scores"][1])

    print()
    print("--- what survives the round trip ---")
    original = {"tags": ("a", "b"), "counts": {1: "one"}}
    round_tripped = json.loads(json.dumps(original))
    print("in  ->", original)
    print("out ->", round_tripped)
    print("equal? ->", original == round_tripped, " <- tuple became list, int key became str")
    try:
        json.dumps({"unique": {1, 2}})
    except TypeError as error:
        print("a set cannot be serialised at all ->", type(error).__name__ + ":", error)
    print("fix: convert first, e.g. sorted({1, 2}) ->", json.dumps({"unique": sorted({1, 2})}))

    print()
    print("--- corrupt and missing files ---")
    broken = TMP / "broken.json"
    broken.write_text('{"name": "Ada", ', encoding="utf-8")  # truncated write

    def load_data(path: Path) -> dict:
        """Return saved data, or an empty dict when there is nothing usable."""
        try:
            with open(path, encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"  {path.name} does not exist yet — first run, that is normal")
            return {}
        except json.JSONDecodeError as error:
            print(f"  {path.name} is corrupt ({error}); starting fresh")
            return {}

    print("load_data(broken.json)  ->", load_data(broken))
    print("load_data(missing.json) ->", load_data(TMP / "missing.json"))
    print("JSONDecodeError is a ValueError? ->", issubclass(json.JSONDecodeError, ValueError))

    # -----------------------------------------------------------------------
    # 7. Data hygiene
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("7. Data hygiene: never crash the import on one bad row")
    print("=" * 70)

    dirty = TMP / "dirty.csv"
    dirty.write_text(
        "name,amount\n"
        "  Ada  ,12.50\n"  # untrimmed whitespace
        "Grace,n/a\n"  # not a number
        ",7.00\n"  # missing name
        "Linus,-3\n"  # non-positive
        "Katherine,9.99\n",
        encoding="utf-8",
    )

    def clean(rows: list[dict], required: list[str]) -> tuple[list[dict], list[str]]:
        """Return (good rows, problem messages). Never raises."""
        good: list[dict] = []
        problems: list[str] = []
        for index, row in enumerate(rows):
            number = index + 1
            missing = []
            for field in required:
                value = row.get(field)
                if value is None or str(value).strip() == "":
                    missing.append(field)
            if missing:
                problems.append(f"row {number}: missing {', '.join(missing)}")
                continue
            try:
                amount = float(row["amount"])
            except ValueError:
                problems.append(f"row {number}: amount {row['amount']!r} is not a number")
                continue
            if amount <= 0:
                problems.append(f"row {number}: amount must be positive, got {amount}")
                continue
            good.append({"name": row["name"].strip(), "amount": amount})
        return good, problems

    with open(dirty, encoding="utf-8", newline="") as file:
        all_rows = list(csv.DictReader(file))

    good_rows, problems = clean(all_rows, ["name", "amount"])
    print(f"imported {len(good_rows)} of {len(all_rows)} rows")
    for row in good_rows:
        print("  kept   ->", row)
    for problem in problems:
        print("  skipped->", problem)

    print()
    print("--- write to a temp file, then replace: never a half-written data file ---")
    final = TMP / "clean.json"
    staging = final.with_suffix(".json.tmp")
    staging.write_text(json.dumps(good_rows, indent=2), encoding="utf-8")
    staging.replace(final)  # atomic on the same filesystem
    print("wrote", final.name, "->", len(json.loads(final.read_text(encoding='utf-8'))), "records")
    print("staging file still around? ->", staging.exists())

    print()
    print("files created during this demo (all inside tmp/, all about to be deleted):")
    for child in sorted(TMP.iterdir()):
        print(f"  {child.name:<16}{child.stat().st_size:>6} bytes")


if __name__ == "__main__":
    try:
        main()
    finally:
        # finally: the tmp/ folder goes away even if a demo above raises.
        cleanup(TMP)
        print()
        print("tmp/ removed — the repository is exactly as it was.")
        print("Done. Now open exercises.py in this folder.")
