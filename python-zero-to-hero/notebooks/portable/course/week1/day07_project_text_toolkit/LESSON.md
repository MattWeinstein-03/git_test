# Day 07 — Project 1: Text & Data Toolkit

> **Time:** ~5 hours  |  **Prerequisites:** Days 01–06

## What you'll be able to do after today
- Turn a written brief into working code, one independently testable milestone at a time, without being told what to type.
- Normalise messy human text so that every later step can stop worrying about case, spacing and punctuation.
- Count and rank the contents of a document with a dict and a named sort key, including the tie-breaking rule.
- Compute a small set of statistics over the same data and state exactly what each one means.
- Render a fixed-width, column-aligned report with f-string format specs, to a layout somebody else specified.
- Decide, in advance and in writing, what your code does with empty input — and then make it do that.

## Why this matters

This is the first thing you have built that has more than one moving part. Everything up to now has been a single function answering a single question; today six pieces have to agree with each other, and the report at the end is only correct if all of them are.

That is the actual job. Professional work is not a stream of clever one-liners — it is turning a specification into parts that compose, where each part has a definition precise enough to test. The two skills being graded today are "read the brief properly" and "get M1 finished before starting M2". Both of those sound like advice about attitude. They are not; they are the difference between finishing and not finishing.

There is also a diagnostic value in a project like this. Week 1 taught you ten or so ideas. Recognising them in a lesson is easy and means very little. Reaching for the right one, unprompted, when the only thing in front of you is a paragraph of requirements — that is knowledge. Today tells you honestly which of the two you have.

---

## The goal

A **Text & Data Toolkit**: a small command-line program that takes a block of text and answers questions about it. How many words? Which words repeat? How long is the average word? How many sentences? Then it prints one aligned report with the answers.

The text is embedded in `exercises.py` as `SAMPLE_TEXT`. There is no file reading today — `pathlib` and `open()` are Day 10, and the moment you have them you can point this same toolkit at a real document without changing a line of the analysis code. That is not an accident of the exercise; it is the reason the analysis functions take a string rather than a filename.

Scope: about 80–120 lines of your own code across five functions plus a `main()`. Nothing installed, nothing downloaded, nothing imported.

---

## A five-minute `def` primer

Tomorrow, Day 08, is the real lesson on functions: parameters, defaults, scope, return values, type hints, the lot. You have already *used* `def` — every exercise since Day 01 has been a function body you filled in — but nobody has yet explained the shape to you properly.

Today you have to write the whole shape yourself, so here is the working minimum. Not the theory. Just enough to build the toolkit confidently.

### The shape

```python
def word_length(word: str) -> int:
    """How many characters `word` has."""
    return len(word)
```

Reading that line by line:

- `def` starts a definition. It means "here is a named recipe", and running the `def` line does **not** run the body — it only files the recipe under the name.
- `word_length` is the name. It follows the same rules as a variable name (Day 01, section 10): `lower_snake_case`.
- `(word: str)` is the **parameter list**. `word` is a name that will exist inside the function, bound to whatever the caller passes in. The `: str` is a **type hint** — a note to human readers and to tools, saying "a string is expected here". Python does not check it and does not enforce it. Day 08 explains hints properly; today, copy the ones already written in `exercises.py`.
- `-> int` is the hint for what comes back.
- The `:` ends the header, and the indented block below it is the **body** — same indentation rule as `if` and `for` (Day 03).
- The docstring is the `"""..."""` on the first line of the body. It documents what the function does. The ones in `exercises.py` are the specification you are being graded against; leave them there.
- `return` hands a value back to whoever called the function, and stops the function immediately.

### Calling it

```python
n = word_length("toolkit")
print(n)          # 7
```

The value `"toolkit"` is bound to the parameter `word`, the body runs, and `return len(word)` sends `7` back. The name `n` is bound to that 7.

### The four things that catch everyone

**1. `return` is not `print`.** This is the single most common Week-1 misunderstanding, and today it will cost you a milestone if you get it wrong.

```python
def bad_double(n: int) -> int:
    print(n * 2)          # displays it, hands back nothing

def good_double(n: int) -> int:
    return n * 2          # hands the value back

print(bad_double(5))      # 10, then None  <- the 10 came from the inner print
print(good_double(5))     # 10
```

A function that prints instead of returning gives back `None` (Day 01, section 5.5). The tests call your functions and inspect what comes back, so a printed answer scores zero. Only `main()` prints today. Everything else returns.

**2. A function with no `return` returns `None`.** Falling off the end of the body is the same as `return None`. If a test says "expected `{}`, got `None`", you forgot to return.

**3. Names created inside a function are private to it.** This is called *scope*, and it gets a proper treatment tomorrow.

```python
def counter() -> int:
    total = 0
    total = total + 1
    return total

print(counter())      # 1
print(total)          # NameError: name 'total' is not defined
```

That is a feature, not a nuisance: it means your helper's `total` cannot collide with anybody else's `total`.

**4. `return` inside a loop exits the whole function**, not just the loop. `break` leaves the loop; `return` leaves the building.

### Calling one of your own functions from another

Perfectly normal, and today's milestones are designed for it:

```python
def clean(text: str) -> str:
    return " ".join(text.split()).casefold()

def first_word(text: str) -> str:
    cleaned = clean(text)          # M-something calls M-something-earlier
    words = cleaned.split()
    if not words:
        return ""
    return words[0]
```

`word_counts` should call `clean_text`. `top_words` should call `word_counts`. `text_stats` should reuse `word_counts`. `render_report` should call `text_stats` and `top_words`. Each milestone builds on the last one, which is exactly why they are numbered.

### Extra helpers are allowed and encouraged

You are not limited to the five graded names. If two milestones need the same list of cleaned words, write yourself a helper:

```python
def words_of(text: str) -> list[str]:
    """The words of `text`: cleaned, punctuation-trimmed, empties dropped."""
    words = []
    for piece in clean_text(text).split():
        word = strip_punctuation(piece)
        if word:
            words.append(word)
    return words
```

Nothing tests `words_of`, so it is yours to shape. `solutions.py` uses exactly this one, plus two more. Writing them is not cheating and it is not overkill — it is the whole reason `def` exists, which is what tomorrow's lesson is about.

> **Gotcha:** define a function before you call it *at the top level of the file*, but functions may call each other in any order, because the call happens later — when the program runs, not when the `def` is read. That is why `words_of` above can mention `clean_text` even if `clean_text` is defined further down the file.

That is the primer. It is deliberately thin: no defaults, no `*args`, no return-a-tuple tricks, nothing about how arguments are matched up. All of that is tomorrow, and none of it is needed today.

---

## Rules of engagement

Graded by review as well as by the tests.

**You may use anything from Days 01–06:**

| Day | Tools you will actually want today |
|---|---|
| D1 | variables, `print`, `type()`, comments |
| D2 | `str.strip`, `str.casefold`, `str.split`, `str.join`, `len`, `round`, f-strings with `:<16` / `:>6` / `:>6.2f` |
| D3 | `if` / `elif` / `else`, `and` / `or` / `not`, truthiness (an empty string is falsy) |
| D4 | `for`, `continue`, accumulator variables |
| D5 | lists, tuples, `list.append`, `list.sort(key=...)`, slicing |
| D6 | dicts, `dict.get`, `dict.items`, sets |

**You may not use:**

- `collections.Counter`, which counts a sequence in one call, or `re`, which would do the punctuation stripping and sentence splitting in a fraction of the lines. Both are Day 17. Both would make this project a twenty-line file, and you would learn nothing from it. Note them down as things to come back to — knowing the loop first is what makes the shortcut obviously useful later, rather than magic.
- `string.punctuation` — the exact set of characters is written out for you in `exercises.py` as `PUNCTUATION`.
- Comprehensions and generators (Day 15), the anonymous one-line function form (Day 16), exception handling (Day 09), classes (Day 12), and reading or writing files (Day 10).
- Anything at all from outside the standard library, and in fact anything from outside this file: today's toolkit brings nothing in from elsewhere.

**Two specific consequences:**

1. `sort(key=...)` needs a *named* `def` function, defined at module level and passed without parentheses: `pairs.sort(key=by_count_then_word)`. The one-line anonymous alternative you may have seen in other people's code is Day 16.
2. Nothing may raise on empty input. Every milestone below says what an empty text produces. Guard with `if`, because you do not have exception handling yet — and, more to the point, because "no words" is not an error. It is a perfectly ordinary answer that has to be decided in advance.

---

## User stories

1. As a user, I can hand the toolkit a block of text with ragged spacing and mixed capitals and get back a single, predictable, normalised version of it.
2. As a user, I can see how many times each word appears, without `"Hello,"` and `"hello"` being counted as two different words.
3. As a user, I can ask for the ten most common words and get them in a stable order, so that running it twice gives the same answer.
4. As a user, I can see the headline numbers — words, unique words, sentences, average word length, longest word — with each one defined so I know what it counted.
5. As a user, I can print one report whose columns line up, so I can read it without counting characters.
6. As a user, I can run the whole thing with one command and see it work on the built-in sample text.

---

## The graded API

Everything lives in `exercises.py`. The names and behaviours are fixed, because `test_exercises.py` grades them milestone by milestone — `test_m1_*` through `test_m5_*` — so partial credit is visible from the first milestone onward. Run `python check.py day07` as often as you like; a rising number is the point.

```
M1  clean_text(text)               -> str
M2  word_counts(text)              -> dict[str, int]
M3  top_words(text, n)             -> list[tuple[str, int]]
M4  text_stats(text)               -> dict[str, object]
M5  render_report(text, top_n)     -> str
    main()                         -> None      prints the demonstration
```

Given to you at the top of `exercises.py`, already written:

| Name | What it is |
|---|---|
| `SAMPLE_TEXT` | the text `main()` demonstrates on |
| `PUNCTUATION` | every character that counts as punctuation |
| `SENTENCE_ENDINGS` | `".!?"` |
| `strip_punctuation(word)` | `word.strip(PUNCTUATION)`, so the punctuation rule is not a guess |

---

## Milestone 1 — `clean_text(text)`

Normalise the text so that no later milestone has to think about spacing or case.

Three changes, and they do not interfere with each other, so the order is up to you:

1. whitespace at the very start and the very end disappears;
2. every run of internal whitespace — spaces, tabs, newlines, or any mixture — becomes exactly one space;
3. the text is casefolded.

Punctuation is **not** touched. `"Hello,"` becomes `"hello,"` and keeps its comma. Removing punctuation is M2's job, and doing it here would break M4's sentence counting, which needs the full stops.

| Input | Output |
|---|---|
| `"  Hello   World  "` | `"hello world"` |
| `"Hello\tWORLD\n\nagain"` | `"hello world again"` |
| `"The Cat SAT."` | `"the cat sat."` |
| `"one"` | `"one"` |
| `""` | `""` |
| `"   \n\t "` | `""` |

**Why casefold and not lower.** `str.casefold()` is the version of `lower()` built for *comparing* text rather than displaying it. On English they agree. On text from elsewhere they do not: German `"STRASSE"` and `"Straße"` both casefold to `"strasse"`, so a word counter using casefold treats them as the same word, which is almost always what a reader means. It costs you nothing to pick the right tool now.

**Hints.**

- Day 02, section 8.3 already solved most of this in one line. `text.split()` with **no argument** splits on every run of any whitespace and discards the runs at both ends. So `" ".join(text.split())` trims and collapses in one step, and it handles tabs and newlines without you naming them.
- `str.replace(" ", "")` is not a substitute: it cannot see a tab, and it cannot collapse a run of three spaces into one.
- Chain in whatever order reads best. Both of these are correct:

```python
" ".join(text.split()).casefold()
" ".join(text.casefold().split())
```

> **Gotcha:** `"a  b".split(" ")` — with an explicit space — returns `["a", "", "b"]`, complete with an empty string in the middle. `split()` with no argument returns `["a", "b"]`. This difference matters in about half of all beginner word-counting bugs, including the ones you are about to write.

---

## Milestone 2 — `word_counts(text)`

A dict mapping each word to how many times it appears.

The pipeline, in order:

1. normalise the text with `clean_text`, so case and spacing stop mattering;
2. split it into whitespace-separated pieces;
3. strip punctuation from **both ends** of each piece with `strip_punctuation`;
4. discard any piece that is now empty;
5. count what is left.

**What counts as punctuation.** Exactly this set, given to you as `PUNCTUATION`:

```python
PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
```

`str.strip(chars)` removes any character in `chars` from each end of a string, and keeps going until it meets a character that is not in the set. It never touches the middle. Three consequences worth knowing before you are surprised by them:

- `"hello!!!"` → `"hello"`, and `"...hello?!"` → `"hello"`. Runs are handled for free.
- `"don't"` → `"don't"` and `"well-known"` → `"well-known"`. Inner punctuation survives, because it is not at an edge. That is the behaviour this brief wants.
- `"--"` → `""` and `"..."` → `""`. A piece that was nothing but punctuation is now empty, and step 4 drops it. An empty string is falsy (Day 03), so the test is `if word:` and needs no comparison.

**Key order: first appearance.** Dicts remember the order keys were inserted (Day 06). Walking the words in order and inserting each new one as you meet it therefore gives you first-appearance order for free — and a test checks it, so do not sort the keys.

| Input | Output |
|---|---|
| `"the cat sat on the mat"` | `{"the": 2, "cat": 1, "sat": 1, "on": 1, "mat": 1}` |
| `"Hello, HELLO... hello?!"` | `{"hello": 3}` |
| `"Apple APPLE apple"` | `{"apple": 3}` |
| `"well-known don't"` | `{"well-known": 1, "don't": 1}` |
| `"-- ... ! the"` | `{"the": 1}` |
| `""` or `"   "` | `{}` |

**Hints.**

- The counting pattern is Day 06's, and it is three lines:

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
```

  `counts[word] + 1` on its own raises `KeyError` the first time it meets each word. `.get(word, 0)` supplies the missing zero. An `if word in counts:` / `else:` pair also works and is two lines longer.
- This is the milestone where a `words_of(text)` helper earns its keep, because M4 needs the same list. Write it once.
- Do not call `strip_punctuation` on the whole text. It only strips the ends, so on a whole document it would remove the final full stop and nothing else.

---

## Milestone 3 — `top_words(text, n)`

The `n` most frequent words, as a list of `(word, count)` tuples.

Ordering, applied in this order:

1. higher count first;
2. equal counts are ordered alphabetically.

That second rule is not decoration. Without it, the answer depends on the order the words happened to appear in the document, which means your report changes when the input is reordered in a way that should not matter. A ranking with an undefined tie rule is a ranking nobody can test.

Size rules:

- `n` of 0 or less returns `[]`;
- asking for more words than exist returns every word, with no padding.

| Call | Result |
|---|---|
| `top_words("the cat sat on the mat", 2)` | `[("the", 2), ("cat", 1)]` |
| `top_words("banana apple cherry apple banana cherry", 2)` | `[("apple", 2), ("banana", 2)]` |
| `top_words("the cat", 9)` | `[("cat", 1), ("the", 1)]` |
| `top_words("the cat", 0)` | `[]` |
| `top_words("the cat", -3)` | `[]` |
| `top_words("", 5)` | `[]` |

**Hints.**

- `dict.items()` gives you the `(key, value)` pairs. `list(counts.items())` turns them into a list you can sort.
- `list.sort()` sorts in place and returns `None` (Day 05 — the classic trap). `sorted(...)` returns a new list. Either is fine; do not write `pairs = pairs.sort(...)`.
- The key function, named and at module level:

```python
def by_count_then_word(pair: tuple[str, int]) -> tuple[int, str]:
    """Sort key: biggest count first, then alphabetically."""
    word, count = pair
    return (-count, word)
```

  Then `pairs.sort(key=by_count_then_word)` — note: no parentheses after the name. You are handing `sort` the function itself so that it can call it once per item; `by_count_then_word()` would call it immediately, with no argument, and fail.
- **Why negate the count instead of `reverse=True`?** Because `reverse=True` reverses *everything*, including the alphabet, so ties would come out Z-to-A. Negating one column flips one column. Tuples compare left to right (Day 05), so `(-3, "the")` sorts before `(-2, "cat")`, and `(-2, "apple")` before `(-2, "banana")`.
- Guard `n <= 0` before slicing. `pairs[:0]` happens to be `[]` by luck, but `pairs[:-3]` silently drops the last three pairs and returns the rest — a wrong answer with no error message, which is the worst kind.
- Slicing past the end is safe: `[:9]` on a two-item list gives two items. "More than exist" needs no special case.

---

## Milestone 4 — `text_stats(text)`

Five statistics in one dict, keyed in exactly this insertion order:

| Key | Type | Meaning |
|---|---|---|
| `"word_count"` | `int` | how many words there are, counting repeats |
| `"sentence_count"` | `int` | how many sentences (definition below) |
| `"unique_words"` | `int` | how many different words |
| `"average_word_length"` | `float` | mean word length, rounded to 2 decimals |
| `"longest_word"` | `str` | the longest word |

"Word" means precisely what M2 means by it: casefolded, edge punctuation stripped, empties discarded. So `word_count` is the sum of `word_counts(text).values()` and `unique_words` is the number of keys in that dict. A test checks that those two agree with M2, so reuse M2 rather than re-deriving it differently.

### The sentence rule, stated exactly

Guessing is not allowed here, so:

- a sentence ends at one of `.`, `!` or `?` — the three characters in `SENTENCE_ENDINGS`;
- a **run** of those characters counts once. `"Really?!"` is one sentence. `"Wait..."` is one sentence;
- if the text has at least one word but no ending character at all, the count is **1**. An unpunctuated line is still one sentence;
- if the text has no words, every count is 0 — including this one. `"..."` is not a sentence, because there is nothing in it to say.

The algorithm is one loop: walk the characters of the text and count each ending character whose *previous* character is not also an ending character.

| Input | `sentence_count` |
|---|---|
| `"Hi. Bye."` | 2 |
| `"One. Two. Three."` | 3 |
| `"Really?! Wow..."` | 2 |
| `"no terminator here"` | 1 |
| `"..."` | 0 (no words) |
| `""` | 0 |

This definition counts `"e.g."` as two sentences, and `"Dr. Who"` as two. That is a known limitation, written down on purpose: correct sentence splitting needs pattern matching (`re`, Day 17) and a list of abbreviations, and it is still wrong sometimes. Today's rule is simple, precise, and exactly what the tests use. Shipping a documented approximation beats shipping an undocumented one.

### The other three, exactly

- **`average_word_length`** — add up the lengths of the words (after punctuation stripping, counting repeats), divide by `word_count`, and round **once at the end** with `round(value, 2)`. Rounding each word's length first, or rounding a running average, gives a different and wrong answer.
- **`longest_word`** — the word with the most characters. Ties go to the word that appears **first**. Walk the words in order and compare with a strict `>`: `if len(word) > len(longest)`. With `>=`, every later tie overwrites your answer and you end up with the last of the tied words instead of the first.
- **Empty text** — `word_count` 0, `sentence_count` 0, `unique_words` 0, `average_word_length` `0.0`, `longest_word` `""`. Nothing raises.

### Worked examples

```
text_stats("The cat sat. The cat ran! The end?")
    -> {"word_count": 8, "sentence_count": 3, "unique_words": 5,
        "average_word_length": 3.0, "longest_word": "the"}
```

Eight words, five of them distinct (`the`, `cat`, `sat`, `ran`, `end`); every word is three characters so the average is exactly `3.0`; every word ties on length, so the first one, `the`, wins.

```
text_stats("Python")
    -> {"word_count": 1, "sentence_count": 1, "unique_words": 1,
        "average_word_length": 6.0, "longest_word": "python"}

text_stats("")
    -> {"word_count": 0, "sentence_count": 0, "unique_words": 0,
        "average_word_length": 0.0, "longest_word": ""}
```

**Hints.**

- Divide only when there is something to divide by. `total / 0` raises `ZeroDivisionError`, and you have no exception handling until Day 09, so an `if word_count > 0:` guard is both the available answer and the right one.
- Start the accumulators at values that mean "nothing yet": `total_length = 0` and `longest_word = ""`. `len("")` is 0, so the very first word is always longer, and the loop needs no special case for its first pass.
- One loop can do both jobs. You are already walking the words to add up their lengths; check the length against the longest in the same pass.
- Build the returned dict as one literal at the end, with the keys in the documented order.

> **Gotcha:** counting the sentence endings has a trap that will cost you twenty minutes if you meet it cold. If you track the previous character in a variable, do **not** start it at `""`. `"" in ".!?"` is `True` — the empty string counts as a substring of every string — so the very first character of the text would never be counted. Start it at a space, or track a "was the last character an ending" boolean instead.

---

## Milestone 5 — `render_report(text, top_n)`

One string, several lines, columns that line up. It returns the string and prints nothing: printing is `main()`'s job, and that separation is exactly what lets a test assert on the layout in one line.

### The layout, exactly

Labels are left-justified in **16** characters and values right-justified in **6**, so every statistics line is 22 characters wide.

```
line 1   "TEXT REPORT"
line 2   "===========" (eleven '=', matching the title)
line 3   f"{'words':<16}{word_count:>6}"
line 4   f"{'unique words':<16}{unique_words:>6}"
line 5   f"{'sentences':<16}{sentence_count:>6}"
line 6   f"{'avg word length':<16}{average_word_length:>6.2f}"
line 7   f"{'longest word':<16}{longest_word:>6}"
line 8   ""                      one completely empty line
line 9   f"top {shown} words"    `shown` = how many rows FOLLOW
line 10  "-" repeated to the length of line 9
line 11+ one row per word, f"{word:<16}{count:>6}"
```

Note line 9 carefully: the heading reports **how many rows actually follow**, not what was asked for. Ask for the top 5 of a two-word document and the heading says `top 2 words`. A report that overstates itself does not get trusted twice.

For `"The cat sat. The cat ran! The end?"` with `top_n = 3`, the exact output is:

```
TEXT REPORT
===========
words                8
unique words         5
sentences            3
avg word length   3.00
longest word       the

top 3 words
-----------
the                  3
cat                  2
end                  1
```

The tests compare against that string character for character, so:

- **no line has trailing whitespace.** Line 8 is the empty string, not a line of spaces. Because every populated line ends with a right-justified value, you get this for free — unless you add a space of your own between the columns, which you must not.
- **the whole string does not end with a newline.** Build a list of lines and `"\n".join(lines)`. `join` cannot add a trailing newline; `print` adds the final one when the report is displayed, which is exactly the right division of labour.
- `avg word length` uses `:>6.2f`, so `3.0` renders as `  3.00`. Two decimals always, even on a whole number.

### The two variations

**`top_n` of 0 or less** — stop after line 7. No blank line, no heading, no underline, no rows. The report is seven lines:

```
TEXT REPORT
===========
words                8
unique words         5
sentences            3
avg word length   3.00
longest word       the
```

**Text with no words** — the entire report is three lines, and `top_n` is ignored:

```
TEXT REPORT
===========
(no words found)
```

That applies to `""`, to `"   \n\t"`, and to `"..."` — anything M2 finds no words in.

### A width is a minimum, not a maximum

`f"{'internationalisation':<16}"` produces all twenty characters, unpadded and untruncated. So the row for a long word is simply wider than 22, and the `longest word` line for it looks like:

```
longest word    internationalisation
```

That is correct and the tests require it. Do not slice words to fit.

**Hints.**

- Call your own milestones. `stats = text_stats(text)` and `pairs = top_words(text, top_n)` is nearly the whole function; the rest is formatting.
- Pull the five values out of `stats` into local names first. It makes each f-string short enough to read, and it names what each column is.
- `"=" * len(TITLE)` beats typing eleven `=` characters and counting them. Same for the dashes under the heading — derive them from the heading you just built, and they can never drift out of sync.
- Build `lines` as a list and `append` to it, then `"\n".join(lines)` once, at the end. Growing a string with `+=` works but makes the trailing-newline rule easy to get wrong and hides the shape of the output from the next reader.
- Check the empty case *early* and return the short report straight away (a "guard clause"). Wrapping the entire rest of the function in an `else:` is more indentation for no benefit.

---

## `main()`

The demonstration, and the only function in the file that prints.

Requirements:

- print the report for `SAMPLE_TEXT` with a top-5 ranking;
- a title line above the report is welcome; banner art is not;
- read no input, write no files, take no arguments — so it is safe to run anywhere, including from a test;
- return nothing. `main() -> None`. It is called under `if __name__ == "__main__":`, which is already written at the bottom of `exercises.py`.

Running it should look roughly like this — your title line and your sample text may differ:

```
$ python course/week1/day07_project_text_toolkit/exercises.py
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

> **Gotcha:** `if __name__ == "__main__":` is what stops `main()` from running when the test harness loads your file to grade it. Day 11 explains the mechanism; today, just do not call `main()` at the top level of the module. If your tests suddenly print a report, that is what happened.

---

## Suggested order of work

1. Read this whole brief. All of it, before typing anything. Ten minutes now saves an hour of reworking M2 because you did not know what M4 needed.
2. Run the demo: `python course/week1/day07_project_text_toolkit/examples.py`. It builds the same six-step pipeline over log lines instead of prose, so you can see the shape without being handed your answer.
3. `clean_text`. Then `python check.py day07` and watch `test_m1_*` go green. Do not move on until they are.
4. `words_of` (your own helper, ungraded), then `word_counts`. M2 green.
5. `by_count_then_word`, then `top_words`. M3 green.
6. `text_stats` — the sentence counter is the fiddly part; do the other four keys first and come back to it.
7. `render_report`. Print it and *look* at it before you run the tests: a layout bug is obvious to your eyes and cryptic in a diff.
8. `main()`. Run the file for real.
9. Read `solutions.py` and compare decisions.

If a milestone fights you for more than thirty minutes, run `python check.py day07 -v` and read the actual comparison. Then print the intermediate value — `print(repr(words))` — instead of reasoning about it. Day 01, section 11.4.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Printing the answer instead of returning it | `assert None == {...}` | Only `main()` prints. Everything else `return`s |
| Forgetting `return` entirely | the test reports `None` | Add `return`; falling off the end gives `None` |
| `text.split(" ")` instead of `text.split()` | empty strings among your words, `""` counted as a word | `split()` with no argument, which handles every run of any whitespace |
| Using `str.replace` to collapse spaces | tabs and newlines survive, runs become several spaces | `" ".join(text.split())` |
| Stripping punctuation from the whole text | only the final full stop disappears | Strip each *piece* after splitting |
| Removing punctuation in `clean_text` | M4's sentence count is 0 or 1 everywhere | M1 keeps punctuation; M2 strips it per word |
| `counts[word] = counts[word] + 1` | `KeyError: 'the'` | `counts.get(word, 0) + 1` |
| `pairs = pairs.sort(key=...)` | `None` where a list should be | `pairs.sort(...)` mutates and returns `None`; sort then use `pairs` |
| `sort(key=by_count_then_word())` | `TypeError: missing 1 required positional argument` | Pass the function, no parentheses |
| `sort(reverse=True)` instead of a negated count | ties come out Z-to-A | `return (-count, word)` |
| Not guarding `n <= 0` | `top_words(text, -3)` returns most of the list | `if n <= 0: return []` |
| Dividing by `word_count` when it is 0 | `ZeroDivisionError` | Guard with `if word_count > 0:` |
| `>=` when tracking the longest word | you get the *last* tied word, not the first | Strict `>` |
| Starting `previous = ""` in the sentence loop | the first character never counts | `"" in ".!?"` is `True`; start at `" "` |
| Rounding as you go | the average is off by a cent-sized amount | `round` once, at the very end |
| A space typed between report columns | trailing whitespace, or a 23-character line | Let the format specs do all the spacing |
| `"\n".join(lines) + "\n"` | the trailing-newline test fails | `join` alone; `print` supplies the last newline |
| Calling `main()` at module level | reports printed during grading; a slow test run | Keep it under `if __name__ == "__main__":` |

---

## Mental model

A **pipeline**: each stage narrows raw mess into something the next stage can assume.

```
  raw text
  "  The Cat   SAT.\n\nThe cat!  "
        |
        |  M1 clean_text        trim, collapse, casefold
        v
  "the cat sat. the cat!"
        |
        |  M2 word_counts       split, strip edges, drop empties, count
        v
  {"the": 2, "cat": 2, "sat": 1}
        |
        +---------------------------+
        |                           |
        |  M3 top_words             |  M4 text_stats
        |  sort by (-count, word)   |  words, sentences, unique,
        v                           v  average, longest
  [("cat", 2), ("the", 2)]      {"word_count": 5, ...}
        |                           |
        +------------+--------------+
                     |
                     |  M5 render_report      f-string widths, "\n".join
                     v
              "TEXT REPORT\n===========\nwords ..."
                     |
                     |  main()                the only print
                     v
                 your terminal
```

Three things the diagram is trying to teach:

- **Normalise once, at the entrance.** After M1, no later stage asks "might this be upper case?" Every stage you skip that question in is a stage that cannot get it wrong.
- **Data flows one way.** Nothing later in the pipeline reaches back and changes something earlier. That is why each stage can be tested by itself, and why a failing `test_m4_*` tells you the bug is in M4 or in something M4 called — not somewhere in a tangle.
- **Printing is at the very end, once.** A function that returns a value can be tested, reused, and composed. A function that prints one can only be watched.

---

## Stretch goals

Not graded. Pick whichever interest you; each one is doable with Days 01–06.

- `word_lengths(text)` returning `{length: how many words have it}` — a histogram, and the same counting pattern keyed by a number instead of a string.
- `character_counts(text)` over letters only, ignoring spaces and punctuation. Then find the most common letter in English prose and see whether your sample agrees with the usual answer.
- `unique_words(text)` returning a **set**, and `shared_words(a, b)` returning the words two texts have in common — set intersection in one operator (Day 06).
- A stop-word list: hold `{"the", "a", "and", "of", "to", "is", "it", "in"}` in a set and add a `skip_common` behaviour to your ranking. Suddenly the top-5 says something about the document.
- `longest_words(text, n)` — the n longest distinct words, ties alphabetical. Another named key function, a different key.
- `average_sentence_length(text)` in words. You have both numbers already.
- A crude readability score: something like `0.39 * words_per_sentence + 11.8 * average_word_length - 15.59`. Invented numbers, real shape.
- A bar chart column in the report: `"#" * count` next to each top word, capped so a common word cannot wrap the terminal.
- Make the report width a parameter — `render_report(text, top_n, label_width=16)` — and notice that you need Day 08's default arguments to do it *properly*. This one is deliberately a cliffhanger.

---

## How to know you're done

- [ ] `python check.py day07` reports every check passing.
- [ ] `python course/week1/day07_project_text_toolkit/exercises.py` prints a report for the sample text and exits without a traceback.
- [ ] `clean_text("  A\tB\n\nC  ")` is `"a b c"` — one space between each, nothing at the ends.
- [ ] `word_counts("Hello, HELLO... hello?!")` is `{"hello": 3}`.
- [ ] `word_counts("-- ...")` is `{}`, not `{"--": 1, "...": 1}` and not `{"": 2}`.
- [ ] `top_words(text, 0)` and `top_words(text, -5)` are both `[]`.
- [ ] Two words with the same count come out alphabetically, and you can say why `reverse=True` was the wrong tool.
- [ ] `text_stats("")` returns all zeros, `0.0` and `""`, and raises nothing.
- [ ] `text_stats("cat bat mat")["longest_word"]` is `"cat"` — the first of the tied words.
- [ ] `text_stats(t)["word_count"]` equals `sum(word_counts(t).values())` for any `t` you try.
- [ ] The rendered report's columns line up, no line ends in a space, and the string does not end in a newline.
- [ ] Asking for more top words than exist changes the heading, not just the number of rows.
- [ ] Days 01–06 tools only: no comprehension, no anonymous one-line function, nothing brought in from another module, no exception handling, no classes — and you could say what each of those would have bought you and which day it arrives.
- [ ] Every function has a docstring, and no function is longer than about 20 lines.

---

## Practice

1. Run the demo first. It is a *different* dataset — pipe-separated log lines — built with exactly the pipeline your project needs, so you can see the shape without being handed your own answer:

   ```bash
   python course/week1/day07_project_text_toolkit/examples.py
   ```

2. Then work through the milestones in `exercises.py`, grading as you go:

   ```bash
   python check.py day07
   python check.py day07 -v      # full failure detail
   ```

3. When it is green, run the toolkit itself and read the report:

   ```bash
   python course/week1/day07_project_text_toolkit/exercises.py
   ```

4. Then point it at text of your own. Paste a few paragraphs of something you wrote into `SAMPLE_TEXT` and look at the top ten words. Almost every document is dominated by `the`, `a`, `and`, `of` and `to` — which is why the stop-word stretch goal exists, and why word frequency alone is a weak signal. Noticing that from your own data is worth more than being told.

5. Read `solutions.py` and compare decisions. Not to check you match it — to notice where you disagreed, and to be able to say why.

---

## Recall check

1. Why does `clean_text` casefold the text but leave the punctuation alone?
2. What is the difference between `text.split()` and `text.split(" ")`, and which one does this project need?
3. `"don't"` keeps its apostrophe but `"hello!"` loses its exclamation mark. Both use the same call. Why do they behave differently?
4. Why does the tie-break rule for `top_words` exist at all? What would go wrong without it?
5. Why does the sort key return `(-count, word)` rather than using `reverse=True`?
6. `top_words(text, -3)` must return `[]`. What does it return if you forget the guard and just slice?
7. Why must `text_stats` guard the division that computes the average, and why is a guard rather than an error the right answer?
8. Why does tracking the longest word use `>` and not `>=`?
9. `render_report` returns a string instead of printing. Name two things that buys you.
10. Which single line of today's code would `collections.Counter` replace, and why are you not allowed to use it yet?

<details>
<summary>Answers</summary>

1. Casefolding makes `"The"` and `"the"` the same word, which is the entire point of a word counter — without it the top-5 is polluted by capitalisation accidents. Punctuation has to stay because M4 counts sentences by looking for `.`, `!` and `?`; strip them at M1 and every document becomes one sentence. Each stage removes only what the *later* stages agree they do not need.
2. `split()` with no argument splits on every run of any whitespace — spaces, tabs, newlines — and discards leading and trailing runs, so `"  a\t\tb "` gives `["a", "b"]`. `split(" ")` splits on each single space character, keeping empty strings between consecutive spaces and at the ends: `["", "", "a\t\tb", ""]`. This project needs the no-argument form everywhere.
3. `str.strip(chars)` only removes characters at the two **ends** of the string, and stops as soon as it meets one that is not in the set. The apostrophe in `"don't"` is in the middle, so it is never a candidate; the `!` in `"hello!"` is at an end, so it goes.
4. Without a tie rule the order of equal-count words is whatever the counting loop happened to produce, which depends on the order the words appeared in the document. The same information in a different order would give a different report, the output could not be asserted on in a test, and two runs over reordered input would disagree. Alphabetical is arbitrary but *stable*, and stable is the property that matters.
5. `reverse=True` reverses the comparison for the whole key, so the alphabetical part would run Z-to-A as well. Negating just the count reverses one column and leaves the other alone. Tuples compare left to right, so `(-3, "the")` sorts before `(-2, "apple")`, and among equal counts the words compare normally.
6. `pairs[:-3]` — everything except the last three pairs. So you get a list of plausible-looking results with no error and no clue that anything is wrong. That is strictly worse than a crash, which is the general argument for guarding inputs at the entrance.
7. `total / 0` raises `ZeroDivisionError`, and you have no exception handling until Day 09. More importantly, "no words" is not a failure — it is an ordinary input with an obvious right answer, `0.0`. Reserving exceptions for genuinely exceptional things is a habit worth forming before you have the syntax to abuse.
8. Both find a word of maximum length, but `>=` replaces the current best on every tie, so it ends up holding the *last* of the tied words. `>` only replaces on a strict improvement, so the first one survives — which is the rule the brief states.
9. Any two of: it can be tested with a single equality assertion; it can be reused by anything that wants text (a terminal, a file on Day 10, an HTTP response on Day 19) without changing a line; it can be composed — put into another string, compared with a previous run, or diffed; and the printing decision stays in one place instead of being scattered through the code that computes.
10. The three-line counting loop in `word_counts` collapses to `Counter(words)`, and `top_words` collapses to `Counter(words).most_common(n)` (though its tie order is insertion order, not alphabetical, so it would not quite satisfy this brief). You are not allowed it yet because the loop is the thing being learned: `.get(key, 0) + 1` is the pattern behind grouping, tallying, indexing and caching, and you will write it by hand many more times in situations no library covers. `Counter` arrives on Day 17 as a labour saver, which is the only way to appreciate it.

</details>
