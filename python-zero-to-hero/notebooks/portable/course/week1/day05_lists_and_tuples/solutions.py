"""Day 05 solutions — Lists and Tuples.

Reference implementations. Same names, same signatures, same docstrings as
exercises.py. Read these after you have made your own attempt.

They are deliberately plain: explicit loops, no cleverness, nothing from a later
day. Several of them exist to show the one-line difference between "changed the
caller's list" and "returned a new list".
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
    # why: items[-1] rather than items[len(items) - 1] — same answer, less to
    # read and nothing to get wrong. With one item, index 0 and index -1 are
    # the same slot, which gives the required "twice" behaviour for free.
    return (items[0], items[-1])


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
    # why: a slice is always a new list, so there is nothing to copy and no way
    # to disturb the argument. The empty case needs no special handling.
    return items[::2]


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
    # why: copy, then mutate the copy. `result += [item]` or `result.append(...)`
    # are both fine here because `result` is ours alone. Doing it in two named
    # steps makes the "the copy is the thing I change" decision visible.
    result = list(items)
    result.append(item)
    return result


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
    # why: sorted() returns a new list and leaves the argument alone, and a
    # slice past the end clips instead of raising — so short lists need no `if`.
    ordered = sorted(scores, reverse=True)
    return ordered[:3]


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
    lines = []
    # why: start=1 removes every `position + 1` from the body, and with it the
    # chance of getting one of them wrong.
    for position, item in enumerate(items, start=1):
        lines.append(f"{position}. {item}")
    return lines


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
    # why: zip is lazy — it produces pairs on demand — so list() is what turns
    # it into the list of tuples the caller asked for.
    return list(zip(names, scores))


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
    result = list(items)
    # why: the empty list has no index 0 to assign to, so it needs the guard.
    # A one-item list does not: index 0 and -1 are the same slot and swapping
    # it with itself is harmless.
    if len(result) > 0:
        result[0], result[-1] = result[-1], result[0]
    return result


# ---------------------------------------------------------------------------
# Exercise 8 — sorting with key=, using a named function
# ---------------------------------------------------------------------------
def length_then_alphabetical(word: str) -> tuple[int, str]:
    """Sort key: length first, then the word itself for ties."""
    # why: a tuple key compares left to right, so equal lengths fall through to
    # an ordinary alphabetical comparison of the words.
    return (len(word), word)


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
    # why: the function name is handed over with no brackets. Python calls it
    # once per word and sorts by the answers.
    return sorted(words, key=length_then_alphabetical)


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
    grid = []
    for row_index in range(rows):
        # why: `[0] * cols` is evaluated afresh on every pass, so every row is
        # a different object. Writing `[[0] * cols] * rows` evaluates the inner
        # list once and stores it `rows` times — one row wearing three hats.
        grid.append([0] * cols)
    return grid


# ---------------------------------------------------------------------------
# Exercise 10 — the whole day in one function (the hard one)
# ---------------------------------------------------------------------------
def rank_key(pair: tuple[str, int]) -> tuple[int, str]:
    """Sort key for a (name, score) pair: score descending, name ascending."""
    name, score = pair
    # why: negating the score makes a bigger score sort earlier, while the name
    # keeps its normal ascending order. `reverse=True` cannot do this, because
    # it would flip the name comparison as well.
    return (-score, name)


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
    # why: zip + list gives a list of pairs; sorted returns a new list, so
    # neither argument is touched at any point.
    pairs = list(zip(names, scores))
    ranked = sorted(pairs, key=rank_key)

    lines = []
    for position, pair in enumerate(ranked, start=1):
        # why: unpacking the pair gives the two parts readable names, which
        # beats pair[0] and pair[1] inside the f-string.
        name, score = pair
        lines.append(f"{position}. {name} - {score}")
    return lines


if __name__ == "__main__":
    print(top_three([70, 95, 88, 60, 92]))
    print(make_grid(2, 3))
    print(leaderboard(["Ada", "Grace", "Alan"], [88, 95, 79]))
