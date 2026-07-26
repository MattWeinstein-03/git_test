"""Day 04 exercises — Loops.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

`def` is still just "a named recipe" until Day 8. Write your code indented under
the `def` line and finish with `return <the answer>`.

Everything here is solvable with Days 1-4 tools: arithmetic, string methods and
slicing, f-strings, `if`/`elif`/`else`, `while`, `for`, `range`, `break`,
`continue`, loop `else`, and accumulator variables. Lists arrive tomorrow, so
today every accumulator is a number, a bool or a string — which means no
`.split()`, no `.join()` and no `sorted()`. That restriction is deliberate: the
long way round is what makes tomorrow's shortcuts make sense.

Two questions to ask yourself before writing any of these:

1. What should the answer be for *empty* input — an empty string, or a count of
   zero? That is the value your accumulator must start at.
2. Am I walking through the items of something (use `for`), or repeating until
   a condition changes (use `while`)?

Every function returns its answer except `print_countdown`, which is explicitly
about printing. Everything else must `return`; a function that prints instead
gives back `None`, and `None` is not a total.

Grade your work from the course root:

    python check.py day04
    python check.py day04 -v      # show full failure detail
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
    # TODO: your code here
    raise NotImplementedError("exercise 1: sum_to")


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
    # TODO: your code here
    raise NotImplementedError("exercise 2: count_vowels")


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
    # TODO: your code here
    raise NotImplementedError("exercise 3: count_up_to")


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
    # TODO: your code here
    raise NotImplementedError("exercise 4: largest_digit")


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
    # TODO: your code here
    raise NotImplementedError("exercise 5: first_index_of")


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
    # TODO: your code here
    raise NotImplementedError("exercise 6: print_countdown")


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
    # TODO: your code here
    raise NotImplementedError("exercise 7: is_prime")


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
    # TODO: your code here
    raise NotImplementedError("exercise 8: collatz_steps")


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
    # TODO: your code here
    raise NotImplementedError("exercise 9: triangle")


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
    # TODO: your code here
    raise NotImplementedError("exercise 10: sum_csv_numbers")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(count_up_to(5))
    # print(triangle(4))
    # print(sum_csv_numbers("10, 20, 30"))
    print("Run `python check.py day04` from the course root to grade your work.")
