"""M5 — the command line.

`main` is the only function in the project that configures logging, prints, or
decides an exit code. Everything it does is a call into one of the modules above,
in the order the brief lists them: load settings, extract, transform, load,
report.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Mapping, Sequence
from itertools import islice
from typing import Any, Callable

from pipeline_ref.config import Settings, load_settings
from pipeline_ref.extract import extract_records
from pipeline_ref.load import (
    connect,
    count_rows,
    sensor_stats,
    top_sensors,
    upsert_records,
)
from pipeline_ref.report import format_table
from pipeline_ref.transform import run_transform

logger = logging.getLogger("sensorpipe")

Fetch = Callable[[str], "tuple[int, Mapping[str, Any]]"]

LOG_FORMAT = "%(levelname)-8s %(name)s: %(message)s"


def build_parser() -> argparse.ArgumentParser:
    """Build the `sensorpipe` argument parser: run, report, stats."""
    parser = argparse.ArgumentParser(
        prog="sensorpipe",
        description="Fetch, clean, store and report on sensor readings.",
    )
    # why: the global flag is declared on the top-level parser so it works before
    # the subcommand, which is where operators instinctively type it.
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="log at DEBUG instead of INFO"
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="fetch, transform and store readings")
    run.add_argument(
        "--limit", type=int, default=0, help="store at most N records (0 = no limit)"
    )

    report = subcommands.add_parser("report", help="show the busiest sensors")
    report.add_argument("--limit", type=int, default=5, help="how many sensors to show")

    stats = subcommands.add_parser("stats", help="show statistics for one sensor")
    stats.add_argument("--sensor", required=True, help="the sensor to describe")

    return parser


def _configure_logging(verbose: bool) -> None:
    """Set up logging once, for the whole application."""
    # why: basicConfig without force=True leaves an already-configured root alone,
    # so importing this app into a bigger one does not hijack its logging.
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format=LOG_FORMAT)


def _command_run(
    args: argparse.Namespace, settings: Settings, fetch: Fetch
) -> tuple[int, str]:
    """Do the whole pipeline once. Returns (exit code, text to print)."""
    records, quarantined, errors = extract_records(fetch, settings)
    for message in errors:
        logger.error("extract: %s", message)

    kept, summary = run_transform(records, settings.min_value)
    if args.limit and args.limit > 0:
        kept = list(islice(kept, args.limit))
        logger.info("--limit %d: storing %d of %d record(s)", args.limit, len(kept), summary["total"])

    connection = connect(settings.db_path)
    try:
        written = upsert_records(connection, kept, batch_size=settings.batch_size)
        stored = count_rows(connection)
    finally:
        connection.close()

    if errors and written == 0:
        # why: "the source broke and we saved nothing" is the one case a scheduler
        # must notice, so it is the one case that gets a non-zero exit code.
        logger.error("extraction failed and nothing was stored")
        return 1, format_table(["metric", "value"], [["errors", len(errors)]])

    logger.info("stored %d record(s); %d row(s) in the database", written, stored)
    rows: list[list[Any]] = [
        ["fetched", summary["total"]],
        ["written", written],
        ["stored", stored],
        ["quarantined", len(quarantined)],
        ["errors", len(errors)],
    ]
    span_start, span_end = summary["span"]
    table = format_table(["metric", "value"], rows)
    bands = format_table(
        ["band", "count"], [[band, count] for band, count in summary["bands"].items()]
    )
    window = f"window: {span_start or '-'} .. {span_end or '-'}"
    return 0, "\n".join([table, "", bands, "", window])


def _command_report(args: argparse.Namespace, settings: Settings) -> tuple[int, str]:
    """Print the busiest sensors already in the database."""
    connection = connect(settings.db_path)
    try:
        leaders = top_sensors(connection, limit=args.limit)
    finally:
        connection.close()
    rows = [[item["sensor"], item["count"], item["mean"]] for item in leaders]
    return 0, format_table(["sensor", "count", "mean"], rows)


def _command_stats(args: argparse.Namespace, settings: Settings) -> tuple[int, str]:
    """Print one sensor's statistics, or return 2 when it is unknown."""
    connection = connect(settings.db_path)
    try:
        stats = sensor_stats(connection, args.sensor)
    finally:
        connection.close()
    if stats is None:
        logger.error("unknown sensor: %s", args.sensor)
        return 2, ""
    rows = [[stats["sensor"], stats["count"], stats["mean"], stats["min"], stats["max"]]]
    return 0, format_table(["sensor", "count", "mean", "min", "max"], rows)


def _http_fetch(url: str) -> tuple[int, Mapping[str, Any]]:
    """A real HTTP transport. Only ever built inside the `run` branch."""
    # why: imported here, not at module scope, so the module (and every test)
    # works on a machine that has never installed requests.
    import requests  # noqa: PLC0415 - deliberate lazy import

    response = requests.get(url, timeout=10)
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    return response.status_code, payload


def main(
    argv: Sequence[str] | None = None,
    fetch: Fetch | None = None,
    env: Mapping[str, str] | None = None,
) -> int:
    """Run one `sensorpipe` command and return its exit code."""
    args = build_parser().parse_args(argv)

    try:
        settings = load_settings(env)
    except ValueError as error:
        # why: a misconfigured deployment is a user error, not a bug. One line the
        # operator can act on beats forty lines of traceback.
        _configure_logging(verbose=bool(getattr(args, "verbose", False)))
        logger.error("configuration error: %s", error)
        return 2

    _configure_logging(verbose=args.verbose or settings.verbose)
    logger.debug("settings: %s", settings)

    if args.command == "run":
        transport = fetch if fetch is not None else _http_fetch
        code, output = _command_run(args, settings, transport)
    elif args.command == "report":
        code, output = _command_report(args, settings)
    else:
        code, output = _command_stats(args, settings)

    if output:
        print(output)
    return code


if __name__ == "__main__":  # pragma: no cover - convenience only
    raise SystemExit(main())
