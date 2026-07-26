"""Day 02 exercises — Numbers and Strings.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

`def` is still just "a named recipe" until Day 8. Write your code indented under
the `def` line and finish with `return <the answer>`.

Everything here is solvable with Day 1 and Day 2 tools: arithmetic, `//`, `%`,
`round`, casting, indexing, slicing, string methods, and f-strings. You do not
need `if` (Day 3) or loops (Day 4) for any of them.

Grade your work from the course root:

    python check.py day02
    python check.py day02 -v      # show full failure detail
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Exercise 1 — indexing plus a method
# ---------------------------------------------------------------------------
def initials(first: str, last: str) -> str:
    """Return the upper-case initials of a name, with a dot after each.

    Take the first character of each name, upper-case it, and follow it with a
    full stop. Assume both names have at least one character.

    Args:
        first: a first name, any case.
        last: a last name, any case.

    Returns:
        A four-character string like "A.L.".

    Examples:
        initials("Ada", "Lovelace") -> "A.L."
        initials("grace", "hopper") -> "G.H."
        initials("k", "j") -> "K.J."
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: initials")


# ---------------------------------------------------------------------------
# Exercise 2 — chaining two methods
# ---------------------------------------------------------------------------
def clean_name(raw: str) -> str:
    """Tidy up a name typed by a human.

    Remove whitespace from both ends, then capitalise the first letter of each
    word and lower-case the rest. Two chained method calls do the whole job.

    Args:
        raw: a name as typed, possibly padded and in any case.

    Returns:
        The tidied name.

    Examples:
        clean_name("  ada LOVELACE  ") -> "Ada Lovelace"
        clean_name("GRACE HOPPER") -> "Grace Hopper"
        clean_name("alan\\n") -> "Alan"
        clean_name("   ") -> ""
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: clean_name")


# ---------------------------------------------------------------------------
# Exercise 3 — arithmetic and rounding
# ---------------------------------------------------------------------------
def price_with_tax(price: float, tax_rate: float) -> float:
    """Return `price` with tax added, rounded to 2 decimal places.

    `tax_rate` is a fraction, so 0.2 means 20%. Round the final answer once,
    at the end, with `round(value, 2)`.

    Args:
        price: the pre-tax price.
        tax_rate: the tax as a fraction of the price, e.g. 0.2 for 20%.

    Returns:
        The price including tax, rounded to 2 decimals.

    Examples:
        price_with_tax(100.0, 0.2) -> 120.0
        price_with_tax(19.99, 0.2) -> 23.99
        price_with_tax(9.99, 0.0) -> 9.99
        price_with_tax(1.0, 0.175) -> 1.18
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: price_with_tax")


# ---------------------------------------------------------------------------
# Exercise 4 — // and % together, plus zero-padding
# ---------------------------------------------------------------------------
def seconds_to_clock(total_seconds: int) -> str:
    """Turn a number of seconds into a "HH:MM:SS" clock string.

    Each part is padded to at least two digits with a leading zero. Hours are
    not capped: 360000 seconds is "100:00:00" and that is correct.

    Floor division (`//`) and modulo (`%`) are the whole exercise. The f-string
    spec you want for zero-padding is `:02d`.

    Args:
        total_seconds: a whole number of seconds, 0 or more.

    Returns:
        The duration as "HH:MM:SS".

    Examples:
        seconds_to_clock(0) -> "00:00:00"
        seconds_to_clock(59) -> "00:00:59"
        seconds_to_clock(60) -> "00:01:00"
        seconds_to_clock(4000) -> "01:06:40"
        seconds_to_clock(86399) -> "23:59:59"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: seconds_to_clock")


# ---------------------------------------------------------------------------
# Exercise 5 — slicing from the right
# ---------------------------------------------------------------------------
def mask_card(number: str) -> str:
    """Hide all but the last four characters of a card number.

    Replace every character except the final four with a "*". The result is
    always the same length as the input. Assume at least four characters.

    Args:
        number: a card number as a string of digits.

    Returns:
        The masked number.

    Examples:
        mask_card("4111111111111234") -> "************1234"
        mask_card("12345") -> "*2345"
        mask_card("1234") -> "1234"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: mask_card")


# ---------------------------------------------------------------------------
# Exercise 6 — split and join
# ---------------------------------------------------------------------------
def slugify(title: str) -> str:
    """Turn a title into a URL-friendly slug.

    Lower-case everything, and replace every run of whitespace with a single
    hyphen. Leading and trailing whitespace disappears entirely, and a run of
    several spaces becomes one hyphen, not several.

    `split()` with no argument plus `"-".join(...)` does this in one line —
    section 8.3 of the lesson.

    Args:
        title: any text.

    Returns:
        The slug: lower-case words joined by single hyphens.

    Examples:
        slugify("Hello World") -> "hello-world"
        slugify("  Python   Zero to Hero  ") -> "python-zero-to-hero"
        slugify("ONE") -> "one"
        slugify("   ") -> ""
        slugify("tabs\\tand\\nnewlines") -> "tabs-and-newlines"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: slugify")


# ---------------------------------------------------------------------------
# Exercise 7 — an f-string format spec
# ---------------------------------------------------------------------------
def format_money(amount: float) -> str:
    """Format `amount` as pounds: a "£" sign, thousands separators, 2 decimals.

    One f-string with one format spec. Do not build this with `str()` and `+`.

    Args:
        amount: an amount of money.

    Returns:
        The formatted string, e.g. "£1,234.50".

    Examples:
        format_money(1234.5) -> "£1,234.50"
        format_money(0) -> "£0.00"
        format_money(9.999) -> "£10.00"
        format_money(1000000) -> "£1,000,000.00"
        format_money(-5.5) -> "£-5.50"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: format_money")


# ---------------------------------------------------------------------------
# Exercise 8 — the = specifier
# ---------------------------------------------------------------------------
def debug_line(total: object) -> str:
    """Return the f-string debugging line for the parameter `total`.

    Use the `=` specifier from section 10.3 — `f"{total=}"` — so the result
    contains the *name* `total`, an `=`, and the value as `repr()` shows it.
    Note what that means for strings: they keep their quotes.

    Do not build the string by hand with "total=" + ... ; the point of the
    exercise is the specifier.

    Args:
        total: any value.

    Returns:
        A string of the form "total=<repr of the value>".

    Examples:
        debug_line(42) -> "total=42"
        debug_line(3.5) -> "total=3.5"
        debug_line("hi") -> "total='hi'"
        debug_line(None) -> "total=None"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: debug_line")


# ---------------------------------------------------------------------------
# Exercise 9 — alignment in a fixed-width row
# ---------------------------------------------------------------------------
def table_row(name: str, quantity: int, price: float) -> str:
    """Return one row of a fixed-width table, 27 characters wide.

    The layout, all in a single f-string:
        * `name` left-justified in 12 characters
        * `quantity` right-justified in 5 characters
        * `price` right-justified in 10 characters with exactly 2 decimals

    Names longer than 12 characters are not truncated — a format spec's width
    is a minimum, not a maximum.

    Args:
        name: the item name.
        quantity: how many.
        price: the unit price.

    Returns:
        The formatted row, with no newline.

    Examples:
        table_row("widget", 2, 9.99) -> "widget          2      9.99"
        table_row("bolt", 10, 0.5) -> "bolt           10      0.50"
        table_row("gizmo", 1, 24.0) -> "gizmo           1     24.00"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: table_row")


# ---------------------------------------------------------------------------
# Exercise 10 — the whole day in one report (the hard one)
# ---------------------------------------------------------------------------
def text_summary(text: str) -> str:
    """Return a four-part summary of `text` as one multi-line string.

    Assume `text` contains at least one word.

    Definitions:
        * characters   — `len(text)`, exactly as given, spaces included
        * words        — how many whitespace-separated pieces there are
        * avg word len — the number of non-whitespace characters divided by the
          number of words, rounded to 2 decimals. `"".join(text.split())` gives
          you the text with all whitespace removed.

    Layout — five lines joined with "\\n", no trailing newline:
        line 1: "Summary"
        line 2: seven dashes, "-------"
        line 3: "characters" left-justified in 14, then the count
                right-justified in 6
        line 4: "words" left-justified in 14, then the count right-justified
                in 6
        line 5: "avg word len" left-justified in 14, then the average
                right-justified in 6 with exactly 2 decimals

    Args:
        text: the text to summarise; at least one word.

    Returns:
        The five-line summary.

    Examples:
        text_summary("the cat sat on the mat") ->
            "Summary\\n"
            "-------\\n"
            "characters        22\\n"
            "words              6\\n"
            "avg word len    2.83"

        text_summary("hello") ->
            "Summary\\n"
            "-------\\n"
            "characters         5\\n"
            "words              1\\n"
            "avg word len    5.00"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: text_summary")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(seconds_to_clock(4000))
    # print(table_row("widget", 2, 9.99))
    # print(text_summary("the cat sat on the mat"))
    print("Run `python check.py day02` from the course root to grade your work.")
