"""M1 — configuration.

The only module in the project allowed to look at the environment. Everything
downstream receives a validated `Settings` object, so there is exactly one place
where a bad deployment can be caught, and exactly one place to look when a value
is surprising.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

PREFIX = "SENSORPIPE_"

DEFAULTS: dict[str, str] = {
    "URL": "https://example.invalid/v1/readings",
    "DB": "sensorpipe.db",
    "BATCH_SIZE": "100",
    "MAX_PAGES": "10",
    "MIN_VALUE": "0.0",
    "VERBOSE": "0",
}

TRUE_WORDS = {"1", "true", "yes", "on"}
FALSE_WORDS = {"0", "false", "no", "off"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated application configuration.

    Frozen so it cannot drift while the program runs, and hashable so it can be
    passed anywhere without defensive copying.
    """

    source_url: str
    db_path: Path
    batch_size: int
    max_pages: int
    min_value: float
    verbose: bool


def _raw(env: Mapping[str, str], name: str) -> str:
    """Read one setting as text, falling back to the documented default."""
    return env.get(PREFIX + name, DEFAULTS[name])


def _fail(name: str, value: str, expected: str) -> ValueError:
    """Build the error message an operator will actually read."""
    # why: the variable name and the offending value are the two facts the person
    # staring at a failed deployment needs. Never just "invalid configuration".
    return ValueError(f"{PREFIX}{name}={value!r} is invalid: expected {expected}")


def _int_setting(env: Mapping[str, str], name: str, low: int, high: int) -> int:
    raw = _raw(env, name)
    try:
        value = int(raw)
    except ValueError as error:
        raise _fail(name, raw, f"an integer between {low} and {high}") from error
    if not low <= value <= high:
        raise _fail(name, raw, f"an integer between {low} and {high}")
    return value


def _float_setting(env: Mapping[str, str], name: str) -> float:
    raw = _raw(env, name)
    try:
        return float(raw)
    except ValueError as error:
        raise _fail(name, raw, "a number") from error


def _bool_setting(env: Mapping[str, str], name: str) -> bool:
    raw = _raw(env, name)
    cleaned = raw.strip().lower()
    if cleaned in TRUE_WORDS:
        return True
    if cleaned in FALSE_WORDS:
        return False
    raise _fail(name, raw, "one of 1/true/yes/on or 0/false/no/off")


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build `Settings` from a mapping of environment variables.

    Args:
        env: the mapping to read. `None` means `os.environ`, which is the
            production path; tests pass a plain dict, which is why no patching is
            needed anywhere in this project.

    Returns:
        A validated, frozen `Settings`.

    Raises:
        ValueError: on any invalid value, naming the variable and the value.
    """
    source = os.environ if env is None else env

    url = _raw(source, "URL")
    if not url.startswith(("http://", "https://")):
        raise _fail("URL", url, "a URL starting with http:// or https://")

    return Settings(
        source_url=url,
        db_path=Path(_raw(source, "DB")),
        batch_size=_int_setting(source, "BATCH_SIZE", 1, 10_000),
        max_pages=_int_setting(source, "MAX_PAGES", 1, 1_000_000),
        min_value=_float_setting(source, "MIN_VALUE"),
        verbose=_bool_setting(source, "VERBOSE"),
    )
