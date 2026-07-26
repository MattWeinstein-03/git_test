# Day 05 — Lists and Tuples

> **Time:** ~4 hours  |  **Prerequisites:** Day 04

## What you'll be able to do after today
- Build a list, then read any single item, any run of items, or every n-th item out of it with indexing and slicing — counting from the left or from the right.
- Name every list method you will use this week, say what it gives back, and explain why `scores = scores.sort()` destroys your data.
- Choose between `sort` and `sorted` deliberately, and sort by something other than the value itself using `key=` and a named function.
- Walk a list with `enumerate` when you need positions, and walk two lists side by side with `zip`.
- Summarise a list with `len`, `sum`, `min`, `max`, `any` and `all`, and test membership with `in`.
- Store rows inside a list to make a grid, and read and write a single cell of it.
- Say what a tuple is, why immutability is a feature rather than a restriction, and unpack one into separate names — including the two-name swap.
- Predict what happens to `a` when you write `b = a` and then change `b`, and copy a list correctly when you did not want that to happen.

## Why this matters

Everything you have stored so far has needed its own name. Three scores means three variables. A hundred scores means you stop, because `score_1` through `score_100` is not a program, it is a punishment.

A list holds any number of values under one name, in order, and lets you reach them by position. That single idea turns Day 04's loops from a curiosity into the engine of real work: read a file into a list of lines, filter it, sort it, total it, report on it. Every table, every queue of jobs, every set of search results, every row of a CSV arrives in your program as a list.

The second half of today is the part that bites people six months in. Lists are **mutable** — unlike the strings of Day 02, a list can be changed in place — and two names can point at the same list. When they do, changing one changes "both", because there was only ever one list. This is not a curiosity either. Mysteriously-changing data is one of the most common bugs in professional Python, and by the end of today you will know exactly what causes it and the three one-line fixes.

---

## 1. Why you need a list

Here is the problem, written out honestly:

```python
score_1 = 88
score_2 = 92
score_3 = 79

total = score_1 + score_2 + score_3
print("Average:", total / 3)          # Average: 86.33333333333333
```

Now add a fourth score. You must edit the assignment, edit the total, and edit the divisor — three places for one change. Now imagine the scores come from a file and you do not know how many there will be until the program runs. There is no number of variables you can write in advance that is correct.

A list fixes all of it:

```python
scores = [88, 92, 79]
print("Average:", sum(scores) / len(scores))    # Average: 86.33333333333333

scores.append(95)                                # a fourth score arrives
print("Average:", sum(scores) / len(scores))     # Average: 88.5
```

The code that computes the average did not change. It does not care how many scores there are. That property — code whose shape is independent of the size of the data — is what makes programs able to handle real workloads, and a list is the first place you meet it.

---

## 2. Making a list

Square brackets, values separated by commas.

```python
numbers = [1, 2, 3]
names = ["Ada", "Grace", "Alan"]
mixed = [1, "two", 3.0, True, None]
empty = []

print(numbers)              # [1, 2, 3]
print(names)                # ['Ada', 'Grace', 'Alan']
print(mixed)                # [1, 'two', 3.0, True, None]
print(empty)                # []
print(len(numbers))         # 3
print(len(empty))           # 0
print(type(numbers).__name__)   # list
```

Four things worth noticing straight away:

- **Order is kept.** `[1, 2, 3]` is not the same list as `[3, 2, 1]`. Whatever order you put things in is the order you get them back in.
- **Duplicates are allowed.** `[1, 1, 1]` is a perfectly good three-item list.
- **A list can hold anything**, including a mixture of types. In practice you should keep a list to one kind of thing — a list of scores, a list of names — because code that has to cope with "either a number or a string, who knows" is code full of special cases.
- **`print` shows a list with brackets and quotes.** That is `repr` at work (Day 02, section 4.3): `['Ada']` tells you it is a list of one string, while a bare `Ada` would not.

### 2.1 The other ways to make one

```python
print(list("hello"))              # ['h', 'e', 'l', 'l', 'o']   any sequence -> list
print(list(range(5)))             # [0, 1, 2, 3, 4]             range -> list
print("a,b,c".split(","))         # ['a', 'b', 'c']             split gives a list
print([0] * 5)                    # [0, 0, 0, 0, 0]             repetition
print([1, 2] + [3, 4])            # [1, 2, 3, 4]                concatenation
```

`list(range(5))` is worth a pause. On Day 04 you used `range` to drive a loop; `range` is not a list, it is a recipe for producing numbers one at a time. `list()` runs the recipe to completion and collects the results. `print(range(5))` shows `range(0, 5)`, not the numbers, for exactly that reason.

`[0] * 5` is the standard way to make a list of a known size filled with a starting value — a row of five zeros, ten empty strings, whatever you need. Section 13.2 shows the one place it goes badly wrong.

### 2.2 Building a list with a loop

The accumulator pattern from Day 04, with a list as the accumulator:

```python
squares = []                      # start empty
for number in range(1, 6):        # 1, 2, 3, 4, 5
    squares.append(number * number)
print(squares)                    # [1, 4, 9, 16, 25]
```

Three lines, and it is the shape of a thousand programs you will write: **empty list, loop, append**. Learn it as one movement.

> **Forward reference:** Python has a one-line shorthand for "build a list from another list", called a *comprehension*. It is genuinely useful and it is Day 15. Writing the loop out longhand first is not a waste — it is the thing the shorthand is short *for*, and you cannot read the shorthand fluently until the longhand is automatic.

---

## 3. Indexing

A list is an ordered sequence, exactly like a string, and it is indexed exactly like a string: positions count from **0**.

```python
names = ["Ada", "Grace", "Alan", "Edsger"]
print(names[0])         # Ada
print(names[1])         # Grace
print(names[3])         # Edsger
print(len(names))       # 4
print(names[4])         # IndexError: list index out of range
```

```
   "Ada"  "Grace"  "Alan"  "Edsger"
  +------+-------+-------+--------+
  |   0  |   1   |   2   |    3   |     <- index from the left
  |  -4  |  -3   |  -2   |   -1   |     <- index from the right
  +------+-------+-------+--------+
```

The last valid index is `len(names) - 1`. Asking for `names[len(names)]` is the classic off-by-one and it raises `IndexError` every time.

### 3.1 Negative indexing

Negative indexes count from the right, starting at `-1`:

```python
names = ["Ada", "Grace", "Alan", "Edsger"]
print(names[-1])        # Edsger    the last one
print(names[-2])        # Alan      second from the end
print(names[-4])        # Ada       same as names[0]
print(names[-5])        # IndexError
```

`names[-1]` is how you get the last item, and it is one of the highest-value four characters in the language. Compare:

```python
print(names[len(names) - 1])    # Edsger   correct, and noise
print(names[-1])                # Edsger   correct, and obvious
```

There is no `-0`, because `-0` is `0`, which already means "the first item". So the right-hand end starts at `-1`.

### 3.2 Indexing with a variable

The index does not have to be a literal. Anything that evaluates to a whole number works, which is what makes loops and lists fit together:

```python
names = ["Ada", "Grace", "Alan"]
position = 1
print(names[position])          # Grace
print(names[position + 1])      # Alan

for index in range(len(names)):
    print(index, names[index])
```

```
0 Ada
1 Grace
2 Alan
```

That loop works, and you should recognise it, but it is not how you write it. Section 9 replaces it with `enumerate`.

> **Gotcha:** `names[1.0]` raises `TypeError: list indices must be integers or slices, not float`, even though `1.0` is numerically a whole number. This bites after division, because `/` always produces a float: `names[len(names) / 2]` is a `TypeError`, and `names[len(names) // 2]` is the middle item. Floor division exists for exactly this.

---

## 4. Slicing

Indexing gives you one item. **Slicing** gives you a new list containing several. Same three-part syntax as Day 02's strings, same rules:

```
items[start:stop:step]
```

- `start` — first index included (default: 0)
- `stop` — first index **excluded** (default: past the end)
- `step` — how far to jump each time (default: 1)

```python
letters = ["a", "b", "c", "d", "e", "f"]
print(letters[1:3])       # ['b', 'c']                indexes 1 and 2, NOT 3
print(letters[:3])        # ['a', 'b', 'c']           from the start
print(letters[3:])        # ['d', 'e', 'f']           to the end
print(letters[:])         # ['a','b','c','d','e','f'] a full copy
print(letters[::2])       # ['a', 'c', 'e']           every second item
print(letters[1::2])      # ['b', 'd', 'f']           every second, from index 1
print(letters[::-1])      # ['f','e','d','c','b','a'] reversed
print(letters[-2:])       # ['e', 'f']                the last two
print(letters[:-2])       # ['a','b','c','d']         all but the last two
print(letters[2:5:2])     # ['c', 'e']                all three parts at once
```

Because `stop` is excluded, `len(items[a:b])` is exactly `b - a`, and `items[:n] + items[n:]` rebuilds the original for any `n`. Cut at a boundary, lose nothing.

### 4.1 A slice is always a new list

This is the sentence to remember. Indexing a list gives you the item that is in it; slicing a list gives you **a brand-new list** containing the same items.

```python
original = ["a", "b", "c"]
piece = original[0:2]
piece.append("NEW")
print(piece)        # ['a', 'b', 'NEW']
print(original)     # ['a', 'b', 'c']       untouched
```

That property is what makes `items[:]` a copying idiom, and section 13 is built on it.

### 4.2 Slices clip, indexes raise

```python
letters = ["a", "b", "c", "d"]
print(letters[1:100])     # ['b', 'c', 'd']   no error, clipped at the end
print(letters[100:])      # []                empty list, no error
print(letters[3:1])       # []                start after stop -> empty
print(letters[100])       # IndexError
```

An out-of-range index shouts. An out-of-range slice hands you an empty list and says nothing. A silent `[]` where you expected data is a bug that will not announce itself, so when a slice comes back empty and you did not expect it, suspect your numbers.

### 4.3 Assigning to a slice

Unlike a string, a list lets you assign *through* a slice, replacing a run of items:

```python
letters = ["a", "b", "c", "d"]
letters[1:3] = ["X", "Y"]
print(letters)              # ['a', 'X', 'Y', 'd']

letters[1:3] = ["Z"]        # the replacement can be a different length
print(letters)              # ['a', 'Z', 'd']

letters[1:1] = ["p", "q"]   # an empty slice inserts without deleting
print(letters)              # ['a', 'p', 'q', 'Z', 'd']
```

You will not need this often — `insert`, `append` and `extend` are clearer for most jobs — but seeing it makes the point that a list is genuinely changeable, and that is the next section.

> **Gotcha:** `letters[1:3] = "XY"` does something surprising: the right-hand side is treated as a sequence of items, and a string is a sequence of characters, so you get `['a', 'X', 'Y', 'd']` — which happens to look right here, but `letters[1:3] = "hello"` splices in five separate letters. Assign a list to a slice, not a string.

---

## 5. Lists are mutable

Day 02 established that a string cannot be changed:

```python
word = "python"
word[0] = "P"           # TypeError: 'str' object does not support item assignment
```

A list can:

```python
scores = [88, 92, 79]
scores[0] = 100
print(scores)           # [100, 92, 79]
```

No new list was made. The list that `scores` refers to was **modified in place**. This is the deepest difference between the types you have met so far, and it is worth stating as a table:

| Type | Mutable? | Changing it means |
|---|---|---|
| `int`, `float`, `bool`, `None` | no | make a new value, rebind the name |
| `str` | no | make a new string, rebind the name |
| `tuple` (section 12) | no | make a new tuple, rebind the name |
| `list` | **yes** | the object itself changes; every name pointing at it sees the change |
| `dict`, `set` (Day 06) | **yes** | same |

Mutability is why lists are efficient for building data up piece by piece — appending to a list does not copy the list — and it is why section 13 exists. Both halves of that sentence matter.

---

## 6. List methods, and what each one gives back

A method is a function attached to a value, called with a dot. Lists have eleven you will use regularly. The single most important column in the table below is the middle one.

| Method | Returns | Changes the list? |
|---|---|---|
| `append(x)` | `None` | yes — adds one item at the end |
| `extend(other)` | `None` | yes — adds every item of `other` |
| `insert(i, x)` | `None` | yes — inserts before index `i` |
| `pop()` / `pop(i)` | **the removed item** | yes |
| `remove(x)` | `None` | yes — deletes the first `x` |
| `index(x)` | **an int** | no |
| `count(x)` | **an int** | no |
| `sort()` | `None` | yes — reorders in place |
| `reverse()` | `None` | yes — reorders in place |
| `clear()` | `None` | yes — empties it |
| `copy()` | **a new list** | no |

Read that column again. Eight of the eleven return `None`. That is the source of the single most expensive mistake of Week 1, and section 8.1 is devoted to it.

### 6.1 `append` — add one item

```python
items = ["a", "b"]
result = items.append("c")
print(items)        # ['a', 'b', 'c']
print(result)       # None            <- append hands back nothing
```

`append` always adds **exactly one item**, whatever that item is. Append a list and you get a list *inside* your list:

```python
items = ["a", "b"]
items.append(["c", "d"])
print(items)        # ['a', 'b', ['c', 'd']]
print(len(items))   # 3               <- not 4
```

### 6.2 `extend` — add every item of another sequence

```python
items = ["a", "b"]
items.extend(["c", "d"])
print(items)        # ['a', 'b', 'c', 'd']
print(len(items))   # 4
```

The difference between `append` and `extend` in one screen:

```python
one = [1, 2]
one.append([3, 4])
print(one)          # [1, 2, [3, 4]]      one new item, which is a list

two = [1, 2]
two.extend([3, 4])
print(two)          # [1, 2, 3, 4]        two new items

three = ["a"]
three.extend("bc")  # a string is a sequence of characters
print(three)        # ['a', 'b', 'c']     <- rarely what you meant
```

`extend` and `+=` do the same thing to a list. `items = items + other` does something subtly different, and section 13.3 explains why the difference matters.

### 6.3 `insert` — add at a position

```python
items = ["a", "c"]
items.insert(1, "b")        # insert before index 1
print(items)                # ['a', 'b', 'c']
items.insert(0, "start")    # insert at the front
print(items)                # ['start', 'a', 'b', 'c']
items.insert(999, "end")    # an index past the end clips to the end
print(items)                # ['start', 'a', 'b', 'c', 'end']
```

`insert(0, x)` is how you add to the front. It is worth knowing that inserting at the front is slower than appending at the end, because every other item has to shuffle up one place. For a few hundred items you will never notice; for a few million, you will.

### 6.4 `pop` — remove *and* return

`pop` is the one method whose return value you nearly always want:

```python
queue = ["first", "second", "third"]
last = queue.pop()          # no argument -> the last item
print(last)                 # third
print(queue)                # ['first', 'second']

first = queue.pop(0)        # an index -> that item
print(first)                # first
print(queue)                # ['second']

queue.pop()
queue.pop()                 # IndexError: pop from empty list
```

"Remove the last item and tell me what it was" is `pop()`. That is how you process a pile of work in a loop until it is empty.

### 6.5 `remove` — delete by value

```python
items = ["a", "b", "c", "b"]
items.remove("b")
print(items)                # ['a', 'c', 'b']    <- only the FIRST match went
items.remove("zzz")         # ValueError: list.remove(x): x not in list
```

Two facts, both easy to forget: `remove` deletes one occurrence, not all of them, and it raises `ValueError` if the value is not there. Check with `in` first (section 11) when absence is a possibility.

### 6.6 `index` and `count` — questions, not changes

```python
names = ["Ada", "Grace", "Alan", "Grace"]
print(names.index("Grace"))     # 1     the FIRST position
print(names.count("Grace"))     # 2
print(names.count("Nobody"))    # 0     no error
print(names.index("Nobody"))    # ValueError: 'Nobody' is not in list
```

`count` is safe for anything. `index` raises when it fails, so guard it with `in`:

```python
if "Nobody" in names:
    print(names.index("Nobody"))
else:
    print("not present")        # not present
```

### 6.7 `sort`, `reverse`, `clear`, `copy`

```python
scores = [88, 92, 79]
scores.sort()
print(scores)               # [79, 88, 92]        rearranged in place
scores.sort(reverse=True)
print(scores)               # [92, 88, 79]

letters = ["a", "b", "c"]
letters.reverse()
print(letters)              # ['c', 'b', 'a']     reversed in place

backup = letters.copy()     # a new list with the same items
letters.clear()
print(letters)              # []
print(backup)               # ['c', 'b', 'a']     the copy survived
```

`reverse()` reorders the list you have; `letters[::-1]` produces a new reversed list and leaves the original alone. Pick according to whether you want the original preserved.

---

## 7. Functions that work on a whole list

These are **functions**, not methods — you write `len(items)`, not `items.len()`. None of them changes the list.

```python
scores = [88, 92, 79, 92]
print(len(scores))          # 4
print(sum(scores))          # 351
print(min(scores))          # 79
print(max(scores))          # 92
print(sum(scores) / len(scores))    # 87.75      the average
print(sorted(scores))       # [79, 88, 92, 92]   a NEW sorted list
print(scores)               # [88, 92, 79, 92]   original untouched
```

### 7.1 `sorted` and `reversed`

```python
words = ["pear", "fig", "apple"]
print(sorted(words))                # ['apple', 'fig', 'pear']
print(sorted(words, reverse=True))  # ['pear', 'fig', 'apple']
print(words)                        # ['pear', 'fig', 'apple']   untouched

print(list(reversed(words)))        # ['apple', 'fig', 'pear']
print(words[::-1])                  # ['apple', 'fig', 'pear']   same result
```

`reversed(words)` does not hand you a list — it hands you a lazy walker that produces the items backwards one at a time. Printing it shows something unhelpful like `<list_reverseiterator object at 0x7f...>`. Wrap it in `list()` when you want a list, or use it directly in a `for` loop where laziness costs nothing:

```python
for word in reversed(words):
    print(word)
```

```
apple
fig
pear
```

Why be lazy at all? Because reversing a ten-million-item list to look at the first three of them wastes ten million copies. Day 15 is entirely about that idea.

### 7.2 `any` and `all`

Both take a list and answer a yes/no question about its truthiness (Day 03).

```python
print(any([False, False, True]))    # True     at least one is true
print(all([True, True, True]))      # True     every one is true
print(all([True, False]))           # False
print(any([0, "", None]))           # False    every item is falsy
print(all([1, "a", [0]]))           # True     every item is truthy
```

The empty-list cases look odd until you read them out loud:

```python
print(any([]))      # False    "is at least one true?" — there are none, so no
print(all([]))      # True     "are they all true?" — there are none to fail
```

`all([])` being `True` is a real source of bugs when the list came from a filter that matched nothing. If "empty" matters, test `len(items) > 0` separately.

### 7.3 The reference table

| Call | Returns | Note |
|---|---|---|
| `len(items)` | `int` | number of items |
| `sum(items)` | number | numbers only; `sum([])` is `0` |
| `min(items)` / `max(items)` | an item | raises `ValueError` on an empty list |
| `sorted(items)` | **new list** | original untouched |
| `reversed(items)` | lazy walker | wrap in `list()` for a list |
| `any(items)` | `bool` | `any([])` is `False` |
| `all(items)` | `bool` | `all([])` is `True` |
| `list(other)` | **new list** | converts and copies |
| `enumerate(items)` | lazy pairs | section 9 |
| `zip(a, b)` | lazy pairs | section 10 |

> **Gotcha:** `min([])` and `max([])` raise `ValueError: min() arg is an empty sequence`, but `sum([])` is `0` and `len([])` is `0`. If your data can be empty — and real data can always be empty — check before calling `min` or `max`.

---

## 8. `sort` versus `sorted`

Two tools, same job, different shapes. The distinction is not stylistic.

```python
scores = [88, 92, 79]

scores.sort()               # METHOD: rearranges scores, returns None
print(scores)               # [79, 88, 92]

names = ["Zoe", "Ada"]
ordered = sorted(names)     # FUNCTION: returns a new list, leaves names alone
print(ordered)              # ['Ada', 'Zoe']
print(names)                # ['Zoe', 'Ada']
```

| | `items.sort()` | `sorted(items)` |
|---|---|---|
| Kind | method on a list | function on any sequence |
| Returns | `None` | a new list |
| Original | reordered | untouched |
| Works on a string? | no | yes — gives a list of characters |
| Use when | you own the list and want it ordered | you must not disturb the input |

`sorted` works on anything you can loop over, which lists do not:

```python
print(sorted("cab"))                    # ['a', 'b', 'c']
print("".join(sorted("cab")))           # abc
```

### 8.1 `.sort()` returns `None` — the mistake that eats an evening

Type this line and you have destroyed your data:

```python
scores = [88, 92, 79]
scores = scores.sort()          # <- looks so reasonable
print(scores)                   # None
```

`scores.sort()` sorted the list and returned `None`, exactly as documented. Then `scores =` threw the sorted list away and bound the name to `None`. Your list is gone. And the error you get is not at this line — it is further down, at whatever tries to use it:

```python
print(len(scores))              # TypeError: object of type 'NoneType' has no len()
print(scores[0])                # TypeError: 'NoneType' object is not subscriptable
for score in scores:            # TypeError: 'NoneType' object is not iterable
    print(score)
```

The rule, which covers `sort`, `reverse`, `append`, `extend`, `insert`, `remove` and `clear` all at once:

> **A method that changes a list in place returns `None`. Never assign its result to anything.**

```python
scores.sort()                   # correct: call it, keep the list
scores = sorted(scores)         # also correct: assign the FUNCTION's result
scores = scores.sort()          # wrong, always, in every context
```

This is a deliberate design decision, not an oversight. Returning `None` from mutating methods means a line can either change a thing or produce a thing, never both, so you can tell which is happening by looking at it. Python applies the same rule everywhere: `list.append`, `dict.update` and `set.add` all return `None`.

> **Gotcha:** the same trap in string clothing, and it is the mirror image. `text.strip()` returns a new string and you *must* assign it (`text = text.strip()`); `items.sort()` returns `None` and you must *not*. The difference is that strings are immutable, so their methods have nothing to do but return a new value. Ask yourself "can this type be changed in place?" and the answer falls out.

### 8.2 Sorting by something other than the value

By default `sorted` compares the items themselves: numbers numerically, strings alphabetically by character code. Two consequences of "by character code" catch everyone:

```python
print(sorted(["banana", "Apple", "cherry"]))     # ['Apple', 'banana', 'cherry']
print(sorted([10, 9, 100]))                      # [9, 10, 100]
print(sorted(["10", "9", "100"]))                # ['10', '100', '9']
```

Every capital letter sorts before every lower-case letter, because `"A"` is character 65 and `"a"` is 97. And `"100"` sorts before `"9"` because text is compared position by position — `"1"` beats `"9"` at the first character, and the comparison stops there.

To sort by something *derived* from each item, pass `key=`. The value you give `key=` is a **function** — not a call, a function itself, with no brackets after it. Python calls it once per item and sorts by the answers.

```python
words = ["banana", "fig", "apple"]

print(sorted(words, key=len))           # ['fig', 'apple', 'banana']
print(sorted(words, key=len, reverse=True))    # ['banana', 'apple', 'fig']
print(sorted(["banana", "Apple"], key=str.lower))   # ['Apple', 'banana']
```

`key=len` reads as "sort by the length of each item". Note there are no brackets on `len` — `key=len()` would call `len` with no arguments right now and fail. You are handing over the function itself for Python to call later.

When no built-in function computes what you need, write one and give it a name. `def` gets taught properly on Day 08; today, treat it as "a named recipe that takes something in and hands something back":

```python
def second_item(pair: tuple[str, int]) -> int:
    """Pull the number out of a (name, score) pair."""
    return pair[1]


results = [("Ada", 88), ("Grace", 95), ("Alan", 79)]
print(sorted(results, key=second_item))
# [('Alan', 79), ('Ada', 88), ('Grace', 95)]
print(sorted(results, key=second_item, reverse=True))
# [('Grace', 95), ('Ada', 88), ('Alan', 79)]
```

That is a leaderboard, in one line, from data in any order.

A named key function can compute anything you like, which is where it beats `len`:

```python
def surname(full_name: str) -> str:
    """The last whitespace-separated word of a name."""
    return full_name.split()[-1]


people = ["Ada Lovelace", "Grace Hopper", "Alan Turing"]
print(sorted(people, key=surname))
# ['Grace Hopper', 'Ada Lovelace', 'Alan Turing']
```

> **Forward reference:** Python has a way to write a throwaway one-expression function inline, right there in the `key=` slot, and you will meet it constantly in other people's code. That is Day 16, and it is deliberately not today. A named function is not a beginner's substitute for it either — a name that says *why* you are sorting is frequently the better choice even once you know both forms.

### 8.3 Sorting by two things at once

Return a tuple from your key function and Python compares the first element, then breaks ties with the second:

```python
def length_then_alphabetical(word: str) -> tuple[int, str]:
    """Sort key: shortest first, then alphabetical among equal lengths."""
    return (len(word), word)


words = ["pear", "fig", "plum", "kiwi", "date"]
print(sorted(words, key=length_then_alphabetical))
# ['fig', 'date', 'kiwi', 'pear', 'plum']
```

All the four-letter words come after `"fig"`, and among themselves they are alphabetical. This is the standard way to express "rank by score, then by name for ties", and you will use it in exercise 10.

> **Gotcha:** `sorted` refuses to compare types it has no ordering for. `sorted([1, "a"])` raises `TypeError: '<' not supported between instances of 'str' and 'int'`. This is a common surprise when a list of numbers has one string in it because something came out of a file untranslated.

---

## 9. `enumerate` — position and item together

You often need both the item and where it was. The obvious approach works and is clumsy:

```python
names = ["Ada", "Grace", "Alan"]
for index in range(len(names)):
    print(index, names[index])
```

`enumerate` gives you both directly:

```python
for index, name in enumerate(names):
    print(index, name)
```

```
0 Ada
1 Grace
2 Alan
```

`enumerate` hands out a pair for each item — position first, item second — and `for index, name in ...` unpacks that pair into two names (section 12.3 explains unpacking properly).

Numbering for humans starts at 1, and `enumerate` takes a `start`:

```python
for rank, name in enumerate(names, start=1):
    print(f"{rank}. {name}")
```

```
1. Ada
2. Grace
3. Alan
```

That second argument saves you writing `index + 1` in three places and getting it wrong in one of them.

Like `reversed`, `enumerate` is lazy. To see it as data, convert it:

```python
print(list(enumerate(["a", "b"])))              # [(0, 'a'), (1, 'b')]
print(list(enumerate(["a", "b"], start=1)))     # [(1, 'a'), (2, 'b')]
```

The pairs are **tuples**, which is one reason tuples are on today's menu.

> **Gotcha:** `for index, name in names:` — forgetting the `enumerate` — fails with `ValueError: too many values to unpack (expected 2)`, because it tries to split the string `"Ada"` into two names. Read the error as "you asked for two things and the item was not a pair of things".

---

## 10. `zip` — walk two lists side by side

When related data lives in two lists, `zip` pairs them up position by position:

```python
names = ["Ada", "Grace", "Alan"]
scores = [88, 95, 79]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

```
Ada: 88
Grace: 95
Alan: 79
```

`zip` is lazy too, and `list()` shows what it produces:

```python
print(list(zip(names, scores)))
# [('Ada', 88), ('Grace', 95), ('Alan', 79)]
```

A list of pairs — which is exactly the shape section 8.2 sorted, and (Day 06) exactly the shape a dictionary is built from.

`zip` takes as many lists as you like:

```python
codes = ["A", "B", "C"]
print(list(zip(names, scores, codes)))
# [('Ada', 88, 'A'), ('Grace', 95, 'B'), ('Alan', 79, 'C')]
```

> **Gotcha:** `zip` stops at the shortest input and says nothing. `list(zip([1, 2, 3], ["a"]))` is `[(1, 'a')]` — two items silently dropped. When the lists are supposed to be the same length, that silence hides a real bug, so check `len(a) == len(b)` first if it matters. (Python 3.10+ has `zip(a, b, strict=True)`, which raises instead. Use it when you can.)

---

## 11. `in` — membership

```python
names = ["Ada", "Grace", "Alan"]
print("Ada" in names)          # True
print("Zoe" in names)          # False
print("Zoe" not in names)      # True
print("ada" in names)          # False    exact match, case included
```

`in` on a list checks whole items, not parts of them:

```python
print("Ad" in names)           # False    'Ad' is not one of the items
print("Ad" in names[0])        # True     that is a STRING containment test
```

This is the guard you put in front of `remove` and `index`:

```python
if "Grace" in names:
    names.remove("Grace")
print(names)                   # ['Ada', 'Alan']
```

> **Gotcha:** `in` on a list searches item by item from the front. For a handful of items that is instant. For a list of a hundred thousand names, checked inside a loop that runs a hundred thousand times, it is ten billion comparisons and your program appears to hang. Day 06's `set` answers exactly this question without the search, and knowing when to reach for it is one of the genuine performance skills in Python.

---

## 12. Tuples

A tuple is an ordered sequence, like a list, that **cannot be changed** after it is created. Round brackets instead of square:

```python
point = (3, 4)
print(point)            # (3, 4)
print(point[0])         # 3
print(point[-1])        # 4
print(len(point))       # 2
print(type(point).__name__)     # tuple

point[0] = 99           # TypeError: 'tuple' object does not support item assignment
```

Everything that reads works: indexing, slicing, `len`, `in`, `count`, `index`, looping, `sorted`, `min`, `max`, `sum`. Everything that writes is absent — no `append`, no `sort`, no `remove`.

```python
point = (3, 4, 5)
print(point[1:])        # (4, 5)        slicing a tuple gives a tuple
print(4 in point)       # True
print(sum(point))       # 12
print(sorted(point))    # [3, 4, 5]     sorted always returns a LIST
```

### 12.1 The comma is what makes a tuple

The brackets are usually optional; the comma never is.

```python
pair = 3, 4                 # a tuple, no brackets needed
print(pair)                 # (3, 4)

not_a_tuple = (5)           # brackets around one value are just grouping
print(type(not_a_tuple).__name__)   # int

one_tuple = (5,)            # THE COMMA makes it a tuple
print(type(one_tuple).__name__)     # tuple
print(len(one_tuple))               # 1

empty = ()
print(len(empty))                   # 0
```

The one-element tuple with its trailing comma looks like a typo and is not. `("a")` is the string `"a"`; `("a",)` is a tuple holding it. Watch for this when a function wants a tuple of options and you pass only one.

### 12.2 Why immutability is useful

"A list, but worse" is the obvious first reaction. Here is what you actually gain:

**1. It cannot be changed by accident.** If you hand a list to code you do not control, that code can append to it, sort it, or empty it, and your data changes under you. Hand over a tuple and no code anywhere can alter it. The guarantee is enforced by the language, not by a comment asking politely.

**2. It can be a dictionary key.** Only unchangeable values can be dictionary keys or set members (Day 06 explains why). A tuple can; a list cannot:

```python
locations = {}
locations[(51.5, -0.1)] = "London"      # fine: a tuple key
print(locations)                         # {(51.5, -0.1): 'London'}

locations[[51.5, -0.1]] = "London"       # TypeError: unhashable type: 'list'
```

Coordinates, (row, column) cells, (year, month) periods — all naturally tuples, all frequently keys.

**3. It signals intent.** A tuple says "this is one thing made of fixed parts": a point has an x and a y, a colour has three channels, a database row has these columns in this order. A list says "this is several of the same thing, and there might be more tomorrow". A reader who knows the convention learns something from your choice of brackets.

The practical rule:

> **Same kind of thing, variable number, might change** — list. **Different roles, fixed number, fixed once made** — tuple.

**4. Functions return tuples.** You have already seen one: `divmod(17, 5)` gives `(3, 2)`. Returning several values as a tuple is normal Python, and it is why unpacking is the next section.

### 12.3 Unpacking

Assign a tuple to several names at once and each name gets one element:

```python
point = (3, 4)
x, y = point
print(x)        # 3
print(y)        # 4

quotient, remainder = divmod(17, 5)
print(quotient, remainder)      # 3 2

first, second, third = "abc"    # works on any sequence, not only tuples
print(first, second, third)     # a b c

head, tail = ["one", "two"]     # and on lists
print(head, tail)               # one two
```

The count must match exactly:

```python
x, y = (1, 2, 3)        # ValueError: too many values to unpack (expected 2)
x, y, z = (1, 2)        # ValueError: not enough values to unpack (expected 3, got 2)
```

Unpacking is why `for index, name in enumerate(names)` and `for name, score in zip(names, scores)` work: each item is a pair, and the two names take its two parts.

When you do not need one of the parts, the convention is to name it `_`:

```python
results = [("Ada", 88), ("Grace", 95)]
for name, _ in results:
    print(name)
```

```
Ada
Grace
```

`_` is an ordinary variable name with no special power. Using it announces "I know there is a value here and I am ignoring it on purpose".

### 12.4 The swap idiom

Swapping two variables in most languages needs a third:

```python
a = 1
b = 2
temp = a
a = b
b = temp
print(a, b)     # 2 1
```

In Python, tuple unpacking does it in one line:

```python
a = 1
b = 2
a, b = b, a
print(a, b)     # 2 1
```

The right-hand side is evaluated **first and completely** — it builds the tuple `(2, 1)` from the current values — and only then are the names assigned. That ordering is what makes the swap safe, and it generalises:

```python
first, middle, last = "x", "y", "z"
first, middle, last = last, first, middle
print(first, middle, last)      # z x y
```

It also means this does what you would hope, with no temporary variable and no partial state:

```python
items = ["a", "b", "c"]
items[0], items[-1] = items[-1], items[0]
print(items)        # ['c', 'b', 'a']
```

### 12.5 Tuples are not entirely bulletproof

A tuple's *contents* cannot be swapped out. If one of those contents is itself mutable, that object can still change:

```python
row = ("header", [1, 2])
row[1].append(3)
print(row)              # ('header', [1, 2, 3])
row[1] = [9]            # TypeError: 'tuple' object does not support item assignment
```

The tuple still holds the same list it always held — that list changed. "Immutable" means the tuple's own slots are fixed, not that everything reachable from it is frozen. A tuple containing a list also cannot be a dictionary key, for the same reason.

---

## 13. Aliasing: two names, one list

This is the most important section of the day. Read it twice.

### 13.1 `b = a` does not copy

```python
a = [1, 2, 3]
b = a               # NOT a copy
b.append(4)
print(b)            # [1, 2, 3, 4]
print(a)            # [1, 2, 3, 4]     <- a changed too
```

Nothing copied anything. `b = a` made a second **name** for the one list that already existed. There is one list and two labels on it, so it does not matter which label you use to change it — the change is visible through both. Two names pointing at one object are called **aliases**.

You can confirm it. `id()` reports an object's identity, and `is` asks "are these the same object?":

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]           # a different list that happens to look the same

print(a is b)           # True     one object, two names
print(a is c)           # False    two objects
print(a == c)           # True     equal contents
print(id(a) == id(b))   # True
```

`==` asks "same contents?". `is` asks "same object?". They answer different questions and confusing them causes bugs that survive code review.

Why is this not a problem with numbers and strings? It is, and it never shows, because they are immutable:

```python
a = 5
b = a
b = b + 1               # cannot change 5; makes 6 and rebinds b
print(a, b)             # 5 6       a is untouched
```

There is no operation on an `int` or a `str` that changes it in place, so aliasing is undetectable. Lists, dicts and sets have such operations, so aliasing is visible — and, when unintended, expensive.

### 13.2 Where this actually bites you

**Rebinding versus mutating.** These two lines look similar and behave completely differently:

```python
a = [1, 2, 3]
b = a
b = [9, 9]          # REBIND: b now names a different list
print(a)            # [1, 2, 3]     unaffected

a = [1, 2, 3]
b = a
b.append(9)         # MUTATE: changes the shared list
print(a)            # [1, 2, 3, 9]  affected
```

`b = ...` moves a label. `b.something()` changes the object. Every aliasing bug is that distinction, missed.

**Passing a list to a function.** A function receives the same list, not a copy, so a mutating method inside the function changes the caller's data:

```python
def add_zero(numbers: list[int]) -> None:
    """Append a zero to the list that was passed in."""
    numbers.append(0)


scores = [1, 2]
add_zero(scores)
print(scores)       # [1, 2, 0]      the caller's list changed
```

Sometimes that is the point. Frequently it is a surprise, and "this function quietly modified my input" is a bug report you will file and receive for the rest of your career. Today's exercises are strict about it: several of them require you to return a **new** list and leave the argument exactly as you found it, and the tests check the argument afterwards.

**Copying a list of lists — the shared-row trap.** This one is famous:

```python
grid = [[0] * 3] * 3
print(grid)         # [[0, 0, 0], [0, 0, 0], [0, 0, 0]]     looks perfect

grid[0][0] = 9
print(grid)         # [[9, 0, 0], [9, 0, 0], [9, 0, 0]]     three 9s!
```

Read `[[0] * 3] * 3` carefully. The inner `[0] * 3` runs **once**, producing one row. The outer `* 3` then makes a list containing that same row three times — three references to one list, not three lists.

```python
grid = [[0] * 3] * 3
print(grid[0] is grid[1])       # True      the same row object
print(len(grid))                # 3         three entries, one list
```

Build it with a loop instead, so `[0] * 3` runs afresh each time:

```python
grid = []
for row_index in range(3):
    grid.append([0] * 3)        # a NEW row on every pass

grid[0][0] = 9
print(grid)                     # [[9, 0, 0], [0, 0, 0], [0, 0, 0]]
print(grid[0] is grid[1])       # False     three distinct rows
```

Exercise 9 is this, and the test for it changes one cell and checks the others.

### 13.3 Copying a list: three ways, all the same

When you want a genuinely separate list, say so. All three of these produce a new list with the same items:

```python
a = [1, 2, 3]

b = list(a)         # the type name used as a converter
c = a.copy()        # the method, added in Python 3.3
d = a[:]            # a full slice — and every slice is a new list

b.append(99)
c.append(88)
d.append(77)
print(a)            # [1, 2, 3]     untouched by all three
print(b)            # [1, 2, 3, 99]
print(a is b, a is c, a is d)       # False False False
```

Which to use? `list(a)` is the clearest to a newcomer and works on any sequence (including a tuple or a string). `a.copy()` says "copy" in the plainest possible English. `a[:]` is compact and extremely common in existing code, so you must be able to read it.

There is a fourth form you have already met, and it matters because it is the one that surprises people:

```python
a = [1, 2]
b = a
a = a + [3]         # + builds a NEW list; a is rebound to it
print(a, b)         # [1, 2, 3] [1, 2]      b kept the old list

a = [1, 2]
b = a
a += [3]            # += on a list MUTATES it in place, like extend
print(a, b)         # [1, 2, 3] [1, 2, 3]   b sees the change
```

For numbers and strings, `x = x + y` and `x += y` are interchangeable. For lists they are not: `+` creates, `+=` modifies. That is a genuine trap and it is not a spelling difference.

### 13.4 Shallow versus deep

Every copy in section 13.3 is a **shallow** copy: it makes a new outer list holding the *same inner objects*. If the items are numbers or strings, that is a complete copy, because those cannot change. If the items are themselves lists, it is not:

```python
original = [[1, 2], [3, 4]]
shallow = list(original)            # new outer list...

print(shallow is original)          # False     different outer lists
print(shallow[0] is original[0])    # True      SAME inner list

shallow[0].append(99)
print(original)                     # [[1, 2, 99], [3, 4]]   leaked through
shallow.append([5, 6])              # outer change stays local
print(original)                     # [[1, 2, 99], [3, 4]]
```

Picture it:

```
    original ──> [ ●   ,   ● ]
                   \       \
                    \       \
                    [1,2]   [3,4]        <- the inner lists
                    /       /
                   /       /
    shallow  ──> [ ●   ,   ● ]

  Two outer lists. Two entries each. But only TWO inner lists in total,
  each one pointed at twice. Change an inner list through either outer
  list and both "copies" show the change.
```

A **deep** copy makes new inner lists as well. With one level of nesting you can do it with a loop and one copy per row:

```python
original = [[1, 2], [3, 4]]

deep = []
for row in original:
    deep.append(list(row))          # a fresh copy of each row

print(deep == original)             # True      same contents
print(deep[0] is original[0])       # False     different objects
deep[0].append(99)
print(original)                     # [[1, 2], [3, 4]]    untouched
```

For arbitrarily nested data the standard library has `copy.deepcopy`, which handles any depth and any cycles. It needs an import, imports are Day 11, and a loop is clearer for the one-level case you will meet this week. Knowing the function exists is today's job.

The rule to carry forward:

> One level of nesting needs one level of copying. `list(x)` protects the outer list only.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `scores = scores.sort()` | `scores` is `None`; later `TypeError: 'NoneType' object is not ...` | `scores.sort()`, or `scores = sorted(scores)` |
| Assigning any mutating method's result | `None` where a list should be | mutating methods return `None`; call them, do not assign them |
| `items[len(items)]` | `IndexError: list index out of range` | last index is `len(items) - 1`, or use `items[-1]` |
| `items[len(items) / 2]` | `TypeError: list indices must be integers` | `//` not `/` |
| `append` when you meant `extend` | a list nested inside your list | `extend` for many items, `append` for one |
| `extend("ab")` | `['a', 'b']` — separate characters | a string is a sequence; wrap it: `extend(["ab"])` |
| `remove(x)` on a missing value | `ValueError: list.remove(x): x not in list` | check `if x in items` first |
| `index(x)` on a missing value | `ValueError: 'x' is not in list` | check `in` first, or use `count` |
| `min([])` / `max([])` | `ValueError: min() arg is an empty sequence` | test `len(items) > 0` first |
| Expecting `all([])` to be `False` | `True` | check emptiness separately |
| `b = a` expecting a copy | changing `b` changes `a` | `list(a)`, `a.copy()` or `a[:]` |
| `a += [x]` expecting a new list | aliases see the change | `a = a + [x]` to rebind instead |
| `[[0] * 3] * 3` | changing one cell changes a whole column | build rows in a loop |
| `list(nested)` expecting a deep copy | inner changes leak through | copy each row: `deep.append(list(row))` |
| Mutating a list you were given | the caller's data changes behind their back | copy first, or return a new list |
| `(5)` as a one-item tuple | it is the `int` `5` | `(5,)` — the comma makes the tuple |
| `zip` with unequal lengths | extra items silently dropped | check lengths, or `zip(a, b, strict=True)` |
| `for i, x in items:` | `ValueError: too many values to unpack` | you meant `enumerate(items)` |
| `sorted([1, "a"])` | `TypeError: '<' not supported between ...` | make the types uniform first |
| `sorted(words, key=len())` | `TypeError: len() takes exactly one argument` | pass the function, not a call: `key=len` |

---

## Mental model

A list is a **numbered shelf of hooks**. Each hook holds a tag; each tag points at a value. A variable name is a label stuck on the shelf, not on the values.

```
   scores ─────┐
               v
             +------+------+------+------+
   hook:     |  0   |  1   |  2   |  3   |     <- index from the left
             | -4   | -3   | -2   | -1   |     <- index from the right
             +------+------+------+------+
   holds:    |  88  |  92  |  79  |  95  |
             +------+------+------+------+
             0      1      2      3      4     <- slice boundaries live BETWEEN hooks

   scores[2]      -> 79            one hook
   scores[1:3]    -> [92, 79]      a NEW shelf holding what is between boundaries 1 and 3
   scores[-1]     -> 95            the last hook
   scores.append(100)              hang one more on the end — same shelf
   scores.sort()                   rearrange the tags — same shelf, returns None
   sorted(scores)                  a whole new shelf, this one untouched
```

Three consequences fall out of the picture, and they are the whole of today:

```
   ALIASING            b = a           one shelf, two labels
       a ──┐
           ├──> [ 1 , 2 , 3 ]          b.append(4) is visible through a,
       b ──┘                           because there is only one shelf

   COPYING             b = list(a)      two shelves, same tags
       a ────> [ ● , ● ]                b.append(4) is invisible to a
       b ────> [ ● , ● ]                (the tags point at the same values,
                 \   \                   but numbers and strings cannot change,
                  1   2                   so nobody can tell)

   SHALLOW TRAP        b = list(a)      two shelves, same tags, tags point at SHELVES
       a ────> [ ● , ● ]                b[0].append(9) IS visible through a,
       b ────> [ ● , ● ]                because a[0] and b[0] are one shelf
                 \   \
              [1,2]  [3,4]
```

- **Indexes name hooks; slice numbers name the gaps between them.** That is why `stop` is excluded and why `items[:n] + items[n:]` rebuilds the original.
- **A tuple is the same shelf welded shut.** You can read every hook; you cannot add, remove or re-hang one. That is what makes it safe to hand out and legal as a dictionary key.
- **Assignment moves labels; methods change shelves.** `b = a` is a label. `b.append(x)` is a shelf. Every mysteriously-changing-data bug you ever write will be those two confused.

---

## Practice

1. Run the demo and read every line of output against the code that produced it. The aliasing section at the end is the one to slow down on:

   ```bash
   python course/week1/day05_lists_and_tuples/examples.py
   ```

2. Fifteen minutes in the REPL, predicting the answer before you press Enter:

   ```bash
   python
   ```

   Try: `[1,2,3][-1]`, `[1,2,3][1:]`, `[1,2,3][::-1]`, `[1,2,3][5:]`, `len([0]*4)`, `[1,2]+[3]`, `["a"].append(["b"])` then print the list, `["a"].extend("bc")` then print, `[3,1,2].sort()`, `sorted([3,1,2])`, `sorted(["10","9"])`, `sorted(["b","A"])`, `sorted(["pear","fig"], key=len)`, `list(enumerate("ab", start=1))`, `list(zip([1,2,3],["a"]))`, `any([])`, `all([])`, `(5)` vs `(5,)`, and then the big one:

   ```python
   a = [[0] * 2] * 2
   a[0][0] = 9
   a
   ```

   Predict that last result before you run it. If you predicted `[[9, 0], [0, 0]]`, re-read section 13.2 — this is the single most common list bug in Python.

3. Open `course/week1/day05_lists_and_tuples/exercises.py` and work top to bottom. Read each docstring's examples carefully: where an exercise says "does not modify the argument", the tests check the argument afterwards, and that is deliberate.

4. Grade yourself from the course root:

   ```bash
   python check.py day05
   python check.py day05 -v      # full failure detail
   ```

5. Extra rep, no tests attached: write a program that takes `["ada", "grace", "alan", "edsger"]` and prints a numbered list, longest name first, with ties broken alphabetically — using `enumerate(..., start=1)` and a named key function that returns a tuple. Then change the tie-break to reverse-alphabetical and notice what you *cannot* do by flipping `reverse=True` (it flips both parts of the key at once). Solving that properly needs a trick: negate the numeric part instead.

---

## Recall check

1. `items = ["a", "b", "c", "d"]`. Give the value of `items[1]`, `items[-1]`, `items[1:3]`, `items[:2]`, `items[-2:]`, `items[::-1]`, `items[10:]`.
2. What does `items.append(["x", "y"])` do to a three-item list, and how does `items.extend(["x", "y"])` differ?
3. Which list methods return `None`, and what is the specific damage done by `items = items.sort()`?
4. When would you use `sorted(items)` rather than `items.sort()`?
5. What do you pass to `key=` — a function or a call to a function? Write the line that sorts `["pear", "fig"]` shortest-first, and the line that sorts `[("Ada", 88), ("Alan", 79)]` highest-score-first using a named function.
6. What is the difference between `a == b` and `a is b`?
7. `a = [1, 2]`, then `b = a`, then `b.append(3)`. What is `a`? Now the same but with `b = list(a)` — what is `a`? Why do the two differ?
8. Why does `grid = [[0] * 3] * 3` followed by `grid[0][0] = 9` change three rows, and how do you build the grid so it does not?
9. `original = [[1, 2], [3, 4]]` and `copy_of_it = list(original)`. Which of these affects `original`: `copy_of_it.append([5, 6])`, or `copy_of_it[0].append(99)`? Why?
10. Give two reasons to choose a tuple over a list, and say what `(5)` and `(5,)` each are.

<details>
<summary>Answers</summary>

1. `"b"`, `"d"`, `["b", "c"]`, `["a", "b"]`, `["c", "d"]`, `["d", "c", "b", "a"]`, `[]`. The last one is the important one: an out-of-range *slice* returns an empty list without complaint, while an out-of-range *index* raises `IndexError`.
2. `append` adds exactly one item, so the list becomes four items long and the fourth is itself a list: `['a', 'b', 'c', ['x', 'y']]`. `extend` adds every item of its argument, giving five items: `['a', 'b', 'c', 'x', 'y']`. Beware `extend("xy")`, which adds two separate characters.
3. `append`, `extend`, `insert`, `remove`, `clear`, `sort` and `reverse` all return `None` (`pop` returns the removed item; `copy`, `index` and `count` return values). `items = items.sort()` sorts the list, then throws the sorted list away and binds the name to `None`. The error surfaces later and elsewhere — `TypeError: 'NoneType' object is not iterable` or `has no len()` — which is what makes it expensive to find.
4. When you must not disturb the original: it belongs to your caller, someone else is still using it, or you need both orders. Also when the input is not a list at all — `sorted` works on strings, tuples, ranges and (Day 06) dictionaries, and always returns a list.
5. A function, with no brackets after it: `key=len`, not `key=len()`. Python calls it once per item. Shortest-first: `sorted(["pear", "fig"], key=len)`. For the pairs, define `def score_of(pair): return pair[1]` and call `sorted(results, key=score_of, reverse=True)`.
6. `==` compares contents: two different lists holding equal items are `==`. `is` compares identity: it is `True` only when both names refer to the very same object. `[1,2] == [1,2]` is `True`; `[1,2] is [1,2]` is `False`.
7. With `b = a`, `a` becomes `[1, 2, 3]` — `b = a` created a second name for one list, and `append` changed that one list. With `b = list(a)`, `a` stays `[1, 2]` — `list()` built a separate list, so `b`'s change happens somewhere `a` cannot see.
8. The inner `[0] * 3` is evaluated once, producing a single row; the outer `* 3` stores three references to that one row. Setting `grid[0][0]` changes the only row that exists, and all three entries show it. Build it with a loop that appends a fresh `[0] * 3` each pass, so there are three separate rows.
9. `copy_of_it[0].append(99)` affects `original`; `copy_of_it.append([5, 6])` does not. `list(original)` is a *shallow* copy: the outer list is new, so adding to it is invisible to `original`, but both outer lists point at the same two inner lists, so mutating an inner list is visible through both. Copy each row (`deep.append(list(row))`) if you need independence.
10. Any two of: it cannot be changed by accident, including by code you handed it to; it can be a dictionary key or set member, where a list cannot; it signals "fixed number of parts with different roles" to a reader; it is what functions like `divmod`, `enumerate` and `zip` hand back, so unpacking it is idiomatic. `(5)` is the integer `5` — brackets there are only grouping. `(5,)` is a one-element tuple, and the comma is what makes it one.

</details>
