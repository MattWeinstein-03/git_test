"""M5 — reporting.

One function, and it is pure: values in, string out. That is what makes the CLI
testable with a single assertion and what lets the same table go to a terminal, a
log file or an email without changing anything here.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

COLUMN_GAP = "  "


def _is_number(value: Any) -> bool:
    """True for ints and floats, but not for bools (which are ints in Python)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def format_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Render an aligned plain-text table.

    Columns are padded to their widest cell (header included) and joined by two
    spaces. Numeric columns are right-aligned, everything else left-aligned. No
    line has trailing whitespace and the result has no trailing newline.
    """
    text_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(str(header)) for header in headers]
    for row in text_rows:
        for index, cell in enumerate(row):
            if index < len(widths):
                widths[index] = max(widths[index], len(cell))

    numeric = []
    for index in range(len(headers)):
        column = [row[index] for row in rows if index < len(row)]
        # why: alignment follows the data, not the header, and an empty column has
        # no data to follow — left-align it.
        numeric.append(bool(column) and all(_is_number(cell) for cell in column))

    def render(cells: Sequence[str]) -> str:
        parts = []
        for index, cell in enumerate(cells):
            width = widths[index] if index < len(widths) else len(cell)
            right = numeric[index] if index < len(numeric) else False
            parts.append(cell.rjust(width) if right else cell.ljust(width))
        # why: padding the last column would leave trailing spaces, which show up
        # in diffs, in test failures and in copied output. Strip the right edge.
        return COLUMN_GAP.join(parts).rstrip()

    lines = [render([str(header) for header in headers])]
    lines.append(COLUMN_GAP.join("-" * width for width in widths).rstrip())
    lines.extend(render(row) for row in text_rows)
    return "\n".join(lines)
