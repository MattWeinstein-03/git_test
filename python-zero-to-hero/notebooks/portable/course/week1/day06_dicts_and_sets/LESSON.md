# Day 06 — Dictionaries and Sets

> **Time:** ~4 hours  |  **Prerequisites:** Day 05

## What you'll be able to do after today
- Build a dictionary, read from it, add to it, change it and delete from it, and say exactly when a lookup raises `KeyError` and when it hands you a default instead.
- Loop over a dictionary's keys, its values, or both at once, and explain why `.keys()` is a live view rather than a snapshot.
- Write the counting pattern and the grouping pattern from memory — the two loops that turn a pile of raw records into an answer.
- Find the key with the largest value in one line with `max(d, key=d.get)`, and rank a whole dictionary by value.
- Store a dictionary inside a dictionary, and a list inside a dictionary, and reach a value two levels down.
- Use a set to remove duplicates, test membership, and compare two collections with union, intersection, difference and symmetric difference.
- Preserve original order while removing duplicates, with `dict.fromkeys`.
- Say why a list cannot be a dictionary key but a tuple can, and choose correctly between a list, a tuple, a dictionary and a set for a given job.
- Explain, in plain language, why looking something up in a dictionary of ten million items is no slower than in a dictionary of ten.

## Why this matters

Yesterday's list answers "what is at position 3?". Almost no real question sounds like that. Real questions sound like "what is Ada's score?", "how many times does the word *the* appear?", "which orders belong to customer 4192?", "have I already processed this ID?".

Answer those with a list and you write a search: walk every item, compare, stop when you find it. That works, and it gets slower in direct proportion to the amount of data, and it is a great deal of code for a small question. A dictionary answers all four instantly and reads like the question.

Dictionaries are also the native shape of the data you will meet from Day 10 onwards. A JSON document is a dictionary. A row from a database driver is a dictionary. An HTTP response's headers are a dictionary. A configuration file is a dictionary. Every keyword argument you pass to a function (Day 08) arrives as a dictionary. Python itself stores your variables in one.

Sets are the smaller idea with the sharper edge: the collection that holds no duplicates and can answer "is this in here?" without looking. Together with dictionaries they close the gap between "my program produces the right answer" and "my program produces the right answer on real data".

---

## 1. The problem a dictionary solves

Suppose you have names and scores. With lists, you keep them in step by position:

```python
names = ["Ada", "Grace", "Alan"]
scores = [88, 95, 79]
```

To find Grace's score you must find Grace's position first:

```python
position = names.index("Grace")     # 1
print(scores[position])             # 95
```

Three problems, in increasing order of seriousness:

1. **It is fragile.** Sort `names` and forget to sort `scores` the same way and every score now belongs to the wrong person. Nothing raises. The numbers are simply wrong from then on.
2. **It is slow.** `index` walks the list from the front. One lookup in a list of a million names is a million comparisons; a million lookups is a million million.
3. **It does not say what you mean.** `scores[names.index("Grace")]` is machinery. The question was "what is Grace's score?".

A dictionary stores the association directly:

```python
scores = {"Ada": 88, "Grace": 95, "Alan": 79}
print(scores["Grace"])      # 95
```

One structure, no parallel lists to keep in step, and the code is the question.

---

## 2. Making a dictionary

Curly braces, `key: value` pairs, commas between them.

```python
scores = {"Ada": 88, "Grace": 95, "Alan": 79}
empty = {}

print(scores)               # {'Ada': 88, 'Grace': 95, 'Alan': 79}
print(len(scores))          # 3
print(len(empty))           # 0
print(type(scores).__name__)    # dict
```

The vocabulary, which you need to be precise about:

- a **key** is what you look something up by — `"Ada"`
- a **value** is what you get back — `88`
- together they are an **item**, or a key-value pair
- `len(d)` counts pairs, not keys and values separately

Written out over several lines for readability, with a trailing comma that makes later edits a one-line diff:

```python
scores = {
    "Ada": 88,
    "Grace": 95,
    "Alan": 79,
}
```

### 2.1 The rules on keys and values

**Keys must be unique.** Write the same key twice and the last value wins, silently:

```python
print({"a": 1, "a": 2})     # {'a': 2}
```

**Keys must be immutable** — strings, numbers, tuples, `bool`, `None`. Not lists, not dictionaries, not sets. Section 14 explains why, and it is a genuinely interesting reason rather than an arbitrary rule.

**Values can be anything at all**, including lists and other dictionaries, and they do not need to be the same type as each other:

```python
person = {
    "name": "Ada",
    "age": 36,
    "scores": [88, 95],
    "address": {"city": "London"},
    "active": True,
}
print(person["scores"])         # [88, 95]
print(person["address"])        # {'city': 'London'}
```

**Order is kept.** A dictionary remembers the order you inserted keys in, and iterating gives them back in that order. That has been guaranteed since Python 3.7. Older tutorials that tell you dictionaries are unordered are describing a language version you will never use — but do not lean on the order to mean anything more than "the order they went in".

### 2.2 The other ways to build one

```python
print(dict(a=1, b=2))                       # {'a': 1, 'b': 2}
pairs = [("Ada", 88), ("Grace", 95)]
print(dict(pairs))                          # {'Ada': 88, 'Grace': 95}
print(dict(zip(["Ada", "Grace"], [88, 95])))    # {'Ada': 88, 'Grace': 95}
print(dict.fromkeys(["a", "b"], 0))         # {'a': 0, 'b': 0}
```

`dict(zip(names, scores))` is the answer to section 1's fragile parallel lists: zip them once, at the point where they are still in step, and never think about positions again.

`dict.fromkeys(keys, value)` builds a dictionary with every key mapped to the same starting value. It has a second, unrelated use that you will reach for constantly — deduplicating a list while keeping its order — and that is section 13.

> **Gotcha:** `{}` is an empty **dictionary**, not an empty set. `type({}).__name__` is `dict`. There is no literal for an empty set; you write `set()`. This trips up everyone once.

---

## 3. Lookup, `KeyError`, and `.get`

Square brackets, exactly like list indexing, except the index is a key:

```python
scores = {"Ada": 88, "Grace": 95}
print(scores["Ada"])        # 88
print(scores["Grace"])      # 95
print(scores["Nobody"])     # KeyError: 'Nobody'
```

`KeyError` is the dictionary's `IndexError`: you asked for something that is not there. Note what it does *not* do — there is no "return nothing" or "return zero". A missing key is an error, loudly, at the line that asked.

Three ways to handle a key that might be missing.

**1. Check first with `in`.** Membership on a dictionary tests **keys**:

```python
scores = {"Ada": 88}
print("Ada" in scores)          # True
print("Nobody" in scores)       # False
print(88 in scores)             # False   <- 88 is a VALUE, not a key

if "Nobody" in scores:
    print(scores["Nobody"])
else:
    print("no score recorded")  # no score recorded
```

**2. `.get(key)` — returns `None` when missing.**

```python
scores = {"Ada": 88}
print(scores.get("Ada"))        # 88
print(scores.get("Nobody"))     # None      no error at all
```

**3. `.get(key, default)` — returns your default when missing.** This is the one you will use most:

```python
scores = {"Ada": 88}
print(scores.get("Nobody", 0))      # 0
print(scores.get("Ada", 0))         # 88
print(scores.get("Nobody", "n/a"))  # n/a
```

`.get(key, 0)` reads as "the score if there is one, otherwise zero", and it collapses a four-line `if`/`else` into an expression. It is the backbone of the counting pattern in section 8.

Which to use? `d[key]` when a missing key means your program is broken and you want to hear about it immediately. `.get(key, default)` when absence is a normal, expected state of the world. Choosing `.get` everywhere out of caution is a mistake: it turns a loud bug at the right line into a `None` that travels somewhere else and fails there.

> **Gotcha:** `.get` does not add anything to the dictionary. `scores.get("Nobody", 0)` hands you `0` and `scores` still has no `"Nobody"` key. If you wanted the key to be created, that is `setdefault` (section 9) — a name that has confused people for thirty years, because it both gets *and* sets.

---

## 4. Adding, updating and deleting

### 4.1 Adding and updating are the same syntax

```python
scores = {"Ada": 88}

scores["Grace"] = 95        # the key is new -> it is added
print(scores)               # {'Ada': 88, 'Grace': 95}

scores["Ada"] = 100         # the key exists -> its value is replaced
print(scores)               # {'Ada': 100, 'Grace': 95}
```

This is a deliberate contrast with lists, where `items[5] = "x"` on a three-item list raises `IndexError` — a list will not grow by assignment, a dictionary will. Which means a typo in a key creates a new entry rather than complaining:

```python
scores["Adaa"] = 88         # no error; you now have a fourth person
```

Nothing protects you from that. Consistent key spelling matters.

Compound assignment works, as long as the key already exists:

```python
scores = {"Ada": 88}
scores["Ada"] += 10
print(scores)               # {'Ada': 98}

scores["Nobody"] += 1       # KeyError: 'Nobody' — there is nothing to add to
```

That last line is why the counting pattern is written the way it is.

### 4.2 `update` — merge another dictionary in

```python
settings = {"colour": "red", "size": 10}
settings.update({"size": 12, "font": "mono"})
print(settings)             # {'colour': 'red', 'size': 12, 'font': 'mono'}
```

Existing keys are overwritten, new keys are added, and `update` returns `None` — it changes the dictionary in place, following Day 05's rule about mutating methods. `settings = settings.update(...)` destroys your data exactly as `scores = scores.sort()` did.

There is also `|` for dictionaries (Python 3.9+), which builds a **new** merged dictionary and leaves both originals alone:

```python
defaults = {"colour": "red", "size": 10}
custom = {"size": 12}
print(defaults | custom)    # {'colour': 'red', 'size': 12}
print(defaults)             # {'colour': 'red', 'size': 10}   untouched
```

Right-hand side wins on conflicts. "Defaults, overridden by what the user asked for" is the standard use, and it is a one-liner.

### 4.3 Deleting

```python
scores = {"Ada": 88, "Grace": 95, "Alan": 79}

del scores["Alan"]              # remove by key
print(scores)                   # {'Ada': 88, 'Grace': 95}

removed = scores.pop("Grace")   # remove AND hand back the value
print(removed)                  # 95
print(scores)                   # {'Ada': 88}

print(scores.pop("Nobody", 0))  # 0      a default makes pop safe
del scores["Nobody"]            # KeyError: 'Nobody'
scores.pop("Nobody")            # KeyError: 'Nobody'

scores.clear()
print(scores)                   # {}
```

`pop` with a default is the safe removal: "take it out if it is there, otherwise give me this and say nothing".

### 4.4 The method table

| Operation | Returns | Missing key |
|---|---|---|
| `d[key]` | the value | **`KeyError`** |
| `d.get(key)` | the value or `None` | `None` |
| `d.get(key, default)` | the value or `default` | `default` |
| `d[key] = value` | — | creates the key |
| `d.setdefault(key, default)` | the value, creating it if needed | inserts `default` |
| `d.update(other)` | `None` | adds/overwrites |
| `del d[key]` | — | **`KeyError`** |
| `d.pop(key)` | the value | **`KeyError`** |
| `d.pop(key, default)` | the value or `default` | `default` |
| `d.clear()` | `None` | — |
| `d.copy()` | a new dict | — |
| `key in d` | `bool` | `False` |
| `len(d)` | `int` | — |

---

## 5. `keys`, `values`, `items` — and why they are live

Three methods give you the parts of a dictionary:

```python
scores = {"Ada": 88, "Grace": 95}
print(scores.keys())        # dict_keys(['Ada', 'Grace'])
print(scores.values())      # dict_values([88, 95])
print(scores.items())       # dict_items([('Ada', 88), ('Grace', 95)])
```

Those are not lists. Note the names in the output: `dict_keys`, not `list`. They are **views** — windows onto the dictionary that show whatever it contains *right now*.

```python
scores = {"Ada": 88}
keys = scores.keys()
print(keys)                 # dict_keys(['Ada'])

scores["Grace"] = 95        # change the dictionary...
print(keys)                 # dict_keys(['Ada', 'Grace'])   <- the view changed too
```

Nothing was recomputed. `keys` was never a copy; it is a live window. That is efficient — no data is duplicated — and it is a genuine surprise if you expected a snapshot.

When you want a snapshot, take one:

```python
scores = {"Ada": 88}
frozen = list(scores.keys())    # a real list, made now
scores["Grace"] = 95
print(frozen)                   # ['Ada']       unaffected
print(list(scores.keys()))      # ['Ada', 'Grace']
```

You can loop over a view, check membership in it, take its `len`, and pass it to `sorted`, `min`, `max`, `sum` and `list`. You cannot index it — `scores.keys()[0]` raises `TypeError: 'dict_keys' object is not subscriptable`, because a view has no positions. Wrap it in `list(...)` if you need position 0.

```python
scores = {"Ada": 88, "Grace": 95, "Alan": 79}
print(len(scores.keys()))           # 3
print("Ada" in scores.keys())       # True    (`"Ada" in scores` is the same test)
print(sorted(scores.keys()))        # ['Ada', 'Alan', 'Grace']
print(sum(scores.values()))         # 262
print(max(scores.values()))         # 95
print(list(scores.items())[0])      # ('Ada', 88)
```

`sum(scores.values())` and `max(scores.values())` are how you total and peak a dictionary. Note what `max(scores.values())` does *not* tell you: which key it belonged to. Section 11 fixes that.

> **Gotcha:** the liveness has a sharp edge. Adding or deleting keys **while looping over** a dictionary raises `RuntimeError: dictionary changed size during iteration`, because the view you are walking has changed under you. If you need to delete keys based on some condition, collect them into a list first and delete afterwards, in a second loop.

---

## 6. Iterating

Looping over a dictionary directly gives you its **keys**:

```python
scores = {"Ada": 88, "Grace": 95}

for name in scores:
    print(name)
```

```
Ada
Grace
```

`for name in scores` and `for name in scores.keys()` do the same thing. The shorter form is idiomatic; the longer one is not wrong, and is sometimes clearer next to a `.values()` loop.

To get the values you need the key or the view:

```python
for name in scores:
    print(name, scores[name])       # look each one up

for score in scores.values():       # values only, no keys
    print(score)
```

To get both at once — which is what you want nine times in ten — use `.items()` and unpack the pair, exactly as you did with `zip` and `enumerate` yesterday:

```python
for name, score in scores.items():
    print(f"{name} scored {score}")
```

```
Ada scored 88
Grace scored 95
```

`.items()` hands out a tuple per pair; `for name, score in ...` unpacks it into two names. This is the standard dictionary loop. Learn it as one movement.

Iteration follows insertion order, so you can sort it when you want a different one:

```python
scores = {"Grace": 95, "Ada": 88, "Alan": 79}

for name in sorted(scores):                 # keys, alphabetically
    print(name, scores[name])
```

```
Ada 88
Alan 79
Grace 95
```

`sorted(scores)` sorts the keys, because iterating a dictionary gives keys. It returns a list and does not touch the dictionary.

> **Gotcha:** `for name, score in scores:` — without `.items()` — fails with `ValueError: too many values to unpack (expected 2)`, because iterating a dictionary gives one key at a time and Python tries to split the string `"Grace"` into two names. Same error, same cause, as forgetting `enumerate` yesterday.

---

## 7. Nested dictionaries and dictionaries of lists

Values can be any type, including collections. Two shapes come up constantly.

### 7.1 A dictionary inside a dictionary

```python
people = {
    "ada": {"name": "Ada Lovelace", "age": 36, "city": "London"},
    "grace": {"name": "Grace Hopper", "age": 45, "city": "New York"},
}

print(people["ada"]["city"])            # London
print(people["ada"])                    # {'name': 'Ada Lovelace', ...}
print(len(people))                      # 2      two people, not six fields
```

Read `people["ada"]["city"]` strictly left to right: `people["ada"]` gives the inner dictionary; `["city"]` then looks a key up in *that*. There is no special "nested lookup" feature — it is two ordinary lookups, one after the other.

This is the shape of every JSON document you will ever load (Day 10), and it is why the next paragraph matters.

**Missing keys at two levels.** `people["zoe"]["city"]` raises `KeyError: 'zoe'` before it ever gets to `"city"`. Chaining `.get` handles the outer level:

```python
print(people.get("zoe", {}))            # {}
print(people.get("zoe", {}).get("city", "unknown"))     # unknown
```

`.get("zoe", {})` gives an empty dictionary when the person is missing, and looking `"city"` up in an empty dictionary with its own default gives `"unknown"`. Two defaults, no `if`, no error. This idiom is worth memorising — you will use it on real API data.

Loop over the outer dictionary and you get keys; the value is the inner dictionary:

```python
for key, record in people.items():
    print(key, "lives in", record["city"])
```

```
ada lives in London
grace lives in New York
```

### 7.2 A list inside a dictionary

"One key, many values" is a dictionary of lists:

```python
teams = {
    "red": ["Ada", "Grace"],
    "blue": ["Alan"],
}

print(teams["red"])             # ['Ada', 'Grace']
print(teams["red"][0])          # Ada
print(len(teams["blue"]))       # 1

teams["blue"].append("Edsger")  # mutate the list that is already in there
print(teams["blue"])            # ['Alan', 'Edsger']

teams["green"] = []             # a new, empty team
teams["green"].append("Barbara")
print(teams)
# {'red': ['Ada', 'Grace'], 'blue': ['Alan', 'Edsger'], 'green': ['Barbara']}
```

Note `teams["blue"].append(...)`. The lookup gives you the actual list stored in the dictionary — not a copy — so appending to it changes what the dictionary holds. That is Day 05's aliasing, working for you rather than against you.

Totalling per key needs two `len`s and a loop:

```python
total = 0
for members in teams.values():
    total += len(members)
print(total)                    # 4
```

Section 9 shows how to build a dictionary of lists from raw records without writing `if key in d` yourself.

---

## 8. The counting pattern

This is one of the two most useful loops in Python. Learn it until you can write it without thinking.

**The question:** how many times does each item appear?

```python
words = ["apple", "fig", "apple", "pear", "fig", "apple"]

counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

print(counts)       # {'apple': 3, 'fig': 2, 'pear': 1}
```

Four lines. The whole trick is `counts.get(word, 0)`: "the count so far, or zero if this is the first time". Then add one and store it back.

Why not `counts[word] = counts[word] + 1`? Because the first time a word appears there is no `counts[word]` to read, and you get `KeyError`. The alternatives:

```python
# Longhand, with an explicit check — correct, and three lines instead of one:
counts = {}
for word in words:
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1

# With setdefault — also correct, slightly less direct to read:
counts = {}
for word in words:
    counts.setdefault(word, 0)
    counts[word] += 1
```

All three produce the same dictionary. `counts[word] = counts.get(word, 0) + 1` is the one to have in your fingers.

It works on anything you can loop over, which includes strings:

```python
letters = {}
for character in "banana":
    letters[character] = letters.get(character, 0) + 1
print(letters)      # {'b': 1, 'a': 3, 'n': 2}
```

And it composes with everything from yesterday:

```python
text = "the cat sat on the mat the end"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)       # {'the': 3, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1, 'end': 1}
print(len(counts))  # 6      distinct words
print(sum(counts.values()))  # 8      total words
```

> **Forward reference:** the standard library has `collections.Counter`, which does this whole loop in one call and adds `most_common()` on top. It is genuinely the right tool at work, and it is Day 17 — using it needs an import, and imports are Day 11. Write the loop by hand until then; it is four lines and it is the thing `Counter` is doing for you.

### 8.1 Counting by a derived key

The thing you count does not have to be the item itself. Count by anything you can compute from it:

```python
words = ["fig", "pear", "plum", "apple", "kiwi"]

by_length = {}
for word in words:
    key = len(word)
    by_length[key] = by_length.get(key, 0) + 1
print(by_length)    # {3: 1, 4: 3, 5: 1}
```

Note the keys are integers here. Keys do not have to be strings — any immutable value works, and `3` is a perfectly good key.

---

## 9. The grouping pattern, with `setdefault`

The other essential loop. **The question:** which items belong to each category?

Counting reduced each group to a number. Grouping keeps the members.

```python
words = ["apple", "avocado", "fig", "pear", "plum", "fennel"]

groups = {}
for word in words:
    first_letter = word[0]
    groups.setdefault(first_letter, []).append(word)

print(groups)
# {'a': ['apple', 'avocado'], 'f': ['fig', 'fennel'], 'p': ['pear', 'plum']}
```

The single line that does the work is worth taking apart:

```python
groups.setdefault(first_letter, []).append(word)
```

`setdefault(key, default)` does two things:
- if the key exists, it returns the existing value and changes nothing
- if the key does not exist, it **inserts** `key: default` and returns that default

Either way you get back a list — the one that was already there, or the brand-new empty one it just inserted. `.append(word)` then adds to that list, which is the list inside the dictionary, because a lookup gives you the object and not a copy.

The longhand, so you can see there is no magic:

```python
groups = {}
for word in words:
    first_letter = word[0]
    if first_letter not in groups:
        groups[first_letter] = []       # create the empty list
    groups[first_letter].append(word)   # then append to it
```

Identical result. Use whichever you find clearer; `setdefault` is idiomatic and shorter, the `if` version is impossible to misread. What you must not write is `groups[first_letter].append(word)` on its own — `KeyError` the first time each letter appears.

> **Gotcha:** `setdefault` evaluates its default **every time**, even when the key already exists, and it is `get`'s pushier cousin: it can change the dictionary. Use `.get(key, default)` when you only want to read; use `setdefault` when you genuinely want the key created. Writing `d.setdefault(k, 0)` in a read-only report will quietly grow your dictionary with zeros for everything you looked at.

### 9.1 Grouping records

Real grouping usually starts from a list of tuples — which, from Day 05, is what `zip` produces and what a CSV row looks like:

```python
sales = [
    ("food", 12.50),
    ("tools", 40.00),
    ("food", 3.25),
    ("books", 15.00),
    ("food", 8.75),
]

# Group the amounts:
by_category = {}
for category, amount in sales:
    by_category.setdefault(category, []).append(amount)
print(by_category)
# {'food': [12.5, 3.25, 8.75], 'tools': [40.0], 'books': [15.0]}

# Or total them directly — the counting pattern with += amount instead of + 1:
totals = {}
for category, amount in sales:
    totals[category] = totals.get(category, 0) + amount
print(totals)       # {'food': 24.5, 'tools': 40.0, 'books': 15.0}
```

Two loops, four lines each, and you have gone from raw records to a report. This is the shape of a very large fraction of the data work you will ever do.

Once grouped, summarising is another short loop:

```python
averages = {}
for category, amounts in by_category.items():
    averages[category] = round(sum(amounts) / len(amounts), 2)
print(averages)     # {'food': 8.17, 'tools': 40.0, 'books': 15.0}
```

---

## 10. `max(d, key=d.get)` — the key with the biggest value

You have a dictionary of counts. Which key won?

`max(counts)` is not the answer — iterating a dictionary gives keys, so that returns the alphabetically last key:

```python
counts = {"apple": 3, "fig": 2, "pear": 1}
print(max(counts))              # pear      <- the largest KEY, not the winner
print(max(counts.values()))     # 3         <- the winning COUNT, but not whose
```

Use Day 05's `key=` and hand over the dictionary's own `get` method:

```python
print(max(counts, key=counts.get))      # apple
print(min(counts, key=counts.get))      # pear
```

Read it as: "the largest of the keys, where each key is judged by `counts.get(key)`". `max` walks the keys, calls `counts.get` on each one, and returns the key whose value came out highest. Note there are no brackets on `counts.get` — you are handing over the method itself for `max` to call, exactly as with `key=len` yesterday.

Ties go to the first one encountered in insertion order:

```python
counts = {"a": 5, "b": 5}
print(max(counts, key=counts.get))      # a
```

If ties matter, decide the rule explicitly rather than relying on insertion order. A named key function that returns a tuple gives you full control:

```python
def by_count_then_name(word: str) -> tuple[int, str]:
    """Rank key: count descending, then name ascending."""
    return (-counts[word], word)


counts = {"pear": 2, "apple": 3, "fig": 2}
print(sorted(counts, key=by_count_then_name))       # ['apple', 'fig', 'pear']
```

That is the whole "top N words" report: count with the pattern from section 8, then sort the keys with a named key function. Negating the count sorts it descending while the name still sorts ascending — `reverse=True` cannot do that, because it would flip both.

Sorting the items rather than the keys gives you pairs, which is often what you want to print:

```python
def second_item(pair: tuple[str, int]) -> int:
    """The value from a (key, value) pair."""
    return pair[1]


counts = {"apple": 3, "fig": 2, "pear": 1}
print(sorted(counts.items(), key=second_item, reverse=True))
# [('apple', 3), ('fig', 2), ('pear', 1)]
```

> **Gotcha:** `max({})` and `max({}, key={}.get)` both raise `ValueError: max() arg is an empty sequence`. An empty dictionary has no winner. If your data can be empty — it can — check `len(d) > 0` first.

---

## 11. Sets

A set is an unordered collection of **unique** items.

```python
numbers = {3, 1, 2, 3, 1}
print(numbers)              # {1, 2, 3}      duplicates gone
print(len(numbers))         # 3
print(type(numbers).__name__)   # set
```

Same curly braces as a dictionary, but items instead of `key: value` pairs. A set is essentially a dictionary that kept only the keys — which tells you what it is good at, and what it cannot do.

**Creating one:**

```python
print(set())                    # set()          the ONLY way to make an empty set
print({1, 2, 3})                # {1, 2, 3}
print(set([1, 2, 2, 3]))        # {1, 2, 3}      from a list
print(set("banana"))            # {'a', 'b', 'n'} from a string: unique characters
print(set())                    # set()
print(len({}))                  # 0     <- careful: {} is an empty DICT
```

**What a set cannot do:** there is no order, so there is no indexing and no slicing. `numbers[0]` raises `TypeError: 'set' object is not subscriptable`. There is no "first item" to ask for. If you need order, you need a list — often `sorted(my_set)`, which returns one.

**Changing a set:**

```python
tags = {"python", "beginner"}
tags.add("lists")               # add one item
print(len(tags))                # 3
tags.add("lists")               # adding an existing item does nothing at all
print(len(tags))                # 3

tags.discard("beginner")        # remove if present; silent when absent
tags.discard("nonexistent")     # no error
tags.remove("lists")            # remove; KeyError when absent
tags.remove("nonexistent")      # KeyError: 'nonexistent'
print(tags)                     # {'python'}

tags.update(["a", "b"])         # add several
tags.clear()                    # empty it
```

`add`, `discard`, `remove`, `update` and `clear` all return `None` — Day 05's rule holds for every mutating method in the language. `pop()` removes and returns *some* item, and which one is not something you should rely on.

**Membership, which is the headline feature:**

```python
allowed = {"red", "green", "blue"}
print("red" in allowed)         # True
print("pink" in allowed)        # False
```

That looks identical to `in` on a list, and behaves completely differently underneath: a list is searched item by item, a set is not searched at all. Section 15 explains how, and section 16 tells you when to care.

### 11.1 The four set operations

This is why sets exist beyond deduplication. Each operation comes in two spellings — an operator and a method — that do the same thing.

```python
a = {1, 2, 3, 4}
b = {3, 4, 5}

print(a | b)        # {1, 2, 3, 4, 5}   UNION: in either
print(a & b)        # {3, 4}            INTERSECTION: in both
print(a - b)        # {1, 2}            DIFFERENCE: in a but not b
print(b - a)        # {5}               order matters for difference
print(a ^ b)        # {1, 2, 5}         SYMMETRIC DIFFERENCE: in one, not both

print(a.union(b))                   # {1, 2, 3, 4, 5}
print(a.intersection(b))            # {3, 4}
print(a.difference(b))              # {1, 2}
print(a.symmetric_difference(b))    # {1, 2, 5}
```

All four return a **new** set and leave `a` and `b` alone. The methods accept any sequence, while the operators demand real sets:

```python
print({1, 2}.union([2, 3]))     # {1, 2, 3}    a list is fine here
print({1, 2} | [2, 3])          # TypeError: unsupported operand type(s)
```

In practice you use these to compare two collections and describe the difference in one line each:

```python
yesterday = {"ada", "grace", "alan"}
today = {"grace", "alan", "edsger"}

print(sorted(today - yesterday))    # ['edsger']         arrived
print(sorted(yesterday - today))    # ['ada']            left
print(sorted(today & yesterday))    # ['alan', 'grace']  stayed
print(sorted(today | yesterday))    # ['ada', 'alan', 'edsger', 'grace']
```

Written with lists and loops that is thirty lines of nested searching. Written with sets it is four expressions, and it is also dramatically faster.

There are comparison operators too:

```python
print({1, 2} <= {1, 2, 3})          # True    subset: every item of the left is in the right
print({1, 2, 3} >= {1, 2})          # True    superset
print({1, 2}.isdisjoint({3, 4}))    # True    no items in common
print({1, 2} == {2, 1})             # True    order is not part of a set's value
```

That last line is the difference from a list in one comparison: `[1, 2] == [2, 1]` is `False`, `{1, 2} == {2, 1}` is `True`.

> **Gotcha:** sets have no order and you must not assume the one you see. `print({3, 1, 2})` happens to show `{1, 2, 3}` for small integers, because of how integers hash, and that is a coincidence rather than a promise. For strings the display order is not even the same between two runs of your program. When you need a stable order — for a test, a report, or anything a human reads — call `sorted()` on it.

---

## 12. Deduplicating, with and without order

`set()` removes duplicates, and destroys order doing it:

```python
names = ["ada", "grace", "ada", "alan", "grace"]
print(set(names))                   # {'grace', 'ada', 'alan'}   order unreliable
print(len(set(names)))              # 3                          count is reliable
print(sorted(set(names)))           # ['ada', 'alan', 'grace']   alphabetical
```

`len(set(items))` — "how many distinct things are there?" — is a genuinely useful one-liner.

When you need duplicates removed but the **original order kept**, use `dict.fromkeys`:

```python
names = ["ada", "grace", "ada", "alan", "grace"]
print(list(dict.fromkeys(names)))   # ['ada', 'grace', 'alan']
```

Why does that work? `dict.fromkeys(names)` builds a dictionary whose keys are the names, each mapped to `None`. Keys are unique, so duplicates collapse; dictionaries keep insertion order, so first-seen order survives. `list(...)` then takes the keys back out as a list. It is a two-birds trick and it is the standard idiom.

```python
print(dict.fromkeys(names))         # {'ada': None, 'grace': None, 'alan': None}
```

The longhand, which does the same thing and shows what is happening:

```python
seen = set()
unique = []
for name in names:
    if name not in seen:
        unique.append(name)
        seen.add(name)
print(unique)                       # ['ada', 'grace', 'alan']
```

That loop is worth being able to write, because it generalises: swap the condition and you have "first occurrence of each category", "first error per file", and so on. Note the shape — a set to remember what has been seen, a list to keep the order. Using a list for `seen` instead would work and would get slower as the data grew.

---

## 13. Hashability: why a list cannot be a key

Try it:

```python
d = {}
d[[1, 2]] = "x"         # TypeError: unhashable type: 'list'
d[(1, 2)] = "x"         # fine
print(d)                # {(1, 2): 'x'}

print({1, 2, 3})        # fine
print({[1], [2]})       # TypeError: unhashable type: 'list'
print({(1, 2), (3, 4)}) # {(1, 2), (3, 4)}    tuples are fine
```

The rule: **dictionary keys and set members must be hashable, and hashable means immutable** (in practice, and with one caveat below).

To *hash* a value is to run it through a function that turns it into an integer:

```python
print(hash("ada"))      # some integer — a different one each time you run Python
print(hash((1, 2)))     # some integer — stable
print(hash(42))         # 42
print(hash([1, 2]))     # TypeError: unhashable type: 'list'
```

A dictionary uses that integer to decide **where to store** the pair — which is section 15's subject. Everything follows from that one sentence.

Now imagine lists were allowed as keys:

```python
key = [1, 2]
d = {key: "x"}          # stored in the slot for hash([1, 2])
key.append(3)           # the key is now [1, 2, 3]
d[[1, 2, 3]]            # looks in the slot for hash([1, 2, 3]) — nothing there
```

The entry would be filed under an address that no longer matches its own contents. It would be in the dictionary, unreachable, and `len(d)` would still say 1. Rather than allow that, Python refuses at the door: mutable types do not provide a hash at all.

So:

| Type | Hashable? | Can be a dict key or set member? |
|---|---|---|
| `int`, `float`, `bool`, `None` | yes | yes |
| `str` | yes | yes |
| `tuple` of hashable things | yes | yes |
| `tuple` containing a list | **no** | no |
| `list` | no | no |
| `dict` | no | no |
| `set` | no | no (`frozenset` is the hashable version) |

The tuple caveat, following straight from Day 05 section 12.5:

```python
print(hash((1, 2)))            # fine
print(hash((1, [2])))          # TypeError: unhashable type: 'list'
```

A tuple is hashable only if everything inside it is. The tuple's own slots are fixed, but a list inside it could still change, so the same filing problem returns and Python refuses again.

This is where the tuple earns its place in the language. Composite keys are common and natural:

```python
grid = {}
grid[(0, 0)] = "start"
grid[(2, 3)] = "treasure"
print(grid[(2, 3)])             # treasure

monthly = {}
monthly[(2024, 3)] = 1500       # (year, month)
print(monthly[(2024, 3)])       # 1500
```

A `(row, column)` cell, a `(year, month)` period, a `(latitude, longitude)` point — one key, several parts, no string-mashing.

> **Gotcha:** `1`, `1.0` and `True` all hash the same and compare equal, so they are the *same key*. `{1: "a", 1.0: "b", True: "c"}` is a one-item dictionary holding `{1: 'c'}`. And `{1, True}` has one member. This is rarely what anyone wants; it is a good reason to keep key types uniform.

---

## 14. Why lookup does not get slower

Here is the property that makes dictionaries and sets worth learning properly, in plain language.

**Finding something in a list means looking.** `"zoe" in names` starts at the front and compares item by item until it finds a match or runs out. On average that is half the list; in the worst case (absent) it is all of it. Ten times more names, ten times more work.

**Finding something in a dictionary means calculating.** Python hashes your key — one quick calculation on the key itself, which does not care how many other keys exist — and that number tells it which slot to look in. It goes straight there. One hash, one jump, one comparison to confirm. Ten times more keys does not mean ten times more work; it means the same work.

The consequence, made concrete. Two programs asking "which of these ten thousand names are on the allowed list of ten thousand?":

```python
# With a list: for each name, scan the allowed list.
# 10,000 names x ~5,000 comparisons each = ~50,000,000 comparisons.

# With a set: for each name, hash it and jump.
# 10,000 names x 1 lookup each = 10,000 lookups.
```

Same answer. Thousands of times less work. Turn ten thousand into a million and the list version stops being viable while the set version is still instant.

This is why "put it in a set first" is a reflex among experienced Python programmers:

```python
allowed_list = ["red", "green", "blue"]      # fine for three
allowed = set(allowed_list)                  # do this once, before the loop
for colour in ["red", "pink", "blue"]:
    print(colour, colour in allowed)
```

```
red True
pink False
blue True
```

Building the set costs one pass over the data. If you are going to test membership more than a handful of times, that pass pays for itself many times over.

Three honest caveats, so you do not over-apply this:

- **The keys must be hashable.** Lists cannot go in a set. Convert to tuples if you need to.
- **Order is lost.** A set has none; a dictionary keeps insertion order and nothing else.
- **It is not free.** A set of a million strings uses noticeably more memory than a list of the same strings, and for a handful of items the difference in speed is unmeasurable. Reach for a set when the collection is big, or when you are testing membership repeatedly, or when uniqueness is the actual point.

The formal names for this are "O(n) versus O(1)" — linear time versus constant time — and you will hear them in interviews. The idea underneath is the whole content: **looking through everything, versus calculating where to look.**

---

## 15. Choosing between list, tuple, dict and set

| | list | tuple | dict | set |
|---|---|---|---|---|
| Written | `[1, 2]` | `(1, 2)` | `{"a": 1}` | `{1, 2}` |
| Empty | `[]` | `()` | `{}` | `set()` |
| Ordered | yes | yes | insertion order | **no** |
| Duplicates | yes | yes | keys no, values yes | **no** |
| Indexable | `x[0]` | `x[0]` | by key: `x["a"]` | **no** |
| Changeable | yes | **no** | yes | yes |
| Can be a dict key | no | yes (if contents are) | no | no |
| Membership test | slow (scans) | slow (scans) | **fast** (keys) | **fast** |
| Reach for it when | a sequence you will add to, sort, or index | a fixed record of parts; a composite key | you look values up *by* something | uniqueness or fast membership |

Worked decisions, which is how this actually gets used:

- **Scores for three students, need the average** — list of numbers. You are totalling, not looking anything up.
- **Score for a named student** — dict, `{"Ada": 88}`. The question has "by name" in it.
- **A point on a map** — tuple, `(51.5, -0.1)`. Fixed parts, different roles, and you may want it as a key.
- **Which user IDs have logged in today** — set. Uniqueness is the point and you will test membership.
- **Words seen so far, in order, no repeats** — `dict.fromkeys` on a list, or a list plus a `seen` set.
- **Each team's members** — dict of lists, `{"red": ["Ada"]}`.
- **A record loaded from JSON** — dict of dicts, however it came.
- **Counting anything** — dict, built with `counts.get(k, 0) + 1`.
- **A CSV row** — list while you are processing the file, tuple once it is a fixed record.

If you cannot decide, ask what the *question* is. "What is at position 3?" is a list. "What is X's Y?" is a dict. "Have I seen this?" is a set. "What are the parts of this one thing?" is a tuple.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `d["missing"]` | `KeyError: 'missing'` | `d.get("missing", default)`, or check `in` first |
| `d[k] += 1` on a new key | `KeyError` | `d[k] = d.get(k, 0) + 1` |
| `d[k].append(x)` on a new key | `KeyError` | `d.setdefault(k, []).append(x)` |
| Expecting `.get` to create the key | the dictionary is unchanged | use `setdefault` when you want it inserted |
| `d = d.update(other)` | `d` becomes `None` | `d.update(other)`, or `d = d \| other` |
| `for k, v in d:` | `ValueError: too many values to unpack` | `for k, v in d.items():` |
| `value in d` to find a value | `False` — `in` tests keys | `value in d.values()` |
| `d.keys()[0]` | `TypeError: 'dict_keys' object is not subscriptable` | `list(d.keys())[0]` |
| Expecting `.keys()` to be a snapshot | it reflects later changes | `list(d.keys())` |
| Adding/deleting keys while looping | `RuntimeError: dictionary changed size during iteration` | collect keys into a list, change afterwards |
| `max(d)` for the top value | the largest **key** | `max(d, key=d.get)` |
| `max({})` | `ValueError: max() arg is an empty sequence` | check `len(d) > 0` first |
| `{}` for an empty set | it is an empty dict | `set()` |
| `my_set[0]` | `TypeError: 'set' object is not subscriptable` | sets have no order; use `sorted(my_set)` |
| Relying on set display order | different order between runs | `sorted()` before printing or comparing |
| `set(items)` to dedupe in order | order lost | `list(dict.fromkeys(items))` |
| `{[1], [2]}` or `d[[1, 2]]` | `TypeError: unhashable type: 'list'` | use tuples: `d[(1, 2)]` |
| `set_a \| [1, 2]` (a list) | `TypeError: unsupported operand type(s)` | `set_a.union([1, 2])` |
| `.remove(x)` on a missing set member | `KeyError` | `.discard(x)` |
| `in` on a huge list inside a loop | your program appears to hang | build a `set` once, before the loop |
| Two dicts with the same key twice | the second value silently wins | keys are unique; check your source data |

---

## Mental model

A list is a **numbered shelf**: to find something you walk along it. A dictionary is a **cloakroom with a ticket machine**.

```
   You hand over a coat and a NAME.  The machine hashes the name
   into a number, and that number is the peg it hangs on.

     "Ada"  --hash-->  7  -->  peg 7  holds  88
     "Grace"--hash--> 42  -->  peg 42 holds  95
     "Alan" --hash--> 13  -->  peg 13 holds  79

   Getting it back:   hash("Grace") is 42.  Go to peg 42.  Done.
                      Not "check every peg" — ONE calculation, ONE jump.

   Which is why:
     * lookup does not slow down as the cloakroom grows   (section 14)
     * a key must be hashable, so the number can be computed at all
     * a key must not CHANGE after it is filed, or the ticket
       would no longer match the peg                      (section 13)
     * there is no "peg 3" question you can ask — you ask by NAME,
       never by position
```

And a set is the same cloakroom **with no coats**: it keeps only the tickets.

```
   dict:  { "ada": 88 , "grace": 95 }     keys -> values
   set:   { "ada"     , "grace"      }    keys only

   Everything true of dict keys is true of set members:
     unique, hashable, unordered, fast to find.

   The four comparisons, in one picture:

        a = {1,2,3,4}          b = {3,4,5}

              +-----------+-----------+---------+
              |   1   2   |   3   4   |    5    |
              +-----------+-----------+---------+
               only in a    in both     only in b

        a | b  = everything above          {1,2,3,4,5}
        a & b  = the middle block          {3,4}
        a - b  = the left block            {1,2}
        a ^ b  = both ends, not middle     {1,2,5}
```

Three sentences to carry away:

- **A list answers "what is at position 3?". A dictionary answers "what is X's Y?".** Choosing the wrong one is why some programs are ten lines and some are a hundred.
- **The two loops that do most of the work** are `d[k] = d.get(k, 0) + 1` (count) and `d.setdefault(k, []).append(v)` (group). Everything else today is support for those.
- **Hashing is the whole mechanism.** It explains the speed, the immutable-key rule, the lack of order, and the uniqueness — one idea, four consequences.

---

## Practice

1. Run the demo and read every line of output against the code that produced it:

   ```bash
   python course/week1/day06_dicts_and_sets/examples.py
   ```

2. Fifteen minutes in the REPL, predicting before you press Enter:

   ```bash
   python
   ```

   Try: `{"a": 1}["b"]`, `{"a": 1}.get("b")`, `{"a": 1}.get("b", 0)`, `"a" in {"a": 1}`, `1 in {"a": 1}`, `len({"a": 1, "a": 2})`, `list({"a": 1}.items())`, `type({}).__name__`, `type(set()).__name__`, `{1, 2, 2, 3}`, `set("banana")`, `{1,2,3} & {2,3,4}`, `{1,2,3} - {2}`, `{1,2} ^ {2,3}`, `sorted({"b": 1, "a": 2})`, `max({"a": 1, "b": 9}, key={"a": 1, "b": 9}.get)`, `list(dict.fromkeys(["b","a","b"]))`, `{1: "a", True: "b"}`, and `hash([1])`.

   Then predict this one before running it:

   ```python
   d = {"a": 1}
   keys = d.keys()
   d["b"] = 2
   keys
   ```

   If you predicted `dict_keys(['a'])`, re-read section 5 — views are live.

3. Open `course/week1/day06_dicts_and_sets/exercises.py` and work top to bottom. Exercises 3, 5 and 6 are the counting and grouping patterns; if you can write those two loops from memory afterwards, today has done its job.

4. Grade yourself from the course root:

   ```bash
   python check.py day06
   python check.py day06 -v      # full failure detail
   ```

5. Extra rep, no tests attached: take a paragraph of text and print the five most common words, one per line, as `the             12`, using the counting pattern, a named key function that sorts by count descending and word ascending, and an f-string format spec from Day 02. Then print how many *distinct* words there were, and the words that appear exactly once, alphabetically. That is a real text-analysis tool, built out of two loops and a sort.

---

## Recall check

1. `d = {"a": 1}`. What do `d["b"]`, `d.get("b")` and `d.get("b", 0)` each do? When should you prefer the first?
2. Why does `counts[word] += 1` fail on a word's first appearance, and what is the standard one-line fix?
3. What does `d.setdefault(k, [])` do that `d.get(k, [])` does not?
4. What does `key in d` test — keys, values, or both? How do you test for a value?
5. `d = {"a": 1}`, then `view = d.keys()`, then `d["b"] = 2`. What is in `view`, and how would you have taken a snapshot instead?
6. Write the loop that turns `["a", "b", "a"]` into `{"a": 2, "b": 1}`, and the loop that turns `[("x", 1), ("y", 2), ("x", 3)]` into `{"x": [1, 3], "y": [2]}`.
7. `counts = {"apple": 3, "fig": 2}`. What do `max(counts)`, `max(counts.values())` and `max(counts, key=counts.get)` each give you?
8. How do you write an empty set, and what is `{}`?
9. `a = {1, 2, 3}` and `b = {3, 4}`. Give `a | b`, `a & b`, `a - b`, `b - a`, `a ^ b`.
10. How do you remove duplicates from a list while keeping the original order, and why does that work?
11. Why can a tuple be a dictionary key when a list cannot? Give an example of a tuple that still cannot be one.
12. In one or two sentences and no jargon: why is looking a key up in a dictionary of ten million items no slower than in a dictionary of ten?

<details>
<summary>Answers</summary>

1. `d["b"]` raises `KeyError: 'b'`. `d.get("b")` returns `None`. `d.get("b", 0)` returns `0`. Prefer `d["b"]` when a missing key means your program or your data is broken — you want the error at the line that asked, not a `None` that fails somewhere else later.
2. Because `+=` reads the old value first, and on the first appearance there is no old value to read, so the read raises `KeyError`. The fix: `counts[word] = counts.get(word, 0) + 1`.
3. `setdefault` **inserts** `k: []` into the dictionary when `k` is missing, and returns the value that is now stored there — so appending to what it returns changes the dictionary. `get` returns a default without storing anything, so appending to that default modifies a throwaway list and the dictionary never sees it.
4. `key in d` tests keys only. For a value, use `value in d.values()`. (That scans the values one by one and is not fast — if you need it often, you probably want a second dictionary keyed the other way round.)
5. `view` contains both keys: `dict_keys(['a', 'b'])`. Views are live windows onto the dictionary, not copies. For a snapshot, `list(d.keys())`.
6. Counting: `counts = {}` then `for item in items: counts[item] = counts.get(item, 0) + 1`. Grouping: `groups = {}` then `for key, value in pairs: groups.setdefault(key, []).append(value)`.
7. `max(counts)` gives `"fig"` — the largest *key* alphabetically, because iterating a dictionary gives keys. `max(counts.values())` gives `3` — the winning count, without saying whose. `max(counts, key=counts.get)` gives `"apple"` — the key with the largest value, which is the question you meant.
8. `set()`. `{}` is an empty **dictionary** — there is no literal for an empty set, because the braces were taken first.
9. `{1, 2, 3, 4}`, `{3}`, `{1, 2}`, `{4}`, `{1, 2, 4}`.
10. `list(dict.fromkeys(items))`. `dict.fromkeys` builds a dictionary using the items as keys: keys are unique, so duplicates collapse, and dictionaries preserve insertion order, so the first-seen order survives. `list()` then extracts the keys in that order. (The longhand is a `seen` set plus a result list.)
11. A key must be hashable, and hashable in practice means immutable: the dictionary computes a number from the key to decide where to store the pair, so a key that changed after filing would be unreachable. A tuple cannot change, so it can be hashed; a list can, so it cannot. The exception is a tuple that *contains* something mutable — `(1, [2])` is not hashable, because the list inside it could still change.
12. Because it does not look through the items at all. It performs one calculation on the key itself to work out which slot the value lives in, then goes straight to that slot. The calculation depends on the key, not on how many other keys exist, so the size of the dictionary does not change the work.

</details>
