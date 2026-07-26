"""Day 04 — Loops: runnable demonstrations.

Run me from the course root:

    python course/week1/day04_loops/examples.py

Every section number matches a section in LESSON.md. Predict each result before
you read it.

Nothing in this file loops forever and nothing asks for input, so it always
finishes on its own. Section 13 shows infinite loops as text, deliberately —
the one place you should type an infinite loop is your own REPL, where Ctrl-C
is one keystroke away.
"""

# ---------------------------------------------------------------------------
# 1. The problem loops solve
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. One piece of code, run many times")
print("=" * 70)

# Without a loop you would write print(1) ... print(5): five near-identical
# lines that cannot grow with the data.
for number in range(1, 6):
    print("counted:", number)

print("The shape does not change when the job gets bigger.")


# ---------------------------------------------------------------------------
# 2. while
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. while: repeat as long as a condition holds")
print("=" * 70)

count = 1  # SETUP: the variable exists before the loop
while count <= 3:  # CONDITION: checked before every turn, including the first
    print("count is", count)
    count += 1  # CHANGE: without this line the condition never becomes false
print("done, count is now", count, "-> the condition failed at 4")

# The condition is checked FIRST, so a loop can run zero times.
count = 10
while count < 5:
    print("never printed")
print("a while whose condition starts false runs its body zero times")

# 2.2 Counting down: the change does not have to be upwards.
seconds = 3
while seconds > 0:
    print("T minus", seconds)
    seconds -= 1
print("Liftoff!")

# 2.3 The case `for` cannot do: how many halvings until we drop below 1?
value = 1000.0
halvings = 0
while value >= 1:
    value = value / 2
    halvings += 1
print("1000 halved", halvings, "times ->", value)
print("No range could have known '10' in advance. The condition worked it out.")


# ---------------------------------------------------------------------------
# 3. for: once per item
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. for: once per item of an iterable")
print("=" * 70)

# A string is an iterable of its characters.
for letter in "cat":
    print("letter ->", letter)

# 3.1 The same job written both ways. The `for` version cannot be off by one.
word = "cat"
print("for   version:", end=" ")
for letter in word:
    print(letter, end=" ")
print()

print("while version:", end=" ")
i = 0
while i < len(word):
    print(word[i], end=" ")
    i += 1
print("   <- four chances to get the bookkeeping wrong")

# 3.2 for + if: the workhorse combination of Days 3 and 4.
text = "hello world"
vowels = 0
for character in text:
    if character in "aeiou":
        vowels += 1
print(f"vowels in {text!r} ->", vowels)


# ---------------------------------------------------------------------------
# 4. range in all three forms
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. range(stop) / range(start, stop) / range(start, stop, step)")
print("=" * 70)

print("range(5)        ->", end=" ")
for i in range(5):
    print(i, end=" ")
print("   <- starts at 0, stops BEFORE 5")

print("range(2, 6)     ->", end=" ")
for i in range(2, 6):
    print(i, end=" ")
print("   <- 6 - 2 = 4 values")

print("range(0, 10, 2) ->", end=" ")
for i in range(0, 10, 2):
    print(i, end=" ")
print("   <- every second number")

print("range(5, 0, -1) ->", end=" ")
for i in range(5, 0, -1):
    print(i, end=" ")
print("   <- counting down; 0 is excluded")

print("range(5, -1, -1)->", end=" ")
for i in range(5, -1, -1):
    print(i, end=" ")
print("   <- stop at -1 to include 0")

# The inclusive-counting idiom: to reach n, stop at n + 1.
total = 0
for i in range(1, 11):
    total += i
print("sum of 1..10 via range(1, 11) ->", total, " <- range(1, 10) would give 45")

# An empty range is silent, not an error.
turns = 0
for i in range(5, 0):  # start above stop with the default +1 step
    turns += 1
for i in range(0, 5, -1):  # walking down towards a stop above the start
    turns += 1
print("range(5, 0) and range(0, 5, -1) ran the body", turns, "times (no error)")

# 4.4 A range is a recipe, not a stored run of numbers.
print("print(range(5)) ->", range(5), " <- it prints its recipe, not its values")
print("len(range(5))   ->", len(range(5)))
print("type(range(5))  ->", type(range(5)).__name__)
shown = ""
for i in range(5):
    shown += str(i) + " "
print("to SEE the values you must consume them ->", shown)

# 4.5 range(len(text)) when the position matters as much as the character.
word = "cat"
for i in range(len(word)):
    print(f"index {i} holds {word[i]!r}")
print("range(len(x)) is exactly the valid indexes — never off by one.")
print("Careful: range needs whole numbers. range(len(word) / 2) is a TypeError")
print("because / gives a float; use // ->", len(word) // 2)


# ---------------------------------------------------------------------------
# 5. Choosing between while and for
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. Which loop?")
print("=" * 70)

print("If you can name the collection      -> for")
print("If you can only name the stop test  -> while")
print()
print(f"{'job':<38}{'loop':<8}")
print("-" * 46)
print(f"{'once per character of a string':<38}{'for':<8}")
print(f"{'a fixed number of turns':<38}{'for':<8}")
print(f"{'counting up, down or in steps':<38}{'for':<8}")
print(f"{'until the user types quit':<38}{'while':<8}")
print(f"{'until a value drops below a limit':<38}{'while':<8}")
print(f"{'retry until it works, max 3 goes':<38}{'while':<8}")
print()
print("A while ending in `i += 1` with condition `i < len(x)` is a for loop")
print("written the long way. Convert it.")


# ---------------------------------------------------------------------------
# 6. Accumulator patterns
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Accumulators: outside the loop, updated inside it")
print("=" * 70)

# 6.1 Running total — start at 0, the value that changes nothing when added.
total = 0
for i in range(1, 6):
    total += i
print("running total 1..5      ->", total)

# A product starts at 1. Starting it at 0 makes every answer 0.
product = 1
for i in range(1, 6):
    product *= i
print("product 1..5           ->", product)
broken = 0
for i in range(1, 6):
    broken *= i
print("product started at 0   ->", broken, " <- the classic accumulator bug")

# 6.2 Counter — add 1 when a test passes.
text = "Mississippi"
letter_count = 0
for character in text:
    if character == "s":
        letter_count += 1
print(f"'s' in {text!r}  ->", letter_count)

# 6.3 Max-so-far — hold the best candidate seen so far.
digits = "38207"
largest = int(digits[0])  # start from the first item, not from 0
for character in digits:
    value = int(character)
    if value > largest:
        largest = value
print(f"largest digit of {digits!r} ->", largest)

# Minimum is the same shape with the comparison flipped.
smallest = int(digits[0])
for character in digits:
    value = int(character)
    if value < smallest:
        smallest = value
print(f"smallest digit of {digits!r} ->", smallest)

# 6.4 Found-flag — start at False, only ever set it True.
text = "hello world"
found_z = False
for character in text:
    if character == "z":
        found_z = True
print(f"is there a 'z' in {text!r}? ->", found_z)

# 6.5 Building a string — start at "", the empty accumulator for text.
word = "python"
reversed_word = ""
for character in word:
    reversed_word = character + reversed_word  # new character goes in FRONT
print(f"{word!r} reversed by hand ->", reversed_word)

raw = "a1b2c3"
digits_only = ""
for character in raw:
    if character.isdigit():
        digits_only += character
print(f"digits kept from {raw!r} ->", digits_only)

# Separators: add one only when there is already something to separate from.
result = ""
for i in range(1, 4):
    if result:  # truthiness: non-empty means "something is already here"
        result += ", "
    result += str(i)
print("joined with separators ->", repr(result))

trailing = ""
for i in range(1, 4):
    trailing += str(i) + ", "
print("naive version          ->", repr(trailing), "then", repr(trailing[:-2]))

print()
print(f"{'question':<26}{'start':<10}{'update':<24}")
print("-" * 60)
print(f"{'what is the total?':<26}{'0':<10}{'total += value':<24}")
print(f"{'what is the product?':<26}{'1':<10}{'product *= value':<24}")
print(f"{'how many match?':<26}{'0':<10}{'count += 1 inside an if':<24}")
print(f"{'what is the largest?':<26}{'first':<10}{'if v > best: best = v':<24}")
print(f"{'is there one?':<26}{'False':<10}{'found = True':<24}")
print(f"{'what does text become?':<26}{'empty str':<10}{'out += piece':<24}")


# ---------------------------------------------------------------------------
# 7. break
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. break: leave the whole loop now")
print("=" * 70)

print("characters before the first space ->", end=" ")
for character in "hello world":
    if character == " ":
        break
    print(character, end="")
print()

# break changes the ANSWER here, not just the speed.
text = "hello world"
first = -1  # -1 means "not found", the same convention as str.find()
for i in range(len(text)):
    if text[i] == "o":
        first = i
        break
last = -1
for i in range(len(text)):
    if text[i] == "o":
        last = i  # no break: the last match overwrites the first
print(f"first 'o' in {text!r} (with break) ->", first)
print(f"last  'o' in {text!r} (no break)   ->", last)

# `while True` plus break: the exit lives in the middle of the body.
n = 1
while True:
    n *= 2
    if n > 100:
        break
print("first power of 2 above 100 ->", n)


# ---------------------------------------------------------------------------
# 8. continue
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. continue: skip this turn, keep looping")
print("=" * 70)

print("odd numbers 1..7 ->", end=" ")
for i in range(1, 8):
    if i % 2 == 0:
        continue
    print(i, end=" ")
print()

raw = "12a34"
total = 0
for character in raw:
    if not character.isdigit():
        continue  # reject early, then get on with the real work
    total += int(character)
print(f"digits of {raw!r} summed ->", total)

print("Gotcha: in a while loop, `continue` skips the increment too if the")
print("increment is at the bottom of the body — that is an instant hang.")


# ---------------------------------------------------------------------------
# 9. The loop else clause
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. else on a loop = 'finished without hitting break'")
print("=" * 70)

number = 91
divisor = 2
while divisor * divisor <= number:
    if number % divisor == 0:
        print(number, "is divisible by", divisor)
        break
    divisor += 1
else:
    print(number, "is prime")

number = 97
divisor = 2
while divisor * divisor <= number:
    if number % divisor == 0:
        print(number, "is divisible by", divisor)
        break
    divisor += 1
else:
    print(number, "is prime", " <- the else fired: no break happened")

for character in "hello":
    if character.isdigit():
        print("found a digit:", character)
        break
else:
    print("no digits in 'hello'   <- the search idiom, with no found-flag")

for character in "ab3":
    if character.isdigit():
        print("found a digit:", character, " <- break ran, so else did not")
        break
else:
    print("no digits in 'ab3'")

print("Read `else` as 'no break', not 'otherwise'. It also fires when the")
print("loop body never ran at all — zero turns means zero breaks.")


# ---------------------------------------------------------------------------
# 10. Sentinel loops
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("10. Sentinel loops: keep going until the stop value arrives")
print("=" * 70)

print("The real shape needs input(), which this file must not call:")
print("    while True:")
print("        reply = input('amount (or done): ')")
print("        if reply == 'done':   # the sentinel")
print("            break")
print("        total += int(reply)")
print()

# The same shape with a character as the sentinel.
data = "4,2,9#7,7,7"  # everything after the # is someone else's problem
total = 0
for character in data:
    if character == "#":
        break
    if character.isdigit():
        total += int(character)
print(f"digits before the '#' in {data!r} ->", total)

# A while sentinel with an index — note the ORDER of the two conditions.
data = "abc.def"
i = 0
before_dot = ""
while i < len(data) and data[i] != ".":
    before_dot += data[i]
    i += 1
print(f"text before the '.' in {data!r} ->", repr(before_dot))
print("`i < len(data)` MUST come first: short-circuiting is what stops")
print("data[i] being evaluated once i has run off the end.")

# Proof that the same loop is safe on a string with no sentinel in it at all.
data = "abcdef"
i = 0
collected = ""
while i < len(data) and data[i] != ".":
    collected += data[i]
    i += 1
print(f"no '.' in {data!r} -> collected everything:", repr(collected))


# ---------------------------------------------------------------------------
# 11. Nested loops
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("11. Nested loops: the inner loop runs in full on every outer turn")
print("=" * 70)

for row in range(3):
    for column in range(2):
        print(f"row={row} column={column}")
print("3 outer turns x 2 inner turns = 6 lines. Multiply the counts.")

print()
print("11.1 a rectangle (end='' keeps the row on one line):")
for row in range(3):
    for column in range(5):
        print("*", end="")
    print()  # finish the row

print()
print("11.2 a triangle (the inner count depends on the outer variable):")
for row in range(1, 5):
    for column in range(row):
        print("*", end="")
    print()

print()
print("...and the same shape without the inner loop, using string repetition:")
size = 4
for row in range(1, size + 1):
    print(" " * (size - row) + "*" * row)

print()
print("11.3 building a grid as a string instead of printing it:")
grid = ""
for row in range(3):
    for column in range(3):
        grid += "#"
    grid += "\n"
print("repr ->", repr(grid))
print(grid, end="")

grid = ""
for row in range(3):
    if grid:
        grid += "\n"  # separator BEFORE each row except the first
    grid += "#" * 3
print("no trailing newline ->", repr(grid))

print()
print("11.4 a times table, aligned with Day 2 format specs:")
for row in range(1, 4):
    line = ""
    for column in range(1, 4):
        line += f"{row * column:>4}"
    print(line)


# ---------------------------------------------------------------------------
# 12. Off-by-one errors
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("12. Off-by-one: one too many, or one too few")
print("=" * 70)

wanted = ""
for i in range(1, 11):
    wanted += str(i) + " "
print("range(1, 11) ->", wanted, " <- 1 to 10 inclusive: correct")

missing = ""
for i in range(1, 10):
    missing += str(i) + " "
print("range(1, 10) ->", missing, " <- 10 is silently missing")

zero_based = ""
for i in range(10):
    zero_based += str(i) + " "
print("range(10)    ->", zero_based, " <- ten values, but from 0")

word = "cat"
print()
print(f"{word!r} has len {len(word)}, so its valid indexes are 0..{len(word) - 1}")
i = 0
while i < len(word):  # `<` is correct
    print(f"  word[{i}] -> {word[i]!r}")
    i += 1
print("  `while i <= len(word)` would try word[3] -> IndexError")

print()
print("Diagnosis table:")
print(f"{'symptom':<42}{'likely cause':<30}")
print("-" * 72)
print(f"{'IndexError on the last turn':<42}{'<= where < was meant':<30}")
print(f"{'the last item is missing':<42}{'range(1, n) not range(1, n+1)':<30}")
print(f"{'the body never runs':<42}{'start/stop wrong way round':<30}")
print(f"{'out by one item worth':<42}{'accumulator start value':<30}")
print()
print("Fastest debugger: print(f'{i=}') inside the loop.")
for i in range(1, 4):
    print(f"  {i=}")


# ---------------------------------------------------------------------------
# 13. Infinite loops, and how to stop one
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("13. Infinite loops: causes, and Ctrl-C")
print("=" * 70)

print("None of these are run here on purpose. Read them, then try one in the")
print("REPL where Ctrl-C is one keystroke away.")
print()
print("  1. forgot the change:      while count < 5: print(count)")
print("  2. changed the wrong one:  while i < 5: j += 1")
print("  3. moving away from exit:  while count > 0: count += 1")
print("  4. while True, no break:   while True: print('still here')")
print("  5. continue jumping over the increment (section 8's gotcha)")
print()
print("To stop one: press Ctrl-C in the terminal. Python stops with")
print("    KeyboardInterrupt")
print("and the traceback names the line the loop was spinning on. That is not")
print("a crash you caused with bad syntax — it is you, interrupting.")
print()

# 13.3 The safety belt: a turn limit turns a possible hang into a wrong answer.
value = 27
steps = 0
while value != 1 and steps < 1000:  # the second test is the safety belt
    if value % 2 == 0:
        value = value // 2
    else:
        value = value * 3 + 1
    steps += 1
print("Collatz from 27 reached 1 in", steps, "steps (guard: max 1000)")
print("Nobody has proved that loop always terminates — hence the guard.")


# ---------------------------------------------------------------------------
# Putting it together — one pass over some text, five answers at once
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("Putting it together — five accumulators, one loop")
print("=" * 70)

sentence = "Loops turn 1 idea into 100 lines of work."

characters = 0  # running total
digit_count = 0  # counter
letters_only = ""  # string accumulator
biggest_gap = 0  # max-so-far (longest run of non-space characters)
current_gap = 0
has_digit = False  # found-flag

for character in sentence:
    characters += 1
    if character.isdigit():
        digit_count += 1
        has_digit = True
    if character.isalpha():
        letters_only += character
    if character == " ":
        current_gap = 0
    else:
        current_gap += 1
        if current_gap > biggest_gap:
            biggest_gap = current_gap

print(f"{'text':<22}{sentence!r}")
print(f"{'characters':<22}{characters}")
print(f"{'digit characters':<22}{digit_count}")
print(f"{'contains a digit':<22}{has_digit}")
print(f"{'longest word run':<22}{biggest_gap}")
print(f"{'letters only':<22}{letters_only!r}")
print()
print("One pass, five answers. Every one of them is an accumulator with a")
print("different starting value — that is the whole of section 6.")

print()
print("Done. Now open exercises.py in this folder.")
