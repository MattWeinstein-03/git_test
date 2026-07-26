"""M2 — extract.

Two jobs: get pages out of an unreliable source (retries, backoff, pagination,
bounded), and turn raw dicts into typed `Record` objects without ever crashing on
bad data. The transport arrives as a parameter, so nothing here knows what HTTP
is.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from pipeline_ref.config import Settings

logger = logging.getLogger(__name__)  # why: no handlers here; main() configures

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

# (status, payload) is all the logic needs from a transport.
Fetch = Callable[[str], "tuple[int, Mapping[str, Any]]"]


@dataclass(frozen=True, slots=True)
class Record:
    """One validated reading. `band` is filled in by the transform stage."""

    sensor: str
    value: float
    taken: datetime
    region: str
    band: str = ""


def _parse_timestamp(text: str) -> datetime:
    """Parse an ISO-8601 timestamp into an aware UTC datetime.

    Accepts a `Z` suffix, an explicit offset, or no zone at all (treated as UTC).
    """
    # why: fromisoformat only accepts "Z" from 3.11, and normalising keeps this
    # working on 3.10 too.
    normalised = text.strip().replace("Z", "+00:00").replace("z", "+00:00")
    parsed = datetime.fromisoformat(normalised)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)  # relabel, do not shift
    return parsed.astimezone(timezone.utc)  # shift to UTC


def normalise_record(raw: Mapping[str, Any]) -> Record:
    """Turn one raw payload item into a `Record`.

    Raises:
        ValueError: if the sensor, value or timestamp is missing or unusable.
    """
    sensor = raw.get("sensor")
    if not isinstance(sensor, str) or not sensor.strip():
        raise ValueError(f"missing or empty sensor in {dict(raw)!r}")

    if "value" not in raw:
        raise ValueError(f"missing value in {dict(raw)!r}")
    try:
        value = float(raw["value"])
    except (TypeError, ValueError) as error:
        # why: float(None) is a TypeError and float("abc") is a ValueError; both
        # mean the same thing to the caller.
        raise ValueError(f"unparseable value in {dict(raw)!r}") from error

    taken_raw = raw.get("taken")
    if not isinstance(taken_raw, str):
        raise ValueError(f"missing timestamp in {dict(raw)!r}")
    try:
        taken = _parse_timestamp(taken_raw)
    except ValueError as error:
        raise ValueError(f"unparseable timestamp {taken_raw!r}") from error

    region = raw.get("region")
    region_text = region.strip().lower() if isinstance(region, str) and region.strip() else "unknown"

    return Record(sensor=sensor.strip(), value=value, taken=taken, region=region_text)


def normalise_all(
    raws: Iterable[Mapping[str, Any]],
) -> tuple[list[Record], list[dict[str, Any]]]:
    """Normalise many records, quarantining the ones that fail.

    Returns:
        (records, quarantined) — quarantined items are the original dicts.
    """
    records: list[Record] = []
    quarantined: list[dict[str, Any]] = []
    for raw in raws:
        try:
            records.append(normalise_record(raw))
        except (ValueError, AttributeError, TypeError) as error:
            # why: one bad row must never end a nightly run. Count it, log it at
            # DEBUG, keep going.
            logger.debug("quarantined record: %s", error)
            quarantined.append(dict(raw) if isinstance(raw, Mapping) else {"raw": raw})
    return records, quarantined


def _backoff_delay(attempt: int, base: float, cap: float = 30.0) -> float:
    """Exponential backoff, capped. No jitter, so tests are deterministic."""
    return float(min(base * 2 ** (attempt - 1), cap))


def fetch_page(
    fetch: Fetch,
    url: str,
    max_attempts: int = 3,
    base_delay: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
) -> Mapping[str, Any]:
    """Fetch one page, retrying transient failures with exponential backoff.

    Args:
        fetch: injected transport returning (status, payload).
        url: the page to fetch.
        max_attempts: total attempts allowed, at least 1.
        base_delay: first backoff delay; 0.0 means "do not wait" (tests).
        sleep: injected, so a test never actually waits.

    Returns:
        The payload from the first 2xx response.

    Raises:
        RuntimeError: when attempts are exhausted or the status is not retryable.
        ValueError: if `max_attempts` is less than 1.
    """
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be at least 1, got {max_attempts}")

    status = -1
    for attempt in range(1, max_attempts + 1):
        status, payload = fetch(url)
        if 200 <= status < 300:
            return payload
        retryable = status in RETRYABLE_STATUS and attempt < max_attempts
        if not retryable:
            break
        delay = _backoff_delay(attempt, base_delay)
        logger.warning("HTTP %s from %s, retrying in %.2fs", status, url, delay)
        if delay:
            sleep(delay)
    raise RuntimeError(f"fetch failed with status {status}")


def extract_records(
    fetch: Fetch,
    settings: Settings,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[list[Record], list[dict[str, Any]], list[str]]:
    """Walk every page from `settings.source_url`, normalising as it goes.

    Returns:
        (records, quarantined, errors). A page-level failure is recorded in
        `errors` as f"{url}: {message}" and stops the walk; it never propagates.
    """
    records: list[Record] = []
    quarantined: list[dict[str, Any]] = []
    errors: list[str] = []

    url: str | None = settings.source_url
    pages = 0
    while url and pages < settings.max_pages:
        try:
            payload = fetch_page(fetch, url, base_delay=0.0, sleep=sleep)
        except Exception as error:  # noqa: BLE001 - report, never propagate
            errors.append(f"{url}: {error}")
            logger.error("extraction stopped at %s: %s", url, error)
            break
        pages += 1
        items = payload.get("items") or []
        good, bad = normalise_all(items)
        records.extend(good)
        quarantined.extend(bad)
        logger.debug("page %s: %d ok, %d quarantined", url, len(good), len(bad))
        url = payload.get("next")

    logger.info(
        "extracted %d records from %d page(s), quarantined %d",
        len(records),
        pages,
        len(quarantined),
    )
    return records, quarantined, errors
