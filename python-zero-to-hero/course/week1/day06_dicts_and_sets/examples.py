"""Day 06 — Dictionaries and Sets: runnable demonstrations.

Run me from the course root:

    python course/week1/day06_dicts_and_sets/examples.py

Every section number matches a section in LESSON.md. Predict each result before
you read it. The interesting lines are the ones where you were wrong.

Nothing here asks for input, touches the network, or writes a file. Lines that
would raise an error are printed as text rather than executed, so the whole file
runs top to bottom with zero errors.

One housekeeping note: sets have no order, and the order Python happens to
display for a set of strings can differ between runs. Wherever that matters
below, the output is passed through sorted() first so that what you see is
stable. That is exactly what you should do in your own code.
"""


# ---------------------------------------------------------------------------
# 1. The problem a dictionary solves
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. Two parallel lists, versus one dictionary")
print("=" * 70)

names = ["Ada", "Grace", "Alan"]
scores = [88, 95, 79]

# Fragile: find the position first, then use it in the OTHER list.
position = names.index("Grace")
print("names.index('Grace') ->", position, "-> scores[position] ->", scores[position])
print("Sort one list and forget the other and every score is wrong. Silently.")

# Direct: the association is the data structure.
score_by_name = {"Ada": 88, "Grace": 95, "Alan": 79}
print("score_by_name['Grace'] ->", score_by_name["Grace"], " <- the code is the question")


# ---------------------------------------------------------------------------
# 2. Making a dictionary
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. Making dictionaries")
print("=" * 70)

scores = {"Ada": 88, "Grace": 95, "Alan": 79}
empty = {}
print("scores       ->", scores)
print("len(scores)  ->", len(scores), " <- pairs, not keys plus values")
print("empty        ->", empty, "of length", len(empty))
print("type(scores) ->", type(scores).__name__)

# Duplicate keys: the last one silently wins.
print("{'a': 1, 'a': 2} ->", {"a": 1, "a": 2}, " <- keys are unique")

# Values can be anything, including other collections.
person = {
    "name": "Ada",
    "age": 36,
    "scores": [88, 95],
    "address": {"city": "London"},
    "active": True,
}
print("person['scores']  ->", person["scores"])
print("person['address'] ->", person["address"])

# The other ways to build one.
print("dict(a=1, b=2)                    ->", dict(a=1, b=2))
print("dict([('Ada', 88), ('Grace', 95)])->", dict([("Ada", 88), ("Grace", 95)]))
print("dict(zip(names, [88, 95, 79]))    ->", dict(zip(names, [88, 95, 79])))
print("   ^ that is the fix for section 1: zip them once, while they are in step")
print("dict.fromkeys(['a', 'b'], 0)      ->", dict.fromkeys(["a", "b"], 0))
print("{} is an empty", type({}).__name__, "- an empty set is set(), not {}")


# ---------------------------------------------------------------------------
# 3. Lookup, KeyError, and .get
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Looking things up (and what happens when they are missing)")
print("=" * 70)

scores = {"Ada": 88, "Grace": 95}
print("scores['Ada']       ->", scores["Ada"])
print("scores['Nobody']    ->  KeyError: 'Nobody'")

# 1. Check first. `in` on a dictionary tests KEYS.
print("'Ada' in scores     ->", "Ada" in scores)
print("'Nobody' in scores  ->", "Nobody" in scores)
print("88 in scores        ->", 88 in scores, " <- 88 is a VALUE, not a key")
print("88 in scores.values() ->", 88 in scores.values())

if "Nobody" in scores:
    print("found it")
else:
    print("guarded lookup -> no score recorded")

# 2 and 3. .get, with and without a default.
print("scores.get('Ada')        ->", scores.get("Ada"))
print("scores.get('Nobody')     ->", scores.get("Nobody"), " <- None, no error")
print("scores.get('Nobody', 0)  ->", scores.get("Nobody", 0), " <- your default")
print("scores.get('Nobody','n/a')->", scores.get("Nobody", "n/a"))
print("scores after all that    ->", scores, " <- .get NEVER adds a key")
print("Use d[key] when a missing key is a bug you want to hear about;")
print("use d.get(key, default) when absence is normal.")


# ---------------------------------------------------------------------------
# 4. Adding, updating and deleting
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Adding, updating, deleting")
print("=" * 70)

scores = {"Ada": 88}
scores["Grace"] = 95  # new key -> added
print("scores['Grace'] = 95 ->", scores)
scores["Ada"] = 100  # existing key -> replaced
print("scores['Ada'] = 100  ->", scores, " <- same syntax for add and update")
print("A list will NOT grow by assignment (IndexError); a dictionary will.")
scores["Adaa"] = 88
print("a typo'd key just creates a new entry ->", scores)
del scores["Adaa"]

scores = {"Ada": 88}
scores["Ada"] += 10
print("scores['Ada'] += 10  ->", scores)
print("scores['Nobody'] += 1 ->  KeyError: nothing to add to")
print("   ^ this is why the counting pattern is written the way it is")

settings = {"colour": "red", "size": 10}
settings.update({"size": 12, "font": "mono"})
print("settings.update({...}) ->", settings, " <- in place, returns None")

defaults = {"colour": "red", "size": 10}
custom = {"size": 12}
print("defaults | custom ->", defaults | custom, " <- a NEW merged dict")
print("defaults          ->", defaults, " <- untouched; right-hand side wins")

scores = {"Ada": 88, "Grace": 95, "Alan": 79}
del scores["Alan"]
print("del scores['Alan']    ->", scores)
removed = scores.pop("Grace")
print("scores.pop('Grace')   -> returned", removed, "| scores", scores)
print("scores.pop('Nobody', 0)->", scores.pop("Nobody", 0), " <- a default makes pop safe")
print("scores.pop('Nobody')  ->  KeyError")
print("del scores['Nobody']  ->  KeyError")
scores.clear()
print("scores.clear()        ->", scores)


# ---------------------------------------------------------------------------
# 5. keys, values, items - and why they are LIVE
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. keys / values / items are live views, not lists")
print("=" * 70)

scores = {"Ada": 88, "Grace": 95}
print("scores.keys()   ->", scores.keys())
print("scores.values() ->", scores.values())
print("scores.items()  ->", scores.items())
print("Note the type names: dict_keys, not list.")

live = {"Ada": 88}
keys_view = live.keys()
print("view before adding a key ->", keys_view)
live["Grace"] = 95
print("view after  adding a key ->", keys_view, " <- it changed too. Nothing recomputed.")

snapshot = list(live.keys())  # a real list, made now
live["Alan"] = 79
print("list(live.keys()) taken earlier ->", snapshot, " <- a snapshot, unaffected")
print("live.keys() now                 ->", live.keys())

scores = {"Ada": 88, "Grace": 95, "Alan": 79}
print("len(scores.keys())      ->", len(scores.keys()))
print("'Ada' in scores.keys()  ->", "Ada" in scores.keys(), " <- same as 'Ada' in scores")
print("sorted(scores.keys())   ->", sorted(scores.keys()))
print("sum(scores.values())    ->", sum(scores.values()), " <- the total")
print("max(scores.values())    ->", max(scores.values()), " <- the peak, but not WHOSE")
print("list(scores.items())[0] ->", list(scores.items())[0])
print("scores.keys()[0]        ->  TypeError: 'dict_keys' object is not subscriptable")
print("Adding or deleting keys WHILE looping ->")
print("   RuntimeError: dictionary changed size during iteration")
print("   Collect the keys into a list first, then change the dict afterwards.")


# ---------------------------------------------------------------------------
# 6. Iterating
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Looping over a dictionary")
print("=" * 70)

scores = {"Ada": 88, "Grace": 95}

print("for name in scores:            (keys)")
for name in scores:
    print("   ", name)

print("for score in scores.values():  (values)")
for score in scores.values():
    print("   ", score)

print("for name, score in scores.items():  (both - the standard loop)")
for name, score in scores.items():
    print(f"    {name} scored {score}")

unsorted_scores = {"Grace": 95, "Ada": 88, "Alan": 79}
print("for name in sorted(scores):    (keys, alphabetically)")
for name in sorted(unsorted_scores):
    print("   ", name, unsorted_scores[name])

print("Forgetting .items(): `for k, v in scores:` ->")
print("   ValueError: too many values to unpack (expected 2)")


# ---------------------------------------------------------------------------
# 7. Nested dictionaries and dictionaries of lists
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. Dictionaries inside dictionaries, lists inside dictionaries")
print("=" * 70)

people = {
    "ada": {"name": "Ada Lovelace", "age": 36, "city": "London"},
    "grace": {"name": "Grace Hopper", "age": 45, "city": "New York"},
}
print("people['ada']         ->", people["ada"])
print("people['ada']['city'] ->", people["ada"]["city"], " <- two ordinary lookups")
print("len(people)           ->", len(people), " <- two people, not six fields")
print("This is the shape of every JSON document you will load on Day 10.")

print("people['zoe']['city']  ->  KeyError: 'zoe' (it never reaches 'city')")
print("people.get('zoe', {})  ->", people.get("zoe", {}))
print("people.get('zoe', {}).get('city', 'unknown') ->",
      people.get("zoe", {}).get("city", "unknown"), " <- memorise this idiom")

for key, record in people.items():
    print("   ", key, "lives in", record["city"])

teams = {"red": ["Ada", "Grace"], "blue": ["Alan"]}
print()
print("teams['red']    ->", teams["red"])
print("teams['red'][0] ->", teams["red"][0])
teams["blue"].append("Edsger")
print("teams['blue'].append('Edsger') ->", teams["blue"])
print("   ^ the lookup gave the ACTUAL list, not a copy: Day 05 aliasing at work")
teams["green"] = []
teams["green"].append("Barbara")
print("teams ->", teams)

total = 0
for members in teams.values():
    total += len(members)
print("total members across all teams ->", total)


# ---------------------------------------------------------------------------
# 8. The counting pattern
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. The counting pattern (learn this by heart)")
print("=" * 70)

words = ["apple", "fig", "apple", "pear", "fig", "apple"]

counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
print("words  ->", words)
print("counts ->", counts)
print("The whole trick: counts.get(word, 0) is 'the count so far, or zero'.")

# The same thing, written out longhand.
longhand = {}
for word in words:
    if word in longhand:
        longhand[word] = longhand[word] + 1
    else:
        longhand[word] = 1
print("longhand with if/else ->", longhand, " <- identical result, three lines")

with_setdefault = {}
for word in words:
    with_setdefault.setdefault(word, 0)
    with_setdefault[word] += 1
print("with setdefault       ->", with_setdefault, " <- also identical")

# It works on anything you can loop over.
letters = {}
for character in "banana":
    letters[character] = letters.get(character, 0) + 1
print("counting 'banana'     ->", letters)

text = "the cat sat on the mat the end"
word_counts = {}
for word in text.split():
    word_counts[word] = word_counts.get(word, 0) + 1
print("counting a sentence   ->", word_counts)
print("len(word_counts)          ->", len(word_counts), " <- distinct words")
print("sum(word_counts.values()) ->", sum(word_counts.values()), " <- total words")
print("Forward reference: collections.Counter does this in one call and is")
print("Day 17. Reaching for it needs Day 11 machinery, so write the loop.")

# Count by a DERIVED key.
fruit = ["fig", "pear", "plum", "apple", "kiwi"]
by_length = {}
for word in fruit:
    key = len(word)
    by_length[key] = by_length.get(key, 0) + 1
print("counting by len(word) ->", by_length, " <- integer keys are fine")


# ---------------------------------------------------------------------------
# 9. The grouping pattern, with setdefault
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. The grouping pattern (learn this one too)")
print("=" * 70)

words = ["apple", "avocado", "fig", "pear", "plum", "fennel"]

groups = {}
for word in words:
    first_letter = word[0]
    groups.setdefault(first_letter, []).append(word)
print("grouped by first letter ->", groups)
print("setdefault(k, []) returns the list that is now stored under k -")
print("either the one already there, or the empty one it just inserted.")

longhand_groups = {}
for word in words:
    first_letter = word[0]
    if first_letter not in longhand_groups:
        longhand_groups[first_letter] = []
    longhand_groups[first_letter].append(word)
print("the same, longhand      ->", longhand_groups)
print("What you must NOT write: groups[letter].append(word) on its own ->")
print("   KeyError the first time each letter appears.")

sales = [
    ("food", 12.50),
    ("tools", 40.00),
    ("food", 3.25),
    ("books", 15.00),
    ("food", 8.75),
]

by_category = {}
for category, amount in sales:
    by_category.setdefault(category, []).append(amount)
print()
print("grouped amounts ->", by_category)

totals = {}
for category, amount in sales:
    totals[category] = totals.get(category, 0) + amount
print("totals          ->", totals, " <- counting pattern with += amount")

averages = {}
for category, amounts in by_category.items():
    averages[category] = round(sum(amounts) / len(amounts), 2)
print("averages        ->", averages)
print("Two four-line loops take you from raw records to a report.")


# ---------------------------------------------------------------------------
# 10. max(d, key=d.get)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("10. Which key has the biggest value?")
print("=" * 70)

counts = {"apple": 3, "fig": 2, "pear": 1}
print("counts                    ->", counts)
print("max(counts)               ->", max(counts), " <- the largest KEY. Not the winner.")
print("max(counts.values())      ->", max(counts.values()), " <- the count, but not whose")
print("max(counts, key=counts.get)->", max(counts, key=counts.get), " <- the question you meant")
print("min(counts, key=counts.get)->", min(counts, key=counts.get))
print("No brackets on counts.get: you hand over the method for max to call.")

tied = {"a": 5, "b": 5}
print("ties go to the first key inserted ->", max(tied, key=tied.get))
print("max({}) ->  ValueError: max() arg is an empty sequence")


# Full control over ties needs a named key function (`def` is Day 08).
ranking = {"pear": 2, "apple": 3, "fig": 2}


def by_count_then_name(word: str) -> tuple[int, str]:
    """Rank key: count descending, then name ascending."""
    return (-ranking[word], word)


def second_item(pair: tuple[str, int]) -> int:
    """The value from a (key, value) pair."""
    return pair[1]


print("sorted(ranking, key=by_count_then_name) ->",
      sorted(ranking, key=by_count_then_name))
print("   negating the count sorts it DOWN while the name still sorts UP;")
print("   reverse=True cannot do that, because it would flip both")
print("sorted(counts.items(), key=second_item, reverse=True) ->",
      sorted(counts.items(), key=second_item, reverse=True))


# ---------------------------------------------------------------------------
# 11. Sets
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("11. Sets: unordered, unique")
print("=" * 70)

numbers = {3, 1, 2, 3, 1}
print("{3, 1, 2, 3, 1} ->", numbers, "of length", len(numbers), " <- duplicates gone")
print("type            ->", type(numbers).__name__)
print("set()           ->", set(), " <- the ONLY way to write an empty set")
print("set([1, 2, 2, 3])->", set([1, 2, 2, 3]))
print("sorted(set('banana')) ->", sorted(set("banana")), " <- unique characters")
print("A set is a dictionary that kept only the keys.")
print("numbers[0] ->  TypeError: 'set' object is not subscriptable (no order)")

tags = {"python", "beginner"}
tags.add("lists")
print("after add('lists')      -> length", len(tags))
tags.add("lists")
print("after add('lists') again -> length", len(tags), " <- adding a duplicate does nothing")
tags.discard("beginner")
tags.discard("nonexistent")  # silent
print("after two discards      ->", sorted(tags))
tags.remove("lists")
print("after remove('lists')   ->", sorted(tags))
print("remove() on a missing member -> KeyError; discard() stays silent")

allowed = {"red", "green", "blue"}
print("'red' in allowed  ->", "red" in allowed)
print("'pink' in allowed ->", "pink" in allowed)

# The four operations.
print()
a = {1, 2, 3, 4}
b = {3, 4, 5}
print("a =", a, " b =", b)
print("a | b (union)                ->", a | b, " <- in either")
print("a & b (intersection)         ->", a & b, " <- in both")
print("a - b (difference)           ->", a - b, " <- in a, not b")
print("b - a (difference, reversed) ->", b - a, " <- order matters")
print("a ^ b (symmetric difference) ->", a ^ b, " <- in one, not both")
print("a.union(b)                   ->", a.union(b))
print("a.intersection(b)            ->", a.intersection(b))
print("a.difference(b)              ->", a.difference(b))
print("a.symmetric_difference(b)    ->", a.symmetric_difference(b))
print("a and b are untouched:", a, b)
print("{1, 2}.union([2, 3]) ->", {1, 2}.union([2, 3]), " <- methods accept lists")
print("{1, 2} | [2, 3]      ->  TypeError: operators need real sets")

yesterday = {"ada", "grace", "alan"}
today = {"grace", "alan", "edsger"}
print()
print("who arrived (today - yesterday) ->", sorted(today - yesterday))
print("who left    (yesterday - today) ->", sorted(yesterday - today))
print("who stayed  (today & yesterday) ->", sorted(today & yesterday))
print("everyone    (today | yesterday) ->", sorted(today | yesterday))
print("With lists and loops that is thirty lines of nested searching.")

print()
print("{1, 2} <= {1, 2, 3}          ->", {1, 2} <= {1, 2, 3}, " <- subset")
print("{1, 2, 3} >= {1, 2}          ->", {1, 2, 3} >= {1, 2}, " <- superset")
print("{1, 2}.isdisjoint({3, 4})    ->", {1, 2}.isdisjoint({3, 4}))
print("{1, 2} == {2, 1}             ->", {1, 2} == {2, 1}, " <- order is not part of it")
print("[1, 2] == [2, 1]             ->", [1, 2] == [2, 1], " <- for a list it is")
print("Never rely on the order a set prints in. Call sorted() first.")


# ---------------------------------------------------------------------------
# 12. Deduplicating, with and without order
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("12. Removing duplicates")
print("=" * 70)

names = ["ada", "grace", "ada", "alan", "grace"]
print("names                 ->", names)
print("len(set(names))       ->", len(set(names)), " <- how many distinct? reliable")
print("sorted(set(names))    ->", sorted(set(names)), " <- unique, alphabetical")
print("set(names)            -> order unreliable, so it is not printed raw here")
print("list(dict.fromkeys(names)) ->", list(dict.fromkeys(names)),
      " <- unique, ORIGINAL order")
print("dict.fromkeys(names)  ->", dict.fromkeys(names))
print("   keys are unique (duplicates collapse) and dicts keep insertion")
print("   order (first-seen order survives). list() takes the keys back out.")

seen = set()
unique = []
for name in names:
    if name not in seen:
        unique.append(name)
        seen.add(name)
print("the longhand version  ->", unique)
print("   a set to remember what has been seen, a list to keep the order")


# ---------------------------------------------------------------------------
# 13. Hashability
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("13. Why a list cannot be a key")
print("=" * 70)

d = {}
d[(1, 2)] = "x"
print("d[(1, 2)] = 'x'  ->", d, " <- a tuple key is fine")
print("d[[1, 2]] = 'x'  ->  TypeError: unhashable type: 'list'")
print("{(1, 2), (3, 4)} ->", {(1, 2), (3, 4)}, " <- tuples in a set: fine")
print("{[1], [2]}       ->  TypeError: unhashable type: 'list'")

print()
print("To hash a value is to turn it into an integer:")
print("  hash(42)     ->", hash(42))
print("  hash((1, 2)) ->", hash((1, 2)), " <- an integer (stable across runs)")
print("  hash('ada')  -> an integer, DIFFERENT every time you start Python")
print("  hash([1, 2]) ->  TypeError: unhashable type: 'list'")
print("The dictionary uses that integer to decide WHERE to store the pair.")
print("If lists were allowed as keys:")
print("  key = [1, 2]; d = {key: 'x'}      filed under hash([1, 2])")
print("  key.append(3)                     the key is now [1, 2, 3]")
print("  d[[1, 2, 3]]                      looks in a different slot: nothing there")
print("The entry would be present, unreachable, and uncountable. Python")
print("refuses at the door instead: mutable types provide no hash at all.")

print()
print("hash((1, 2))   -> fine")
print("hash((1, [2])) ->  TypeError: a tuple is hashable only if its contents are")

grid = {}
grid[(0, 0)] = "start"
grid[(2, 3)] = "treasure"
print("composite keys are the point:", grid)
print("grid[(2, 3)] ->", grid[(2, 3)])
monthly = {(2024, 3): 1500, (2024, 4): 1800}
print("monthly[(2024, 3)] ->", monthly[(2024, 3)], " <- a (year, month) key")

print()
print("1, 1.0 and True hash the same and compare equal, so they are ONE key:")
print("  {1: 'a', 1.0: 'b', True: 'c'} ->", {1: "a", 1.0: "b", True: "c"})
print("  len({1, True})                ->", len({1, True}))


# ---------------------------------------------------------------------------
# 14. Why lookup does not get slower
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("14. Why a big dictionary is not a slow dictionary")
print("=" * 70)

print("Finding something in a LIST means looking:")
print("  'zoe' in names  -> compare item by item until found or exhausted.")
print("  Ten times more names, ten times more work.")
print()
print("Finding something in a DICT or SET means calculating:")
print("  hash the key -> that number says which slot -> go straight there.")
print("  The calculation depends on the KEY, not on how many keys exist.")
print("  Ten times more keys, the same work.")
print()
print("10,000 names checked against 10,000 allowed values:")
print("  with a list: ~50,000,000 comparisons")
print("  with a set:      10,000 lookups")
print("Same answer. Thousands of times less work.")

allowed_list = ["red", "green", "blue"]
allowed = set(allowed_list)  # build the set ONCE, before the loop
for colour in ["red", "pink", "blue"]:
    print("   ", colour, "allowed?", colour in allowed)

print()
print("Three honest caveats:")
print("  1. Members must be hashable - no lists in a set.")
print("  2. Order is lost (a dict keeps insertion order; a set keeps none).")
print("  3. It is not free: more memory, and for five items nobody can measure")
print("     the difference. Reach for it when the data is big, when you test")
print("     membership repeatedly, or when uniqueness is the actual point.")
print("The formal names are O(n) versus O(1). The idea is: looking through")
print("everything, versus calculating where to look.")


# ---------------------------------------------------------------------------
# 15. Choosing between them
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("15. Which one do I want?")
print("=" * 70)

print("  'What is at position 3?'          -> list")
print("  'What is X's Y?'                  -> dict")
print("  'Have I seen this already?'       -> set")
print("  'What are the parts of this one thing?' -> tuple")
print()
print("  three scores, need the average    -> list   [88, 95, 79]")
print("  a score for a named student       -> dict   {'Ada': 88}")
print("  a point on a map                  -> tuple  (51.5, -0.1)")
print("  which user IDs logged in today    -> set    {4192, 7781}")
print("  each team's members               -> dict of lists")
print("  a record loaded from JSON         -> dict of dicts")
print("  counting anything                 -> dict, via d.get(k, 0) + 1")

print()
print("Done. Now open exercises.py in this folder.")
