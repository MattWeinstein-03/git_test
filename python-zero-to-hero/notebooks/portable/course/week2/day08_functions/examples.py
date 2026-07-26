"""Day 08 — Functions: runnable demonstrations.

Run me from the course root:

    python course/week2/day08_functions/examples.py

Every section number matches a section in LESSON.md. Read the code, read the
printed output, and check that you could have predicted the output.
"""

# ---------------------------------------------------------------------------
# 1. What a function actually is
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. Defining and calling")
print("=" * 70)


def add(a, b):
    """Return the sum of a and b."""
    # The body does not run until somebody calls add(...).
    return a + b


# `add` is the function object; `add(2, 3)` is a call that produces a value.
print("add               ->", add)  # <function add at 0x...>
print("add(2, 3)         ->", add(2, 3))  # 5
print("type(add)         ->", type(add))  # <class 'function'>
print("expected: a function object, then 5, then <class 'function'>")

# Functions are values. You can put one in a variable or a list.
operation = add  # no parentheses: we copy the function itself
print("operation(10, 5)  ->", operation(10, 5), "(same function, new name)")


# ---------------------------------------------------------------------------
# 2. Parameters vs arguments
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. Parameters vs arguments")
print("=" * 70)


def area(width, height):  # width and height are PARAMETERS (slots)
    return width * height


print("area(3, 4) ->", area(3, 4), "  # 3 and 4 are ARGUMENTS (the values)")

# Calling with too few arguments is an error. We catch it here only so the
# script keeps running; Day 9 explains try/except properly.
try:
    area(3)
except TypeError as error:
    print("area(3) raised TypeError:", error)
    print("expected: 'missing 1 required positional argument: height'")


# ---------------------------------------------------------------------------
# 3. Positional and keyword arguments
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Positional vs keyword arguments")
print("=" * 70)


def introduce(name, city):
    return f"{name} lives in {city}"


print("positional, right order:", introduce("Ada", "London"))
print("positional, wrong order:", introduce("London", "Ada"), " <- silently wrong")
print("keyword, any order:     ", introduce(city="London", name="Ada"))
print("mixed (positional first):", introduce("Ada", city="London"))


# ---------------------------------------------------------------------------
# 4. Default values, and the mutable-default trap
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Defaults")
print("=" * 70)


def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


print(greet("Ada"))  # uses the default
print(greet("Ada", "Good morning"))  # overrides positionally
print(greet("Ada", greeting="Yo"))  # overrides by keyword


# THE TRAP. The default list is created ONCE, when Python reads the def line.
def broken_add_item(item, basket=[]):
    basket.append(item)
    return basket


print()
print("broken_add_item('apple') ->", broken_add_item("apple"))
print("broken_add_item('pear')  ->", broken_add_item("pear"), " <- apple is STILL there")
# The evidence: the default value lives on the function object and got mutated.
print("broken_add_item.__defaults__ ->", broken_add_item.__defaults__)


# THE FIX: use None as the default and build a fresh object inside the body.
def add_item(item, basket=None):
    if basket is None:
        basket = []  # a brand new list on every call that omits `basket`
    basket.append(item)
    return basket


print("add_item('apple')        ->", add_item("apple"))
print("add_item('pear')         ->", add_item("pear"), " <- correct: independent calls")
print("add_item('fig', ['nut']) ->", add_item("fig", ["nut"]), " <- caller's list used")


# ---------------------------------------------------------------------------
# 5. return vs print
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. return vs print")
print("=" * 70)


def double_print(n):
    print("  (inside double_print, showing)", n * 2)  # side effect only


def double_return(n):
    return n * 2  # produces a value the caller can use


a = double_print(5)
b = double_return(5)
print("value returned by double_print ->", a, "(functions with no return give None)")
print("value returned by double_return ->", b)
# Only the returning version composes into bigger expressions.
print("double_return(3) + double_return(4) ->", double_return(3) + double_return(4))


def sign(n):
    # Guard clauses: handle a case and leave immediately.
    if n > 0:
        return "positive"
    if n < 0:
        return "negative"
    return "zero"


for value in (5, -5, 0):
    print(f"sign({value}) -> {sign(value)}")


# ---------------------------------------------------------------------------
# 6. Returning several values with a tuple
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. Multiple return values")
print("=" * 70)


def min_max(numbers):
    return min(numbers), max(numbers)  # one tuple, two values inside


data = [4, 9, 1, 7]
pair = min_max(data)
print("min_max(data) ->", pair, "type:", type(pair).__name__)

low, high = min_max(data)  # tuple unpacking, from Day 5
print(f"unpacked: low={low} high={high}")

_, biggest = min_max(data)  # `_` means "I am ignoring this one"
print("ignored the first value, kept:", biggest)


def stats(numbers):
    # More than 2-3 values? Name them with a dict so callers cannot mix up order.
    return {
        "count": len(numbers),
        "total": sum(numbers),
        "mean": sum(numbers) / len(numbers),
    }


print("stats([1, 2, 3]) ->", stats([1, 2, 3]))


# ---------------------------------------------------------------------------
# 7. *args and **kwargs
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. *args and **kwargs")
print("=" * 70)


def total(*numbers):  # `numbers` is a TUPLE of everything passed positionally
    result = 0
    for n in numbers:
        result += n
    return result


print("total()            ->", total(), " (empty tuple sums to 0)")
print("total(1, 2, 3)     ->", total(1, 2, 3))
print("total(1, 2, 3, 4)  ->", total(1, 2, 3, 4))


def make_tag(name, **attributes):  # `attributes` is a DICT of keyword arguments
    parts = [name]
    for key in sorted(attributes):  # sorted -> predictable, testable output
        parts.append(f'{key}="{attributes[key]}"')
    return "<" + " ".join(parts) + ">"


print("make_tag('br')                        ->", make_tag("br"))
print("make_tag('a', href='/home', id='top') ->", make_tag("a", href="/home", id="top"))


def describe(a, b=2, *extra, **options):
    # The full order: required, defaults, *args, **kwargs.
    return f"a={a} b={b} extra={extra} options={options}"


print(describe(1))
print(describe(1, 3, 4, 5, mode="fast", debug=True))


def volume(length, width, height):
    return length * width * height


dims_tuple = (2, 3, 4)
dims_dict = {"length": 2, "width": 3, "height": 4}
# At the CALL SITE, * and ** unpack instead of collect.
print("volume(*dims_tuple) ->", volume(*dims_tuple))
print("volume(**dims_dict) ->", volume(**dims_dict))


# ---------------------------------------------------------------------------
# 8. Scope: local, global, shadowing
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. Scope")
print("=" * 70)

TAX_RATE = 0.2  # module-level CONSTANT: read by functions, never reassigned


def with_tax(price):
    return price * (1 + TAX_RATE)  # reading an outer name is fine


print("with_tax(100) ->", with_tax(100))


def local_only():
    secret = "inside"  # born on call, dies on return
    return secret


print("local_only() ->", local_only())
try:
    print(secret)  # noqa: F821 - deliberately broken to show the error
except NameError as error:
    print("reading `secret` outside the function raised NameError:", error)

counter = 0


def broken_bump():
    # Assigning to `counter` makes it local for the whole function, so reading
    # it on the right-hand side fails.
    counter = counter + 1  # noqa: F823
    return counter


try:
    broken_bump()
except UnboundLocalError as error:
    print("broken_bump() raised UnboundLocalError:", error)


def bump(current):
    """The professional fix: take the value in, hand the new value out."""
    return current + 1


counter = bump(counter)
counter = bump(counter)
print("counter after two explicit bumps ->", counter)

name = "global Ada"


def shadow_demo():
    name = "local Grace"  # shadows the global INSIDE this function only
    return name


print("shadow_demo() ->", shadow_demo(), "| global name is still ->", name)


# ---------------------------------------------------------------------------
# 9. Docstrings
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. Docstrings")
print("=" * 70)


def apply_discount(price, percent=10.0):
    """Return `price` reduced by `percent` percent.

    Args:
        price: original price in whole currency units.
        percent: how much to knock off, 0-100. Defaults to 10.

    Returns:
        The discounted price as a float.

    Examples:
        apply_discount(100) -> 90.0
        apply_discount(50, percent=50) -> 25.0
    """
    return price * (1 - percent / 100)


print("apply_discount(100)            ->", apply_discount(100))
print("apply_discount(50, percent=50) ->", apply_discount(50, percent=50))
# The docstring is data attached to the function, not a comment.
print("first docstring line ->", apply_discount.__doc__.splitlines()[0])


# ---------------------------------------------------------------------------
# 10. Type hints: documentation, NOT runtime enforcement
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("10. Type hints")
print("=" * 70)


def repeat(text: str, times: int = 2) -> str:
    """Return `text` repeated `times` times."""
    return text * times


print("repeat('ab', 3) ->", repeat("ab", 3))
# Nothing checks the annotation at runtime: an int sails straight through.
print("repeat(5, 3)    ->", repeat(5, 3), " <- hints did NOT stop this")
print("annotations live on the function:", repeat.__annotations__)


def repeat_checked(text: str, times: int = 2) -> str:
    """Same, but with a REAL runtime check that you wrote yourself."""
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    return text * times


try:
    repeat_checked(5, 3)
except TypeError as error:
    print("repeat_checked(5, 3) raised TypeError:", error)


# ---------------------------------------------------------------------------
# 11. Pure functions vs side effects
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("11. Pure vs side-effecting")
print("=" * 70)


def add_tax(price: float, rate: float) -> float:
    """Pure: same input -> same output, touches nothing outside itself."""
    return price * (1 + rate)


def apply_tax_in_place(prices: list[float], rate: float) -> None:
    """Impure: mutates the caller's list and prints. Returns None."""
    for index in range(len(prices)):
        prices[index] = round(prices[index] * (1 + rate), 2)
    print("  (side effect: prices list was modified in place)")


def with_tax(prices: list[float], rate: float) -> list[float]:
    """Pure alternative: build and return a NEW list."""
    result = []
    for price in prices:
        result.append(round(price * (1 + rate), 2))
    return result


print("add_tax(100, 0.2) ->", add_tax(100, 0.2))

original = [10.0, 20.0]
copy_returned = with_tax(original, 0.2)
print("after with_tax:  original =", original, "returned =", copy_returned)

apply_tax_in_place(original, 0.2)
print("after apply_tax_in_place: original =", original, " <- caller's data changed")


def rebind(items: list[int]) -> None:
    items = [99]  # rebinding the local name does nothing to the caller


def mutate(items: list[int]) -> None:
    items.append(99)  # mutating the object DOES affect the caller


numbers = [1]
rebind(numbers)
print("after rebind(numbers) ->", numbers)
mutate(numbers)
print("after mutate(numbers) ->", numbers)


# ---------------------------------------------------------------------------
# 12. Decomposition: the before/after refactoring from the lesson
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("12. Decomposition — same behaviour, seven small functions")
print("=" * 70)

ORDERS = [
    {"id": 1, "customer": "ada", "items": [("widget", 2, 9.99), ("bolt", 10, 0.5)]},
    {"id": 2, "customer": "grace", "items": [("gizmo", 1, 24.0)]},
    {"id": 3, "customer": "ada", "items": [("widget", 1, 9.99)]},
]

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
    """Return shipping: free above the threshold, flat rate below it."""
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
    for customer, amount in totals.items():
        if amount > best_amount:
            best_name, best_amount = customer, amount
    return best_name, best_amount


def format_order(order_id: int, customer: str, priced: dict[str, float]) -> str:
    """Return a printable multi-line receipt for one order."""
    lines = [f"Order {order_id} for {customer.title()}"]
    for label in ("subtotal", "shipping", "tax", "total"):
        lines.append(f"  {label + ':':<10}{priced[label]:>8.2f}")
    return "\n".join(lines)


def print_report(orders: list[dict]) -> None:
    """Print receipts plus a summary. ALL the side effects live here."""
    grand_total = 0.0
    for order in orders:
        priced = price_order(order["items"])
        grand_total += priced["total"]
        print(format_order(order["id"], order["customer"], priced))
    print("-" * 30)
    print(f"Grand total: {grand_total:.2f}")
    top_name, top_amount = best_customer(totals_by_customer(orders))
    print(f"Best customer: {top_name.title()} ({top_amount:.2f})")


print_report(ORDERS)

print()
print("Each piece is now testable on its own, with no printing involved:")
print("  order_subtotal([('bolt', 10, 0.5)]) ->", order_subtotal([("bolt", 10, 0.5)]))
print("  shipping_for(19.99) ->", shipping_for(19.99), "(below threshold)")
print("  shipping_for(20.01) ->", shipping_for(20.01), "(free)")
print("  totals_by_customer(ORDERS) ->", totals_by_customer(ORDERS))
print("  best_customer({'a': 1.0, 'b': 9.0}) ->", best_customer({"a": 1.0, "b": 9.0}))

print()
print("Done. Now open exercises.py in this folder.")
