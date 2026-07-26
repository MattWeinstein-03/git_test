"""Day 04 solutions — Loops.

Reference implementations. Same names, same signatures, same docstrings as
exercises.py. Read these after you have made your own attempt.

Every one of them is a plain loop with an accumulator. There are shorter,
cleverer ways to write several of these using tools from Day 5 onwards; none of
them would teach you anything today.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Exercise 1 — a running total (sections 4.2 and 6.1)
# ---------------------------------------------------------------------------
def sum_to(n: int) -> int:
    """Add up every whole number from 1 to `n` inclusive.

    Use a `for` loop over a `range`. Remember that `range`'s stop value is
    excluded, so "up to and including n" is `range(1, n + 1)`.

    When `n` is 0 or negative there is nothing to add, and the answer is 0 —
    which is exactly what an accumulator starting at 0 gives you if the loop
    body never runs. You should not need an `if` for that case at all.

    Args:
        n: the last number to include.

    Returns:
        The sum 1 + 2 + ... + n, or 0 when n is less than 1.

    Examples:
        sum_to(5) -> 15        # 1+2+3+4+5
        sum_to(1) -> 1
        sum_to(0) -> 0
        sum_to(-3) -> 0
        sum_to(100) -> 5050
    """
    total = 0
    # why: no guard for n < 1 is needed. range(1, 0) and range(1, -2) are both
    # empty, the body never runs, and the accumulator's starting value of 0 is
    # already the correct answer for "nothing to add".
    for i in range(1, n + 1):
        total += i
    return total


# ---------------------------------------------------------------------------
# Exercise 2 — a counter over a string (sections 3.2 and 6.2)
# ---------------------------------------------------------------------------
def count_vowels(text: str) -> int:
    """Count the vowels in `text`.

    The vowels are a, e, i, o and u. Case does not matter, so "A" counts. `y`
    is not a vowel for this exercise.

    Walk the string one character at a time with `for character in text:`, and
    add 1 to a counter each time the character is a vowel. `character.lower()
    in "aeiou"` is a compact way to ask the question.

    Args:
        text: any text, possibly empty.

    Returns:
        How many characters of `text` are vowels.

    Examples:
        count_vowels("hello world") -> 3
        count_vowels("AEIOU") -> 5
        count_vowels("rhythm") -> 0
        count_vowels("") -> 0
    """
    count = 0
    for character in text:
        # why: lower() once, on the single character, so the test handles "A"
        # and "a" without listing ten vowels.
        if character.lower() in "aeiou":
            count += 1
    return count


# ---------------------------------------------------------------------------
# Exercise 3 — a string accumulator with separators (section 6.5)
# ---------------------------------------------------------------------------
def count_up_to(n: int) -> str:
    """Return the numbers 1 to `n` as one string, separated by single spaces.

    There is no space at the start and none at the end — the spaces go
    *between* the numbers, so `n` numbers need `n - 1` spaces. Two ways to get
    that right, both in section 6.5:

        * add the separator before each number *except* when the accumulator is
          still empty (`if result:` is the test), or
        * add "number + space" every time and slice the last character off at
          the end with `result[:-1]`.

    When `n` is 0 or negative there are no numbers, so the answer is the empty
    string. Note that you need `str(i)` to glue a number onto a string.

    Args:
        n: the last number to include.

    Returns:
        The numbers 1..n joined by single spaces, or "" when n is less than 1.

    Examples:
        count_up_to(3) -> "1 2 3"
        count_up_to(1) -> "1"
        count_up_to(0) -> ""
        count_up_to(-2) -> ""
        count_up_to(5) -> "1 2 3 4 5"
    """
    result = ""
    for i in range(1, n + 1):
        # why: the separator goes in BEFORE the new number, and only when the
        # accumulator already holds something. That is Day 3 truthiness: "" is
        # falsy, so the first number never gets a leading space, and there is
        # never a trailing one to clean up afterwards.
        if result:
            result += " "
        result += str(i)
    return result


# ---------------------------------------------------------------------------
# Exercise 4 — max-so-far (section 6.3)
# ---------------------------------------------------------------------------
def largest_digit(number: int) -> int:
    """Return the largest single digit in `number`.

    A minus sign is not a digit, so work with `abs(number)`. Turn the number
    into text with `str(...)`, walk its characters, convert each one back with
    `int(character)`, and keep the biggest value you have seen.

    Because every digit is 0 or more, starting the accumulator at 0 is safe
    here — and it gives the right answer for `0`, whose only digit is 0.

    Args:
        number: any whole number, positive, negative or zero.

    Returns:
        The value of the largest digit, as an int.

    Examples:
        largest_digit(4291) -> 9
        largest_digit(-57) -> 7
        largest_digit(1111) -> 1
        largest_digit(0) -> 0
        largest_digit(9) -> 9
    """
    # why: abs() first, so the "-" of a negative number never reaches the loop
    # and int(character) can never fail.
    digits = str(abs(number))
    largest = 0
    for character in digits:
        value = int(character)
        if value > largest:
            largest = value
    return largest


# ---------------------------------------------------------------------------
# Exercise 5 — search with break, and the -1 convention (sections 4.5, 7)
# ---------------------------------------------------------------------------
def first_index_of(text: str, target: str) -> int:
    """Return the index of the first occurrence of `target` in `text`.

    `target` is a single character. When it does not appear at all, return -1 —
    the same "not found" convention as Day 2's `str.find`.

    Write the loop yourself rather than calling `find` or `index`; the point of
    the exercise is the search. You need the *position*, not just the
    character, so loop with `for i in range(len(text)):` and compare `text[i]`.

    Stop as soon as you find it. Without a `break` (or an immediate return) you
    would end up reporting the *last* match instead of the first — the loop
    would still be correct, and the answer would still be wrong.

    Args:
        text: the text to search, possibly empty.
        target: a single character to look for.

    Returns:
        The index of the first match, or -1 if there is none.

    Examples:
        first_index_of("hello", "l") -> 2
        first_index_of("hello", "h") -> 0
        first_index_of("hello", "z") -> -1
        first_index_of("", "a") -> -1
        first_index_of("banana", "a") -> 1
    """
    # why: range(len(text)) gives exactly the valid indexes, so there is no
    # off-by-one to get wrong. An empty string gives an empty range, the body
    # never runs, and the -1 at the bottom is returned.
    for i in range(len(text)):
        if text[i] == target:
            # why: returning here is `break` plus "and this is the answer" in
            # one move — nothing after the first match is even looked at.
            return i
    return -1


# ---------------------------------------------------------------------------
# Exercise 6 — a while loop that prints (sections 2.2 and 13)
# ---------------------------------------------------------------------------
def print_countdown(start: int) -> None:
    """Print a countdown from `start` to 1, then "Liftoff!".

    This is the one exercise today that prints instead of returning. Each
    number goes on its own line, in descending order, followed by a final line
    reading exactly `Liftoff!`.

    When `start` is 0 or negative there is nothing to count down, so only the
    `Liftoff!` line is printed.

    Use a `while` loop, and make sure something in the body moves `start`
    towards the exit — `start -= 1`. If you leave that out, the loop prints the
    same number forever, and you stop it with Ctrl-C (section 13).

    Args:
        start: the number to count down from.

    Returns:
        None. This one prints; it does not return the text.

    Examples:
        print_countdown(3) prints:
            3
            2
            1
            Liftoff!

        print_countdown(1) prints:
            1
            Liftoff!

        print_countdown(0) prints:
            Liftoff!
    """
    # why: reassigning the parameter is fine here — it is a local name, and the
    # caller's variable is untouched. `current = start` would be equally good
    # and slightly kinder to a reader.
    current = start
    while current > 0:
        print(current)
        current -= 1  # the CHANGE: without this the loop never ends
    print("Liftoff!")


# ---------------------------------------------------------------------------
# Exercise 7 — a loop with an early exit (sections 7, 9, 12)
# ---------------------------------------------------------------------------
def is_prime(n: int) -> bool:
    """Return True when `n` is a prime number.

    A prime is a whole number of 2 or more whose only factors are 1 and itself.
    So 2, 3, 5, 7 and 97 are prime; 1, 0 and every negative number are not; and
    9 is not, because 3 divides it.

    Guard the small cases first (Day 3, section 4.3), then look for a factor:
    try each candidate divisor and ask `n % divisor == 0`. The moment one
    divides evenly you have your answer and can stop — no point testing the
    rest.

    You only have to test divisors up to the square root of `n`, because a
    factor above it always has a partner below it. `int(n ** 0.5) + 1` is the
    stop value for that; the `+ 1` is there because `range`'s stop is excluded,
    and getting it wrong makes `is_prime(9)` claim 9 is prime. If the square
    root feels like a leap, `range(2, n)` is also correct, just slower.

    Args:
        n: any whole number.

    Returns:
        True if `n` is prime, False otherwise.

    Examples:
        is_prime(2) -> True
        is_prime(9) -> False
        is_prime(97) -> True
        is_prime(1) -> False
        is_prime(-7) -> False
    """
    # why: guard clause first. Everything below 2 — including 1, 0 and the
    # negatives — is not prime, and the loop below would wrongly report True
    # for them because its range would be empty.
    if n < 2:
        return False

    # why: the + 1 makes the square root itself a candidate. For n = 9,
    # int(9 ** 0.5) is 3, so the range must be range(2, 4) to include 3 — and
    # 3 is the divisor that proves 9 is not prime. Drop the + 1 and this
    # function claims every perfect square of a prime is prime.
    for divisor in range(2, int(n**0.5) + 1):
        if n % divisor == 0:
            return False  # one factor is enough; stop looking
    return True


# ---------------------------------------------------------------------------
# Exercise 8 — a while loop of unknown length (sections 2.3 and 13.3)
# ---------------------------------------------------------------------------
def collatz_steps(n: int) -> int:
    """Count the steps the Collatz rule takes to get from `n` down to 1.

    The rule, applied over and over:
        * if the current value is even, halve it (use `//` so it stays an int)
        * if it is odd, multiply by 3 and add 1
    Stop when the value reaches 1, and return how many steps that took.

    From 6: 6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1, which is 8 steps.
    Starting at 1 takes 0 steps, because you are already there.

    Nobody can tell you in advance how many steps a given number needs — which
    is exactly why this is a `while` loop and not a `for`. The condition is
    "the value is not 1 yet".

    Anything below 1 is not a valid starting point; return -1 for those.

    Args:
        n: the starting value.

    Returns:
        The number of steps to reach 1, or -1 when n is less than 1.

    Examples:
        collatz_steps(1) -> 0
        collatz_steps(2) -> 1
        collatz_steps(6) -> 8
        collatz_steps(27) -> 111
        collatz_steps(0) -> -1
    """
    if n < 1:
        return -1

    value = n
    steps = 0
    # why: the condition is the finish line ("not 1 yet"), because there is no
    # way to know the number of turns in advance. n = 1 fails the test straight
    # away and the answer is 0 turns, which is correct.
    while value != 1:
        if value % 2 == 0:
            # why: // keeps the value an int. / would turn it into a float, and
            # then `value % 2 == 0` starts comparing floats — Day 2, section 3.
            value = value // 2
        else:
            value = value * 3 + 1
        steps += 1
    return steps


# ---------------------------------------------------------------------------
# Exercise 9 — nested loops that build text (section 11)
# ---------------------------------------------------------------------------
def triangle(height: int) -> str:
    """Build a left-aligned triangle of "*" characters, as one string.

    Row 1 has one star, row 2 has two, and so on down to row `height`. The rows
    are separated by newlines ("\\n") and there is **no** trailing newline at
    the end. A height of 0 or less gives the empty string.

    The classic shape is a loop inside a loop: the outer loop walks the rows,
    and the inner loop adds `row` stars. `"*" * row` (Day 2 string repetition)
    can do the inner loop's job in one operation if you prefer — both are
    fine, and the second is impossible to get off by one.

    Watch the newlines. Adding "\\n" after every row leaves one on the end;
    adding it *before* every row except the first does not (section 11.3).

    Args:
        height: how many rows.

    Returns:
        The triangle as one multi-line string, with no trailing newline.

    Examples:
        triangle(3) -> "*\\n**\\n***"       which prints as:
            *
            **
            ***

        triangle(1) -> "*"
        triangle(0) -> ""
        triangle(-4) -> ""
    """
    result = ""
    # why: range(1, height + 1) makes `row` the row number AND the star count,
    # so the inner loop's bound needs no arithmetic. A height of 0 or less
    # gives an empty range and therefore the empty string, with no guard.
    for row in range(1, height + 1):
        if result:
            result += "\n"  # separator before each row except the first
        stars = ""
        for column in range(row):
            stars += "*"
        result += stars
    return result


# ---------------------------------------------------------------------------
# Exercise 10 — parsing by hand (the hard one: sections 6, 8, 10)
# ---------------------------------------------------------------------------
def sum_csv_numbers(text: str) -> int:
    """Add up the comma-separated whole numbers in `text`.

    `text` contains digits, commas and spaces, and nothing else. Commas
    separate the numbers; spaces are decoration and must be ignored.

    You cannot use `text.split(",")` — that hands back a list, and lists are
    Day 5. Do it the way a parser does, with two accumulators:

        * `total`   — the running total of the finished numbers, starts at 0
        * `current` — the number you are in the middle of reading, starts at 0

    For each character:
        * a space          -> `continue`, there is nothing to do
        * a digit          -> `current = current * 10 + int(character)`
                              (that is how "4" then "2" becomes 42)
        * a comma          -> the number has ended: add `current` to `total`
                              and reset `current` to 0

    Then the bit everyone forgets: when the loop ends there is no final comma,
    so the last number is still sitting in `current` and has never been added.
    Add it after the loop. This is a fencepost problem — three numbers have
    only two commas between them (section 12's gotcha).

    An empty field counts as 0, so `"5,"` is 5 and `""` is 0.

    Args:
        text: digits, commas and spaces only.

    Returns:
        The sum of the numbers in `text`.

    Examples:
        sum_csv_numbers("3,1,4") -> 8
        sum_csv_numbers("10,20,30") -> 60
        sum_csv_numbers("12") -> 12
        sum_csv_numbers("1, 2, 3") -> 6
        sum_csv_numbers("5,") -> 5
        sum_csv_numbers("") -> 0
    """
    total = 0
    current = 0
    for character in text:
        if character == " ":
            # why: `continue` says "nothing to do with this one" without
            # nesting the real work inside an else.
            continue
        if character == ",":
            total += current  # the number ended here
            current = 0  # start the next one from scratch
        else:
            # why: shift the digits we already have one place left and add the
            # new one. "4" then "2" -> 4 * 10 + 2 -> 42.
            current = current * 10 + int(character)
    # why: the fencepost. There is no comma after the last number, so the loop
    # never got the signal to bank it. An empty string leaves current at 0,
    # which adds nothing — so this line needs no guard either.
    return total + current


if __name__ == "__main__":
    print(count_up_to(5))
    print(triangle(4))
    print(sum_csv_numbers("10, 20, 30"))
