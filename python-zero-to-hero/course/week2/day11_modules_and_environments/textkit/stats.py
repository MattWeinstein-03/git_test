"""Counting helpers built on top of `cleaning`.

Note the RELATIVE import below: `.cleaning` means "the module named cleaning in
my own package". That is why `python textkit/stats.py` fails while
`python -m textkit.stats` works — see LESSON.md section 5.
"""

from __future__ import annotations

from .cleaning import normalize, strip_punctuation


def word_counts(text: str) -> dict[str, int]:
    """Return {word: count} for `text`, cleaned and lowercased.

    Examples:
        word_counts("The cat, the DOG. The cat!") -> {"the": 3, "cat": 2, "dog": 1}
        word_counts("") -> {}
    """
    counts: dict[str, int] = {}
    for raw_word in normalize(text).split():
        word = strip_punctuation(raw_word)
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts


def _rank_key(pair: tuple[str, int]) -> tuple[int, str]:
    """Sort key: most frequent first, then alphabetically for ties."""
    word, count = pair
    return (-count, word)


def top_words(text: str, limit: int = 3) -> list[tuple[str, int]]:
    """Return the `limit` most common (word, count) pairs, highest first.

    Ties are broken alphabetically so the output is predictable.

    Examples:
        top_words("the cat the dog the cat", limit=2) -> [("the", 3), ("cat", 2)]
        top_words("a b", limit=5) -> [("a", 1), ("b", 1)]
    """
    pairs = list(word_counts(text).items())
    pairs.sort(key=_rank_key)
    return pairs[:limit]


def main() -> int:
    """Entry point, so this module is useful from the command line too."""
    sample = "The cat, the DOG. The cat!"
    print(f"counts   -> {word_counts(sample)}")
    print(f"top two  -> {top_words(sample, limit=2)}")
    return 0


if __name__ == "__main__":
    # Only runs when this file is the program: `python -m textkit.stats`.
    raise SystemExit(main())
