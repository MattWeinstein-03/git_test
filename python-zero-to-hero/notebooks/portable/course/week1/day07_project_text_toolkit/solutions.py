"""Day 07 solutions — Project 1: the Text & Data Toolkit.

The reference implementation. Same names, same signatures, same docstrings as
exercises.py, fully working. Read it *after* your own attempt, and pay attention
to the places where you made a different decision — the interesting question is
never "did I match this file", it is "why did I choose differently".

Days 1-6 tools only. No later-day shortcuts: this file could have been written
on the evening of Day 06.

Run it to see the finished toolkit:

    python course/week1/day07_project_text_toolkit/solutions.py
"""


SAMPLE_TEXT = """
The Text toolkit counts words. It counts words, and it counts sentences,
and it reports what it found.

    A toolkit is a small program you keep;   a script is a small program
you throw away. This one is a toolkit: the report it prints is the same
report every time, and the numbers in it can be checked.

Words in, numbers out. That is the whole job!
"""

PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

SENTENCE_ENDINGS = ".!?"

TITLE = "TEXT REPORT"


def strip_punctuation(word: str) -> str:
    """Return `word` with punctuation removed from both ends only.

    `str.strip(chars)` removes any character in `chars` from each end of the
    string, and keeps chewing until it meets a character that is not in the
    set. It never touches the middle, which is why "don't" survives intact
    and "hello!!!" does not.

    Args:
        word: one whitespace-separated piece of text.

    Returns:
        The word with edge punctuation gone. Possibly the empty string.

    Examples:
        strip_punctuation("Hello,") -> "Hello"
        strip_punctuation("...hello?!") -> "hello"
        strip_punctuation("don't") -> "don't"
        strip_punctuation("well-known") -> "well-known"
        strip_punctuation("--") -> ""
    """
    return word.strip(PUNCTUATION)


# ---------------------------------------------------------------------------
# Helpers of my own. Not graded, not required — but the milestones share work,
# and sharing it once beats copying it four times.
# ---------------------------------------------------------------------------
def words_of(text: str) -> list[str]:
    """The words of `text`, in order: cleaned, trimmed, empties dropped.

    This is milestone 2's steps 1-4 with the counting left off, which is
    exactly what milestones 2 and 4 both need.

    Examples:
        words_of("Hello, HELLO... --") -> ["hello", "hello"]
    """
    words: list[str] = []
    for piece in clean_text(text).split():
        word = strip_punctuation(piece)
        # why: a piece that was nothing but punctuation is now "", and "" is
        # falsy (Day 3), so this one `if` drops "--" and "..." without naming
        # them.
        if word:
            words.append(word)
    return words


def count_sentence_endings(text: str) -> int:
    """How many runs of ".", "!" or "?" appear in `text`.

    A run counts once: "Really?!" is one, "Wait..." is one.

    Examples:
        count_sentence_endings("Hi. Bye.") -> 2
        count_sentence_endings("Really?! Wow...") -> 2
        count_sentence_endings("no ending") -> 0
    """
    endings = 0
    # why: " " is the starting "previous character", and it is deliberately not
    # the empty string. `"" in ".!?"` is True — the empty string counts as a
    # substring of everything — which would make the first character of the
    # text never count. A real character avoids the trap entirely.
    previous = " "
    for character in text:
        if character in SENTENCE_ENDINGS and previous not in SENTENCE_ENDINGS:
            endings += 1
        previous = character
    return endings


def by_count_then_word(pair: tuple[str, int]) -> tuple[int, str]:
    """Sort key for (word, count) pairs: biggest count first, then A-Z.

    `sort` only ever sorts smallest-first, so negating the count is how you
    reverse one column while leaving the other one alone. `reverse=True` would
    flip the alphabet too, which is not what the brief asks for.

    Examples:
        by_count_then_word(("the", 3)) -> (-3, "the")
    """
    word, count = pair
    return (-count, word)


# ===========================================================================
# MILESTONE 1 — clean_text
# ===========================================================================
def clean_text(text: str) -> str:
    """Return `text` normalised: trimmed, casefolded, single-spaced.

    Three normalisations, in any order you like — they do not interfere:
      1. whitespace at the very start and the very end disappears;
      2. every run of internal whitespace — spaces, tabs, newlines, or any
         mixture — becomes exactly one space;
      3. the text is casefolded, so "HELLO", "Hello" and "hello" all come out
         as "hello".

    Punctuation is *not* touched here. "Hello," stays "hello," — trimming
    punctuation is Milestone 2's job.

    Casefolding is `str.casefold()`, not `str.lower()`. For English text they
    agree; casefold is the aggressive version built for comparing text, and it
    also folds cases that `lower()` leaves alone (German "STRASSE" and "Straße"
    both casefold to "strasse").

    Args:
        text: any text, however badly spaced.

    Returns:
        The normalised text. The empty string if `text` had no non-whitespace
        characters at all.

    Examples:
        clean_text("  Hello   World  ") -> "hello world"
        clean_text("Hello\\tWORLD\\n\\nagain") -> "hello world again"
        clean_text("The Cat SAT.") -> "the cat sat."
        clean_text("") -> ""
        clean_text("   \\n\\t ") -> ""
        clean_text("one") -> "one"
    """
    # why: split() with no argument breaks on every run of any whitespace and
    # discards the runs at both ends, so trimming and collapsing are one step
    # (Day 02, section 8.3). Joining with a single space puts exactly one back.
    return " ".join(text.split()).casefold()


# ===========================================================================
# MILESTONE 2 — word_counts
# ===========================================================================
def word_counts(text: str) -> dict[str, int]:
    """Return a dict mapping each word in `text` to how often it appears.

    The pipeline, in order:
      1. normalise `text` with clean_text, so case and spacing stop mattering;
      2. split it into whitespace-separated pieces;
      3. strip punctuation from both ends of each piece with
         strip_punctuation;
      4. throw away any piece that is now empty — a lone "--" or "..." is not
         a word;
      5. count what is left.

    Key order: first appearance in the text. Dicts remember the order you
    inserted keys in (Day 6), and the counting loop inserts each new word the
    first time it meets it, so you get this for free — as long as you build the
    dict by walking the words in order.

    Args:
        text: any text.

    Returns:
        {word: count}, keys in first-appearance order. An empty dict when
        `text` holds no words.

    Examples:
        word_counts("the cat sat on the mat")
            -> {"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}
        word_counts("Hello, HELLO... hello?!") -> {"hello": 3}
        word_counts("Apple APPLE apple") -> {"apple": 3}
        word_counts("well-known don't") -> {"well-known": 1, "don't": 1}
        word_counts("-- ... !") -> {}
        word_counts("") -> {}
    """
    counts: dict[str, int] = {}
    for word in words_of(text):
        # why: .get(word, 0) is the Day 6 counting pattern. counts[word] + 1
        # would raise KeyError the first time each word appears, and an `if
        # word in counts` check is two lines doing one line's work.
        counts[word] = counts.get(word, 0) + 1
    return counts


# ===========================================================================
# MILESTONE 3 — top_words
# ===========================================================================
def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """Return the `n` most frequent words in `text` as (word, count) pairs.

    Build on Milestone 2: count first, then rank.

    Ordering rules, applied in this order:
      1. higher count first;
      2. words with the same count are ordered alphabetically (so the answer
         never depends on where they happened to appear in the text).

    Size rules:
      * `n` of 0 or less returns an empty list;
      * asking for more words than exist returns every word, no padding.

    Sort with a named `def` helper passed as `key=`, returning the tuple
    `(-count, word)`. Negating the count turns "biggest first" into "smallest
    first", which is the only direction `sort` has. See LESSON.md, M3.

    Args:
        text: any text.
        n: how many pairs you want at most.

    Returns:
        A list of (word, count) tuples, longest-first then alphabetical.

    Examples:
        top_words("the cat sat on the mat", 2) -> [("the", 2), ("cat", 1)]
        top_words("banana apple cherry apple banana cherry", 2)
            -> [("apple", 2), ("banana", 2)]
        top_words("the cat", 9) -> [("cat", 1), ("the", 1)]
        top_words("the cat", 0) -> []
        top_words("the cat", -3) -> []
        top_words("", 5) -> []
    """
    # why: guard first. Without this, n = 0 would slice [:0] correctly by luck
    # but n = -1 would slice [:-1] and silently drop the last pair.
    if n <= 0:
        return []
    pairs = list(word_counts(text).items())
    pairs.sort(key=by_count_then_word)
    # why: slicing past the end is not an error in Python — [:9] on a 2-item
    # list gives 2 items — so "more than exist" needs no special case.
    return pairs[:n]


# ===========================================================================
# MILESTONE 4 — text_stats
# ===========================================================================
def text_stats(text: str) -> dict[str, object]:
    """Return five statistics about `text` in one dict.

    The keys, in this exact insertion order:

        "word_count"          int    how many words, counting repeats
        "sentence_count"      int    how many sentences (definition below)
        "unique_words"        int    how many different words
        "average_word_length" float  mean word length, rounded to 2 decimals
        "longest_word"        str    the longest word

    "Word" means exactly what Milestone 2 means by it: casefolded, edge
    punctuation removed, empties discarded. So `word_count` is the total of
    `word_counts(text).values()`, and `unique_words` is how many keys that dict
    has. Reuse the milestone you already finished.

    Sentence counting — the precise rule, no guessing:
      * a sentence ends at one of ".", "!" or "?" (SENTENCE_ENDINGS);
      * a *run* of those characters counts once, so "Really?!" is one sentence
        and "Wait..." is one sentence;
      * if the text contains at least one word but no ending character at all,
        the count is 1 — an unpunctuated line is still one sentence;
      * if the text contains no words, every count is 0, including this one.
        "..." is not a sentence, because there is nothing in it to say.

      Walk the characters of the text and count each ending character whose
      previous character is not also an ending character. That is the whole
      algorithm. It counts "e.g." as two sentences, and abbreviations like
      that are the reason real sentence splitting needs `re` (Day 17). Today's
      definition is the one the tests use.

    Average word length: add up the lengths of the words (after punctuation
    stripping, counting repeats) and divide by `word_count`. Round the answer
    once, at the end, with `round(value, 2)`.

    Longest word: the word with the most characters. Ties go to the one that
    appears **first** in the text, so compare with a strict `>` while walking
    the words in order — `>=` would keep overwriting your answer with later
    ties.

    Empty text: every number is 0, the average is 0.0, and the longest word is
    "". Nothing raises. Dividing by `word_count` when it is 0 would raise
    ZeroDivisionError, so guard it with an `if` (Day 3).

    Args:
        text: any text.

    Returns:
        The five statistics, keyed as above.

    Examples:
        text_stats("The cat sat. The cat ran! The end?") ->
            {"word_count": 8, "sentence_count": 3, "unique_words": 5,
             "average_word_length": 3.0, "longest_word": "the"}

        text_stats("Python") ->
            {"word_count": 1, "sentence_count": 1, "unique_words": 1,
             "average_word_length": 6.0, "longest_word": "python"}

        text_stats("") ->
            {"word_count": 0, "sentence_count": 0, "unique_words": 0,
             "average_word_length": 0.0, "longest_word": ""}
    """
    words = words_of(text)
    word_count = len(words)

    total_length = 0
    longest_word = ""
    for word in words:
        total_length += len(word)
        # why: strictly greater than, so the FIRST word of a tied length wins
        # and later ties leave it alone.
        if len(word) > len(longest_word):
            longest_word = word

    average_word_length = 0.0
    sentence_count = 0
    if word_count > 0:
        # why: guarded, because word_count of 0 would be ZeroDivisionError,
        # and "no words" has to answer 0.0 rather than crash.
        average_word_length = round(total_length / word_count, 2)
        sentence_count = count_sentence_endings(text)
        # why: text with words but no ".", "!" or "?" is still one sentence.
        if sentence_count == 0:
            sentence_count = 1

    # why: insertion order is the documented order, and dicts keep it (Day 6),
    # so render_report can rely on reading them in this sequence.
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "unique_words": len(word_counts(text)),
        "average_word_length": average_word_length,
        "longest_word": longest_word,
    }


# ===========================================================================
# MILESTONE 5 — render_report
# ===========================================================================
def render_report(text: str, top_n: int) -> str:
    """Return a formatted, multi-line report about `text`.

    The report is a *string*. It does not print anything — main() prints. That
    separation is what makes the layout testable with one assertion.

    Layout when `text` contains words and `top_n` is 1 or more. Every column is
    produced by an f-string format spec: labels left-justified in 16
    characters, values right-justified in 6, so each of those lines is 22
    characters wide.

        line 1   "TEXT REPORT"
        line 2   eleven "=" characters, matching the title's length
        line 3   f"{'words':<16}{word_count:>6}"
        line 4   f"{'unique words':<16}{unique_words:>6}"
        line 5   f"{'sentences':<16}{sentence_count:>6}"
        line 6   f"{'avg word length':<16}{average_word_length:>6.2f}"
        line 7   f"{'longest word':<16}{longest_word:>6}"
        line 8   "" — one completely empty line
        line 9   f"top {shown} words", where `shown` is how many rows follow,
                 NOT what was asked for
        line 10  as many "-" characters as line 9 has characters
        line 11+ one row per word, f"{word:<16}{count:>6}"

    Variations:
      * `top_n` of 0 or less: stop after line 7. No blank line, no heading, no
        rows.
      * `text` with no words: the whole report is three lines — the title, the
        "=" underline, and "(no words found)". `top_n` is ignored.
      * A word longer than 16 characters is not truncated: a width is a
        minimum, not a maximum, so that row is simply wider than 22.

    Formatting rules the tests enforce:
      * no line has trailing whitespace (the empty line 8 is empty, not spaces);
      * the string does not end with a newline;
      * lines are joined with "\\n" — build a list of lines and use
        "\\n".join(lines).

    Args:
        text: any text.
        top_n: how many words to list in the ranking section.

    Returns:
        The report as one string.

    Examples:
        render_report("The cat sat. The cat ran! The end?", 3) ->
            "TEXT REPORT\\n"
            "===========\\n"
            "words                8\\n"
            "unique words         5\\n"
            "sentences            3\\n"
            "avg word length   3.00\\n"
            "longest word       the\\n"
            "\\n"
            "top 3 words\\n"
            "-----------\\n"
            "the                  3\\n"
            "cat                  2\\n"
            "end                  1"

        render_report("", 3) ->
            "TEXT REPORT\\n===========\\n(no words found)"
    """
    stats = text_stats(text)
    # why: a list of lines, joined at the very end. Building one long string
    # with += makes the trailing-newline rule easy to get wrong, and hides the
    # shape of the output from anyone reading the code.
    lines = [TITLE, "=" * len(TITLE)]

    if stats["word_count"] == 0:
        lines.append("(no words found)")
        return "\n".join(lines)

    # why: pulling the values out into names keeps each f-string readable, and
    # names what each column means.
    word_count = stats["word_count"]
    unique_words = stats["unique_words"]
    sentence_count = stats["sentence_count"]
    average_word_length = stats["average_word_length"]
    longest_word = stats["longest_word"]

    # why: 16 and 6 are the widths the brief specifies. Left-justify the label,
    # right-justify the number, and the decimal points line up by themselves.
    lines.append(f"{'words':<16}{word_count:>6}")
    lines.append(f"{'unique words':<16}{unique_words:>6}")
    lines.append(f"{'sentences':<16}{sentence_count:>6}")
    lines.append(f"{'avg word length':<16}{average_word_length:>6.2f}")
    lines.append(f"{'longest word':<16}{longest_word:>6}")

    if top_n > 0:
        pairs = top_words(text, top_n)
        # why: the heading reports how many rows actually follow. Asking for
        # five words in a three-word document and printing "top 5 words" over
        # three rows would be a small lie, and reports that lie do not get
        # trusted twice.
        heading = f"top {len(pairs)} words"
        lines.append("")
        lines.append(heading)
        lines.append("-" * len(heading))
        for word, count in pairs:
            lines.append(f"{word:<16}{count:>6}")

    return "\n".join(lines)


# ===========================================================================
# The demonstration entry point — the only place that prints
# ===========================================================================
def main() -> None:
    """Print a report for SAMPLE_TEXT. Returns nothing; printing is the point.

    Requirements:
      * print the report for SAMPLE_TEXT with a top-5 ranking;
      * print nothing else that would confuse a reader — a title line above the
        report is welcome, banner art is not;
      * read no input, write no files, and take no arguments, so it is safe to
        run from anywhere.

    Examples:
        main() -> prints a report containing "TEXT REPORT" and "top 5 words"
    """
    # why: main() is the only function here that prints. Everything else
    # returns a value, which is why everything else is testable.
    print("Text & Data Toolkit — sample text")
    print()
    print(render_report(SAMPLE_TEXT, 5))


if __name__ == "__main__":
    main()
