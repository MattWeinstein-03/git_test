"""Day 03 — Conditionals: runnable demonstrations.

Run me from the course root:

    python course/week1/day03_conditionals/examples.py

Every section number matches a section in LESSON.md. Predict each result before
you read it.
"""

# ---------------------------------------------------------------------------
# 1. Booleans are values
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. True and False are ordinary values")
print("=" * 70)

is_open = True
is_admin = False
print("is_open ->", is_open, "| type ->", type(is_open).__name__)

# A comparison PRODUCES a bool. It does not need an `if` to exist.
age = 20
is_adult = age >= 18
print("age >= 18 stored in a variable ->", is_adult)

# bool is a kind of int, which is occasionally handy and mostly trivia.
print("True + True ->", True + True, "| int(True) ->", int(True), "| True == 1 ->", True == 1)
print("Watch the spelling: `true` (lowercase) is a NameError.")


# ---------------------------------------------------------------------------
# 2. Comparison operators
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. The six comparisons")
print("=" * 70)

print("5 == 5 ->", 5 == 5, "| 5 != 3 ->", 5 != 3)
print("5 > 3  ->", 5 > 3, "| 5 < 3  ->", 5 < 3)
print("5 >= 5 ->", 5 >= 5, "| 5 <= 4 ->", 5 <= 4)

print()
print("Strings compare character by character, by character code:")
print("'apple' < 'banana' ->", "apple" < "banana")
print("'Zoo' < 'apple'    ->", "Zoo" < "apple", " <- capitals sort before lowercase")
print("'Zoo'.lower() < 'apple'.lower() ->", "Zoo".lower() < "apple".lower())
print("'abc' == 'ABC'     ->", "abc" == "ABC")

print()
print("Numbers written as text are not numbers:")
print("'10' > '9'  ->", "10" > "9", " <- text: '1' comes before '9'")
print("10 > 9      ->", 10 > 9)
print("'10' == 10  ->", "10" == 10, " <- different types are never equal")
print("'10' > 9    ->  TypeError: '>' not supported between 'str' and 'int'")

print()
print("And never compare floats with ==:")
print("0.1 + 0.2 == 0.3          ->", 0.1 + 0.2 == 0.3)
print("abs((0.1+0.2) - 0.3) < 1e-9 ->", abs((0.1 + 0.2) - 0.3) < 1e-9)


# ---------------------------------------------------------------------------
# 3. and, or, not
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Combining conditions")
print("=" * 70)

age = 25
has_ticket = True
print("age >= 18 and has_ticket ->", age >= 18 and has_ticket)
print("age < 18 or has_ticket   ->", age < 18 or has_ticket)
print("not has_ticket           ->", not has_ticket)

print()
print("Truth table for and / or:")
print(f"{'a':<7}{'b':<7}{'a and b':<10}{'a or b':<8}")
print("-" * 32)
print(f"{'True':<7}{'True':<7}{str(True and True):<10}{str(True or True):<8}")
print(f"{'True':<7}{'False':<7}{str(True and False):<10}{str(True or False):<8}")
print(f"{'False':<7}{'True':<7}{str(False and True):<10}{str(False or True):<8}")
print(f"{'False':<7}{'False':<7}{str(False and False):<10}{str(False or False):<8}")

print()
print("Precedence: `and` binds tighter than `or`.")
print("True or False and False   ->", True or False and False, " <- True or (False and False)")
print("(True or False) and False ->", (True or False) and False)

# The dangerous part: the buggy version often agrees with the correct one.
is_member = False
senior_age = 70
is_student = False
print("member or age>=65 and not student   ->", is_member or senior_age >= 65 and not is_student)
print("(member or age>=65) and not student ->", (is_member or senior_age >= 65) and not is_student)
print("Both True here — which is exactly why you must bracket mixed and/or.")

print()
print("Short-circuiting: the right-hand side is skipped when it cannot matter.")
text = ""
print("len(text) > 0 and text[0] == 'a' ->", len(text) > 0 and text[0] == "a",
      " <- no IndexError: text[0] never ran")
print("text[0] == 'a' and len(text) > 0 ->  IndexError (wrong order!)")
print("0 and 1/0 ->", 0 and 1 / 0, " <- no ZeroDivisionError either")

print()
print("and/or return an OPERAND, not True/False:")
print("1 and 2        ->", 1 and 2)
print("0 and 2        ->", 0 and 2)
print("'' or 'default'->", "" or "default")
print("'a' or 'b'     ->", "a" or "b")
print("None or 0      ->", None or 0)
name = ""
print("name or 'anonymous' ->", name or "anonymous", " <- the fallback idiom")
print("Trap: that idiom treats 0 and '' as missing. If 0 is valid, test `is None`.")
print("Trap: `if x == 1 or 2:` is `(x == 1) or 2` — always true.")


# ---------------------------------------------------------------------------
# 4. if / elif / else
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. if / elif / else")
print("=" * 70)

temperature = 30
if temperature > 25:
    print("temperature 30 ->", "hot")
elif temperature > 15:
    print("temperature 30 ->", "mild")
else:
    print("temperature 30 ->", "cold")

# Only the FIRST matching branch runs. This chain is broken:
score = 95
if score > 50:
    print("broken order, score 95 ->", "pass", " <- 'distinction' is unreachable")
elif score > 90:
    print("never printed")

# Fixed: most specific condition first.
if score > 90:
    print("fixed order,  score 95 ->", "distinction")
elif score > 50:
    print("pass")
else:
    print("fail")

# Separate ifs are separate questions: several can fire.
print("separate ifs, score 95 ->", end=" ")
if score > 90:
    print("distinction", end=" ")
if score > 50:
    print("pass", end=" ")
print()

# The grading pattern. Notice: no `and score < 90` is needed anywhere.
print()
print("Grading chain (no redundant upper bounds needed):")
score = 95
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
print("  95 ->", grade)
score = 84
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "F"
print("  84 ->", grade)

# Guard-clause shape: deal with the awkward case first.
raw_name = "  "
if not raw_name.strip():
    message = "no name given"
else:
    message = f"Hello, {raw_name.strip()}!"
print("guard clause on '  ' ->", message)

# pass is the official do-nothing placeholder (an empty block is a SyntaxError).
value = 5
if value > 10:
    pass  # TODO: handle the big case later
else:
    print("pass demo: value is small")


# ---------------------------------------------------------------------------
# 5. Indentation is syntax
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. Indentation decides what belongs to the if")
print("=" * 70)

if False:
    print("A — never printed")
    print("B — never printed")
print("C — outside the if, always printed")

# The same three lines with one un-indented differ in behaviour, silently:
if False:
    print("A — never printed")
print("B — now OUTSIDE the if, so it prints")
print("C — prints")

print()
print("The four errors you will meet:")
print("  no indent after ':'   -> IndentationError: expected an indented block")
print("  extra indent          -> IndentationError: unexpected indent")
print("  ragged indent         -> IndentationError: unindent does not match ...")
print("  a tab among spaces    -> TabError: inconsistent use of tabs and spaces")
print("Four spaces per level. Never tabs. Configure your editor once.")


# ---------------------------------------------------------------------------
# 6. Nesting, and flattening it
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Nesting versus combining")
print("=" * 70)

age = 20
has_ticket = False

# Nested: two gates, one inside the other.
if age >= 18:
    if has_ticket:
        nested = "come in"
    else:
        nested = "buy a ticket first"
else:
    nested = "too young"
print("nested version    ->", nested)

# Flattened with `and`: same behaviour, one level shallower.
if age >= 18 and has_ticket:
    flat = "come in"
elif age >= 18:
    flat = "buy a ticket first"
else:
    flat = "too young"
print("flattened version ->", flat)
print("Two levels is normal, three is a smell, four means restructure.")


# ---------------------------------------------------------------------------
# 7. Truthiness
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. Truthiness: what `if` really asks")
print("=" * 70)

print("Falsy:  False  None  0  0.0  ''  []  ()  {}  set()")
print("Truthy: everything else")
print()
print("bool(0), bool(1), bool(-1)      ->", bool(0), bool(1), bool(-1))
print("bool(''), bool('a'), bool(' ')  ->", bool(""), bool("a"), bool(" "))
print("bool('0'), bool('False')        ->", bool("0"), bool("False"),
      " <- non-empty strings are TRUTHY")
print("bool([]), bool([0])             ->", bool([]), bool([0]),
      " <- a list containing 0 is truthy")
print("bool(None), bool(0.0)           ->", bool(None), bool(0.0))

name = ""
if name:
    print("greeting ->", f"Hello, {name}")
else:
    print("greeting -> Hello, stranger   (because '' is falsy)")

print()
print("These four all test the same thing; the first is the one to write:")
print("  if name:            <- idiomatic")
print("  if name != '':")
print("  if len(name) > 0:")
print("  if bool(name) == True:   <- actively bad style")

print()
print("Where truthiness is the WRONG tool — 0 and None mean different things:")
quantity = 0
if quantity:
    print("  truthiness says: in stock")
else:
    print("  truthiness says: 'out of stock or unknown' — it cannot tell them apart")

if quantity is None:
    print("  explicit says: unknown")
elif quantity == 0:
    print("  explicit says: out of stock  <- the distinction survives")
else:
    print("  explicit says: in stock")


# ---------------------------------------------------------------------------
# 8. Chained comparisons
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. Chained comparisons")
print("=" * 70)

score = 85
print("0 <= score <= 100 ->", 0 <= score <= 100, " <- the range check")
print("18 <= 25 < 65     ->", 18 <= 25 < 65)
print("1 <= 5 <= 10 <= 20->", 1 <= 5 <= 10 <= 20)
print("'a' <= 'm' <= 'z' ->", "a" <= "m" <= "z")
print("0 <= 5 <= 3       ->", 0 <= 5 <= 3)
print()
print("a == b == c really does mean 'all equal':", 1 == 1 == 1)
print("but x != y != z does NOT mean 'all different':", 1 != 2 != 1,
      " <- 1 and 1 are equal!")


# ---------------------------------------------------------------------------
# 9. Conditional expressions
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. Conditional expressions: value if condition else other")
print("=" * 70)

age = 20
label = "adult" if age >= 18 else "minor"
print("label ->", label)

count = 1
print("pluralising:", f"{count} item{'s' if count != 1 else ''}")
count = 3
print("pluralising:", f"{count} item{'s' if count != 1 else ''}")

total = 0
items = 0
average = total / items if items else 0.0
print("safe average with 0 items ->", average, " <- the divide never ran")

print()
print("The `else` is compulsory: `x = 1 if flag` is a SyntaxError.")
print("Do not nest them. This is legal and unreadable:")
size = 5
print("  'small' if size<3 else 'medium' if size<10 else 'large' ->",
      "small" if size < 3 else "medium" if size < 10 else "large")
print("  ... that wants to be an if/elif/else chain.")


# ---------------------------------------------------------------------------
# 10. is versus ==
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("10. is versus ==")
print("=" * 70)

a = [1, 2, 3]  # lists arrive properly on Day 5; they show this most clearly
b = [1, 2, 3]  # a separate list that happens to look the same
c = a  # the same list, second name

print("a == b ->", a == b, " <- same contents")
print("a is b ->", a is b, " <- different objects")
print("a == c ->", a == c)
print("a is c ->", a is c, " <- literally the same object")
print("id(a) == id(c) ->", id(a) == id(c), "| id(a) == id(b) ->", id(a) == id(b))

print()
print("`is` is correct for exactly three values: None, True, False.")
value = None
print("value is None     ->", value is None)
print("value is not None ->", value is not None)

print()
print("Why `is` on other values is a trap — small ints are cached and shared:")
small_one = 256
small_two = 256
print("256 is 256 (two names) ->", small_one is small_two)
computed = int("257")
literal = 257
print("int('257') == 257 ->", computed == literal, " <- always True")
print("int('257') is 257 ->", computed is literal, " <- False: same value, other object")
print("Rule: `is` for None/True/False, `==` for values. No exceptions needed.")

flag = True
print()
print("Even for booleans, plain truthiness is best:")
if flag:
    print("  if flag:          <- best")
print("  if flag is True:  <- correct but noisy")
print("  if flag == True:  <- noisy and fragile (1 == True is also True)")


# ---------------------------------------------------------------------------
# 11. = versus ==
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("11. = assigns, == compares")
print("=" * 70)

count = 5  # assignment
print("count == 5 ->", count == 5, " <- comparison")
print()
print("Getting it wrong is a SyntaxError, and Python tells you the fix:")
print("    if count = 5:")
print("    SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?")
print("In C the same typo compiles and is always true. Python protects you here.")
print()
print("Footnote: `:=` (the walrus) assigns inside a condition. Not needed this")
print("week; it is mentioned only so the symbol is not a mystery later.")

# Putting it together: one small classifier using most of today's ideas.
print()
print("=" * 70)
print("Putting it together — a tiny ticket-price rule")
print("=" * 70)


def price_for(age_value, is_member_value):
    """Return the ticket price in pounds for an age and membership flag.

    `def` is only "a named recipe" until Day 8 — it is used here so the same
    rules can be applied to six different inputs without copying them out six
    times. The conditional logic inside is all Day 3 material.
    """
    if not 0 <= age_value <= 120:
        return 0.0  # a guard clause: refuse nonsense first
    if age_value < 5:
        return 0.0
    if age_value < 16:
        base = 6.0
    elif age_value >= 65:
        base = 7.0
    else:
        base = 12.0
    return round(base * 0.9, 2) if is_member_value else base


print(f"{'age':>5}{'member':>9}{'price':>8}")
print("-" * 22)
print(f"{3:>5}{'False':>9}{price_for(3, False):>8.2f}")
print(f"{10:>5}{'False':>9}{price_for(10, False):>8.2f}")
print(f"{10:>5}{'True':>9}{price_for(10, True):>8.2f}")
print(f"{30:>5}{'False':>9}{price_for(30, False):>8.2f}")
print(f"{70:>5}{'True':>9}{price_for(70, True):>8.2f}")
print(f"{999:>5}{'False':>9}{price_for(999, False):>8.2f}")

print()
print("Done. Now open exercises.py in this folder.")
