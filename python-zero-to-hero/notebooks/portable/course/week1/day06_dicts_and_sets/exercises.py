"""Day 06 exercises — Dictionaries and Sets.

Fill in each function body. Delete the `raise NotImplementedError(...)` line and
write real code. Work top to bottom: they get harder.

`def` is still just "a named recipe" until Day 8. Write your code indented under
the `def` line and finish with `return <the answer>`.

Everything here is solvable with Days 1-6: strings, `if`, loops, lists, tuples,
`sorted` with `key=`, dictionaries and sets. You do not need comprehensions
(Day 15), `collections.Counter` (Day 17), or anything from outside the
built-in language.

Two exercises say **the argument must not be modified**, and the tests check the
argument after the call. That is Day 05 section 13, and it applies to
dictionaries exactly as it did to lists.

Grade your work from the course root:

    python check.py day06
    python check.py day06 -v      # show full failure detail
"""


# ---------------------------------------------------------------------------
# Exercise 1 — .get with a default
# ---------------------------------------------------------------------------
def lookup_price(prices: dict[str, float], item: str) -> float:
    """Return the price of `item`, or 0.0 when the item is not priced.

    Use `.get` with a default rather than `prices[item]`, which would raise
    `KeyError` for an unknown item.

    Args:
        prices: item name -> price.
        item: the name to look up.

    Returns:
        The price, or 0.0 if `item` is not a key.

    Examples:
        lookup_price({"tea": 2.5, "jam": 3.0}, "tea") -> 2.5
        lookup_price({"tea": 2.5}, "coffee") -> 0.0
        lookup_price({}, "anything") -> 0.0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 1: lookup_price")


# ---------------------------------------------------------------------------
# Exercise 2 — return a new dictionary, leave the argument alone
# ---------------------------------------------------------------------------
def add_or_update(prices: dict[str, float], item: str, price: float) -> dict[str, float]:
    """Return a new dictionary with `item` set to `price`.

    If `item` is already a key its price is replaced; if it is not, it is added.
    Either way the answer is a **new** dictionary.

    **`prices` must not be modified.** Copy it first with `dict(prices)` or
    `prices.copy()`, then set the key on the copy.

    Args:
        prices: item name -> price. Left exactly as it was found.
        item: the name to set.
        price: the price to set it to.

    Returns:
        A new dictionary.

    Examples:
        add_or_update({"tea": 2.5}, "jam", 3.0) -> {"tea": 2.5, "jam": 3.0}
        add_or_update({"tea": 2.5}, "tea", 9.0) -> {"tea": 9.0}

        original = {"tea": 2.5}
        add_or_update(original, "jam", 3.0)     # -> {"tea": 2.5, "jam": 3.0}
        original                                # still {"tea": 2.5}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 2: add_or_update")


# ---------------------------------------------------------------------------
# Exercise 3 — the counting pattern
# ---------------------------------------------------------------------------
def count_items(items: list[str]) -> dict[str, int]:
    """Count how many times each item appears.

    This is lesson section 8. The loop body is one line:
    `counts[item] = counts.get(item, 0) + 1`.

    Args:
        items: a list of strings, possibly with repeats.

    Returns:
        A dictionary mapping each distinct item to its count.

    Examples:
        count_items(["a", "b", "a"]) -> {"a": 2, "b": 1}
        count_items(["x"]) -> {"x": 1}
        count_items([]) -> {}
        count_items(["a", "a", "a"]) -> {"a": 3}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 3: count_items")


# ---------------------------------------------------------------------------
# Exercise 4 — accumulating into a dictionary
# ---------------------------------------------------------------------------
def total_by_category(records: list[tuple[str, float]]) -> dict[str, float]:
    """Total the amounts for each category.

    Each record is a `(category, amount)` tuple. Unpack it in the `for` line —
    `for category, amount in records:` — and accumulate with the counting
    pattern, adding `amount` instead of `1`.

    Round each total to 2 decimal places, so that adding floats does not leave
    you with `24.500000000000004` (Day 02 section 3).

    Args:
        records: a list of `(category, amount)` tuples.

    Returns:
        A dictionary mapping each category to its rounded total.

    Examples:
        total_by_category([("food", 12.5), ("tools", 40.0), ("food", 3.25)]) ->
            {"food": 15.75, "tools": 40.0}
        total_by_category([("a", 0.1), ("a", 0.2)]) -> {"a": 0.3}
        total_by_category([]) -> {}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 4: total_by_category")


# ---------------------------------------------------------------------------
# Exercise 5 — the grouping pattern with setdefault
# ---------------------------------------------------------------------------
def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:
    """Group words by their first letter, keeping the original order.

    This is lesson section 9. The loop body is one line:
    `groups.setdefault(word[0], []).append(word)`.

    Assume every word has at least one character. Do not change the case of
    anything: `"Fig"` is grouped under `"F"`.

    Args:
        words: a list of non-empty strings.

    Returns:
        A dictionary mapping each first letter to the list of words that start
        with it, in the order they appeared.

    Examples:
        group_by_first_letter(["apple", "avocado", "fig"]) ->
            {"a": ["apple", "avocado"], "f": ["fig"]}
        group_by_first_letter(["pear", "plum", "fig"]) ->
            {"p": ["pear", "plum"], "f": ["fig"]}
        group_by_first_letter([]) -> {}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 5: group_by_first_letter")


# ---------------------------------------------------------------------------
# Exercise 6 — max with key=
# ---------------------------------------------------------------------------
def most_common(counts: dict[str, int]) -> str:
    """Return the key with the largest value.

    `max(counts, key=counts.get)` is the whole answer — lesson section 10 —
    except for one case it cannot handle: an empty dictionary, which raises
    `ValueError`. Return `""` for that, so guard it with `len(counts)` first.

    When two keys tie, return whichever `max` picks (the first one it meets,
    which is the first inserted).

    Args:
        counts: a dictionary of names to numbers.

    Returns:
        The key with the highest value, or "" when there are no keys.

    Examples:
        most_common({"apple": 3, "fig": 2}) -> "apple"
        most_common({"a": 1, "b": 9, "c": 4}) -> "b"
        most_common({"only": 0}) -> "only"
        most_common({}) -> ""
    """
    # TODO: your code here
    raise NotImplementedError("exercise 6: most_common")


# ---------------------------------------------------------------------------
# Exercise 7 — deduplicate, keeping order
# ---------------------------------------------------------------------------
def unique_in_order(items: list[str]) -> list[str]:
    """Return the items with duplicates removed, in their original order.

    Only the **first** appearance of each item is kept. `set(items)` removes
    the duplicates but loses the order, so it is not the answer on its own.
    Either use `list(dict.fromkeys(items))` (lesson section 12) or write the
    longhand version with a `seen` set and a result list.

    Args:
        items: a list of strings, possibly with repeats.

    Returns:
        A new list of the distinct items, first-seen order preserved.

    Examples:
        unique_in_order(["b", "a", "b", "c", "a"]) -> ["b", "a", "c"]
        unique_in_order(["x", "x", "x"]) -> ["x"]
        unique_in_order([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: unique_in_order")


# ---------------------------------------------------------------------------
# Exercise 8 — set operations
# ---------------------------------------------------------------------------
def compare_tags(before: list[str], after: list[str]) -> dict[str, list[str]]:
    """Describe how a collection of tags changed, using set operations.

    Build sets from the two lists, then answer three questions with one
    operation each:

        "added"   — in `after` but not `before`      (difference)
        "removed" — in `before` but not `after`      (difference, other way)
        "kept"    — in both                          (intersection)

    Each of the three lists must be **sorted**, because a set has no order and
    a caller needs a predictable answer. Duplicates inside either input
    disappear, which is what building a set does for you.

    Args:
        before: the tags as they were.
        after: the tags as they are now.

    Returns:
        A dictionary with exactly the keys "added", "removed" and "kept", each
        holding a sorted list.

    Examples:
        compare_tags(["a", "b"], ["b", "c"]) ->
            {"added": ["c"], "removed": ["a"], "kept": ["b"]}
        compare_tags(["x"], ["x"]) ->
            {"added": [], "removed": [], "kept": ["x"]}
        compare_tags([], ["new", "new"]) ->
            {"added": ["new"], "removed": [], "kept": []}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: compare_tags")


# ---------------------------------------------------------------------------
# Exercise 9 — a dictionary of lists
# ---------------------------------------------------------------------------
def average_scores(scores: dict[str, list[int]]) -> dict[str, float]:
    """Turn a dictionary of score lists into a dictionary of averages.

    Loop with `.items()`, so you have the name and the list of scores together.
    Round each average to 2 decimal places. A student with an **empty** list
    of scores gets `0.0` — dividing by `len([])` would raise
    `ZeroDivisionError`, so check the length first.

    **`scores` must not be modified**, and neither must the lists inside it.

    Args:
        scores: student name -> list of that student's scores.

    Returns:
        A new dictionary mapping each name to their average, rounded to 2dp.

    Examples:
        average_scores({"ada": [90, 80], "alan": [70]}) ->
            {"ada": 85.0, "alan": 70.0}
        average_scores({"grace": [1, 2, 2]}) -> {"grace": 1.67}
        average_scores({"new": []}) -> {"new": 0.0}
        average_scores({}) -> {}
    """
    # TODO: your code here
    raise NotImplementedError("exercise 9: average_scores")


# ---------------------------------------------------------------------------
# Exercise 10 — the whole day in one function (the hard one)
# ---------------------------------------------------------------------------
def word_report(text: str, top_n: int) -> list[tuple[str, int]]:
    """Return the `top_n` most frequent words in `text` as (word, count) pairs.

    The steps:
        1. Split `text` on whitespace.
        2. Normalise each piece: lower-case it, then strip the characters
           `.,!?;:` from both ends with `.strip(".,!?;:")` (Day 02 section 8.1).
           Skip any piece that is empty after stripping.
        3. Count the normalised words (lesson section 8).
        4. Sort the counted words: highest count first, and for equal counts,
           alphabetically. Use a named key function that returns
           `(-count, word)` — `reverse=True` cannot do this, because it would
           put tied words in backwards alphabetical order.
        5. Return the first `top_n` pairs as a list of `(word, count)` tuples.

    A `top_n` larger than the number of distinct words returns all of them. A
    `top_n` of 0 returns an empty list.

    Args:
        text: any text.
        top_n: how many pairs to return, 0 or more.

    Returns:
        A list of at most `top_n` `(word, count)` tuples, most frequent first.

    Examples:
        word_report("the cat sat. The cat, the end!", 2) ->
            [("the", 3), ("cat", 2)]

        word_report("b a b a c", 3) ->
            [("a", 2), ("b", 2), ("c", 1)]
            # a and b tie on 2, so they are alphabetical

        word_report("hello", 5) -> [("hello", 1)]
        word_report("", 3) -> []
        word_report("anything at all", 0) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 10: word_report")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(count_items(["a", "b", "a"]))
    # print(group_by_first_letter(["apple", "avocado", "fig"]))
    # print(word_report("the cat sat. The cat, the end!", 2))
    print("Run `python check.py day06` from the course root to grade your work.")
