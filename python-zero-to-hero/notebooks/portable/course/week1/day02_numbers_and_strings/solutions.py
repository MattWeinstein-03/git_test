"""Day 02 solutions — Numbers and Strings.

Reference implementations. Same names, same signatures, same docstrings as
exercises.py. Read these after you have made your own attempt.
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
    # why: index 0 is the first character; .upper() on a one-character string
    # is still just a string, so it can be glued straight into an f-string.
    return f"{first[0].upper()}.{last[0].upper()}."


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
    # why: chaining reads left to right as a pipeline — strip, then title.
    # Each call returns a NEW string, which the next call consumes.
    return raw.strip().title()


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
    # why: round once, at the end. Rounding the multiplier or an intermediate
    # value first would introduce an error and then multiply it.
    return round(float(price) * (1 + tax_rate), 2)


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
    hours = total_seconds // 3600
    # why: strip the whole hours off first (% 3600), then ask how many whole
    # minutes are left in the remainder.
    minutes = total_seconds % 3600 // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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
    # why: number[-4:] is "the last four" without any arithmetic, and
    # "*" * (len - 4) is exactly as many stars as we hid. A 4-character input
    # gives "*" * 0, which is the empty string — no special case needed.
    return "*" * (len(number) - 4) + number[-4:]


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
    # why: split() with no argument throws away every run of whitespace,
    # including tabs and newlines, so no separate strip() or replace() is
    # needed. join then puts exactly one hyphen back between the pieces.
    return "-".join(title.lower().split())


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
    # why: the spec order is [,][.precision][type] — the comma groups
    # thousands, .2f fixes the decimals. The £ is just literal text.
    return f"£{amount:,.2f}"


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
    # why: the specifier writes the expression text for you, so the label can
    # never drift out of sync with the value. It uses repr(), which is why a
    # string comes back quoted.
    return f"{total=}"


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
    # why: one f-string, three specs, no manual space counting — change a
    # width and the whole column moves.
    return f"{name:<12}{quantity:>5}{price:>10.2f}"


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
    words = text.split()
    word_count = len(words)
    # why: joining the split pieces with nothing removes every space, tab and
    # newline in one step, so the letter count needs no character-by-character
    # work (which would need a loop we have not learned yet).
    letters = len("".join(words))
    average = round(letters / word_count, 2)

    header = "Summary"
    underline = "-" * len(header)
    chars_line = f"{'characters':<14}{len(text):>6}"
    words_line = f"{'words':<14}{word_count:>6}"
    average_line = f"{'avg word len':<14}{average:>6.2f}"
    # why: "\n".join keeps the lines visible as separate pieces and guarantees
    # there is no trailing newline.
    return "\n".join([header, underline, chars_line, words_line, average_line])


if __name__ == "__main__":
    print(text_summary("the cat sat on the mat"))
