"""Day 03 graded checks — Conditionals."""


# --- Exercise 1: is_freezing ----------------------------------------------
def test_is_freezing_below_zero(day):
    assert day.is_freezing(-4.0) is True


def test_is_freezing_zero_counts_as_freezing(day):
    got = day.is_freezing(0)
    assert got is True, f"0 is at freezing point, so expected True, got {got!r}"


def test_is_freezing_just_above_zero(day):
    assert day.is_freezing(0.5) is False


def test_is_freezing_room_temperature(day):
    assert day.is_freezing(21.0) is False


# --- Exercise 2: sign_word -------------------------------------------------
def test_sign_word_negative(day):
    assert day.sign_word(-3) == "negative"


def test_sign_word_zero(day):
    assert day.sign_word(0) == "zero"


def test_sign_word_float_zero(day):
    got = day.sign_word(0.0)
    assert got == "zero", f"0.0 == 0, so this is still the zero branch, got {got!r}"


def test_sign_word_positive(day):
    assert day.sign_word(7.5) == "positive"


# --- Exercise 3: is_valid_percentage --------------------------------------
def test_is_valid_percentage_lower_bound_is_inclusive(day):
    assert day.is_valid_percentage(0) is True


def test_is_valid_percentage_upper_bound_is_inclusive(day):
    got = day.is_valid_percentage(100)
    assert got is True, f"100 is a valid percentage, got {got!r}"


def test_is_valid_percentage_middle(day):
    assert day.is_valid_percentage(55.5) is True


def test_is_valid_percentage_just_over(day):
    assert day.is_valid_percentage(100.01) is False


def test_is_valid_percentage_negative(day):
    assert day.is_valid_percentage(-0.5) is False


# --- Exercise 4: can_ride -------------------------------------------------
def test_can_ride_tall_and_old_enough(day):
    assert day.can_ride(150, 30, False) is True


def test_can_ride_young_but_accompanied(day):
    assert day.can_ride(150, 8, True) is True


def test_can_ride_young_and_alone_is_refused(day):
    assert day.can_ride(150, 8, False) is False


def test_can_ride_too_short_even_with_an_adult(day):
    got = day.can_ride(90, 8, True)
    assert got is False, (
        "the height rule applies to everyone — if this returned True, the "
        f"`or` needs brackets (section 3.1). Got {got!r}"
    )


def test_can_ride_both_limits_are_inclusive(day):
    assert day.can_ride(120, 12, False) is True


# --- Exercise 5: starts_with_vowel ----------------------------------------
def test_starts_with_vowel_lowercase(day):
    assert day.starts_with_vowel("apple") is True


def test_starts_with_vowel_ignores_case(day):
    assert day.starts_with_vowel("Igloo") is True


def test_starts_with_vowel_consonant(day):
    assert day.starts_with_vowel("banana") is False


def test_starts_with_vowel_empty_string_does_not_crash(day):
    got = day.starts_with_vowel("")
    assert got is False, (
        "an empty word starts with nothing, so expected False. If this raised "
        "IndexError, put the length test first and join it with `and`. If it "
        f"returned '', return a real bool rather than `word and ...`. Got {got!r}"
    )


def test_starts_with_vowel_single_letter(day):
    assert day.starts_with_vowel("E") is True


# --- Exercise 6: describe_stock -------------------------------------------
def test_describe_stock_none_is_unknown(day):
    got = day.describe_stock(None)
    assert got == "unknown", f"None means nobody counted yet, got {got!r}"


def test_describe_stock_zero_is_out_of_stock(day):
    got = day.describe_stock(0)
    assert got == "out of stock", (
        "0 and None are both falsy, so truthiness alone cannot tell them "
        f"apart — test `is None` first. Got {got!r}"
    )


def test_describe_stock_positive_is_in_stock(day):
    assert day.describe_stock(12) == "in stock"


def test_describe_stock_one_is_in_stock(day):
    assert day.describe_stock(1) == "in stock"


def test_describe_stock_negative_is_invalid(day):
    assert day.describe_stock(-3) == "invalid"


# --- Exercise 7: pluralise ------------------------------------------------
def test_pluralise_one_is_singular(day):
    assert day.pluralise(1, "item") == "1 item"


def test_pluralise_zero_is_plural(day):
    got = day.pluralise(0, "item")
    assert got == "0 items", f"English pluralises zero, got {got!r}"


def test_pluralise_many(day):
    assert day.pluralise(3, "file") == "3 files"


def test_pluralise_negative_is_plural(day):
    got = day.pluralise(-1, "dog")
    assert got == "-1 dogs", f"use `count != 1`, not `count > 1`, got {got!r}"


# --- Exercise 8: letter_grade ---------------------------------------------
def test_letter_grade_top_band(day):
    assert day.letter_grade(95) == "A"


def test_letter_grade_band_boundaries_are_inclusive(day):
    assert day.letter_grade(90) == "A"
    assert day.letter_grade(80) == "B"
    assert day.letter_grade(70) == "C"
    assert day.letter_grade(60) == "D"


def test_letter_grade_just_below_a_boundary(day):
    got = day.letter_grade(89)
    assert got == "B", (
        "89 belongs to the 80s band. If this returned 'A', your chain is "
        f"ordered lowest-first. Got {got!r}"
    )


def test_letter_grade_failing(day):
    assert day.letter_grade(0) == "F"
    assert day.letter_grade(59) == "F"


def test_letter_grade_rejects_out_of_range_scores(day):
    assert day.letter_grade(101) == "invalid"
    assert day.letter_grade(-1) == "invalid"


# --- Exercise 9: fizz_label -----------------------------------------------
def test_fizz_label_plain_number_comes_back_as_text(day):
    got = day.fizz_label(1)
    assert got == "1", f"the fallback branch returns str(number), got {got!r}"


def test_fizz_label_divisible_by_three(day):
    assert day.fizz_label(3) == "Fizz"
    assert day.fizz_label(9) == "Fizz"


def test_fizz_label_divisible_by_five(day):
    assert day.fizz_label(5) == "Buzz"
    assert day.fizz_label(20) == "Buzz"


def test_fizz_label_divisible_by_both(day):
    got = day.fizz_label(15)
    assert got == "FizzBuzz", (
        "15 is divisible by 3 and by 5, and the 'both' branch has to be "
        f"tested first or it can never run. Got {got!r}"
    )


def test_fizz_label_zero_and_negatives(day):
    assert day.fizz_label(0) == "FizzBuzz"
    assert day.fizz_label(-9) == "Fizz"
    assert day.fizz_label(-7) == "-7"


# --- Exercise 10: ticket_price -------------------------------------------
def _close(got: float, want: float) -> bool:
    """Floats are approximate (Day 2, section 3), so compare with a tolerance."""
    return abs(got - want) < 1e-9


def test_ticket_price_weekend_surcharge(day):
    got = day.ticket_price(30, False, True)
    assert _close(got, 14.0), f"12 + 2 weekend surcharge = 14.0, got {got!r}"


def test_ticket_price_surcharge_then_member_discount(day):
    got = day.ticket_price(30, True, True)
    assert _close(got, 12.6), (
        "the surcharge is applied before the discount: (12 + 2) * 0.9 = 12.6. "
        f"Discounting first would give 12.8. Got {got!r}"
    )


def test_ticket_price_age_bands(day):
    assert _close(day.ticket_price(30, False, False), 12.0)
    assert _close(day.ticket_price(10, False, False), 6.0)
    assert _close(day.ticket_price(16, False, False), 12.0)
    assert _close(day.ticket_price(64, False, False), 12.0)
    assert _close(day.ticket_price(65, False, False), 7.0)
    assert _close(day.ticket_price(10, True, False), 5.4)
    assert _close(day.ticket_price(70, False, True), 9.0)


def test_ticket_price_free_stays_free(day):
    got = day.ticket_price(3, True, True)
    assert _close(got, 0.0), (
        "an under-5 is free, and neither the weekend surcharge nor the member "
        f"discount changes that. Got {got!r}"
    )


def test_ticket_price_rejects_impossible_ages(day):
    assert _close(day.ticket_price(130, False, False), 0.0)
    assert _close(day.ticket_price(-1, True, True), 0.0)
