"""Day 17 graded checks — the standard library.

The `day` fixture hands these tests your exercises.py (or solutions.py when
PZH_SOLUTIONS=1 is set). Never import exercises directly.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from itertools import count

import pytest


class _ListHandler(logging.Handler):
    """Collect records so a test can assert on logging without touching files."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _capturing_logger(name: str) -> tuple[logging.Logger, _ListHandler]:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    handler = _ListHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger, handler


# --- exercise 1: top_words ------------------------------------------------


def test_top_words_counts_case_insensitively(day):
    assert day.top_words("the cat, the dog. THE cat!", 2) == [("the", 3), ("cat", 2)]


def test_top_words_breaks_ties_alphabetically(day):
    got = day.top_words("b a b a c", 3)
    assert got == [("a", 2), ("b", 2), ("c", 1)], f"got {got}"


def test_top_words_limit_zero(day):
    assert day.top_words("anything at all", 0) == []


def test_top_words_strips_punctuation_only_at_edges(day):
    got = day.top_words("well-known; well-known.", 1)
    assert got == [("well-known", 2)], f"inner punctuation stays; got {got}"


def test_top_words_empty_text(day):
    assert day.top_words("   ", 5) == []


# --- exercise 2: group_by_initial ----------------------------------------


def test_group_by_initial_groups_case_insensitively(day):
    got = day.group_by_initial(["apple", "Avocado", "beet"])
    assert got == {"a": ["apple", "Avocado"], "b": ["beet"]}, f"got {got}"


def test_group_by_initial_skips_empty_strings(day):
    assert day.group_by_initial(["", "x"]) == {"x": ["x"]}


def test_group_by_initial_returns_plain_dict(day):
    got = day.group_by_initial(["a"])
    assert type(got) is dict, f"return a plain dict, got {type(got).__name__}"


def test_group_by_initial_does_not_default_missing_keys(day):
    got = day.group_by_initial(["a"])
    with pytest.raises(KeyError):
        got["z"]


def test_group_by_initial_preserves_input_order(day):
    got = day.group_by_initial(["zeta", "zulu", "zap"])
    assert got == {"z": ["zeta", "zulu", "zap"]}


# --- exercise 3: last_n_events -------------------------------------------


def test_last_n_events_keeps_the_newest(day):
    assert day.last_n_events(["a", "b", "c", "d", "e"], 3) == ["c", "d", "e"]


def test_last_n_events_short_input(day):
    assert day.last_n_events(["a"], 5) == ["a"]


def test_last_n_events_limit_zero(day):
    assert day.last_n_events(["a", "b"], 0) == []


def test_last_n_events_handles_a_long_stream(day):
    stream = (f"e{i}" for i in range(100_000))
    assert day.last_n_events(stream, 2) == ["e99998", "e99999"]


def test_last_n_events_returns_a_list(day):
    got = day.last_n_events(["a", "b"], 2)
    assert isinstance(got, list), f"got {type(got).__name__}; convert the deque"


# --- exercise 4: group_ids_by_status -------------------------------------


def test_group_ids_by_status_handles_unsorted_input(day):
    records = [
        {"status": "ok", "id": 3},
        {"status": "fail", "id": 2},
        {"status": "ok", "id": 1},
    ]
    got = day.group_ids_by_status(records)
    assert got == {"fail": [2], "ok": [1, 3]}, (
        f"got {got} — did you sort by the group key before calling groupby?"
    )


def test_group_ids_by_status_empty(day):
    assert day.group_ids_by_status([]) == {}


def test_group_ids_by_status_single_status(day):
    records = [{"status": "ok", "id": 9}, {"status": "ok", "id": 4}]
    assert day.group_ids_by_status(records) == {"ok": [4, 9]}


def test_group_ids_by_status_ignores_extra_fields(day):
    records = [{"status": "ok", "id": 1, "note": "x"}]
    assert day.group_ids_by_status(records) == {"ok": [1]}


# --- exercise 5: biggest_swing -------------------------------------------


def test_biggest_swing_finds_largest_absolute_change(day):
    assert day.biggest_swing([("t0", 10.0), ("t1", 12.0), ("t2", 4.0)]) == (
        "t1",
        "t2",
        -8.0,
    )


def test_biggest_swing_two_readings(day):
    assert day.biggest_swing([("a", 1.0), ("b", 3.0)]) == ("a", "b", 2.0)


def test_biggest_swing_only_compares_neighbours(day):
    # 0 -> 100 would be the biggest jump overall, but they are not adjacent.
    readings = [("a", 0.0), ("b", 3.0), ("c", 100.0), ("d", 99.0)]
    assert day.biggest_swing(readings) == ("b", "c", 97.0)


def test_biggest_swing_prefers_the_earliest_tie(day):
    readings = [("a", 0.0), ("b", 5.0), ("c", 10.0)]
    assert day.biggest_swing(readings) == ("a", "b", 5.0)


def test_biggest_swing_rejects_short_input(day):
    with pytest.raises(ValueError):
        day.biggest_swing([("a", 1.0)])


# --- exercise 6: parse_timestamp -----------------------------------------


def test_parse_timestamp_handles_z_suffix(day):
    got = day.parse_timestamp("2024-03-15T13:45:00Z")
    assert got.isoformat() == "2024-03-15T13:45:00+00:00"


def test_parse_timestamp_converts_offsets_to_utc(day):
    got = day.parse_timestamp("2024-03-15T14:45:00+01:00")
    assert got.isoformat() == "2024-03-15T13:45:00+00:00", f"got {got.isoformat()}"


def test_parse_timestamp_treats_naive_as_utc(day):
    got = day.parse_timestamp("2024-03-15T13:45:00")
    assert got.isoformat() == "2024-03-15T13:45:00+00:00"


def test_parse_timestamp_always_returns_aware(day):
    for text in ("2024-01-01T00:00:00", "2024-01-01T00:00:00Z"):
        got = day.parse_timestamp(text)
        assert got.tzinfo is not None, f"{text} produced a naive datetime"
        assert got.utcoffset().total_seconds() == 0


def test_parse_timestamp_result_is_comparable_with_utc(day):
    got = day.parse_timestamp("2024-03-15T13:45:00Z")
    reference = datetime(2024, 3, 15, 13, 45, tzinfo=timezone.utc)
    assert got == reference


def test_parse_timestamp_rejects_nonsense(day):
    with pytest.raises(ValueError):
        day.parse_timestamp("not a timestamp")


# --- exercise 7: busiest_hour --------------------------------------------


def test_busiest_hour_counts_by_utc_hour(day):
    stamps = [
        "2024-03-15T13:00:00Z",
        "2024-03-15T13:59:00Z",
        "2024-03-15T09:00:00Z",
    ]
    assert day.busiest_hour(stamps) == (13, 2)


def test_busiest_hour_ties_prefer_earlier_hour(day):
    assert day.busiest_hour(["2024-03-15T05:00:00Z", "2024-03-15T04:00:00Z"]) == (4, 1)


def test_busiest_hour_normalises_offsets(day):
    # 14:30+01:00 is 13:30 UTC, so both land in hour 13.
    stamps = ["2024-03-15T14:30:00+01:00", "2024-03-15T13:10:00Z"]
    assert day.busiest_hour(stamps) == (13, 2)


def test_busiest_hour_ignores_unparseable(day):
    assert day.busiest_hour(["nonsense", "2024-03-15T07:00:00Z"]) == (7, 1)


def test_busiest_hour_nothing_parsed(day):
    assert day.busiest_hour(["nonsense"]) == (-1, 0)
    assert day.busiest_hour([]) == (-1, 0)


# --- exercise 8: parse_log_line ------------------------------------------


def test_parse_log_line_extracts_named_groups(day):
    got = day.parse_log_line("2024-03-15T13:45:00Z WARNING api.fetch: retrying in 0.5s")
    want = {
        "timestamp": "2024-03-15T13:45:00Z",
        "level": "WARNING",
        "logger": "api.fetch",
        "message": "retrying in 0.5s",
    }
    assert got == want, f"got {got}"


def test_parse_log_line_message_may_contain_colons(day):
    got = day.parse_log_line("2024-03-15T13:45:00Z INFO api: retry: soon")
    assert got["message"] == "retry: soon", f"got {got}"


def test_parse_log_line_rejects_garbage(day):
    assert day.parse_log_line("garbage") is None
    assert day.parse_log_line("") is None


def test_parse_log_line_requires_uppercase_level(day):
    assert day.parse_log_line("2024-03-15T13:45:00Z info api: hello") is None


def test_parse_log_line_tolerates_surrounding_whitespace(day):
    got = day.parse_log_line("  2024-03-15T13:45:00Z INFO api: hello  \n")
    assert got is not None, "leading/trailing whitespace should be ignored"
    assert got["message"] == "hello", f"got {got['message']!r}"


def test_parse_log_line_handles_underscored_logger_names(day):
    got = day.parse_log_line("2024-03-15T13:45:00Z DEBUG my_app.sub_module: ok")
    assert got is not None and got["logger"] == "my_app.sub_module"


# --- exercise 9: build_parser --------------------------------------------


def test_build_parser_defaults(day):
    args = day.build_parser().parse_args(["data.csv"])
    got = (args.source, args.limit, args.format, args.verbose, args.tag)
    assert got == ("data.csv", 10, "text", False, []), f"got {got}"


def test_build_parser_parses_options(day):
    args = day.build_parser().parse_args(
        ["d.csv", "-l", "2", "--format", "json", "-v", "--tag", "x", "--tag", "y"]
    )
    assert (args.limit, args.format, args.verbose, args.tag) == (2, "json", True, ["x", "y"])


def test_build_parser_limit_is_an_int(day):
    args = day.build_parser().parse_args(["d.csv", "--limit", "7"])
    assert args.limit == 7
    assert isinstance(args.limit, int), "use type=int so argparse converts for you"


def test_build_parser_rejects_bad_limit(day):
    with pytest.raises(SystemExit):
        day.build_parser().parse_args(["d.csv", "--limit", "abc"])


def test_build_parser_rejects_bad_format_choice(day):
    with pytest.raises(SystemExit):
        day.build_parser().parse_args(["d.csv", "--format", "xml"])


def test_build_parser_requires_source(day):
    with pytest.raises(SystemExit):
        day.build_parser().parse_args([])


def test_build_parser_program_name(day):
    assert day.build_parser().prog == "report"


# --- exercise 10: summarise_log ------------------------------------------

SAMPLE = [
    "2024-03-15T13:00:00Z INFO api: mail a@b.com queued",
    "2024-03-15T13:30:00Z ERROR api: boom",
    "rubbish",
]


def test_summarise_log_counts_totals_and_bad_lines(day):
    logger, _ = _capturing_logger("pzh.day17.totals")
    summary = day.summarise_log(SAMPLE, logger, limit=2)
    assert (summary["total"], summary["bad"]) == (3, 1), f"got {summary}"


def test_summarise_log_counts_levels_deterministically(day):
    logger, _ = _capturing_logger("pzh.day17.levels")
    lines = [
        "2024-03-15T13:00:00Z INFO api: a",
        "2024-03-15T13:00:00Z ERROR api: b",
        "2024-03-15T13:00:00Z ERROR api: c",
        "2024-03-15T13:00:00Z DEBUG api: d",
    ]
    summary = day.summarise_log(lines, logger)
    assert summary["levels"] == {"ERROR": 2, "DEBUG": 1, "INFO": 1}
    assert list(summary["levels"]) == ["ERROR", "DEBUG", "INFO"], (
        f"order must be count desc then name asc; got {list(summary['levels'])}"
    )


def test_summarise_log_redacts_emails(day):
    logger, _ = _capturing_logger("pzh.day17.redact")
    summary = day.summarise_log(SAMPLE, logger, limit=2)
    assert summary["recent"] == ["mail <redacted> queued", "boom"], f"got {summary['recent']}"


def test_summarise_log_reports_busiest_hour(day):
    logger, _ = _capturing_logger("pzh.day17.busiest")
    summary = day.summarise_log(SAMPLE, logger)
    assert summary["busiest"] == (13, 2), f"got {summary['busiest']}"


def test_summarise_log_warns_once_per_bad_line(day):
    logger, handler = _capturing_logger("pzh.day17.warn")
    day.summarise_log(["rubbish", "also rubbish"], logger)
    assert len(handler.records) == 2, f"expected 2 warnings, got {len(handler.records)}"
    assert all(r.levelno == logging.WARNING for r in handler.records)


def test_summarise_log_uses_deferred_formatting(day):
    logger, handler = _capturing_logger("pzh.day17.deferred")
    day.summarise_log(["rubbish"], logger)
    record = handler.records[0]
    assert record.args == ("rubbish",), (
        "pass the line as a %s argument, not an f-string; "
        f"record.args was {record.args!r}"
    )
    assert record.getMessage() == "unparseable line: rubbish"


def test_summarise_log_recent_is_bounded(day):
    logger, _ = _capturing_logger("pzh.day17.recent")
    lines = [f"2024-03-15T0{i}:00:00Z INFO api: m{i}" for i in range(1, 6)]
    summary = day.summarise_log(lines, logger, limit=2)
    assert summary["recent"] == ["m4", "m5"], f"got {summary['recent']}"


def test_summarise_log_handles_empty_input(day):
    logger, handler = _capturing_logger("pzh.day17.empty")
    summary = day.summarise_log([], logger)
    assert summary == {
        "total": 0,
        "bad": 0,
        "levels": {},
        "busiest": (-1, 0),
        "recent": [],
    }, f"got {summary}"
    assert handler.records == []


def test_summarise_log_streams_input(day):
    logger, _ = _capturing_logger("pzh.day17.stream")
    lines = (f"2024-03-15T13:00:00Z INFO api: m{i}" for i in count())
    bounded = (line for line, _ in zip(lines, range(5_000)))
    summary = day.summarise_log(bounded, logger, limit=1)
    assert summary["total"] == 5_000
    assert summary["recent"] == ["m4999"]
