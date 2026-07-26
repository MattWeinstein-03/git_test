"""Day 05 exercises — Lists and Tuples.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

`def` is still just "a named recipe" until Day 8. Write your code indented under
the `def` line and finish with `return <the answer>`. The `list[int]` and
`tuple[str, int]` notes after the colons are type hints — they document what goes
in and what comes out, and Day 8 explains them properly.

Everything here is solvable with Days 1-5: arithmetic, strings, `if`, loops,
lists, tuples, `sorted` with `key=`, `enumerate`, `zip`, and `len/sum/min/max`.
You do not need dictionaries (Day 6) or comprehensions (Day 15) anywhere.

Read the docstrings closely. Several exercises say **the argument must not be
modified**, and the tests check the argument after the call. That is section 13
of the lesson, and getting it wrong here is much cheaper than getting it wrong
at work.

Grade your work from the course root:

    python check.py day05
    python check.py day05 -v      # show full failure detail
"""


# ---------------------------------------------------------------------------
# Exercise 1 — indexing, and building a tuple
# ---------------------------------------------------------------------------
def first_and_last(items: list[str]) -> tuple[str, str]:
    """Return a 2-tuple holding the first and the last item of `items`.

    Use index 0 and index -1. Assume the list has at least one item; a
    one-item list gives that item twice.

    Args:
        items: a list of at least one string.

    Returns:
        A tuple `(first_item, last_item)`.

    Examples:
        first_and_last(["a", "b", "c"]) -> ("a", "c")
        first_and_last(["only"]) -> ("only", "only")
        first_and_last(["x", "y"]) -> ("x", "y")
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: first_and_last")


# ---------------------------------------------------------------------------
# Exercise 2 — slicing with a step
# ---------------------------------------------------------------------------
def every_other(items: list[int]) -> list[int]:
    """Return a new list holding every second item, starting with the first.

    One slice does the whole job. An empty list gives an empty list.

    Args:
        items: a list of numbers.

    Returns:
        A new list: the items at index 0, 2, 4, and so on.

    Examples:
        every_other([1, 2, 3, 4, 5]) -> [1, 3, 5]
        every_other([10, 20, 30, 40]) -> [10, 30]
        every_other([7]) -> [7]
        every_other([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: every_other")


# ---------------------------------------------------------------------------
# Exercise 3 — return a new list, leave the argument alone
# ---------------------------------------------------------------------------
def add_item(items: list[str], item: str) -> list[str]:
    """Return a new list with `item` added at the end.

    **`items` must not be modified.** `items.append(item)` changes the caller's
    list and returns `None`, which fails this exercise twice over. Copy first
    (`list(items)`, `items.copy()` or `items[:]`), then append to the copy — or
    build the answer with `+`.

    Args:
        items: a list of strings. Left exactly as it was found.
        item: the string to add.

    Returns:
        A new list, one item longer than `items`.

    Examples:
        add_item(["a", "b"], "c") -> ["a", "b", "c"]
        add_item([], "first") -> ["first"]

        original = ["a"]
        add_item(original, "b")     # -> ["a", "b"]
        original                    # still ["a"] — unchanged
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: add_item")


# ---------------------------------------------------------------------------
# Exercise 4 — sorted versus sort
# ---------------------------------------------------------------------------
def top_three(scores: list[int]) -> list[int]:
    """Return the three highest scores, highest first.

    Fewer than three scores means you return however many there are.

    **`scores` must not be modified**, so this is a job for `sorted(...)` and
    not for `scores.sort()`. Remember what `.sort()` gives back.

    Args:
        scores: a list of numbers. Left exactly as it was found.

    Returns:
        A new list of at most three numbers, in descending order.

    Examples:
        top_three([70, 95, 88, 60, 92]) -> [95, 92, 88]
        top_three([1, 2]) -> [2, 1]
        top_three([]) -> []
        top_three([5, 5, 5, 5]) -> [5, 5, 5]
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: top_three")


# ---------------------------------------------------------------------------
# Exercise 5 — enumerate with start=1
# ---------------------------------------------------------------------------
def numbered_list(items: list[str]) -> list[str]:
    """Return the items as numbered strings, counting from 1.

    Each result line is the number, a full stop, a space, then the item:
    `"1. Ada"`. Use `enumerate(items, start=1)` rather than a counter you
    increment yourself.

    Args:
        items: a list of strings.

    Returns:
        A new list of strings, the same length as `items`.

    Examples:
        numbered_list(["Ada", "Grace"]) -> ["1. Ada", "2. Grace"]
        numbered_list(["only"]) -> ["1. only"]
        numbered_list([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: numbered_list")


# ---------------------------------------------------------------------------
# Exercise 6 — zip
# ---------------------------------------------------------------------------
def pair_up(names: list[str], scores: list[int]) -> list[tuple[str, int]]:
    """Pair each name with the score in the same position.

    `zip` does the pairing. Wrap the result in `list(...)` so you return a real
    list of tuples. Where the two lists differ in length, `zip` stops at the
    shorter one and the extra items are dropped — that is the behaviour this
    exercise wants.

    Args:
        names: a list of names.
        scores: a list of numbers.

    Returns:
        A new list of `(name, score)` tuples.

    Examples:
        pair_up(["Ada", "Alan"], [88, 79]) -> [("Ada", 88), ("Alan", 79)]
        pair_up(["Ada"], [88, 79, 70]) -> [("Ada", 88)]
        pair_up([], [1, 2]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: pair_up")


# ---------------------------------------------------------------------------
# Exercise 7 — the swap idiom, without touching the argument
# ---------------------------------------------------------------------------
def swap_ends(items: list[int]) -> list[int]:
    """Return a new list with the first and last items exchanged.

    A list of 0 or 1 items comes back with the same contents (still a *new*
    list, not the one you were given).

    **`items` must not be modified.** Copy it, then use the swap idiom on the
    copy: `copy[0], copy[-1] = copy[-1], copy[0]`.

    Args:
        items: a list of numbers. Left exactly as it was found.

    Returns:
        A new list, the same length as `items`.

    Examples:
        swap_ends([1, 2, 3]) -> [3, 2, 1]
        swap_ends([1, 2]) -> [2, 1]
        swap_ends([9]) -> [9]
        swap_ends([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: swap_ends")


# ---------------------------------------------------------------------------
# Exercise 8 — sorting with key=, using a named function
# ---------------------------------------------------------------------------
def sort_by_length(words: list[str]) -> list[str]:
    """Return the words sorted shortest first, ties broken alphabetically.

    Write a small named function above this one that takes a word and returns
    the tuple `(len(word), word)`, then pass it as `key=`. Sorting by a tuple
    compares the first part and only looks at the second part when the first
    parts are equal — lesson section 8.3.

    **`words` must not be modified.**

    Args:
        words: a list of strings. Left exactly as it was found.

    Returns:
        A new list holding the same words in the new order.

    Examples:
        sort_by_length(["pear", "fig", "plum"]) -> ["fig", "pear", "plum"]
        sort_by_length(["bb", "a", "cc", "aa"]) -> ["a", "aa", "bb", "cc"]
        sort_by_length([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: sort_by_length")


# ---------------------------------------------------------------------------
# Exercise 9 — nested lists, and the shared-row trap
# ---------------------------------------------------------------------------
def make_grid(rows: int, cols: int) -> list[list[int]]:
    """Build a grid of zeros: a list of `rows` lists, each `cols` items long.

    Every row must be an **independent** list. `[[0] * cols] * rows` is the
    wrong answer — it stores one row several times, so changing a single cell
    appears to change a whole column (lesson section 13.2). Build it with a
    loop that appends a fresh `[0] * cols` on every pass.

    `rows` of 0 gives an empty list. `cols` of 0 gives that many empty rows.

    Args:
        rows: how many rows, 0 or more.
        cols: how many items in each row, 0 or more.

    Returns:
        A new list of `rows` new lists of `cols` zeros.

    Examples:
        make_grid(2, 3) -> [[0, 0, 0], [0, 0, 0]]
        make_grid(1, 1) -> [[0]]
        make_grid(0, 5) -> []
        make_grid(2, 0) -> [[], []]

        grid = make_grid(2, 2)
        grid[0][0] = 9
        grid                    # [[9, 0], [0, 0]] — only ONE cell changed
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: make_grid")


# ---------------------------------------------------------------------------
# Exercise 10 — the whole day in one function (the hard one)
# ---------------------------------------------------------------------------
def leaderboard(names: list[str], scores: list[int]) -> list[str]:
    """Return a numbered leaderboard: highest score first, ties alphabetical.

    Steps:
        1. Pair each name with its score (`zip`).
        2. Sort the pairs by score, highest first, breaking ties by name in
           normal alphabetical order.
        3. Number the sorted pairs from 1 and format each one as
           `"1. Grace - 95"` — rank, full stop, space, name, space, hyphen,
           space, score.

    Step 2 is the interesting one. `reverse=True` cannot help you here: it
    would reverse the *whole* key, putting tied names in backwards alphabetical
    order. Write a named key function that returns `(-score, name)` instead —
    negating the score sorts it descending while the name still sorts ascending.

    **Neither argument may be modified.**

    Args:
        names: a list of names.
        scores: a list of numbers, the same length as `names`.

    Returns:
        A new list of formatted strings, one per pair.

    Examples:
        leaderboard(["Ada", "Grace", "Alan"], [88, 95, 79]) ->
            ["1. Grace - 95", "2. Ada - 88", "3. Alan - 79"]

        leaderboard(["Zoe", "Ada", "Bob"], [70, 70, 90]) ->
            ["1. Bob - 90", "2. Ada - 70", "3. Zoe - 70"]

        leaderboard([], []) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: leaderboard")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(top_three([70, 95, 88, 60, 92]))
    # print(make_grid(2, 3))
    # print(leaderboard(["Ada", "Grace", "Alan"], [88, 95, 79]))
    print("Run `python check.py day05` from the course root to grade your work.")
