"""Day 07 — the shape of the project, demonstrated on a DIFFERENT dataset.

Run me from the course root:

    python course/week1/day07_project_text_toolkit/examples.py

This is a **log analyser**, not a text toolkit. The data is not prose: it is
seven pipe-separated log lines, plus one line of rubbish that has to survive
being read. The domain is different, the fields are different, the column widths
are different — and the *shape* is exactly the shape your project needs:

    1  normalise the raw input
    2  count things into a dict
    3  rank the counts, biggest first, ties broken predictably
    4  compute a handful of statistics
    5  render one aligned report string
    6  print it from one place, and one place only

Read it for the shape. The numbers here are about log levels; the numbers in your
project are about words. Nothing in this file is a milestone answer.

Days 1-6 tools only, same as the project: strings and their methods, f-strings,
`if`, loops, lists, tuples, dicts, sets. Nothing is read from disk, nothing is
written, nothing is typed in.
"""


# ---------------------------------------------------------------------------
# The data lives in the module, exactly as SAMPLE_TEXT does in the project.
# Reading this out of a real file is Day 10.
#
# Note the deliberate mess: inconsistent capitals, ragged spacing around the
# pipes, one line that is not a log entry at all, and one blank line. Real input
# always looks like this, and "normalise first" is the answer to all of it.
# ---------------------------------------------------------------------------
LOG_TEXT = """
2024-03-01 09:14:02 | INFO  | user ada logged in
2024-03-01 09:14:40 |  warn | disk usage at 91%
2024-03-01 09:15:11 | INFO  |    user ada opened report

this line is not a log entry at all
2024-03-01 09:16:03 | ERROR | database timeout after 30s
2024-03-01 09:16:04 | error | retrying database connection
2024-03-01 09:16:09 | info  | database connection restored
2024-03-01 09:20:00 | WARN  | disk usage at 93%
"""

# The separator between a log line's three fields.
SEPARATOR = "|"

# How many fields a well-formed line has: timestamp, level, message.
FIELD_COUNT = 3

TITLE = "LOG REPORT"


# ===========================================================================
# 1. Normalising: turn messy input into one predictable shape
# ===========================================================================
def clean_field(field: str) -> str:
    """Trim a field and squeeze every run of internal whitespace to one space.

    `split()` with no argument splits on every run of any whitespace and throws
    away the runs at the ends, so joining the pieces back with a single space
    does the trimming and the squeezing in one step.
    """
    return " ".join(field.split())


def entries_of(text: str) -> list[tuple[str, str]]:
    """Every well-formed log line in `text`, as (level, message) tuples.

    Levels come back upper-cased so that "warn", "Warn" and "WARN" are one
    level. Lines that do not have exactly three pipe-separated fields are
    skipped — including blank lines, which have none.
    """
    entries: list[tuple[str, str]] = []
    for line in text.split("\n"):
        parts = line.split(SEPARATOR)
        # why: a guard, not a nest. Bail out on the lines we cannot use and the
        # rest of the loop body only ever deals with good data.
        if len(parts) != FIELD_COUNT:
            continue
        level = clean_field(parts[1]).upper()
        message = clean_field(parts[2])
        entries.append((level, message))
    return entries


def skipped_count(text: str) -> int:
    """How many non-blank lines of `text` were not usable log entries."""
    skipped = 0
    for line in text.split("\n"):
        if not line.strip():
            continue  # a blank line is not a problem, it is just blank
        if len(line.split(SEPARATOR)) != FIELD_COUNT:
            skipped += 1
    return skipped


# ===========================================================================
# 2. Counting: one dict, one loop, .get for the default
# ===========================================================================
def level_counts(text: str) -> dict[str, int]:
    """{level: how many lines had it}, keys in first-appearance order."""
    counts: dict[str, int] = {}
    for level, _message in entries_of(text):
        # why: .get(level, 0) means the first sighting of a level does not need
        # its own special case. counts[level] + 1 would raise KeyError here.
        counts[level] = counts.get(level, 0) + 1
    return counts


# ===========================================================================
# 3. Ranking: a NAMED key function, and a negated number
# ===========================================================================
def by_count_then_level(pair: tuple[str, int]) -> tuple[int, str]:
    """Sort key for (level, count) pairs: biggest count first, then A-Z.

    `sort` only sorts smallest-first. Negating the count reverses that one
    column while leaving the level names in ordinary alphabetical order, which
    `reverse=True` could not do — it would flip both.

    `key=` wants a function, and this is one: `def`, a name, one argument, a
    returned tuple. Passing it means writing `key=by_count_then_level` with no
    parentheses — you are handing over the function itself, not calling it.
    """
    level, count = pair
    return (-count, level)


def busiest_levels(text: str, n: int) -> list[tuple[str, int]]:
    """The `n` most common levels as (level, count) pairs.

    `n` of 0 or less gives an empty list. Asking for more levels than exist
    gives all of them — slicing past the end of a list is not an error.
    """
    if n <= 0:
        return []
    pairs = list(level_counts(text).items())
    pairs.sort(key=by_count_then_level)
    return pairs[:n]


# ===========================================================================
# 4. Statistics: numbers computed once, returned in a dict
# ===========================================================================
def log_stats(text: str) -> dict[str, object]:
    """Five facts about a log, keyed in the order the report prints them."""
    entries = entries_of(text)
    entry_count = len(entries)

    total_length = 0
    longest_message = ""
    for _level, message in entries:
        total_length += len(message)
        # why: strictly greater than. Two messages of equal length are a tie,
        # and a tie goes to the earlier line; `>=` would hand it to the later
        # one every time.
        if len(message) > len(longest_message):
            longest_message = message

    average_length = 0.0
    if entry_count > 0:
        # why: guarded, because dividing by zero raises and "an empty log" is a
        # perfectly ordinary thing to be handed.
        average_length = round(total_length / entry_count, 2)

    return {
        "entries": entry_count,
        "skipped": skipped_count(text),
        "levels": len(level_counts(text)),
        "avg message len": average_length,
        "longest message": longest_message,
    }


# ===========================================================================
# 5. Rendering: build a list of lines, join once, return a string
# ===========================================================================
def render_log_report(text: str, top_n: int) -> str:
    """The whole log report as one string. Prints nothing — that is main's job.

    Labels are left-justified in 18 characters and values right-justified in 5,
    so the columns line up whatever the numbers are. (Your project uses 16 and
    6. The widths are a decision, not a law — but once written down in a brief
    they are a contract, so match your brief exactly.)
    """
    stats = log_stats(text)
    lines = [TITLE, "=" * len(TITLE)]

    if stats["entries"] == 0:
        lines.append("(no log entries found)")
        return "\n".join(lines)

    # why: one loop over the stats dict instead of five near-identical
    # f-strings. It works because dicts keep insertion order (Day 6), so the
    # rows come out in the order log_stats built them.
    for label, value in stats.items():
        if label == "avg message len":
            lines.append(f"{label:<18}{value:>5.2f}")
        else:
            lines.append(f"{label:<18}{value:>5}")

    if top_n > 0:
        pairs = busiest_levels(text, top_n)
        heading = f"busiest {len(pairs)} levels"
        lines.append("")
        lines.append(heading)
        lines.append("-" * len(heading))
        for level, count in pairs:
            lines.append(f"{level:<18}{count:>5}")

    # why: "\n".join guarantees no trailing newline, and it keeps the lines
    # visible as separate things right up to the last moment.
    return "\n".join(lines)


# ===========================================================================
# 6. main(): the only function in the file that prints
# ===========================================================================
def main() -> None:
    print("=" * 70)
    print("1. Normalising: messy input in, one predictable shape out")
    print("=" * 70)

    print("raw field       ->", repr("  ERROR   "))
    print("clean_field(it) ->", repr(clean_field("  ERROR   ")))
    print("clean_field     ->", repr(clean_field("  disk    usage\tat 91%  ")))
    print()
    print("entries_of(LOG_TEXT) keeps the usable lines and drops the rest:")
    for level, message in entries_of(LOG_TEXT):
        print(f"   {level:<6} {message}")
    print()
    print("lines skipped as unusable ->", skipped_count(LOG_TEXT))
    print("  (the blank line is not counted as a problem — it is just blank)")
    print("note that 'warn', 'WARN', 'info' and 'INFO' have already stopped")
    print("being different things. That is what normalising buys you: every")
    print("later step gets to assume one shape.")

    print()
    print("=" * 70)
    print("2. Counting into a dict")
    print("=" * 70)

    counts = level_counts(LOG_TEXT)
    print("level_counts(LOG_TEXT) ->", counts)
    print("keys are in first-appearance order:", list(counts))
    print("total counted ->", sum(counts.values()), "which equals the entry count")
    print()
    print("the same three lines of code count anything you can name:")
    print("  counts[key] = counts.get(key, 0) + 1")
    print("Day 17 has collections.Counter, which does this in one call. Knowing")
    print("the loop first is what makes Counter obviously useful later, instead")
    print("of magic.")

    print()
    print("=" * 70)
    print("3. Ranking, with the tie rule written down")
    print("=" * 70)

    print("busiest_levels(LOG_TEXT, 2) ->", busiest_levels(LOG_TEXT, 2))
    print("busiest_levels(LOG_TEXT, 9) ->", busiest_levels(LOG_TEXT, 9))
    print("  asking for 9 of 3 things gives 3 things, not 9 and not an error")
    print("busiest_levels(LOG_TEXT, 0) ->", busiest_levels(LOG_TEXT, 0))
    print("busiest_levels(LOG_TEXT, -2) ->", busiest_levels(LOG_TEXT, -2))
    print("  a negative n is guarded, because pairs[:-2] would quietly drop two")
    print()
    print("ERROR and WARN both appear twice. The tie is broken alphabetically,")
    print("so the answer never depends on which happened to be logged first:")
    print("  by_count_then_level(('WARN', 2))  ->", by_count_then_level(("WARN", 2)))
    print("  by_count_then_level(('ERROR', 2)) ->", by_count_then_level(("ERROR", 2)))
    print("  (-2, 'ERROR') sorts before (-2, 'WARN'), so ERROR is listed first")

    print()
    print("=" * 70)
    print("4. Statistics, returned rather than printed")
    print("=" * 70)

    stats = log_stats(LOG_TEXT)
    for label, value in stats.items():
        print(f"   {label:<18}{value}")
    print()
    print("two messages tie on length at 28 characters:")
    print("   'retrying database connection'")
    print("   'database connection restored'")
    print("longest message ->", repr(stats["longest message"]))
    print("The earlier one wins, because the comparison is `>` and not `>=`.")
    print("That single character is the whole tie rule, and your project has the")
    print("same one for its longest word.")

    print()
    print("=" * 70)
    print("5. One report string, built from a list of lines")
    print("=" * 70)
    print()
    print(render_log_report(LOG_TEXT, 3))
    print()
    print("things worth noticing about that report:")
    print("  * every line is a label padded to 18 plus a value padded to 5, so")
    print("    the numbers line up without a single space typed by hand")
    print("  * the heading says how many rows FOLLOW, not how many were asked")
    print("    for — a report that overstates itself is not trusted twice")
    print("  * no line ends in a space, and the string does not end in a")
    print('    newline, because "\\n".join cannot add one')

    print()
    print("=" * 70)
    print("6. The edges: empty input, and no ranking wanted")
    print("=" * 70)
    print()
    print("render_log_report('', 3):")
    print(render_log_report("", 3))
    print()
    print("render_log_report(LOG_TEXT, 0) — stats only, no ranking section:")
    print(render_log_report(LOG_TEXT, 0))
    print()
    print("Empty input is not an error and does not need a traceback (Day 9) to")
    print("handle. It needs one `if` and a decision about what the right answer")
    print("is. Deciding that BEFORE you write the code is most of the skill.")

    print()
    print("=" * 70)
    print("Now build the text toolkit")
    print("=" * 70)
    print("Same six steps, different data:")
    print("  clean_text     normalise, like clean_field above")
    print("  word_counts    count into a dict, like level_counts")
    print("  top_words      rank with a named key function, like busiest_levels")
    print("  text_stats     compute numbers, like log_stats")
    print("  render_report  one aligned string, like render_log_report")
    print("  main           the only place that prints")
    print()
    print("Read LESSON.md, then work through exercises.py milestone by milestone:")
    print("  python check.py day07")


if __name__ == "__main__":
    main()
