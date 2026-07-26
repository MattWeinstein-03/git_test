"""M3 — transform.

Three stages, chained lazily: filter, then enrich, then aggregate. The first two
are generators, so peak memory does not depend on how many records the source
has. The aggregate holds one fixed-size summary and nothing else.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import replace
from datetime import datetime
from typing import Any

from pipeline_ref.extract import Record

logger = logging.getLogger(__name__)

LOW_BAND_BELOW = 10.0
HIGH_BAND_FROM = 25.0


def band_for(value: float) -> str:
    """Name the band a value falls into: "low", "normal" or "high"."""
    if value < LOW_BAND_BELOW:
        return "low"
    if value < HIGH_BAND_FROM:
        return "normal"
    return "high"


def filter_records(records: Iterable[Record], min_value: float) -> Iterator[Record]:
    """Yield the records whose value is >= `min_value`."""
    for record in records:
        if record.value >= min_value:
            yield record
        # why: no else-branch logging. One log line per dropped record turns a
        # million-row run into a gigabyte of noise; the aggregate counts instead.


def enrich_records(records: Iterable[Record]) -> Iterator[Record]:
    """Yield copies of the records with `band` filled in."""
    for record in records:
        # why: Record is frozen, so this is a new object rather than a mutation.
        # replace() keeps every other field without repeating the field list.
        yield replace(record, band=band_for(record.value))


def _ordered(counter: Counter[str]) -> dict[str, int]:
    """Counter -> dict ordered by count descending, then key ascending."""
    # why: most_common alone leaves ties in insertion order, which makes output
    # depend on the order rows happened to arrive in. Sort explicitly.
    return {key: count for key, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))}


def aggregate(records: Iterable[Record]) -> dict[str, Any]:
    """Consume the stream once and return a summary of it.

    Returns a dict with "total", "sensors", "bands", "regions" and "span".
    """
    total = 0
    sums: defaultdict[str, float] = defaultdict(float)
    counts: Counter[str] = Counter()
    lowest: dict[str, float] = {}
    highest: dict[str, float] = {}
    bands: Counter[str] = Counter()
    regions: Counter[str] = Counter()
    earliest: datetime | None = None
    latest: datetime | None = None

    for record in records:
        # why: everything is accumulated in this single pass. A second `for` over
        # `records` would see an exhausted iterator and report zeros.
        total += 1
        sensor = record.sensor
        sums[sensor] += record.value
        counts[sensor] += 1
        if sensor not in lowest or record.value < lowest[sensor]:
            lowest[sensor] = record.value
        if sensor not in highest or record.value > highest[sensor]:
            highest[sensor] = record.value
        bands[record.band] += 1
        regions[record.region] += 1
        if earliest is None or record.taken < earliest:
            earliest = record.taken
        if latest is None or record.taken > latest:
            latest = record.taken

    sensors: dict[str, dict[str, float | int]] = {}
    for sensor in sorted(counts):
        sensors[sensor] = {
            "count": counts[sensor],
            "mean": round(sums[sensor] / counts[sensor], 3),
            "min": lowest[sensor],
            "max": highest[sensor],
        }

    span = ("", "") if earliest is None or latest is None else (earliest.isoformat(), latest.isoformat())
    logger.debug("aggregated %d record(s) over %d sensor(s)", total, len(sensors))
    return {
        "total": total,
        "sensors": sensors,
        "bands": _ordered(bands),
        "regions": _ordered(regions),
        "span": span,
    }


def run_transform(
    records: Iterable[Record], min_value: float
) -> tuple[list[Record], dict[str, Any]]:
    """Chain the stages and return (enriched records, summary).

    The input is iterated exactly once: the summary and the returned list are
    produced by the same pass.
    """
    kept: list[Record] = []

    def tap(stream: Iterable[Record]) -> Iterator[Record]:
        # why: the caller wants the records AND a summary, but the stream can only
        # be walked once. Collecting as it passes through costs one pass, not two.
        for record in stream:
            kept.append(record)
            yield record

    chain = tap(enrich_records(filter_records(records, min_value)))
    summary = aggregate(chain)  # nothing has been read until this line runs
    return kept, summary
