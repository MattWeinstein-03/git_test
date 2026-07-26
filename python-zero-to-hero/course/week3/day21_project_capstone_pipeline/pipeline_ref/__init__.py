"""sensorpipe reference implementation.

This is the package `solutions.py` is built from, and the layout your own
`pipeline/` package should mirror:

    config.py     M1 - settings from the environment, validated once
    extract.py    M2 - retries, pagination, normalisation, quarantine
    transform.py  M3 - generator stages: filter -> enrich -> aggregate
    load.py       M4 - SQLite schema and idempotent upserts
    report.py     M5 - table formatting
    cli.py        M5 - argparse subcommands and main()

Read the code only after your own attempt. Reading the *structure* first is fine
and encouraged.
"""

from pipeline_ref.cli import build_parser, main
from pipeline_ref.config import Settings, load_settings
from pipeline_ref.extract import (
    Record,
    extract_records,
    fetch_page,
    normalise_all,
    normalise_record,
)
from pipeline_ref.load import (
    connect,
    count_rows,
    sensor_stats,
    top_sensors,
    upsert_records,
)
from pipeline_ref.report import format_table
from pipeline_ref.transform import (
    aggregate,
    band_for,
    enrich_records,
    filter_records,
    run_transform,
)

__all__ = [
    "Record",
    "Settings",
    "aggregate",
    "band_for",
    "build_parser",
    "connect",
    "count_rows",
    "enrich_records",
    "extract_records",
    "fetch_page",
    "filter_records",
    "format_table",
    "load_settings",
    "main",
    "normalise_all",
    "normalise_record",
    "run_transform",
    "sensor_stats",
    "top_sensors",
    "upsert_records",
]
