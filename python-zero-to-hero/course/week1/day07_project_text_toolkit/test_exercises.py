"""Day 07 graded checks — Project 1: the Text & Data Toolkit.

Tests are named test_m1_* … test_m5_* so partial credit is visible: finish
Milestone 1 and the M1 checks go green while the rest still fail. That is
working as intended, and `python check.py day07` shows you the count.

Nothing here reads or writes a file, and nothing here needs anything installed
beyond pytest. The `day` fixture (see conftest.py at the course root) hands your
`exercises.py` to every test as `day`.
"""


# The texts the checks are built on. Kept at the top so a failure message can be
# read against the input that produced it.
SENTENCES = "The cat sat. The cat ran! The end?"
PUNCTUATED = "Hello, HELLO... hello?! 'World' -- world; \"WORLD\"!"
TIED = "banana apple cherry apple banana cherry"


# ===========================================================================
# M1 — clean_text
# ===========================================================================
def test_m1_clean_text_trims_and_collapses_spaces(day):
    got = day.clean_text("  Hello   World  ")
    assert got == "hello world", f"got {got!r}"


def test_m1_clean_text_collapses_tabs_and_newlines_too(day):
    got = day.clean_text("Hello\tWORLD\n\nagain")
    assert got == "hello world again", (
        f"every run of whitespace becomes one space; got {got!r}"
    )


def test_m1_clean_text_casefolds(day):
    assert day.clean_text("The Cat SAT") == "the cat sat"


def test_m1_clean_text_leaves_punctuation_alone(day):
    got = day.clean_text("The Cat SAT.")
    assert got == "the cat sat.", f"M1 does not strip punctuation; got {got!r}"


def test_m1_clean_text_empty_and_whitespace_only(day):
    assert day.clean_text("") == ""
    got = day.clean_text("   \n\t ")
    assert got == "", f"whitespace-only text has nothing in it; got {got!r}"


def test_m1_clean_text_single_word(day):
    assert day.clean_text("  ONE\n") == "one"


# ===========================================================================
# M2 — word_counts
# ===========================================================================
def test_m2_word_counts_counts_repeats(day):
    got = day.word_counts("the cat sat on the mat")
    want = {"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_m2_word_counts_ignores_case_and_edge_punctuation(day):
    got = day.word_counts("Hello, HELLO... hello?!")
    assert got == {"hello": 3}, f"all three are the same word; got {got!r}"


def test_m2_word_counts_mixed_case_is_one_word(day):
    assert day.word_counts("Apple APPLE apple") == {"apple": 3}


def test_m2_word_counts_keeps_punctuation_inside_a_word(day):
    got = day.word_counts("well-known don't")
    want = {"well-known": 1, "don't": 1}
    assert got == want, f"only the EDGES are stripped; got {got!r}"


def test_m2_word_counts_drops_punctuation_only_pieces(day):
    got = day.word_counts("-- ... ! the")
    assert got == {"the": 1}, f"a piece that strips to '' is not a word; got {got!r}"


def test_m2_word_counts_punctuation_heavy_text(day):
    got = day.word_counts(PUNCTUATED)
    want = {"hello": 3, "world": 3}
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_m2_word_counts_empty_and_single_word(day):
    assert day.word_counts("") == {}
    assert day.word_counts("   ") == {}
    assert day.word_counts("Python.") == {"python": 1}


def test_m2_word_counts_keys_are_in_first_appearance_order(day):
    got = day.word_counts("cat mat cat bat")
    assert list(got) == ["cat", "mat", "bat"], (
        f"keys go in the order the words first appear; got {list(got)!r}"
    )


# ===========================================================================
# M3 — top_words
# ===========================================================================
def test_m3_top_words_orders_by_count(day):
    got = day.top_words("the cat sat on the mat", 2)
    want = [("the", 2), ("cat", 1)]
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_m3_top_words_breaks_ties_alphabetically(day):
    got = day.top_words(TIED, 3)
    want = [("apple", 2), ("banana", 2), ("cherry", 2)]
    assert got == want, f"equal counts sort A-Z; got {got!r}"


def test_m3_top_words_tie_break_beats_text_order(day):
    got = day.top_words(TIED, 2)
    assert got == [("apple", 2), ("banana", 2)], (
        f"'banana' appears first in the text but 'apple' still wins; got {got!r}"
    )


def test_m3_top_words_returns_pairs_of_word_and_count(day):
    got = day.top_words(SENTENCES, 3)
    want = [("the", 3), ("cat", 2), ("end", 1)]
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_m3_top_words_asking_for_too_many(day):
    got = day.top_words("the cat", 9)
    assert got == [("cat", 1), ("the", 1)], (
        f"return everything there is, with no padding; got {got!r}"
    )


def test_m3_top_words_zero_or_negative_is_empty(day):
    assert day.top_words("the cat", 0) == []
    got = day.top_words("the cat", -3)
    assert got == [], f"a negative n is not a slice from the end; got {got!r}"


def test_m3_top_words_empty_and_single_word_text(day):
    assert day.top_words("", 5) == []
    assert day.top_words("   ", 5) == []
    assert day.top_words("Python!", 5) == [("python", 1)]


def test_m3_top_words_punctuation_heavy_tie(day):
    got = day.top_words(PUNCTUATED, 1)
    assert got == [("hello", 3)], f"'hello' and 'world' tie on 3; got {got!r}"


# ===========================================================================
# M4 — text_stats
# ===========================================================================
def test_m4_text_stats_full_result(day):
    got = day.text_stats(SENTENCES)
    want = {
        "word_count": 8,
        "sentence_count": 3,
        "unique_words": 5,
        "average_word_length": 3.0,
        "longest_word": "the",
    }
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_m4_text_stats_keys_are_in_the_documented_order(day):
    got = day.text_stats(SENTENCES)
    want = [
        "word_count",
        "sentence_count",
        "unique_words",
        "average_word_length",
        "longest_word",
    ]
    assert list(got) == want, f"got {list(got)!r}\nwant {want!r}"


def test_m4_text_stats_single_word(day):
    got = day.text_stats("Python")
    want = {
        "word_count": 1,
        "sentence_count": 1,
        "unique_words": 1,
        "average_word_length": 6.0,
        "longest_word": "python",
    }
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_m4_text_stats_empty_text_is_all_zeros(day):
    want = {
        "word_count": 0,
        "sentence_count": 0,
        "unique_words": 0,
        "average_word_length": 0.0,
        "longest_word": "",
    }
    assert day.text_stats("") == want
    got = day.text_stats("   \n ")
    assert got == want, f"whitespace-only text has no words; got {got!r}"


def test_m4_text_stats_punctuation_only_text_has_no_sentences(day):
    got = day.text_stats("...")
    assert got["word_count"] == 0
    assert got["sentence_count"] == 0, (
        f"no words means no sentences, even with a full stop; got {got!r}"
    )


def test_m4_text_stats_counts_a_run_of_endings_once(day):
    got = day.text_stats("Really?! Wow...")
    assert got["sentence_count"] == 2, (
        f"'?!' is one ending and '...' is one ending; got {got!r}"
    )


def test_m4_text_stats_unpunctuated_text_is_one_sentence(day):
    got = day.text_stats("no terminator here")
    assert got["sentence_count"] == 1, f"got {got!r}"


def test_m4_text_stats_counts_every_ending_character(day):
    assert day.text_stats("One. Two. Three.")["sentence_count"] == 3
    assert day.text_stats("Why? Because! Yes.")["sentence_count"] == 3


def test_m4_text_stats_longest_word_ties_go_to_the_first(day):
    got = day.text_stats("cat bat mat")
    assert got["longest_word"] == "cat", (
        f"three words of length 3: the first one wins; got {got!r}"
    )


def test_m4_text_stats_longest_word_ignores_edge_punctuation(day):
    got = day.text_stats("hi, extraordinary!")
    assert got["longest_word"] == "extraordinary", f"got {got!r}"


def test_m4_text_stats_average_is_rounded_to_two_places(day):
    got = day.text_stats("no terminator here")
    assert got["average_word_length"] == 5.33, (
        f"(2 + 10 + 4) / 3 = 5.333...; got {got!r}"
    )


def test_m4_text_stats_agrees_with_word_counts(day):
    counts = day.word_counts(PUNCTUATED)
    stats = day.text_stats(PUNCTUATED)
    assert stats["word_count"] == sum(counts.values())
    assert stats["unique_words"] == len(counts)


# ===========================================================================
# M5 — render_report
# ===========================================================================
EXPECTED_SENTENCES_REPORT = "\n".join(
    [
        "TEXT REPORT",
        "===========",
        "words                8",
        "unique words         5",
        "sentences            3",
        "avg word length   3.00",
        "longest word       the",
        "",
        "top 3 words",
        "-----------",
        "the                  3",
        "cat                  2",
        "end                  1",
    ]
)

EXPECTED_PUNCTUATED_REPORT = "\n".join(
    [
        "TEXT REPORT",
        "===========",
        "words                6",
        "unique words         2",
        "sentences            3",
        "avg word length   5.00",
        "longest word     hello",
        "",
        "top 2 words",
        "-----------",
        "hello                3",
        "world                3",
    ]
)


def test_m5_render_report_exact_layout(day):
    got = day.render_report(SENTENCES, 3)
    assert got == EXPECTED_SENTENCES_REPORT, (
        f"got:\n{got}\n\nwant:\n{EXPECTED_SENTENCES_REPORT}"
    )


def test_m5_render_report_heading_counts_the_rows_shown(day):
    got = day.render_report(PUNCTUATED, 5)
    assert got == EXPECTED_PUNCTUATED_REPORT, (
        f"asked for 5, only 2 words exist, so the heading says 2\n"
        f"got:\n{got}\n\nwant:\n{EXPECTED_PUNCTUATED_REPORT}"
    )


def test_m5_render_report_stat_lines_are_22_characters(day):
    lines = day.render_report(SENTENCES, 3).split("\n")
    for index in (2, 3, 4, 5, 6):
        assert len(lines[index]) == 22, (
            f"line {index + 1} should be 16 + 6 characters wide, "
            f"got {len(lines[index])}: {lines[index]!r}"
        )


def test_m5_render_report_without_a_ranking_section(day):
    got = day.render_report(SENTENCES, 0)
    lines = got.split("\n")
    assert len(lines) == 7, (
        f"top_n of 0 stops after the stats — no blank line, no heading; "
        f"got {len(lines)} lines:\n{got}"
    )
    assert lines[6] == "longest word       the", f"got {lines[6]!r}"


def test_m5_render_report_negative_top_n_also_has_no_ranking(day):
    assert len(day.render_report(SENTENCES, -1).split("\n")) == 7


def test_m5_render_report_empty_text(day):
    want = "TEXT REPORT\n===========\n(no words found)"
    got = day.render_report("", 3)
    assert got == want, f"got:\n{got}\n\nwant:\n{want}"
    assert day.render_report("   \n\t", 5) == want


def test_m5_render_report_single_word_text(day):
    got = day.render_report("Python!", 3)
    want = "\n".join(
        [
            "TEXT REPORT",
            "===========",
            "words                1",
            "unique words         1",
            "sentences            1",
            "avg word length   6.00",
            "longest word    python",
            "",
            "top 1 words",
            "-----------",
            "python               1",
        ]
    )
    assert got == want, f"got:\n{got}\n\nwant:\n{want}"


def test_m5_render_report_has_no_trailing_newline(day):
    got = day.render_report(SENTENCES, 3)
    assert not got.endswith("\n"), "join the lines, do not append a newline"


def test_m5_render_report_has_no_trailing_whitespace_on_any_line(day):
    for line in day.render_report(SENTENCES, 3).split("\n"):
        assert line == line.rstrip(), f"trailing whitespace on {line!r}"


def test_m5_render_report_does_not_truncate_a_long_word(day):
    lines = day.render_report("internationalisation internationalisation short", 2)
    lines = lines.split("\n")
    assert "longest word    internationalisation" in lines, (
        f"a width is a minimum, not a maximum; got:\n{lines!r}"
    )
    assert "internationalisation     2" in lines, f"got:\n{lines!r}"


def test_m5_render_report_row_count_matches_top_n(day):
    lines = day.render_report(SENTENCES, 2).split("\n")
    assert lines[8] == "top 2 words", f"got {lines[8]!r}"
    assert len(lines) == 12, (
        f"7 stat lines + blank + heading + underline + 2 rows; "
        f"got {len(lines)} lines"
    )


# ===========================================================================
# main() — the demonstration
# ===========================================================================
def test_main_prints_a_report_for_the_sample_text(day, capsys):
    day.main()
    printed = capsys.readouterr().out
    assert "TEXT REPORT" in printed, f"got:\n{printed}"
    assert "top 5 words" in printed, f"main() shows a top-5 ranking; got:\n{printed}"


def test_main_returns_nothing_and_reads_nothing(day, capsys):
    result = day.main()
    capsys.readouterr()
    assert result is None, f"main() prints; it does not return a value. Got {result!r}"
