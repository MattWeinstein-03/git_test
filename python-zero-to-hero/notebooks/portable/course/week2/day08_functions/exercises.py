"""Day 08 exercises — Functions.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

Grade your work from the course root:

    python check.py day08
    python check.py day08 -v      # show full failure detail
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Exercise 1 — the shape of a function
# ---------------------------------------------------------------------------
def rectangle_area(width: float, height: float) -> float:
    """Return the area of a rectangle.

    Args:
        width: the rectangle's width.
        height: the rectangle's height.

    Returns:
        width multiplied by height, as a float.

    Examples:
        rectangle_area(3, 4) -> 12.0
        rectangle_area(2.5, 2) -> 5.0
        rectangle_area(0, 99) -> 0.0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: rectangle_area")


# ---------------------------------------------------------------------------
# Exercise 2 — defaults and a guard clause
# ---------------------------------------------------------------------------
def greet(name: str, greeting: str = "Hello") -> str:
    """Return a greeting line for `name`.

    An empty (or whitespace-only) name becomes "stranger". Surrounding
    whitespace on a real name is stripped.

    Args:
        name: who to greet.
        greeting: the word to greet with. Defaults to "Hello".

    Returns:
        A string of the form "<greeting>, <name>!".

    Examples:
        greet("Ada") -> "Hello, Ada!"
        greet("Ada", "Yo") -> "Yo, Ada!"
        greet("  Grace  ") -> "Hello, Grace!"
        greet("") -> "Hello, stranger!"
        greet("   ", greeting="Hi") -> "Hi, stranger!"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: greet")


# ---------------------------------------------------------------------------
# Exercise 3 — default values and rounding
# ---------------------------------------------------------------------------
def apply_discount(price: float, percent: float = 10.0) -> float:
    """Return `price` with `percent` percent taken off, rounded to 2 decimals.

    A percent of 0 leaves the price alone. A percent of 100 gives 0.0.
    Raise a ValueError if `percent` is below 0 or above 100.

    Args:
        price: the original price.
        percent: how much to knock off, from 0 to 100. Defaults to 10.0.

    Returns:
        The discounted price, rounded to 2 decimal places.

    Examples:
        apply_discount(100) -> 90.0
        apply_discount(50, percent=50) -> 25.0
        apply_discount(19.99, 0) -> 19.99
        apply_discount(10.0, 33.0) -> 6.7
        apply_discount(10.0, 150.0) -> raises ValueError
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: apply_discount")


# ---------------------------------------------------------------------------
# Exercise 4 — returning several values in a tuple
# ---------------------------------------------------------------------------
def min_max_mean(numbers: list[float]) -> tuple[float, float, float]:
    """Return the smallest value, largest value and mean of `numbers`.

    The mean is rounded to 2 decimal places. An empty list returns
    (0.0, 0.0, 0.0) rather than crashing.

    Args:
        numbers: a list of ints or floats.

    Returns:
        A 3-tuple: (minimum, maximum, mean).

    Examples:
        min_max_mean([4, 9, 1, 7]) -> (1, 9, 5.25)
        min_max_mean([2.0]) -> (2.0, 2.0, 2.0)
        min_max_mean([1, 2]) -> (1, 2, 1.5)
        min_max_mean([]) -> (0.0, 0.0, 0.0)
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: min_max_mean")


# ---------------------------------------------------------------------------
# Exercise 5 — the mutable-default trap
# ---------------------------------------------------------------------------
def collect_unique(item: str, seen: list[str] | None = None) -> list[str]:
    """Add `item` to `seen` unless it is already there, and return the list.

    When `seen` is not given you must start from a FRESH empty list, so two
    separate calls never share data. This is the mutable-default trap from
    section 4.1 of the lesson: do not write `seen: list[str] = []`.

    Args:
        item: the value to record.
        seen: an existing list to add to. Defaults to a new empty list.

    Returns:
        The list that `item` was added to (the same list object that was
        passed in, when one was passed in).

    Examples:
        collect_unique("a") -> ["a"]
        collect_unique("b") -> ["b"]          # NOT ["a", "b"]
        collect_unique("b", ["a"]) -> ["a", "b"]
        collect_unique("a", ["a"]) -> ["a"]   # no duplicates
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: collect_unique")


# ---------------------------------------------------------------------------
# Exercise 6 — a pure function that must not mutate its argument
# ---------------------------------------------------------------------------
def running_totals(numbers: list[float]) -> list[float]:
    """Return a new list of running totals, leaving `numbers` untouched.

    Element i of the result is the sum of numbers[0] through numbers[i].
    The input list must not be modified in any way.

    Args:
        numbers: a list of ints or floats.

    Returns:
        A NEW list of the same length holding the running totals.

    Examples:
        running_totals([1, 2, 3]) -> [1, 3, 6]
        running_totals([5]) -> [5]
        running_totals([2, -2, 4]) -> [2, 0, 4]
        running_totals([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: running_totals")


# ---------------------------------------------------------------------------
# Exercise 7 — *args
# ---------------------------------------------------------------------------
def summarize(*numbers: float) -> dict[str, float]:
    """Summarise however many numbers you are handed.

    Args:
        *numbers: any number of ints or floats, passed positionally.

    Returns:
        A dict with exactly these keys:
            "count"  - how many numbers were given
            "total"  - their sum
            "mean"   - their average, rounded to 2 decimals
            "spread" - largest minus smallest
        For no arguments at all, every value is 0 (count) or 0.0.

    Examples:
        summarize(1, 2, 3) -> {"count": 3, "total": 6, "mean": 2.0, "spread": 2}
        summarize(10) -> {"count": 1, "total": 10, "mean": 10.0, "spread": 0}
        summarize() -> {"count": 0, "total": 0.0, "mean": 0.0, "spread": 0.0}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: summarize")


# ---------------------------------------------------------------------------
# Exercise 8 — **kwargs
# ---------------------------------------------------------------------------
def make_tag(name: str, **attributes: str) -> str:
    """Build an HTML opening tag from a tag name and keyword attributes.

    Attributes appear in alphabetical order by key so the output is
    predictable. Two naming fixes are applied to each key:
      * a single trailing underscore is dropped ("class_" -> "class"),
        because `class` is a reserved word in Python;
      * remaining underscores become dashes ("data_id" -> "data-id").

    Args:
        name: the tag name, e.g. "a" or "img".
        **attributes: any number of attribute=value keyword arguments.

    Returns:
        The tag as a string, e.g. '<a href="/home">'.

    Examples:
        make_tag("br") -> "<br>"
        make_tag("a", href="/home") -> '<a href="/home">'
        make_tag("p", class_="lead") -> '<p class="lead">'
        make_tag("img", src="cat.png", alt="a cat") -> '<img alt="a cat" src="cat.png">'
        make_tag("div", data_id="7") -> '<div data-id="7">'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: make_tag")


# ---------------------------------------------------------------------------
# Exercise 9 — a pure text function
# ---------------------------------------------------------------------------
def word_frequency(text: str) -> dict[str, int]:
    """Count how often each word appears in `text`.

    Words are separated by whitespace. Comparison is case-insensitive, so
    "The" and "the" are the same word. Strip the punctuation characters
    . , ! ? ; : " ' from both ends of each word. Words that are empty after
    stripping are ignored.

    Args:
        text: any string, possibly empty.

    Returns:
        A dict mapping each lowercased word to its count.

    Examples:
        word_frequency("the cat the dog") -> {"the": 2, "cat": 1, "dog": 1}
        word_frequency("Hi, hi! HI?") -> {"hi": 3}
        word_frequency("") -> {}
        word_frequency("a ... a") -> {"a": 2}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: word_frequency")


# ---------------------------------------------------------------------------
# Exercise 10 — decomposition under pressure (the hard one)
# ---------------------------------------------------------------------------
def format_receipt(items: list[tuple[str, int, float]], tax_rate: float = 0.07) -> str:
    """Return a printable receipt for `items` as a single multi-line string.

    Each item is a (name, quantity, unit_price) tuple. Build the string with
    "\\n" between lines and NO trailing newline. Use helper functions if it
    keeps things clear; only `format_receipt` is graded.

    Layout — every line is exactly 36 characters wide:

        item lines:  name.title() left-justified in 12
                     quantity right-justified in 3
                     " x "
                     unit price right-justified in 7, 2 decimals
                     " = "
                     line total right-justified in 8, 2 decimals
        separator:   36 dashes
        summary:     label left-justified in 28, amount right-justified in 8
                     with 2 decimals, for these three labels in this order:
                       "SUBTOTAL"
                       "TAX <rate>%"   rate as a percentage with 1 decimal
                       "TOTAL"

    Money rules: every line total, the subtotal, the tax and the total are
    each rounded to 2 decimals. tax = round(subtotal * tax_rate, 2) and
    total = round(subtotal + tax, 2). An empty item list returns the single
    line "(no items)".

    Args:
        items: list of (name, quantity, unit_price) tuples.
        tax_rate: tax as a fraction, e.g. 0.07 for 7%. Defaults to 0.07.

    Returns:
        The receipt as one string.

    Examples:
        format_receipt([]) -> "(no items)"

        format_receipt([("widget", 2, 9.99), ("bolt", 10, 0.5)]) ->
            'Widget        2 x    9.99 =    19.98\\n'
            'Bolt         10 x    0.50 =     5.00\\n'
            '------------------------------------\\n'
            'SUBTOTAL                       24.98\\n'
            'TAX 7.0%                        1.75\\n'
            'TOTAL                          26.73'

        format_receipt([("tea", 1, 3.0)], tax_rate=0.2) ->
            'Tea           1 x    3.00 =     3.00\\n'
            '------------------------------------\\n'
            'SUBTOTAL                        3.00\\n'
            'TAX 20.0%                       0.60\\n'
            'TOTAL                           3.60'
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: format_receipt")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(rectangle_area(3, 4))
    # print(greet("Ada"))
    # print(format_receipt([("widget", 2, 9.99), ("bolt", 10, 0.5)]))
    print("Run `python check.py day08` from the course root to grade your work.")
