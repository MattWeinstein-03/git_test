# Day 04 — Loops

> **Time:** ~4 hours  |  **Prerequisites:** Days 01–03

## What you'll be able to do after today
- Write a `while` loop with its three moving parts in place — setup, condition, change — and explain which missing part causes an infinite loop.
- Choose `for` or `while` on purpose, and say in one sentence why the other one was wrong for the job.
- Produce any run of numbers you need with `range` in all three of its forms, including counting backwards.
- Walk through a string one character at a time and accumulate a total, a count, a maximum, a flag or a new string as you go.
- Stop a loop early with `break`, skip one turn with `continue`, and use the loop `else` clause to answer "did it get all the way through?".
- Write a sentinel loop that keeps going until a stop value arrives.
- Nest one loop inside another to build a grid or a triangle of text, and predict how many times the inner body runs.
- Diagnose an off-by-one error from its symptom, and stop a runaway loop with Ctrl-C without panicking.

## Why this matters

Yesterday your programs could finally make a decision. They still cannot do a job of work, because every useful job involves *the same thing, many times*: every line in a file, every row in a report, every character in a name, every attempt until the user gets it right. Without loops your only option is copy-paste, and copy-paste means the tenth copy has a typo nobody notices for a year.

Loops are also the first place where your code can be *wrong in an interesting way*. A conditional either matches or it does not. A loop can run one time too few (and quietly drop the last item), one time too many (and crash on the item that is not there), or forever (and take the machine with it). Those three failures — the off-by-one, the boundary crash, the infinite loop — are the bread and butter of debugging for the rest of your career, and by the end of today you will recognise all three on sight.

Everything from here builds on this. Day 5's lists exist so you have something better to loop over; Day 6's counting patterns are today's accumulators with a nicer container; Day 15's comprehensions are a compressed `for` loop. Learn the long form properly now and the short forms will be obvious later.

---

## 1. The problem loops solve

Say you want to print the numbers 1 to 5. With Days 1–3 only, you write `print(1)` through `print(5)` — five lines, one per number. That works, and it is a dead end. Five is fine; five hundred is not; and "however many the user asks for" is impossible, because you cannot write a number of lines that depends on a value you have not seen yet.

A loop is one piece of code that runs repeatedly:

```python
for number in range(1, 6):
    print(number)
```

```
1
2
3
4
5
```

Two lines, and the shape does not change when the job grows. `range(1, 501)` prints five hundred numbers. `range(1, n + 1)` prints as many as the value of `n`, decided while the program is running.

Python has exactly two loops:

- **`while`** — repeat *as long as a condition holds*. You use it when you do not know in advance how many turns you need.
- **`for`** — repeat *once for each item in a sequence*. You use it when you do know, or when something can hand you the items one at a time.

Both are in this lesson, and section 5 is about choosing.

---

## 2. `while`

A `while` loop is an `if` that repeats. Same shape: keyword, condition, colon, indented block. The difference is what happens at the bottom of the block — instead of carrying on, execution jumps back up to the condition and asks again.

```python
count = 1
while count <= 3:
    print("count is", count)
    count += 1
print("done, count is now", count)
```

```
count is 1
count is 2
count is 3
done, count is now 4
```

Trace it by hand, because this is the mechanism:

| Check | `count` | Condition | Action |
|---|---|---|---|
| 1 | 1 | `1 <= 3` → True | print, `count` becomes 2 |
| 2 | 2 | `2 <= 3` → True | print, `count` becomes 3 |
| 3 | 3 | `3 <= 3` → True | print, `count` becomes 4 |
| 4 | 4 | `4 <= 3` → False | leave the loop |

Notice that the condition is checked *before* each turn, including the first. If it is false at the start, the body never runs at all:

```python
count = 10
while count < 5:
    print("never printed")
print("straight past it")
```

```
straight past it
```

### 2.1 The three moving parts

Every correct `while` loop has three things, and if you can name them you can debug any loop:

```python
total = 0          # 1. SETUP: something exists before the loop starts
n = 1
while n <= 4:      # 2. CONDITION: a test that will eventually become false
    total += n
    n += 1         # 3. CHANGE: something the condition depends on must move
print(total)       # 10   (1 + 2 + 3 + 4)
```

- **Setup** — the variables the condition and body use must exist *before* the `while` line. Forget this and you get `NameError`.
- **Condition** — evaluated fresh before every turn. It must be able to become false.
- **Change** — somewhere in the body, a variable the condition reads has to move towards making it false. This is the one people forget, and forgetting it is the infinite loop of section 13.

### 2.2 A loop that counts down

Nothing says the change has to be upwards:

```python
seconds = 3
while seconds > 0:
    print(seconds)
    seconds -= 1
print("Liftoff!")
```

```
3
2
1
Liftoff!
```

### 2.3 A loop whose length is not known in advance

This is what `while` is *for*. How many times do you have to halve 1000 before it drops below 1? You do not know, and you do not need to:

```python
value = 1000.0
halvings = 0
while value >= 1:
    value = value / 2
    halvings += 1
print(halvings, "halvings, ending at", value)
```

```
10 halvings, ending at 0.9765625
```

No `range` could have told you 10 in advance. The condition worked it out.

> **Gotcha:** the variable in the condition and the variable you change must be the *same* variable. `while n < 5:` with `count += 1` in the body is an infinite loop, and it looks completely reasonable at a glance. When a loop hangs, the first thing to check is whether the thing you are changing is the thing you are testing.

---

## 3. `for`: doing something once per item

A `for` loop takes something that can be walked through — Python calls that an **iterable** — and runs its body once per item, binding each item to a variable you name.

```
for  <name>  in  <iterable>  :
     ^           ^
     the loop variable        something that yields items one at a time
```

A string is an iterable of its characters, which makes it the perfect first thing to loop over:

```python
for letter in "cat":
    print(letter)
```

```
c
a
t
```

The loop variable (`letter` here) is an ordinary variable. You choose the name, it is re-bound on every turn, and it survives after the loop still holding the final value — `print(letter)` after that loop shows `t`. That is occasionally useful and mostly a trap; do not rely on it.

### 3.1 Why `for` is safer than `while`

Compare these two, which do the same thing:

```python
word = "cat"

# for: the iterable decides when to stop
for letter in word:
    print(letter, end=" ")
print()

# while: you decide when to stop, and you can get it wrong
i = 0
while i < len(word):
    print(word[i], end=" ")
    i += 1
print()
```

```
c a t 
c a t 
```

The `while` version has four opportunities for error: the starting value, the comparison operator, the bound, and the increment. Write `<=` instead of `<` and you get `IndexError`. Forget `i += 1` and it never ends. The `for` version has none of those opportunities, because it does not count — it consumes.

**Rule: if you are walking through the items of something, use `for`.** Reach for `while` only when there is no sequence to walk.

### 3.2 Counting characters

Combine `for` with Day 3's `if` and you can already answer real questions:

```python
text = "hello world"
vowels = 0
for character in text:
    if character in "aeiou":
        vowels += 1
print(vowels)      # 3
```

Read that as: start at zero; for each character, if it is one of the vowels, add one. `character in "aeiou"` is Day 2's substring test doing duty as a membership test.

### 3.3 `for` over a string, one word at a time

Not yet — splitting text into words hands you a *list*, and lists are tomorrow. Today, "one character at a time" is the tool you have, and it is enough to count, total, search and build.

> **Gotcha:** `for letter in word:` gives you the *character*, not its position. If you need to know where you are, you need `range(len(word))` (section 4.3) — or Day 5's `enumerate`, which is the right answer and arrives tomorrow.

---

## 4. `range`

`range` produces a run of whole numbers. It has three forms, and they are the same three as string slicing, which is not a coincidence: stop, then start-stop, then start-stop-step.

### 4.1 One argument: `range(stop)`

Starts at 0, stops *before* `stop`:

```python
for i in range(5):
    print(i, end=" ")
print()
```

```
0 1 2 3 4 
```

Five numbers, and `5` is not one of them. `range(5)` means "five values, counting from zero" — the same half-open convention as `text[0:5]`, for the same reason: `range(n)` always produces exactly `n` values.

```python
for i in range(0):
    print("never printed")
print("range(0) produces nothing at all")
```

### 4.2 Two arguments: `range(start, stop)`

```python
for i in range(2, 6):
    print(i, end=" ")
print()
```

```
2 3 4 5 
```

`start` is included, `stop` is excluded. The count is `stop - start` — `range(2, 6)` gives 4 values.

This is where the `+ 1` idiom comes from. To count 1 to 10 *inclusive*, you must ask for a stop of 11:

```python
total = 0
for i in range(1, 11):
    total += i
print(total)      # 55
```

`range(1, 10)` would have stopped at 9 and given 45. Getting used to writing `n + 1` when you mean "up to and including n" is most of section 12.

### 4.3 Three arguments: `range(start, stop, step)`

```python
for i in range(0, 10, 2):
    print(i, end=" ")
print()
```

```
0 2 4 6 8 
```

`step` can be negative, which is how you count down:

```python
for i in range(5, 0, -1):
    print(i, end=" ")
print()
```

```
5 4 3 2 1 
```

Read `range(5, 0, -1)` as "start at 5, walk down, stop before 0". The `stop` is still excluded, which is why the last value is 1 and not 0. To include 0, stop at `-1`:

```python
for i in range(5, -1, -1):
    print(i, end=" ")
print()
```

```
5 4 3 2 1 0 
```

A step of the wrong sign gives you nothing — no error, just an empty run. Both `range(5, 0)` (start above stop, stepping up) and `range(0, 5, -1)` (stepping down towards a stop that is above the start) produce zero values, so the loop body never runs. An empty loop that silently does nothing is a real bug and a quiet one: if a loop produces no output, print the range's endpoints and check their order.

A step of zero would be a run with no end, so Python refuses it:

```python
range(0, 5, 0)
```

```
ValueError: range() arg 3 must not be zero
```

### 4.4 `range` is not a list

Printing a `range` does not show you numbers:

```python
print(range(5))          # range(0, 5)
print(len(range(5)))     # 5
print(type(range(5)))    # <class 'range'>
```

A `range` is a *recipe* for producing numbers, not a stored run of them. It remembers three integers — start, stop, step — and works out each value when asked. That is why `range(1_000_000_000)` is instant and uses no memory: nothing has been produced yet.

To see the numbers you must consume them, which today means looping:

```python
shown = ""
for i in range(5):
    shown += str(i) + " "
print(shown)             # 0 1 2 3 4
```

(Tomorrow, `list(range(5))` shows them in one step. That is a list, so it waits for Day 5.)

### 4.5 `range(len(text))` — when you need the position

Sometimes the position matters as much as the character: reporting where a match was found, or comparing a character with the one before it. `range(len(text))` produces exactly the valid indexes:

```python
word = "cat"
for i in range(len(word)):
    print(i, word[i])
```

```
0 c
1 a
2 t
```

`len(word)` is 3, so `range(3)` gives `0 1 2` — which are precisely the legal indexes, because the last valid index is `len - 1` (Day 2, section 5). The half-open convention did that work for you: `range(len(x))` is *never* off by one, which is a good reason to write it that way rather than `range(0, len(word) - 1 + 1)`.

Use this form only when you genuinely need `i`. `for letter in word:` is clearer when you do not.

> **Gotcha:** `range` takes whole numbers only. `range(2.5)` raises `TypeError: 'float' object cannot be interpreted as an integer`, and so does `range(len(word) / 2)` — because `/` always gives a float (Day 2, section 1.1). Use `//` for the halfway point: `range(len(word) // 2)`.

---

## 5. Choosing between `while` and `for`

| Situation | Use | Why |
|---|---|---|
| Once per character of a string | `for` | the string knows how many there are |
| A fixed number of turns | `for` with `range` | the count is known up front |
| Counting up, down, or in steps | `for` with `range` | `range` does the arithmetic |
| Until the user types "quit" | `while` | nobody knows how many turns that is |
| Until a value converges or drops below a threshold | `while` | the data decides |
| Retry until it works, up to 3 attempts | `while` | two exit conditions at once |
| Walk a list (tomorrow) | `for` | same reason as a string |

The heuristic in one line: **if you can name the collection, use `for`; if you can only name the stopping condition, use `while`.**

A useful sanity check on your own code: a `while` loop whose body ends in `i += 1` and whose condition is `i < len(something)` is a `for` loop that has been written the long way. Convert it.

---

## 6. Accumulator patterns

This section is the practical heart of the day. An **accumulator** is a variable that lives *outside* the loop, starts at a deliberate value, and is updated *inside* the loop. When the loop ends, the accumulator holds the answer.

The shape never changes:

```
1. set the accumulator to its starting value      (before the loop)
2. for each item:  update the accumulator         (inside the loop)
3. use the accumulator                            (after the loop)
```

The whole skill is choosing the right starting value. Get that wrong and the loop is correct but the answer is not.

### 6.1 Running total: start at 0

```python
total = 0
for i in range(1, 6):
    total += i
print(total)      # 15
```

Zero is the right start because adding zero changes nothing — it is the "nothing yet" value for addition. It is also the correct answer when the loop runs zero times, which is why an empty run gives `0` rather than crashing.

For a product, the "nothing yet" value is `1`, not `0`:

```python
product = 1
for i in range(1, 6):
    product *= i
print(product)    # 120   (1*2*3*4*5)
```

Start a product at 0 and the answer is 0 forever. That is the single most common accumulator bug.

### 6.2 Counter: start at 0, add 1 conditionally

A counter is a total that adds `1` when a test passes, instead of adding the item:

```python
text = "Mississippi"
letter_count = 0
for character in text:
    if character == "s":
        letter_count += 1
print(letter_count)     # 4
```

The `if` inside the `for` is the workhorse combination of Days 3 and 4. Almost every real loop has one.

### 6.3 Max-so-far and min-so-far

To find the largest thing, hold the best candidate seen so far and replace it whenever you meet something better:

```python
digits = "38207"
largest = 0                      # the smallest possible digit
for character in digits:
    value = int(character)
    if value > largest:
        largest = value
print(largest)      # 8
```

The starting value needs thought. `0` works here only because no digit is below 0. When you cannot rule anything out, start from the first item instead — `largest = int(digits[0])` — and let the loop compare the rest. That version still works when every value is negative, where starting at `0` would wrongly answer `0`. It does assume there *is* a first item, so a real function guards the empty case with an `if` first (Day 3, section 4.3).

Minimum is the same with the comparison flipped and the starting value inverted.

> **Gotcha:** do not name your accumulator `max` or `min`. Those are built-in functions, and rebinding the name breaks them for the rest of the file — a confusing `TypeError: 'int' object is not callable` several lines later. `largest`, `best`, `highest`: fine.

### 6.4 Found-flag: start at False

When the question is "is there one?", accumulate a boolean:

```python
text = "hello world"
found_z = False
for character in text:
    if character == "z":
        found_z = True
print(found_z)      # False
```

Start at `False` — "I have not seen one yet" — and only ever set it to `True`. Never set it back to `False` inside the loop; that turns "was there ever one?" into "was the last one one?", which is a different question and almost never the one you meant.

Once the flag is `True` there is nothing left to learn, so this pattern usually wants `break` (section 7).

### 6.5 Building a string

You have no lists today, so a string is your accumulator when the answer is text. Start with `""` — the "nothing yet" value for concatenation:

```python
word = "python"
reversed_word = ""
for character in word:
    reversed_word = character + reversed_word    # each new character goes in FRONT
print(reversed_word)      # nohtyp
```

Read the update line carefully; the order is the entire trick. `reversed_word + character` would have built `"python"` unchanged.

Filtering into a new string is the same shape:

```python
raw = "a1b2c3"
digits_only = ""
for character in raw:
    if character.isdigit():
        digits_only += character
print(digits_only)        # 123
```

**Separators.** Joining with a separator has one wrinkle: you want the separator *between* items, not after every one. The trick is to add it only when the accumulator is not empty — which is Day 3's truthiness doing useful work:

```python
result = ""
for i in range(1, 4):
    if result:                 # truthy means "there is already something here"
        result += ", "
    result += str(i)
print(result)      # 1, 2, 3
```

The naive version — `result += str(i) + ", "` — leaves `'1, 2, 3, '` with a trailing comma and space, which you then have to slice off with `result[:-2]`. Both are legitimate; adding the separator first is cleaner. Tomorrow `", ".join(...)` does the whole job in one call — that is why `join` exists.

> **Gotcha:** `+=` on a string builds a brand-new string every time, because strings are immutable (Day 2, section 7). For a handful of pieces that is irrelevant. For a hundred thousand it is genuinely slow, and the answer is to collect the pieces in a list and `join` them once (Day 5). Know the limit exists; do not worry about it this week.

### 6.6 The four patterns side by side

| Question | Accumulator | Start | Update |
|---|---|---|---|
| What is the total? | number | `0` | `total += value` |
| What is the product? | number | `1` | `product *= value` |
| How many match? | number | `0` | `count += 1` inside an `if` |
| What is the largest? | number | first item | `if value > best: best = value` |
| Is there one? | bool | `False` | `found = True` inside an `if` |
| What does the text become? | string | `""` | `out += piece` |

---

## 7. `break`

`break` leaves the loop immediately. Not the current turn — the whole loop. Execution continues at the first line after the loop body.

```python
for character in "hello world":
    if character == " ":
        break
    print(character, end="")
print()
print("stopped at the first space")
```

```
hello
stopped at the first space
```

The characters after the space are never looked at. That is the point: `break` is how you say "I have what I came for".

It is the natural partner to the found-flag:

```python
text = "hello world"
target = "o"
position = -1                      # -1 means "not found", as Day 2's find() does
for i in range(len(text)):
    if text[i] == target:
        position = i
        break                      # first match only; stop looking
print(position)      # 4
```

Without the `break`, `position` would end up as `7` — the *last* match rather than the first. `break` is not only an optimisation here; it changes the answer.

`break` also gives a `while True:` loop its exit, which is a deliberate and common idiom:

```python
n = 1
while True:                # no condition of its own
    n *= 2
    if n > 100:
        break              # ...so the exit must be inside
print(n)      # 128
```

Use `while True` when the natural exit test belongs in the middle or at the end of the body rather than at the top. Just make sure the `break` is reachable — `while True` with no `break` is an infinite loop by construction.

> **Gotcha:** `break` only leaves *one* loop — the innermost one it sits in. In nested loops (section 11), a `break` in the inner loop returns you to the outer loop, which carries on to its next turn. Breaking out of both needs a flag, or (from Day 8) a `return`.

---

## 8. `continue`

`continue` abandons the *current turn* and jumps straight to the top of the loop for the next one. The loop keeps going.

```python
for i in range(1, 8):
    if i % 2 == 0:
        continue          # skip the even numbers
    print(i, end=" ")
print()
```

```
1 3 5 7 
```

`continue` is for skipping input you do not care about, and it earns its keep when the alternative is wrapping the whole body in an `if`:

```python
raw = "12a34"
total = 0
for character in raw:
    if not character.isdigit():
        continue          # not a digit: nothing to do this turn
    total += int(character)
print(total)      # 10
```

The same loop with the condition inverted — `if character.isdigit(): total += int(character)` — gives the identical `10`. With a one-line body, that version is clearer. With a fifteen-line body and three things to skip, `continue` keeps the real work at one level of indentation instead of four. Prefer whichever reads better, and know that `continue` is the tool for "reject early, then get on with it".

> **Gotcha:** `continue` in a `while` loop skips the rest of the body — *including* the line that changes the loop variable, if that line is at the bottom. This is a classic hang:
>
> ```python
> i = 0
> while i < 5:
>     if i == 2:
>         continue      # i is never incremented again: infinite loop
>     print(i)
>     i += 1
> ```
>
> Increment *before* the `continue`, or use a `for` loop, where the advance is not your responsibility.

---

## 9. The loop `else` clause

Both loops can take an `else`. It is rare, it is genuinely useful, and its name is misleading — so learn it as a phrase:

> **`else` runs when the loop finished without ever hitting `break`.**

Read it as "no break", not as "otherwise".

```python
number = 91
divisor = 2
while divisor * divisor <= number:
    if number % divisor == 0:
        print(number, "is divisible by", divisor)
        break
    divisor += 1
else:
    print(number, "is prime")
```

```
91 is divisible by 7
```

Change `number` to `97` and the loop runs out of divisors without breaking, so the `else` fires:

```
97 is prime
```

The same with a `for`:

```python
text = "hello"
for character in text:
    if character.isdigit():
        print("found a digit:", character)
        break
else:
    print("no digits in", text)
```

```
no digits in hello
```

Without `else` you would need a found-flag (`found = False` before, `found = True` and `break` inside) and an `if not found:` after the loop — three extra lines saying the same thing. `for`/`else` is the search idiom: `break` means "found it", `else` means "searched everything and it was not there".

> **Gotcha:** the `else` belongs to the *loop*, not to the `if` inside it, and the indentation is the only thing that tells them apart — `else` lines up with `for` or `while`. Also note it still runs when the loop body never executed at all: an empty range means zero turns, zero `break`s, so the `else` fires. If that would be wrong for your case, test for the empty case first.

---

## 10. Sentinel loops

A **sentinel** is a special value that means "stop". Sentinel loops are the classic use of `while`: keep processing until the stop value shows up, however long that takes.

The real version reads from `input()`:

```python
# Illustration only — examples.py cannot call input(), because it must run
# unattended. Type this one into the REPL yourself.
total = 0
while True:
    reply = input("amount (or 'done'): ")
    if reply == "done":            # the sentinel
        break
    total += int(reply)
print("total:", total)
```

The shape is: loop forever, fetch the next thing, test it against the sentinel, `break` if it matches, otherwise process it.

You can practise the same shape without a keyboard by walking a string whose sentinel is a character. Here `#` means "end of data":

```python
data = "4,2,9#7,7,7"       # everything after the # is someone else's problem
total = 0
for character in data:
    if character == "#":
        break                       # the sentinel: stop reading
    if character.isdigit():
        total += int(character)
print(total)      # 15   (4+2+9, and nothing after the #)
```

A sentinel in a `while` loop with an index, so you can see both halves of the pattern:

```python
data = "abc.def"
i = 0
before_dot = ""
while i < len(data) and data[i] != ".":     # two exit conditions
    before_dot += data[i]
    i += 1
print(before_dot)      # abc
```

Two things to notice in that condition. First, both exits are checked every turn: run out of characters, or meet the sentinel. Second, the order matters — `i < len(data)` has to come first so that short-circuiting (Day 3, section 3.2) prevents `data[i]` from being evaluated when `i` has run off the end. Swap them and you get `IndexError` on any string without a dot. Yesterday's short-circuit rule is not trivia; it is load-bearing in loops.

> **Gotcha:** pick a sentinel that cannot be real data. `0` is a terrible sentinel for "sum these numbers" because 0 is a plausible amount; `""` is a poor sentinel for text that may legitimately be blank. `"done"`, `"quit"` and `-1`-for-a-count are conventional because they are outside the range of valid values.

---

## 11. Nested loops

A loop inside a loop. The inner loop runs *completely*, from start to finish, on every single turn of the outer loop.

```python
for row in range(3):
    for column in range(2):
        print(row, column)
```

```
0 0
0 1
1 0
1 1
2 0
2 1
```

Three outer turns times two inner turns is six lines. **Multiply the counts** to know how many times the innermost body runs — that is the whole mental model, and it is also the performance warning: a nested loop over 1,000 items each is a million turns.

### 11.1 A rectangle of text

`print()` moves to a new line by default; `print(..., end="")` does not. Use `end=""` in the inner loop to stay on one line, then a bare `print()` after it to finish the row.

```python
for row in range(3):
    for column in range(5):
        print("*", end="")
    print()          # end the row
```

```
*****
*****
*****
```

### 11.2 A triangle

Make the inner count depend on the outer variable and the shape stops being rectangular:

```python
for row in range(1, 5):
    for column in range(row):
        print("*", end="")
    print()
```

```
*
**
***
****
```

Row 1 prints one star, row 2 prints two. `range(row)` produces `row` values, so the inner count *is* the row number. Once you see that the inner bound can be an expression, every text shape is available:

```python
size = 4
for row in range(1, size + 1):
    spaces = size - row
    print(" " * spaces + "*" * row)
```

```
   *
  **
 ***
****
```

That last one does not even need the inner loop — `"*" * row` (Day 2's string repetition) does the inner loop's job in one operation. When the inner loop only concatenates a constant, prefer the multiplication; it is shorter and impossible to get off by one.

### 11.3 Building a grid as a string

Returning text is more useful than printing it — a caller can test it, log it or wrap it. Accumulate into a string, ending each row with `"\n"`:

```python
grid = ""
for row in range(3):
    for column in range(3):
        grid += "#"
    grid += "\n"
print(repr(grid))          # '###\n###\n###\n'
print(grid, end="")
```

```
###
###
###
```

If you want no trailing newline — usually the tidier choice — add the `"\n"` *before* each row except the first, using the truthiness trick from section 6.5: `if grid: grid += "\n"` at the top of the outer loop gives `'###\n###\n###'` instead.

### 11.4 A times table

Nested loops plus Day 2's format specs give you an aligned table:

```python
for row in range(1, 4):
    line = ""
    for column in range(1, 4):
        line += f"{row * column:>4}"
    print(line)
```

```
   1   2   3
   2   4   6
   3   6   9
```

`:>4` right-aligns each number in four characters, so the columns line up without counting spaces.

> **Gotcha:** reusing the same variable name for both loops (`for i ... for i ...`) does not raise an error and will waste your afternoon. The inner loop overwrites the outer's variable, so the outer loop resumes with the wrong value. Name them for what they are: `row` and `column`, `outer` and `inner`, `word` and `letter`.

---

## 12. Off-by-one errors

The most common loop bug in every language: the loop runs one time too many, or one time too few. Python's half-open conventions remove most of the arithmetic, but you still have to decide whether the endpoint is included.

### 12.1 The four shapes

Want the numbers **1 to 10 inclusive**? Only one of these is right:

| You write | You get | Comment |
|---|---|---|
| `range(1, 10)` | 1…9 | one too few — the classic |
| `range(1, 11)` | 1…10 | correct |
| `range(10)` | 0…9 | ten values, but starting from 0 |
| `range(1, 11, 1)` | 1…10 | correct, and the `1` step is noise |

### 12.2 The index version

```python
word = "cat"
i = 0
while i < len(word):       # `<` is correct
    print(word[i], end=" ")
    i += 1
print()
```

Change `<` to `<=` and you get:

```
c a t
IndexError: string index out of range
```

because `word[3]` does not exist — the last valid index is `len(word) - 1`. The rule to hold on to: **`< len(x)` is right, `<= len(x)` is wrong, and `<= len(x) - 1` is right but no one writes it.**

### 12.3 The symptoms, and what they mean

| Symptom | Likely cause |
|---|---|
| `IndexError` on the last turn | `<=` where `<` was meant, or `len(x)` where `len(x) - 1` was meant |
| The last item is silently missing | `range(1, n)` where `range(1, n + 1)` was meant |
| One extra blank/zero at the end | the loop ran once too many times over an empty or missing value |
| The loop body never runs | `start` and `stop` are the wrong way round for the step |
| The answer is out by exactly one item's worth | the accumulator started at the wrong value, not the loop |

### 12.4 How to find one in ten seconds

Do not stare at the code. Run the loop with a length of 0, 1 and 2 and see whether the answers are right. Nearly every off-by-one shows up at 0 or 1, where "one too many" and "one too few" are the difference between an answer, an empty answer and a crash.

Or print the loop variable on every turn with `print(f"{i=}")` — Day 2's `=` specifier, which labels the value with its own name. It is the fastest loop debugger you have until Day 9's `pdb`.

> **Gotcha:** "fencepost" problems are off-by-one's twin. Ten fence panels need eleven posts; three items joined by commas need two commas; a range from 3 to 7 spans four steps but touches five numbers. When something is *between* the items rather than *on* them, count it separately and expect the number to differ by one.

---

## 13. Infinite loops, and how to stop one

An infinite loop is a loop whose condition never becomes false. Your program stops responding, your terminal fills up or freezes, and the fan starts.

**To stop it: press Ctrl-C** (hold Control, press C) in the terminal where it is running. That sends a keyboard interrupt, and Python stops with a traceback ending in `KeyboardInterrupt`:

```
^CTraceback (most recent call last):
  File "loop.py", line 3, in <module>
    count += 1
KeyboardInterrupt
```

That is not a crash you caused by writing bad syntax — it is you, deliberately interrupting. Note the file and line in the traceback: they tell you where the loop was spinning, which is usually enough to find the bug. If a loop is printing so fast you cannot read anything, Ctrl-C first and then look.

On the rare occasion Ctrl-C does not take, close the terminal window (or `Ctrl-\`, or kill the process from another terminal). You will not damage anything.

### 13.1 The four ways to write one

**Forgot to change the variable:**

```python
count = 0
while count < 5:
    print(count)        # prints 0 forever
    # count += 1        <- the missing line
```

**Changed the wrong variable** — `while i < 5:` with `j += 1` in the body. `j` moves, `i` does not, and the code looks entirely reasonable.

**A condition that can never be false** — `while count > 0:` with `count += 1` inside. The change is real but it moves *away* from the exit.

**`while True` with no reachable `break`** — the exit has to exist, and it has to be somewhere the code can actually get to.

And a fifth, subtler one: a `continue` that jumps over the increment (section 8's gotcha).

### 13.2 Deliberate infinite loops

`while True` is not a bug by itself — it is the standard shape for a server, an event loop or a menu, where the exit is a `break` or a `return` somewhere inside. The rule is that the exit must exist and must be reachable, and it should be obvious to a reader where it is.

### 13.3 The safety belt

When a loop's stopping condition depends on data you do not fully trust, add a maximum turn count so a bug becomes a wrong answer instead of a hang:

```python
value = 27
steps = 0
while value != 1 and steps < 1000:     # the second test is the safety belt
    if value % 2 == 0:
        value = value // 2
    else:
        value = value * 3 + 1
    steps += 1
print(steps)      # 111
```

That loop is the Collatz sequence, and nobody has proved it always terminates. The `steps < 1000` guard means that if it does not, you get an answer you can inspect rather than a frozen terminal.

> **Gotcha:** an infinite loop that prints on every turn can produce gigabytes of output in seconds and make the terminal itself unresponsive, which is worse than a silent hang. When you are unsure about a loop, either print nothing inside it or add a counter guard before you run it.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| No change to the loop variable | the program hangs; Ctrl-C shows the line | add `count += 1` (or use `for`) |
| Testing `i` but incrementing `j` | hangs, and looks completely reasonable | test and change the same variable |
| `continue` before the increment in a `while` | hangs on one specific value | increment first, or use `for` |
| `while i <= len(text):` | `IndexError: string index out of range` | `<` not `<=` |
| `range(1, n)` for "1 to n" | last item silently missing | `range(1, n + 1)` |
| `range(5, 0)` to count down | the loop body never runs | `range(5, 0, -1)` |
| `range(len(x) / 2)` | `TypeError: 'float' object cannot be interpreted as an integer` | `//` not `/` |
| Product accumulator starting at 0 | answer is always 0 | start a product at `1` |
| Max accumulator starting at 0 with negative data | answer is wrongly `0` | start from the first item |
| Setting a found-flag back to `False` in the loop | reports the *last* match, not *any* match | only ever set it `True` |
| Accumulator declared inside the loop | it resets every turn; answer is the last item | declare it before the loop |
| `print` inside the loop when the answer is wanted after it | output for each turn, no total | print after the loop |
| Forgetting `break` after finding a match | you get the last match, not the first | `break` when done |
| Expecting `break` to leave both nested loops | the outer loop carries on | use a flag, or Day 8's `return` |
| Reusing `i` for inner and outer loops | wrong results, no error | name them `row` and `column` |
| Thinking `range(5)` includes 5 | one too few, every time | `stop` is excluded |
| `print(range(5))` to see the numbers | `range(0, 5)` | loop over it (or Day 5's `list()`) |
| Missing colon or indentation after `for` | `SyntaxError` / `IndentationError` | `for x in y:` then indent 4 |
| Mutating the thing you are looping over | skipped or repeated items | Day 5 material; loop over a copy |

---

## Mental model

A `for` loop is a **conveyor belt with a worker beside it**. The belt carries the items past, one at a time; the worker does the same thing to each one; a tally board on the wall is the only thing that remembers anything between items.

```
                    the accumulator lives OUTSIDE the loop
                            +-------------+
                            | total =  15 |   <- the tally board
                            +-------------+
                                  ^
                                  | updated once per item
                                  |
   range(1,6) ->  [1] [2] [3] [4] [5]  ->  belt runs out -> loop ends
                       ^
                   the worker: the indented body,
                   run once per item, same code every time

   break     = stop the belt right now and walk away
   continue  = let this one go past untouched, wait for the next
   else      = the speech you give only if the belt ran out on its own
               (never given if you walked away early)
```

A `while` loop is the same worker, but **there is no belt** — instead there is a question painted on the wall, asked before every single item: *"still true?"*. The worker keeps going until the answer is no. If nothing inside the loop can change that answer, the worker never stops, and Ctrl-C is you walking over and switching the machine off.

Three ideas worth keeping:

- **The accumulator is outside; the work is inside.** Anything you declare inside the loop is reborn every turn and remembers nothing. This one distinction explains most "why is my total always the last value?" bugs.
- **The starting value is a decision, not a formality.** `0` for a sum, `1` for a product, `""` for text, `False` for "have I seen one?", the first item for a maximum. It is also the answer you get when the belt is empty — so pick a starting value that would be *correct* for no items at all.
- **Half-open ranges make the arithmetic disappear.** `range(n)` gives `n` values; `range(len(x))` gives exactly the valid indexes; `range(a, b)` gives `b - a` values. Trust the convention instead of adding and subtracting ones, and off-by-one errors mostly stop happening.

---

## Practice

1. Run the demo and read every line of output against the code that produced it:

   ```bash
   python course/week1/day04_loops/examples.py
   ```

2. Fifteen minutes in the REPL. Predict before you press Enter:

   ```bash
   python
   ```

   Try: `len(range(5))`, `print(range(5))`, `range(5, 0)` in a `for` loop, `range(5, 0, -1)`, `for c in "hi": print(c)`, a `while` loop that counts down from 3, `for i in range(3): pass` then `print(i)`, and a `for`/`else` search for a digit in `"abc"` and in `"ab3"`. Then deliberately write an infinite loop — `while True: pass` — and practise Ctrl-C on it, so that the first time you meet one by accident you already know what to do. (`while True: pass` prints nothing, which makes it a safe one to practise on.)

3. By hand, on paper, no computer: trace `for row in range(1, 4): for col in range(row): print(row, col)` and write down every line it prints, in order. Then run it. If your paper and the machine disagree, find out which of you is wrong before reading on.

4. Open `course/week1/day04_loops/exercises.py` and work top to bottom. Every one of them is an accumulator with a different starting value; if you are stuck, the first question to ask is "what should the answer be for empty input?", and the second is "what starting value gives that answer?".

5. Grade yourself from the course root:

   ```bash
   python check.py day04
   python check.py day04 -v
   ```

6. Extra rep: print a 9x9 multiplication table with aligned columns and a header row. Then print a diamond of stars of a given odd height. Then write a loop that finds the first number above 1000 that is divisible by both 17 and 23. All three are Day 1–4 tools only.

---

## Recall check

1. What are the three moving parts of a correct `while` loop, and which one is missing when the loop hangs?
2. How many values does `range(2, 10, 3)` produce, and what are they?
3. What is the difference between `break` and `continue`?
4. When does a loop's `else` clause run — and when does it not?
5. Why does `for i in range(5, 0):` print nothing, and how do you count down from 5 to 1?
6. You are multiplying numbers together in a loop. What should the accumulator start at, and what happens if you start it at 0?
7. Given `word = "cat"`, why is `while i <= len(word):` wrong, and what does it raise?
8. How do you stop a program that is stuck in an infinite loop, and what do you look at afterwards?

<details>
<summary>Answers</summary>

1. **Setup** (the variables exist before the loop), **condition** (a test that can become false), and **change** (something in the body moves a variable the condition reads). When a loop hangs it is almost always the change: either it is missing, or it is applied to a different variable than the one the condition tests, or a `continue` is jumping over it.
2. Three values: `2`, `5`, `8`. It starts at 2, steps by 3, and stops *before* 10 — so 11 is never reached and 8 is the last one.
3. `break` leaves the loop entirely and continues at the first line after it. `continue` abandons only the current turn and goes back to the top of the loop for the next one. `break` reduces the number of turns to zero; `continue` skips work inside one turn.
4. It runs when the loop finished **without hitting `break`** — including when the loop body never ran at all, because zero turns means zero breaks. It does not run if the loop was left by `break`. Read it as "no break", not "otherwise".
5. Because the default step is `+1`, and you cannot walk upwards from 5 and reach anything below 5, so the range is empty — no error, no output. Count down with `range(5, 0, -1)`, which gives `5 4 3 2 1`; use `range(5, -1, -1)` if you want 0 as well.
6. Start it at `1`, the value that changes nothing under multiplication. Starting at 0 makes every product 0, because `0 * anything` is 0 — and the loop will look perfectly correct while returning the wrong answer.
7. Because the valid indexes of a 3-character string are 0, 1 and 2 — `len(word) - 1` is the last one. `i <= len(word)` lets `i` reach 3 and `word[3]` raises `IndexError: string index out of range`. Use `i < len(word)`, or better, `for character in word:`.
8. Press **Ctrl-C** in the terminal running it; Python stops with a `KeyboardInterrupt` traceback. Afterwards, read the file and line number in that traceback — it points at the line the loop was spinning on — then check the three moving parts: is a variable changing, is it the one the condition tests, and can the condition ever be false?

</details>
