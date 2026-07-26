"""Text tidying helpers.

This module depends on nothing else in the package, which is what makes it a
safe bottom layer: `stats.py` can import it without any risk of a cycle.
"""

from __future__ import annotations

PUNCTUATION = ".,!?;:\"'()[]"


def strip_punctuation(word: str) -> str:
    """Return `word` without leading or trailing punctuation.

    Examples:
        strip_punctuation("cat.") -> "cat"
        strip_punctuation("'quoted'") -> "quoted"
        strip_punctuation("...") -> ""
    """
    return word.strip(PUNCTUATION)


def normalize(text: str) -> str:
    """Return `text` lowercased with runs of whitespace collapsed to one space.

    Examples:
        normalize("  Hello,   WORLD  ") -> "hello, world"
        normalize("a\\n\\tb") -> "a b"
    """
    # split() with no argument splits on any run of whitespace and drops empties.
    return " ".join(text.lower().split())
