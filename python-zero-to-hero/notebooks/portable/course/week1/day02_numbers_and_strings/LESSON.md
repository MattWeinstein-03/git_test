# Day 02 — Numbers and Strings

> **Time:** ~4 hours  |  **Prerequisites:** Day 01

## What you'll be able to do after today
- Compute with all seven arithmetic operators, including `//`, `%` and `**`, and predict the result of an expression without running it.
- Explain why `0.1 + 0.2` is not `0.3`, and choose an approach that does not lose money.
- Convert between `str`, `int` and `float` deliberately, and say exactly which conversions raise `ValueError` and why.
- Pull any character, any substring, or any every-nth-character run out of a string with indexing and slicing, including from the right-hand end.
- State what "strings are immutable" means and rewrite code that wrongly assumes otherwise.
- Reach for the right string method out of the fifteen you will use most, and know what each one gives back.
- Format output precisely with f-strings: two decimal places, thousands separators, and text aligned left, right or centre in a fixed width.

## Why this matters

Nearly all data starts life as text and needs to become numbers, or starts as numbers and needs to become readable text. A CSV row is text. A web form is text. A log file is text. `input()` is text. Meanwhile the answers you need — totals, averages, percentages — are numbers, and the report you produce at the end is text again.

Today is that conversion layer, plus the arithmetic in the middle. It is also the day that makes your output stop looking amateurish: `Total: 1234.5678999999` versus `Total:      1,234.57` is one format spec apart, and the second one is what a person can actually use. Day 07's project is built almost entirely out of today's string methods, and f-strings appear on every remaining day of the course.

---

## 1. Arithmetic

Seven operators. Five are familiar from school; two are not, and those two are the ones you will use to solve real problems.

```python
print(7 + 3)     # 10   addition
print(7 - 3)     # 4    subtraction
print(7 * 3)     # 21   multiplication
print(7 / 3)     # 2.3333333333333335   true division -> ALWAYS a float
print(7 // 3)    # 2    floor division -> how many whole 3s fit in 7
print(7 % 3)     # 1    modulo -> what is left over
print(7 ** 3)    # 343  exponentiation -> 7 to the power of 3
```

### 1.1 `/` always gives a float

Even when the answer is exact:

```python
print(10 / 2)          # 5.0    not 5
print(type(10 / 2))    # <class 'float'>
print(10 // 2)         # 5
print(type(10 // 2))   # <class 'int'>
```

This is a deliberate Python 3 change. It means division never silently discards a remainder, which was a rich source of bugs in Python 2. When you want a whole number, ask for one with `//`.

### 1.2 `//` floor division — "how many whole ones fit"

```python
print(17 // 5)      # 3     three whole 5s fit in 17
print(100 // 7)     # 14
print(4 // 5)       # 0     no whole 5s fit in 4
print(-7 // 2)      # -4    NOT -3
```

That last line surprises everyone. `//` **floors** — it rounds *down*, towards negative infinity, not towards zero. `-7 / 2` is `-3.5`, and the next integer down from `-3.5` is `-4`.

```python
print(7 / 2, 7 // 2)        # 3.5 3
print(-7 / 2, -7 // 2)      # -3.5 -4
print(int(-7 / 2))          # -3    int() truncates towards zero instead
```

Both behaviours are useful. Know which one you asked for.

### 1.3 `%` modulo — the remainder

```python
print(17 % 5)      # 2     17 = 3*5 + 2
print(10 % 2)      # 0     no remainder: 10 is even
print(7 % 2)       # 1     remainder 1: 7 is odd
print(9 % 3)       # 0
```

`%` looks like a toy until you notice how often "the remainder" is the answer to a real question:

```python
# Is a number even? (Day 3 turns this into a decision.)
print(48 % 2 == 0)      # True

# Split 4000 seconds into minutes and seconds:
total_seconds = 4000
minutes = total_seconds // 60      # 66
seconds = total_seconds % 60       # 40
print(minutes, "minutes", seconds, "seconds")

# Extract the last digit of a number:
print(1234 % 10)        # 4

# Wrap around a fixed range — 15 hours after 20:00 on a 24-hour clock:
print((20 + 15) % 24)   # 11

# Is a year divisible by 4?
print(2024 % 4 == 0)    # True
```

The pairing of `//` and `%` — quotient and remainder — comes up constantly: seconds to hours/minutes, items to pages, pence to pounds, indexes to rows and columns.

### 1.4 `**` exponentiation

```python
print(2 ** 10)       # 1024
print(3 ** 0)        # 1
print(2 ** 0.5)      # 1.4142135623730951   a fractional power is a root
print(9 ** 0.5)      # 3.0
print(2 ** -1)       # 0.5
```

`**` is the only arithmetic operator that is **right-associative**: `2 ** 3 ** 2` is `2 ** (3 ** 2)` = `2 ** 9` = `512`, not `(2 ** 3) ** 2` = `64`. Every other operator groups left to right.

### 1.5 Compound assignment

```python
total = 10
total += 5     # same as total = total + 5
print(total)   # 15
total -= 3     # 12
total *= 2     # 24
total //= 5    # 4
total **= 2    # 16
total %= 7     # 2
print(total)   # 2
```

These are shorthand, nothing more. `total += 5` and `total = total + 5` do the same thing for numbers. You will use `+=` constantly from Day 4 onwards to build up totals.

### 1.6 `round`, `abs`, and friends

```python
print(round(3.14159, 2))    # 3.14
print(round(2.71828, 3))    # 2.718
print(round(4.7))           # 5      no second argument -> nearest int
print(abs(-7))              # 7
print(min(3, 9, 2))         # 2
print(max(3, 9, 2))         # 9
print(divmod(17, 5))        # (3, 2)  -> the // answer and the % answer together
```

`divmod(a, b)` returns `(a // b, a % b)` in one go.

> **Gotcha:** `round` uses *banker's rounding* — halves go to the nearest **even** number, so `round(0.5)` is `0` and `round(1.5)` is `2` and `round(2.5)` is `2`. This is deliberate (it avoids a systematic upward bias when you round thousands of values) and it is not what school taught you. Also, `round(2.675, 2)` gives `2.67`, not `2.68`, because `2.675` is not exactly 2.675 in binary — which brings us to section 3.

---

## 2. Operator precedence

Python evaluates operators in a fixed order, not left to right.

```python
print(2 + 3 * 4)        # 14, not 20
print((2 + 3) * 4)      # 20
```

The order, tightest-binding first:

| Precedence | Operators | Note |
|---|---|---|
| 1 (highest) | `()` | grouping — always wins |
| 2 | `**` | right-associative |
| 3 | `-x`, `+x` | unary minus/plus |
| 4 | `*`, `/`, `//`, `%` | left to right |
| 5 | `+`, `-` | left to right |
| 6 | `<`, `<=`, `>`, `>=`, `==`, `!=` | comparisons (Day 3) |
| 7 | `not` | |
| 8 | `and` | |
| 9 (lowest) | `or` | |

Worked examples:

```python
print(10 - 2 - 3)          # 5    left to right: (10-2)-3
print(2 ** 3 ** 2)         # 512  right to left: 2 ** (3 ** 2)
print(-2 ** 2)             # -4   ** binds tighter than unary minus: -(2**2)
print((-2) ** 2)           # 4
print(10 / 5 * 2)          # 4.0  same precedence, left to right
print(1 + 2 * 3 ** 2)      # 19   3**2=9, 2*9=18, 1+18=19
print(7 % 3 * 2)           # 2    % and * are equal, left to right: (7%3)*2
```

The professional habit is not memorising rows 3 to 5 of that table; it is **using brackets when the answer is not instantly obvious to a reader**. `(1 + 2) * (3 ** 2)` costs four characters and removes all doubt. Reviewers never complain about clarifying parentheses.

> **Gotcha:** the trap in real code is mixing `/` and `*` in an average or a percentage. `total / count * 100` is `(total / count) * 100`, which is usually right — but `total / (count * 100)` is a completely different number, and both look plausible in a diff. Bracket it.

---

## 3. Floats are approximate

Run this:

```python
print(0.1 + 0.2)              # 0.30000000000000004
print(0.1 + 0.2 == 0.3)       # False
```

Nothing is broken. Here is why, and it matters enough to spend five minutes on.

Computers store numbers in binary — sums of halves, quarters, eighths, sixteenths. Some decimal fractions have no exact binary form, exactly as one third has no exact decimal form (0.3333… forever). `0.1` is one of those. What gets stored is the closest available binary value:

```python
print(format(0.1, ".20f"))    # 0.10000000000000000555
print(format(0.2, ".20f"))    # 0.20000000000000001110
print(format(0.3, ".20f"))    # 0.29999999999999998890
```

Add the first two and the tiny errors combine into something that is *not* the stored version of `0.3`. Hence `False`.

This affects every language that uses the IEEE 754 double-precision standard, which is nearly all of them. It is a property of binary fractions, not a Python defect.

### 3.1 What to do about it

**Never compare floats with `==`.** Compare with a tolerance:

```python
a = 0.1 + 0.2
b = 0.3
print(abs(a - b) < 1e-9)      # True — "close enough"
```

**Round for display, at the last moment:**

```python
print(round(0.1 + 0.2, 2))    # 0.3
print(f"{0.1 + 0.2:.2f}")     # 0.30
```

**Errors accumulate.** One addition is invisible; ten thousand are not:

```python
total = 0.0
count = 0
while count < 10:
    total += 0.1
    count += 1
print(total)                  # 0.9999999999999999
print(total == 1.0)           # False
```

(That loop is Day 4 syntax; today just read the result.)

**For money, use whole numbers of the smallest unit.** Count pence, cents, satoshis — integers are exact:

```python
price_pence = 1999          # £19.99 stored as an integer
quantity = 3
total_pence = price_pence * quantity
print(total_pence)                              # 5997
print("Total: £" + str(total_pence / 100))      # Total: £59.97
```

Python also ships `decimal.Decimal` and `fractions.Fraction` for exact decimal and rational arithmetic. They are the right answer for financial systems, they are slower, and they are Day 17 material. Knowing they exist is today's job.

> **Gotcha:** `round()` does not fix a float, it produces another float. `round(2.675, 2)` is `2.67` because the stored value of `2.675` is very slightly below the true 2.675. If a rounding result must be exact to the penny, do the arithmetic in integers.

---

## 4. Casting: converting between types

Three conversion tools, all named after the type they produce.

```python
print(int("42"), type(int("42")))          # 42 <class 'int'>
print(float("3.5"), type(float("3.5")))    # 3.5 <class 'float'>
print(str(42), type(str(42)))              # 42 <class 'str'>
```

### 4.1 `int()`

```python
print(int("42"))       # 42
print(int(" 42 "))     # 42     surrounding whitespace is allowed
print(int("-7"))       # -7
print(int("+7"))       # 7
print(int(3.9))        # 3      truncates towards zero, does NOT round
print(int(-3.9))       # -3     also towards zero
print(int(True))       # 1
print(int(False))      # 0
```

Two behaviours to separate carefully: `int()` on a **float** truncates; `int()` on a **string** demands a clean whole number and refuses anything else.

```python
int("3.5")      # ValueError: invalid literal for int() with base 10: '3.5'
int("abc")      # ValueError: invalid literal for int() with base 10: 'abc'
int("")         # ValueError: invalid literal for int() with base 10: ''
int("1,000")    # ValueError — the comma is not part of a number
int("4 2")      # ValueError — the inner space is not allowed
int(None)       # TypeError: int() argument must be a string ... not 'NoneType'
```

Note the pattern: bad *content* in a string is a `ValueError`; the wrong *kind* of thing entirely is a `TypeError`. That distinction is worth internalising now, because on Day 9 you will catch them separately.

If you have text like `"3.5"` and want a whole number, convert in two steps and choose your rounding:

```python
print(int(float("3.5")))        # 3   truncate
print(round(float("3.5")))      # 4   round (to even, so 2.5 -> 2)
```

### 4.2 `float()`

More permissive, because floats have more valid spellings:

```python
print(float("3.5"))      # 3.5
print(float("42"))       # 42.0
print(float(" 2.5 "))    # 2.5
print(float("1e3"))      # 1000.0     scientific notation
print(float("-.5"))      # -0.5
print(float("inf"))      # inf        a real float value: infinity
print(float(7))          # 7.0
```

And it still refuses nonsense:

```python
float("abc")      # ValueError: could not convert string to float: 'abc'
float("")         # ValueError: could not convert string to float: ''
float("3,5")      # ValueError — comma decimal separators are not understood
```

### 4.3 `str()`

`str()` never fails. Every value in Python can describe itself as text.

```python
print(str(42))         # 42
print(str(3.14))       # 3.14
print(str(True))       # True
print(str(None))       # None
print(repr("hi"))      # 'hi'    <- repr adds the quotes; str does not
```

Use `str()` when you need to glue a number into text with `+`. Once you have f-strings (section 10) you will rarely need it explicitly.

### 4.4 `bool()`

Not on today's list, but it completes the set and you will meet it tomorrow:

```python
print(bool(0), bool(1), bool(-1))        # False True True
print(bool(""), bool("a"), bool("0"))    # False True True
```

`bool("0")` is `True`, because `"0"` is a non-empty string. That trips people up. Day 3 covers truthiness properly.

### 4.5 The conversion table

| Call | Result | Notes |
|---|---|---|
| `int("42")` | `42` | whitespace ok, sign ok |
| `int("3.5")` | **ValueError** | strings must be whole numbers |
| `int(3.5)` | `3` | truncates towards zero |
| `int("")` | **ValueError** | |
| `float("3.5")` | `3.5` | |
| `float("1e3")` | `1000.0` | |
| `float("abc")` | **ValueError** | |
| `str(3.5)` | `"3.5"` | never fails |
| `int(True)` | `1` | `bool` is a kind of `int` |
| `int(None)` | **TypeError** | wrong type, not bad content |

> **Gotcha:** a string of digits is not a number. `"10" > "9"` is `False`, because text compares character by character and `"1"` comes before `"9"` in the alphabet. Convert before comparing.

---

## 5. Strings are sequences: indexing

A string is an ordered sequence of characters, and each character has a position — its **index**. Indexes start at **0**.

```python
word = "Python"
print(word[0])     # P
print(word[1])     # y
print(word[5])     # n
print(len(word))   # 6
```

```
  P  y  t  h  o  n
  0  1  2  3  4  5      <- index
 -6 -5 -4 -3 -2 -1      <- negative index
```

Zero-based indexing feels arbitrary for about a week and then feels correct. The payoff: the index is the *offset from the start*, so `word[0]` is "0 characters in from the beginning", and the mathematics of slicing comes out clean.

The last valid index is `len(word) - 1`. Going past it is an error:

```python
word = "Python"
print(word[6])
```

```
IndexError: string index out of range
```

`IndexError` is the fourth error type you have met, and it always means the same thing: you asked for a position that is not there. The classic cause is writing `len(x)` where you meant `len(x) - 1`.

### 5.1 Negative indexing

Negative indexes count from the right, starting at `-1`:

```python
word = "Python"
print(word[-1])    # n    last character
print(word[-2])    # o    second to last
print(word[-6])    # P    same as word[0]
print(word[-7])    # IndexError
```

Why `-1` and not `-0`? Because `-0` is `0`, which already means "first". So the right-hand end starts at `-1`.

This is genuinely useful. Compare:

```python
filename = "report.csv"
print(filename[len(filename) - 1])    # v    correct, and ugly
print(filename[-1])                   # v    same thing, obviously
```

### 5.2 Characters are strings

There is no separate character type in Python. `word[0]` is a string of length 1, and every string operation works on it:

```python
letter = "Python"[0]
print(letter, type(letter), len(letter))     # P <class 'str'> 1
print(letter.lower())                        # p
```

---

## 6. Slicing

Indexing gives one character. **Slicing** gives a substring. The syntax has three parts, all optional:

```
text[start:stop:step]
```

- `start` — first index included (default: 0)
- `stop` — first index **excluded** (default: end of string)
- `step` — how far to jump each time (default: 1)

```python
text = "Python"
print(text[0:2])      # Py     indexes 0 and 1 — NOT 2
print(text[2:5])      # tho    indexes 2, 3, 4
print(text[:3])       # Pyt    from the start
print(text[3:])       # hon    to the end
print(text[:])        # Python everything (a full copy)
print(text[::2])      # Pto    every second character
print(text[1::2])     # yhn    every second, starting at index 1
print(text[::-1])     # nohtyP reversed
```

### 6.1 Why `stop` is excluded

This is the design decision that makes everything else neat, so it is worth the paragraph:

- `len(text[a:b])` is exactly `b - a`. `text[0:3]` has 3 characters. No mental arithmetic.
- `text[:n] + text[n:]` reconstructs the original for any `n`. Slices join up with no gaps and no overlaps.
- The index in `text[i]` and the boundary in `text[i:]` are the same number.

Half-open ranges (include the start, exclude the stop) are used by `range` (Day 4) and by list slicing (Day 5) for the same reasons. Learn the pattern once, apply it everywhere.

### 6.2 Slices are forgiving, indexes are not

An out-of-range *index* raises. An out-of-range *slice* silently clips:

```python
text = "Python"
print(text[2:100])     # thon    no error, just stops at the end
print(text[100:])      # ''      empty string, no error
print(text[4:2])       # ''      start after stop -> empty
print(text[100])       # IndexError
```

This asymmetry is a frequent source of silent bugs: a slice that returns `""` when you expected content will not announce itself. If a slice comes back empty and you did not expect that, check your numbers.

### 6.3 Negative slicing

```python
filename = "report.csv"
print(filename[-4:])       # .csv    last four characters
print(filename[:-4])       # report  everything except the last four
print(filename[-3:])       # csv
print(filename[::-1])      # vsc.troper

card = "4111111111111234"
print("Last four:", card[-4:])                    # 1234
print("Masked:", "*" * 12 + card[-4:])            # ************1234
```

`text[:-n]` — "everything except the last n characters" — is one of the most useful idioms in the language.

### 6.4 A negative step reverses direction

```python
text = "abcdefg"
print(text[::-1])       # gfedcba   reversed
print(text[::-2])       # geca      every second, backwards
print(text[5:2:-1])     # fed       from index 5 down to (not including) 2
```

With a negative step, `start` should be *greater* than `stop`, because you are walking backwards. `text[2:5:-1]` gives `""` — no error, just nothing, because you cannot walk backwards from 2 to reach 5.

> **Gotcha:** `text[::-1]` is the standard way to reverse a string, and it *looks* like a hieroglyph. Read it as "no start, no stop, step backwards by one". You will meet it in other people's code, so recognise it.

---

## 7. Strings are immutable

A string cannot be changed after it is created. Full stop.

```python
word = "python"
word[0] = "P"
```

```
TypeError: 'str' object does not support item assignment
```

Every string method that appears to modify a string in fact **returns a new string** and leaves the original alone:

```python
name = "ada"
name.upper()
print(name)          # ada   <- unchanged! the new string was discarded

name = name.upper()  # rebind the name to the result
print(name)          # ADA
```

This is the most common single mistake of Week 1. `name.upper()` computes a value; if you do not store it, it is thrown away, exactly like `2 + 2` on a line by itself.

To "change" a string, build a new one:

```python
word = "python"
word = "P" + word[1:]        # take the tail, glue a new head on
print(word)                  # Python

# Or use the tool designed for it:
print("hello world".replace("world", "there"))   # hello there
```

Why would a language forbid modification? Three real benefits:
- **Safety.** A string you pass into someone else's code cannot come back altered. No defensive copying.
- **Dictionary keys.** Only unchangeable values can be dictionary keys (Day 6) — a key that mutated would get lost.
- **Speed.** Python can reuse identical strings freely, because nothing can change one under another name.

Numbers, `bool`, `None` and tuples (Day 5) are immutable too. Lists, dicts and sets are mutable, and on Day 5 you will see what a difference that makes.

> **Gotcha:** `text.strip()` on its own line does nothing useful. If you find yourself surprised that a value "did not change", check whether you stored the result. `text = text.strip()` is the line you meant.

---

## 8. The string methods you will actually use

A **method** is a function attached to a value, called with a dot: `value.method(args)`. Strings have around 45; these fifteen cover almost everything you will do this week.

Since strings are immutable, every one of these returns something new. None of them modify the original.

### 8.1 Cleaning: `strip`, `lstrip`, `rstrip`

```python
raw = "  hello  \n"
print(repr(raw.strip()))       # 'hello'      both ends
print(repr(raw.lstrip()))      # 'hello  \n'  left only
print(repr(raw.rstrip()))      # '  hello'    right only
```

By default `strip()` removes whitespace — spaces, tabs, newlines. Pass a string and it removes any of *those characters* from the ends, in any order, until it hits something else:

```python
print("...hello!!!".strip(".!"))       # hello
print("xxhixx".strip("x"))             # hi
print("hello".strip("lo"))             # he      <- both l and o stripped from the right
```

That last one catches people. `strip("lo")` is not "remove the substring 'lo'"; it is "remove any of the characters l or o from either end". Use `replace` or a slice for substrings.

`strip()` on input is close to mandatory. Users add trailing spaces; files have trailing newlines.

### 8.2 Case: `lower`, `upper`, `title`, `capitalize`, `casefold`

```python
text = "hELLo woRLD"
print(text.lower())        # hello world
print(text.upper())        # HELLO WORLD
print(text.title())        # Hello World      first letter of each word
print(text.capitalize())   # Hello world      first letter of the string only
print(text.casefold())     # hello world      aggressive lowercase
```

`lower()` is what you use to compare text case-insensitively:

```python
answer = "YES"
print(answer.lower() == "yes")     # True
```

`casefold()` is `lower()` for the whole world — it handles cases like German `"ß"`, which casefolds to `"ss"`:

```python
print("Straße".lower())        # straße
print("Straße".casefold())     # strasse
print("Straße".lower() == "strasse")      # False
print("Straße".casefold() == "strasse")   # True
```

Rule: `lower()` for display, `casefold()` for comparing. Day 7's project uses `casefold()`.

`title()` is naive — it capitalises after every non-letter:

```python
print("o'brien mcdonald".title())     # O'Brien Mcdonald   <- not what a human wants
```

Fine for tidying a word list, wrong for real names.

### 8.3 Splitting and joining: `split`, `join`, `splitlines`

`split()` breaks a string into a list of pieces. (Lists are Day 5; today you use the result as a whole or index into it.)

```python
print("a,b,c".split(","))            # ['a', 'b', 'c']
print("one two  three".split())      # ['one', 'two', 'three']
print("a,b,,c".split(","))           # ['a', 'b', '', 'c']
print("a-b-c".split("-", 1))         # ['a', 'b-c']     maxsplit=1
```

Two importantly different behaviours:
- `split()` with **no argument** splits on any run of whitespace and discards empty pieces. `"a  b".split()` is `['a', 'b']`.
- `split(",")` with an argument splits on every single occurrence and keeps empties. `"a,,b".split(",")` is `['a', '', 'b']`.

The no-argument form is what you want for words in a sentence. The argument form is what you want for structured data, where an empty field is meaningful.

`join` is the reverse, and its shape surprises everyone: the **separator** is the string you call it on, and the pieces are the argument.

```python
print("-".join(["2024", "03", "01"]))       # 2024-03-01
print(" ".join(["hello", "world"]))         # hello world
print("".join(["a", "b", "c"]))             # abc
print(", ".join(["x", "y"]))                # x, y
```

`"-".join(...)` reads as "put a dash between each of these". Every piece must already be a string — `" ".join([1, 2])` raises `TypeError: sequence item 0: expected str instance, int found`.

Split then join is the standard way to normalise whitespace, and you will use it in Day 07's `clean_text`:

```python
messy = "  too    many   spaces\there  "
print(repr(" ".join(messy.split())))       # 'too many spaces here'
```

Read that from the inside out: `split()` breaks on every run of whitespace and throws the whitespace away; `" ".join(...)` puts exactly one space back between the pieces. Tabs, newlines and double spaces all collapse.

`splitlines()` splits on line breaks:

```python
print("a\nb\nc".splitlines())      # ['a', 'b', 'c']
```

Two things you can usefully do with the list that comes back, before Day 5 teaches lists properly: take its length, and index it.

```python
sentence = "the cat sat on the mat"
print(len(sentence.split()))       # 6    <- a word count, in one line
print(sentence.split()[0])         # the  <- the first word
print("".join(sentence.split()))   # thecatsatonthemat  <- letters only
```

`len(text.split())` is the standard word count and you will use it today.

### 8.4 Replacing: `replace`

```python
print("hello world".replace("world", "there"))     # hello there
print("a-b-c".replace("-", ""))                    # abc
print("aaa".replace("a", "b", 2))                  # bba    at most 2 replacements
print("hello".replace("z", "x"))                   # hello  no match, no error
```

`replace` acts on every occurrence unless you cap it, and never complains when there is nothing to replace.

### 8.5 Testing: `startswith`, `endswith`, `in`, `isdigit`

```python
name = "report.csv"
print(name.startswith("rep"))        # True
print(name.endswith(".csv"))         # True
print(name.endswith((".csv", ".tsv")))   # True — a tuple means "any of these"
print("port" in name)                # True     substring test
print("xyz" in name)                 # False
```

`in` is an operator, not a method, and it is the most readable way to ask "does this contain that".

The `is*` family asks what a string is made of. Each returns `True` only if **every** character qualifies and the string is not empty:

```python
print("42".isdigit())        # True
print("4.2".isdigit())       # False    the dot is not a digit
print("-42".isdigit())       # False    nor is the minus sign
print("".isdigit())          # False    empty is never True
print("abc".isalpha())       # True
print("abc123".isalnum())    # True
print("   ".isspace())       # True
print("Hello".istitle())     # True
```

`isdigit()` is the standard pre-check before `int()` — it lets you avoid the `ValueError` instead of handling it. Note the two things it does *not* accept: decimal points and minus signs. `"-42".isdigit()` is `False`, so a check for negative numbers needs more than this.

### 8.6 Finding and counting: `find`, `index`, `count`

```python
text = "the cat sat on the mat"
print(text.find("cat"))       # 4      index where it starts
print(text.find("dog"))       # -1     not found — no error
print(text.find("the", 1))    # 15     start searching from index 1
print(text.count("the"))      # 2
print(text.count("t"))        # 5
print(text.count("z"))        # 0
```

`index()` does the same as `find()` but raises `ValueError` when it fails instead of returning `-1`. Use `find` when absence is normal, `index` when absence is a bug.

> **Gotcha:** `-1` is a real index (the last character), so `if text.find("x")` treats "not found" as truthy nonsense. Compare explicitly: `text.find("x") == -1`. Better still, if you only need to know whether it is there, use `in`.

### 8.7 Padding: `ljust`, `rjust`, `center`, `zfill`

```python
print("ab".ljust(6, ".") + "|")     # ab....|
print("ab".rjust(6, ".") + "|")     # ....ab|
print("ab".center(6, ".") + "|")    # ..ab..|
print("7".zfill(3))                 # 007
```

These are the older way to align text. f-string format specs (section 10) do the same thing more concisely, and that is what you should reach for — but you will see these in existing code, and `zfill` is still the neatest way to pad a number with leading zeros.

### 8.8 The reference table

| Method | Returns | Example |
|---|---|---|
| `strip(chars=None)` | new `str` | `"  hi  ".strip()` -> `"hi"` |
| `lower()` / `upper()` | new `str` | `"Hi".lower()` -> `"hi"` |
| `title()` | new `str` | `"ada lovelace".title()` -> `"Ada Lovelace"` |
| `casefold()` | new `str` | `"Straße".casefold()` -> `"strasse"` |
| `split(sep=None)` | `list[str]` | `"a b".split()` -> `["a", "b"]` |
| `join(parts)` | new `str` | `"-".join(["a","b"])` -> `"a-b"` |
| `replace(old, new)` | new `str` | `"aa".replace("a","b")` -> `"bb"` |
| `startswith(p)` | `bool` | `"hi.py".startswith("hi")` -> `True` |
| `endswith(p)` | `bool` | `"hi.py".endswith(".py")` -> `True` |
| `find(sub)` | `int` or `-1` | `"abc".find("c")` -> `2` |
| `count(sub)` | `int` | `"aaa".count("a")` -> `3` |
| `isdigit()` | `bool` | `"42".isdigit()` -> `True` |
| `sub in text` | `bool` | `"a" in "cat"` -> `True` |
| `ljust/rjust/center(w)` | new `str` | `"a".rjust(3)` -> `"  a"` |
| `len(text)` | `int` | `len("abc")` -> `3` |

---

## 9. Building strings: three ways, one winner

```python
name = "Ada"
age = 36

# 1. Concatenation — verbose, needs str(), easy to lose a space
print("Name: " + name + ", age " + str(age))

# 2. print with several arguments — fine for quick output, no control
print("Name:", name + ",", "age", age)

# 3. f-string — say what you mean
print(f"Name: {name}, age {age}")
```

All three print `Name: Ada, age 36`. From here on, use f-strings.

---

## 10. f-strings

Put `f` before the opening quote, and any `{expression}` inside is replaced by its value.

```python
name = "Ada"
age = 36
print(f"{name} is {age}")                 # Ada is 36
print(f"{name} will be {age + 1} soon")   # Ada will be 37 soon
print(f"{name.upper()} has {len(name)} letters")   # ADA has 3 letters
print(f"2 + 2 = {2 + 2}")                 # 2 + 2 = 4
```

Anything that produces a value can go in the braces: arithmetic, method calls, indexing. Conversion to text is automatic — no `str()` needed, ever.

Literal braces need doubling:

```python
print(f"{{not a placeholder}}")     # {not a placeholder}
```

### 10.1 Format specifications

After the value, a colon introduces a **format spec** that controls how the value is rendered. This is where f-strings stop being convenient and start being essential.

**Decimal places — `:.Nf`**

```python
pi = 3.14159265
print(f"{pi:.2f}")            # 3.14
print(f"{pi:.0f}")            # 3
print(f"{pi:.5f}")            # 3.14159
print(f"{2:.2f}")             # 2.00      <- pads to two places
print(f"{1/3:.3f}")           # 0.333
```

`:.2f` is the money format, and it pads as well as truncates: `2` becomes `2.00`, which is what a price column needs.

**Width and alignment — `:<N`, `:>N`, `:^N`**

```python
print(f"[{'ab':<10}]")        # [ab        ]   left, padded right
print(f"[{'ab':>10}]")        # [        ab]   right, padded left
print(f"[{'ab':^10}]")        # [    ab    ]   centred
print(f"[{'ab':*^10}]")       # [****ab****]   centred, padded with *
print(f"[{'ab':.<10}]")       # [ab........]   left, padded with .
```

Remember the arrows point where the text goes: `<` pushes it left, `>` pushes it right, `^` centres it.

Defaults differ by type, which is why you should be explicit: strings default to left-aligned, numbers to right-aligned.

```python
print(f"[{'ab':10}]")         # [ab        ]   string: left by default
print(f"[{42:10}]")           # [        42]   number: right by default
```

**Thousands separator — `:,`**

```python
print(f"{1234567:,}")         # 1,234,567
print(f"{1234567.891:,.2f}")  # 1,234,567.89
print(f"{1234567:_}")         # 1_234_567
```

**Combining them.** The full order is `[[fill]align][sign][width][,][.precision][type]`:

```python
print(f"{1234.5678:>12,.2f}")     #     1,234.57
print(f"{42:05d}")                # 00042        zero-padded integer
print(f"{0.4567:.1%}")            # 45.7%        percentage
print(f"{255:x}")                 # ff           hexadecimal
print(f"{5:+d}")                  # +5           always show the sign
```

This is exactly how you build an aligned table without counting spaces by hand:

```python
print(f"{'Item':<12}{'Qty':>5}{'Price':>10}")
print(f"{'-' * 27}")
print(f"{'widget':<12}{2:>5}{9.99:>10.2f}")
print(f"{'bolt':<12}{10:>5}{0.5:>10.2f}")
```

```
Item          Qty     Price
---------------------------
widget          2      9.99
bolt           10      0.50
```

Day 07's M5 `render_report` is that idea and nothing more.

### 10.2 Nested quotes

The quote style inside the braces must differ from the one delimiting the string (before Python 3.12, which relaxed this):

```python
data = "a,b"
print(f"first piece: {data.split(',')[0]}")     # single quotes inside double
```

### 10.3 The `=` specifier: instant debugging

Put `=` after an expression and the f-string prints the expression text as well as its value:

```python
total = 42
name = "Ada"
print(f"{total=}")                # total=42
print(f"{name=}")                 # name='Ada'
print(f"{total * 2=}")            # total * 2=84
print(f"{len(name)=}")            # len(name)=3
```

Notice `name='Ada'` keeps the quotes: `=` uses `repr()`, so you can see whitespace and tell `42` from `"42"`. This is the fastest debugging tool in Python — better than a bare `print(total)`, because the label cannot drift out of sync with the value. Use it constantly, and delete it before you commit.

You can add a space for readability, and combine with a spec:

```python
price = 1234.5678
print(f"{price = }")           # price = 1234.5678
print(f"{price=:.2f}")         # price=1234.57
```

> **Gotcha:** an f-string is evaluated **immediately**, at the moment the line runs. It is not a template you can fill in later. And if you forget the `f`, you get the braces printed literally — `print("{name}")` outputs `{name}`, which is a five-second bug that has embarrassed everyone.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Expecting `/` to give an int | `10 / 2` is `5.0` | use `//` for whole numbers |
| `-7 // 2` "should be" `-3` | `-4` | `//` floors; `int(-7/2)` truncates |
| Comparing floats with `==` | `0.1 + 0.2 == 0.3` is `False` | compare with a tolerance, or use ints for money |
| `int("3.5")` | `ValueError: invalid literal for int()` | `int(float("3.5"))` |
| Trusting `round` to be exact | `round(2.675, 2)` is `2.67` | do money arithmetic in pence |
| Calling a method and ignoring the result | the string "did not change" | `text = text.strip()` |
| `text[0] = "X"` | `TypeError: 'str' object does not support item assignment` | build a new string: `"X" + text[1:]` |
| `text[len(text)]` | `IndexError: string index out of range` | last index is `len(text) - 1`, or use `text[-1]` |
| Expecting `text[0:3]` to include index 3 | one character short of what you wanted | `stop` is excluded, always |
| `strip("lo")` to remove a substring | `"hello".strip("lo")` is `"he"` | `strip` takes a *character set*; use `replace` |
| `"a".join(list_of_ints)` | `TypeError: sequence item 0: expected str` | convert the pieces to strings first |
| `if text.find("x"):` | `-1` is truthy, so "not found" looks found | `text.find("x") == -1`, or use `in` |
| Forgetting the `f` | `{name}` printed literally | add the `f` prefix |
| `"10" > "9"` | `False` | convert to numbers before comparing |
| `split()` vs `split(",")` on empties | unexpected `''` entries, or none | no-arg drops empties, with-arg keeps them |

---

## Mental model

Think of a string as a **row of numbered pigeonholes, sealed under glass**.

```
        P    y    t    h    o    n
      +----+----+----+----+----+----+
      |  0 |  1 |  2 |  3 |  4 |  5 |     index from the left
      | -6 | -5 | -4 | -3 | -2 | -1 |     index from the right
      +----+----+----+----+----+----+
      0    1    2    3    4    5    6     <- slice boundaries live BETWEEN holes

      text[2]     -> "t"        one pigeonhole
      text[2:5]   -> "tho"      everything between boundary 2 and boundary 5
      text[:3]    -> "Pyt"      from the left wall to boundary 3
      text[-2:]   -> "on"       from boundary -2 to the right wall
      text[::-1]  -> "nohtyP"   walk the row backwards
```

- **Indexes name pigeonholes; slice numbers name the gaps between them.** That is why `stop` is excluded and why `text[:n] + text[n:]` always rebuilds the original — you cut at a gap, you lose nothing.
- **The glass is the immutability.** You can read any hole and photocopy any run of holes, but you cannot write into one. `upper()` hands you a whole new row; the old one is untouched, and is lost unless you keep hold of it.
- **Numbers are a different kind of thing.** `int` is exact and unbounded. `float` is a binary approximation with about 15 useful digits — fast, close, and not exact. Choosing between them is choosing between "must be right" and "must be quick".
- **f-strings are the label printer.** The value stays what it is; the spec decides how it looks on the shelf: `:.2f` for money, `:>10` for a right-aligned column, `:,` for readability.

---

## Practice

1. Run the demo and read every line of output against the code that produced it:

   ```bash
   python course/week1/day02_numbers_and_strings/examples.py
   ```

2. Ten minutes in the REPL, predicting before you press Enter:

   ```bash
   python
   ```

   Try: `7 // 2`, `-7 // 2`, `7 % 2`, `2 ** 0.5`, `0.1 + 0.2`, `round(2.5)`, `round(3.5)`, `int("3.5")`, `"Python"[-2:]`, `"Python"[::-1]`, `"a,b,,c".split(",")`, `"a b".split()`, `"-".join(["x","y"])`, `"hello".strip("lo")`, `f"{1234.5:>12,.2f}"`, `f"{'ab':^9}|"`. For each one, decide the answer first. Getting them wrong in the REPL is free; getting them wrong on Day 7 is not.

3. Open `course/week1/day02_numbers_and_strings/exercises.py` and work top to bottom. The docstring examples are what the tests check.

4. Grade yourself from the course root:

   ```bash
   python check.py day02
   python check.py day02 -v
   ```

5. Extra rep: write a script that turns `4000` seconds into `"01:06:40"` using only `//`, `%` and an f-string with `:02d`. Then make it handle `359999`. Then check what happens at `360000` and decide whether you care.

---

## Recall check

1. What is the difference between `7 / 2`, `7 // 2` and `7 % 2`? What does `-7 // 2` give, and why?
2. Why is `0.1 + 0.2 == 0.3` `False`, and what are two ways to work around it?
3. Which of these raise `ValueError`: `int("42")`, `int("3.5")`, `int(3.5)`, `float("abc")`, `str(None)`?
4. `text = "Python"`. Give the value of `text[1]`, `text[-1]`, `text[1:3]`, `text[:2]`, `text[-2:]`, `text[::-1]`.
5. What does "strings are immutable" mean in practice, and what is the fix for `name.upper()` appearing not to work?
6. What is the difference between `"a b  c".split()` and `"a,b,,c".split(",")`?
7. Write the f-string that prints `1234.5678` as `  1,234.57` (right-aligned in width 10, two decimals, thousands separator).
8. What does `f"{total=}"` print when `total` is `42`, and why is it better than `print(total)`?

<details>
<summary>Answers</summary>

1. `7 / 2` is `3.5` (true division, always a float). `7 // 2` is `3` (floor division: how many whole 2s fit). `7 % 2` is `1` (the remainder). `-7 // 2` is `-4`, because floor division rounds *down* towards negative infinity, not towards zero — `-7 / 2` is `-3.5` and the next integer down is `-4`. Use `int(-7 / 2)` for `-3`.
2. Because binary cannot represent `0.1`, `0.2` or `0.3` exactly, so the stored values are slightly off and the two small errors do not cancel. Workarounds: compare with a tolerance (`abs(a - b) < 1e-9`), round for display (`f"{x:.2f}"`), or do the arithmetic in integers of the smallest unit (pence). `decimal.Decimal` is the heavyweight option, Day 17.
3. `int("3.5")` and `float("abc")` raise `ValueError`. `int("42")` is `42`, `int(3.5)` is `3` (truncation, no error), `str(None)` is `"None"` (`str` never fails).
4. `"y"`, `"n"`, `"yt"`, `"Py"`, `"on"`, `"nohtyP"`.
5. No operation can change an existing string; every method returns a new one. So `name.upper()` computes a new string and discards it unless you keep it. The fix is to store the result: `name = name.upper()`.
6. `split()` with no argument splits on any run of whitespace and drops empty pieces, giving `['a', 'b', 'c']`. `split(",")` splits on every single comma and keeps empties, giving `['a', 'b', '', 'c']`. Use the first for words, the second for structured fields where a blank means something.
7. `f"{1234.5678:>10,.2f}"`. (The order is align, width, comma, precision, type.)
8. It prints `total=42` — the expression text plus its value, using `repr` for the value. Better than `print(total)` because the label is generated from the expression, so it cannot drift out of date, and `repr` makes `42` and `"42"` visibly different.

</details>
