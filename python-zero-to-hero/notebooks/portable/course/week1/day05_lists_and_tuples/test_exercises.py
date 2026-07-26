"""Day 05 graded checks — Lists and Tuples.

Several of these do the same thing twice: check the answer, then check that the
argument you were given is exactly as you found it. Section 13 of the lesson is
why. A function that quietly rewrites its caller's data is a bug even when the
value it returns is correct.
"""


# --- Exercise 1: first_and_last -------------------------------------------
def test_first_and_last_three_items(day):
    assert day.first_and_last(["a", "b", "c"]) == ("a", "c")


def test_first_and_last_single_item_appears_twice(day):
    got = day.first_and_last(["only"])
    assert got == ("only", "only"), f"one item is both first and last, got {got!r}"


def test_first_and_last_returns_a_tuple(day):
    got = day.first_and_last(["x", "y"])
    assert isinstance(got, tuple), f"expected a tuple, got {type(got).__name__}"
    assert got == ("x", "y")


# --- Exercise 2: every_other ----------------------------------------------
def test_every_other_odd_length(day):
    assert day.every_other([1, 2, 3, 4, 5]) == [1, 3, 5]


def test_every_other_even_length(day):
    assert day.every_other([10, 20, 30, 40]) == [10, 30]


def test_every_other_single_item(day):
    assert day.every_other([7]) == [7]


def test_every_other_empty(day):
    assert day.every_other([]) == []


def test_every_other_does_not_modify_the_argument(day):
    numbers = [1, 2, 3, 4]
    day.every_other(numbers)
    assert numbers == [1, 2, 3, 4], f"the argument was changed: {numbers!r}"


# --- Exercise 3: add_item -------------------------------------------------
def test_add_item_appends_to_the_end(day):
    assert day.add_item(["a", "b"], "c") == ["a", "b", "c"]


def test_add_item_onto_an_empty_list(day):
    assert day.add_item([], "first") == ["first"]


def test_add_item_does_not_modify_the_argument(day):
    original = ["a"]
    day.add_item(original, "b")
    assert original == ["a"], (
        f"add_item must return a NEW list and leave its argument alone, "
        f"but the argument is now {original!r} — you used items.append(item) "
        f"on the caller's list instead of on a copy"
    )


def test_add_item_returns_a_different_object(day):
    original = ["a"]
    result = day.add_item(original, "b")
    assert result is not original, "the result must be a new list, not the argument"


# --- Exercise 4: top_three ------------------------------------------------
def test_top_three_picks_the_highest_three_in_order(day):
    got = day.top_three([70, 95, 88, 60, 92])
    assert got == [95, 92, 88], f"highest first, got {got!r}"


def test_top_three_with_fewer_than_three(day):
    assert day.top_three([1, 2]) == [2, 1]


def test_top_three_empty(day):
    assert day.top_three([]) == []


def test_top_three_keeps_duplicates(day):
    assert day.top_three([5, 5, 5, 5]) == [5, 5, 5]


def test_top_three_does_not_modify_the_argument(day):
    scores = [70, 95, 88, 60, 92]
    day.top_three(scores)
    assert scores == [70, 95, 88, 60, 92], (
        f"the argument was reordered: {scores!r} — use sorted(scores) rather "
        f"than scores.sort()"
    )


# --- Exercise 5: numbered_list --------------------------------------------
def test_numbered_list_counts_from_one(day):
    got = day.numbered_list(["Ada", "Grace"])
    assert got == ["1. Ada", "2. Grace"], f"got {got!r}"


def test_numbered_list_single_item(day):
    assert day.numbered_list(["only"]) == ["1. only"]


def test_numbered_list_empty(day):
    assert day.numbered_list([]) == []


def test_numbered_list_keeps_the_original_order(day):
    got = day.numbered_list(["c", "a", "b"])
    assert got == ["1. c", "2. a", "3. b"], f"do not sort the items, got {got!r}"


# --- Exercise 6: pair_up --------------------------------------------------
def test_pair_up_equal_lengths(day):
    got = day.pair_up(["Ada", "Alan"], [88, 79])
    assert got == [("Ada", 88), ("Alan", 79)], f"got {got!r}"


def test_pair_up_stops_at_the_shorter_list(day):
    assert day.pair_up(["Ada"], [88, 79, 70]) == [("Ada", 88)]


def test_pair_up_empty_names(day):
    assert day.pair_up([], [1, 2]) == []


def test_pair_up_returns_a_list_of_tuples(day):
    got = day.pair_up(["Ada"], [88])
    assert isinstance(got, list), f"expected a list, got {type(got).__name__}"
    assert isinstance(got[0], tuple), f"expected tuples inside, got {got!r}"


# --- Exercise 7: swap_ends ------------------------------------------------
def test_swap_ends_three_items(day):
    assert day.swap_ends([1, 2, 3]) == [3, 2, 1]


def test_swap_ends_two_items(day):
    assert day.swap_ends([1, 2]) == [2, 1]


def test_swap_ends_single_item(day):
    assert day.swap_ends([9]) == [9]


def test_swap_ends_empty(day):
    got = day.swap_ends([])
    assert got == [], f"an empty list has no ends to swap, got {got!r}"


def test_swap_ends_does_not_modify_the_argument(day):
    items = [1, 2, 3, 4]
    result = day.swap_ends(items)
    assert items == [1, 2, 3, 4], (
        f"the argument was changed: {items!r} — copy it first, then swap on "
        f"the copy"
    )
    assert result is not items, "the result must be a new list, not the argument"


# --- Exercise 8: sort_by_length -------------------------------------------
def test_sort_by_length_shortest_first(day):
    got = day.sort_by_length(["pear", "fig", "plum"])
    assert got == ["fig", "pear", "plum"], f"got {got!r}"


def test_sort_by_length_breaks_ties_alphabetically(day):
    got = day.sort_by_length(["bb", "a", "cc", "aa"])
    assert got == ["a", "aa", "bb", "cc"], (
        f"equal lengths sort alphabetically, got {got!r}"
    )


def test_sort_by_length_mixed_lengths(day):
    got = day.sort_by_length(["plum", "fig", "kiwi", "date", "pear"])
    assert got == ["fig", "date", "kiwi", "pear", "plum"], f"got {got!r}"


def test_sort_by_length_empty(day):
    assert day.sort_by_length([]) == []


def test_sort_by_length_does_not_modify_the_argument(day):
    words = ["pear", "fig", "plum"]
    day.sort_by_length(words)
    assert words == ["pear", "fig", "plum"], (
        f"the argument was reordered: {words!r} — sorted() returns a new list, "
        f".sort() rearranges the one you were given"
    )


# --- Exercise 9: make_grid ------------------------------------------------
def test_make_grid_shape(day):
    got = day.make_grid(2, 3)
    assert got == [[0, 0, 0], [0, 0, 0]], f"got {got!r}"


def test_make_grid_one_by_one(day):
    assert day.make_grid(1, 1) == [[0]]


def test_make_grid_no_rows(day):
    assert day.make_grid(0, 5) == []


def test_make_grid_empty_rows(day):
    assert day.make_grid(2, 0) == [[], []]


def test_make_grid_rows_are_independent(day):
    grid = day.make_grid(3, 3)
    grid[0][0] = 9
    assert grid == [[9, 0, 0], [0, 0, 0], [0, 0, 0]], (
        f"changing one cell changed a whole column: {grid!r} — the rows are "
        f"the same list stored three times, which is what [[0] * 3] * 3 does. "
        f"Append a fresh [0] * cols on each pass of a loop instead"
    )


def test_make_grid_rows_are_different_objects(day):
    grid = day.make_grid(2, 2)
    assert grid[0] is not grid[1], "each row must be its own list object"


# --- Exercise 10: leaderboard ---------------------------------------------
def test_leaderboard_orders_by_score_descending(day):
    got = day.leaderboard(["Ada", "Grace", "Alan"], [88, 95, 79])
    want = ["1. Grace - 95", "2. Ada - 88", "3. Alan - 79"]
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_leaderboard_breaks_ties_alphabetically(day):
    got = day.leaderboard(["Zoe", "Ada", "Bob"], [70, 70, 90])
    want = ["1. Bob - 90", "2. Ada - 70", "3. Zoe - 70"]
    assert got == want, (
        f"tied scores sort by name in NORMAL alphabetical order\n"
        f"got  {got!r}\nwant {want!r}"
    )


def test_leaderboard_empty(day):
    assert day.leaderboard([], []) == []


def test_leaderboard_single_entry(day):
    assert day.leaderboard(["Ada"], [100]) == ["1. Ada - 100"]


def test_leaderboard_does_not_modify_its_arguments(day):
    names = ["Ada", "Grace", "Alan"]
    scores = [88, 95, 79]
    day.leaderboard(names, scores)
    assert names == ["Ada", "Grace", "Alan"], f"names was changed: {names!r}"
    assert scores == [88, 95, 79], f"scores was changed: {scores!r}"
