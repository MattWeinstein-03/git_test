"""Day 15 reference solutions.

Same signatures and docstrings as exercises.py. Read these *after* your own
attempt; `# why:` comments mark the choices that are not obvious.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator


def squares_of_evens(numbers: Iterable[int]) -> list[int]:
    """Return the square of every even number, in the original order.

    Examples:
        >>> squares_of_evens([1, 2, 3, 4])
        [4, 16]
    """
    return [n * n for n in numbers if n % 2 == 0]


def word_lengths(words: Iterable[str]) -> dict[str, int]:
    """Map each word to its length, ignoring words shorter than 3 characters.

    Examples:
        >>> word_lengths(["yield", "is", "lazy"])
        {'yield': 5, 'lazy': 4}
    """
    return {word: len(word) for word in words if len(word) >= 3}


def unique_domains(emails: Iterable[str]) -> set[str]:
    """Return the set of lowercase domains from a list of email addresses.

    Examples:
        >>> sorted(unique_domains(["a@Example.com", "c@other.org"]))
        ['example.com', 'other.org']
    """
    # why: count("@") == 1 rejects both "no-at" and "a@b@c" in one condition,
    # which keeps the filter honest and the split unambiguous.
    return {
        address.split("@")[1].lower()
        for address in emails
        if address.count("@") == 1
    }


def flatten_matrix(matrix: Iterable[Iterable[int]]) -> list[int]:
    """Flatten one level of nesting, left to right, keeping only positive values.

    Examples:
        >>> flatten_matrix([[1, -2, 3], [4, 0]])
        [1, 3, 4]
    """
    return [value for row in matrix for value in row if value > 0]


class Countdown:
    """An iterator that counts down from `start` to 1, written by hand.

    Examples:
        >>> list(Countdown(3))
        [3, 2, 1]
    """

    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self) -> Countdown:
        # why: an iterator is its own iterable, so `for n in Countdown(3)` works
        # and `iter(c) is c` holds. Returning a new object here would let the
        # same Countdown be looped twice and quietly break the protocol.
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


def running_totals(numbers: Iterable[float]) -> Iterator[float]:
    """Yield the cumulative sum after each input value, lazily.

    Examples:
        >>> list(running_totals([1, 2, 3]))
        [1, 3, 6]
    """
    total: float = 0
    for number in numbers:
        total += number
        yield total  # why: yield inside the loop keeps memory at one accumulator


def take(iterable: Iterable[object], n: int) -> list[object]:
    """Return the first `n` items as a list, without over-consuming the source.

    Examples:
        >>> take([10, 20, 30], 2)
        [10, 20]
    """
    if n <= 0:
        # why: returning early means we never call iter(), so an infinite source
        # is not even touched.
        return []
    result: list[object] = []
    for item in iterable:
        result.append(item)
        if len(result) >= n:
            break  # why: the break is what makes an endless source survivable
    return result


def chunked(iterable: Iterable[object], size: int) -> Iterator[list[object]]:
    """Return an iterator of consecutive lists of at most `size` items.

    Examples:
        >>> list(chunked([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    if size < 1:
        raise ValueError(f"size must be at least 1, got {size}")

    # why: `chunked` itself has no `yield`, so the ValueError above fires at call
    # time. The lazy part lives in the inner generator.
    def generate() -> Iterator[list[object]]:
        batch: list[object] = []
        for item in iterable:
            batch.append(item)
            if len(batch) == size:
                yield batch
                batch = []  # why: a fresh list, so the caller can keep the old one
        if batch:
            yield batch

    return generate()


def flatten_deep(nested: Iterable[object]) -> Iterator[object]:
    """Yield every non-list leaf value at any depth, left to right.

    Examples:
        >>> list(flatten_deep([1, [2, [3, [4]], 5], 6]))
        [1, 2, 3, 4, 5, 6]
    """
    for item in nested:
        if isinstance(item, list):
            yield from flatten_deep(item)  # why: stays lazy at every depth
        else:
            yield item


def _parse_lines(lines: Iterable[str]) -> Iterator[tuple[str, float] | None]:
    """Yield (sensor_id, value) for good lines and None for quarantined ones.

    Kept as its own generator stage so `stream_report` stays readable: one stage
    parses, the other counts.
    """
    for raw in lines:
        line = raw.strip()
        if not line:
            yield None
            continue
        parts = line.split(",")
        if len(parts) != 3:
            yield None
            continue
        try:
            value = float(parts[2])
        except ValueError:
            yield None
            continue
        yield parts[0], value


def stream_report(lines: Iterable[str], cutoff: float) -> dict[str, object]:
    """Aggregate a stream of CSV-ish sensor lines into one summary dict.

    Examples:
        >>> stream_report(["s1,temp,21.5", "junk"], 20.0)["kept"]
        1
    """
    kept = 0
    skipped = 0
    total = 0.0
    sensors: dict[str, int] = {}

    for parsed in _parse_lines(lines):
        if parsed is None:
            skipped += 1
            continue
        sensor_id, value = parsed
        if value <= cutoff:
            continue  # well formed but uninteresting: neither kept nor skipped
        kept += 1
        total += value
        # why: .get avoids a branch and mirrors the Day 6 counting pattern
        sensors[sensor_id] = sensors.get(sensor_id, 0) + 1

    return {
        "kept": kept,
        "skipped": skipped,
        "total": total,
        "mean": total / kept if kept else 0.0,
        "sensors": sensors,
    }


if __name__ == "__main__":
    print("Solutions module. Run `python check.py day15` to grade exercises.py.")
