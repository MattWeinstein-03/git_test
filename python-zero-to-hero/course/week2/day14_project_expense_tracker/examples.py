"""Day 14 — the shape of the project, demonstrated on a DIFFERENT app.

Run me from the course root:

    python course/week2/day14_project_expense_tracker/examples.py

This is a reading log, not an expense tracker. It is deliberately a different
domain built with exactly the pattern your project needs:

    a validated dataclass  ->  a store class  ->  json persistence
                           ->  csv import that survives bad rows
                           ->  pure reporting functions
                           ->  a thin main() that does all the printing

Read it for the SHAPE. Then build the expense tracker yourself.

Everything is written into a `tmp/` folder next to this file, which is deleted
on the way out.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
TMP = HERE / "tmp"


# ---------------------------------------------------------------------------
# The custom exception: one type for "your data is not acceptable".
# ---------------------------------------------------------------------------
class ReadingError(Exception):
    """Raised when a reading-log entry fails validation."""


# ---------------------------------------------------------------------------
# M1-shaped: a dataclass that cannot exist in an invalid state.
# ---------------------------------------------------------------------------
@dataclass
class Reading:
    """One book you read, on one date."""

    pages: int
    title: str
    date: str  # ISO YYYY-MM-DD, so it sorts chronologically as plain text
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Validation lives HERE, the single door into the object. Every caller
        # (menu, csv import, json load) gets the same rules for free.
        if isinstance(self.pages, bool) or not isinstance(self.pages, int):
            raise ReadingError(f"pages must be a whole number, got {type(self.pages).__name__}")
        if self.pages <= 0:
            raise ReadingError(f"pages must be positive, got {self.pages}")
        if not self.title.strip():
            raise ReadingError("title must not be empty")
        if not _is_iso_date(self.date):
            raise ReadingError(f"date must be YYYY-MM-DD, got {self.date!r}")
        # ...and normalising lives here too, so nothing downstream has to guess.
        self.title = self.title.strip()

    @property
    def month(self) -> str:
        """The "YYYY-MM" this reading belongs to."""
        return self.date[:7]

    def to_dict(self) -> dict:
        """A plain dict, ready for json.dump."""
        return {
            "pages": self.pages,
            "title": self.title,
            "date": self.date,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Reading:
        """Alternative constructor: build from a dict, e.g. straight out of JSON."""
        for name in ("pages", "title", "date"):
            if name not in data:
                raise ReadingError(f"missing field: {name}")
        return cls(
            pages=data["pages"],
            title=data["title"],
            date=data["date"],
            tags=list(data.get("tags", [])),
        )


def _is_iso_date(text: str) -> bool:
    """True when `text` has the SHAPE of an ISO date. No datetime needed (Day 17)."""
    if not isinstance(text, str):
        return False
    parts = text.split("-")
    if len(parts) != 3:
        return False
    year, month, day = parts
    if len(year) != 4 or len(month) != 2 or len(day) != 2:
        return False
    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        return False
    return 1 <= int(month) <= 12 and 1 <= int(day) <= 31


# ---------------------------------------------------------------------------
# M2/M3/M4/M5-shaped: the store owns the collection and answers questions.
# ---------------------------------------------------------------------------
def _by_total_then_name(pair: tuple[str, float]) -> tuple[float, str]:
    """Sort key: biggest total first, then alphabetically. No lambda (Day 16)."""
    name, total = pair
    return (-total, name)


class ReadingLog:
    """A collection of Readings, with persistence and reports."""

    def __init__(self, readings: list[Reading] | None = None) -> None:
        # why: copy the caller's list, so nobody can bypass add() later.
        self._readings: list[Reading] = list(readings) if readings is not None else []

    # --- M2: the container ------------------------------------------------
    def add(self, reading: Reading) -> None:
        if not isinstance(reading, Reading):
            raise TypeError(f"expected a Reading, got {type(reading).__name__}")
        self._readings.append(reading)

    def remove(self, index: int) -> Reading:
        return self._readings.pop(index)  # IndexError propagates, correctly

    def all(self) -> list[Reading]:
        return list(self._readings)  # a copy: callers cannot mutate our list

    def __len__(self) -> int:
        return len(self._readings)

    def __iter__(self):
        return iter(self._readings)

    # --- M3: persistence --------------------------------------------------
    def save(self, path: Path) -> int:
        """Write every reading as a JSON array. Returns how many were written."""
        path.parent.mkdir(parents=True, exist_ok=True)
        records = []
        for reading in self._readings:
            records.append(reading.to_dict())
        with open(path, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=2)
        return len(records)

    @classmethod
    def load(cls, path: Path) -> ReadingLog:
        """Read a log back. A missing file is an empty log, not an error."""
        try:
            with open(path, encoding="utf-8") as file:
                records = json.load(file)
        except FileNotFoundError:
            return cls()  # first run: perfectly normal
        except json.JSONDecodeError as error:
            raise ReadingError(f"{path} is not valid JSON") from error
        if not isinstance(records, list):
            raise ReadingError(f"{path} must contain a list of readings")
        log = cls()
        for record in records:
            log.add(Reading.from_dict(record))
        return log

    # --- M4: reporting (no printing, no disk) -----------------------------
    def total_pages(self) -> int:
        total = 0
        for reading in self._readings:
            total += reading.pages
        return total

    def pages_by_title(self) -> dict[str, int]:
        """{title: pages}, keys alphabetical for stable output."""
        raw: dict[str, int] = {}
        for reading in self._readings:
            raw[reading.title] = raw.get(reading.title, 0) + reading.pages
        ordered: dict[str, int] = {}
        for title in sorted(raw):
            ordered[title] = raw[title]
        return ordered

    def top_titles(self, limit: int) -> list[tuple[str, int]]:
        if limit <= 0:
            return []
        pairs = list(self.pages_by_title().items())
        pairs.sort(key=_by_total_then_name)
        return pairs[:limit]

    def monthly_pages(self) -> dict[str, int]:
        """{"YYYY-MM": pages}, in chronological order (ISO strings sort that way)."""
        raw: dict[str, int] = {}
        for reading in self._readings:
            raw[reading.month] = raw.get(reading.month, 0) + reading.pages
        ordered: dict[str, int] = {}
        for month in sorted(raw):
            ordered[month] = raw[month]
        return ordered

    # --- M5: csv import that never crashes on one bad row -----------------
    def import_csv(self, path: Path) -> tuple[int, list[str]]:
        """Add every usable row. Returns (added, problems)."""
        added = 0
        problems: list[str] = []
        with open(path, encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for index, row in enumerate(reader):
                number = index + 1

                missing = None
                for name in ("pages", "title", "date"):
                    value = row.get(name)
                    if value is None or str(value).strip() == "":
                        missing = name
                        break
                if missing is not None:
                    problems.append(f"row {number}: missing {missing}")
                    continue

                try:
                    pages = int(str(row["pages"]).strip())
                except ValueError:
                    problems.append(f"row {number}: pages {row['pages']!r} is not a number")
                    continue

                try:
                    reading = Reading(
                        pages=pages,
                        title=str(row["title"]),
                        date=str(row["date"]).strip(),
                    )
                except ReadingError as error:
                    problems.append(f"row {number}: {error}")
                    continue

                self.add(reading)
                added += 1
        return added, problems


# ---------------------------------------------------------------------------
# The thin layer that prints. Everything above returns data instead.
# ---------------------------------------------------------------------------
def format_report(log: ReadingLog) -> str:
    """Turn a log into a printable report. Pure: takes data, returns a string."""
    if not len(log):
        return "(nothing logged yet)"
    lines = [f"{'title':<28}{'pages':>7}"]
    for title, pages in log.pages_by_title().items():
        lines.append(f"{title:<28}{pages:>7}")
    lines.append("-" * 35)
    lines.append(f"{'TOTAL':<28}{log.total_pages():>7}")
    for month, pages in log.monthly_pages().items():
        lines.append(f"{month:<28}{pages:>7}")
    return "\n".join(lines)


def titles_of(log: "ReadingLog") -> list[str]:
    """The titles in a log, in order. A loop, because comprehensions are Day 15."""
    found = []
    for reading in log:
        found.append(reading.title)
    return found


def cleanup(folder: Path) -> None:
    """Delete `folder` and everything in it."""
    if not folder.exists():
        return
    for child in sorted(folder.iterdir()):
        if child.is_file():
            child.unlink()
    folder.rmdir()


def main() -> None:
    print("=" * 70)
    print("1. A validated dataclass: the only door in is __post_init__")
    print("=" * 70)

    reading = Reading(320, "  Dune ", "2024-03-01", ["scifi"])
    print("valid    ->", reading)
    print("  .month ->", reading.month, " (a @property, no parentheses)")
    print("  .title ->", repr(reading.title), "(normalised for you)")

    for bad in (
        (0, "Dune", "2024-03-01"),
        (10, "   ", "2024-03-01"),
        (10, "Dune", "1 March 2024"),
        ("ten", "Dune", "2024-03-01"),
    ):
        try:
            Reading(*bad)  # noqa: B017 - the point is the message
        except ReadingError as error:
            print(f"rejected {bad!r:<34} -> {error}")

    print()
    print("dataclass equality compares FIELDS, which makes round-trip tests easy:")
    print("  Reading(1, 'a', '2024-01-01') == Reading(1, 'a', '2024-01-01') ->",
          Reading(1, "a", "2024-01-01") == Reading(1, "a", "2024-01-01"))

    print()
    print("=" * 70)
    print("2. The store: it owns the collection")
    print("=" * 70)

    log = ReadingLog()
    log.add(Reading(320, "Dune", "2024-03-01"))
    log.add(Reading(180, "Emma", "2024-03-14"))
    log.add(Reading(90, "Dune", "2024-04-02"))
    print("len(log)      ->", len(log), "  (__len__)")
    print("iterating     ->", titles_of(log), "  (__iter__)")
    print("log.all()     -> a COPY, so this cannot break the store:")
    stolen = log.all()
    stolen.clear()
    print("  after clearing the copy, len(log) is still", len(log))
    try:
        log.add("not a reading")
    except TypeError as error:
        print("log.add('not a reading') -> TypeError:", error)

    print()
    print("=" * 70)
    print("3. JSON persistence, and a lossless round trip")
    print("=" * 70)

    TMP.mkdir(parents=True, exist_ok=True)
    data_file = TMP / "reading_log.json"
    written = log.save(data_file)
    print(f"saved {written} records to tmp/{data_file.name}")
    print("file on disk (first 6 lines):")
    for line in data_file.read_text(encoding="utf-8").splitlines()[:6]:
        print("   ", line)

    reloaded = ReadingLog.load(data_file)
    print("reloaded ->", len(reloaded), "records")
    print("round trip is lossless ->", reloaded.all() == log.all())

    print()
    print("a missing file is NOT an error — a first run has nothing to read:")
    print("  ReadingLog.load(tmp/never_written.json) ->",
          len(ReadingLog.load(TMP / "never_written.json")), "records")

    broken = TMP / "broken.json"
    broken.write_text('[{"pages": 1, ', encoding="utf-8")
    try:
        ReadingLog.load(broken)
    except ReadingError as error:
        print("  a CORRUPT file IS an error ->", error)
        print("    (returning an empty log there would look like 'you read nothing'")
        print("     and could then be saved over the top of your real data)")

    print()
    print("=" * 70)
    print("4. Reporting: methods that return data, not printing")
    print("=" * 70)

    print("total_pages()    ->", log.total_pages())
    print("pages_by_title() ->", log.pages_by_title())
    print("top_titles(1)    ->", log.top_titles(1))
    print("top_titles(0)    ->", log.top_titles(0))
    print("monthly_pages()  ->", log.monthly_pages(), "(ISO keys sort chronologically)")
    print("the reports agree ->",
          log.total_pages() == sum(log.monthly_pages().values()))

    print()
    print("=" * 70)
    print("5. CSV import: skip bad rows, report every one")
    print("=" * 70)

    dirty = TMP / "import.csv"
    dirty.write_text(
        "pages,title,date\n"
        "320,Dune,2024-03-01\n"  # fine
        "abc,Emma,2024-03-14\n"  # pages not a number
        ",Persuasion,2024-03-15\n"  # missing pages
        "100,,2024-03-16\n"  # missing title
        "150,Ulysses,16 June 1904\n"  # bad date shape
        "-4,Anathem,2024-03-17\n"  # not positive
        "42,  Piranesi  ,2024-04-01\n",  # fine, and untrimmed
        encoding="utf-8",
    )
    fresh = ReadingLog()
    added, problems = fresh.import_csv(dirty)
    print(f"imported {added} rows, skipped {len(problems)}:")
    for problem in problems:
        print("  ", problem)
    print("kept ->", titles_of(fresh))
    print("one bad row never stops the import, and nothing is dropped silently")

    print()
    print("=" * 70)
    print("6. The printing layer, kept separate")
    print("=" * 70)
    print(format_report(log))
    print()
    print("format_report() is pure: give it a log, get a string. That is why it")
    print("can be tested in one assertion and reused by a menu, a file, or a web")
    print("page. Your project's main() should be this thin.")


if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup(TMP)
        print()
        print("tmp/ removed — the repository is unchanged.")
        print("Now build the expense tracker in exercises.py. Same shape, your code.")
