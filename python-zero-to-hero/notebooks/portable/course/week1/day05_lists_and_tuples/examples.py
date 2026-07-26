"""Day 05 — Lists and Tuples: runnable demonstrations.

Run me from the course root:

    python course/week1/day05_lists_and_tuples/examples.py

Every section number matches a section in LESSON.md. Predict each result before
you read it. The interesting lines are the ones where you were wrong.

Nothing here asks for input, touches the network, or writes a file. Lines that
would raise an error are printed as text rather than executed, so the whole file
runs top to bottom with zero errors.
"""


# ---------------------------------------------------------------------------
# 1. Why you need a list
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. One name for any number of values")
print("=" * 70)

# The problem: one variable per value does not scale.
score_1 = 88
score_2 = 92
score_3 = 79
print("three separate variables ->", (score_1 + score_2 + score_3) / 3)

# The fix: one list, and code that does not care how many items there are.
scores = [88, 92, 79]
print("scores            ->", scores)
print("sum / len         ->", sum(scores) / len(scores))

scores.append(95)  # a fourth score arrives at runtime
print("after append(95)  ->", scores)
print("sum / len (again) ->", sum(scores) / len(scores), " <- same code, more data")


# ---------------------------------------------------------------------------
# 2. Making a list
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. Making lists")
print("=" * 70)

numbers = [1, 2, 3]
names = ["Ada", "Grace", "Alan"]
mixed = [1, "two", 3.0, True, None]
empty = []

print("numbers ->", numbers)
print("names   ->", names, " <- print shows the quotes: these are strings")
print("mixed   ->", mixed, " <- legal, but keep lists to one kind of thing")
print("empty   ->", empty, "of length", len(empty))
print("type    ->", type(numbers).__name__)

# Order is kept and duplicates are allowed: a list is not a set (Day 06).
print("[1, 2, 3] == [3, 2, 1] ->", [1, 2, 3] == [3, 2, 1], " <- order is part of the value")
print("[1, 1, 1]              ->", [1, 1, 1], "has length", len([1, 1, 1]))

# The other ways to build one.
print("list('hello')   ->", list("hello"))
print("list(range(5))  ->", list(range(5)))
print("range(5) itself ->", range(5), " <- a recipe, not a list")
print("'a,b,c'.split(',') ->", "a,b,c".split(","))
print("[0] * 5         ->", [0] * 5)
print("[1, 2] + [3, 4] ->", [1, 2] + [3, 4])

# The pattern you will write a thousand times: empty list, loop, append.
squares = []
for number in range(1, 6):
    squares.append(number * number)
print("empty list + loop + append ->", squares)


# ---------------------------------------------------------------------------
# 3. Indexing
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Indexing: one item at a time")
print("=" * 70)

names = ["Ada", "Grace", "Alan", "Edsger"]
print("names     ->", names)
print("names[0]  ->", names[0], " <- indexes start at 0")
print("names[1]  ->", names[1])
print("names[3]  ->", names[3], " <- the last one, len - 1")
print("len(names)->", len(names))
print("names[4]  ->  IndexError: list index out of range")
print()
print('   "Ada"  "Grace"  "Alan"  "Edsger"')
print("     0       1       2        3      <- index from the left")
print("    -4      -3      -2       -1      <- index from the right")
print()
print("names[-1] ->", names[-1], " <- the last item, the easy way")
print("names[-2] ->", names[-2])
print("names[len(names) - 1] ->", names[len(names) - 1], "(correct, and noise)")

# The index can be any expression that produces a whole number.
position = 1
print("position = 1; names[position]     ->", names[position])
print("names[position + 1]               ->", names[position + 1])
print("names[len(names) // 2]            ->", names[len(names) // 2], " <- // not /")
print("names[len(names) / 2]  ->  TypeError: list indices must be integers")

# It works, but section 9 replaces it with enumerate.
for index in range(len(names)):
    print("  index", index, "holds", names[index])


# ---------------------------------------------------------------------------
# 4. Slicing
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Slicing: items[start:stop:step]")
print("=" * 70)

letters = ["a", "b", "c", "d", "e", "f"]
print("letters       ->", letters)
print("letters[1:3]  ->", letters[1:3], " <- indexes 1 and 2; stop is EXCLUDED")
print("letters[:3]   ->", letters[:3], " <- from the start")
print("letters[3:]   ->", letters[3:], " <- to the end")
print("letters[:]    ->", letters[:], " <- a full copy")
print("letters[::2]  ->", letters[::2], " <- every second item")
print("letters[1::2] ->", letters[1::2])
print("letters[::-1] ->", letters[::-1], " <- reversed")
print("letters[-2:]  ->", letters[-2:], " <- the last two")
print("letters[:-2]  ->", letters[:-2], " <- all but the last two")
print("letters[2:5:2]->", letters[2:5:2], " <- all three parts at once")

# Because stop is excluded, the arithmetic comes out clean.
print("len(letters[1:4]) ->", len(letters[1:4]), "= 4 - 1, no mental arithmetic")
print("letters[:2] + letters[2:] ->", letters[:2] + letters[2:], " <- rebuilds it exactly")

# A slice is always a NEW list.
original = ["a", "b", "c"]
piece = original[0:2]
piece.append("NEW")
print("piece after append   ->", piece)
print("original             ->", original, " <- untouched: a slice is a new list")

# Slices clip; indexes raise.
print("letters[1:100] ->", letters[1:100], " <- clipped, no error")
print("letters[100:]  ->", letters[100:], " <- empty, no error, easy to miss")
print("letters[3:1]   ->", letters[3:1], " <- start after stop: empty")
print("letters[100]   ->  IndexError")

# Assigning through a slice replaces a run of items.
patch = ["a", "b", "c", "d"]
patch[1:3] = ["X", "Y"]
print("after patch[1:3] = ['X','Y'] ->", patch)
patch[1:3] = ["Z"]
print("after patch[1:3] = ['Z']     ->", patch, " <- lengths need not match")
patch[1:1] = ["p", "q"]
print("after patch[1:1] = ['p','q'] ->", patch, " <- empty slice inserts")


# ---------------------------------------------------------------------------
# 5. Lists are mutable
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. A list CAN be changed; a string cannot")
print("=" * 70)

print("word = 'python'; word[0] = 'P'")
print("  ->  TypeError: 'str' object does not support item assignment")

scores = [88, 92, 79]
print("scores before ->", scores)
scores[0] = 100
print("scores[0] = 100 ->", scores, " <- no new list was made; this one changed")

print()
print("immutable: int, float, bool, None, str, tuple")
print("mutable:   list, dict, set")
print("Mutability is why building a list is cheap - and why section 13 exists.")


# ---------------------------------------------------------------------------
# 6. List methods, and what each one gives back
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. The methods, and their RETURN VALUES")
print("=" * 70)

# append adds exactly one item, and hands back None.
items = ["a", "b"]
result = items.append("c")
print("items.append('c') -> items", items, "| returned", result, " <- None!")

one = [1, 2]
one.append([3, 4])
print("append a list ->", one, "of length", len(one), " <- one new item")

two = [1, 2]
two.extend([3, 4])
print("extend a list ->", two, "of length", len(two), " <- two new items")

three = ["a"]
three.extend("bc")
print("extend a string ->", three, " <- a string is a sequence of characters")

# insert puts an item before a position.
ordered = ["a", "c"]
ordered.insert(1, "b")
print("insert(1, 'b')   ->", ordered)
ordered.insert(0, "start")
print("insert(0, 'start')->", ordered, " <- insert at the front")
ordered.insert(999, "end")
print("insert(999,'end') ->", ordered, " <- an index past the end clips")

# pop is the one method whose return value you almost always want.
queue = ["first", "second", "third"]
last = queue.pop()
print("queue.pop()  -> returned", repr(last), "| queue is now", queue)
first = queue.pop(0)
print("queue.pop(0) -> returned", repr(first), "| queue is now", queue)
print("pop() on an empty list ->  IndexError: pop from empty list")

# remove deletes the FIRST match by value, and raises when absent.
dupes = ["a", "b", "c", "b"]
dupes.remove("b")
print("remove('b') on ['a','b','c','b'] ->", dupes, " <- only the first one went")
print("remove('zzz') ->  ValueError: list.remove(x): x not in list")

# index and count ask questions instead of changing anything.
people = ["Ada", "Grace", "Alan", "Grace"]
print("people.index('Grace') ->", people.index("Grace"), " <- the FIRST position")
print("people.count('Grace') ->", people.count("Grace"))
print("people.count('Nobody')->", people.count("Nobody"), " <- 0, no error")
print("people.index('Nobody')->  ValueError: 'Nobody' is not in list")
if "Nobody" in people:
    print("  found it")
else:
    print("  guard with `in` before calling index() or remove()")

# sort / reverse / clear / copy
marks = [88, 92, 79]
marks.sort()
print("marks.sort()             ->", marks, " <- rearranged in place")
marks.sort(reverse=True)
print("marks.sort(reverse=True) ->", marks)

letters = ["a", "b", "c"]
letters.reverse()
print("letters.reverse()        ->", letters, " <- in place")
backup = letters.copy()
letters.clear()
print("after clear(): letters ->", letters, "| backup ->", backup)


# ---------------------------------------------------------------------------
# 7. Functions that work on a whole list
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. len, sum, min, max, sorted, reversed, any, all")
print("=" * 70)

scores = [88, 92, 79, 92]
print("scores        ->", scores)
print("len(scores)   ->", len(scores))
print("sum(scores)   ->", sum(scores))
print("min(scores)   ->", min(scores), "| max(scores) ->", max(scores))
print("average       ->", sum(scores) / len(scores))
print("sorted(scores)->", sorted(scores), " <- a NEW list")
print("scores        ->", scores, " <- the original is untouched")

words = ["pear", "fig", "apple"]
print("sorted(words)               ->", sorted(words))
print("sorted(words, reverse=True) ->", sorted(words, reverse=True))
print("list(reversed(words))       ->", list(reversed(words)))
print("words[::-1]                 ->", words[::-1], " <- same result")
print("reversed(words) unwrapped is a lazy walker, not a list:")
for word in reversed(words):
    print("   ", word)

print()
print("any([False, False, True]) ->", any([False, False, True]))
print("all([True, True, True])   ->", all([True, True, True]))
print("all([True, False])        ->", all([True, False]))
print("any([0, '', None])        ->", any([0, "", None]), " <- every item is falsy")
print("all([1, 'a', [0]])        ->", all([1, "a", [0]]), " <- every item is truthy")
print("any([])                   ->", any([]), " <- no items, so none is true")
print("all([])                   ->", all([]), " <- no items, so none can fail")
print("sum([])                   ->", sum([]), "| len([]) ->", len([]))
print("min([]) / max([])         ->  ValueError: arg is an empty sequence")


# ---------------------------------------------------------------------------
# 8. sort versus sorted
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. sort (method, in place, None) vs sorted (function, new list)")
print("=" * 70)

in_place = [88, 92, 79]
in_place.sort()
print("in_place.sort() then in_place ->", in_place)

untouched = ["Zoe", "Ada"]
ordered = sorted(untouched)
print("sorted(untouched) ->", ordered, "| untouched ->", untouched)

print("sorted works on any sequence:")
print("  sorted('cab')            ->", sorted("cab"))
print("  ''.join(sorted('cab'))   ->", "".join(sorted("cab")))
print("  sorted(('c', 'a'))       ->", sorted(("c", "a")), " <- always returns a LIST")

# 8.1 The mistake that eats an evening.
print()
print("The single most expensive Week 1 mistake:")
broken = [88, 92, 79]
broken = broken.sort()  # sorts the list, returns None, then throws the list away
print("  broken = broken.sort()  ->", broken, " <- your data is gone")
print("  len(broken)   ->  TypeError: object of type 'NoneType' has no len()")
print("  broken[0]     ->  TypeError: 'NoneType' object is not subscriptable")
print("  for x in broken ->  TypeError: 'NoneType' object is not iterable")
print("  RULE: a method that changes a list in place returns None.")
print("        scores.sort()          correct")
print("        scores = sorted(scores) correct")
print("        scores = scores.sort()  wrong, always")
print("  Mirror image with strings: text = text.strip() is REQUIRED, because")
print("  strings are immutable and their methods have nothing to do but return.")

# 8.2 Sorting by something other than the value.
print()
print("Default order compares the items themselves:")
print("  sorted(['banana','Apple','cherry']) ->", sorted(["banana", "Apple", "cherry"]))
print("     capitals sort first: 'A' is character 65, 'a' is 97")
print("  sorted([10, 9, 100])   ->", sorted([10, 9, 100]))
print("  sorted(['10','9','100'])->", sorted(["10", "9", "100"]), " <- text, not numbers")

fruit = ["banana", "fig", "apple"]
print("  sorted(fruit, key=len) ->", sorted(fruit, key=len), " <- no brackets on len")
print("  sorted(fruit, key=len, reverse=True) ->", sorted(fruit, key=len, reverse=True))
print("  sorted(['banana','Apple'], key=str.lower) ->",
      sorted(["banana", "Apple"], key=str.lower))


# `def` is Day 08. For now: a named recipe that takes something in and hands
# something back. `key=` wants exactly that.
def second_item(pair: tuple[str, int]) -> int:
    """Pull the number out of a (name, score) pair."""
    return pair[1]


def surname(full_name: str) -> str:
    """The last whitespace-separated word of a name."""
    return full_name.split()[-1]


def length_then_alphabetical(word: str) -> tuple[int, str]:
    """Sort key: shortest first, then alphabetical among equal lengths."""
    return (len(word), word)


results = [("Ada", 88), ("Grace", 95), ("Alan", 79)]
print()
print("A named key function sorts by whatever you can compute:")
print("  sorted(results, key=second_item)               ->", sorted(results, key=second_item))
print("  sorted(results, key=second_item, reverse=True) ->",
      sorted(results, key=second_item, reverse=True), " <- a leaderboard")

people = ["Ada Lovelace", "Grace Hopper", "Alan Turing"]
print("  sorted(people, key=surname) ->", sorted(people, key=surname))

mixed_lengths = ["pear", "fig", "plum", "kiwi", "date"]
print("  key returning a TUPLE sorts by two things at once:")
print("  sorted(..., key=length_then_alphabetical) ->",
      sorted(mixed_lengths, key=length_then_alphabetical))
print("  sorted([1, 'a']) ->  TypeError: '<' not supported between 'str' and 'int'")


# ---------------------------------------------------------------------------
# 9. enumerate
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. enumerate: position and item together")
print("=" * 70)

names = ["Ada", "Grace", "Alan"]

print("The clumsy way:")
for index in range(len(names)):
    print("   ", index, names[index])

print("enumerate:")
for index, name in enumerate(names):
    print("   ", index, name)

print("enumerate(..., start=1) for human numbering:")
for rank, name in enumerate(names, start=1):
    print(f"    {rank}. {name}")

print("list(enumerate(['a','b']))          ->", list(enumerate(["a", "b"])))
print("list(enumerate(['a','b'], start=1)) ->", list(enumerate(["a", "b"], start=1)))
print("Each pair is a TUPLE - which is why tuples are on today's menu.")
print("Forgetting enumerate: `for i, x in names:` -> ValueError: too many values")


# ---------------------------------------------------------------------------
# 10. zip
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("10. zip: walk two lists side by side")
print("=" * 70)

names = ["Ada", "Grace", "Alan"]
scores = [88, 95, 79]

for name, score in zip(names, scores):
    print(f"    {name}: {score}")

print("list(zip(names, scores)) ->", list(zip(names, scores)))
print("   a list of pairs - the shape section 8.2 sorted, and the shape a")
print("   dictionary is built from (Day 06)")

codes = ["A", "B", "C"]
print("three lists at once ->", list(zip(names, scores, codes)))
print("zip stops at the shortest input, silently:")
print("  list(zip([1,2,3], ['a'])) ->", list(zip([1, 2, 3], ["a"])), " <- two items dropped")
print("  Python 3.10+: zip(a, b, strict=True) raises instead.")


# ---------------------------------------------------------------------------
# 11. in
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("11. Membership with `in`")
print("=" * 70)

names = ["Ada", "Grace", "Alan"]
print("'Ada' in names     ->", "Ada" in names)
print("'Zoe' in names     ->", "Zoe" in names)
print("'Zoe' not in names ->", "Zoe" not in names)
print("'ada' in names     ->", "ada" in names, " <- exact match, case included")
print("'Ad' in names      ->", "Ad" in names, " <- whole items, not parts")
print("'Ad' in names[0]   ->", "Ad" in names[0], " <- that is a string test")

if "Grace" in names:
    names.remove("Grace")
print("guarded remove ->", names)
print("`in` on a list searches item by item. A big list inside a big loop is")
print("slow; Day 06's set answers the same question without searching.")


# ---------------------------------------------------------------------------
# 12. Tuples
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("12. Tuples: a sequence that cannot change")
print("=" * 70)

point = (3, 4, 5)
print("point           ->", point, "of type", type(point).__name__)
print("point[0]        ->", point[0], "| point[-1] ->", point[-1])
print("point[1:]       ->", point[1:], " <- slicing a tuple gives a tuple")
print("len(point)      ->", len(point), "| 4 in point ->", 4 in point)
print("sum(point)      ->", sum(point), "| sorted(point) ->", sorted(point))
print("point[0] = 99   ->  TypeError: 'tuple' object does not support item assignment")
print("No append, no sort, no remove: everything that writes is absent.")

# The comma is what makes a tuple, not the brackets.
print()
pair = 3, 4
print("pair = 3, 4        ->", pair, " <- brackets optional")
print("(5)  has type", type((5)).__name__, "-> brackets alone are only grouping")
print("(5,) has type", type((5,)).__name__, "of length", len((5,)), " <- THE COMMA")
print("()   is an empty tuple of length", len(()))

# Why immutability is useful.
print()
print("Why bother with a type that can do less?")
print("  1. Nobody can change it - not even code you handed it to.")
print("  2. It can be a dictionary key or a set member; a list cannot.")
locations = {}
locations[(51.5, -0.1)] = "London"
print("     locations[(51.5, -0.1)] = 'London' ->", locations)
print("     locations[[51.5, -0.1]] = ... -> TypeError: unhashable type: 'list'")
print("  3. It signals 'fixed parts with different roles' to a reader.")
print("  4. Functions hand them back: divmod(17, 5) ->", divmod(17, 5))
print("  RULE: same kind of thing, variable number  -> list")
print("        different roles, fixed once made     -> tuple")

# Unpacking.
print()
x, y, z = point
print("x, y, z = point        ->", x, y, z)
quotient, remainder = divmod(17, 5)
print("q, r = divmod(17, 5)   ->", quotient, remainder)
first, second, third = "abc"
print("a, b, c = 'abc'        ->", first, second, third)
head, tail = ["one", "two"]
print("head, tail = ['one','two'] ->", head, tail)
print("x, y = (1, 2, 3)       ->  ValueError: too many values to unpack (expected 2)")

print("Ignore a part on purpose by naming it _ :")
scored = [("Ada", 88), ("Grace", 95)]
for name, _ in scored:
    print("   ", name)

# The swap idiom.
print()
a = 1
b = 2
temp = a  # the three-line version other languages need
a = b
b = temp
print("swap with a temp variable ->", a, b)
a = 1
b = 2
a, b = b, a  # the right-hand side is built FIRST, then assigned
print("a, b = b, a               ->", a, b)
three_way = ["x", "y", "z"]
three_way[0], three_way[-1] = three_way[-1], three_way[0]
print("items[0], items[-1] = items[-1], items[0] ->", three_way)

# A tuple is not entirely bulletproof.
print()
row = ("header", [1, 2])
row[1].append(3)
print("row = ('header', [1, 2]); row[1].append(3) ->", row)
print("The tuple still holds the same list - that LIST changed.")
print("row[1] = [9] ->  TypeError: 'tuple' object does not support item assignment")


# ---------------------------------------------------------------------------
# 13. Aliasing: two names, one list
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("13. The most important section of the day")
print("=" * 70)

a = [1, 2, 3]
b = a  # NOT a copy: a second name for one list
b.append(4)
print("a = [1,2,3]; b = a; b.append(4)")
print("  b ->", b)
print("  a ->", a, " <- a changed too, because there is only ONE list")

a = [1, 2, 3]
b = a
c = [1, 2, 3]  # a different list that happens to look the same
print("a is b ->", a is b, " <- same object")
print("a is c ->", a is c, " <- different objects")
print("a == c ->", a == c, " <- equal contents")
print("id(a) == id(b) ->", id(a) == id(b))
print("`==` asks 'same contents?'.  `is` asks 'same object?'")

# Numbers and strings alias too; you can never tell, because they cannot change.
a = 5
b = a
b = b + 1
print("with ints: a =", a, "b =", b, " <- no operation can change 5 in place")

# Rebinding vs mutating: the whole bug, in four lines.
print()
first = [1, 2, 3]
second = first
second = [9, 9]  # REBIND: moves the label
print("b = [9, 9]  (rebind) -> a is", first, " <- unaffected")
first = [1, 2, 3]
second = first
second.append(9)  # MUTATE: changes the object
print("b.append(9) (mutate) -> a is", first, " <- affected")
print("`b = ...` moves a label. `b.something()` changes the object.")


# Passing a list to a function passes the same list.
def add_zero(numbers: list[int]) -> None:
    """Append a zero to the list that was passed in."""
    numbers.append(0)


caller_list = [1, 2]
add_zero(caller_list)
print("a function that appends -> the caller's list is now", caller_list)
print("Today's exercises are strict about this: several must NOT modify their")
print("argument, and the tests check the argument afterwards.")

# The shared-row trap.
print()
grid = [[0] * 3] * 3
print("grid = [[0] * 3] * 3 ->", grid, " <- looks perfect")
grid[0][0] = 9
print("grid[0][0] = 9       ->", grid, " <- three 9s")
print("grid[0] is grid[1]   ->", grid[0] is grid[1], " <- one row, stored three times")

grid = []
for row_index in range(3):
    grid.append([0] * 3)  # a NEW row on every pass
grid[0][0] = 9
print("built with a loop    ->", grid)
print("grid[0] is grid[1]   ->", grid[0] is grid[1], " <- three distinct rows")

# Three ways to copy, all equivalent.
print()
source = [1, 2, 3]
copy_a = list(source)
copy_b = source.copy()
copy_c = source[:]
copy_a.append(99)
copy_b.append(88)
copy_c.append(77)
print("source          ->", source, " <- untouched by all three copies")
print("list(source)    ->", copy_a)
print("source.copy()   ->", copy_b)
print("source[:]       ->", copy_c)
print("source is copy_a/b/c ->", source is copy_a, source is copy_b, source is copy_c)

# + creates, += mutates. For lists these are NOT interchangeable.
print()
plus_a = [1, 2]
plus_b = plus_a
plus_a = plus_a + [3]
print("a = a + [3] -> a", plus_a, "| b", plus_b, " <- b kept the old list")
inplace_a = [1, 2]
inplace_b = inplace_a
inplace_a += [3]
print("a += [3]    -> a", inplace_a, "| b", inplace_b, " <- b sees the change")

# Shallow vs deep.
print()
original = [[1, 2], [3, 4]]
shallow = list(original)
print("original                 ->", original)
print("shallow is original      ->", shallow is original, " <- different outer lists")
print("shallow[0] is original[0]->", shallow[0] is original[0], " <- SAME inner list")
shallow[0].append(99)
print("shallow[0].append(99) -> original is", original, " <- it leaked through")
shallow.append([5, 6])
print("shallow.append([5,6]) -> original is", original, " <- outer change stayed local")

original = [[1, 2], [3, 4]]
deep = []
for row in original:
    deep.append(list(row))  # a fresh copy of every row
deep[0].append(99)
print("copy each row -> deep", deep, "| original", original, " <- independent")
print("deep[0] is original[0] ->", deep[0] is original[0])
print("RULE: one level of nesting needs one level of copying.")
print("      list(x) protects the outer list only.")
print("      copy.deepcopy handles any depth - that needs Day 11's imports.")

print()
print("Done. Now open exercises.py in this folder.")
