# Text & Data Toolkit

A small command-line text analyser: normalise a block of text, count its words,
rank the most frequent ones, compute a handful of statistics, and print one
column-aligned report. Built for Day 07 of python-zero-to-hero — the Week 1
capstone — using nothing but the core language from Days 01–06.

No installation, no configuration, no data files. The text it analyses lives in
the module as `SAMPLE_TEXT`, because reading text out of a file is Day 10.

This README is a model — replace it with your own once your version runs.

## Requirements

- Python 3.10 or newer (`python --version`)
- pytest, only for grading: `python -m pip install pytest`

Nothing else. The toolkit brings in no modules at all, not even from the
standard library.

## Run it

From the course root:

```bash
python course/week1/day07_project_text_toolkit/exercises.py
```

Or from inside the project folder:

```bash
cd course/week1/day07_project_text_toolkit
python exercises.py
```

It prints a report for the built-in sample text and exits. There is no menu and
nothing to type — this toolkit takes no input, which is what makes it safe to
run from a test:

```
Text & Data Toolkit — sample text

TEXT REPORT
===========
words               67
unique words        36
sentences            6
avg word length   3.97
longest word    sentences

top 5 words
-----------
it                   6
a                    5
is                   5
the                  5
and                  3
```

Until you have written `main()` you get `NotImplementedError: main` instead, and
until Milestone 5 works `main()` cannot. That is expected: the entry point runs
the finished pipeline. Grade with `python check.py day07` while you build, and
run this command when the checks are green.

## Analyse your own text

Replace `SAMPLE_TEXT` at the top of `exercises.py` with whatever you like — a few
paragraphs of your own writing, a chapter you pasted in, a changelog. Triple
quotes let it run over as many lines as you want:

```python
SAMPLE_TEXT = """
Paste anything here. Ragged    spacing, MIXED case and "punctuation!!"
are all handled — that is what Milestone 1 is for.
"""
```

Then run the file again. Nothing else needs to change, because every function
takes the text as an argument.

## What the numbers mean

| Row | Counts |
|---|---|
| `words` | whitespace-separated pieces, casefolded, with punctuation stripped from each end; pieces that were nothing but punctuation are not words |
| `unique words` | how many different words, by that same definition |
| `sentences` | runs of `.`, `!` or `?`; text with words but no ending character counts as 1; text with no words counts as 0 |
| `avg word length` | mean word length, rounded to 2 decimals |
| `longest word` | the longest word; ties go to the one appearing first |
| `top N words` | the most frequent words, highest count first, ties alphabetical; `N` is how many rows are actually shown |

`LESSON.md` states each of these precisely — that document is the contract the
tests grade against, including the exact report layout.

## Grade it

From the course root:

```bash
python check.py day07          # milestone-by-milestone progress
python check.py day07 -v       # with full failure detail
```

Or with pytest directly:

```bash
python -m pytest course/week1/day07_project_text_toolkit -q
```

The checks are named `test_m1_*` … `test_m5_*`, so partial credit is visible:
finish Milestone 1 and its checks pass while the rest still fail. That is the
intended experience — watch the number climb.

To prove to yourself that the suite is passable, grade the reference
implementation instead of your own file:

```bash
PZH_SOLUTIONS=1 python -m pytest course/week1/day07_project_text_toolkit -q
```

## Use it as a library

Every function takes plain arguments and returns plain data, so the analysis
works without the report:

```python
text = "The cat sat. The cat ran! The end?"

clean_text(text)        # 'the cat sat. the cat ran! the end?'
word_counts(text)       # {'the': 3, 'cat': 2, 'sat': 1, 'ran': 1, 'end': 1}
top_words(text, 2)      # [('the', 3), ('cat', 2)]
text_stats(text)        # {'word_count': 8, 'sentence_count': 3, ...}
print(render_report(text, 3))
```

`render_report` returns a string rather than printing one, which is why it can be
tested in a single assertion — and why, on Day 10, you will be able to write it
to a file without touching it.

## Files

| File | What it is |
|---|---|
| `LESSON.md` | the project brief: the `def` primer, milestones M1–M5, hints, the exact report layout, done-checklist |
| `exercises.py` | your implementation, and the program's entry point |
| `solutions.py` | the reference implementation — read it after your attempt |
| `examples.py` | the same pipeline demonstrated on a different dataset (a server log) |
| `test_exercises.py` | the graded checks, `test_m1_*` … `test_m5_*` |
| `README.md` | this file |

## Known limitations

Deliberate, and each one is a later day of the course:

- Sentence counting is a character rule, so `"e.g."` counts as two sentences.
  Doing better needs pattern matching (`re`, Day 17) and a list of
  abbreviations — and is still imperfect.
- The text is embedded in the module. Reading a real document is Day 10.
- Word frequency alone is a weak signal: almost every English document is topped
  by `the`, `a`, `and`, `of`, `to`. Filtering stop words is a stretch goal in
  `LESSON.md`.
- The counting loop would be one call to `collections.Counter`, which arrives on
  Day 17. Writing the loop first is the point of today.
