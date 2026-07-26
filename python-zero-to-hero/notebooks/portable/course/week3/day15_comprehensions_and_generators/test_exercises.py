"""Day 15 graded checks — comprehensions, iterators, generators.

The `day` fixture hands these tests your exercises.py (or solutions.py when
PZH_SOLUTIONS=1 is set). Never import exercises directly.
"""

from __future__ import annotations

import inspect
import sys
from itertools import count, islice

import pytest


# --- exercise 1: squares_of_evens -----------------------------------------


def test_squares_of_evens_keeps_only_even_squares(day):
    assert day.squares_of_evens([1, 2, 3, 4]) == [4, 16]


def test_squares_of_evens_handles_zero_and_negatives(day):
    assert day.squares_of_evens([-2, 0, 7]) == [4, 0]


def test_squares_of_evens_empty_input(day):
    assert day.squares_of_evens([]) == []


def test_squares_of_evens_does_not_mutate_input(day):
    numbers = [1, 2, 3, 4]
    day.squares_of_evens(numbers)
    assert numbers == [1, 2, 3, 4], "a comprehension must not modify its source"


def test_squares_of_evens_accepts_any_iterable(day):
    got = day.squares_of_evens(n for n in range(7))
    assert got == [0, 4, 16, 36], f"got {got}, want [0, 4, 16, 36]"


# --- exercise 2: word_lengths ---------------------------------------------


def test_word_lengths_maps_word_to_length(day):
    assert day.word_lengths(["yield", "is", "lazy"]) == {"yield": 5, "lazy": 4}


def test_word_lengths_drops_short_words(day):
    assert day.word_lengths(["a", "bb"]) == {}


def test_word_lengths_keeps_exactly_three_characters(day):
    got = day.word_lengths(["abc"])
    assert got == {"abc": 3}, f"3 characters is long enough; got {got}"


# --- exercise 3: unique_domains -------------------------------------------


def test_unique_domains_lowercases_and_deduplicates(day):
    got = day.unique_domains(["a@Example.com", "b@example.com", "c@other.org"])
    assert got == {"example.com", "other.org"}


def test_unique_domains_returns_a_set(day):
    assert isinstance(day.unique_domains(["x@y.io"]), set)


def test_unique_domains_ignores_malformed_addresses(day):
    got = day.unique_domains(["bad-address", "x@y.io", "a@b@c.com", ""])
    assert got == {"y.io"}, f"only single-@ addresses count; got {got}"


# --- exercise 4: flatten_matrix -------------------------------------------


def test_flatten_matrix_flattens_and_filters(day):
    assert day.flatten_matrix([[1, -2, 3], [4, 0]]) == [1, 3, 4]


def test_flatten_matrix_skips_empty_rows(day):
    assert day.flatten_matrix([[], [7]]) == [7]


def test_flatten_matrix_preserves_row_major_order(day):
    got = day.flatten_matrix([[3, 1], [2]])
    assert got == [3, 1, 2], f"order must follow the input; got {got}"


# --- exercise 5: Countdown (iterator protocol) ----------------------------


def test_countdown_class_iterates_down_to_one(day):
    assert list(day.Countdown(3)) == [3, 2, 1]


def test_countdown_class_zero_is_empty(day):
    assert list(day.Countdown(0)) == []


def test_countdown_class_iter_returns_self(day):
    counter = day.Countdown(2)
    assert iter(counter) is counter, "__iter__ on an iterator must return self"


def test_countdown_class_is_single_use(day):
    counter = day.Countdown(2)
    assert next(counter) == 2
    assert list(counter) == [1], "an iterator continues where it left off"
    assert list(counter) == [], "and is empty once exhausted"


def test_countdown_class_raises_stop_iteration(day):
    counter = day.Countdown(1)
    next(counter)
    with pytest.raises(StopIteration):
        next(counter)


def test_countdown_class_does_not_use_yield(day):
    counter = day.Countdown(2)
    assert not inspect.isgeneratorfunction(
        type(counter).__next__
    ), "__next__ must return a value, not be a generator function"
    assert next(counter) == 2


# --- exercise 6: running_totals -------------------------------------------


def test_running_totals_accumulates(day):
    assert list(day.running_totals([1, 2, 3])) == [1, 3, 6]


def test_running_totals_handles_negatives_and_floats(day):
    assert list(day.running_totals([5, -5, 2.5])) == [5, 0, 2.5]


def test_running_totals_empty_input(day):
    assert list(day.running_totals([])) == []


def test_running_totals_is_a_generator_function(day):
    assert inspect.isgeneratorfunction(
        day.running_totals
    ), "running_totals must contain `yield`, not build and return a list"


def test_running_totals_is_lazy_on_infinite_input(day):
    stream = day.running_totals(count(1))  # 1, 2, 3, ... forever
    assert list(islice(stream, 4)) == [1, 3, 6, 10]


# --- exercise 7: take -----------------------------------------------------


def test_take_returns_first_n(day):
    assert day.take([10, 20, 30], 2) == [10, 20]


def test_take_handles_short_source(day):
    assert day.take("abc", 10) == ["a", "b", "c"]


def test_take_zero_returns_empty(day):
    assert day.take([1, 2], 0) == []


def test_take_does_not_hang_on_infinite_source(day):
    assert day.take(count(), 3) == [0, 1, 2]


def test_take_does_not_overconsume(day):
    source = iter([1, 2, 3, 4, 5])
    assert day.take(source, 2) == [1, 2]
    remaining = list(source)
    assert remaining == [3, 4, 5], (
        f"take pulled too many values; the source still had {remaining}"
    )


# --- exercise 8: chunked --------------------------------------------------


def test_chunked_splits_with_short_final_chunk(day):
    assert list(day.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_chunked_size_larger_than_input(day):
    assert list(day.chunked("abc", 5)) == [["a", "b", "c"]]


def test_chunked_empty_input_yields_nothing(day):
    assert list(day.chunked([], 3)) == []


def test_chunked_rejects_bad_size_at_call_time(day):
    with pytest.raises(ValueError):
        day.chunked([1, 2, 3], 0)  # no list() here: must raise on the call


def test_chunked_streams_lazily(day):
    stream = day.chunked(count(), 3)
    first_two = [next(stream), next(stream)]
    assert first_two == [[0, 1, 2], [3, 4, 5]], f"got {first_two}"


def test_chunked_returns_independent_lists(day):
    chunks = list(day.chunked([1, 2, 3, 4], 2))
    assert chunks[0] is not chunks[1], "each chunk must be a fresh list"
    assert chunks == [[1, 2], [3, 4]]


# --- exercise 9: flatten_deep --------------------------------------------


def test_flatten_deep_descends_all_levels(day):
    assert list(day.flatten_deep([1, [2, [3, [4]], 5], 6])) == [1, 2, 3, 4, 5, 6]


def test_flatten_deep_drops_empty_lists(day):
    assert list(day.flatten_deep([[], [[]], [1]])) == [1]


def test_flatten_deep_treats_strings_and_tuples_as_leaves(day):
    assert list(day.flatten_deep(["ab", [(1, 2)]])) == ["ab", (1, 2)]


def test_flatten_deep_is_a_generator_function(day):
    assert inspect.isgeneratorfunction(
        day.flatten_deep
    ), "flatten_deep must yield, not return a list"


def test_flatten_deep_survives_deep_nesting(day):
    nested: object = 1
    for _ in range(200):
        nested = [nested]
    assert list(day.flatten_deep([nested])) == [1]


# --- exercise 10: stream_report ------------------------------------------


def test_stream_report_counts_kept_and_skipped(day):
    data = ["s1,temp,21.5", "", "s1,temp,19.0", "junk", "s2,temp,30.5"]
    got = day.stream_report(data, 20.0)
    want = {
        "kept": 2,
        "skipped": 2,
        "total": 52.0,
        "mean": 26.0,
        "sensors": {"s1": 1, "s2": 1},
    }
    assert got == want, f"got {got}, want {want}"


def test_stream_report_all_malformed(day):
    got = day.stream_report(["a,b,c"], 0.0)
    want = {"kept": 0, "skipped": 1, "total": 0.0, "mean": 0.0, "sensors": {}}
    assert got == want, f"got {got}, want {want}"


def test_stream_report_mean_is_zero_when_nothing_kept(day):
    got = day.stream_report(["s1,temp,1.0", "s1,temp,2.0"], 100.0)
    assert got["kept"] == 0
    assert got["skipped"] == 0, "well-formed rows below the cutoff are not skipped"
    assert got["mean"] == 0.0
    assert got["sensors"] == {}


def test_stream_report_groups_repeated_sensors(day):
    data = ["s1,a,5", "s1,a,6", "s2,a,7", "s1,a,0"]
    got = day.stream_report(data, 1.0)
    assert got["sensors"] == {"s1": 2, "s2": 1}, f"got {got['sensors']}"
    assert got["kept"] == 3


def test_stream_report_tolerates_whitespace_and_newlines(day):
    data = ["s1,a,5\n", "   ", "\t", "s2,a,6\n"]
    got = day.stream_report(data, 0.0)
    assert got["kept"] == 2, f"got {got}"
    assert got["skipped"] == 2, f"got {got}"


def test_stream_report_consumes_the_stream_only_once(day):
    lines = iter(["s1,a,5", "s2,a,6"])
    got = day.stream_report(lines, 0.0)
    assert got["kept"] == 2
    assert list(lines) == [], "the stream should be fully consumed exactly once"


def test_stream_report_handles_a_large_stream_without_materialising_it(day):
    # 200k synthetic lines through a generator: fine if you stream, slow and
    # memory-hungry if you called list() on the input.
    lines = (f"s{i % 3},temp,{i}" for i in range(200_000))
    got = day.stream_report(lines, 100.0)
    assert got["kept"] == 200_000 - 101, f"got {got['kept']}"
    assert sum(got["sensors"].values()) == got["kept"]
    assert sys.getsizeof(got) < 10_000, "the report itself should be tiny"
