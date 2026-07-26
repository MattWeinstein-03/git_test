# Day 08 — Functions

> **Time:** ~4 hours  |  **Prerequisites:** Day 07

## What you'll be able to do after today
- Write a function with `def`, call it with positional and keyword arguments, and explain the difference between a parameter and an argument.
- Give parameters default values, and avoid the mutable-default trap that bites every beginner exactly once.
- Accept any number of arguments with `*args` and `**kwargs`, and say when that is a good idea and when it is laziness.
- Return values (including several at once via a tuple) instead of printing them, and explain why that distinction decides whether your code is reusable.
- Predict whether a name inside a function refers to a local variable, a global, or a shadowed outer name.
- Write a docstring and type hints that describe a function honestly, and state exactly what type hints do *not* do when the program runs.
- Take a 40-line blob of straight-line code and refactor it into small, named, testable functions.

## Why this matters

Week 1 you wrote code in a straight line: read some data, loop over it, print a result. That works until the file is 200 lines long and you need "the same thing as before but for a different city", at which point you copy-paste the block and change two numbers. Two weeks later there are five copies and a bug fixed in three of them.

A function is the tool that stops that. It gives a chunk of behaviour a name, a documented input, and a documented output. Named behaviour can be tested, reused, and reasoned about one piece at a time — and "one piece at a time" is the only way humans handle programs bigger than a screen. Every other topic in this course (classes, modules, tests, decorators) is built on top of functions. Today is the hinge of the course.

---

## 1. What a function actually is

A function is a named, reusable block of code that takes inputs and (usually) produces an output.

You have already used functions: `len("abc")`, `print("hi")`, `sorted([3, 1, 2])`. Today you write your own.

```python
def add(a, b):
    return a + b

result = add(2, 3)
print(result)
```

Prints `5`.

The anatomy, line by line:

```
def      add      (a, b)      :
^        ^        ^           ^
keyword  name     parameters  start of the indented body
```

- `def` tells Python "a function definition follows".
- `add` is the name you will call it by. Same rules as variable names: `lower_snake_case`, no spaces.
- `(a, b)` is the **parameter list**: local names that will be filled in when the function is called.
- The `:` starts a block; everything indented below it is the **body**.
- `return a + b` computes a value and hands it back to whoever called the function.

Two separate moments in time, and beginners routinely confuse them:

1. **Definition time** — Python reads `def add(a, b):` and creates a function object. It does *not* run the body. A syntax error in the body is caught here; a logic error is not.
2. **Call time** — you write `add(2, 3)`, and now the body runs with `a = 2` and `b = 3`.

```python
def broken(x):
    return x + undefined_name   # no error yet — the body has not run

print("still fine here")        # prints
broken(1)                       # NameError now, at call time
```

> **Gotcha:** `add` and `add()` are different things. `add` is the function object itself (you can store it in a variable, put it in a list, pass it to another function). `add()` *calls* it. `print(add)` shows something like `<function add at 0x10a2f3d80>`; `print(add(1, 2))` shows `3`. If you ever see `<function ... at 0x...>` in your output, you forgot the parentheses.

---

## 2. Parameters vs arguments (the words matter)

- A **parameter** is the name in the definition. It's a slot.
- An **argument** is the actual value you pass at the call site. It fills the slot.

```python
def area(width, height):   # width, height are PARAMETERS
    return width * height

area(3, 4)                 # 3 and 4 are ARGUMENTS
```

You will read error messages like `area() missing 1 required positional argument: 'height'`. That message uses both words precisely, and now you can decode it: the slot named `height` never got a value.

Interviewers ask this. More importantly, documentation assumes you know it.

---

## 3. Positional and keyword arguments

By default, arguments are matched to parameters **by position**:

```python
def introduce(name, city):
    return f"{name} lives in {city}"

print(introduce("Ada", "London"))   # Ada lives in London
print(introduce("London", "Ada"))   # London lives in Ada  <- silently wrong
```

Nothing crashed in the second call. Python has no idea which one is a name. You can remove that whole category of bug by passing arguments **by keyword**:

```python
print(introduce(city="London", name="Ada"))   # Ada lives in London
```

Keyword arguments can be given in any order, because the name does the matching, not the position.

Rules you have to obey:

```python
introduce("Ada", city="London")     # ok: positional first, then keyword
introduce(name="Ada", "London")     # SyntaxError: positional argument follows keyword argument
introduce("Ada", name="Ada2")       # TypeError: got multiple values for argument 'name'
```

Practical style rule used in real codebases: **pass booleans and numbers-with-unclear-meaning by keyword.** Compare:

```python
send_report(data, True, False)                        # true what? false what?
send_report(data, include_totals=True, dry_run=False) # obvious
```

> **Gotcha:** once a parameter name is public, renaming it breaks every caller who used it as a keyword. Choose parameter names as carefully as function names.

---

## 4. Default values

A parameter with a default becomes optional:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Ada"))                    # Hello, Ada!
print(greet("Ada", "Good morning"))    # Good morning, Ada!
print(greet("Ada", greeting="Yo"))     # Yo, Ada!
```

Parameters with defaults must come **after** parameters without them, otherwise Python cannot tell what a lone positional argument means:

```python
def bad(greeting="Hello", name):   # SyntaxError: non-default argument follows default argument
    ...
```

### 4.1 The mutable-default trap

This is the single most famous Python gotcha. Read it twice.

```python
def add_item(item, basket=[]):     # DANGER: never do this
    basket.append(item)
    return basket
```

Full demonstration:

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket

print(add_item("apple"))    # ['apple']
print(add_item("pear"))     # ['apple', 'pear']   <- the apple is still there
```

Why: the default value is evaluated **once, at definition time**, and stored on the function object. Every call that omits `basket` gets *the same list*. You can see the evidence:

```python
print(add_item.__defaults__)   # (['apple', 'pear'],)
```

The fix is a two-line pattern you will use for the rest of your career:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []          # a fresh list per call
    basket.append(item)
    return basket
```

And the behaviour you wanted:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket

print(add_item("apple"))    # ['apple']
print(add_item("pear"))     # ['pear']   <- correct
```

Rule: **never use a list, dict, or set as a default value.** Immutable defaults (`0`, `""`, `None`, `False`, `(1, 2)`) are safe because nothing can mutate them.

> **Gotcha:** the same trap applies to any expression evaluated at definition time, such as `def log(msg, when=time.time())`. That timestamp is frozen at import. Use `when=None` and compute inside.

---

## 5. `return` vs printing

`print` shows a value to a human. `return` hands a value back to the program. They are not interchangeable, and confusing them is the #1 reason beginner functions "don't work".

```python
def double_print(n):
    print(n * 2)

def double_return(n):
    return n * 2

a = double_print(5)     # prints 10
b = double_return(5)    # prints nothing
print(a)                # None
print(b)                # 10
```

A function with no `return` statement returns `None`. `None` is a real value meaning "nothing here"; it is not an error.

Why it matters: you cannot build with `print`. `double_return(5) + 1` works. `double_print(5) + 1` raises `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`.

```python
total = double_return(3) + double_return(4)   # 14 — composable
```

`return` also exits the function immediately:

```python
def sign(n):
    if n > 0:
        return "positive"
    if n < 0:
        return "negative"
    return "zero"          # only reached when neither branch returned

print(sign(-4))            # negative
```

Nothing after a `return` in the same block runs. That is a feature: early `return` for edge cases keeps the rest of the body free of deep nesting. This is called a **guard clause**:

```python
def average(numbers):
    if not numbers:            # guard: handle the weird case and leave
        return 0.0
    return sum(numbers) / len(numbers)
```

> **Gotcha:** `return` inside a loop exits the *whole function*, not just the loop. If you meant to stop the loop only, you want `break`.

---

## 6. Returning several values with a tuple

Python functions return exactly one object — but a tuple is one object holding many values, so this looks like multiple returns:

```python
def min_max(numbers):
    return min(numbers), max(numbers)      # parentheses optional; this is a tuple

low, high = min_max([4, 9, 1, 7])          # tuple unpacking (Day 5)
print(low, high)                           # 1 9

pair = min_max([4, 9, 1, 7])
print(pair)                                # (1, 9)
print(type(pair))                          # <class 'tuple'>
```

Guidance: two or three related values as a tuple is idiomatic (`low, high`). Five values as a tuple is a bug factory — the caller has to remember the order. When you get there, return a dict with named keys, and after Day 12, a small class or dataclass.

```python
def stats(numbers):
    return {"count": len(numbers), "total": sum(numbers), "mean": sum(numbers) / len(numbers)}

result = stats([1, 2, 3])
print(result["mean"])       # 2.0
```

Use `_` as the name for a value you are deliberately ignoring: `low, _ = min_max(data)`.

---

## 7. `*args` and `**kwargs`

Sometimes you genuinely do not know how many arguments there will be.

`*args` collects extra **positional** arguments into a tuple:

```python
def total(*numbers):
    result = 0
    for n in numbers:
        result += n
    return result

print(total())            # 0
print(total(1, 2, 3))     # 6
print(total(1, 2, 3, 4))  # 10
```

`**kwargs` collects extra **keyword** arguments into a dict:

```python
def make_tag(name, **attributes):
    parts = [name]
    for key in sorted(attributes):                  # sorted for predictable output
        parts.append(f'{key}="{attributes[key]}"')
    return "<" + " ".join(parts) + ">"

print(make_tag("a", href="/home", id="link1"))      # <a href="/home" id="link1">
```

The `*` and `**` are the syntax; `args` and `kwargs` are merely the conventional names. `def total(*numbers)` is the same mechanism with a better name — prefer a descriptive name when you know what the values are.

The same symbols work in the other direction, at the call site, to **unpack** a sequence or dict into arguments:

```python
def volume(length, width, height):
    return length * width * height

dims = (2, 3, 4)
print(volume(*dims))                       # 24 — same as volume(2, 3, 4)

named = {"length": 2, "width": 3, "height": 4}
print(volume(**named))                     # 24 — same as volume(length=2, ...)
```

Full parameter order in a definition: normal parameters, then defaults, then `*args`, then `**kwargs`.

```python
def f(a, b=2, *extra, **options):
    return a, b, extra, options

print(f(1))                      # (1, 2, (), {})
print(f(1, 3, 4, 5, mode="x"))   # (1, 3, (4, 5), {'mode': 'x'})
```

> **Gotcha:** `*args`/`**kwargs` destroy your documentation. A signature of `def process(*args, **kwargs)` tells a reader nothing, and your editor cannot help them. Use it when you are genuinely forwarding arguments to something else, or when the count is truly unbounded (`total`, `max`). Otherwise name your parameters.

---

## 8. Scope: local, global, and shadowing

A **scope** is a region of code where a name means something. Every function call creates a fresh local scope.

```python
def f():
    x = 10          # local to f
    print(x)

f()                 # 10
print(x)            # NameError: name 'x' is not defined
```

Locals are born at call time and die when the function returns. This is what makes functions safe to reuse: your `total` variable cannot be clobbered by someone else's `total`.

Reading an outer name works fine:

```python
TAX_RATE = 0.2                 # module level = "global" in Python terms

def with_tax(price):
    return price * (1 + TAX_RATE)   # reads the global, fine

print(with_tax(100))           # 120.0
```

**Assigning** to a name anywhere in a function makes it local for the whole function:

```python
count = 0

def bump():
    count = count + 1     # UnboundLocalError: cannot access local variable 'count'
    return count
```

Python saw `count =` and decided `count` is local; then the right-hand side tried to read the local before it had a value. The keyword `global` overrides that decision:

```python
count = 0

def bump():
    global count
    count = count + 1
    return count

print(bump(), bump(), count)   # 1 2 2
```

Now: **do not do this.** `global` means any part of the program can change the value, so understanding one function requires reading all of them. The professional version passes the value in and returns the new one:

```python
def bump(count):
    return count + 1

count = 0
count = bump(count)     # explicit, testable
```

Legitimate module-level globals are **constants** — written `UPPER_SNAKE_CASE`, assigned once, never mutated (`TAX_RATE`, `MAX_RETRIES`, `DEFAULT_ENCODING`).

### 8.1 Shadowing

Shadowing is using a local name that hides an outer one:

```python
name = "global Ada"

def show():
    name = "local Grace"    # shadows the global inside this function only
    print(name)

show()          # local Grace
print(name)     # global Ada
```

Shadowing a *variable* is usually harmless. Shadowing a *builtin* is how you lose an afternoon:

```python
list = [1, 2, 3]        # you have just destroyed the list() function in this scope
print(list("abc"))      # TypeError: 'list' object is not callable
```

Names to never use as variables: `list`, `dict`, `set`, `str`, `int`, `sum`, `min`, `max`, `type`, `id`, `input`, `next`, `object`, `bytes`, `format`. When you want one anyway, add a trailing underscore: `list_`, `type_`.

### 8.2 The LEGB rule

When Python resolves a name it looks, in order:

- **L**ocal — this function's own names
- **E**nclosing — a surrounding function's names (Day 16, closures)
- **G**lobal — module level
- **B**uiltin — `len`, `print`, `sum`, ...

First match wins. That single sentence explains every scope question you will ever have.

---

## 9. Docstrings

A docstring is a string literal as the very first statement of a function. It is not a comment; it is stored on the function and readable at runtime.

```python
def apply_discount(price, percent=10.0):
    """Return `price` reduced by `percent` percent.

    Args:
        price: The original price, in whole currency units.
        percent: How much to knock off, 0-100. Defaults to 10.

    Returns:
        The discounted price as a float.

    Examples:
        >>> apply_discount(100)
        90.0
        >>> apply_discount(50, percent=50)
        25.0
    """
    return price * (1 - percent / 100)

print(apply_discount.__doc__.splitlines()[0])   # Return `price` reduced by `percent` percent.
help(apply_discount)                            # prints the signature plus the docstring
```

Conventions worth following:
- Triple double quotes, always, even for one line.
- First line: one sentence, imperative mood ("Return the total", not "Returns" or "This function will").
- Then a blank line, then details.
- Document *what and why*, not *how* — the code already says how.
- Every non-obvious function gets examples. Examples are the part readers actually read.

> **Gotcha:** a comment above the `def` is invisible to `help()`, to your editor's tooltip, and to documentation tools. Put the explanation inside the function as a docstring.

---

## 10. Type hints — what they do and what they emphatically do not do

You have been seeing these all course. Now the full story.

```python
def repeat(text: str, times: int = 2) -> str:
    """Return `text` repeated `times` times."""
    return text * times
```

- `text: str` — the *annotation* for parameter `text` is `str`.
- `times: int = 2` — annotation plus default.
- `-> str` — the return annotation.

Common notations you need to read:

```python
def f(a: int, b: float, c: str, d: bool) -> None: ...
def g(items: list[str]) -> dict[str, int]: ...          # list of str -> dict of str->int
def h(pair: tuple[int, int]) -> set[str]: ...
def i(value: str | None) -> int | None: ...             # "or None", the optional pattern
def j(numbers: list[int | float]) -> float: ...
```

`-> None` is the honest annotation for a function that only has side effects (it prints, it writes a file) and returns nothing.

### What they do

1. **Document** the function for humans, in a form that cannot drift into prose.
2. Let your **editor** autocomplete and warn you (`"abc" - 1` gets underlined).
3. Let a **static type checker** — `mypy`, run separately, Day 18 — read your whole codebase and prove there are no type mismatches, before you ship.

### What they do NOT do

**Nothing at runtime. They are not checked. They do not convert.**

```python
def repeat(text: str, times: int = 2) -> str:
    return text * times

print(repeat(5, 3))       # 15  <- no error, no conversion, wrong "str"
print(repeat("ab", 3))    # ababab
```

Python happily multiplied the integer. The annotation was a note to humans and tools; the interpreter shrugged. Internalise this:

> Type hints are documentation the computer can check **when you ask it to**, not a runtime guarantee. If bad input must be rejected while the program runs, *you* write the check and raise an error (Day 9).

```python
def repeat(text: str, times: int = 2) -> str:
    if not isinstance(text, str):                     # a real runtime check
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    return text * times
```

Where do the annotations actually live? On the function object:

```python
print(repeat.__annotations__)   # {'text': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
```

> **Gotcha:** `list[str]` (lowercase, built-in) works from Python 3.9. Older code says `List[str]` with `from typing import List`. Both are correct in their era; write the lowercase form.

---

## 11. Pure functions vs side effects

A **pure** function:
1. returns the same output for the same input, every time, and
2. changes nothing outside itself.

```python
def add_tax(price: float, rate: float) -> float:   # pure
    return price * (1 + rate)
```

A function with **side effects** does something to the world: prints, writes a file, mutates an argument, changes a global, sends an email, asks for input.

```python
def add_tax_and_log(prices: list[float], rate: float) -> None:   # impure
    for i in range(len(prices)):
        prices[i] = prices[i] * (1 + rate)      # mutates the caller's list
    print("prices updated")                     # touches the terminal
```

Pure functions are the ones you can test in one line, cache, reuse, and reason about. Side effects are unavoidable — a program that changes nothing is useless — so the goal is not purity everywhere, it is **separation**:

> Keep the calculating in pure functions. Keep the printing, reading, and writing in a thin layer at the edge.

Mutation deserves a specific warning. Arguments are passed by *object reference*: rebinding a parameter does not affect the caller, but mutating a mutable object does.

```python
def rebind(items: list[int]) -> None:
    items = [99]              # only the local name changes

def mutate(items: list[int]) -> None:
    items.append(99)          # the caller's list changes

data = [1]
rebind(data)
print(data)      # [1]
mutate(data)
print(data)      # [1, 99]
```

If you must transform a list, prefer returning a new one and say so in the name:

```python
def with_tax(prices: list[float], rate: float) -> list[float]:
    result = []
    for p in prices:
        result.append(p * (1 + rate))
    return result
```

Naming convention that communicates intent: `sorted(x)` returns a new list, `x.sort()` mutates. `get_*` / `calculate_*` / `format_*` suggest pure; `save_*` / `update_*` / `print_*` / `send_*` announce side effects.

---

## 12. Decomposition: turning a blob into functions

The skill, not the syntax. Signs a chunk of code should become a function:

- You can describe it in one short sentence ("work out the shipping cost") — that sentence is the function name.
- You copy-pasted it.
- It needs a comment to explain what the next ten lines do.
- Its middle is deeply indented.
- You want to test it but cannot without running everything.

Heuristics:
- One job per function. If the name needs "and", split it.
- Aim for a body you can see without scrolling (roughly under 20 lines).
- Few parameters (0–3 ideal). A long parameter list means the data wants to be grouped (Day 12).
- Name functions with a verb: `calculate_total`, `load_orders`, `format_receipt`. Name predicates with `is_`/`has_`: `is_valid_email`.

### 12.1 Before — 40 lines of Week-1 style code

This works. It is also unreadable, untestable, and unreusable.

```python
orders = [
    {"id": 1, "customer": "ada", "items": [("widget", 2, 9.99), ("bolt", 10, 0.5)]},
    {"id": 2, "customer": "grace", "items": [("gizmo", 1, 24.0)]},
    {"id": 3, "customer": "ada", "items": [("widget", 1, 9.99)]},
]

customer_totals = {}
grand_total = 0.0
for order in orders:
    subtotal = 0.0
    for name, qty, price in order["items"]:
        subtotal += qty * price
    if subtotal > 20:
        shipping = 0.0
    else:
        shipping = 4.95
    tax = subtotal * 0.2
    total = subtotal + shipping + tax
    grand_total += total
    customer = order["customer"]
    if customer in customer_totals:
        customer_totals[customer] += total
    else:
        customer_totals[customer] = total
    print("Order " + str(order["id"]) + " for " + customer.title())
    print("  subtotal: " + format(subtotal, ".2f"))
    print("  shipping: " + format(shipping, ".2f"))
    print("  tax:      " + format(tax, ".2f"))
    print("  TOTAL:    " + format(total, ".2f"))

print("-" * 30)
print("Grand total: " + format(grand_total, ".2f"))
best = ""
best_value = -1.0
for customer in customer_totals:
    if customer_totals[customer] > best_value:
        best = customer
        best_value = customer_totals[customer]
print("Best customer: " + best.title() + " (" + format(best_value, ".2f") + ")")
```

Problems, concretely:
- To test the free-shipping threshold you must run the whole script and read printed text.
- The tax rate `0.2` and threshold `20` are buried in the middle of a loop.
- Calculation and printing are welded together, so you cannot reuse the maths in a web app or a report.
- The "best customer" loop is a generic idea trapped inside this specific script.

### 12.2 After — the same behaviour, decomposed

```python
TAX_RATE = 0.2
FREE_SHIPPING_THRESHOLD = 20.0
FLAT_SHIPPING = 4.95


def line_total(quantity: int, unit_price: float) -> float:
    """Return the cost of one order line."""
    return quantity * unit_price


def order_subtotal(items: list[tuple[str, int, float]]) -> float:
    """Return the sum of all line totals in `items`."""
    subtotal = 0.0
    for _name, quantity, unit_price in items:
        subtotal += line_total(quantity, unit_price)
    return subtotal


def shipping_for(subtotal: float) -> float:
    """Return shipping cost: free above the threshold, flat rate below."""
    if subtotal > FREE_SHIPPING_THRESHOLD:
        return 0.0
    return FLAT_SHIPPING


def price_order(items: list[tuple[str, int, float]]) -> dict[str, float]:
    """Return subtotal, shipping, tax and total for one order's items."""
    subtotal = order_subtotal(items)
    shipping = shipping_for(subtotal)
    tax = subtotal * TAX_RATE
    return {
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": subtotal + shipping + tax,
    }


def totals_by_customer(orders: list[dict]) -> dict[str, float]:
    """Return {customer: money spent} across all `orders`."""
    totals: dict[str, float] = {}
    for order in orders:
        priced = price_order(order["items"])
        customer = order["customer"]
        totals[customer] = totals.get(customer, 0.0) + priced["total"]
    return totals


def best_customer(totals: dict[str, float]) -> tuple[str, float]:
    """Return the (name, amount) pair with the highest amount."""
    best_name = ""
    best_amount = -1.0
    for name, amount in totals.items():
        if amount > best_amount:
            best_name, best_amount = name, amount
    return best_name, best_amount


def format_order(order_id: int, customer: str, priced: dict[str, float]) -> str:
    """Return a printable multi-line receipt for one order."""
    lines = [f"Order {order_id} for {customer.title()}"]
    for label in ("subtotal", "shipping", "tax", "total"):
        lines.append(f"  {label + ':':<10}{priced[label]:>8.2f}")
    return "\n".join(lines)


def print_report(orders: list[dict]) -> None:
    """Print receipts for every order plus a summary. Side effects live here."""
    grand_total = 0.0
    for order in orders:
        priced = price_order(order["items"])
        grand_total += priced["total"]
        print(format_order(order["id"], order["customer"], priced))
    print("-" * 30)
    print(f"Grand total: {grand_total:.2f}")
    name, amount = best_customer(totals_by_customer(orders))
    print(f"Best customer: {name.title()} ({amount:.2f})")
```

What you bought:

| Before | After |
|---|---|
| Test the shipping rule by reading printed output | `shipping_for(19.99) == 4.95` |
| Rates buried in a loop | Named constants at the top |
| Maths + printing fused | `price_order` pure, `print_report` impure |
| "Best customer" logic single-use | `best_customer` works on any totals dict |
| One 40-line thing to understand | Seven things, each understandable alone |

It is more lines. That is fine: lines are cheap, understanding is expensive. Note the shape — a stack of pure functions with a single thin impure `print_report` at the top. That shape is the goal.

> **Gotcha:** do not decompose until you know what the code does. Write the ugly version, get it correct, *then* extract functions. Premature abstraction is worse than a long function because you invent the wrong boundaries.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Printing instead of returning | `None` where you expected a value; `TypeError: ... 'NoneType'` | `return` the value; print at the call site |
| Forgetting `()` when calling | `<function add at 0x...>` in output | `add(1, 2)` not `add` |
| Wrong number of arguments | `TypeError: f() missing 1 required positional argument: 'b'` | Check the signature; count the slots |
| Mutable default | Values leak between calls | `param=None` plus `if param is None:` |
| Default before non-default | `SyntaxError: non-default argument follows default argument` | Reorder: required first |
| Assigning to a global inside a function | `UnboundLocalError: cannot access local variable 'x'` | Pass it in, return it out |
| Shadowing a builtin | `TypeError: 'list' object is not callable` | Rename to `items`, `list_` |
| Expecting hints to validate | Wrong types sail through | Hints are for tools; `raise` for runtime checks |
| Positional after keyword | `SyntaxError: positional argument follows keyword argument` | Move positionals first |
| Missing `return` in one branch | `None` for some inputs | Ensure every path returns |
| Mutating an argument by accident | Caller's list/dict changed | Build and return a new object |
| One function doing five jobs | Untestable, name contains "and" | Split at the "and" |

---

## Mental model

A function is a **vending machine**.

```
        arguments in
             |
             v
   +---------------------+
   |  def price_order()  |   <- the machine: a named, documented process
   |                     |
   |  local scope: the   |   <- its private workspace, wiped after every use
   |  inside of the box  |
   +---------------------+
             |
             v
        return value out
```

- You interact only through the slot (parameters) and the tray (return value).
- What happens inside is nobody's business — that is why you can rewrite the body without breaking callers.
- The workspace is cleaned between uses. Nothing you did last time is still lying around... *unless* you left a mutable default inside the machine, which is exactly why that trap surprises people.
- A **pure** machine only ever hands things to the tray. An **impure** one also shakes the room: prints, writes files, edits the crate you handed it.

Programs are built by wiring machines together: small ones with obvious jobs, feeding one big one at the top.

---

## Practice

1. Run the demo and read every printed line against the code that produced it:

   ```bash
   python course/week2/day08_functions/examples.py
   ```

2. Open `course/week2/day08_functions/exercises.py`. Work top to bottom — they escalate. Replace each `raise NotImplementedError(...)` with your implementation. Read the docstring examples carefully; the tests use them.

3. Grade yourself from the course root:

   ```bash
   python check.py day08
   python check.py day08 -v      # full failure detail
   ```

4. When everything passes, compare your work with `solutions.py`. Different is fine; unclear is not. Ask yourself: could someone read the signature and docstring and use my function without reading the body?

5. Extra rep with real payoff: take your Day 07 project file, and extract at least four functions from it without changing its behaviour. Run it before and after and diff the output.

---

## Recall check

1. What is the difference between a parameter and an argument?
2. When is a default value evaluated, and why does that make `def f(x, acc=[])` dangerous?
3. What does a function return if it has no `return` statement?
4. How do you return two values from a function, and what type do you actually get back?
5. `*args` and `**kwargs` — which collects what, and what type is each inside the function?
6. Why does this raise `UnboundLocalError`, and what are the two fixes?
   ```python
   total = 0
   def add(n):
       total = total + n
       return total
   ```
7. Name three things type hints do and one thing they do not do.
8. Give two signs that a chunk of code should be pulled out into its own function.

<details>
<summary>Answers</summary>

1. A parameter is the name in the `def` line (a slot); an argument is the value passed at the call site (what fills the slot). Error messages use both words precisely.
2. At definition time, once. The same object is reused by every call that omits the argument, so mutations to a list/dict/set default persist across calls. Use `None` as the default and create the real value inside the body.
3. `None`.
4. `return a, b` — you get one object, a `tuple`. The caller usually unpacks it: `x, y = f()`.
5. `*args` collects extra positional arguments into a **tuple**; `**kwargs` collects extra keyword arguments into a **dict**. At a call site the same symbols unpack a sequence/dict into arguments instead.
6. The assignment `total = ...` makes `total` local for the entire function, so reading it on the right-hand side happens before it has a value. Fixes: (a) preferred — pass it in and return the new value: `def add(total, n): return total + n`; (b) `global total` at the top of the function, which you should avoid.
7. They document intent, drive editor autocomplete/warnings, and let a static checker such as mypy verify the whole codebase. They do **not** check or convert anything at runtime — `repeat(5, 3)` still runs.
8. Any two of: you can name it in one sentence; you copy-pasted it; it needs a comment to explain the next ten lines; it is deeply indented; you want to unit-test it in isolation; the value is needed in two places.

</details>
