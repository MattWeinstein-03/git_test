"""Day 02 — Numbers and Strings: runnable demonstrations.

Run me from the course root:

    python course/week1/day02_numbers_and_strings/examples.py

Every section number matches a section in LESSON.md. Predict each result before
you read it. The interesting lines are the ones where you were wrong.
"""

# ---------------------------------------------------------------------------
# 1. Arithmetic
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. The seven arithmetic operators")
print("=" * 70)

print("7 + 3  ->", 7 + 3)
print("7 - 3  ->", 7 - 3)
print("7 * 3  ->", 7 * 3)
print("7 / 3  ->", 7 / 3, " <- true division, ALWAYS a float")
print("7 // 3 ->", 7 // 3, " <- floor division: how many whole 3s fit")
print("7 % 3  ->", 7 % 3, " <- modulo: what is left over")
print("7 ** 3 ->", 7**3, " <- exponentiation")

# / gives a float even when the answer is exact.
print("10 / 2  ->", 10 / 2, "of type", type(10 / 2).__name__)
print("10 // 2 ->", 10 // 2, "of type", type(10 // 2).__name__)

# // FLOORS: it rounds down, towards negative infinity, not towards zero.
print("-7 / 2  ->", -7 / 2)
print("-7 // 2 ->", -7 // 2, " <- NOT -3: floor goes down")
print("int(-7 / 2) ->", int(-7 / 2), " <- int() truncates towards zero")

# % answers real questions.
print("48 % 2 == 0 (even?)   ->", 48 % 2 == 0)
print("1234 % 10 (last digit)->", 1234 % 10)
print("(20 + 15) % 24 (clock)->", (20 + 15) % 24)

# // and % together split a quantity into two parts.
total_seconds = 4000
print(total_seconds, "seconds is", total_seconds // 60, "min", total_seconds % 60, "sec")
print("divmod(4000, 60) ->", divmod(4000, 60), " <- both answers at once")

# ** is the only operator that groups right to left.
print("2 ** 3 ** 2 ->", 2**3**2, " <- 2 ** (3 ** 2) = 2 ** 9")
print("(2 ** 3) ** 2 ->", (2**3) ** 2)
print("2 ** 0.5 ->", 2**0.5, " <- a fractional power is a root")

# Compound assignment is shorthand, nothing more.
total = 10
total += 5  # 15
total *= 2  # 30
total //= 4  # 7
print("10, then += 5, *= 2, //= 4 ->", total, "(15, then 30, then 7)")

# Rounding and friends.
print("round(3.14159, 2) ->", round(3.14159, 2))
print("round(4.7)        ->", round(4.7))
print("abs(-7)           ->", abs(-7))
print("min(3, 9, 2)      ->", min(3, 9, 2), "| max(3, 9, 2) ->", max(3, 9, 2))
# Banker's rounding: halves go to the nearest EVEN number.
print("round(0.5), round(1.5), round(2.5), round(3.5) ->",
      round(0.5), round(1.5), round(2.5), round(3.5))


# ---------------------------------------------------------------------------
# 2. Operator precedence
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. Precedence: not left to right")
print("=" * 70)

print("2 + 3 * 4    ->", 2 + 3 * 4, " <- * binds tighter than +")
print("(2 + 3) * 4  ->", (2 + 3) * 4)
print("10 - 2 - 3   ->", 10 - 2 - 3, " <- equal precedence: left to right")
print("-2 ** 2      ->", -(2**2), " <- ** binds tighter than unary minus")
print("(-2) ** 2    ->", (-2) ** 2)
print("10 / 5 * 2   ->", 10 / 5 * 2)
print("1 + 2 * 3 ** 2 ->", 1 + 2 * 3**2, " <- 3**2=9, 2*9=18, 1+18=19")
print("7 % 3 * 2    ->", 7 % 3 * 2, " <- % and * are equal: (7%3)*2")
print("Rule of thumb: if a reader would have to think, add brackets.")


# ---------------------------------------------------------------------------
# 3. Floats are approximate
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Why 0.1 + 0.2 is not 0.3")
print("=" * 70)

print("0.1 + 0.2        ->", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3 ->", 0.1 + 0.2 == 0.3, " <- False, and that is correct")

# The stored values, to 20 decimal places. None of them is what you typed.
print("0.1 stored as", format(0.1, ".20f"))
print("0.2 stored as", format(0.2, ".20f"))
print("0.3 stored as", format(0.3, ".20f"))

# Workaround 1: compare with a tolerance.
difference = abs((0.1 + 0.2) - 0.3)
print("abs(sum - 0.3) < 1e-9 ->", difference < 1e-9)

# Workaround 2: round for display, at the last possible moment.
print("round(0.1 + 0.2, 2) ->", round(0.1 + 0.2, 2))
print(f'f"{{0.1 + 0.2:.2f}}" -> {0.1 + 0.2:.2f}')

# Errors accumulate. Ten additions of 0.1 do not make 1.0.
running = 0.0
running += 0.1
running += 0.1
running += 0.1
running += 0.1
running += 0.1
running += 0.1
running += 0.1
running += 0.1
running += 0.1
running += 0.1
print("0.1 added ten times ->", running, "| == 1.0 ->", running == 1.0)

# Workaround 3, for money: count the smallest unit as a whole number.
price_pence = 1999  # £19.99, stored exactly
total_pence = price_pence * 3
print("3 x 1999 pence ->", total_pence, "pence = £" + str(total_pence / 100))
print("round(2.675, 2) ->", round(2.675, 2), " <- not 2.68; the stored value is lower")


# ---------------------------------------------------------------------------
# 4. Casting
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Converting between types")
print("=" * 70)

print("int('42')   ->", int("42"), "of type", type(int("42")).__name__)
print("int(' 42 ') ->", int(" 42 "), " <- surrounding whitespace is fine")
print("int('-7')   ->", int("-7"))
print("int(3.9)    ->", int(3.9), " <- truncates towards zero, does not round")
print("int(-3.9)   ->", int(-3.9))
print("int(True)   ->", int(True), "| int(False) ->", int(False))

print("float('3.5') ->", float("3.5"))
print("float('42')  ->", float("42"))
print("float('1e3') ->", float("1e3"), " <- scientific notation")
print("float(7)     ->", float(7))

print("str(42)   ->", repr(str(42)), "| str(None) ->", repr(str(None)))
print("str() never fails: every value can describe itself as text.")

# Which conversions blow up, and with which error:
print()
print("These raise ValueError (right type, unusable content):")
print("    int('3.5')    int('abc')    int('')    int('1,000')    float('abc')")
print("These raise TypeError (wrong kind of thing entirely):")
print("    int(None)     float(None)")
print("Two steps get you from '3.5' to a whole number:")
print("    int(float('3.5'))   ->", int(float("3.5")), "(truncate)")
print("    round(float('3.5')) ->", round(float("3.5")), "(round)")

# A string of digits is not a number.
print('"10" > "9"  ->', "10" > "9", " <- text compares character by character")
print("10 > 9      ->", 10 > 9, " <- convert first, then compare")


# ---------------------------------------------------------------------------
# 5. Indexing
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. Indexing: one character at a time")
print("=" * 70)

word = "Python"
print("word         ->", word)
print("word[0]      ->", word[0], " <- indexes start at 0")
print("word[1]      ->", word[1])
print("word[5]      ->", word[5], " <- the last one, len - 1")
print("len(word)    ->", len(word))
print("word[6]      ->  IndexError: string index out of range")
print()
print("  P  y  t  h  o  n")
print("  0  1  2  3  4  5   <- index from the left")
print(" -6 -5 -4 -3 -2 -1   <- index from the right")
print()
print("word[-1] ->", word[-1], "| word[-2] ->", word[-2], "| word[-6] ->", word[-6])

filename = "report.csv"
print("filename[len(filename) - 1] ->", filename[len(filename) - 1], "(correct, ugly)")
print("filename[-1]                ->", filename[-1], "(same, obvious)")

# There is no separate character type: one character is a string of length 1.
letter = word[0]
print("word[0] is a", type(letter).__name__, "of length", len(letter))


# ---------------------------------------------------------------------------
# 6. Slicing
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Slicing: text[start:stop:step]")
print("=" * 70)

text = "Python"
print("text[0:2]  ->", repr(text[0:2]), " <- indexes 0 and 1; stop is EXCLUDED")
print("text[2:5]  ->", repr(text[2:5]))
print("text[:3]   ->", repr(text[:3]), " <- from the start")
print("text[3:]   ->", repr(text[3:]), " <- to the end")
print("text[:]    ->", repr(text[:]), " <- a full copy")
print("text[::2]  ->", repr(text[::2]), " <- every second character")
print("text[1::2] ->", repr(text[1::2]))
print("text[::-1] ->", repr(text[::-1]), " <- reversed")

# Why stop is excluded: the numbers work out.
print("len(text[0:3]) ->", len(text[0:3]), "= 3 - 0, no mental arithmetic")
print("text[:4] + text[4:] ->", repr(text[:4] + text[4:]), " <- slices join up exactly")

# Slices clip; indexes raise.
print("text[2:100] ->", repr(text[2:100]), " <- clipped, no error")
print("text[100:]  ->", repr(text[100:]), " <- empty, no error")
print("text[4:2]   ->", repr(text[4:2]), " <- start after stop: empty")
print("text[100]   ->  IndexError")

# Negative slicing is where this becomes genuinely useful.
print()
print("filename[-4:] ->", repr(filename[-4:]), " <- the extension")
print("filename[:-4] ->", repr(filename[:-4]), " <- everything except it")

card = "4111111111111234"
print("card[-4:]            ->", card[-4:])
print("'*' * 12 + card[-4:] ->", "*" * 12 + card[-4:])

backwards = "abcdefg"
print("'abcdefg'[::-2]  ->", repr(backwards[::-2]))
print("'abcdefg'[5:2:-1]->", repr(backwards[5:2:-1]), " <- walking backwards")
print("'abcdefg'[2:5:-1]->", repr(backwards[2:5:-1]), " <- impossible: empty")


# ---------------------------------------------------------------------------
# 7. Immutability
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. Strings cannot be changed")
print("=" * 70)

print("word[0] = 'X' raises TypeError: 'str' object does not support item assignment")

name = "ada"
name.upper()  # the result is computed and thrown away
print("after a bare name.upper() ->", name, " <- unchanged!")
name = name.upper()  # store it, and now something happened
print("after name = name.upper() ->", name)

# To "change" a string, build a new one.
word = "python"
word = "P" + word[1:]
print("'P' + word[1:] ->", word)
print("'hello world'.replace('world', 'there') ->", "hello world".replace("world", "there"))

# Immutability is why two names can share one string with no risk.
one = "shared"
two = one
print("id(one) == id(two) ->", id(one) == id(two), " <- one object, two names, safe")


# ---------------------------------------------------------------------------
# 8. The string methods you will actually use
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. String methods")
print("=" * 70)

raw = "  hello  \n"
print("raw            ->", repr(raw))
print("raw.strip()    ->", repr(raw.strip()))
print("raw.lstrip()   ->", repr(raw.lstrip()))
print("raw.rstrip()   ->", repr(raw.rstrip()))
print("'...hi!!!'.strip('.!') ->", repr("...hi!!!".strip(".!")))
print("'hello'.strip('lo')    ->", repr("hello".strip("lo")),
      " <- a CHARACTER SET, not a substring")

text = "hELLo woRLD"
print()
print("text.lower()      ->", text.lower())
print("text.upper()      ->", text.upper())
print("text.title()      ->", text.title())
print("text.capitalize() ->", text.capitalize())
print("'YES'.lower() == 'yes' ->", "YES".lower() == "yes")
print("'Straße'.lower()    ->", "Straße".lower())
print("'Straße'.casefold() ->", "Straße".casefold(), " <- casefold for comparing")
print('"o\'brien mcdonald".title() ->', "o'brien mcdonald".title(),
      " <- title() is naive about apostrophes")

print()
print("'a,b,c'.split(',')       ->", "a,b,c".split(","))
print("'one two  three'.split() ->", "one two  three".split(), " <- any whitespace run")
print("'a,b,,c'.split(',')      ->", "a,b,,c".split(","), " <- keeps the empty field")
print("'a-b-c'.split('-', 1)    ->", "a-b-c".split("-", 1), " <- maxsplit")
print("'-'.join(['2024','03','01']) ->", "-".join(["2024", "03", "01"]))
print("' '.join(['hello','world'])  ->", " ".join(["hello", "world"]))

# The whitespace-normalising idiom you will reuse on Day 7.
messy = "  too    many   spaces\there  "
print("messy                   ->", repr(messy))
print("' '.join(messy.split()) ->", repr(" ".join(messy.split())))

print()
print("'a-b-c'.replace('-', '')  ->", "a-b-c".replace("-", ""))
print("'aaa'.replace('a','b',2)  ->", "aaa".replace("a", "b", 2))
print("'hello'.replace('z','x')  ->", "hello".replace("z", "x"), " <- no match, no error")

name = "report.csv"
print()
print("name.startswith('rep')          ->", name.startswith("rep"))
print("name.endswith('.csv')           ->", name.endswith(".csv"))
print("name.endswith(('.csv', '.tsv')) ->", name.endswith((".csv", ".tsv")))
print("'port' in name                  ->", "port" in name)
print("'xyz' in name                   ->", "xyz" in name)

print()
print("'42'.isdigit()   ->", "42".isdigit())
print("'4.2'.isdigit()  ->", "4.2".isdigit(), " <- the dot is not a digit")
print("'-42'.isdigit()  ->", "-42".isdigit(), " <- nor is the minus sign")
print("''.isdigit()     ->", "".isdigit(), " <- empty is never True")
print("'abc'.isalpha()  ->", "abc".isalpha(), "| 'abc123'.isalnum() ->", "abc123".isalnum())

sentence = "the cat sat on the mat"
print()
print("sentence.find('cat')    ->", sentence.find("cat"))
print("sentence.find('dog')    ->", sentence.find("dog"), " <- -1 means not found")
print("sentence.find('the', 1) ->", sentence.find("the", 1))
print("sentence.count('the')   ->", sentence.count("the"))
print("sentence.count('t')     ->", sentence.count("t"))
print("Careful: -1 is truthy. Compare to -1, or just use `in`.")

print()
print("'ab'.ljust(6, '.')  ->", "ab".ljust(6, ".") + "|")
print("'ab'.rjust(6, '.')  ->", "ab".rjust(6, ".") + "|")
print("'ab'.center(6, '.') ->", "ab".center(6, ".") + "|")
print("'7'.zfill(3)        ->", "7".zfill(3))


# ---------------------------------------------------------------------------
# 9 & 10. f-strings
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9-10. Building strings: f-strings win")
print("=" * 70)

person = "Ada"
age = 36

print("concatenation: " + "Name: " + person + ", age " + str(age))
print("print args:", "Name:", person + ",", "age", age)
print(f"f-string:      Name: {person}, age {age}")

print()
print(f"any expression works: {age + 1}, {person.upper()}, {len(person)}, {2 + 2}")
print(f"{{doubled braces}} print literally")

pi = 3.14159265
print()
print("Decimal places:")
print(f"  {{pi:.2f}} -> {pi:.2f}")
print(f"  {{pi:.0f}} -> {pi:.0f}")
print(f"  {{2:.2f}}  -> {2:.2f}   <- pads as well as truncates")

print("Width and alignment (the arrow points where the text goes):")
print(f"  {{'ab':<10}} -> [{'ab':<10}]")
print(f"  {{'ab':>10}} -> [{'ab':>10}]")
print(f"  {{'ab':^10}} -> [{'ab':^10}]")
print(f"  {{'ab':*^10}} -> [{'ab':*^10}]")
print(f"  strings default left:  [{'ab':10}]")
print(f"  numbers default right: [{42:10}]")

print("Thousands separators and more:")
print(f"  {{1234567:,}}       -> {1234567:,}")
print(f"  {{1234567.891:,.2f}} -> {1234567.891:,.2f}")
print(f"  {{1234.5678:>12,.2f}} -> [{1234.5678:>12,.2f}]")
print(f"  {{42:05d}}          -> {42:05d}")
print(f"  {{0.4567:.1%}}      -> {0.4567:.1%}")
print(f"  {{5:+d}}            -> {5:+d}")

print()
print("An aligned table with no manual space counting:")
print(f"{'Item':<12}{'Qty':>5}{'Price':>10}")
print("-" * 27)
print(f"{'widget':<12}{2:>5}{9.99:>10.2f}")
print(f"{'bolt':<12}{10:>5}{0.5:>10.2f}")
print(f"{'gizmo':<12}{1:>5}{24.0:>10.2f}")

# The = specifier: the fastest debugging tool in Python.
total = 42
print()
print("The = specifier prints the expression AND its value:")
print(f"  {total=}")
print(f"  {person=}      <- note the quotes: it uses repr()")
print(f"  {total * 2=}")
print(f"  {len(person)=}")
price = 1234.5678
print(f"  {price = }     <- spaces are allowed")
print(f"  {price=:.2f}   <- and format specs still work")

print()
print("Forget the f and you get the braces: ", "{person} is {age}")

print()
print("Done. Now open exercises.py in this folder.")
