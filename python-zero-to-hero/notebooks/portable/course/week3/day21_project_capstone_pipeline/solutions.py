"""Day 21 reference solutions — Project 3: sensorpipe.

The real code is in `pipeline_ref/`, one module per milestone, because that is the
layout the brief asks you to build:

    pipeline_ref/config.py     M1  Settings, load_settings
    pipeline_ref/extract.py    M2  Record, normalise_record, normalise_all,
                                   fetch_page, extract_records
    pipeline_ref/transform.py  M3  filter_records, enrich_records, aggregate,
                                   run_transform
    pipeline_ref/load.py       M4  connect, upsert_records, count_rows,
                                   sensor_stats, top_sensors
    pipeline_ref/report.py     M5  format_table
    pipeline_ref/cli.py        M5  build_parser, main

This module is the thin re-export that makes those names importable as one flat
API surface — exactly what your own `exercises.py` should become once your
`pipeline/` package exists. `# why:` comments live next to the decisions they
explain, in the module that makes them.

Read the modules in milestone order. Run the app with:

    python course/week3/day21_project_capstone_pipeline/solutions.py run --help
"""

from __future__ import annotations

import sys
from pathlib import Path

# why: running this file directly (rather than importing it) leaves the day folder
# out of sys.path on some setups; adding it means `python solutions.py run` works
# from any working directory.
sys.path.insert(0, str(Path(__file__).parent))

from pipeline_ref.cli import build_parser, main  # noqa: E402
from pipeline_ref.config import Settings, load_settings  # noqa: E402
from pipeline_ref.extract import (  # noqa: E402
    Record,
    extract_records,
    fetch_page,
    normalise_all,
    normalise_record,
)
from pipeline_ref.load import (  # noqa: E402
    connect,
    count_rows,
    sensor_stats,
    top_sensors,
    upsert_records,
)
from pipeline_ref.report import format_table  # noqa: E402
from pipeline_ref.transform import (  # noqa: E402
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


if __name__ == "__main__":
    raise SystemExit(main())
