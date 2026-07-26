"""Day 04 graded checks — Loops."""


# --- Exercise 1: sum_to ---------------------------------------------------
def test_sum_to_five(day):
    got = day.sum_to(5)
    assert got == 15, f"1+2+3+4+5 is 15, got {got!r}"


def test_sum_to_one(day):
    got = day.sum_to(1)
    assert got == 1, f"the range must include n itself, got {got!r}"


def test_sum_to_zero_and_negative(day):
    assert day.sum_to(0) == 0
    assert day.sum_to(-3) == 0


def test_sum_to_one_hundred(day):
    got = day.sum_to(100)
    assert got == 5050, f"want 5050, got {got!r} — check the range's stop value"


# --- Exercise 2: count_vowels --------------------------------------------
def test_count_vowels_sentence(day):
    got = day.count_vowels("hello world")
    assert got == 3, f"e, o and o make 3, got {got!r}"


def test_count_vowels_ignores_case(day):
    got = day.count_vowels("AEIOU")
    assert got == 5, f"upper-case vowels count too, got {got!r}"


def test_count_vowels_none_present(day):
    assert day.count_vowels("rhythm") == 0


def test_count_vowels_empty_string(day):
    got = day.count_vowels("")
    assert got == 0, f"an empty string has no vowels, got {got!r}"


def test_count_vowels_counts_repeats(day):
    assert day.count_vowels("aaa eee") == 6


# --- Exercise 3: count_up_to ---------------------------------------------
def test_count_up_to_three(day):
    got = day.count_up_to(3)
    assert got == "1 2 3", f"got {got!r}"


def test_count_up_to_one_has_no_spaces(day):
    got = day.count_up_to(1)
    assert got == "1", f"one number needs no separator at all, got {got!r}"


def test_count_up_to_zero_and_negative_are_empty(day):
    assert day.count_up_to(0) == ""
    assert day.count_up_to(-2) == ""


def test_count_up_to_five_has_no_edge_spaces(day):
    got = day.count_up_to(5)
    assert got == "1 2 3 4 5", f"got {got!r}"
    assert not got.startswith(" "), f"no leading space, got {got!r}"
    assert not got.endswith(" "), f"no trailing space, got {got!r}"


# --- Exercise 4: largest_digit -------------------------------------------
def test_largest_digit_mixed(day):
    got = day.largest_digit(4291)
    assert got == 9, f"got {got!r}"


def test_largest_digit_ignores_the_minus_sign(day):
    got = day.largest_digit(-57)
    assert got == 7, (
        "'-' is not a digit; use abs(number) before turning it into text. "
        f"Got {got!r}"
    )


def test_largest_digit_all_the_same(day):
    assert day.largest_digit(1111) == 1


def test_largest_digit_zero(day):
    got = day.largest_digit(0)
    assert got == 0, f"the only digit of 0 is 0, got {got!r}"


def test_largest_digit_returns_an_int_not_a_string(day):
    got = day.largest_digit(4291)
    assert isinstance(got, int), f"convert the character back with int(), got {got!r}"


# --- Exercise 5: first_index_of ------------------------------------------
def test_first_index_of_middle_character(day):
    got = day.first_index_of("hello", "l")
    assert got == 2, f"the first 'l' is at index 2, not 3, got {got!r}"


def test_first_index_of_first_character(day):
    assert day.first_index_of("hello", "h") == 0


def test_first_index_of_missing_character(day):
    got = day.first_index_of("hello", "z")
    assert got == -1, f"not found is -1, got {got!r}"


def test_first_index_of_empty_text(day):
    assert day.first_index_of("", "a") == -1


def test_first_index_of_stops_at_the_first_match(day):
    got = day.first_index_of("banana", "a")
    assert got == 1, (
        "without a break (or an immediate return) you get the LAST match, 5. "
        f"Got {got!r}"
    )


# --- Exercise 6: print_countdown (this one prints, so we capture output) ---
def test_print_countdown_from_three(day, capsys):
    day.print_countdown(3)
    got = capsys.readouterr().out
    want = "3\n2\n1\nLiftoff!\n"
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_print_countdown_from_one(day, capsys):
    day.print_countdown(1)
    got = capsys.readouterr().out
    assert got == "1\nLiftoff!\n", f"got {got!r}"


def test_print_countdown_from_zero_prints_only_liftoff(day, capsys):
    day.print_countdown(0)
    got = capsys.readouterr().out
    assert got == "Liftoff!\n", (
        "with nothing to count down, the loop body must not run at all. "
        f"Got {got!r}"
    )


def test_print_countdown_returns_none(day, capsys):
    got = day.print_countdown(2)
    capsys.readouterr()
    assert got is None, f"this exercise prints, it does not return, got {got!r}"


# --- Exercise 7: is_prime -----------------------------------------------
def test_is_prime_small_primes(day):
    assert day.is_prime(2) is True
    assert day.is_prime(3) is True
    assert day.is_prime(7) is True


def test_is_prime_perfect_square_is_not_prime(day):
    got = day.is_prime(9)
    assert got is False, (
        "3 divides 9. If this said True, your range stops one short — the "
        f"square root itself has to be tested. Got {got!r}"
    )
    assert day.is_prime(25) is False


def test_is_prime_larger_number(day):
    assert day.is_prime(97) is True
    assert day.is_prime(91) is False


def test_is_prime_rejects_one_zero_and_negatives(day):
    got = day.is_prime(1)
    assert got is False, f"1 is not prime — guard the small cases, got {got!r}"
    assert day.is_prime(0) is False
    assert day.is_prime(-7) is False


# --- Exercise 8: collatz_steps -------------------------------------------
def test_collatz_steps_one_is_already_there(day):
    got = day.collatz_steps(1)
    assert got == 0, f"starting at 1 takes no steps, got {got!r}"


def test_collatz_steps_two(day):
    assert day.collatz_steps(2) == 1


def test_collatz_steps_six(day):
    got = day.collatz_steps(6)
    assert got == 8, f"6 3 10 5 16 8 4 2 1 is 8 steps, got {got!r}"


def test_collatz_steps_twenty_seven(day):
    got = day.collatz_steps(27)
    assert got == 111, f"want 111, got {got!r}"


def test_collatz_steps_rejects_values_below_one(day):
    assert day.collatz_steps(0) == -1
    assert day.collatz_steps(-5) == -1


# --- Exercise 9: triangle ------------------------------------------------
def test_triangle_three_rows(day):
    got = day.triangle(3)
    want = "*\n**\n***"
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_triangle_one_row(day):
    assert day.triangle(1) == "*"


def test_triangle_zero_and_negative_are_empty(day):
    assert day.triangle(0) == ""
    assert day.triangle(-4) == ""


def test_triangle_has_no_trailing_newline(day):
    got = day.triangle(4)
    assert not got.endswith("\n"), (
        "add the newline BEFORE each row except the first, or slice the last "
        f"one off. Got {got!r}"
    )


def test_triangle_row_widths_increase_by_one(day):
    got = day.triangle(5)
    assert got.count("\n") == 4, f"5 rows need 4 newlines between them, got {got!r}"
    assert got.startswith("*\n**\n"), f"row 1 has one star, row 2 has two, got {got!r}"
    assert got.endswith("\n*****"), f"the last row has 5 stars, got {got!r}"
    assert got.count("*") == 15, f"1+2+3+4+5 = 15 stars in total, got {got!r}"


# --- Exercise 10: sum_csv_numbers ----------------------------------------
def test_sum_csv_numbers_single_digits(day):
    got = day.sum_csv_numbers("3,1,4")
    assert got == 8, f"got {got!r}"


def test_sum_csv_numbers_multi_digit_numbers(day):
    got = day.sum_csv_numbers("10,20,30")
    assert got == 60, (
        "a two-digit field is one number, not two digits added up. "
        f"Got {got!r}"
    )


def test_sum_csv_numbers_one_field_only(day):
    got = day.sum_csv_numbers("12")
    assert got == 12, (
        "with no comma at all, the number is only banked after the loop ends. "
        f"Got {got!r}"
    )


def test_sum_csv_numbers_ignores_spaces(day):
    assert day.sum_csv_numbers("1, 2, 3") == 6
    assert day.sum_csv_numbers(" 100 , 1 ") == 101


def test_sum_csv_numbers_empty_field_counts_as_zero(day):
    assert day.sum_csv_numbers("5,") == 5
    assert day.sum_csv_numbers("") == 0
