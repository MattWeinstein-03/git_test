"""Day 01 exercises — Getting Started.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

You have not been taught `def` yet — that is Day 8. For today, treat each
exercise as a *named recipe*: the line starting with `def` gives the recipe a
name and lists the values it is handed, and `return` is how the recipe hands
its answer back. Write your code indented under the `def` line, and finish with
`return <the answer>`.

Everything here is solvable with today's tools only: variables, `+` on strings,
`str()`, `int()`, `len()`, `type(x).__name__`, `print` with `sep`/`end`, and
`"\\n"` for a line break. You do not need anything from later days.

Grade your work from the course root:

    python check.py day01
    python check.py day01 -v      # show full failure detail
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Exercise 1 — build a string from a value
# ---------------------------------------------------------------------------
def greeting_line(name: str) -> str:
    """Return a greeting for `name`.

    Args:
        name: the person's name.

    Returns:
        The string "Hello, <name>!" — a comma and a space after "Hello",
        an exclamation mark at the end, and nothing else.

    Examples:
        greeting_line("Ada") -> "Hello, Ada!"
        greeting_line("Grace Hopper") -> "Hello, Grace Hopper!"
        greeting_line("") -> "Hello, !"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: greeting_line")


# ---------------------------------------------------------------------------
# Exercise 2 — join two values with a separator you supply
# ---------------------------------------------------------------------------
def full_name(first: str, last: str) -> str:
    """Return the two names joined by a single space.

    Nothing clever: no capitalisation, no stripping, no punctuation. Exactly
    one space between the two pieces.

    Args:
        first: the first name.
        last: the last name.

    Returns:
        "<first> <last>".

    Examples:
        full_name("Ada", "Lovelace") -> "Ada Lovelace"
        full_name("grace", "hopper") -> "grace hopper"
        full_name("Prince", "") -> "Prince "
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: full_name")


# ---------------------------------------------------------------------------
# Exercise 3 — ask Python what a value is
# ---------------------------------------------------------------------------
def type_name(value: object) -> str:
    """Return the name of `value`'s type, as a plain lowercase-ish word.

    Return the *name* only: "int", not "<class 'int'>". The tool for this is
    `type(value).__name__`, from section 8 of the lesson.

    Args:
        value: any value at all.

    Returns:
        The type's name as a string.

    Examples:
        type_name(42) -> "int"
        type_name(3.14) -> "float"
        type_name("hi") -> "str"
        type_name(True) -> "bool"
        type_name(None) -> "NoneType"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: type_name")


# ---------------------------------------------------------------------------
# Exercise 4 — the input() conversion habit
# ---------------------------------------------------------------------------
def to_whole_number(text: str) -> int:
    """Convert a string of digits into an `int`.

    This is the conversion you must remember every time you call `input()`,
    which always hands back text. `to_whole_number("36")` must return the
    number 36, not the string "36".

    Surrounding whitespace is fine — `int()` copes with it already, so you do
    not need to do anything special.

    Args:
        text: a string containing a whole number, e.g. "36" or "-4".

    Returns:
        The same number as an `int`.

    Examples:
        to_whole_number("36") -> 36
        to_whole_number("0") -> 0
        to_whole_number("-4") -> -4
        to_whole_number(" 7 ") -> 7
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: to_whole_number")


# ---------------------------------------------------------------------------
# Exercise 5 — mixing a value and its type into one sentence
# ---------------------------------------------------------------------------
def describe_value(value: object) -> str:
    """Return a one-line description of `value`: what it is and what type.

    The exact shape is "<value> is of type <typename>". Remember that `+` will
    not glue a number onto a string — `str()` is how you convert one.

    Args:
        value: any value at all.

    Returns:
        A string of the form "<value> is of type <typename>".

    Examples:
        describe_value(42) -> "42 is of type int"
        describe_value(3.5) -> "3.5 is of type float"
        describe_value("hi") -> "hi is of type str"
        describe_value(True) -> "True is of type bool"
        describe_value(None) -> "None is of type NoneType"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: describe_value")


# ---------------------------------------------------------------------------
# Exercise 6 — print with a custom separator
# ---------------------------------------------------------------------------
def print_row(left: str, middle: str, right: str) -> None:
    """Print the three values on ONE line, separated by " | ".

    This exercise is about printing, so there is nothing to return. Use a
    single `print` call with the `sep` keyword argument — do not build the
    string yourself with `+`.

    Args:
        left: the first value.
        middle: the second value.
        right: the third value.

    Returns:
        None. The output is the point.

    Examples:
        print_row("a", "b", "c") prints:
            a | b | c
        print_row("name", "city", "year") prints:
            name | city | year
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: print_row")


# ---------------------------------------------------------------------------
# Exercise 7 — two prints, one underline
# ---------------------------------------------------------------------------
def print_banner(text: str) -> None:
    """Print `text`, then a row of "-" exactly as long as `text` underneath it.

    Two lines of output. `len(text)` tells you how many dashes you need, and
    `"-" * n` builds a string of n dashes.

    Args:
        text: the heading to print.

    Returns:
        None.

    Examples:
        print_banner("Report") prints:
            Report
            ------
        print_banner("Day 01") prints:
            Day 01
            ------
        print_banner("") prints one empty line, then another empty line.
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: print_banner")


# ---------------------------------------------------------------------------
# Exercise 8 — a multi-line string
# ---------------------------------------------------------------------------
def profile_card(name: str, city: str, birth_year: int) -> str:
    """Return a three-line profile as a SINGLE string.

    Use "\\n" between the lines. There is no trailing newline at the end.
    `birth_year` arrives as a number, so it needs converting before it can be
    glued to text.

    Args:
        name: the person's name.
        city: where they live.
        birth_year: the year they were born, as an int.

    Returns:
        A string of exactly three lines:
            "Name: <name>"
            "City: <city>"
            "Born: <birth_year>"

    Examples:
        profile_card("Ada", "London", 1815) -> "Name: Ada\\nCity: London\\nBorn: 1815"
        profile_card("Grace", "New York", 1906) ->
            "Name: Grace\\nCity: New York\\nBorn: 1906"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: profile_card")


# ---------------------------------------------------------------------------
# Exercise 9 — the whole day in one function (the hard one)
# ---------------------------------------------------------------------------
def type_report(first: object, second: object, third: object) -> str:
    """Return a numbered report describing three values and their types.

    The report is a single string. Its shape, for the values 42, 3.5 and "hi":

        Type report
        -----------
        1. 42 is of type int
        2. 3.5 is of type float
        3. hi is of type str

    Rules:
        * The first line is exactly "Type report".
        * The second line is a row of "-" the same length as "Type report",
          which is 11 characters.
        * Then one line per value, numbered "1. ", "2. ", "3. ", each in the
          same "<value> is of type <typename>" shape as `describe_value`.
        * Lines are joined with "\\n" and there is NO trailing newline.

    Args:
        first: any value.
        second: any value.
        third: any value.

    Returns:
        The five-line report as one string.

    Examples:
        type_report(42, 3.5, "hi") ->
            "Type report\\n-----------\\n1. 42 is of type int\\n"
            "2. 3.5 is of type float\\n3. hi is of type str"

        type_report(True, None, 0) ->
            "Type report\\n-----------\\n1. True is of type bool\\n"
            "2. None is of type NoneType\\n3. 0 is of type int"
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: type_report")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(greeting_line("Ada"))
    # print(describe_value(3.5))
    # print(type_report(42, 3.5, "hi"))
    print("Run `python check.py day01` from the course root to grade your work.")
