"""Day 21 graded checks — Project 3: sensorpipe.

Tests are named test_m1_* … test_m5_* so partial credit is visible: finish M1 and
the config checks go green while the rest still fail.

Two rules this file follows, and yours should too:

  * No network. The source is a plain function that returns (status, payload)
    from a dict, which is the whole reason `fetch` is a parameter.
  * No writes into the repository. Every database lives under `tmp_path`.

The whole file runs in well under a second.
"""

from __future__ import annotations

import dataclasses
import itertools
import logging
import sqlite3
from datetime import datetime, timezone

import pytest

UTC = timezone.utc

BASE_URL = "https://example.invalid/v1/readings"
PAGE_TWO_URL = "https://example.invalid/v1/readings?cursor=p2"

# Two pages of deliberately messy source data: string values, three timestamp
# shapes, a mixed-case region, a missing region, and two rows that must be
# quarantined rather than crash the run.
RAW_PAGE_ONE = {
    "items": [
        {"sensor": " s1 ", "value": "21.5", "taken": "2024-03-15T13:00:00Z", "region": "EU"},
        {"sensor": "s2", "value": 19.0, "taken": "2024-03-15T13:00:00+01:00", "region": "US"},
        {"sensor": "", "value": 5.0, "taken": "2024-03-15T13:00:00Z"},
        {"sensor": "s4", "value": "abc", "taken": "2024-03-15T13:00:00Z", "region": "eu"},
    ],
    "next": PAGE_TWO_URL,
}
RAW_PAGE_TWO = {
    "items": [
        {"sensor": "s1", "value": 30.0, "taken": "2024-03-15T14:00:00Z", "region": "eu"},
        {"sensor": "s1", "value": "9.25", "taken": "2024-03-15T15:00:00Z"},
        {"sensor": "s3", "value": 12.5, "taken": "2024-03-16T00:30:00Z", "region": "eu"},
    ],
    "next": None,
}

# 5 usable records: s1 x3 (21.5, 30.0, 9.25), s2 x1 (19.0), s3 x1 (12.5).
GOOD_RECORD_COUNT = 5
QUARANTINE_COUNT = 2


class FakeSource:
    """A stand-in for the network: a dict of url -> (status, payload)."""

    def __init__(self, pages=None, always=None):
        self.pages = pages if pages is not None else {
            BASE_URL: (200, RAW_PAGE_ONE),
            PAGE_TWO_URL: (200, RAW_PAGE_TWO),
        }
        self.always = always
        self.calls: list[str] = []

    def __call__(self, url: str):
        self.calls.append(url)
        if self.always is not None:
            return self.always
        if url not in self.pages:
            return 404, {}
        return self.pages[url]


def env_for(tmp_path, **extra) -> dict[str, str]:
    """An environment mapping pointing the app at a temporary database."""
    env = {"SENSORPIPE_URL": BASE_URL, "SENSORPIPE_DB": str(tmp_path / "sensorpipe.db")}
    env.update(extra)
    return env


def settings_for(day, tmp_path, **extra):
    """Settings built through the graded loader, so M1 stays the only source."""
    return day.load_settings(env_for(tmp_path, **extra))


def record(day, sensor="s1", value=10.0, hour=13, minute=0, region="eu", band=""):
    """One Record, with sensible defaults so tests say only what matters."""
    return day.Record(
        sensor=sensor,
        value=value,
        taken=datetime(2024, 3, 15, hour, minute, tzinfo=UTC),
        region=region,
        band=band,
    )


def endless_records(day):
    """An infinite source, for proving a stage is lazy."""
    for number in itertools.count():
        yield record(day, sensor=f"s{number}", value=float(number))


def stored_readings(db_path) -> list[dict]:
    """Read a database back with plain sqlite3, independently of M4."""
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT sensor, value, taken, region, band FROM readings ORDER BY sensor, taken"
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


# ===========================================================================
# M1 — configuration
# ===========================================================================
def test_m1_load_settings_applies_documented_defaults(day):
    settings = day.load_settings({})
    assert settings.source_url == "https://example.invalid/v1/readings"
    assert str(settings.db_path) == "sensorpipe.db"
    assert settings.batch_size == 100
    assert settings.max_pages == 10
    assert settings.min_value == 0.0
    assert settings.verbose is False


def test_m1_load_settings_reads_every_variable(day):
    settings = day.load_settings(
        {
            "SENSORPIPE_URL": "http://localhost:8000/v1/readings",
            "SENSORPIPE_DB": "/tmp/pipe.db",
            "SENSORPIPE_BATCH_SIZE": "25",
            "SENSORPIPE_MAX_PAGES": "3",
            "SENSORPIPE_MIN_VALUE": "-2.5",
            "SENSORPIPE_VERBOSE": "true",
        }
    )
    assert settings.source_url == "http://localhost:8000/v1/readings"
    assert settings.batch_size == 25
    assert settings.max_pages == 3
    assert settings.min_value == -2.5
    assert settings.verbose is True


def test_m1_db_path_is_a_path_object(day):
    from pathlib import Path

    settings = day.load_settings({"SENSORPIPE_DB": "data/pipe.db"})
    assert isinstance(settings.db_path, Path), "db_path must be a Path, not a str"
    assert settings.db_path.name == "pipe.db"


def test_m1_boolean_words_are_all_accepted(day):
    for text in ("1", "true", "TRUE", "yes", "on"):
        assert day.load_settings({"SENSORPIPE_VERBOSE": text}).verbose is True, text
    for text in ("0", "false", "No", "off"):
        assert day.load_settings({"SENSORPIPE_VERBOSE": text}).verbose is False, text


def test_m1_settings_is_frozen(day):
    settings = day.load_settings({})
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.batch_size = 5


def test_m1_rejects_a_url_without_a_scheme(day):
    with pytest.raises(ValueError) as caught:
        day.load_settings({"SENSORPIPE_URL": "ftp://example.invalid/x"})
    message = str(caught.value)
    assert "SENSORPIPE_URL" in message, f"name the variable: {message!r}"
    assert "ftp://example.invalid/x" in message, f"quote the value: {message!r}"


def test_m1_rejects_batch_sizes_outside_the_range(day):
    for bad in ("0", "10001", "abc", ""):
        with pytest.raises(ValueError) as caught:
            day.load_settings({"SENSORPIPE_BATCH_SIZE": bad})
        message = str(caught.value)
        assert "SENSORPIPE_BATCH_SIZE" in message, f"{bad!r} -> {message!r}"
        assert bad in message or repr(bad) in message, f"{bad!r} -> {message!r}"


def test_m1_rejects_max_pages_below_one(day):
    with pytest.raises(ValueError, match="SENSORPIPE_MAX_PAGES"):
        day.load_settings({"SENSORPIPE_MAX_PAGES": "0"})


def test_m1_rejects_unparseable_numbers_and_booleans(day):
    with pytest.raises(ValueError, match="SENSORPIPE_MIN_VALUE"):
        day.load_settings({"SENSORPIPE_MIN_VALUE": "warm"})
    with pytest.raises(ValueError, match="SENSORPIPE_VERBOSE"):
        day.load_settings({"SENSORPIPE_VERBOSE": "maybe"})


def test_m1_none_means_the_process_environment(day, monkeypatch):
    monkeypatch.setenv("SENSORPIPE_MAX_PAGES", "7")
    monkeypatch.setenv("SENSORPIPE_VERBOSE", "1")
    settings = day.load_settings()
    assert settings.max_pages == 7
    assert settings.verbose is True


# ===========================================================================
# M2 — extract
# ===========================================================================
def test_m2_normalise_record_cleans_a_good_row(day):
    got = day.normalise_record(
        {"sensor": " s1 ", "value": "21.5", "taken": "2024-03-15T13:00:00Z", "region": "EU"}
    )
    assert got.sensor == "s1", "strip the sensor name"
    assert got.value == 21.5 and isinstance(got.value, float)
    assert got.region == "eu", "lowercase the region"
    assert got.band == "", "band is filled in by M3, not M2"
    assert got.taken == datetime(2024, 3, 15, 13, tzinfo=UTC)


def test_m2_normalise_record_converts_offsets_to_utc(day):
    got = day.normalise_record(
        {"sensor": "s2", "value": 19.0, "taken": "2024-03-15T13:00:00+01:00"}
    )
    assert got.taken == datetime(2024, 3, 15, 12, tzinfo=UTC), "13:00+01:00 is 12:00 UTC"
    assert got.taken.utcoffset() == timezone.utc.utcoffset(None)


def test_m2_normalise_record_treats_naive_timestamps_as_utc(day):
    got = day.normalise_record({"sensor": "s2", "value": 1, "taken": "2024-03-15T13:00:00"})
    assert got.taken == datetime(2024, 3, 15, 13, tzinfo=UTC)
    assert got.taken.tzinfo is not None, "every Record.taken must be timezone-aware"


def test_m2_normalise_record_defaults_the_region(day):
    for raw in (
        {"sensor": "s2", "value": 1, "taken": "2024-03-15T13:00:00Z"},
        {"sensor": "s2", "value": 1, "taken": "2024-03-15T13:00:00Z", "region": "  "},
    ):
        assert day.normalise_record(raw).region == "unknown"


def test_m2_normalise_record_rejects_bad_sensors(day):
    for bad in ("", "   ", None, 7):
        with pytest.raises(ValueError):
            day.normalise_record({"sensor": bad, "value": 1.0, "taken": "2024-03-15T13:00:00Z"})
    with pytest.raises(ValueError):
        day.normalise_record({"value": 1.0, "taken": "2024-03-15T13:00:00Z"})


def test_m2_normalise_record_rejects_bad_values(day):
    for bad in ("abc", None, "", [1]):
        with pytest.raises(ValueError):
            day.normalise_record({"sensor": "s1", "value": bad, "taken": "2024-03-15T13:00:00Z"})
    with pytest.raises(ValueError):
        day.normalise_record({"sensor": "s1", "taken": "2024-03-15T13:00:00Z"})


def test_m2_normalise_record_rejects_bad_timestamps(day):
    for bad in ("15 March 2024", "", "2024-03-15T99:00:00Z", None, 1710500000):
        with pytest.raises(ValueError):
            day.normalise_record({"sensor": "s1", "value": 1.0, "taken": bad})


def test_m2_normalise_all_splits_good_from_bad(day):
    records, quarantined = day.normalise_all(RAW_PAGE_ONE["items"])
    assert [r.sensor for r in records] == ["s1", "s2"]
    assert quarantined == [RAW_PAGE_ONE["items"][2], RAW_PAGE_ONE["items"][3]], (
        "quarantined items are the original dicts, unchanged and in order"
    )


def test_m2_normalise_all_never_raises(day):
    records, quarantined = day.normalise_all([{}, {"sensor": "s1"}, "not a mapping"])
    assert records == []
    assert len(quarantined) == 3, f"everything unusable is quarantined: {quarantined!r}"
    assert day.normalise_all([]) == ([], [])


def test_m2_fetch_page_returns_the_payload_on_success(day):
    source = FakeSource()
    assert day.fetch_page(source, BASE_URL) == RAW_PAGE_ONE
    assert source.calls == [BASE_URL], "one attempt is enough when it works"


def test_m2_fetch_page_retries_transient_failures(day):
    statuses = iter([(503, {}), (429, {}), (200, {"items": []})])
    delays: list[float] = []

    def source(url):
        return next(statuses)

    payload = day.fetch_page(
        source, BASE_URL, max_attempts=3, base_delay=0.5, sleep=delays.append
    )
    assert payload == {"items": []}
    assert len(delays) == 2, f"two failures means two waits, got {delays!r}"
    assert all(delay > 0 for delay in delays), f"backoff must wait: {delays!r}"
    assert delays == sorted(delays), f"backoff must not shrink: {delays!r}"


def test_m2_fetch_page_gives_up_and_names_the_status(day):
    source = FakeSource(always=(503, {}))
    with pytest.raises(RuntimeError, match="503"):
        day.fetch_page(source, BASE_URL, max_attempts=3, base_delay=0.0)
    assert len(source.calls) == 3, f"max_attempts=3 means 3 calls, got {len(source.calls)}"


def test_m2_fetch_page_does_not_retry_a_client_error(day):
    source = FakeSource(always=(404, {}))
    with pytest.raises(RuntimeError, match="404"):
        day.fetch_page(source, BASE_URL, max_attempts=3, base_delay=0.0)
    assert len(source.calls) == 1, "a 404 will not fix itself — do not retry it"


def test_m2_fetch_page_rejects_zero_attempts(day):
    with pytest.raises(ValueError):
        day.fetch_page(FakeSource(), BASE_URL, max_attempts=0)


def test_m2_extract_records_walks_every_page(day, tmp_path):
    source = FakeSource()
    records, quarantined, errors = day.extract_records(source, settings_for(day, tmp_path))
    assert errors == []
    assert len(records) == GOOD_RECORD_COUNT
    assert len(quarantined) == QUARANTINE_COUNT
    assert source.calls == [BASE_URL, PAGE_TWO_URL], "follow the 'next' cursor"
    assert [r.sensor for r in records] == ["s1", "s2", "s1", "s1", "s3"], "source order"


def test_m2_extract_records_respects_max_pages(day, tmp_path):
    source = FakeSource()
    records, _quarantined, errors = day.extract_records(
        source, settings_for(day, tmp_path, SENSORPIPE_MAX_PAGES="1")
    )
    assert source.calls == [BASE_URL], "max_pages=1 means exactly one fetch"
    assert len(records) == 2
    assert errors == []


def test_m2_extract_records_reports_a_failure_instead_of_raising(day, tmp_path):
    source = FakeSource(always=(500, {}))
    records, quarantined, errors = day.extract_records(source, settings_for(day, tmp_path))
    assert records == [] and quarantined == []
    assert len(errors) == 1, f"one page failed, expected one error: {errors!r}"
    assert errors[0].startswith(f"{BASE_URL}: "), f"errors name the url: {errors[0]!r}"
    assert "500" in errors[0]


def test_m2_extract_records_keeps_what_it_already_had(day, tmp_path):
    source = FakeSource(pages={BASE_URL: (200, RAW_PAGE_ONE), PAGE_TWO_URL: (500, {})})
    records, quarantined, errors = day.extract_records(source, settings_for(day, tmp_path))
    assert len(records) == 2, "page one succeeded; its records must survive page two"
    assert len(quarantined) == QUARANTINE_COUNT
    assert len(errors) == 1


# ===========================================================================
# M3 — transform
# ===========================================================================
def test_m3_filter_records_is_inclusive(day):
    records = [record(day, value=9.99), record(day, value=10.0), record(day, value=11.0)]
    kept = list(day.filter_records(records, 10.0))
    assert [r.value for r in kept] == [10.0, 11.0], ">= min_value, not > min_value"


def test_m3_filter_records_is_lazy(day):
    stream = day.filter_records(endless_records(day), 1.0)
    assert iter(stream) is stream, "a generator, not a list"
    first_three = list(itertools.islice(stream, 3))
    assert [r.value for r in first_three] == [1.0, 2.0, 3.0], (
        "an endless source must work — nothing may call list() on the input"
    )


def test_m3_enrich_records_assigns_the_band_boundaries(day):
    values = [0.0, 9.99, 10.0, 24.999, 25.0, 100.0]
    bands = [r.band for r in day.enrich_records(record(day, value=v) for v in values)]
    assert bands == ["low", "low", "normal", "normal", "high", "high"]


def test_m3_enrich_records_does_not_mutate_its_input(day):
    original = record(day, value=15.0)
    enriched = list(day.enrich_records([original]))[0]
    assert enriched.band == "normal"
    assert original.band == "", "use dataclasses.replace — Record is frozen"
    assert enriched is not original


def test_m3_enrich_records_is_lazy(day):
    stream = day.enrich_records(endless_records(day))
    assert iter(stream) is stream, "a generator, not a list"
    assert list(itertools.islice(stream, 2))[1].band == "low"


def test_m3_aggregate_of_nothing(day):
    assert day.aggregate([]) == {
        "total": 0,
        "sensors": {},
        "bands": {},
        "regions": {},
        "span": ("", ""),
    }


def test_m3_aggregate_summarises_per_sensor(day):
    records = [
        record(day, sensor="s1", value=21.5, hour=13),
        record(day, sensor="s1", value=30.0, hour=14),
        record(day, sensor="s1", value=9.25, hour=15),
        record(day, sensor="s2", value=19.0, hour=12),
    ]
    summary = day.aggregate(day.enrich_records(records))
    assert summary["total"] == 4
    assert summary["sensors"]["s1"] == {
        "count": 3,
        "mean": 20.25,
        "min": 9.25,
        "max": 30.0,
    }, f"got {summary['sensors']['s1']!r}"
    assert summary["sensors"]["s2"]["mean"] == 19.0


def test_m3_aggregate_rounds_the_mean_to_three_places(day):
    records = [record(day, value=1.0), record(day, value=2.0), record(day, value=2.0)]
    assert day.aggregate(records)["sensors"]["s1"]["mean"] == 1.667


def test_m3_aggregate_orders_bands_and_regions(day):
    records = [
        record(day, sensor="s1", value=21.5, region="eu"),
        record(day, sensor="s1", value=30.0, region="eu"),
        record(day, sensor="s1", value=9.25, region="unknown"),
        record(day, sensor="s2", value=19.0, region="us"),
        record(day, sensor="s3", value=12.5, region="eu"),
    ]
    summary = day.aggregate(day.enrich_records(records))
    assert summary["bands"] == {"normal": 3, "high": 1, "low": 1}
    assert list(summary["bands"]) == ["normal", "high", "low"], (
        "count descending, then band name ascending"
    )
    assert list(summary["regions"]) == ["eu", "unknown", "us"], f"got {summary['regions']!r}"


def test_m3_aggregate_reports_the_time_span(day):
    records = [
        record(day, hour=14),
        record(day, hour=12),
        record(day, hour=13, minute=30),
    ]
    assert day.aggregate(records)["span"] == (
        "2024-03-15T12:00:00+00:00",
        "2024-03-15T14:00:00+00:00",
    )


def test_m3_aggregate_consumes_a_generator_once(day):
    records = (record(day, value=float(n)) for n in (1, 2, 3))
    summary = day.aggregate(records)
    assert summary["total"] == 3, "a second pass over a generator sees nothing"
    assert summary["sensors"]["s1"]["count"] == 3


def test_m3_run_transform_chains_the_stages(day):
    records = [record(day, value=5.0), record(day, value=15.0), record(day, value=40.0)]
    kept, summary = day.run_transform(records, 10.0)
    assert [r.value for r in kept] == [15.0, 40.0], "filtered"
    assert [r.band for r in kept] == ["normal", "high"], "then enriched"
    assert summary["total"] == 2, "the summary describes what survived the filter"
    assert summary["bands"] == {"high": 1, "normal": 1}


def test_m3_run_transform_reads_the_input_exactly_once(day):
    pulled = 0

    def counted():
        nonlocal pulled
        for value in (1.0, 20.0, 30.0):
            pulled += 1
            yield record(day, value=value)

    kept, summary = day.run_transform(counted(), 10.0)
    assert pulled == 3, f"the source was read {pulled} times, expected 3 (one pass)"
    assert len(kept) == 2 and summary["total"] == 2


def test_m3_run_transform_of_an_empty_stream(day):
    kept, summary = day.run_transform(iter([]), 0.0)
    assert kept == []
    assert summary["total"] == 0 and summary["span"] == ("", "")


# ===========================================================================
# M4 — load
# ===========================================================================
def test_m4_connect_creates_the_schema(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        columns = [
            row[1] for row in connection.execute("PRAGMA table_info(readings)").fetchall()
        ]
        assert columns == ["id", "sensor", "value", "taken", "region", "band"], columns
        assert connection.row_factory is sqlite3.Row, "row_factory must be sqlite3.Row"
    finally:
        connection.close()
    assert (tmp_path / "pipe.db").is_file()


def test_m4_connect_is_repeatable_and_supports_memory(day, tmp_path):
    path = tmp_path / "pipe.db"
    first = day.connect(path)
    second = day.connect(path)  # must not raise "table already exists"
    memory = day.connect(":memory:")
    try:
        assert day.count_rows(first) == 0
        assert day.count_rows(second) == 0
        assert day.count_rows(memory) == 0
    finally:
        first.close()
        second.close()
        memory.close()


def test_m4_upsert_records_writes_rows(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        records = [
            record(day, sensor="s1", value=21.5, hour=13),
            record(day, sensor="s2", value=19.0, hour=13),
        ]
        assert day.upsert_records(connection, records) == 2
        assert day.count_rows(connection) == 2
    finally:
        connection.close()
    rows = stored_readings(tmp_path / "pipe.db")
    assert rows[0]["sensor"] == "s1"
    assert rows[0]["taken"] == "2024-03-15T13:00:00+00:00", "store an aware UTC ISO string"


def test_m4_upsert_records_is_idempotent(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        records = [
            record(day, sensor="s1", value=21.5, hour=13),
            record(day, sensor="s1", value=30.0, hour=14),
            record(day, sensor="s2", value=19.0, hour=13),
        ]
        assert day.upsert_records(connection, records) == 3
        first = day.count_rows(connection)
        assert day.upsert_records(connection, records) == 3
        assert day.count_rows(connection) == first == 3, (
            "re-running must update rows, not duplicate them — check UNIQUE(sensor, taken)"
        )
    finally:
        connection.close()


def test_m4_upsert_records_updates_a_changed_value(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        day.upsert_records(connection, [record(day, value=21.5, band="normal")])
        day.upsert_records(connection, [record(day, value=99.5, region="us", band="high")])
        assert day.count_rows(connection) == 1
    finally:
        connection.close()
    row = stored_readings(tmp_path / "pipe.db")[0]
    assert row["value"] == 99.5, "ON CONFLICT DO UPDATE must overwrite the value"
    assert row["region"] == "us"
    assert row["band"] == "high"


def test_m4_upsert_records_batches_and_accepts_a_generator(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        stream = (record(day, value=float(n), hour=n) for n in range(5))
        assert day.upsert_records(connection, stream, batch_size=2) == 5
        assert day.count_rows(connection) == 5
        assert day.upsert_records(connection, []) == 0
    finally:
        connection.close()


def test_m4_upsert_records_rejects_a_zero_batch_size(day, tmp_path):
    connection = day.connect(":memory:")
    try:
        with pytest.raises(ValueError):
            day.upsert_records(connection, [record(day)], batch_size=0)
    finally:
        connection.close()


def test_m4_sensor_stats_describes_one_sensor(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        day.upsert_records(
            connection,
            [
                record(day, sensor="s1", value=21.5, hour=13),
                record(day, sensor="s1", value=30.0, hour=14),
                record(day, sensor="s1", value=9.25, hour=15),
                record(day, sensor="s2", value=19.0, hour=13),
            ],
        )
        assert day.sensor_stats(connection, "s1") == {
            "sensor": "s1",
            "count": 3,
            "mean": 20.25,
            "min": 9.25,
            "max": 30.0,
        }
        assert day.sensor_stats(connection, "nope") is None
    finally:
        connection.close()


def test_m4_sensor_stats_is_injection_proof(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        day.upsert_records(connection, [record(day, sensor="s1", value=1.0)])
        assert day.sensor_stats(connection, "x' OR '1'='1") is None, (
            "use a ? placeholder: hostile input is a sensor name, not SQL"
        )
        assert day.sensor_stats(connection, "'; DROP TABLE readings; --") is None
        assert day.count_rows(connection) == 1, "the table is still there"
    finally:
        connection.close()


def test_m4_top_sensors_orders_by_count_then_name(day, tmp_path):
    connection = day.connect(tmp_path / "pipe.db")
    try:
        day.upsert_records(
            connection,
            [
                record(day, sensor="s1", value=21.5, hour=13),
                record(day, sensor="s1", value=30.0, hour=14),
                record(day, sensor="s1", value=9.25, hour=15),
                record(day, sensor="s3", value=12.5, hour=13),
                record(day, sensor="s2", value=19.0, hour=13),
            ],
        )
        assert day.top_sensors(connection, 2) == [
            {"sensor": "s1", "count": 3, "mean": 20.25},
            {"sensor": "s2", "count": 1, "mean": 19.0},
        ], "ties break on the sensor name ascending"
        assert len(day.top_sensors(connection, 99)) == 3, "a big limit is not an error"
        assert day.top_sensors(connection, 0) == []
    finally:
        connection.close()


def test_m4_top_sensors_of_an_empty_database(day):
    connection = day.connect(":memory:")
    try:
        assert day.top_sensors(connection) == []
    finally:
        connection.close()


# ===========================================================================
# M5 — report and CLI
# ===========================================================================
EXPECTED_TABLE = "sensor  count   mean\n------  -----  -----\ns1          3  21.53\ns2          1   19.0"


def test_m5_format_table_matches_the_brief(day):
    got = day.format_table(["sensor", "count", "mean"], [["s1", 3, 21.53], ["s2", 1, 19.0]])
    assert got == EXPECTED_TABLE, f"\ngot:\n{got}\nwant:\n{EXPECTED_TABLE}"


def test_m5_format_table_has_no_trailing_whitespace(day):
    got = day.format_table(["sensor", "note"], [["s1", "ok"], ["a-very-long-sensor", "x"]])
    assert not got.endswith("\n"), "no trailing newline"
    for line in got.splitlines():
        assert line == line.rstrip(), f"trailing whitespace in {line!r}"


def test_m5_format_table_pads_to_the_widest_cell(day):
    got = day.format_table(["id"], [["a"], ["bbbb"]]).splitlines()
    assert got == ["id  ".rstrip(), "----", "a", "bbbb"], got


def test_m5_format_table_with_no_rows(day):
    assert day.format_table(["sensor", "count"], []) == "sensor  count\n------  -----"


def test_m5_build_parser_defaults(day):
    parser = day.build_parser()
    assert parser.prog == "sensorpipe"
    run = parser.parse_args(["run"])
    assert run.command == "run" and run.limit == 0 and run.verbose is False
    assert parser.parse_args(["report"]).limit == 5
    assert parser.parse_args(["stats", "--sensor", "s1"]).sensor == "s1"


def test_m5_build_parser_takes_verbose_before_the_subcommand(day):
    args = day.build_parser().parse_args(["-v", "report", "--limit", "3"])
    assert args.verbose is True
    assert args.command == "report" and args.limit == 3


def test_m5_build_parser_requires_a_subcommand_and_a_sensor(day):
    parser = day.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
    with pytest.raises(SystemExit):
        parser.parse_args(["stats"])


def test_m5_main_run_stores_the_pipeline_output(day, tmp_path, capsys):
    source = FakeSource()
    code = day.main(["run"], fetch=source, env=env_for(tmp_path))
    printed = capsys.readouterr().out
    assert code == 0, f"run failed; output was:\n{printed}"
    assert source.calls == [BASE_URL, PAGE_TWO_URL]
    rows = stored_readings(tmp_path / "sensorpipe.db")
    assert len(rows) == GOOD_RECORD_COUNT
    assert {row["band"] for row in rows} == {"low", "normal", "high"}, "bands were enriched"
    assert "stored" in printed and "quarantined" in printed, f"summary was:\n{printed}"


def test_m5_main_run_twice_is_idempotent(day, tmp_path, capsys):
    env = env_for(tmp_path)
    assert day.main(["run"], fetch=FakeSource(), env=env) == 0
    first = stored_readings(tmp_path / "sensorpipe.db")
    assert day.main(["run"], fetch=FakeSource(), env=env) == 0
    second = stored_readings(tmp_path / "sensorpipe.db")
    capsys.readouterr()
    assert len(first) == len(second) == GOOD_RECORD_COUNT, (
        f"a second run changed the row count: {len(first)} -> {len(second)}"
    )
    assert first == second, "a second run must not change the stored data either"


def test_m5_main_run_honours_the_limit(day, tmp_path, capsys):
    code = day.main(["run", "--limit", "2"], fetch=FakeSource(), env=env_for(tmp_path))
    capsys.readouterr()
    assert code == 0
    assert len(stored_readings(tmp_path / "sensorpipe.db")) == 2


def test_m5_main_run_honours_min_value(day, tmp_path, capsys):
    env = env_for(tmp_path, SENSORPIPE_MIN_VALUE="15")
    assert day.main(["run"], fetch=FakeSource(), env=env) == 0
    capsys.readouterr()
    values = [row["value"] for row in stored_readings(tmp_path / "sensorpipe.db")]
    assert sorted(values) == [19.0, 21.5, 30.0], f"9.25 and 12.5 are below 15: {values}"


def test_m5_main_run_reports_a_failed_extraction(day, tmp_path, capsys):
    code = day.main(["run"], fetch=FakeSource(always=(500, {})), env=env_for(tmp_path))
    capsys.readouterr()
    assert code == 1, "errors and nothing stored is exit code 1"


def test_m5_main_run_survives_bad_records(day, tmp_path, capsys):
    only_bad = {"items": [{"sensor": "s4", "value": "abc", "taken": "2024-03-15T13:00:00Z"}]}
    source = FakeSource(pages={BASE_URL: (200, only_bad)})
    code = day.main(["run"], fetch=source, env=env_for(tmp_path))
    capsys.readouterr()
    assert code == 0, "quarantined records are not an error"
    assert stored_readings(tmp_path / "sensorpipe.db") == []


def test_m5_main_report_prints_a_table(day, tmp_path, capsys):
    env = env_for(tmp_path)
    day.main(["run"], fetch=FakeSource(), env=env)
    capsys.readouterr()
    assert day.main(["report", "--limit", "2"], env=env) == 0
    printed = capsys.readouterr().out
    assert "sensor" in printed and "count" in printed and "mean" in printed
    assert "s1" in printed
    lines = [line for line in printed.splitlines() if line.strip()]
    assert lines[1].startswith("---"), f"row two is the rule: {lines!r}"


def test_m5_main_stats_prints_one_sensor(day, tmp_path, capsys):
    env = env_for(tmp_path)
    day.main(["run"], fetch=FakeSource(), env=env)
    capsys.readouterr()
    assert day.main(["stats", "--sensor", "s1"], env=env) == 0
    printed = capsys.readouterr().out
    assert "s1" in printed
    assert "20.25" in printed, f"the mean of s1 is 20.25: {printed!r}"


def test_m5_main_stats_of_an_unknown_sensor(day, tmp_path, capsys):
    env = env_for(tmp_path)
    day.main(["run"], fetch=FakeSource(), env=env)
    capsys.readouterr()
    assert day.main(["stats", "--sensor", "nope"], env=env) == 2


def test_m5_main_reports_a_configuration_error(day, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    code = day.main(["report"], env=env_for(tmp_path, SENSORPIPE_BATCH_SIZE="0"))
    assert code == 2, "a bad setting is a user error: exit 2, no traceback"
    assert "SENSORPIPE_BATCH_SIZE" in caplog.text, (
        f"log the message that names the variable; logged: {caplog.text!r}"
    )


def test_m5_main_verbose_still_returns_zero(day, tmp_path, capsys):
    assert day.main(["-v", "run"], fetch=FakeSource(), env=env_for(tmp_path)) == 0
    capsys.readouterr()


def test_m5_main_never_calls_sys_exit(day, tmp_path, capsys):
    env = env_for(tmp_path)
    for argv in (["run"], ["report"], ["stats", "--sensor", "nope"]):
        result = day.main(argv, fetch=FakeSource(), env=env)
        assert isinstance(result, int), f"main({argv!r}) returned {result!r}, not an int"
    capsys.readouterr()
