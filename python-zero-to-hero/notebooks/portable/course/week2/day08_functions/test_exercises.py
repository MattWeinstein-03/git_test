"""Day 08 graded checks — Functions."""

import pytest


# --- Exercise 1: rectangle_area -------------------------------------------
def test_rectangle_area_whole_numbers(day):
    assert day.rectangle_area(3, 4) == 12.0


def test_rectangle_area_floats(day):
    assert day.rectangle_area(2.5, 2) == 5.0


def test_rectangle_area_zero_side(day):
    assert day.rectangle_area(0, 99) == 0.0


# --- Exercise 2: greet -----------------------------------------------------
def test_greet_uses_default_greeting(day):
    assert day.greet("Ada") == "Hello, Ada!"


def test_greet_accepts_custom_greeting_positionally(day):
    assert day.greet("Ada", "Yo") == "Yo, Ada!"


def test_greet_accepts_custom_greeting_by_keyword(day):
    assert day.greet("Ada", greeting="Hi") == "Hi, Ada!"


def test_greet_strips_whitespace(day):
    assert day.greet("  Grace  ") == "Hello, Grace!"


def test_greet_falls_back_to_stranger(day):
    assert day.greet("") == "Hello, stranger!"
    assert day.greet("   ", greeting="Hi") == "Hi, stranger!"


# --- Exercise 3: apply_discount -------------------------------------------
def test_apply_discount_default_is_ten_percent(day):
    assert day.apply_discount(100) == 90.0


def test_apply_discount_custom_percent(day):
    assert day.apply_discount(50, percent=50) == 25.0


def test_apply_discount_rounds_to_two_places(day):
    got = day.apply_discount(10.0, 33.0)
    assert got == 6.7, f"expected 6.7 (rounded to 2 places), got {got!r}"


def test_apply_discount_edges(day):
    assert day.apply_discount(19.99, 0) == 19.99
    assert day.apply_discount(19.99, 100) == 0.0


def test_apply_discount_rejects_out_of_range(day):
    with pytest.raises(ValueError):
        day.apply_discount(10.0, 150.0)
    with pytest.raises(ValueError):
        day.apply_discount(10.0, -1)


# --- Exercise 4: min_max_mean ---------------------------------------------
def test_min_max_mean_returns_three_values(day):
    got = day.min_max_mean([4, 9, 1, 7])
    assert got == (1, 9, 5.25), f"expected (1, 9, 5.25), got {got!r}"


def test_min_max_mean_single_value(day):
    assert day.min_max_mean([2.0]) == (2.0, 2.0, 2.0)


def test_min_max_mean_result_is_a_tuple(day):
    assert isinstance(day.min_max_mean([1, 2]), tuple)


def test_min_max_mean_empty_list(day):
    assert day.min_max_mean([]) == (0.0, 0.0, 0.0)


# --- Exercise 5: collect_unique -------------------------------------------
def test_collect_unique_starts_a_new_list(day):
    assert day.collect_unique("a") == ["a"]


def test_collect_unique_does_not_share_default_between_calls(day):
    day.collect_unique("a")
    got = day.collect_unique("b")
    assert got == ["b"], f"the mutable-default trap: expected ['b'], got {got!r}"


def test_collect_unique_appends_to_given_list(day):
    existing = ["a"]
    got = day.collect_unique("b", existing)
    assert got == ["a", "b"]
    assert got is existing, "should add to the list you were given, not a copy"


def test_collect_unique_skips_duplicates(day):
    assert day.collect_unique("a", ["a"]) == ["a"]


# --- Exercise 6: running_totals -------------------------------------------
def test_running_totals_basic(day):
    assert day.running_totals([1, 2, 3]) == [1, 3, 6]


def test_running_totals_handles_negatives(day):
    assert day.running_totals([2, -2, 4]) == [2, 0, 4]


def test_running_totals_empty(day):
    assert day.running_totals([]) == []


def test_running_totals_does_not_mutate_input(day):
    numbers = [1, 2, 3]
    day.running_totals(numbers)
    assert numbers == [1, 2, 3], "running_totals must be pure: leave the input alone"


# --- Exercise 7: summarize -------------------------------------------------
def test_summarize_three_numbers(day):
    assert day.summarize(1, 2, 3) == {
        "count": 3,
        "total": 6,
        "mean": 2.0,
        "spread": 2,
    }


def test_summarize_single_number(day):
    got = day.summarize(10)
    assert got["count"] == 1
    assert got["mean"] == 10.0
    assert got["spread"] == 0


def test_summarize_no_arguments(day):
    assert day.summarize() == {
        "count": 0,
        "total": 0.0,
        "mean": 0.0,
        "spread": 0.0,
    }


def test_summarize_rounds_the_mean(day):
    got = day.summarize(1, 2)["mean"]
    assert got == 1.5, f"expected 1.5, got {got!r}"
    assert day.summarize(1, 1, 2)["mean"] == 1.33


# --- Exercise 8: make_tag -------------------------------------------------
def test_make_tag_without_attributes(day):
    assert day.make_tag("br") == "<br>"


def test_make_tag_single_attribute(day):
    assert day.make_tag("a", href="/home") == '<a href="/home">'


def test_make_tag_sorts_attributes(day):
    got = day.make_tag("img", src="cat.png", alt="a cat")
    assert got == '<img alt="a cat" src="cat.png">', f"attributes must be sorted, got {got!r}"


def test_make_tag_drops_trailing_underscore(day):
    assert day.make_tag("p", class_="lead") == '<p class="lead">'


def test_make_tag_converts_underscores_to_dashes(day):
    assert day.make_tag("div", data_id="7") == '<div data-id="7">'


# --- Exercise 9: word_frequency -------------------------------------------
def test_word_frequency_counts_repeats(day):
    assert day.word_frequency("the cat the dog") == {"the": 2, "cat": 1, "dog": 1}


def test_word_frequency_is_case_insensitive_and_strips_punctuation(day):
    assert day.word_frequency("Hi, hi! HI?") == {"hi": 3}


def test_word_frequency_empty_text(day):
    assert day.word_frequency("") == {}


def test_word_frequency_ignores_punctuation_only_words(day):
    assert day.word_frequency("a ... a") == {"a": 2}


def test_word_frequency_keeps_inner_punctuation(day):
    got = day.word_frequency("don't stop, don't")
    assert got == {"don't": 2, "stop": 1}, f"only strip the ENDS of a word, got {got!r}"


# --- Exercise 10: format_receipt ------------------------------------------
EXPECTED_TWO_ITEMS = "\n".join(
    [
        "Widget        2 x    9.99 =    19.98",
        "Bolt         10 x    0.50 =     5.00",
        "------------------------------------",
        "SUBTOTAL                       24.98",
        "TAX 7.0%                        1.75",
        "TOTAL                          26.73",
    ]
)

EXPECTED_CUSTOM_RATE = "\n".join(
    [
        "Tea           1 x    3.00 =     3.00",
        "------------------------------------",
        "SUBTOTAL                        3.00",
        "TAX 20.0%                       0.60",
        "TOTAL                           3.60",
    ]
)


def test_format_receipt_empty(day):
    assert day.format_receipt([]) == "(no items)"


def test_format_receipt_two_items(day):
    got = day.format_receipt([("widget", 2, 9.99), ("bolt", 10, 0.5)])
    assert got == EXPECTED_TWO_ITEMS, (
        "receipt did not match the layout in the docstring.\n"
        f"got:\n{got}\n\nwant:\n{EXPECTED_TWO_ITEMS}"
    )


def test_format_receipt_custom_tax_rate(day):
    got = day.format_receipt([("tea", 1, 3.0)], tax_rate=0.2)
    assert got == EXPECTED_CUSTOM_RATE, f"got:\n{got}\n\nwant:\n{EXPECTED_CUSTOM_RATE}"


def test_format_receipt_lines_are_36_wide(day):
    receipt = day.format_receipt([("widget", 2, 9.99)])
    widths = set()
    for line in receipt.split("\n"):
        widths.add(len(line))
    assert widths == {36}, f"every line must be 36 characters wide, saw widths {widths}"


def test_format_receipt_has_no_trailing_newline(day):
    receipt = day.format_receipt([("tea", 1, 3.0)])
    assert not receipt.endswith("\n")
    assert len(receipt.split("\n")) == 5
