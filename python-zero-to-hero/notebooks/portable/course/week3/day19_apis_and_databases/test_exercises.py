"""Day 19 graded checks — HTTP APIs and SQLite.

Not one test here touches the network: every fetch is a plain function returning
canned dicts, which is the whole point of the day's design. Databases live in
`tmp_path`, so nothing is left behind.

The `day` fixture hands these tests your exercises.py (or solutions.py when
PZH_SOLUTIONS=1 is set). Never import exercises directly.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import pytest


def _connect(tmp_path) -> sqlite3.Connection:
    """A real SQLite file inside pytest's temporary directory."""
    return sqlite3.connect(tmp_path / "test.db")


# --- exercise 1: build_url ------------------------------------------------


def test_build_url_joins_with_one_slash(day):
    assert day.build_url("https://api.example.com/v1", "readings") == (
        "https://api.example.com/v1/readings"
    )


def test_build_url_normalises_extra_slashes(day):
    got = day.build_url("https://api.example.com/v1/", "/readings", {"page": 2})
    assert got == "https://api.example.com/v1/readings?page=2", f"got {got}"


def test_build_url_encodes_values(day):
    got = day.build_url("https://x.io", "search", {"q": "a b"})
    assert got in {"https://x.io/search?q=a+b", "https://x.io/search?q=a%20b"}, f"got {got}"


def test_build_url_omits_none_params(day):
    got = day.build_url("https://x.io", "search", {"q": "hi", "limit": None})
    assert got == "https://x.io/search?q=hi", f"got {got}"


def test_build_url_no_trailing_question_mark(day):
    assert day.build_url("https://x.io", "p", {}) == "https://x.io/p"
    assert day.build_url("https://x.io", "p", None) == "https://x.io/p"


def test_build_url_keeps_param_order_and_casts_values(day):
    got = day.build_url("https://x.io", "p", {"b": 2, "a": True})
    assert got == "https://x.io/p?b=2&a=True", f"got {got}"


def test_build_url_escapes_ampersands(day):
    got = day.build_url("https://x.io", "p", {"q": "a&b=c"})
    assert "a%26b" in got, f"an unescaped & would break the query; got {got}"


# --- exercise 2: backoff_delay -------------------------------------------


def test_backoff_delay_doubles(day):
    assert [day.backoff_delay(a) for a in (1, 2, 3, 4)] == [1.0, 2.0, 4.0, 8.0]


def test_backoff_delay_respects_cap(day):
    assert day.backoff_delay(9) == 30.0
    assert day.backoff_delay(50, base=1.0, cap=5.0) == 5.0


def test_backoff_delay_custom_base(day):
    assert day.backoff_delay(3, base=0.25, cap=2.0) == 1.0
    assert day.backoff_delay(4, base=0.25, cap=2.0) == 2.0


def test_backoff_delay_returns_float(day):
    assert isinstance(day.backoff_delay(1), float)


def test_backoff_delay_rejects_attempt_below_one(day):
    with pytest.raises(ValueError):
        day.backoff_delay(0)


# --- exercise 3: should_retry --------------------------------------------


def test_should_retry_transient_statuses(day):
    for status in (429, 500, 502, 503, 504):
        assert day.should_retry(status, attempt=1, max_attempts=3) is True, status


def test_should_retry_refuses_client_errors(day):
    for status in (400, 401, 403, 404, 422):
        assert day.should_retry(status, attempt=1, max_attempts=5) is False, status


def test_should_retry_refuses_success(day):
    assert day.should_retry(200, attempt=1, max_attempts=3) is False
    assert day.should_retry(301, attempt=1, max_attempts=3) is False


def test_should_retry_stops_at_the_attempt_limit(day):
    assert day.should_retry(503, attempt=3, max_attempts=3) is False
    assert day.should_retry(503, attempt=2, max_attempts=3) is True


def test_should_retry_single_attempt_never_retries(day):
    assert day.should_retry(503, attempt=1, max_attempts=1) is False


# --- exercise 4: parse_readings ------------------------------------------


def test_parse_readings_accepts_good_records(day):
    good, bad = day.parse_readings(
        {"items": [{"sensor": "s1", "value": "21.5", "taken": "2024-01-01T00:00:00+00:00"}]}
    )
    assert bad == []
    assert len(good) == 1
    assert (good[0].sensor, good[0].value, good[0].taken) == (
        "s1",
        21.5,
        "2024-01-01T00:00:00+00:00",
    )


def test_parse_readings_quarantines_bad_records(day):
    payload = {
        "items": [
            {"sensor": "s1", "value": 1.0},
            {"sensor": "s2"},
            {"sensor": "", "value": 1.0},
            {"sensor": "s4", "value": "abc"},
            {"sensor": "s5", "value": None},
        ]
    }
    good, bad = day.parse_readings(payload)
    assert [r.sensor for r in good] == ["s1"], f"kept {[r.sensor for r in good]}"
    assert len(bad) == 4, f"quarantined {len(bad)}"


def test_parse_readings_uses_default_taken(day):
    good, _ = day.parse_readings({"items": [{"sensor": "s1", "value": 1}]}, "T0")
    assert good[0].taken == "T0"


def test_parse_readings_missing_items_key(day):
    assert day.parse_readings({}) == ([], [])
    assert day.parse_readings({"items": None}) == ([], [])


def test_parse_readings_never_raises_on_junk(day):
    good, bad = day.parse_readings({"items": [{"sensor": 7, "value": 1}, {}]})
    assert good == []
    assert len(bad) == 2


def test_parse_readings_preserves_order(day):
    payload = {"items": [{"sensor": f"s{i}", "value": i} for i in range(5)]}
    good, _ = day.parse_readings(payload)
    assert [r.sensor for r in good] == ["s0", "s1", "s2", "s3", "s4"]


def test_parse_readings_returns_reading_instances(day):
    good, _ = day.parse_readings({"items": [{"sensor": "s1", "value": 1}]})
    assert isinstance(good[0], day.Reading)


# --- exercise 5: iter_pages ----------------------------------------------


def test_iter_pages_follows_next(day):
    pages = {
        "/a": {"items": [1, 2], "next": "/b"},
        "/b": {"items": [3], "next": None},
    }
    assert list(day.iter_pages(lambda url: pages[url], "/a")) == [1, 2, 3]


def test_iter_pages_stops_when_next_missing(day):
    assert list(day.iter_pages(lambda url: {"items": ["x"]}, "/a")) == ["x"]


def test_iter_pages_is_lazy(day):
    calls: list[str] = []

    def fetch(url: str) -> dict[str, Any]:
        calls.append(url)
        return {"items": [url], "next": url + "+"}

    stream = day.iter_pages(fetch, "/a", max_pages=50)
    assert calls == [], "calling iter_pages must not fetch anything yet"
    first = next(iter(stream))
    assert first == "/a"
    assert len(calls) == 1, f"one item should need one fetch; made {len(calls)}"


def test_iter_pages_bounds_infinite_pagination(day):
    got = list(day.iter_pages(lambda url: {"items": [1], "next": "/loop"}, "/loop", 3))
    assert got == [1, 1, 1], f"max_pages must stop the loop; got {got}"


def test_iter_pages_rejects_bad_max_pages_at_call_time(day):
    with pytest.raises(ValueError):
        day.iter_pages(lambda url: {"items": []}, "/a", max_pages=0)


def test_iter_pages_handles_empty_pages(day):
    pages = {"/a": {"items": [], "next": "/b"}, "/b": {"items": [1], "next": None}}
    assert list(day.iter_pages(lambda url: pages[url], "/a")) == [1]


# --- exercise 6: fetch_with_retries --------------------------------------


def test_fetch_with_retries_returns_payload_on_success(day):
    payload, delays = day.fetch_with_retries(lambda url: (200, {"ok": True}), "/x")
    assert payload == {"ok": True}
    assert delays == [], "a first-attempt success sleeps not at all"


def test_fetch_with_retries_recovers_after_transient_failures(day):
    calls = [(503, None), (429, None), (200, {"ok": True})]
    slept: list[float] = []
    payload, delays = day.fetch_with_retries(
        lambda url: calls.pop(0), "/x", max_attempts=4, sleep=slept.append
    )
    assert payload == {"ok": True}
    assert delays == [1.0, 2.0], f"exponential backoff expected; got {delays}"
    assert slept == delays, "the returned delays must be the ones actually slept"


def test_fetch_with_retries_does_not_retry_client_errors(day):
    calls: list[str] = []

    def fetch(url: str) -> tuple[int, Any]:
        calls.append(url)
        return 404, None

    with pytest.raises(RuntimeError, match="404"):
        day.fetch_with_retries(fetch, "/x", max_attempts=5, sleep=lambda s: None)
    assert len(calls) == 1, f"404 must not be retried; made {len(calls)} calls"


def test_fetch_with_retries_raises_after_exhausting_attempts(day):
    calls: list[str] = []

    def fetch(url: str) -> tuple[int, Any]:
        calls.append(url)
        return 503, None

    with pytest.raises(RuntimeError, match="503"):
        day.fetch_with_retries(fetch, "/x", max_attempts=3, sleep=lambda s: None)
    assert len(calls) == 3, f"expected 3 attempts, made {len(calls)}"


def test_fetch_with_retries_honours_base_and_cap(day):
    calls = [(503, None), (503, None), (503, None), (200, "ok")]
    payload, delays = day.fetch_with_retries(
        lambda url: calls.pop(0),
        "/x",
        max_attempts=5,
        base_delay=0.25,
        cap=0.5,
        sleep=lambda s: None,
    )
    assert payload == "ok"
    assert delays == [0.25, 0.5, 0.5], f"got {delays}"


def test_fetch_with_retries_accepts_any_2xx(day):
    payload, _ = day.fetch_with_retries(lambda url: (204, None), "/x")
    assert payload is None


def test_fetch_with_retries_rejects_bad_max_attempts(day):
    with pytest.raises(ValueError):
        day.fetch_with_retries(lambda url: (200, None), "/x", max_attempts=0)


# --- exercise 7: init_db -------------------------------------------------


def test_init_db_creates_the_table(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    assert connection.execute("SELECT count(*) FROM readings").fetchone()[0] == 0


def test_init_db_is_idempotent(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.init_db(connection)  # must not raise


def test_init_db_enforces_unique_sensor_and_taken(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    connection.execute("INSERT INTO readings (sensor, value, taken) VALUES ('s1', 1.0, 't')")
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO readings (sensor, value, taken) VALUES ('s1', 2.0, 't')"
        )


def test_init_db_requires_not_null_columns(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("INSERT INTO readings (sensor) VALUES ('s1')")


# --- exercise 8: save_readings -------------------------------------------


def test_save_readings_inserts(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    readings = [
        day.Reading("s1", 21.5, "2024-01-01T00:00:00+00:00"),
        day.Reading("s2", 19.0, "2024-01-01T00:00:00+00:00"),
    ]
    assert day.save_readings(connection, readings) == 2
    assert connection.execute("SELECT count(*) FROM readings").fetchone()[0] == 2


def test_save_readings_is_idempotent(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    readings = [day.Reading("s1", 21.5, "2024-01-01T00:00:00+00:00")]
    day.save_readings(connection, readings)
    day.save_readings(connection, readings)
    count = connection.execute("SELECT count(*) FROM readings").fetchone()[0]
    assert count == 1, f"re-running the load duplicated rows: {count} rows"


def test_save_readings_updates_the_value_on_conflict(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(connection, [day.Reading("s1", 1.0, "t")])
    day.save_readings(connection, [day.Reading("s1", 99.0, "t")])
    value = connection.execute("SELECT value FROM readings WHERE sensor = 's1'").fetchone()[0]
    assert value == 99.0, f"the newer value should win; got {value}"


def test_save_readings_commits(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(connection, [day.Reading("s1", 1.0, "t")])
    connection.close()
    fresh = sqlite3.connect(tmp_path / "test.db")
    assert fresh.execute("SELECT count(*) FROM readings").fetchone()[0] == 1, (
        "data must be committed, not left in an open transaction"
    )
    fresh.close()


def test_save_readings_empty_batch(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    assert day.save_readings(connection, []) == 0


def test_save_readings_accepts_a_generator(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    readings = (day.Reading(f"s{i}", float(i), "t") for i in range(3))
    assert day.save_readings(connection, readings) == 3


# --- exercise 9: find_by_sensor ------------------------------------------


def test_find_by_sensor_returns_matching_rows(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(connection, [day.Reading("s1", 1.0, "2024-01-01T00:00:00+00:00")])
    assert day.find_by_sensor(connection, "s1") == [
        {"sensor": "s1", "value": 1.0, "taken": "2024-01-01T00:00:00+00:00"}
    ]


def test_find_by_sensor_orders_newest_first(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(
        connection,
        [
            day.Reading("s1", 1.0, "2024-01-01T00:00:00+00:00"),
            day.Reading("s1", 2.0, "2024-03-01T00:00:00+00:00"),
            day.Reading("s1", 3.0, "2024-02-01T00:00:00+00:00"),
        ],
    )
    got = [row["value"] for row in day.find_by_sensor(connection, "s1")]
    assert got == [2.0, 3.0, 1.0], f"order by taken descending; got {got}"


def test_find_by_sensor_unknown_sensor(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(connection, [day.Reading("s1", 1.0, "t")])
    assert day.find_by_sensor(connection, "nope") == []


def test_find_by_sensor_resists_sql_injection(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(
        connection,
        [day.Reading("s1", 1.0, "t1"), day.Reading("s2", 2.0, "t2")],
    )
    got = day.find_by_sensor(connection, "x' OR '1'='1")
    assert got == [], (
        "hostile input returned rows, so the value was interpreted as SQL. "
        "Use a `?` placeholder instead of an f-string."
    )


def test_find_by_sensor_injection_cannot_drop_the_table(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(connection, [day.Reading("s1", 1.0, "t1")])
    try:
        day.find_by_sensor(connection, "x'; DROP TABLE readings; --")
    except sqlite3.Error:
        pass  # refusing the input is acceptable; losing the table is not
    remaining = connection.execute("SELECT count(*) FROM readings").fetchone()[0]
    assert remaining == 1, "the table must survive hostile input"


def test_find_by_sensor_handles_quotes_in_legitimate_input(day, tmp_path):
    connection = _connect(tmp_path)
    day.init_db(connection)
    day.save_readings(connection, [day.Reading("O'Brien", 5.0, "t")])
    got = day.find_by_sensor(connection, "O'Brien")
    assert len(got) == 1, f"a legitimate apostrophe must work too; got {got}"


# --- exercise 10: sync_readings ------------------------------------------

PAGES: dict[str, dict[str, Any]] = {
    "/v1/readings": {
        "items": [
            {"sensor": "s1", "value": "21.5", "taken": "2024-01-01T00:00:00+00:00"},
            {"sensor": "s2", "value": 19.0, "taken": "2024-01-01T00:00:00+00:00"},
            {"sensor": "broken"},
        ],
        "next": "/v1/readings?cursor=abc",
    },
    "/v1/readings?cursor=abc": {
        "items": [
            {"sensor": "s3", "value": 25.5, "taken": "2024-01-01T00:00:00+00:00"},
            {"sensor": "s4", "value": "not-a-number"},
        ],
        "next": None,
    },
}


def test_sync_readings_reports_a_summary(day, tmp_path):
    connection = _connect(tmp_path)
    got = day.sync_readings(lambda url: PAGES[url], connection, "/v1/readings")
    want = {"fetched": 5, "saved": 3, "quarantined": 2, "stored": 3}
    assert got == want, f"got {got}, want {want}"


def test_sync_readings_is_idempotent(day, tmp_path):
    connection = _connect(tmp_path)
    day.sync_readings(lambda url: PAGES[url], connection, "/v1/readings")
    second = day.sync_readings(lambda url: PAGES[url], connection, "/v1/readings")
    assert second["stored"] == 3, f"a second run changed the row count: {second}"


def test_sync_readings_creates_its_own_schema(day, tmp_path):
    connection = _connect(tmp_path)
    # No init_db call here: sync must be usable against an empty database.
    summary = day.sync_readings(lambda url: PAGES[url], connection, "/v1/readings")
    assert summary["stored"] == 3


def test_sync_readings_data_is_queryable_afterwards(day, tmp_path):
    connection = _connect(tmp_path)
    day.sync_readings(lambda url: PAGES[url], connection, "/v1/readings")
    rows = day.find_by_sensor(connection, "s1")
    assert len(rows) == 1 and rows[0]["value"] == 21.5, f"got {rows}"


def test_sync_readings_empty_source(day, tmp_path):
    connection = _connect(tmp_path)
    got = day.sync_readings(lambda url: {"items": [], "next": None}, connection, "/x")
    assert got == {"fetched": 0, "saved": 0, "quarantined": 0, "stored": 0}


def test_sync_readings_respects_max_pages(day, tmp_path):
    connection = _connect(tmp_path)
    calls: list[str] = []

    def fetch(url: str) -> dict[str, Any]:
        calls.append(url)
        index = len(calls)
        return {
            "items": [{"sensor": f"s{index}", "value": 1.0, "taken": f"t{index}"}],
            "next": "/loop",
        }

    summary = day.sync_readings(fetch, connection, "/loop", max_pages=2)
    assert len(calls) == 2, f"max_pages ignored: made {len(calls)} fetches"
    assert summary["fetched"] == 2


def test_sync_readings_makes_no_network_calls(day, tmp_path, monkeypatch):
    # If the implementation imported requests and called it, this would fail.
    import builtins

    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name in {"requests", "httpx", "urllib.request", "socket"}:
            raise AssertionError(f"sync_readings must not import {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    connection = _connect(tmp_path)
    summary = day.sync_readings(lambda url: PAGES[url], connection, "/v1/readings")
    assert summary["saved"] == 3
