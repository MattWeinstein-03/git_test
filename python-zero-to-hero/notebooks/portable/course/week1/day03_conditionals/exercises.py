"""Day 03 exercises — Conditionals.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

`def` is still just "a named recipe" until Day 8. Write your code indented under
the `def` line and finish with `return <the answer>`.

Everything here is solvable with Days 1-3 tools: arithmetic, string methods,
f-strings, comparisons, `and`/`or`/`not`, `if`/`elif`/`else`, truthiness, chained
comparisons, conditional expressions, and `is`. You do not need loops (Day 4) or
lists (Day 5) for any of them.

Two habits the tests are watching for:

* Return the answer, never `print` it. A function that prints gives back `None`,
  and `None` is not a price or a grade.
* Order your branches most specific first (section 4.1). Several of these have a
  branch that is unreachable if you get the order wrong, and the test for that
  branch is the one that will fail.

Grade your work from the course root:

    python check.py day03
    python check.py day03 -v      # show full failure detail
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Exercise 1 — a comparison is a value (section 1)
# ---------------------------------------------------------------------------
def is_freezing(celsius: float) -> bool:
    """Return True when a temperature is at or below freezing point.

    Freezing point is 0 degrees Celsius, and 0 itself counts as freezing.

    You do not need an `if` for this. A comparison already produces the `True`
    or `False` you want, so `return` the comparison itself. If you find
    yourself writing `if ...: return True else: return False`, you have written
    four lines where one will do.

    Args:
        celsius: a temperature in degrees Celsius.

    Returns:
        True if `celsius` is 0 or below, False otherwise.

    Examples:
        is_freezing(-4.0) -> True
        is_freezing(0) -> True
        is_freezing(0.5) -> False
        is_freezing(21.0) -> False
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: is_freezing")


# ---------------------------------------------------------------------------
# Exercise 2 — a three-way if / elif / else (section 4)
# ---------------------------------------------------------------------------
def sign_word(number: float) -> str:
    """Describe a number as "negative", "zero" or "positive".

    Exactly one of the three answers applies to any number, so this is one
    decision with three outcomes: a single `if` / `elif` / `else` chain, not
    three separate `if` statements.

    Args:
        number: any number.

    Returns:
        "negative" when the number is below zero, "zero" when it is exactly
        zero, "positive" when it is above zero.

    Examples:
        sign_word(-3) -> "negative"
        sign_word(0) -> "zero"
        sign_word(0.0) -> "zero"
        sign_word(7.5) -> "positive"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: sign_word")


# ---------------------------------------------------------------------------
# Exercise 3 — chained comparison (section 8)
# ---------------------------------------------------------------------------
def is_valid_percentage(value: float) -> bool:
    """Return True when `value` is a percentage between 0 and 100 inclusive.

    Both ends count: 0 is valid and 100 is valid.

    Write this as one chained comparison — `low <= x <= high` — rather than two
    comparisons joined with `and`. It reads like the mathematics it is, and it
    evaluates `value` only once.

    Args:
        value: a number that may or may not be a sensible percentage.

    Returns:
        True if 0 <= value <= 100, False otherwise.

    Examples:
        is_valid_percentage(0) -> True
        is_valid_percentage(55.5) -> True
        is_valid_percentage(100) -> True
        is_valid_percentage(100.01) -> False
        is_valid_percentage(-0.5) -> False
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: is_valid_percentage")


# ---------------------------------------------------------------------------
# Exercise 4 — and / or / not, with brackets (section 3.1)
# ---------------------------------------------------------------------------
def can_ride(height_cm: int, age: int, with_adult: bool) -> bool:
    """Decide whether someone may ride the rollercoaster.

    The rules, exactly as the operator wrote them on the sign:

        You must be at least 120 cm tall, AND either be 12 or older or be
        accompanied by an adult.

    That is a mixed `and`/`or` rule, so bracket the `or` part. Without brackets
    Python reads `a and b or c` as `(a and b) or c`, which lets a 90 cm child
    ride as long as an adult is present — a real bug, and exactly the kind that
    agrees with the correct version on most inputs.

    Args:
        height_cm: the rider's height in centimetres.
        age: the rider's age in whole years.
        with_adult: True if an adult is riding with them.

    Returns:
        True if the rider may ride, False otherwise.

    Examples:
        can_ride(150, 30, False) -> True     # tall enough, old enough
        can_ride(150, 8, True) -> True       # tall enough, adult present
        can_ride(150, 8, False) -> False     # too young, alone
        can_ride(90, 8, True) -> False       # too short, no exceptions
        can_ride(120, 12, False) -> True     # both limits are inclusive
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: can_ride")


# ---------------------------------------------------------------------------
# Exercise 5 — short-circuiting as a guard (section 3.2)
# ---------------------------------------------------------------------------
def starts_with_vowel(word: str) -> bool:
    """Return True when `word` begins with a vowel (a, e, i, o or u).

    Case does not matter: "Apple" starts with a vowel. The empty string does
    not start with anything, so it returns False.

    The interesting part is the empty string. `word[0]` raises IndexError on
    `""`, so the length test has to come first *and* be joined with `and` —
    short-circuiting means the indexing never runs when the word is empty:

        len(word) > 0 and <something about word[0]>

    Swap those two halves round and the empty-string test crashes instead of
    returning False. `"a" in "aeiou"` is a handy way to ask the second half
    (the `in` operator from Day 2, section 8.5).

    Args:
        word: a word, possibly empty, in any case.

    Returns:
        True if the first character is a vowel, False otherwise.

    Examples:
        starts_with_vowel("apple") -> True
        starts_with_vowel("Igloo") -> True
        starts_with_vowel("banana") -> False
        starts_with_vowel("") -> False
        starts_with_vowel("E") -> True
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: starts_with_vowel")


# ---------------------------------------------------------------------------
# Exercise 6 — `is None` versus truthiness (sections 7.1 and 10.1)
# ---------------------------------------------------------------------------
def describe_stock(quantity: int | None) -> str:
    """Describe a stock level, keeping "unknown" and "none" apart.

    `quantity` is either a whole number or `None`. `None` means nobody has
    counted the shelf yet; `0` means somebody counted and there was nothing
    there. Those are different facts and the answer must distinguish them —
    which is precisely what plain truthiness cannot do, because `None` and `0`
    are both falsy.

    Test for `None` first, with `is None` (not `== None`). A negative quantity
    is impossible, so treat it as bad data.

    Args:
        quantity: the number of items in stock, or None if never counted.

    Returns:
        "unknown" when quantity is None,
        "out of stock" when quantity is 0,
        "in stock" when quantity is 1 or more,
        "invalid" when quantity is negative.

    Examples:
        describe_stock(None) -> "unknown"
        describe_stock(0) -> "out of stock"
        describe_stock(12) -> "in stock"
        describe_stock(-3) -> "invalid"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: describe_stock")


# ---------------------------------------------------------------------------
# Exercise 7 — a conditional expression (section 9)
# ---------------------------------------------------------------------------
def pluralise(count: int, noun: str) -> str:
    """Return "<count> <noun>", adding an "s" to the noun unless count is 1.

    Assume the noun is one that pluralises with a plain "s" ("item", "file",
    "dog"). Zero and negative counts take the plural, because English does:
    "0 items", "-1 items".

    Use a conditional expression — `"s" if count != 1 else ""` — inside an
    f-string, as in section 9. A four-line `if`/`else` block that assigns the
    suffix works too, but this is exactly the case the one-liner exists for.

    Args:
        count: how many there are.
        noun: the singular noun.

    Returns:
        The count and the correctly pluralised noun, separated by one space.

    Examples:
        pluralise(1, "item") -> "1 item"
        pluralise(0, "item") -> "0 items"
        pluralise(3, "file") -> "3 files"
        pluralise(-1, "dog") -> "-1 dogs"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: pluralise")


# ---------------------------------------------------------------------------
# Exercise 8 — a grading chain with a guard clause (sections 4.2, 4.3)
# ---------------------------------------------------------------------------
def letter_grade(score: int) -> str:
    """Turn an exam score out of 100 into a letter grade.

    The bands:
        90 and above  -> "A"
        80 to 89      -> "B"
        70 to 79      -> "C"
        60 to 69      -> "D"
        below 60      -> "F"

    A score outside 0 to 100 is not a grade at all; return "invalid" for those.
    Deal with that first, as a guard clause (section 4.3), so the rest of the
    chain can assume the score is sane.

    Then order the bands from most specific to least specific. Because an
    `if`/`elif` chain stops at the first match, `elif score >= 80` already
    means "80 to 89" — you never need `and score < 90`. If you find yourself
    writing the upper bound, re-read section 4.2.

    Args:
        score: an exam score, expected to be 0 to 100 inclusive.

    Returns:
        "A", "B", "C", "D", "F", or "invalid".

    Examples:
        letter_grade(95) -> "A"
        letter_grade(90) -> "A"
        letter_grade(89) -> "B"
        letter_grade(60) -> "D"
        letter_grade(0) -> "F"
        letter_grade(101) -> "invalid"
        letter_grade(-1) -> "invalid"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: letter_grade")


# ---------------------------------------------------------------------------
# Exercise 9 — branch order decides the answer (sections 4.1, and % from Day 2)
# ---------------------------------------------------------------------------
def fizz_label(number: int) -> str:
    """Label a number for the classic Fizz-Buzz rule.

    A number divisible by both 3 and 5 is "FizzBuzz". Divisible by 3 only is
    "Fizz". Divisible by 5 only is "Buzz". Anything else is the number itself,
    as text — use `str(number)` so the return type is always a string.

    "Divisible by 3" is `number % 3 == 0` (Day 2, section 1.3).

    The whole exercise is branch order. "Divisible by both" is the most
    specific case, so it goes first; test for it before the single-factor
    cases, or 15 comes back as "Fizz" and the "FizzBuzz" branch never runs.

    Note that 0 is divisible by everything: `0 % 3` is `0`.

    Args:
        number: any whole number.

    Returns:
        "FizzBuzz", "Fizz", "Buzz", or the number as a string.

    Examples:
        fizz_label(1) -> "1"
        fizz_label(3) -> "Fizz"
        fizz_label(5) -> "Buzz"
        fizz_label(15) -> "FizzBuzz"
        fizz_label(0) -> "FizzBuzz"
        fizz_label(-9) -> "Fizz"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: fizz_label")


# ---------------------------------------------------------------------------
# Exercise 10 — the whole day in one rule (the hard one)
# ---------------------------------------------------------------------------
def ticket_price(age: int, is_member: bool, is_weekend: bool) -> float:
    """Work out the price of a cinema ticket in pounds.

    Apply the rules in this order — the order is part of the exercise, because
    a discount applied before a surcharge gives a different number:

    1. Sanity check. An age below 0 or above 120 is not a person; return 0.0
       immediately as a guard clause and do nothing else.
    2. Base price by age band:
           under 5      -> 0.0   (free)
           5 to 15      -> 6.00
           16 to 64     -> 12.00
           65 and over  -> 7.00
    3. Weekend surcharge: add 2.00 — but only if the base price is not free.
       A free ticket stays free on a Saturday.
    4. Member discount: members pay 90% of whatever the price is at this point.
    5. Round the result to 2 decimal places and return it as a float.

    Steps 3 and 4 are where the marks are. Use the age bands as one
    `if`/`elif`/`else` chain (no redundant upper bounds), and remember that a
    price of 0.0 is falsy, which makes step 3's condition short.

    Args:
        age: the ticket holder's age in whole years.
        is_member: True if they hold a membership card.
        is_weekend: True for Saturday or Sunday.

    Returns:
        The price in pounds, rounded to 2 decimals. 0.0 for free or invalid.

    Examples:
        ticket_price(30, False, False) -> 12.0
        ticket_price(30, False, True) -> 14.0     # 12 + 2 weekend
        ticket_price(30, True, True) -> 12.6      # (12 + 2) * 0.9
        ticket_price(10, True, False) -> 5.4      # 6 * 0.9
        ticket_price(70, False, True) -> 9.0      # 7 + 2
        ticket_price(3, True, True) -> 0.0        # free stays free
        ticket_price(130, False, False) -> 0.0    # not a person
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: ticket_price")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(letter_grade(84))
    # print(fizz_label(15))
    # print(ticket_price(30, True, True))
    print("Run `python check.py day03` from the course root to grade your work.")
