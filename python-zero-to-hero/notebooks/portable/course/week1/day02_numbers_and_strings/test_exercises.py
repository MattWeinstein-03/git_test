"""Day 02 graded checks — Numbers and Strings."""


# --- Exercise 1: initials -------------------------------------------------
def test_initials_basic(day):
    assert day.initials("Ada", "Lovelace") == "A.L."


def test_initials_upper_cases_lowercase_input(day):
    assert day.initials("grace", "hopper") == "G.H."


def test_initials_single_letter_names(day):
    assert day.initials("k", "j") == "K.J."


# --- Exercise 2: clean_name -----------------------------------------------
def test_clean_name_strips_and_titles(day):
    assert day.clean_name("  ada LOVELACE  ") == "Ada Lovelace"


def test_clean_name_fixes_shouting(day):
    assert day.clean_name("GRACE HOPPER") == "Grace Hopper"


def test_clean_name_removes_a_trailing_newline(day):
    assert day.clean_name("alan\n") == "Alan"


def test_clean_name_whitespace_only_becomes_empty(day):
    got = day.clean_name("   ")
    assert got == "", f"expected an empty string, got {got!r}"


# --- Exercise 3: price_with_tax -------------------------------------------
def test_price_with_tax_twenty_percent(day):
    assert day.price_with_tax(100.0, 0.2) == 120.0


def test_price_with_tax_rounds_to_two_places(day):
    got = day.price_with_tax(19.99, 0.2)
    assert got == 23.99, f"expected 23.99 (19.99 * 1.2 = 23.988), got {got!r}"


def test_price_with_tax_zero_rate_changes_nothing(day):
    assert day.price_with_tax(9.99, 0.0) == 9.99


def test_price_with_tax_awkward_rate(day):
    assert day.price_with_tax(1.0, 0.175) == 1.18


# --- Exercise 4: seconds_to_clock -----------------------------------------
def test_seconds_to_clock_zero(day):
    got = day.seconds_to_clock(0)
    assert got == "00:00:00", f"every part is zero-padded to 2 digits, got {got!r}"


def test_seconds_to_clock_under_a_minute(day):
    assert day.seconds_to_clock(59) == "00:00:59"


def test_seconds_to_clock_exactly_a_minute(day):
    assert day.seconds_to_clock(60) == "00:01:00"


def test_seconds_to_clock_mixed(day):
    got = day.seconds_to_clock(4000)
    assert got == "01:06:40", f"4000s is 1h 6m 40s, got {got!r}"


def test_seconds_to_clock_end_of_day(day):
    assert day.seconds_to_clock(86399) == "23:59:59"


def test_seconds_to_clock_over_a_hundred_hours(day):
    assert day.seconds_to_clock(360000) == "100:00:00"


# --- Exercise 5: mask_card ------------------------------------------------
def test_mask_card_full_number(day):
    got = day.mask_card("4111111111111234")
    assert got == "************1234", f"got {got!r}"


def test_mask_card_keeps_the_length(day):
    number = "4111111111111234"
    assert len(day.mask_card(number)) == len(number)


def test_mask_card_five_digits(day):
    assert day.mask_card("12345") == "*2345"


def test_mask_card_exactly_four_digits_is_unchanged(day):
    assert day.mask_card("1234") == "1234"


# --- Exercise 6: slugify --------------------------------------------------
def test_slugify_two_words(day):
    assert day.slugify("Hello World") == "hello-world"


def test_slugify_collapses_runs_of_spaces(day):
    got = day.slugify("  Python   Zero to Hero  ")
    assert got == "python-zero-to-hero", f"one hyphen per gap, got {got!r}"


def test_slugify_single_word(day):
    assert day.slugify("ONE") == "one"


def test_slugify_whitespace_only(day):
    assert day.slugify("   ") == ""


def test_slugify_handles_tabs_and_newlines(day):
    assert day.slugify("tabs\tand\nnewlines") == "tabs-and-newlines"


# --- Exercise 7: format_money ---------------------------------------------
def test_format_money_thousands_and_decimals(day):
    got = day.format_money(1234.5)
    assert got == "£1,234.50", f"got {got!r}"


def test_format_money_zero(day):
    assert day.format_money(0) == "£0.00"


def test_format_money_rounds_up(day):
    assert day.format_money(9.999) == "£10.00"


def test_format_money_millions(day):
    assert day.format_money(1000000) == "£1,000,000.00"


def test_format_money_negative(day):
    assert day.format_money(-5.5) == "£-5.50"


# --- Exercise 8: debug_line -----------------------------------------------
def test_debug_line_int(day):
    got = day.debug_line(42)
    assert got == "total=42", f"expected the parameter name in the output, got {got!r}"


def test_debug_line_float(day):
    assert day.debug_line(3.5) == "total=3.5"


def test_debug_line_uses_repr_for_strings(day):
    got = day.debug_line("hi")
    assert got == "total='hi'", f"the = specifier uses repr(), so quotes stay: got {got!r}"


def test_debug_line_none(day):
    assert day.debug_line(None) == "total=None"


# --- Exercise 9: table_row ------------------------------------------------
def test_table_row_widget(day):
    got = day.table_row("widget", 2, 9.99)
    want = "widget          2      9.99"
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_table_row_pads_the_price_to_two_decimals(day):
    got = day.table_row("bolt", 10, 0.5)
    want = "bolt           10      0.50"
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_table_row_whole_pounds(day):
    got = day.table_row("gizmo", 1, 24.0)
    want = "gizmo           1     24.00"
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_table_row_is_27_characters_wide(day):
    assert len(day.table_row("tea", 3, 1.0)) == 27


def test_table_row_does_not_truncate_long_names(day):
    got = day.table_row("extraordinarily-long", 1, 1.0)
    assert got.startswith("extraordinarily-long"), f"width is a minimum, got {got!r}"


# --- Exercise 10: text_summary --------------------------------------------
EXPECTED_SENTENCE = "\n".join(
    [
        "Summary",
        "-------",
        "characters        22",
        "words              6",
        "avg word len    2.83",
    ]
)

EXPECTED_ONE_WORD = "\n".join(
    [
        "Summary",
        "-------",
        "characters         5",
        "words              1",
        "avg word len    5.00",
    ]
)


def test_text_summary_sentence(day):
    got = day.text_summary("the cat sat on the mat")
    assert got == EXPECTED_SENTENCE, f"got:\n{got}\n\nwant:\n{EXPECTED_SENTENCE}"


def test_text_summary_single_word(day):
    got = day.text_summary("hello")
    assert got == EXPECTED_ONE_WORD, f"got:\n{got}\n\nwant:\n{EXPECTED_ONE_WORD}"


def test_text_summary_counts_raw_characters_including_spaces(day):
    got = day.text_summary("  a  b  ")
    lines = got.split("\n")
    assert lines[2] == f"{'characters':<14}{8:>6}", f"got {lines[2]!r}"
    assert lines[3] == f"{'words':<14}{2:>6}", f"got {lines[3]!r}"
    assert lines[4] == f"{'avg word len':<14}{1.0:>6.2f}", f"got {lines[4]!r}"


def test_text_summary_has_five_lines_and_no_trailing_newline(day):
    got = day.text_summary("one two three")
    assert len(got.split("\n")) == 5
    assert not got.endswith("\n")
