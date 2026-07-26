# Day 12 — Classes

> **Time:** ~4 hours  |  **Prerequisites:** Day 11

## What you'll be able to do after today
- Recognise when a dict-of-dicts has outgrown itself, and replace it with a class for stated reasons.
- Write a class with `__init__`, instance attributes, and methods, and explain what `self` is without hand-waving.
- Tell the difference between a class attribute and an instance attribute, and predict which one a given assignment creates.
- Write `__repr__` (and, when it earns its place, `__str__`) so your objects are debuggable.
- Apply the `_private` convention and say what Python does and does not enforce.
- Replace a hand-written data-holding class with a `@dataclass`, and explain what the decorator generated for you.

## Why this matters

You already have containers: lists, tuples, dicts, sets. They are excellent, and for a while you can model anything with a dict of dicts. Then the program grows, and the cracks appear in a predictable order: every function needs six arguments, nothing validates the data so a typo in a key surfaces three hours later, the same "get the total" logic is copy-pasted in four places, and printing a record produces a wall of braces.

A class fixes all four at once by binding **data and the operations on that data** into one named thing. That is the entire idea. Objects are also the vocabulary of the ecosystem: `Path`, `Exception`, `DictReader`, every library you will ever import gives you objects. You have been using them since Day 1. Today you learn to make them, and — just as important — to know when not to.

---

## 1. Start from the pain: a dict-of-dicts that got out of hand

Here is an honest Week-1-style expense tracker. Nothing is wrong with it yet.

```python
expenses = [
    {"amount": 12.5, "category": "food", "date": "2024-03-01"},
    {"amount": 30.0, "category": "transport", "date": "2024-03-02"},
]

total = 0.0
for expense in expenses:
    total += expense["amount"]
print(total)              # 42.5
```

Now let it grow the way real code grows. Add validation, a formatted display, a per-category report, and a second module that also touches the data:

```python
def add_expense(expenses, amount, category, date):
    if amount <= 0:                                   # validation lives... here?
        raise ValueError(f"amount must be positive, got {amount}")
    if not category.strip():
        raise ValueError("category must not be empty")
    expenses.append({"amount": amount, "category": category, "date": date})

def format_expense(expense):
    return f"{expense['date']} {expense['category']:<10} {expense['amount']:>8.2f}"

def total_by_category(expenses):
    totals = {}
    for expense in expenses:
        key = expense["category"]
        totals[key] = totals.get(key, 0.0) + expense["amount"]
    return totals
```

Four specific problems, and they are not hypothetical:

**1. Nothing enforces the shape.** `{"amount": 5, "categry": "food"}` is a perfectly good dict. The typo is only discovered later, as a `KeyError` in an unrelated function, or worse, as a silently missing row in a report.

**2. Validation is optional.** `add_expense` checks the rules, but nothing stops anyone anywhere writing `expenses.append({"amount": -5})`. The rules live *next to* the data, not *in* it.

**3. The data and its operations drift apart.** `format_expense` and `total_by_category` both need intimate knowledge of the key names. Rename `"amount"` to `"value"` and you must find every dictionary subscript in the codebase — the compiler cannot help you, because to Python they are just strings.

**4. It is invisible when you debug.** `print(expenses[0])` gives `{'amount': 12.5, 'category': 'food', 'date': '2024-03-01'}`. Now imagine ten of those nested three levels deep in a traceback.

The same thing as a class:

```python
class Expense:
    def __init__(self, amount, category, date):
        if amount <= 0:
            raise ValueError(f"amount must be positive, got {amount}")
        if not category.strip():
            raise ValueError("category must not be empty")
        self.amount = amount
        self.category = category.strip().lower()
        self.date = date

    def formatted(self):
        return f"{self.date} {self.category:<10} {self.amount:>8.2f}"

    def __repr__(self):
        return f"Expense(amount={self.amount!r}, category={self.category!r}, date={self.date!r})"
```

```python
expense = Expense(12.5, "Food", "2024-03-01")
print(expense)                       # Expense(amount=12.5, category='food', date='2024-03-01')
print(expense.formatted())           # 2024-03-01 food          12.50
print(expense.amount)                # 12.5
Expense(-5, "food", "2024-03-01")    # ValueError: amount must be positive, got -5
```

What changed, precisely:

- **It is impossible to create an invalid `Expense`.** The only door in is `__init__`, and the rules live there. Validation moved from "please remember to call the right function" to "guaranteed by construction".
- **The name is documentation.** A function taking `expense: Expense` says more than `expense: dict`.
- **Operations live with their data.** `expense.formatted()` cannot drift out of sync with the fields.
- **Attribute typos fail loudly.** `expense.categry` is an `AttributeError` right there; `expense["categry"]` on a dict is a `KeyError` three functions away — but the real win is that your editor autocompletes `.category` and flags the typo before you run anything.
- **It prints usefully**, because you wrote `__repr__`.

> **Gotcha:** this is not "classes are better than dicts". A dict is exactly right for genuinely dynamic key-value data — parsed JSON, a config file, a counter, a cache. Reach for a class when a *thing* has a fixed set of fields, rules about what is valid, and behaviour of its own. Day 13's last section argues the other side.

---

## 2. `class`, instances, and what actually happens

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says woof"
```

Vocabulary, precisely:

- `Dog` is a **class**: a blueprint, a factory, a type. It is itself an object.
- `Dog("Rex", 3)` **instantiates** the class and produces an **instance** — a particular dog.
- `name` and `age` are **instance attributes**: data belonging to one specific dog.
- `bark` is a **method**: a function that belongs to the class, and is called on an instance.

```python
rex = Dog("Rex", 3)
fido = Dog("Fido", 7)

print(rex.name, rex.age)     # Rex 3
print(fido.name, fido.age)   # Fido 7   — a separate, independent object
print(rex.bark())            # Rex says woof
print(type(rex))             # <class '__main__.Dog'>
print(isinstance(rex, Dog))  # True
print(rex is fido)           # False — two distinct objects
```

What Python does when you write `Dog("Rex", 3)`:

1. Creates a new, empty object of type `Dog`.
2. Calls `Dog.__init__(new_object, "Rex", 3)` — passing the new object as the first argument.
3. `__init__` attaches attributes to it and returns nothing.
4. The expression evaluates to the new object.

`__init__` is not "the constructor" in the C++/Java sense; it is the **initialiser**, which runs *after* the object exists. (The actual creator is `__new__`, and you will not need it for years.) Notice the consequence: `__init__` must return `None`. Returning anything else is a `TypeError`.

Naming conventions, follow them: classes are `CapWords` (`BankAccount`, `ExpenseStore`), methods and attributes are `lower_snake_case`. Names with double underscores at both ends (`__init__`, `__repr__`) are "dunder" methods — Python's hooks, not yours to invent.

> **Gotcha:** `class Dog:` and `dog = Dog()` are different things, and the error `TypeError: Dog.__init__() missing 2 required positional arguments: 'name', 'age'` means you instantiated without the arguments `__init__` demands. Read it as an ordinary function-call error, because that is what it is.

---

## 3. `self`, demystified

`self` confuses beginners because it looks like magic. It is not. Here is the whole truth:

**`self` is just the first parameter of a method, and Python passes the instance into it for you.**

```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count
```

These two lines do exactly the same thing:

```python
counter = Counter()
print(counter.increment())        # 1  — the normal way
print(Counter.increment(counter))  # 2  — what Python actually does underneath
```

`counter.increment()` looks up `increment` on the class, and calls it with `counter` as the first argument. That is called a **bound method** — the instance is bound to the first parameter.

```python
print(Counter.increment)          # <function Counter.increment at 0x...>
print(counter.increment)          # <bound method Counter.increment of <Counter object ...>>
```

So:

- `self` is the *instance the method was called on*. Inside `rex.bark()`, `self` **is** `rex`.
- The name `self` is pure convention. `def bark(this)` works identically. Never do it — every Python programmer alive reads `self`.
- You must write it in the definition, and you must not pass it at the call site.
- `self.name = value` creates or updates an attribute *on that one instance*.
- Every method that touches instance data needs `self`. A method that does not is telling you it should be a plain function (or a `@staticmethod`, Day 13).

The two errors this produces, and their translation:

```python
class Broken:
    def greet():                      # forgot self
        return "hi"

Broken().greet()
# TypeError: Broken.greet() takes 0 positional arguments but 1 was given
#   translation: Python passed the instance; your method has nowhere to put it.
```

```python
class AlsoBroken:
    def __init__(self, name):
        name = name                   # forgot self.
    def greet(self):
        return f"hi {self.name}"

AlsoBroken("Ada").greet()
# AttributeError: 'AlsoBroken' object has no attribute 'name'
#   translation: you assigned a local variable that died when __init__ returned.
```

> **Gotcha:** `self` is not a keyword, so nothing warns you when you forget it. If a method mysteriously cannot see data you know you set, look for a missing `self.` on either the assignment or the read.

---

## 4. Class attributes vs instance attributes

An attribute defined in the class body belongs to the **class**, and is shared by every instance. An attribute assigned through `self` belongs to that **instance** alone.

```python
class Robot:
    population = 0                  # CLASS attribute: one copy, shared
    species = "robot"               # CLASS attribute: a shared constant

    def __init__(self, name):
        self.name = name            # INSTANCE attribute: one per robot
        Robot.population += 1       # deliberately update the shared counter
```

```python
r2 = Robot("R2-D2")
c3 = Robot("C-3PO")

print(r2.name, c3.name)          # R2-D2 C-3PO      — separate
print(Robot.population)          # 2                — shared
print(r2.population)             # 2                — found on the class
print(r2.species, c3.species)    # robot robot      — shared
```

The lookup rule, which explains everything else: reading `instance.attribute` looks on the **instance first**, then on the **class**. Writing `instance.attribute = value` *always* creates or updates it on the instance — it never touches the class.

```python
r2.species = "astromech"         # creates an INSTANCE attribute that shadows the class one
print(r2.species)                # astromech
print(c3.species)                # robot         — untouched
print(Robot.species)             # robot         — untouched
```

That asymmetry is why `Robot.population += 1` in `__init__` is written with the *class* name: `self.population += 1` would read the class value (say 2), add one, and store 3 as a new instance attribute, leaving the shared counter at 2 forever. A classic bug worth understanding once.

Legitimate uses for class attributes:

```python
class Account:
    INTEREST_RATE = 0.02          # a constant shared by all accounts
    VALID_TYPES = ("current", "savings")
    count = 0                     # a genuine shared counter
```

And the trap you already know from Day 8, in a new costume:

```python
class Basket:
    items = []                    # DANGER: one list shared by ALL baskets

    def add(self, item):
        self.items.append(item)   # mutates the CLASS's list

a, b = Basket(), Basket()
a.add("apple")
print(b.items)                    # ['apple']   <- b never added anything
```

Mutable class attributes are shared mutable state, exactly like a mutable default argument. The fix is the same in spirit: create it per instance.

```python
class Basket:
    def __init__(self):
        self.items = []           # a fresh list for every basket
```

> **Gotcha:** `instance.__dict__` shows only the instance's own attributes, which is the fastest way to see which of the two you have: `print(r2.__dict__)` gives `{'name': 'R2-D2', 'species': 'astromech'}` — no `population`, because that lives on the class.

---

## 5. Methods

A method is a function defined in a class body, and it can do anything a function can: take arguments, have defaults, return values, raise exceptions, be documented.

```python
class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0) -> None:
        """Open an account. A balance may be supplied, and must not be negative."""
        if balance < 0:
            raise ValueError(f"balance must not be negative, got {balance}")
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> float:
        """Add `amount` to the balance and return the new balance."""
        if amount <= 0:
            raise ValueError(f"deposit must be positive, got {amount}")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        """Take `amount` out, refusing to overdraw. Returns the new balance."""
        if amount <= 0:
            raise ValueError(f"withdrawal must be positive, got {amount}")
        if amount > self.balance:
            raise ValueError(f"cannot withdraw {amount} from {self.balance}")
        self.balance -= amount
        return self.balance

    def summary(self) -> str:
        """Return a one-line human-readable summary."""
        return f"{self.owner}: {self.balance:.2f}"
```

```python
account = BankAccount("Ada", 100.0)
print(account.deposit(50))       # 150.0
print(account.withdraw(30))      # 120.0
print(account.summary())         # Ada: 120.00
account.withdraw(1000)           # ValueError: cannot withdraw 1000 from 120.0
```

Design notes worth absorbing:

- **Methods that change state and methods that ask questions are different jobs.** `deposit` mutates; `summary` is a pure read. Mixing "compute a value and also modify three things" into one method is how classes become unpredictable.
- **Return `self.balance` rather than printing it.** Same Day 8 rule: a method that prints cannot be composed or tested.
- Methods can call each other through `self`: `self.summary()`. That is how you decompose a large method.
- A method that never mentions `self` does not need to be a method.
- Keep the invariants in one place: because `deposit`/`withdraw` are the only paths, the balance can never go negative. (Nothing stops `account.balance = -999` — see the next section for what Python does about that, which is: nothing, on purpose.)

---

## 6. `__repr__` vs `__str__`

Without either, your objects print like this:

```python
print(BankAccount("Ada", 10))
# <__main__.BankAccount object at 0x104b3e390>
```

That tells you the class and a memory address. It is useless in a traceback, in a list, in a debugger, in a log.

Two dunder methods control display, and the distinction is worth learning properly:

| | `__repr__` | `__str__` |
|---|---|---|
| Audience | **developers** | **end users** |
| Goal | unambiguous, ideally re-creatable | readable, friendly |
| Used by | the REPL, `repr()`, containers, debuggers, `!r` | `print()`, `str()`, f-strings |
| Fallback | none — Python's default is the `0x...` form | falls back to `__repr__` |

```python
class Money:
    def __init__(self, amount, currency="GBP"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        # Aim for something you could paste back into Python.
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"

    def __str__(self):
        # Aim for something you could show a user.
        return f"{self.amount:.2f} {self.currency}"
```

```python
price = Money(12.5)
print(repr(price))        # Money(amount=12.5, currency='GBP')
print(str(price))         # 12.50 GBP
print(price)              # 12.50 GBP        — print uses __str__
print(f"{price}")         # 12.50 GBP        — f-string uses __str__
print(f"{price!r}")       # Money(amount=12.5, currency='GBP')   — !r forces __repr__
print([price, price])     # [Money(amount=12.5, ...), Money(...)]  — containers use __repr__
```

That last line is the one that decides the rule of thumb: **always write `__repr__`; write `__str__` only when a friendlier form genuinely exists.** Because containers use `repr`, a list of ten objects with no `__repr__` is ten memory addresses — which is precisely when you needed to see the data.

Conventions for a good `__repr__`:
- Look like a constructor call: `ClassName(field=value, ...)`.
- Use `!r` on the values, so strings keep their quotes and `""` is visible.
- Include the fields that identify the object, not all forty of them.
- Never let it raise. A `__repr__` that crashes turns a small bug into an unreadable traceback.

> **Gotcha:** if you define only `__str__`, then `print(obj)` is pretty but `print([obj])` is still `<object at 0x...>`, because lists call `repr` on their contents. If you define only `__repr__`, both are useful. Hence: `__repr__` first.

---

## 7. Encapsulation and the `_private` convention

Other languages enforce privacy with keywords. Python does not. It uses a convention that is *entirely social*, and this is a deliberate design choice:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = 0.0          # "internal — do not touch from outside"
        self.set_celsius(celsius)     # reuse the validation

    def set_celsius(self, celsius: float) -> None:
        if celsius < -273.15:
            raise ValueError(f"below absolute zero: {celsius}")
        self._celsius = celsius

    def get_celsius(self) -> float:
        return self._celsius

    def get_fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32
```

The naming scale:

| Name | Means | Enforced? |
|---|---|---|
| `name` | public API. Use it, rely on it. | — |
| `_name` | internal. May change without warning. Do not touch from outside. | **No.** Nothing stops you. |
| `__name` | name-mangled to `_ClassName__name`; used to avoid clashes in subclasses. | Only lightly, and it is not "private". |
| `name_` | a public name that would otherwise collide with a keyword (`class_`, `type_`). | — |

```python
temperature = Temperature(21.0)
print(temperature.get_fahrenheit())   # 69.8
print(temperature._celsius)           # 21.0  — works! nothing is blocked
temperature._celsius = -500           # also "works", and now the object is nonsense
```

The Python position, worth understanding rather than resenting: the language trusts you, and the underscore is documentation about *support*, not a lock. It says "I may rename this tomorrow; if you depend on it, that is your risk." Libraries take this seriously — using someone's `_internal` is how your code breaks on their next release.

What this buys you in practice:

- A reader can tell your public surface (`get_celsius`, `set_celsius`) from your plumbing (`_celsius`) at a glance.
- You can refactor internals freely as long as the public names behave the same.
- Helper methods that exist only to keep a big method readable should be `_named`.

The getter/setter pair above is deliberately old-fashioned, and Java programmers write it out of habit. In Python it is usually unnecessary: start with a plain public attribute, and if you later need validation, `@property` upgrades it *without changing a single caller*. That is tomorrow's topic — the point being that Python does not need speculative getters "just in case".

> **Gotcha:** do not reach for `__double_underscore` names to get "real" privacy. It only mangles the name (`obj._Temperature__celsius` still works), it makes debugging awkward, and its actual purpose is avoiding accidental collisions in inheritance hierarchies.

---

## 8. `@dataclass`: the modern default for data holders

Look at how much of a class like this is mechanical:

```python
class Book:
    def __init__(self, title, author, year, tags=None):
        self.title = title
        self.author = author
        self.year = year
        self.tags = tags if tags is not None else []

    def __repr__(self):
        return (f"Book(title={self.title!r}, author={self.author!r}, "
                f"year={self.year!r}, tags={self.tags!r})")

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return (self.title, self.author, self.year, self.tags) == \
               (other.title, other.author, other.year, other.tags)
```

Every field is named four times, and none of that code contains an idea. `@dataclass` writes it for you from the annotations:

```python
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    author: str
    year: int
    tags: list[str] = field(default_factory=list)
```

That is the whole class, and it is equivalent — plus better:

```python
book = Book("Structure and Interpretation", "Abelson", 1985)
print(book)
# Book(title='Structure and Interpretation', author='Abelson', year=1985, tags=[])

print(book == Book("Structure and Interpretation", "Abelson", 1985))   # True
print(Book("A", "B", 1) == Book("A", "B", 2))                          # False
```

What the decorator generated: `__init__`, `__repr__`, and `__eq__`, from the annotated class attributes, in order.

Note what you got for free: **`__eq__` compares by value.** Two books with the same data are equal. Without it, Python compares identity, so two separately-created identical books are *not* equal — a surprise that bites people testing their code.

The features you will actually use:

```python
from dataclasses import dataclass, field

@dataclass
class Expense:
    amount: float
    category: str
    date: str
    note: str = ""                              # a default, like any parameter
    tags: list[str] = field(default_factory=list)   # the fix for mutable defaults

    def __post_init__(self) -> None:
        """Runs right after the generated __init__. The place for validation."""
        if self.amount <= 0:
            raise ValueError(f"amount must be positive, got {self.amount}")
        self.category = self.category.strip().lower()

    def formatted(self) -> str:                  # ordinary methods, as usual
        return f"{self.date} {self.category:<10} {self.amount:>8.2f}"
```

```python
expense = Expense(12.5, "  Food ", "2024-03-01")
print(expense.category)          # food          — __post_init__ normalised it
print(expense.formatted())       # 2024-03-01 food          12.50
Expense(-1, "food", "2024-03-01")  # ValueError: amount must be positive, got -1
```

Two rules that matter:

**`field(default_factory=list)`, never `tags: list[str] = []`.** The second is the Day 8 mutable-default trap, and dataclasses refuse to let you make it: you get `ValueError: mutable default <class 'list'> for field tags is not allowed`. A rare case of a language stopping a classic bug outright.

**Fields with defaults come after fields without**, exactly as with function parameters.

Other options worth knowing exist (`frozen=True` for immutable instances, `order=True` to generate `<`/`>`, `field(compare=False)`), and the helpers `dataclasses.asdict()` / `astuple()` / `replace()` are useful for serialisation:

```python
from dataclasses import asdict
print(asdict(expense))
# {'amount': 12.5, 'category': 'food', 'date': '2024-03-01', 'note': '', 'tags': []}
```

That last one is how a dataclass becomes JSON, which is exactly what the Day 14 project needs.

When *not* to use a dataclass: when the class is mostly behaviour rather than data (a `Store`, a `Parser`, a `Client`), or when construction is genuinely complicated. A dataclass is for things that *hold* data; a plain class is for things that *do* work.

> **Note on `@`:** you are using a decorator today, and that is fine — using one is easy, and `@dataclass` and `@property` (tomorrow) are too useful to postpone. *Writing* your own decorator is Day 16. For now: `@dataclass` above a class means "hand this class to the `dataclass` function, which returns an enhanced version of it".

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Forgetting `self` in a method definition | `TypeError: greet() takes 0 positional arguments but 1 was given` | `def greet(self):` |
| Assigning without `self.` in `__init__` | `AttributeError: 'X' object has no attribute 'name'` | `self.name = name` |
| Passing `self` at the call site | `TypeError: ... takes 1 positional argument but 2 were given` | `obj.greet()`, not `obj.greet(obj)` |
| Mutable class attribute | Every instance shares one list | Create it in `__init__` |
| `self.count += 1` for a shared counter | The class counter never moves | `ClassName.count += 1` |
| Returning a value from `__init__` | `TypeError: __init__() should return None` | Assign attributes; return nothing |
| No `__repr__` | `<__main__.Dog object at 0x...>` everywhere | Write `__repr__` first, `__str__` if useful |
| Only `__str__` | Lists of objects still print addresses | Containers use `__repr__` |
| Expecting `_private` to be enforced | Outsiders happily read `obj._x` | It is a convention; document your public API |
| `tags: list[str] = []` in a dataclass | `ValueError: mutable default ... is not allowed` | `field(default_factory=list)` |
| Comparing plain-class instances with `==` | `False` for identical data | `@dataclass`, or write `__eq__` (Day 13) |
| Fields with defaults before fields without | `TypeError: non-default argument follows default argument` | Reorder the fields |
| A class with one method and no state | Ceremony around a function | Just write the function |

---

## Mental model

A class is a **cookie cutter**; instances are the cookies.

```
   class Expense:            <- the cutter. One of these, defined once.
       amount, category      <- the shape it stamps out
       def formatted(self)   <- an operation every cookie can perform

   Expense(12.5, "food", ...)  ->  cookie #1 { amount: 12.5,  category: "food"  }
   Expense(30.0, "transport",) ->  cookie #2 { amount: 30.0,  category: "transp"}

   INSTANCE attribute  = icing on ONE cookie          (self.amount = ...)
   CLASS attribute     = a property of the CUTTER,
                         visible from every cookie    (population = 0)

   self                = "this cookie", handed to the method automatically.
                         cookie.formatted()  IS  Expense.formatted(cookie)

   __init__            = the stamping-and-decorating step. Runs once per
                         cookie, and is the only door in — which is why
                         validation belongs there.

   __repr__            = the label you write on the cookie so you can tell
                         which one it is at 3am.

   @dataclass          = a machine that writes __init__, __repr__ and __eq__
                         for you from the field list, because that code
                         contains no ideas.
```

One sentence: *a class binds data to the operations on that data, and guarantees — through `__init__` — that no invalid instance can exist.*

---

## Practice

1. Run the demo and read it against the lesson. Section 4 (class vs instance attributes) prints things people get wrong; predict each line before you read it:

   ```bash
   python course/week2/day12_classes/examples.py
   ```

2. Open `exercises.py`. Today you write classes, so the stubs are classes whose methods raise `NotImplementedError`. Replace them. Exercises 5 and 7 are dataclasses — the stub is a plain class you convert, so add the `@dataclass` decorator and the annotated fields.

3. Grade from the course root:

   ```bash
   python check.py day12
   python check.py day12 -v
   ```

4. Then, by hand: take the `Expense`/`total_by_category` dict code from section 1 and finish the conversion — an `Expense` class *and* a `Store` class holding a list of them, with `add`, `total`, and `total_by_category`. Keep it; tomorrow you will extend it, and Day 14's project is exactly this at full size.

---

## Recall check

1. Name four concrete problems a class solves that a dict-of-dicts does not.
2. What is `self`, and what are the two ways of writing the same method call that prove it?
3. What is the difference between a class attribute and an instance attribute? What does `instance.attr = value` always do?
4. Why is `Robot.population += 1` correct inside `__init__` where `self.population += 1` is a bug?
5. When is `__repr__` used and when is `__str__` used? Which should you write first, and why?
6. What does a leading underscore mean, and what does Python enforce about it?
7. Which three methods does `@dataclass` generate, and why does the `__eq__` one matter?
8. Why must a dataclass write `tags: list[str] = field(default_factory=list)` instead of `= []`?

<details>
<summary>Answers</summary>

1. It makes invalid instances impossible by routing all construction through `__init__`; it keeps operations next to the data they use, so they cannot drift apart; it gives the concept a name that documents function signatures and enables editor autocompletion (so field typos are caught immediately); and it prints usefully via `__repr__` instead of as a wall of braces.
2. `self` is the first parameter of a method, into which Python passes the instance the method was called on. `counter.increment()` and `Counter.increment(counter)` are the same call — the first is a bound method that supplies the instance automatically.
3. A class attribute is defined in the class body and shared by every instance; an instance attribute is assigned via `self` and belongs to one object. Reading checks the instance then the class; `instance.attr = value` **always** creates or updates the attribute on the instance, never on the class.
4. `self.population += 1` reads the class value, adds one, and stores the result as a *new instance* attribute that shadows the class one — leaving the shared counter unchanged. Naming the class explicitly updates the single shared value.
5. `__repr__` is used by the REPL, `repr()`, containers, debuggers and `!r`; `__str__` by `print()`, `str()` and f-strings. Write `__repr__` first, because `__str__` falls back to it and because containers (a list of your objects) always use `repr`.
6. `_name` means "internal, may change, do not depend on it from outside". Python enforces nothing — it is a convention about support, not a lock. (`__name` triggers name mangling, which is about avoiding subclass collisions, not privacy.)
7. `__init__`, `__repr__` and `__eq__`. The generated `__eq__` compares field values, so two separately-created objects holding the same data are equal — without it, `==` compares identity and returns False, which surprises everyone testing their code.
8. Because a mutable default is created once and shared by every instance (the Day 8 trap). `default_factory=list` calls `list()` per instance. Dataclasses actually refuse the `= []` form with `ValueError: mutable default <class 'list'> for field tags is not allowed`.

</details>
