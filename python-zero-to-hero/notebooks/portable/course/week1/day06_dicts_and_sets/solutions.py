"""Day 06 solutions — Dictionaries and Sets.

Reference implementations. Same names, same signatures, same docstrings as
exercises.py. Read these after you have made your own attempt.

They are deliberately plain: explicit loops, `.get` with a default, `setdefault`,
and nothing from a later day. Two of them are the counting and grouping patterns
with no decoration at all, because those two loops are the point of today.
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
    # why: .get with a default turns "the price, or nothing sensible" into an
    # expression. The four-line if/else version does the same job with more
    # places to make a mistake.
    return prices.get(item, 0.0)


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
    # why: copy first, then change the copy. Assignment on a dictionary both
    # adds and updates, so no `if` is needed to tell the two cases apart.
    result = dict(prices)
    result[item] = price
    return result


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
    counts = {}
    for item in items:
        # why: counts.get(item, 0) is "the count so far, or zero if this is the
        # first sighting". counts[item] + 1 would raise KeyError that first time.
        counts[item] = counts.get(item, 0) + 1
    return counts


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
    totals = {}
    for category, amount in records:
        # why: the counting pattern with `+ amount` in place of `+ 1`. Unpacking
        # in the for line gives both parts of the tuple readable names.
        totals[category] = totals.get(category, 0) + amount

    rounded = {}
    # why: round at the end, once per category, rather than after every
    # addition — rounding intermediate values would compound the error.
    for category, total in totals.items():
        rounded[category] = round(total, 2)
    return rounded


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
    groups = {}
    for word in words:
        first_letter = word[0]
        # why: setdefault returns the list that is now stored under the key —
        # the existing one, or the empty one it just inserted — and appending
        # to it appends to the list inside the dictionary, because the lookup
        # gives the actual object rather than a copy.
        groups.setdefault(first_letter, []).append(word)
    return groups


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
    # why: max() over an empty collection raises, so the empty case is handled
    # first and separately. Real data is empty more often than you expect.
    if len(counts) == 0:
        return ""
    # why: max walks the KEYS and judges each one by counts.get(key). No
    # brackets on counts.get — max is being handed the method to call itself.
    return max(counts, key=counts.get)


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
    # why: the longhand is spelled out here because it is the version that
    # generalises — change the condition and it becomes "first per category".
    # `list(dict.fromkeys(items))` is the one-line equivalent, and a set is
    # used for `seen` because membership tests on it do not slow down.
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


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
    old_tags = set(before)
    new_tags = set(after)
    # why: sorted() on each result, because a set has no order and an
    # unpredictable answer is untestable and unreadable. sorted also converts
    # the sets to the lists the caller asked for.
    return {
        "added": sorted(new_tags - old_tags),
        "removed": sorted(old_tags - new_tags),
        "kept": sorted(new_tags & old_tags),
    }


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
    averages = {}
    # why: .items() gives the name and the list together, which is what the
    # calculation needs. Nothing here writes to `scores` or to the lists in it.
    for name, student_scores in scores.items():
        if len(student_scores) == 0:
            averages[name] = 0.0
        else:
            averages[name] = round(sum(student_scores) / len(student_scores), 2)
    return averages


# ---------------------------------------------------------------------------
# Exercise 10 — the whole day in one function (the hard one)
# ---------------------------------------------------------------------------
def by_count_then_word(pair: tuple[str, int]) -> tuple[int, str]:
    """Sort key for a (word, count) pair: count descending, word ascending."""
    word, count = pair
    # why: negating the count sorts it downwards while the word keeps its
    # normal upward order. reverse=True would flip both parts of the key.
    return (-count, word)


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
    counts = {}
    for piece in text.split():
        # why: strip() takes a set of CHARACTERS, not a substring, so one call
        # removes any run of punctuation from either end.
        word = piece.lower().strip(".,!?;:")
        if len(word) > 0:
            counts[word] = counts.get(word, 0) + 1

    # why: sorting .items() rather than the keys means the counts travel with
    # the words, so the result is already the list of pairs the caller wants.
    ranked = sorted(counts.items(), key=by_count_then_word)
    # why: a slice past the end clips instead of raising, so a top_n bigger
    # than the data needs no special case, and top_n of 0 gives [].
    return ranked[:top_n]


if __name__ == "__main__":
    print(count_items(["a", "b", "a"]))
    print(group_by_first_letter(["apple", "avocado", "fig"]))
    print(word_report("the cat sat. The cat, the end!", 2))
