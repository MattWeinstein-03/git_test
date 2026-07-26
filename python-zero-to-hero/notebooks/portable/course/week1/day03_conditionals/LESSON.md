# Day 03 — Conditionals

> **Time:** ~4 hours  |  **Prerequisites:** Days 01–02

## What you'll be able to do after today
- Treat `True` and `False` as ordinary values: store them, print them, and build them out of comparisons.
- Combine conditions with `and`, `or` and `not`, and explain what short-circuiting stops from happening.
- Write `if` / `elif` / `else` chains where the branch order is deliberate rather than accidental.
- Explain why Python uses indentation as *syntax*, and fix `IndentationError` and `TabError` without guessing.
- Predict whether any value is truthy or falsy, and use that to write shorter, clearer conditions.
- Use chained comparisons (`0 <= x <= 100`) and conditional expressions (`"yes" if flag else "no"`) where they genuinely help.
- Say exactly when `is` is correct and when it is a bug waiting to surface, and never confuse `=` with `==` again.

## Why this matters

So far every program you have written does the same thing every time. That is not software; that is a calculation. A program becomes useful the moment it can respond to its input: reject the invalid form, charge the child rate, retry the failed request, warn when the disk is nearly full.

Conditionals are also where the *wrong* code starts running silently. An arithmetic bug usually crashes; a logic bug just quietly does the wrong thing for one category of user, forever, until somebody complains. Getting `and`/`or` precedence right, getting branch order right, and knowing which values are falsy are the difference between code that works and code that appears to work.

---

## 1. Booleans are values

`True` and `False` are values, exactly like `42` and `"hi"`. They are of type `bool`, they can be stored in variables, printed, and passed around.

```python
is_open = True
is_admin = False
print(is_open, type(is_open))     # True <class 'bool'>
```

Beginners tend to think of `True` as something that only lives inside an `if`. It does not. A comparison *produces* a boolean, and you can capture it:

```python
age = 20
is_adult = age >= 18       # a comparison produces a bool
print(is_adult)            # True
print(type(is_adult))      # <class 'bool'>
```

That line is worth staring at. `age >= 18` is not a question being asked of the `if` statement; it is an expression that evaluates to `True`, and `is_adult` is now bound to it. `if` merely consumes such a value.

Booleans are also secretly integers — `bool` is a subclass of `int`:

```python
print(True + True)      # 2
print(False + 10)       # 10
print(int(True))        # 1
print(True == 1)        # True
```

This is occasionally useful (counting `True`s by summing them, Day 5) and mostly a curiosity. What matters today: the two words are capitalised. `true` is a `NameError`.

---

## 2. Comparison operators

Six of them. Each produces a `bool`.

```python
print(5 == 5)      # True   equal to
print(5 != 3)      # True   not equal to
print(5 > 3)       # True   greater than
print(5 < 3)       # False  less than
print(5 >= 5)      # True   greater than or equal
print(5 <= 4)      # False  less than or equal
```

They work on strings too, comparing character by character using each character's numeric code:

```python
print("apple" < "banana")     # True    a comes before b
print("Zoo" < "apple")        # True    capital letters sort before lowercase!
print("abc" == "ABC")         # False
print("abc" == "abc")         # True
```

`"Zoo" < "apple"` is `True` because every uppercase letter has a lower code than every lowercase letter. For case-insensitive comparison, normalise first:

```python
print("Zoo".lower() < "apple".lower())     # False — as a human would expect
```

And the trap from Day 2, restated because it bites here:

```python
print("10" > "9")       # False  — text comparison: "1" comes before "9"
print(10 > 9)           # True   — number comparison
print("10" == 10)       # False  — different types are never equal
```

Comparing genuinely incompatible types raises:

```python
print("10" > 9)         # TypeError: '>' not supported between 'str' and 'int'
```

Note the asymmetry: `==` between a `str` and an `int` is simply `False`, but `>` raises. Equality is always answerable ("are these the same value?" — no); ordering is not ("is text bigger than a number?" — meaningless).

> **Gotcha:** never compare floats with `==`. `0.1 + 0.2 == 0.3` is `False` (Day 2, section 3). Use `abs(a - b) < 1e-9`.

---

## 3. `and`, `or`, `not`

Three operators for combining conditions. Python spells them as English words, not `&&`, `||`, `!`.

```python
age = 25
has_ticket = True

print(age >= 18 and has_ticket)      # True   both must be true
print(age < 18 or has_ticket)        # True   at least one must be true
print(not has_ticket)                # False  flips it
```

The truth tables, which you should be able to reproduce from memory:

| `a` | `b` | `a and b` | `a or b` |
|---|---|---|---|
| `True` | `True` | `True` | `True` |
| `True` | `False` | `False` | `True` |
| `False` | `True` | `False` | `True` |
| `False` | `False` | `False` | `False` |

| `a` | `not a` |
|---|---|
| `True` | `False` |
| `False` | `True` |

### 3.1 Precedence: `not`, then `and`, then `or`

`and` binds tighter than `or`, just as `*` binds tighter than `+`:

```python
print(True or False and False)        # True  — it is True or (False and False)
print((True or False) and False)      # False — brackets change everything
```

This is a genuine source of production bugs. Consider a discount rule:

```python
is_member = False
age = 70
is_student = False

# Intended: (member or senior) and not student
print(is_member or age >= 65 and not is_student)     # True — but by luck
print((is_member or age >= 65) and not is_student)   # True — and on purpose
```

Both print `True` here, which is exactly what makes it dangerous: the buggy version agrees with the correct one on most inputs. Bracket every mixed `and`/`or` expression. Always. It costs two characters and removes a category of bug.

### 3.2 Short-circuiting

`and` and `or` stop evaluating as soon as the answer is known.

- `A and B` — if `A` is falsy, the answer is already settled, so `B` is **never evaluated**.
- `A or B` — if `A` is truthy, the answer is settled, so `B` is **never evaluated**.

This is not an optimisation detail; it is a tool you use deliberately to guard a dangerous operation:

```python
text = ""
# text[0] would raise IndexError on an empty string — but it never runs,
# because len(text) > 0 is False and `and` gives up immediately.
print(len(text) > 0 and text[0] == "a")     # False, no crash
```

Swap the order and it breaks:

```python
text = ""
print(text[0] == "a" and len(text) > 0)     # IndexError: string index out of range
```

**Order your conditions so the cheap, protective test comes first.** The same idea with `or`, providing a fallback:

```python
name = ""
display = name or "anonymous"      # "" is falsy, so we get the fallback
print(display)                     # anonymous

name = "Ada"
print(name or "anonymous")         # Ada
```

Which brings up something that surprises people: `and` and `or` do not return `True`/`False`. They return **one of their operands**.

```python
print(1 and 2)          # 2      both truthy -> the last one
print(0 and 2)          # 0      first falsy -> the first one, immediately
print("" or "default")  # default
print("a" or "b")       # a
print(None or 0)        # 0      both falsy -> the last one
```

`x or default` is a genuine idiom for "use x unless it is empty". It has one trap: it treats `0` and `""` as "missing". If `0` is a legitimate value, use an explicit `is None` check instead (section 10).

> **Gotcha:** `if x == 1 or 2:` does not mean what it looks like. Python reads it as `(x == 1) or 2`, and `2` is truthy, so the whole thing is *always* true. Write `if x == 1 or x == 2:` or (Day 5) `if x in (1, 2):`.

---

## 4. `if`, `elif`, `else`

```python
temperature = 30

if temperature > 25:
    print("hot")
elif temperature > 15:
    print("mild")
else:
    print("cold")
```

Prints `hot`.

The anatomy:

```
if     temperature > 25    :
^      ^                   ^
keyword  condition         colon starts the block
    print("hot")
    ^^^^ four spaces of indentation = "this is inside the if"
```

- `if` takes a condition and runs its block when the condition is truthy.
- `elif` (short for "else if") is checked **only if** every condition above it was false. You may have as many as you like.
- `else` runs when nothing above matched. At most one, and it takes no condition.
- Both `elif` and `else` are optional. `if` alone is fine.

### 4.1 Only the first match runs

This is the single most important behaviour of an `if`/`elif` chain, and the source of a classic bug:

```python
score = 95

if score > 50:
    print("pass")
elif score > 90:
    print("distinction")     # NEVER printed — 95 > 50 matched first
```

`elif` branches are checked in order, and the chain stops at the first hit. So **order your conditions from most specific to least specific**:

```python
score = 95

if score > 90:
    print("distinction")
elif score > 50:
    print("pass")
else:
    print("fail")
```

Compare with separate `if` statements, which are independent and can all run:

```python
score = 95

if score > 90:
    print("distinction")     # prints
if score > 50:
    print("pass")            # ALSO prints — these are two separate decisions
```

Choosing between "one chain" and "several ifs" is a real design decision: a chain means *exactly one* of these applies; separate `if`s mean *each of these is a separate question*.

### 4.2 Grading pattern

```python
score = 84

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(grade)      # B
```

Because the chain stops at the first match, `score >= 80` already implies "and not 90 or more". You never have to write `elif score >= 80 and score < 90:` — that redundancy is a sign you have not internalised how `elif` works.

### 4.3 Guard clauses

Handle the awkward cases first and get them out of the way:

```python
name = "  "

if not name.strip():
    result = "no name given"
else:
    result = f"Hello, {name.strip()}!"

print(result)
```

From Day 8 onwards, when you can `return` early, this style keeps the main logic un-nested and is what professional code looks like.

### 4.4 `pass`

An empty block is a `SyntaxError`. `pass` is the official "do nothing" placeholder:

```python
value = 5

if value > 10:
    pass          # TODO: handle the big case later
else:
    print("small")
```

---

## 5. Indentation is syntax, not style

In most languages, braces mark a block and indentation is cosmetic. In Python, **indentation is the syntax**. There are no braces. The amount of leading whitespace is what tells Python which statements belong to which block, and getting it wrong changes the meaning of the program or stops it running.

```python
if False:
    print("A")       # inside the if — skipped
    print("B")       # inside the if — skipped
print("C")           # outside the if — always runs
```

Output: just `C`.

Move one line by four spaces and the program behaves differently:

```python
if False:
    print("A")
print("B")           # now OUTSIDE: this runs
print("C")
```

Output: `B` then `C`. No error, no warning — a different program.

### 5.1 The rules

- **Four spaces per level.** This is PEP 8, and the whole ecosystem follows it.
- **Never use tabs.** Python 3 refuses to mix them with spaces. Configure your editor to insert spaces when you press Tab.
- **Be consistent inside a block.** Every statement in a block must have the same indentation.
- A `:` at the end of a line always means "an indented block follows".

### 5.2 The errors

```python
if True:
print("hi")
```

```
IndentationError: expected an indented block after 'if' statement on line 1
```

```python
if True:
    print("a")
        print("b")
```

```
IndentationError: unexpected indent
```

```python
if True:
    print("a")
   print("b")
```

```
IndentationError: unindent does not match any outer indentation level
```

And the one that will make you doubt your eyes, because the file *looks* perfect:

```
TabError: inconsistent use of tabs and spaces in indentation
```

One line is indented with a tab and its neighbours with spaces. They render identically and are different characters. Fix: turn on "show whitespace" in your editor, or re-indent the block by hand with spaces.

### 5.3 Why would a language do this?

Because in every other language you indent anyway — and then the indentation can *lie*:

```c
if (x > 5)
    printf("a\n");
    printf("b\n");     // looks nested, runs unconditionally. A real CVE class.
```

Python removes the possibility of the layout disagreeing with the logic. The cost is that whitespace becomes something you have to get right; the benefit is that what you see is what runs, in every Python file you will ever read.

> **Gotcha:** when you paste code from a web page, you frequently paste its indentation too, mixed with whatever your editor does. If a paste produces `IndentationError` or `TabError`, do not hunt for the invisible character — re-type the indentation of the affected lines.

---

## 6. Nesting, and how to avoid it

An `if` inside an `if` is a **nested** conditional.

```python
age = 20
has_ticket = True

if age >= 18:
    if has_ticket:
        print("come in")
    else:
        print("buy a ticket first")
else:
    print("too young")
```

Legal, and often the clearest thing when the outer condition really is a separate gate. But nesting deepens fast, and deep nesting is where bugs live — by three levels in, you have to hold three conditions in your head simultaneously.

Two ways to flatten. **Combine conditions with `and`:**

```python
age = 20
has_ticket = True

if age >= 18 and has_ticket:
    print("come in")
elif age >= 18:
    print("buy a ticket first")
else:
    print("too young")
```

**Or invert and exit early** (a guard clause; much stronger from Day 8 when you have `return`):

```python
age = 15

if age < 18:
    message = "too young"
elif not has_ticket:
    message = "buy a ticket first"
else:
    message = "come in"

print(message)
```

Rule of thumb: **two levels is normal, three is a smell, four means stop and restructure.** If you find yourself at four, either you are missing an `and`, or the inner part wants to be a function (Day 8).

---

## 7. Truthiness

`if` does not require a `bool`. It accepts **any** value and asks it a single question: "are you truthy?"

The falsy values — memorise this list, it is short and it is the whole rule:

| Falsy | Kind |
|---|---|
| `False` | the boolean |
| `None` | absence |
| `0`, `0.0`, `-0.0` | any zero number |
| `""` | the empty string |
| `[]` | the empty list (Day 5) |
| `()` | the empty tuple (Day 5) |
| `{}` | the empty dict (Day 6) |
| `set()` | the empty set (Day 6) |

**Everything else is truthy.** Every non-empty string, every non-zero number, every non-empty collection.

```python
print(bool(0), bool(1), bool(-1))          # False True True
print(bool(""), bool("a"), bool(" "))      # False True True
print(bool("0"), bool("False"))            # True True   <- non-empty strings!
print(bool([]), bool([0]))                 # False True  <- a list containing 0
print(bool(None))                          # False
```

Two of those deserve alarm bells:
- `"0"` is **truthy**. It is a one-character string. `if input("continue? "):` is true even when the user types `0`.
- `[0]` is **truthy**. It is a list with one item in it. The item's own falsiness is irrelevant.

The practical pattern — this is why truthiness exists:

```python
name = ""

if name:                        # idiomatic
    print(f"Hello, {name}")
else:
    print("Hello, stranger")

# All of these say the same thing, and the first is what Python programmers write:
if name: ...
if name != "": ...
if len(name) > 0: ...
if bool(name) == True: ...      # actively bad style
```

`if not items:` for "the collection is empty" is likewise the standard spelling from Day 5 onward.

### 7.1 When truthiness is the wrong tool

Truthiness collapses several distinct states into one. Sometimes that distinction matters:

```python
quantity = 0

if quantity:
    print("we have stock")
else:
    print("out of stock or unknown")     # cannot tell 0 from None!
```

If `0` and `None` mean different things — "we counted, there are none" versus "we never counted" — you must test explicitly:

```python
quantity = 0

if quantity is None:
    print("unknown")
elif quantity == 0:
    print("out of stock")
else:
    print("in stock")
```

Rule: use truthiness for "is there anything here?"; use an explicit comparison when you need to distinguish *kinds* of nothing.

> **Gotcha:** `if x == True:` is wrong twice. It is noise when `x` is a bool, and it is a bug when `x` is `1.0` or `"yes"` or `[1]` — all truthy, none equal to `True`. Write `if x:`.

---

## 8. Chained comparisons

Python lets you write the mathematical form directly:

```python
score = 85
print(0 <= score <= 100)          # True
```

This is not `(0 <= score) <= 100` (which would compare a bool to a number). Python treats it as `0 <= score and score <= 100`, and — the useful part — evaluates `score` only once.

```python
age = 25
print(18 <= age < 65)             # True    the standard "in range" test
print(1 <= 5 <= 10 <= 20)         # True    chains can be any length
print("a" <= "m" <= "z")          # True    works on strings too
```

Compare the readability:

```python
if 0 <= score <= 100:             # obviously a range check
if score >= 0 and score <= 100:   # correct, wordier
if 0 <= score and score <= 100:   # correct, and now you have to read twice
```

> **Gotcha:** do not chain in ways that read like English but mean something else. `if a == b == c:` genuinely means "all three equal", which is fine. But `if x != y != z:` does **not** mean "all three different" — it means `x != y and y != z`, so `x` and `z` may be equal. `1 != 2 != 1` is `True`.

---

## 9. Conditional expressions

Sometimes you want a *value* chosen by a condition, not two blocks of code. The conditional expression (other languages call it the ternary operator) does that in one line:

```python
age = 20
label = "adult" if age >= 18 else "minor"
print(label)          # adult
```

Read it in the order the words appear: **the value, the condition, the alternative.** `X if C else Y` means "X when C is true, otherwise Y".

The long form of the same thing:

```python
if age >= 18:
    label = "adult"
else:
    label = "minor"
```

Both are correct. Use the one-liner when the whole thing fits comfortably on one line and both outcomes are simple values:

```python
count = 1
print(f"{count} item{'s' if count != 1 else ''}")     # 1 item

total = 0
items = 0
average = total / items if items else 0.0             # guard against divide-by-zero
print(average)                                        # 0.0

status = "on" if True else "off"
```

The `else` is **not optional** — `x = 1 if flag` is a `SyntaxError`. An expression must always produce a value, so there must be a fallback.

Do not nest them. This is legal and unreadable:

```python
size = 5
label = "small" if size < 3 else "medium" if size < 10 else "large"
```

That wants to be an `if`/`elif`/`else` chain. The one-liner is for choosing between two simple things and nothing more.

> **Gotcha:** a conditional expression evaluates only the branch it needs, so `x / y if y else 0` is safe. But watch the precedence when you embed one in a bigger expression: `"a" + "b" if flag else "c"` is `("a" + "b") if flag else "c"`, not `"a" + ("b" if flag else "c")`. Bracket it.

---

## 10. `is` versus `==`

This distinction confuses people for months. Get it now, in five minutes, and be done with it.

- `==` asks: **do these two values look the same?** (Are they equal?)
- `is` asks: **are these two names pointing at the exact same object in memory?** (Are they identical?)

Remember Day 1's arrow model: names point at values. `==` compares what is at the ends of the arrows. `is` compares where the arrows point.

```python
a = [1, 2, 3]        # a list, from Day 5 — the clearest demonstration
b = [1, 2, 3]        # a SEPARATE list that happens to look the same
c = a                # the SAME list, second name

print(a == b)        # True   — same contents
print(a is b)        # False  — two different objects
print(a == c)        # True   — same contents (obviously: same object)
print(a is c)        # True   — literally the same object
print(id(a), id(b), id(c))    # a and c match; b differs
```

```
   a ------+
           v
        [1, 2, 3]        <- object 1
           ^
   c ------+

   b ---> [1, 2, 3]      <- object 2, equal but not identical
```

### 10.1 Use `is` for exactly three things

`is` is correct only for `None`, `True` and `False` — the three values Python guarantees are singletons (there is exactly one `None` object in the entire program):

```python
value = None
print(value is None)          # the correct, idiomatic check
print(value is not None)      # and its negation
```

That is the list. `x is None` for every other purpose, use `==`.

### 10.2 Why `is` on other values is a trap

Small integers and short strings are *cached* by CPython as an optimisation, so `is` sometimes appears to work:

```python
a = 256
b = 256
print(a is b)        # True — small ints are pre-made and shared

c = 257
d = 257
print(c is d)        # True in a script, False if you type the two lines
                     # separately in the REPL

e = int("257")       # the same number, computed rather than written down
print(e == 257)      # True  — always
print(e is 257)      # False — a different object with the same value
```

Three lines, three different answers, all about the number 257. `==` said `True` every time.

```python
x = "hi"
y = "hi"
print(x is y)        # True — short literals get interned

x = "hello world!"
y = "hello world!"
print(x == y)        # True  — always, and this is what you wanted
```

The exact behaviour depends on the Python version, how the code was compiled, and whether the values are literals in the same file. Code that relies on it is code that will break on a different machine for reasons nobody can reproduce.

> **Gotcha:** `if name is "Ada":` may work today, on your machine, in that file, and fail in production. Newer Pythons warn: `SyntaxWarning: "is" with a literal. Did you mean "=="?`. The rule is mechanical, so just follow it: **`is` for `None`/`True`/`False`, `==` for values.**

### 10.3 And `True`

Even for booleans, prefer plain truthiness:

```python
flag = True

if flag:                # best
if flag is True:        # correct but noisy
if flag == True:        # noisy and fragile (1 == True is also True)
```

---

## 11. `=` versus `==`

`=` **assigns**. `==` **compares**. Confusing them is the most common typo in programming, and Python is unusually good at protecting you from it.

```python
count = 5           # assignment: bind the name `count` to 5
print(count == 5)   # comparison: produces True
```

Get it wrong in a condition and Python refuses to run the file at all:

```python
count = 5
if count = 5:
    print("five")
```

```
  File "demo.py", line 2
    if count = 5:
       ^^^^^^^^^
SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
```

In C, `if (count = 5)` compiles, assigns 5 to `count`, and is always true — a bug that has caused real security failures. Python makes it a syntax error, and even suggests the fix. This is a language design decision in your favour: when you see that message, you know exactly what to change.

### 11.1 Footnote: the walrus operator

Python 3.8 added `:=`, the "walrus operator", which assigns *and* produces a value so it can be used inside a condition — `if (n := len(data)) > 10:` binds `n` and compares in one step. You do not need it this week, and using it before you are fluent with plain `if` makes code harder to read; it is mentioned here only so the symbol is not a mystery when you meet it.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `if x = 5:` | `SyntaxError: invalid syntax. Maybe you meant '=='` | `==` compares, `=` assigns |
| Broadest condition first in a chain | later `elif` branches never run | order most specific first |
| `if x == 1 or 2:` | always true | `if x == 1 or x == 2:` |
| Mixing `and`/`or` without brackets | wrong answer on some inputs only | bracket it: `(a or b) and c` |
| Forgetting the colon | `SyntaxError: expected ':'` | `if cond:` |
| No indentation after `if` | `IndentationError: expected an indented block` | indent four spaces |
| Mixed tabs and spaces | `TabError: inconsistent use of tabs and spaces` | spaces only, always |
| `if x == True:` | works, then breaks for `1.0`/`"y"`/`[1]` | `if x:` |
| `if x is "Ada":` | works sometimes, fails elsewhere | `==` for values, `is` for `None` |
| `x or default` when `0` is valid | `0` silently replaced by the default | `x if x is not None else default` |
| Truthiness where `0` differs from `None` | cannot distinguish "none" from "unknown" | `if x is None:` then `elif x == 0:` |
| `x != y != z` for "all different" | `1 != 2 != 1` is `True` | compare all three pairs |
| Comparing floats with `==` | `0.1 + 0.2 == 0.3` is `False` | `abs(a - b) < 1e-9` |
| `"10" > 9` | `TypeError: '>' not supported between 'str' and 'int'` | convert first |
| `if not x == y:` | works, reads badly | `if x != y:` |
| Nesting four levels deep | unreadable, untestable | combine with `and`, or use guard clauses |

---

## Mental model

An `if`/`elif`/`else` chain is a **row of sieves stacked in a funnel**. Each value is dropped in the top and falls through until something catches it — and once caught, it stops.

```
                     value falls in
                           |
                           v
        +------------------------------------+
   if   |  score >= 90 ?  ----- yes -----> "A"     caught: chain ENDS
        +------------------------------------+
                     | no
                     v
        +------------------------------------+
 elif   |  score >= 80 ?  ----- yes -----> "B"     caught: chain ENDS
        +------------------------------------+
                     | no
                     v
        +------------------------------------+
 elif   |  score >= 70 ?  ----- yes -----> "C"
        +------------------------------------+
                     | no
                     v
        +------------------------------------+
 else   |  the catch-all tray  ----------> "F"
        +------------------------------------+
```

- **Exactly one sieve catches.** That is why order matters: put the finest mesh at the top, or the coarse one takes everything.
- **Separate `if` statements are separate funnels.** The same value goes through all of them, and several can catch it.
- **The gate is truthiness, not equality.** Each sieve asks "are you truthy?", and `0`, `""`, `None` and the empty collections answer no.
- **`and` and `or` are wiring between sensors, with a shortcut.** Once the outcome is decided the rest of the wire is never energised — which is exactly why the cheap, protective test goes first.
- **`==` compares what is in the buckets; `is` asks whether it is the same bucket.** For `None`, there is only ever one bucket, which is why `is None` is the right question.

---

## Practice

1. Run the demo and read every line against the code that produced it:

   ```bash
   python course/week1/day03_conditionals/examples.py
   ```

2. REPL drills. Predict, then check:

   ```bash
   python
   ```

   Try: `bool("0")`, `bool([])`, `bool([0])`, `bool(" ")`, `True or False and False`, `0 and 1/0` (why no error?), `"" or "x"`, `1 == True`, `[] is []`, `None == False`, `1 != 2 != 1`, `0 <= 5 <= 3`, `"a" if 0 else "b"`. Each surprise is a gap worth closing now.

3. Open `course/week1/day03_conditionals/exercises.py` and work top to bottom. Watch your branch order in the grading and triangle exercises — that is where the marks are.

4. Grade yourself from the course root:

   ```bash
   python check.py day03
   python check.py day03 -v
   ```

5. Extra rep: write a script that asks for a number with `input()`, and reports whether it is negative, zero, or positive; whether it is even or odd; and whether it is between 1 and 100 inclusive. Use `isdigit()` to notice non-numeric input before you call `int()` — that is a conditional protecting a conversion, which is a pattern you will use forever.

---

## Recall check

1. What does `and` return when both operands are truthy? What does `or` return when the first is truthy?
2. Why does `0 and 1/0` not raise `ZeroDivisionError`?
3. List every falsy value in Python.
4. Why is `"0"` truthy? Why is `[0]` truthy?
5. What is wrong with this, and what does it print for `score = 95`?
   ```python
   if score > 50:
       print("pass")
   elif score > 90:
       print("distinction")
   ```
6. When is `is` the right operator, and why is `x is 257` unreliable?
7. Rewrite `if x == 1 or 2:` so that it does what its author intended.
8. What is the difference between `if a: ... if b: ...` and `if a: ... elif b: ...`?

<details>
<summary>Answers</summary>

1. `and` returns the **last** operand (`1 and 2` is `2`). `or` returns the **first** truthy operand (`"a" or "b"` is `"a"`). Neither necessarily returns a `bool` — they return one of the operands, which is what makes `name or "anonymous"` work.
2. Short-circuiting. `0` is falsy, so the result of `and` is already settled and the right-hand side is never evaluated. This is why the cheap protective test goes first: `len(t) > 0 and t[0] == "a"`.
3. `False`, `None`, `0`, `0.0`, `""`, `[]`, `()`, `{}`, `set()`. Everything else is truthy.
4. `"0"` is a string containing one character, and non-empty strings are truthy — the *content* is irrelevant. `[0]` is a list with one item in it, and non-empty lists are truthy — the item's own falsiness is irrelevant.
5. The conditions are in the wrong order. `95 > 50` matches first, so it prints `pass` and the `distinction` branch is unreachable for every score above 90. Put the most specific condition first.
6. `is` is right for `None`, `True` and `False` — values with exactly one instance in the program. `x is 257` is unreliable because CPython caches small integers (roughly -5 to 256) but not larger ones, so the answer depends on the version, the compiler and whether the values are literals in the same file. Use `==`.
7. `if x == 1 or x == 2:` — or, from Day 5, `if x in (1, 2):`. As written, Python evaluates `(x == 1) or 2`, and `2` is truthy, so the condition is always true.
8. Separate `if` statements are independent questions: both blocks can run. An `if`/`elif` chain is one decision: at most one block runs, and the first matching condition wins.

</details>
