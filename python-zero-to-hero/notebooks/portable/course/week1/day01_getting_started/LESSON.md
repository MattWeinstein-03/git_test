# Day 01 — Getting Started

> **Time:** ~4 hours  |  **Prerequisites:** none — this is the first day

## What you'll be able to do after today
- Explain what a program is, and describe what happens between pressing Enter on `python file.py` and seeing output.
- Choose correctly between the interactive prompt (the REPL) and a saved script, and move code from one to the other.
- Store values in named variables, rebind those names, and say why "a name points at a value" is more accurate than "a box holds a value".
- Recognise and produce the five starting types — `int`, `float`, `str`, `bool`, `None` — and inspect any value with `type()`.
- Control `print` precisely: several values in one call, a custom separator, and a custom line ending.
- Read text from a person with `input()`, and remember without fail that what comes back is *always* a string.
- Read a `SyntaxError` and a `NameError` and fix the line they point at, instead of staring at the whole file.

## Why this matters

Everything in this course is variables and function calls. Loops, dictionaries, classes, web requests — all of it is built from "give this value a name" and "call this thing with those inputs". If today's ideas are shaky, every later day is guesswork dressed up as progress.

There is also a practical payoff on day one: the two errors you will meet more than any others in your first fortnight are `SyntaxError` and `NameError`, and both are mechanically fixable once you know how to read them. Beginners lose whole evenings to errors that experienced programmers fix in four seconds — not because they are cleverer, but because they read the last line of the message first. You are going to learn that today.

---

## 1. What a program actually is

A computer does an extraordinarily small number of things: it moves numbers around, it does arithmetic, it compares values, and it chooses what to do next based on the result. That is close to the whole list. Everything you have ever seen a computer do — video calls, spreadsheets, games — is an enormous pile of those four operations arranged carefully.

A **program** is a written description of that arrangement: a list of instructions, in order, precise enough that no judgement is required to follow them.

The word "precise" is doing all the work in that sentence. Compare two sets of instructions for the same task:

```
Instructions for a person:              Instructions for a computer:
  Make me a cup of tea.                   1. Fill the kettle with 300ml of water.
                                          2. Switch the kettle on.
                                          3. Wait until the water boils.
                                          4. Put one teabag in a mug.
                                          5. Pour 250ml of boiled water into the mug.
                                          6. Wait 180 seconds.
                                          7. Remove the teabag.
```

A person fills the gaps from experience. A computer has no experience. If you do not say "switch the kettle on", it will not occur to the machine that this might be a good idea. It will pour cold water on the teabag and report success, because you told it to pour water and it poured water.

This is the single largest adjustment you have to make, and it is not a programming skill so much as a habit of thought:

> The computer does exactly what you said, at enormous speed, including when what you said is not what you meant.

Almost every bug you will ever write is a gap between those two things. Not a machine malfunction — a specification error, committed by you, executed faithfully.

### 1.1 Source code, languages, and why Python

You write instructions as text. Text a person can read but a machine cannot execute directly is called **source code**, and the vocabulary and grammar it is written in is a **programming language**.

Languages differ in how much they make you spell out. Here is "print a greeting" in C, then in Python:

```c
#include <stdio.h>

int main(void) {
    printf("Hello, world!\n");
    return 0;
}
```

```python
print("Hello, world!")
```

Both produce the same output. The C version obliges you to declare which toolbox you are borrowing from, name a starting function, say what type of value that function returns, mark the end of the line, and explicitly report success. Those details matter enormously when you are writing an operating system and matter not at all when you are counting words in a document.

Python's design bias is that **your time is more expensive than the computer's**. It fills in what it can, keeps the syntax close to English, and lets you say a lot in a line. That makes it the right first language, and — this part surprises people — also a completely respectable last one: Python runs a large fraction of the world's data analysis, machine learning, automation, and web backends.

### 1.2 A statement is a step

Here is a three-step program. Read it before the explanation.

```python
price = 250
tax = price * 0.2
print("Total:", price + tax)
```

Output:

```
Total: 300.0
```

Three lines, three **statements** — three complete instructions, executed strictly top to bottom:

1. Work out the value `250` and attach the name `price` to it.
2. Multiply whatever `price` refers to by `0.2`, and attach the name `tax` to the result.
3. Add `price` and `tax`, then display the label and the answer.

Order is not decoration. Move line 3 to the top and the program fails, because at that moment nothing named `price` exists yet. Python does not scan ahead looking for what you might have meant later; it starts at line 1 and works down.

> **Gotcha:** "top to bottom" is the rule for today. Later you will meet `if` (skip some lines), `for` (repeat some lines), and `def` (save some lines for later). None of those break the rule — they change *which* lines are next, and each one still runs completely before the next begins.

---

## 2. How Python runs your file

Type this into a file called `hello.py`:

```python
print("Hello, world!")
```

Then, in a terminal, in the same folder as the file:

```bash
python hello.py
```

Output:

```
Hello, world!
```

Between Enter and that output, roughly this happened:

```
   hello.py                the python program                    your screen
  +-------------+        +----------------------+              +--------------+
  | print("Hi") | -----> | 1 read the text      |              |              |
  +-------------+        | 2 check the grammar  | --- error? -> | SyntaxError  |
                         | 3 translate to       |              |              |
                         |   bytecode           |              |              |
                         | 4 execute it step    | --- output ->| Hi           |
                         |   by step            |              |              |
                         +----------------------+              +--------------+
```

Two facts from that diagram earn their keep immediately.

**Fact one: the grammar check happens before anything runs.** Python reads and validates the *whole file* before executing the first line. So this program prints nothing at all:

```python
print("this line is perfectly fine")
print("this line is not fine"      # <- missing closing bracket
```

```
  File "hello.py", line 2
    print("this line is not fine"
         ^
SyntaxError: '(' was never closed
```

The first `print` never ran. If you expected "perfectly fine" to appear before the complaint, adjust your model: a `SyntaxError` means Python could not understand the file well enough to begin, so it did not begin.

**Fact two: everything else happens while running.** A misspelled name, an impossible sum, a missing file — those are all discovered at the moment that line executes, so output before them does appear:

```python
print("first")
print(total)        # nothing called `total` exists
print("third")
```

```
first
Traceback (most recent call last):
  File "hello.py", line 2, in <module>
    print(total)
NameError: name 'total' is not defined
```

`first` printed. `third` did not — an unhandled error stops the program where it stands.

That difference (*"can't understand it"* versus *"understood it, tried it, it failed"*) is the first genuinely useful diagnostic distinction you own. When something goes wrong, look at whether earlier output appeared. If none did, you have a typo in the grammar. If some did, the problem is at the line where output stopped.

> **Gotcha:** on some systems `python` means Python 2, a version retired in 2020, and you need `python3` instead. Check with `python --version`. If it says 2.x, use `python3` everywhere this course says `python`. `python check.py doctor` from the course root verifies your setup.

---

## 3. The REPL versus scripts

There are two ways to run Python, and using the wrong one for the job is a genuine time sink.

### 3.1 The REPL

Type `python` with no filename and you land in the **REPL** — Read, Evaluate, Print, Loop. It reads one line, evaluates it, prints the result, and loops back for more. The `>>>` is Python's prompt asking for your next line.

```
$ python
Python 3.11.5 (main, Sep  5 2023, 09:27:31)
>>> 2 + 2
4
>>> name = "Ada"
>>> name.upper()
'ADA'
>>> len(name)
3
>>> exit()
```

Notice: no `print` needed. The REPL displays the value of whatever you typed automatically — that is the "P" in the acronym. In a script, an expression on its own line computes a value and silently throws it away.

```python
# In a script — this file prints NOTHING:
2 + 2
"hello".upper()

# You have to ask:
print(2 + 2)
print("hello".upper())
```

That single difference explains a very common early confusion: "it worked when I typed it, but my file does nothing".

Two REPL details worth knowing on day one:
- `_` (a single underscore) is the last result: `>>> 2 + 2` then `>>> _ * 10` gives `40`.
- Quoting differs. The REPL shows a string's *representation* with quotes (`'ADA'`); `print` shows its *contents* without them (`ADA`). Same string, two displays.

```
>>> "line1\nline2"
'line1\nline2'
>>> print("line1\nline2")
line1
line2
```

### 3.2 Scripts

A **script** is Python saved in a `.py` file and run with `python file.py`. It is repeatable, editable, shareable, and can be put under version control. All real work lives in scripts.

Use each for what it is good at:

| Use the REPL for | Use a script for |
|---|---|
| "What does `.split()` return exactly?" | Anything you will run more than once |
| Checking one line of syntax | Anything longer than about five lines |
| Inspecting a value's type or methods | Anything you want to keep or share |
| Quick arithmetic | Anything with a bug — you need to edit and re-run |

The professional workflow uses both at once: a script open in your editor, a REPL beside it for questions. When you are unsure what a piece of code does, do not guess and do not reason it out for ten minutes — paste it into the REPL and *look*. Four seconds, no ambiguity. Curiosity is cheap here; use it constantly.

> **Gotcha:** the REPL forgets everything when you close it. If you wrote something in the REPL that you want to keep, copy it into a file *now*.

---

## 4. Variables: names bound to values

A **variable** gives a value a name so you can refer to it later.

```python
message = "Hello"
count = 3
print(message, count)
```

```
Hello 3
```

Read `=` as "gets" or "is bound to", never as "equals". `count = 3` is a command: *make the name `count` refer to the value 3*. It is not a claim about the world, and it does not work in reverse:

```python
3 = count        # SyntaxError: cannot assign to literal here
```

The right-hand side is evaluated first, then the name is attached to the result. Which is why this famously non-mathematical line makes perfect sense:

```python
count = 3
count = count + 1
print(count)      # 4
```

Step by step: evaluate `count + 1` using the current value (3), get 4, then rebind the name `count` to 4. As an equation it is nonsense; as an instruction it is routine.

### 4.1 Name-binding, not boxes

Many tutorials say a variable is "a box you put a value in". That model is comfortable and it will actively mislead you around Day 5, so let us not install it.

The accurate picture: **values live somewhere in memory, and a name is a label pointing at one.**

```
     name          value in memory
  +---------+
  | message | ----------> "Hello"
  +---------+
  | count   | ----------> 3
  +---------+
```

Assignment moves the arrow. It does not copy the value into a container:

```python
a = "first"
b = a           # b now points at the SAME string as a
a = "second"    # only a's arrow moves
print(a)        # second
print(b)        # first
```

```
  a ---> "second"          (a was re-pointed)
  b ---> "first"           (b still points where it did)
```

With strings and numbers you can happily hold either model, because they can never be modified in place — nothing can happen to a value "behind another name's back". On Day 5 you meet lists, which *can* be modified in place, and there the box model produces confident wrong predictions. Learn the true one now while it costs nothing.

### 4.2 Several names, and one shortcut

```python
first = "Ada"
last = "Lovelace"

# Assign several names at once (only when the values are related):
x, y = 3, 4
print(x, y)          # 3 4

# Swap two names, no temporary variable needed:
x, y = y, x
print(x, y)          # 4 3
```

The right-hand side of `x, y = y, x` is fully evaluated before any binding happens, so the swap works. In many other languages this takes three lines and a variable called `temp`. (The machinery behind it is tuple packing and unpacking, Day 5.)

### 4.3 Choose names that survive a week

The value does not care what you call it. Your future self does.

```python
# Bad — you will not know what these mean tomorrow:
x = 1250
t = 0.2
r = x * t

# Good:
monthly_rent = 1250
tax_rate = 0.2
tax_due = monthly_rent * tax_rate
```

Both run identically. One is a document; the other is a puzzle. Names are the cheapest documentation in existence, and the only kind that is always in front of the reader.

> **Gotcha:** a name that does not exist yet cannot be read. `print(total)` before any `total = ...` gives `NameError: name 'total' is not defined`. Python will not invent a zero for you — see section 11.

---

## 5. The types you start with

Every value in Python has a **type**, which decides what the value can do. `5 + 3` is 8; `"5" + "3"` is `"53"`. Same `+`, different types, different meaning. Confusing the two is the most frequent beginner bug in this whole week, so today you learn to check rather than assume.

Five types are enough to start.

### 5.1 `int` — whole numbers

```python
apples = 7
temperature = -4
big = 9_000_000_000_000      # underscores are ignored; they just aid reading
print(apples, temperature, big)
```

```
7 -4 9000000000000
```

Python integers have **no size limit** other than your memory. `2 ** 1000` is an exact answer, not an overflow. This is unusual and genuinely useful.

### 5.2 `float` — numbers with a decimal point

```python
price = 19.99
ratio = 2 / 4          # division ALWAYS produces a float
whole = 4.0            # a float, despite being a whole number
print(price, ratio, whole)
```

```
19.99 0.5 4.0
```

`4` and `4.0` are equal in value (`4 == 4.0` is `True`) but they are different types. Floats are stored as binary fractions, which means they are approximate:

```python
print(0.1 + 0.2)          # 0.30000000000000004
```

That is not a Python bug; it is how essentially every language stores decimals in binary, for the same reason you cannot write one third exactly in decimal. It gets a proper section tomorrow. For today, take away one rule: **never use floats for money you must get exactly right**, and be suspicious of `==` between floats.

### 5.3 `str` — text

A **string** is a sequence of characters in quotes. Single or double, your choice, but be consistent — this course uses double.

```python
name = "Ada"
greeting = 'Hello'
empty = ""                      # a real string, zero characters long
quoted = "She said \"hi\""      # backslash escapes the inner quotes
easier = 'She said "hi"'        # or switch quote style and avoid escaping
print(name, greeting, empty, quoted, easier)
```

```
Ada Hello  She said "hi" She said "hi"
```

Multi-line strings use triple quotes, and keep their line breaks:

```python
address = """221B Baker Street
London
NW1 6XE"""
print(address)
```

```
221B Baker Street
London
NW1 6XE
```

Two escape sequences you will use constantly: `\n` is a newline, `\t` is a tab.

```python
print("Name:\tAda\nCity:\tLondon")
```

```
Name:	Ada
City:	London
```

Join strings end to end with `+`:

```python
first = "Ada"
last = "Lovelace"
print("Name: " + first + " " + last)
```

```
Name: Ada Lovelace
```

Note the deliberate spaces inside the quoted pieces. `+` glues *exactly* what you give it — `"Ada" + "Lovelace"` is `"AdaLovelace"`. (Tomorrow you get f-strings, a far better way to build text than this. Today, `+` and `print`'s multiple arguments are plenty.)

The one thing `+` will not do is mix types:

```python
age = 36
print("Age: " + age)
```

```
TypeError: can only concatenate str (not "int") to str
```

The fix is `str(age)`, which produces the string `"36"`:

```python
age = 36
print("Age: " + str(age))     # Age: 36
```

`str()`, `int()` and `float()` are **conversions** — they build a new value of the requested type. You will use `str()` today; all three get the full treatment tomorrow.

> **Gotcha:** `"36"` and `36` are not the same value and do not behave alike. `36 * 2` is `72`; `"36" * 2` is `"3636"`. Neither is wrong — but only one is what you meant, and Python will not ask which.

### 5.4 `bool` — `True` or `False`

Exactly two values, and the capital letters are part of the spelling.

```python
is_open = True
is_admin = False
print(is_open, is_admin)
print(5 > 3)              # comparisons produce bools
print(5 == 3)
```

```
True False
True
False
```

`true` (lowercase) is not a thing and produces a `NameError`. Booleans are what `if` statements consume, and they get their own day (Day 3).

### 5.5 `None` — the absence of a value

`None` is a single special value meaning "nothing here, deliberately".

```python
middle_name = None
print(middle_name)
print(type(None))
```

```
None
<class 'NoneType'>
```

`None` is not `0`, not `""`, and not `False` — those are all real values. `None` is the *lack* of one. It is how Python says "not set yet", "not found", "this function returns nothing useful". You will see it constantly, including in this common surprise:

```python
result = print("hi")      # print DISPLAYS text; it returns nothing
print(result)             # None
```

### 5.6 The five, at a glance

| Type | Means | Examples | Literal spelling |
|---|---|---|---|
| `int` | whole number | `0`, `-7`, `1_000_000` | digits, no point |
| `float` | decimal number | `3.14`, `-0.5`, `4.0`, `2e3` | digits with a point |
| `str` | text | `"hi"`, `''`, `"7"` | quotes |
| `bool` | truth value | `True`, `False` | capitalised words |
| `NoneType` | nothing | `None` | the word `None` |

---

## 6. `print`: showing values to a human

`print` writes text to the terminal. You have been using it since section 1; now learn its actual behaviour.

### 6.1 Several values in one call

Pass as many values as you like, separated by commas. Python inserts a single space between them and adds a newline at the end.

```python
name = "Ada"
age = 36
print("Name:", name, "Age:", age)
```

```
Name: Ada Age: 36
```

This is different from `+` in two important ways: the spaces come free, and **any type is accepted** — no `str()` needed, because `print` converts each argument for display itself.

```python
print("Total:", 3 + 4, "items", True, None)
```

```
Total: 7 items True None
```

### 6.2 `sep` — what goes between the values

```python
print("a", "b", "c")                 # a b c        (default sep is one space)
print("a", "b", "c", sep="")         # abc
print("a", "b", "c", sep=", ")       # a, b, c
print("2024", "03", "01", sep="-")   # 2024-03-01
print("one", "two", sep="\n")        # one, then two on the next line
```

```
a b c
abc
a, b, c
2024-03-01
one
two
```

### 6.3 `end` — what goes after the last value

The default is `"\n"`, which is why each `print` starts a new line. Override it to keep printing on the same line:

```python
print("Loading", end="")
print(".", end="")
print(".", end="")
print(".", end="")
print(" done")
```

```
Loading... done
```

One line of output from five calls. `sep` and `end` are **keyword arguments** — you must write the name (`sep=`, `end=`), because their position is not what identifies them. That machinery is Day 8; the usage is today.

```python
print("a", "b", sep=" | ", end=" <<\n")
```

```
a | b <<
```

> **Gotcha:** `print` is for humans. Do not build a program where one part `print`s a result and another part needs to use it — printing throws the value away after painting it on screen. Values that the program itself needs must be stored in variables (or, from Day 8, returned). "Printing is not returning" is one of the top three beginner misunderstandings in this course.

---

## 7. `input`: reading from a person

`input()` stops the program, waits for someone to type a line and press Enter, and hands you what they typed.

```python
name = input("What is your name? ")
print("Hello,", name)
```

A session:

```
What is your name? Ada
Hello, Ada
```

The string you pass to `input` is the prompt. Include a trailing space — `input("Name:")` puts the cursor hard against the colon and looks broken.

### 7.1 `input` always returns a string. Always.

This is the single most important sentence on the page.

```python
age = input("Age: ")
print(type(age))
print(age * 2)
```

```
Age: 36
<class 'str'>
3636
```

The user typed digits. Python handed you the **text** `"36"`, so `* 2` repeated the text. Nothing crashed — the answer is just wrong, which is worse.

Convert explicitly when you need a number:

```python
age_text = input("Age: ")      # "36" — a string
age = int(age_text)            # 36   — an int
print(age * 2)                 # 72
```

Or in one step, once the pattern is familiar:

```python
age = int(input("Age: "))
```

Read that from the inside out: `input(...)` runs first and produces text, then `int(...)` converts it. Nesting calls like this is normal Python; just be sure you can name what each layer produces.

`int()` refuses input that is not a whole number, loudly:

```python
int("abc")     # ValueError: invalid literal for int() with base 10: 'abc'
int("3.5")     # ValueError: invalid literal for int() with base 10: '3.5'
float("3.5")   # 3.5 — this is the right tool for decimals
```

For now, that crash is acceptable — you are the only user. Handling bad input gracefully needs `if` (Day 3) and `try` (Day 9).

> **Gotcha:** `input()` inside a script that you run automatically (a test, a scheduled job, a pipeline) will hang forever waiting for a human. That is why `examples.py` in every folder of this course never calls `input()`, and why you should keep input-reading in one obvious place near the top of a program.

---

## 8. `type()`: asking Python what something is

`type(value)` reports a value's type. It is a *diagnostic tool*, and using it early is a sign of competence, not confusion.

```python
print(type(42))          # <class 'int'>
print(type(3.14))        # <class 'float'>
print(type("hi"))        # <class 'str'>
print(type(True))        # <class 'bool'>
print(type(None))        # <class 'NoneType'>
print(type(print))       # <class 'builtin_function_or_method'>
```

The word `class` in the output just means "type" — Python's word for it, explained properly on Day 12.

For a cleaner label, ask for the type's name:

```python
value = 19.99
print(type(value).__name__)      # float
print("value is a", type(value).__name__)
```

```
float
value is a float
```

The double underscores mark a name Python itself defines (say it "dunder name"). You will meet many.

When something behaves oddly, `type()` is the first question to ask, not the last:

```python
quantity = input("How many? ")     # user types 3
print(type(quantity))              # <class 'str'>   <- there is your bug
```

Related and worth knowing today: `len(value)` gives the length of text, and `id(value)` gives the value's identity number in memory. `id` makes section 4.1 concrete:

```python
a = "shared"
b = a
print(id(a) == id(b))    # True — one string, two names
```

---

## 9. Comments

A comment is text for humans. Python ignores everything after a `#` on a line.

```python
# Rates set by the finance team, reviewed every April.
TAX_RATE = 0.2          # 20% standard rate

subtotal = 100
total = subtotal * (1 + TAX_RATE)
print(total)            # 120.0
```

Good comments explain **why**, because the code already says **what**:

```python
# Bad — restates the obvious, and now there are two things to keep in sync:
count = count + 1        # add one to count

# Good — explains a decision the code cannot express:
count = count + 1        # the header row is data too; the exporter omits it
```

Rules of thumb:
- Explain intent, constraints, units, and surprises. `# prices are in pence, not pounds` has saved more projects than any clever line of code.
- If code needs a paragraph of explanation, consider rewriting the code instead.
- `#` followed by one space, then the text. Inline comments sit two spaces after the code.
- Delete stale comments ruthlessly. A comment that contradicts the code is worse than no comment — the reader believes it.

Commenting out a line is how you disable it temporarily while debugging:

```python
print("step 1")
# print("step 2 — silenced while I check step 1")
print("step 3")
```

> **Gotcha:** a `#` inside a string is just a character, not a comment. `print("# not a comment")` prints `# not a comment`. Python only honours `#` outside quotes.

---

## 10. Naming: the rules and the conventions

Two separate things, and knowing which is which matters.

### 10.1 The rules (break these and Python refuses)

A name may contain letters, digits and underscores; it may not *start* with a digit; and it may not be one of Python's ~35 reserved keywords.

```python
user_name = "ok"
_private = "ok"
name2 = "ok"

2name = "no"        # SyntaxError: invalid decimal literal
user-name = "no"    # SyntaxError — a hyphen is a minus sign
class = "no"        # SyntaxError: invalid syntax  (class is a keyword)
```

Names are case-sensitive: `total`, `Total` and `TOTAL` are three different names, and mixing them up produces a `NameError` that reads as an insult.

The keyword list, for reference — you cannot use any of these as names:

```
False   None    True    and     as      assert  async   await
break   class   continue def    del     elif    else    except
finally for     from    global  if      import  in      is
lambda  nonlocal not    or      pass    raise   return  try
while   with    yield
```

You do not need to memorise it. You need to recognise that "invalid syntax" on an assignment often means you have collided with one.

### 10.2 The conventions (PEP 8)

**PEP 8** is Python's official style guide, and the community follows it closely enough that deviating marks your code as foreign. The relevant rules today:

| Kind of thing | Style | Example |
|---|---|---|
| variable | `lower_snake_case` | `user_name`, `total_price` |
| constant | `UPPER_SNAKE_CASE` | `TAX_RATE`, `MAX_RETRIES` |
| function | `lower_snake_case` | `word_count`, `is_valid` |
| class | `CapWords` | `ExpenseStore` (Day 12) |
| throwaway value | `_` | `_` |

**snake_case** means lowercase words joined by underscores. Not `userName` (that is camelCase, the Java and JavaScript convention), not `UserName`, not `username` when it is two words.

```python
# PEP 8:
words_per_minute = 250

# Works, but marks you as a visitor from another language:
wordsPerMinute = 250
WordsPerMinute = 250
```

A "constant" is a value you promise not to change, written in capitals as a message to other readers. Python does not enforce the promise; the convention is the whole mechanism.

Also from PEP 8, and worth adopting from your first file:
- Spaces around `=` in assignments: `x = 1`, not `x=1`. (No spaces for keyword arguments, though: `print("a", end="")`.)
- One space after each comma: `print("a", "b")`.
- Indent with **four spaces**, never tabs. This becomes load-bearing on Day 3, where indentation is syntax rather than decoration.
- Lines under about 88 characters.

Practical naming advice that goes beyond PEP 8:

```python
# Say what it is, not what type it is:
user_list = [...]        # meh
users = [...]            # better

# Booleans read as questions with is_/has_/can_:
is_active = True
has_permission = False

# Don't abbreviate to save four keystrokes:
usr_nm_str = "ada"       # no
user_name = "ada"        # yes

# Never shadow a builtin — you break the tool for the rest of the file:
list = [1, 2, 3]         # now list("abc") raises TypeError
type = "admin"           # now type(x) raises TypeError
```

That last point deserves the emphasis. `list`, `dict`, `str`, `int`, `sum`, `type`, `id`, `input`, `print`, `len`, `max`, `min` are all existing tools. Assigning to one replaces it, quietly, until the moment you try to use it and get `TypeError: 'str' object is not callable`. If you want the word anyway, add a trailing underscore: `type_`, `list_`.

> **Gotcha:** name length should scale with scope. `i` is fine as a loop counter on three lines; a value used across sixty lines needs a name that survives the journey.

---

## 11. Reading your first error messages

Errors are not punishment. They are the most detailed, most specific feedback you will ever get about your code — free, instant, and pointing at a line number. The skill is not avoiding them; it is reading them.

**Always read the last line first.** It names the error type and the problem. Then read the line number. Then, and only then, look at your code.

### 11.1 `SyntaxError` — Python cannot understand the text

Raised *before* the program runs, so nothing executes. Something is wrong with the grammar: a missing bracket, a missing quote, a missing colon.

```python
print("hello"
```

```
  File "demo.py", line 1
    print("hello"
         ^
SyntaxError: '(' was never closed
```

```python
print("hello)
```

```
  File "demo.py", line 1
    print("hello)
          ^
SyntaxError: unterminated string literal (detected at line 1)
```

Missing colon (you meet `if` on Day 3, but the error shape is universal):

```python
if x > 5
    print("big")
```

```
  File "demo.py", line 1
    if x > 5
            ^
SyntaxError: expected ':'
```

A confusing one, worth pre-empting:

```python
print("a" "b")     # fine — adjacent strings are joined: prints ab
print("a", "b")    # fine — two arguments: prints a b
print("a" + "b")   # fine — explicit join: prints ab
print("a" "b" +)   # SyntaxError: invalid syntax
```

Diagnostic habits for `SyntaxError`:
- The caret `^` shows where Python **lost the thread**, which is usually just after the real mistake. An unclosed bracket on line 12 is often reported on line 13 or later, because Python kept hoping.
- Therefore: **check the line above the one reported.** Especially for brackets and quotes.
- Count your brackets. Editors highlight matching pairs; use that.
- `SyntaxError: invalid syntax` with no detail usually means a keyword used as a name (`class = 5`), a missing operator, or `=` where `==` belongs.

### 11.2 `NameError` — Python understood you, but that name does not exist

Raised *while running*, at the exact line that tried to read the name.

```python
print("starting")
print(totl)
```

```
starting
Traceback (most recent call last):
  File "demo.py", line 2, in <module>
    print(totl)
          ^^^^
NameError: name 'totl' is not defined
```

Anatomy of that traceback, since you will read thousands:
- `Traceback (most recent call last)` — a header; ignore it.
- `File "demo.py", line 2, in <module>` — where. `<module>` means "at the top level of the file", not inside a function.
- `print(totl)` with carets under the culprit — Python shows you the offending expression.
- `NameError: name 'totl' is not defined` — the diagnosis.

The four causes, in order of frequency:

1. **A typo.** `totl` for `total`. Python 3.11+ often suggests the fix: `Did you mean: 'total'?`
2. **Wrong case.** `Total` when you defined `total`.
3. **Used before assigned.** Reading a name on line 5 that you bind on line 9. Remember: top to bottom.
4. **Forgotten quotes.** `print(hello)` looks for a variable named `hello`; you meant `print("hello")`.

```python
name = "Ada"
print(Name)      # NameError: name 'Name' is not defined. Did you mean: 'name'?
```

### 11.3 Two more you will meet within the hour

`TypeError` — the right name, the wrong type of value:

```python
print("Age: " + 36)
```

```
TypeError: can only concatenate str (not "int") to str
```

`ValueError` — the right type, but a value the operation cannot use:

```python
int("abc")
```

```
ValueError: invalid literal for int() with base 10: 'abc'
```

That pair is worth learning as a contrast: `TypeError` means *wrong kind of thing*, `ValueError` means *right kind of thing, unusable content*. `int("abc")` is a `ValueError` because `"abc"` is a perfectly good string — it just is not a number. Day 9 covers exceptions properly; `reference/error_messages.md` in this repository is a lookup table you should skim now and return to often.

### 11.4 The debugging loop for today

When something breaks, in this order:

1. Read the **last line** of the error. It says what went wrong.
2. Read the **line number**. If it is a `SyntaxError`, also look at the line above.
3. Look at that line, and **only** that line, first.
4. Print the values involved: `print(type(quantity), repr(quantity))`. Half of all early bugs are visible immediately from a type.
5. Change one thing. Re-run. Not three things — one.

`repr(value)` shows a value as you would type it, which is how you catch invisible problems:

```python
answer = "42 "                 # trailing space from a paste
print(answer)                  # 42     <- looks fine
print(repr(answer))            # '42 '  <- there it is
print(len(answer))             # 3
```

> **Gotcha:** do not "fix" errors by changing things at random until they stop. That produces code that works for reasons you cannot name, which is indistinguishable from code that is about to break. Understand the message, then make the smallest change that addresses it.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Expecting `input()` to give a number | `"3" * 2` is `"33"`; comparisons behave oddly | `int(input(...))` or `float(input(...))` |
| `"Age: " + 36` | `TypeError: can only concatenate str (not "int") to str` | `"Age: " + str(36)`, or `print("Age:", 36)` |
| Typo in a name | `NameError: name 'totl' is not defined` | Read the suggestion; check spelling and case |
| Using a name before binding it | `NameError` on a line above the assignment | Move the assignment earlier — files run top to bottom |
| Unclosed bracket or quote | `SyntaxError: '(' was never closed` | Check the reported line **and the one above** |
| `true` / `false` | `NameError: name 'true' is not defined` | `True` / `False`, capitalised |
| Writing `2 + 2` in a script and seeing nothing | no output at all | Scripts do not auto-display; use `print` |
| Expecting `print` to return a value | `x = print("hi")` then `x` is `None` | `print` displays; store the value in a variable instead |
| `=` where `==` belongs | `SyntaxError: invalid syntax` (or a silent rebinding) | `=` assigns, `==` compares (Day 3) |
| Shadowing a builtin (`list = [...]`) | `TypeError: 'list' object is not callable` | Rename to `items`, or `list_` |
| Mixing tabs and spaces | `TabError: inconsistent use of tabs and spaces` | Four spaces, always; set your editor to insert spaces |
| camelCase names | nothing breaks; reviewers wince | `snake_case` (PEP 8) |
| Trusting `0.1 + 0.2 == 0.3` | `False` | Floats are approximate; Day 2 covers this |
| Reading the *first* line of a traceback | confusion | Read the **last** line first |

---

## Mental model

A program is a **recipe card read by an extremely fast, extremely literal cook**.

```
        your file (the recipe)                 python (the cook)
      +--------------------------+          +---------------------+
      | price = 250              |          | reads the whole     |
      | tax   = price * 0.2      |  ------> | card first: is this  |
      | print("Total:",          |          | even readable?      |
      |        price + tax)      |          |   no  -> SyntaxError |
      +--------------------------+          |   yes -> start      |
                                            +---------------------+
                                                      |
                        the kitchen (memory)           | one step at a time,
                    +--------------------------+       | top to bottom
                    |  price ------> 250       | <-----+
                    |  tax   ------> 50.0      |
                    +--------------------------+
                                 |
                                 v
                          the plate (screen)
                            Total: 300.0
```

- **Names are labels on jars**, not the jars themselves. `tax = price * 0.2` sticks a label on the result of a calculation. Re-labelling (`price = 300`) moves one label and disturbs nothing else.
- **The cook has no common sense.** Ask for salt when you meant sugar and you get salt, immediately, without comment.
- **The cook cannot skip ahead.** Referring to something you have not prepared yet gets you `NameError`, not initiative.
- **Types are what a thing is made of.** You can add two numbers, or glue two strings, but "glue a number onto a string" is not an operation the kitchen has — hence `TypeError`.
- **`print` is plating up.** It shows the result to the diner. Anything the *recipe* still needs must stay in a labelled jar.

---

## Practice

1. Run the demo and read every printed line against the code that produced it. Predict the output before you look:

   ```bash
   python course/week1/day01_getting_started/examples.py
   ```

2. Spend ten minutes in the REPL. Not optional — this is where types stop being abstract:

   ```bash
   python
   ```

   Try: `type(3)`, `type(3.0)`, `type("3")`, `3 == 3.0`, `"3" == 3`, `"ab" * 3`, `len("hello")`, `print("a", "b", sep="")`, `id("x")`. Then deliberately break things: type `2 +`, then `prnt("hi")`, then `"a" + 1`. Read each error. Getting comfortable causing errors on purpose is a real skill.

3. Open `course/week1/day01_getting_started/exercises.py` and work top to bottom — they escalate. Replace each `raise NotImplementedError(...)` with your implementation. The docstring examples are what the tests check.

4. Grade yourself from the course root:

   ```bash
   python check.py day01
   python check.py day01 -v      # full failure detail
   ```

5. Write a throwaway script of your own, `me.py`: ask for a name, a city and a birth year with `input()`, then print a three-line summary. Make it crash on purpose by feeding a letter to `int()`, and read the traceback. Then compare your file with `solutions.py`.

---

## Recall check

1. What is the difference between a `SyntaxError` and a `NameError`, and what does each tell you about how much of your program ran?
2. `count = count + 1` is not a valid equation. Why is it a valid Python statement?
3. What type does `input()` return when the user types `42`, and what goes wrong if you forget?
4. Why does `print("Age: " + 36)` fail while `print("Age:", 36)` works?
5. What is the difference between `4` and `4.0`, and are they equal?
6. What does `None` mean, and how is it different from `0` and `""`?
7. Give the output of each: `print("a", "b", "c", sep="-")` and `print("x", end="!")` followed by `print("y")`.
8. Why is `list = [1, 2, 3]` a bad idea even though Python allows it?

<details>
<summary>Answers</summary>

1. A `SyntaxError` means Python could not parse the file, so **nothing ran** — no output at all appears. A `NameError` happens while running, at the line that referenced a name that does not exist, so any output before that line **did** appear and everything after it did not. Whether earlier output appeared is your first diagnostic.
2. Because `=` is not a claim of equality; it is an instruction. Python evaluates the right-hand side first using the current value of `count`, then rebinds the name `count` to the result. Read it as "count gets count plus one".
3. A `str` — the text `"42"`. Forget, and arithmetic silently misbehaves (`"42" * 2` is `"4242"`) or `TypeError`s (`"42" + 1`), and comparisons like `"42" > 40` raise `TypeError`. Convert with `int(...)` or `float(...)`.
4. `+` on a string demands another string; there is no defined way to concatenate an `int`, so you get `TypeError: can only concatenate str (not "int") to str`. `print` accepts any number of arguments of any type and converts each one for display itself, inserting a space between them.
5. `4` is an `int`, `4.0` is a `float` — different types, stored differently. They are equal in value: `4 == 4.0` is `True`, while `type(4) == type(4.0)` is `False`.
6. `None` is the deliberate absence of a value — "not set", "not found", "returns nothing useful". `0` is a number and `""` is a string; both are real values. A function with no return value gives you `None`.
7. `a-b-c` on one line; then `x!y` on one line (the `end="!"` replaces the newline, so `print("y")` continues the same line).
8. It replaces the builtin `list` tool for the rest of that scope, so a later `list("abc")` raises `TypeError: 'list' object is not callable`. The failure appears far from the cause. Use `items`, or `list_` if you really want the word.

</details>
