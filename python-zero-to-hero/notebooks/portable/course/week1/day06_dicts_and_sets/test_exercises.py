"""Day 06 graded checks — Dictionaries and Sets.

Some of these check the answer and then check that the dictionary you were given
is exactly as you found it. Day 05 section 13 is why: a dictionary is mutable,
and a function that quietly rewrites its caller's data is a bug even when the
value it returns is right.
"""


# --- Exercise 1: lookup_price ---------------------------------------------
def test_lookup_price_known_item(day):
    assert day.lookup_price({"tea": 2.5, "jam": 3.0}, "tea") == 2.5


def test_lookup_price_unknown_item_is_zero(day):
    got = day.lookup_price({"tea": 2.5}, "coffee")
    assert got == 0.0, f"an unknown item costs 0.0, not {got!r}"


def test_lookup_price_empty_dictionary(day):
    assert day.lookup_price({}, "anything") == 0.0


def test_lookup_price_does_not_add_the_missing_key(day):
    prices = {"tea": 2.5}
    day.lookup_price(prices, "coffee")
    assert prices == {"tea": 2.5}, (
        f"looking up a price must not create the key: {prices!r}"
    )


# --- Exercise 2: add_or_update --------------------------------------------
def test_add_or_update_adds_a_new_key(day):
    got = day.add_or_update({"tea": 2.5}, "jam", 3.0)
    assert got == {"tea": 2.5, "jam": 3.0}, f"got {got!r}"


def test_add_or_update_replaces_an_existing_key(day):
    got = day.add_or_update({"tea": 2.5}, "tea", 9.0)
    assert got == {"tea": 9.0}, f"got {got!r}"


def test_add_or_update_does_not_modify_the_argument(day):
    original = {"tea": 2.5}
    day.add_or_update(original, "jam", 3.0)
    assert original == {"tea": 2.5}, (
        f"add_or_update must return a NEW dictionary and leave its argument "
        f"alone, but the argument is now {original!r} — copy it with "
        f"dict(prices) before setting the key"
    )


def test_add_or_update_returns_a_different_object(day):
    original = {"tea": 2.5}
    result = day.add_or_update(original, "jam", 3.0)
    assert result is not original, "the result must be a new dictionary"


# --- Exercise 3: count_items ---------------------------------------------
def test_count_items_counts_repeats(day):
    got = day.count_items(["a", "b", "a"])
    assert got == {"a": 2, "b": 1}, f"got {got!r}"


def test_count_items_single_item(day):
    assert day.count_items(["x"]) == {"x": 1}


def test_count_items_empty(day):
    assert day.count_items([]) == {}


def test_count_items_all_the_same(day):
    assert day.count_items(["a", "a", "a"]) == {"a": 3}


def test_count_items_totals_match_the_input_length(day):
    items = ["a", "b", "a", "c", "b", "a"]
    got = day.count_items(items)
    assert sum(got.values()) == len(items), f"counts do not add up: {got!r}"
    assert got == {"a": 3, "b": 2, "c": 1}, f"got {got!r}"


# --- Exercise 4: total_by_category ---------------------------------------
def test_total_by_category_sums_each_category(day):
    got = day.total_by_category([("food", 12.5), ("tools", 40.0), ("food", 3.25)])
    assert got == {"food": 15.75, "tools": 40.0}, f"got {got!r}"


def test_total_by_category_rounds_float_noise_away(day):
    got = day.total_by_category([("a", 0.1), ("a", 0.2)])
    assert got == {"a": 0.3}, (
        f"0.1 + 0.2 is 0.30000000000000004 — round the total to 2dp. Got {got!r}"
    )


def test_total_by_category_empty(day):
    assert day.total_by_category([]) == {}


def test_total_by_category_single_record(day):
    assert day.total_by_category([("books", 15.0)]) == {"books": 15.0}


# --- Exercise 5: group_by_first_letter ------------------------------------
def test_group_by_first_letter_groups_and_keeps_order(day):
    got = day.group_by_first_letter(["apple", "avocado", "fig"])
    assert got == {"a": ["apple", "avocado"], "f": ["fig"]}, f"got {got!r}"


def test_group_by_first_letter_several_groups(day):
    got = day.group_by_first_letter(["pear", "plum", "fig"])
    assert got == {"p": ["pear", "plum"], "f": ["fig"]}, f"got {got!r}"


def test_group_by_first_letter_empty(day):
    assert day.group_by_first_letter([]) == {}


def test_group_by_first_letter_is_case_sensitive(day):
    got = day.group_by_first_letter(["Fig", "fig"])
    assert got == {"F": ["Fig"], "f": ["fig"]}, (
        f"do not change the case of anything, got {got!r}"
    )


def test_group_by_first_letter_keeps_duplicates(day):
    got = day.group_by_first_letter(["ant", "ant"])
    assert got == {"a": ["ant", "ant"]}, f"grouping is not deduplicating: {got!r}"


# --- Exercise 6: most_common ---------------------------------------------
def test_most_common_picks_the_highest(day):
    assert day.most_common({"apple": 3, "fig": 2}) == "apple"


def test_most_common_ignores_key_order(day):
    got = day.most_common({"a": 1, "b": 9, "c": 4})
    assert got == "b", f"the biggest VALUE wins, not the biggest key. Got {got!r}"


def test_most_common_single_key(day):
    assert day.most_common({"only": 0}) == "only"


def test_most_common_empty_dictionary(day):
    got = day.most_common({})
    assert got == "", f"an empty dictionary has no winner; return \"\". Got {got!r}"


# --- Exercise 7: unique_in_order ------------------------------------------
def test_unique_in_order_keeps_first_appearances(day):
    got = day.unique_in_order(["b", "a", "b", "c", "a"])
    assert got == ["b", "a", "c"], (
        f"first-seen order, not alphabetical order. Got {got!r}"
    )


def test_unique_in_order_all_duplicates(day):
    assert day.unique_in_order(["x", "x", "x"]) == ["x"]


def test_unique_in_order_empty(day):
    assert day.unique_in_order([]) == []


def test_unique_in_order_nothing_to_remove(day):
    assert day.unique_in_order(["a", "b", "c"]) == ["a", "b", "c"]


def test_unique_in_order_returns_a_list(day):
    got = day.unique_in_order(["b", "a", "b"])
    assert isinstance(got, list), f"expected a list, got {type(got).__name__}"


# --- Exercise 8: compare_tags --------------------------------------------
def test_compare_tags_added_removed_kept(day):
    got = day.compare_tags(["a", "b"], ["b", "c"])
    want = {"added": ["c"], "removed": ["a"], "kept": ["b"]}
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_compare_tags_nothing_changed(day):
    got = day.compare_tags(["x"], ["x"])
    want = {"added": [], "removed": [], "kept": ["x"]}
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_compare_tags_collapses_duplicates(day):
    got = day.compare_tags([], ["new", "new"])
    want = {"added": ["new"], "removed": [], "kept": []}
    assert got == want, f"building a set removes the repeat. Got {got!r}"


def test_compare_tags_lists_are_sorted(day):
    got = day.compare_tags(["z", "m"], ["m", "c", "a"])
    assert got["added"] == ["a", "c"], f"added must be sorted, got {got['added']!r}"
    assert got["removed"] == ["z"], f"got {got['removed']!r}"
    assert got["kept"] == ["m"], f"got {got['kept']!r}"


def test_compare_tags_both_empty(day):
    assert day.compare_tags([], []) == {"added": [], "removed": [], "kept": []}


# --- Exercise 9: average_scores ------------------------------------------
def test_average_scores_two_students(day):
    got = day.average_scores({"ada": [90, 80], "alan": [70]})
    assert got == {"ada": 85.0, "alan": 70.0}, f"got {got!r}"


def test_average_scores_rounds_to_two_places(day):
    got = day.average_scores({"grace": [1, 2, 2]})
    assert got == {"grace": 1.67}, f"5/3 rounded to 2dp is 1.67, got {got!r}"


def test_average_scores_empty_score_list_is_zero(day):
    got = day.average_scores({"new": []})
    assert got == {"new": 0.0}, (
        f"a student with no scores averages 0.0 — dividing by len([]) would "
        f"raise ZeroDivisionError. Got {got!r}"
    )


def test_average_scores_empty_dictionary(day):
    assert day.average_scores({}) == {}


def test_average_scores_does_not_modify_the_argument(day):
    scores = {"ada": [90, 80], "new": []}
    day.average_scores(scores)
    assert scores == {"ada": [90, 80], "new": []}, (
        f"neither the dictionary nor the lists inside it may be changed: "
        f"{scores!r}"
    )


# --- Exercise 10: word_report --------------------------------------------
def test_word_report_counts_case_insensitively_and_strips_punctuation(day):
    got = day.word_report("the cat sat. The cat, the end!", 2)
    want = [("the", 3), ("cat", 2)]
    assert got == want, f"got {got!r}\nwant {want!r}"


def test_word_report_breaks_ties_alphabetically(day):
    got = day.word_report("b a b a c", 3)
    want = [("a", 2), ("b", 2), ("c", 1)]
    assert got == want, (
        f"tied counts sort by word in NORMAL alphabetical order\n"
        f"got  {got!r}\nwant {want!r}"
    )


def test_word_report_top_n_larger_than_the_data(day):
    assert day.word_report("hello", 5) == [("hello", 1)]


def test_word_report_empty_text(day):
    assert day.word_report("", 3) == []


def test_word_report_top_n_of_zero(day):
    got = day.word_report("anything at all", 0)
    assert got == [], f"top_n of 0 returns nothing, got {got!r}"
