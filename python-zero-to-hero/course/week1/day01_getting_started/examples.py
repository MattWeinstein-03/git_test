"""Day 01 — Getting Started: runnable demonstrations.

Run me from the course root:

    python course/week1/day01_getting_started/examples.py

Every section number matches a section in LESSON.md. Read the code, predict the
output, then check the printed result against your prediction.

Note: this file never calls input(), because a script that waits for a human
cannot be run automatically. The input() sections show you what a real session
looks like instead.
"""

# ---------------------------------------------------------------------------
# 1. What a program actually is: statements, in order
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. Statements run top to bottom")
print("=" * 70)

# Three statements. Each one completes before the next begins.
price = 250  # step 1: bind the name `price` to the value 250
tax = price * 0.2  # step 2: compute, then bind the name `tax`
print("Total:", price + tax)  # step 3: compute and display
print("expected: Total: 300.0")

# Order matters. `tax` could not have been computed before `price` existed,
# because Python does not look ahead — it only knows what it has already run.
print("price is", price, "and tax is", tax)


# ---------------------------------------------------------------------------
# 2. How Python runs your file
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. Two kinds of failure")
print("=" * 70)

# We cannot demonstrate a real SyntaxError here: this file has to run, and a
# syntax error would stop it from starting at all. That is the whole point of
# the distinction, so read these two examples carefully instead.
print("A SyntaxError happens BEFORE anything runs. This file:")
print('    print("fine")')
print('    print("broken"       <- no closing bracket')
print("prints NOTHING, and reports:")
print("    SyntaxError: '(' was never closed")
print()
print("A NameError happens WHILE running, at the line that reads the name:")
print('    print("first")       <- this DOES print')
print("    print(total)         <- NameError here, program stops")
print('    print("third")       <- never reached')
print()
print("Diagnostic: if you saw no output at all, you have a grammar mistake.")
print("If you saw some output, look at the line where output stopped.")


# ---------------------------------------------------------------------------
# 3. The REPL versus scripts
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Scripts do not auto-display values")
print("=" * 70)

# In the REPL, typing `2 + 2` shows 4. In a script, the value is computed and
# thrown away. The next two lines produce NO output at all:
2 + 2
"hello".upper()

# In a script you have to ask:
print("print(2 + 2)          ->", 2 + 2)
print("print('hello'.upper())->", "hello".upper())

# The REPL also shows the *representation* of a value (with quotes and visible
# escapes), while print shows its *contents*. repr() gives you the REPL view.
multi_line = "line1\nline2"
print("repr(multi_line) ->", repr(multi_line))
print("print(multi_line) ->")
print(multi_line)


# ---------------------------------------------------------------------------
# 4. Variables: names bound to values
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Names, rebinding, and the arrow model")
print("=" * 70)

message = "Hello"
count = 3
print(message, count)

# `=` is an instruction, not an equation. The right-hand side is evaluated
# first, using the CURRENT value, then the name is re-pointed at the result.
count = count + 1
print("after count = count + 1 ->", count, "(expected 4)")

# Assignment moves an arrow; it does not copy a value into a box.
a = "first"
b = a  # b now points at the same string as a
a = "second"  # only a's arrow moves
print("a ->", a, "| b ->", b, "(expected: second | first)")

# id() is proof: two names can point at one value.
shared = "same object"
also_shared = shared
print("id(shared) == id(also_shared) ->", id(shared) == id(also_shared))

# Bind several names at once, and swap without a temporary variable.
x, y = 3, 4
print("x, y =", x, y)
x, y = y, x  # the right-hand side is fully evaluated first
print("after swap ->", x, y)

# Names are the cheapest documentation there is. Compare:
t = 1250 * 0.2  # what is t?
tax_due = 1250 * 0.2  # oh, it is the tax
print("t =", t, "| tax_due =", tax_due, "(identical values, one is readable)")


# ---------------------------------------------------------------------------
# 5. The five starting types
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. int, float, str, bool, None")
print("=" * 70)

# int: whole numbers, no size limit.
apples = 7
temperature = -4
big = 9_000_000_000_000  # underscores are ignored; they only help you read it
print("ints:", apples, temperature, big)
print("2 ** 100 ->", 2**100, "(exact, no overflow)")

# float: numbers with a decimal point. Division ALWAYS gives a float.
price = 19.99
ratio = 2 / 4
whole = 4.0
print("floats:", price, ratio, whole)
print("4 == 4.0 ->", 4 == 4.0, "| same type? ->", type(4) == type(4.0))
# Floats are binary approximations. This is not a bug; Day 2 explains it.
print("0.1 + 0.2 ->", 0.1 + 0.2, " <- not exactly 0.3")

# str: text in quotes.
name = "Ada"
empty = ""
escaped = "She said \"hi\""
simpler = 'She said "hi"'
print("strings:", name, repr(empty), escaped, simpler)
print("tab and newline:")
print("Name:\tAda\nCity:\tLondon")

address = """221B Baker Street
London
NW1 6XE"""
print("triple-quoted string keeps its line breaks:")
print(address)

# Glue strings with +. It joins EXACTLY what you give it, spaces included.
first = "Ada"
last = "Lovelace"
print("Name: " + first + " " + last)
print('"Ada" + "Lovelace" ->', "Ada" + "Lovelace", " <- no space appeared")

# + will not mix types. str() converts a value to text.
age = 36
print('"Age: " + str(age) ->', "Age: " + str(age))
print('"Age: " + age would raise TypeError: can only concatenate str')
print("36 * 2 ->", 36 * 2, '| "36" * 2 ->', "36" * 2, " <- same operator, different types")

# bool: exactly two values, capitalised.
is_open = True
is_admin = False
print("bools:", is_open, is_admin, "| 5 > 3 ->", 5 > 3, "| 5 == 3 ->", 5 == 3)

# None: the deliberate absence of a value.
middle_name = None
print("None ->", middle_name, "| type ->", type(None))
# print() displays text and returns nothing, so its value is None.
returned = print("  (this line was printed by print)")
print("value returned by print ->", returned, "(expected None)")


# ---------------------------------------------------------------------------
# 6. print: sep and end
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Controlling print")
print("=" * 70)

# Several values: Python inserts one space and converts each for display.
print("Name:", name, "Age:", age)
print("Mixed types are fine:", 3 + 4, "items", True, None)

# sep replaces the space BETWEEN values.
print("a", "b", "c")  # a b c
print("a", "b", "c", sep="")  # abc
print("a", "b", "c", sep=", ")  # a, b, c
print("2024", "03", "01", sep="-")  # 2024-03-01
print("one", "two", sep="\n")  # two lines

# end replaces the newline AFTER the last value.
print("Loading", end="")
print(".", end="")
print(".", end="")
print(".", end="")
print(" done")  # all of that is a single line of output

# Both together.
print("a", "b", sep=" | ", end=" <<\n")

# sep and end are keyword arguments: the NAME identifies them, not the
# position. Day 8 explains the mechanism; today you just use it.


# ---------------------------------------------------------------------------
# 7. input: always a string
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. input() and why it always hands back text")
print("=" * 70)

# No real input() call here — this script must run unattended. Instead we
# simulate exactly what input() would have returned: a string.
typed = "36"  # what input("Age: ") gives you when the user types 36
print("input() returned", repr(typed), "of type", type(typed).__name__)
print("typed * 2 ->", typed * 2, " <- text repeated, NOT doubled")

age_number = int(typed)  # explicit conversion
print("int(typed) ->", age_number, "of type", type(age_number).__name__)
print("age_number * 2 ->", age_number * 2, " <- now it is arithmetic")

# The one-step idiom you will write a thousand times:
#     age = int(input("Age: "))
# Read it inside out: input() runs first and gives text, int() converts it.
print("float('3.5') ->", float("3.5"))
print("int('3.5') would raise ValueError: invalid literal for int()")
print("int('abc') would raise ValueError too")


# ---------------------------------------------------------------------------
# 8. type(): the first question to ask
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. Inspecting values with type()")
print("=" * 70)

print("type(42)    ->", type(42))
print("type(3.14)  ->", type(3.14))
print("type('hi')  ->", type("hi"))
print("type(True)  ->", type(True))
print("type(None)  ->", type(None))
print("type(print) ->", type(print))

# .__name__ gives just the label, which reads better inside a sentence.
value = 19.99
print("type(value).__name__ ->", type(value).__name__)
print("value is a", type(value).__name__)

# Two more inspection tools you will use today.
print("len('hello') ->", len("hello"))
print("repr('42 ')  ->", repr("42 "), " <- the trailing space is now visible")
print("len('42 ')   ->", len("42 "), "(three characters, not two)")


# ---------------------------------------------------------------------------
# 9. Comments
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. Comments explain WHY")
print("=" * 70)

# Rates set by the finance team; reviewed every April.
TAX_RATE = 0.2  # 20% standard rate

subtotal = 100
total = subtotal * (1 + TAX_RATE)
print("total with tax ->", total)

# A bad comment restates the code:
#     total = total + 1     # add one to total
# A good comment states something the code cannot:
#     total = total + 1     # the header row counts as data; the exporter drops it

# Commenting out a line disables it while you debug.
print("step 1")
# print("step 2 — silenced while I check step 1")
print("step 3")

# A # inside a string is just a character.
print("# this is not a comment")


# ---------------------------------------------------------------------------
# 10. Naming: rules and conventions
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("10. Names")
print("=" * 70)

user_name = "ada"  # snake_case: the Python convention (PEP 8)
_internal = "private by convention"  # a leading underscore means "internal"
name2 = "digits are fine, just not first"
MAX_RETRIES = 3  # UPPER_SNAKE_CASE means "constant: do not reassign"
print(user_name, _internal, name2, MAX_RETRIES)

# Names are case-sensitive: these are three different names.
total = 1
Total = 2
TOTAL = 3
print("total, Total, TOTAL ->", total, Total, TOTAL)

print("Illegal, each a SyntaxError:  2name = 1   user-name = 1   class = 1")
print("Legal but wrong style:        wordsPerMinute = 250  (camelCase)")
print("Legal but dangerous:          list = [1, 2, 3]  (shadows the builtin)")
# Proof that shadowing is real, without breaking the rest of this file:
print("builtins we must not overwrite: list, dict, str, int, sum, type, id, input")


# ---------------------------------------------------------------------------
# 11. Reading error messages
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("11. Reading errors: last line first")
print("=" * 70)

print("SyntaxError  — Python could not parse the file; NOTHING ran.")
print("    print('hi'        ->  SyntaxError: '(' was never closed")
print("    if x > 5          ->  SyntaxError: expected ':'")
print("    Check the reported line AND the line above it.")
print()
print("NameError    — the name does not exist at that moment.")
print("    print(totl)       ->  NameError: name 'totl' is not defined")
print("    Causes: typo, wrong case, used before assigned, missing quotes.")
print()
print("TypeError    — right name, wrong kind of value.")
print('    "Age: " + 36      ->  TypeError: can only concatenate str')
print()
print("ValueError   — right kind of value, unusable content.")
print("    int('abc')        ->  ValueError: invalid literal for int()")
print()
print("The loop: read the last line, read the line number, look at THAT line,")
print("print the types involved, change ONE thing, re-run.")

# Putting the whole day together: a tiny report built from named values.
print()
print("=" * 70)
print("Putting it together")
print("=" * 70)

learner_name = "Ada"
day_number = 1
hours_planned = 4.0
finished = False

print("Learner:", learner_name, sep=" ")
print("Day:", day_number, "of 21")
print("Hours planned:", hours_planned)
print("Finished:", finished)
print("Types:", type(learner_name).__name__, type(day_number).__name__,
      type(hours_planned).__name__, type(finished).__name__, sep=" ")
print("-" * 30)
print("Summary line: " + learner_name + " is on day " + str(day_number) + ".")

print()
print("Done. Now open exercises.py in this folder.")
