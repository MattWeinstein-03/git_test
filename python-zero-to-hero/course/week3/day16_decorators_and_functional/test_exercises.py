"""Day 16 graded checks — functional Python and decorators.

The `day` fixture hands these tests your exercises.py (or solutions.py when
PZH_SOLUTIONS=1 is set). Never import exercises directly.
"""

from __future__ import annotations

import pytest


# --- exercise 1: sort_by_length_then_alpha ---------------------------------


def test_sort_by_length_then_alpha_orders_by_length(day):
    got = day.sort_by_length_then_alpha(["pear", "fig", "Apple", "kiwi"])
    assert got == ["fig", "kiwi", "pear", "Apple"], f"got {got}"


def test_sort_by_length_then_alpha_tie_break_is_case_insensitive(day):
    got = day.sort_by_length_then_alpha(["bb", "BA", "ab"])
    assert got == ["ab", "BA", "bb"], f"got {got}"


def test_sort_by_length_then_alpha_does_not_mutate_input(day):
    words = ["ccc", "a", "bb"]
    day.sort_by_length_then_alpha(words)
    assert words == ["ccc", "a", "bb"], "sorted() returns a new list; list.sort() mutates"


def test_sort_by_length_then_alpha_empty(day):
    assert day.sort_by_length_then_alpha([]) == []


# --- exercise 2: rank_players ---------------------------------------------


def test_rank_players_orders_by_score_then_name(day):
    players = [
        {"name": "ada", "score": 10},
        {"name": "bo", "score": 30},
        {"name": "cy", "score": 10},
    ]
    assert day.rank_players(players) == ["bo", "ada", "cy"]


def test_rank_players_empty(day):
    assert day.rank_players([]) == []


def test_rank_players_handles_floats_and_negatives(day):
    players = [
        {"name": "a", "score": -1},
        {"name": "b", "score": 2.5},
        {"name": "c", "score": 2.5},
    ]
    assert day.rank_players(players) == ["b", "c", "a"]


def test_rank_players_ignores_extra_keys(day):
    players = [{"name": "x", "score": 1, "team": "red"}]
    assert day.rank_players(players) == ["x"]


# --- exercise 3: parse_and_scale ------------------------------------------


def test_parse_and_scale_drops_unparseable(day):
    assert day.parse_and_scale([" 1.5 ", "oops", "2"], 2.0) == [3.0, 4.0]


def test_parse_and_scale_all_bad_returns_empty(day):
    assert day.parse_and_scale(["", "x"], 10.0) == []


def test_parse_and_scale_preserves_order_and_signs(day):
    got = day.parse_and_scale(["-2", "3", "nope", "0"], 0.5)
    assert got == [-1.0, 1.5, 0.0], f"got {got}"


def test_parse_and_scale_returns_floats(day):
    got = day.parse_and_scale(["2"], 3)
    assert got == [6.0]
    assert isinstance(got[0], float), f"expected float, got {type(got[0]).__name__}"


# --- exercise 4: make_running_average ------------------------------------


def test_make_running_average_tracks_mean(day):
    avg = day.make_running_average()
    assert avg(10) == 10.0
    assert avg(20) == 15.0
    assert avg(0) == 10.0


def test_make_running_average_instances_are_independent(day):
    first = day.make_running_average()
    second = day.make_running_average()
    first(100)
    assert second(4) == 4.0, "each closure must own its state"


def test_make_running_average_returns_float(day):
    avg = day.make_running_average()
    assert isinstance(avg(3), float)


# --- exercise 5: make_adders ---------------------------------------------


def test_make_adders_each_captures_own_offset(day):
    adders = day.make_adders([1, 10, 100])
    got = [add(0) for add in adders]
    assert got == [1, 10, 100], f"got {got} — this is the late-binding bug"


def test_make_adders_functions_are_usable(day):
    assert day.make_adders([5])[0](2) == 7


def test_make_adders_empty_list(day):
    assert day.make_adders([]) == []


def test_make_adders_returns_callables_in_order(day):
    adders = day.make_adders([3, 4])
    assert all(callable(add) for add in adders)
    assert [add(10) for add in adders] == [13, 14]


# --- exercise 6: count_calls ---------------------------------------------


def test_count_calls_passes_through_result(day):
    @day.count_calls
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert add(b=1, a=2) == 3, "the wrapper must accept keyword arguments too"


def test_count_calls_counts(day):
    @day.count_calls
    def noop():
        return None

    assert noop.calls == 0, "the counter starts at zero"
    noop()
    noop()
    assert noop.calls == 2


def test_count_calls_preserves_metadata(day):
    @day.count_calls
    def documented(x):
        """Original docstring."""
        return x

    assert documented.__name__ == "documented", "use functools.wraps"
    assert documented.__doc__ == "Original docstring.", "use functools.wraps"


def test_count_calls_records_duration(day):
    @day.count_calls
    def busy():
        return sum(range(10_000))

    busy()
    assert isinstance(busy.last_duration, float)
    assert busy.last_duration >= 0.0
    assert busy.last_duration < 1.0, "this should be fast; are you timing correctly?"


def test_count_calls_counts_failures_too(day):
    @day.count_calls
    def explodes():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        explodes()
    assert explodes.calls == 1, "a call that raised is still a call"
    assert explodes.last_duration >= 0.0, "use try/finally to time failures"


# --- exercise 7: memoize -------------------------------------------------


def test_memoize_calls_underlying_once_per_argument(day):
    seen = []

    @day.memoize
    def square(n):
        seen.append(n)
        return n * n

    assert (square(4), square(4), square(5)) == (16, 16, 25)
    assert seen == [4, 5], f"underlying function saw {seen}"


def test_memoize_tracks_hits_and_misses(day):
    @day.memoize
    def identity(n):
        return n

    assert (identity.hits, identity.misses) == (0, 0)
    identity(1)
    identity(1)
    identity(2)
    assert (identity.hits, identity.misses) == (1, 2)


def test_memoize_exposes_cache(day):
    @day.memoize
    def double(n):
        return n * 2

    double(3)
    double(4)
    assert sorted(double.cache) == [(3,), (4,)], f"cache keys: {sorted(double.cache)}"
    double.cache.clear()
    assert double.cache == {}


def test_memoize_preserves_metadata(day):
    @day.memoize
    def described(n):
        """Doc kept."""
        return n

    assert described.__name__ == "described"
    assert described.__doc__ == "Doc kept."


def test_memoize_speeds_up_recursion(day):
    calls = []

    @day.memoize
    def fib(n):
        calls.append(n)
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(30) == 832040
    assert len(calls) <= 31, f"a memoised fib(30) needs ~31 calls, made {len(calls)}"


def test_memoize_distinguishes_argument_tuples(day):
    @day.memoize
    def join(a, b):
        return f"{a}-{b}"

    assert join(1, 2) == "1-2"
    assert join(2, 1) == "2-1"
    assert join.misses == 2


# --- exercise 8: retry ---------------------------------------------------


def test_retry_returns_value_on_first_success(day):
    @day.retry(attempts=3, exceptions=(ValueError,))
    def fine():
        return "ok"

    assert fine() == "ok"
    assert fine.attempts_made == 1


def test_retry_recovers_after_failures(day):
    state = {"fails": 2}

    @day.retry(attempts=3, exceptions=(ValueError,))
    def flaky():
        if state["fails"]:
            state["fails"] -= 1
            raise ValueError("later")
        return "ok"

    assert flaky() == "ok"
    assert flaky.attempts_made == 3, f"expected 3 calls, got {flaky.attempts_made}"


def test_retry_reraises_last_error(day):
    @day.retry(attempts=2, exceptions=(ValueError,))
    def always_bad():
        raise ValueError("still broken")

    with pytest.raises(ValueError, match="still broken"):
        always_bad()
    assert always_bad.attempts_made == 2


def test_retry_does_not_swallow_other_exceptions(day):
    calls = []

    @day.retry(attempts=5, exceptions=(ValueError,))
    def wrong_error():
        calls.append(1)
        raise KeyError("not retryable")

    with pytest.raises(KeyError):
        wrong_error()
    assert len(calls) == 1, "only the listed exception types are retried"


def test_retry_rejects_bad_attempts_at_factory_time(day):
    with pytest.raises(ValueError):
        day.retry(attempts=0)


def test_retry_preserves_metadata(day):
    @day.retry(attempts=1)
    def named():
        """Kept."""
        return 1

    assert named.__name__ == "named"
    assert named.__doc__ == "Kept."


def test_retry_resets_attempts_between_calls(day):
    state = {"fails": 1}

    @day.retry(attempts=3, exceptions=(ValueError,))
    def sometimes():
        if state["fails"]:
            state["fails"] -= 1
            raise ValueError("once")
        return "ok"

    sometimes()
    assert sometimes.attempts_made == 2
    sometimes()
    assert sometimes.attempts_made == 1, "the counter is per wrapper call"


# --- exercise 9: audited -------------------------------------------------


def test_audited_records_success(day):
    log: list[str] = []

    @day.audited(log, "api")
    def half(n):
        return n // 2

    assert half(10) == 5
    assert log == ["api:half:ok:5"], f"got {log}"


def test_audited_records_failure_and_reraises(day):
    log: list[str] = []

    @day.audited(log, "api")
    def boom():
        raise KeyError("nope")

    with pytest.raises(KeyError):
        boom()
    assert log == ["api:boom:error:KeyError"], f"got {log}"


def test_audited_uses_repr_of_result(day):
    log: list[str] = []

    @day.audited(log, "x")
    def text():
        return "hi"

    text()
    assert log == ["x:text:ok:'hi'"], f"repr matters; got {log}"


def test_audited_preserves_metadata(day):
    log: list[str] = []

    @day.audited(log, "x")
    def named(a):
        """Doc."""
        return a

    assert named.__name__ == "named"
    assert named.__doc__ == "Doc."


def test_audited_stacks_with_count_calls(day):
    log: list[str] = []

    @day.count_calls
    @day.audited(log, "svc")
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    assert add(1, 1) == 2
    assert add.calls == 2
    assert log == ["svc:add:ok:5", "svc:add:ok:2"], (
        f"stacked decorators must keep the real function name; got {log}"
    )


# --- exercise 10: compose -----------------------------------------------


def test_compose_applies_left_to_right(day):
    clean = day.compose(str.strip, str.lower)
    assert clean("  HeLLo  ") == "hello"


def test_compose_order_matters(day):
    assert day.compose(lambda n: n + 1, lambda n: n * 10)(2) == 30
    assert day.compose(lambda n: n * 10, lambda n: n + 1)(2) == 21


def test_compose_with_no_functions_is_identity(day):
    assert day.compose()(42) == 42
    assert day.compose()("unchanged") == "unchanged"


def test_compose_single_function(day):
    assert day.compose(str.upper)("abc") == "ABC"


def test_compose_is_reusable(day):
    pipeline = day.compose(str.strip, str.lower, lambda s: s.replace(" ", "-"))
    assert pipeline("  A B  ") == "a-b"
    assert pipeline("  C D  ") == "c-d", "the composed function must be reusable"


def test_compose_chains_many_functions(day):
    steps = [lambda n, k=k: n + k for k in range(1, 6)]
    assert day.compose(*steps)(0) == 15
