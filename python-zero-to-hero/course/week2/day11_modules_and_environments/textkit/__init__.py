"""textkit — small text-cleaning helpers.

This file is what makes the directory a package. Its three jobs, in order of
importance:

1. Mark the directory as a regular package.
2. Curate the public API: re-export the few names users need, so they can write
   `textkit.normalize(...)` instead of `textkit.cleaning.normalize(...)`.
3. Hold package metadata such as __version__.

Note the `from . import stats` line: importing a package does NOT automatically
give you its submodules, so without it `textkit.stats` would be an
AttributeError. Keep this file cheap — everything here runs on every import.
"""

from __future__ import annotations

from . import cleaning, stats
from .cleaning import normalize, strip_punctuation
from .stats import top_words, word_counts

__version__ = "0.1.0"
__all__ = [
    "cleaning",
    "normalize",
    "stats",
    "strip_punctuation",
    "top_words",
    "word_counts",
]
