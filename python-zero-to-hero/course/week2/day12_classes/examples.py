"""Day 12 — Classes: runnable demonstrations.

Run me from the course root:

    python course/week2/day12_classes/examples.py

No files are written. Section numbers match LESSON.md. Predict each printed
line before you read it, especially in section 4.
"""

from dataclasses import asdict, dataclass, field

# ---------------------------------------------------------------------------
# 1. Start from the pain: dict-of-dicts vs a class
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. The dict version, and where it hurts")
print("=" * 70)

raw_expenses = [
    {"amount": 12.5, "category": "food", "date": "2024-03-01"},
    {"amount": 30.0, "category": "transport", "date": "2024-03-02"},
]

total = 0.0
for row in raw_expenses:
    total += row["amount"]
print("total from dicts ->", total)

# Nothing stops nonsense getting in: this dict is invalid and Python is happy.
raw_expenses.append({"amount": -5, "categry": "food"})  # negative AND a typo
print("appended garbage ->", raw_expenses[-1])
try:
    print(raw_expenses[-1]["category"])
except KeyError as error:
    print("reading it later  -> KeyError:", error, "(discovered far from the cause)")
raw_expenses.pop()


class Expense:
    """One expense. Cannot exist in an invalid state."""

    def __init__(self, amount: float, category: str, date: str) -> None:
        if amount <= 0:
            raise ValueError(f"amount must be positive, got {amount}")
        if not category.strip():
            raise ValueError("category must not be empty")
        self.amount = amount
        self.category = category.strip().lower()  # normalise once, here
        self.date = date

    def formatted(self) -> str:
        """Return a one-line display form."""
        return f"{self.date} {self.category:<10} {self.amount:>8.2f}"

    def __repr__(self) -> str:
        return (f"Expense(amount={self.amount!r}, category={self.category!r}, "
                f"date={self.date!r})")


print()
expense = Expense(12.5, "  Food ", "2024-03-01")
print("the class version ->", expense)
print("  .formatted()    ->", expense.formatted())
print("  .category       ->", expense.category, "(normalised in __init__)")
try:
    Expense(-5, "food", "2024-03-01")
except ValueError as error:
    print("  invalid input   -> ValueError:", error, "(caught at the door)")
try:
    print(expense.categry)  # noqa: B018 - deliberate typo
except AttributeError as error:
    print("  attribute typo  -> AttributeError:", error)


# ---------------------------------------------------------------------------
# 2. class, instances, identity
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. Instances are independent objects")
print("=" * 70)


class Dog:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def bark(self) -> str:
        return f"{self.name} says woof"


rex = Dog("Rex", 3)
fido = Dog("Fido", 7)
print("rex.name, rex.age   ->", rex.name, rex.age)
print("fido.name, fido.age ->", fido.name, fido.age)
print("rex.bark()          ->", rex.bark())
print("type(rex)           ->", type(rex))
print("isinstance(rex, Dog)->", isinstance(rex, Dog))
print("rex is fido         ->", rex is fido)
print("rex.__dict__        ->", rex.__dict__, "(just the instance's own data)")

try:
    Dog("Rex")
except TypeError as error:
    print("Dog('Rex')          -> TypeError:", error)


# ---------------------------------------------------------------------------
# 3. self, demystified
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. self is just the first parameter")
print("=" * 70)


class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self) -> int:
        self.count += 1
        return self.count


counter = Counter()
print("counter.increment()          ->", counter.increment())
print("Counter.increment(counter)   ->", Counter.increment(counter), "(the same call)")
print("Counter.increment            ->", Counter.increment)
print("counter.increment            ->", counter.increment)
print("^ a 'bound method': the instance is already attached to self")


class Broken:
    def greet():  # noqa: N805 - deliberately missing self
        return "hi"


try:
    Broken().greet()
except TypeError as error:
    print()
    print("method without self -> TypeError:", error)
    print("  translation: Python passed the instance; there was nowhere to put it")


class AlsoBroken:
    def __init__(self, name: str) -> None:
        name = name  # noqa: PLW0127 - deliberately missing self.

    def greet(self) -> str:
        return f"hi {self.name}"


try:
    AlsoBroken("Ada").greet()
except AttributeError as error:
    print("assignment without self. -> AttributeError:", error)
    print("  translation: that was a local variable; it died when __init__ returned")


# ---------------------------------------------------------------------------
# 4. Class attributes vs instance attributes
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Class vs instance attributes (predict before reading)")
print("=" * 70)


class Robot:
    population = 0  # CLASS attribute: one shared copy
    species = "robot"  # CLASS attribute: a shared constant

    def __init__(self, name: str) -> None:
        self.name = name  # INSTANCE attribute
        Robot.population += 1  # name the CLASS to touch the shared counter


r2 = Robot("R2-D2")
c3 = Robot("C-3PO")
print("r2.name, c3.name   ->", r2.name, ",", c3.name, "(separate)")
print("Robot.population   ->", Robot.population, "(shared)")
print("r2.population      ->", r2.population, "(read finds it on the class)")

r2.species = "astromech"  # creates an INSTANCE attribute that shadows the class one
print()
print("after r2.species = 'astromech':")
print("  r2.species       ->", r2.species)
print("  c3.species       ->", c3.species, "(untouched)")
print("  Robot.species    ->", Robot.species, "(untouched)")
print("  r2.__dict__      ->", r2.__dict__)
print("Writing through an instance NEVER modifies the class.")


class BadBasket:
    items: list[str] = []  # DANGER: one list shared by every basket

    def add(self, item: str) -> None:
        self.items.append(item)  # mutates the CLASS's list


a, b = BadBasket(), BadBasket()
a.add("apple")
print()
print("shared mutable class attribute:")
print("  a.items ->", a.items)
print("  b.items ->", b.items, "<- b never added anything")


class GoodBasket:
    def __init__(self) -> None:
        self.items: list[str] = []  # a fresh list per basket

    def add(self, item: str) -> None:
        self.items.append(item)


c, d = GoodBasket(), GoodBasket()
c.add("apple")
print("  fixed: c.items ->", c.items, "| d.items ->", d.items)


# ---------------------------------------------------------------------------
# 5. Methods
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. Methods keep the invariants")
print("=" * 70)


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


account = BankAccount("Ada", 100.0)
print("deposit(50)  ->", account.deposit(50))
print("withdraw(30) ->", account.withdraw(30))
print("summary()    ->", account.summary())
for bad in (0, 1000):
    try:
        account.withdraw(bad)
    except ValueError as error:
        print(f"withdraw({bad})".ljust(13), "-> ValueError:", error)


# ---------------------------------------------------------------------------
# 6. __repr__ vs __str__
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. __repr__ vs __str__")
print("=" * 70)


class Bare:
    def __init__(self, value: int) -> None:
        self.value = value


print("no __repr__:", Bare(1))
print("  ^ the class and a memory address: useless in a traceback or a list")


class Money:
    def __init__(self, amount: float, currency: str = "GBP") -> None:
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


price = Money(12.5)
print()
print("repr(price)  ->", repr(price), "  (developers)")
print("str(price)   ->", str(price), "            (users)")
print("print(price) ->", price, "            (print uses __str__)")
print(f"f'{{price}}'   -> {price}            (f-strings use __str__)")
print(f"f'{{price!r}}' -> {price!r}  (!r forces __repr__)")
print("[price, price] ->", [price, price])
print("^ containers ALWAYS use __repr__, which is why you write it first")


# ---------------------------------------------------------------------------
# 7. Encapsulation and _private
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. _private is a convention, not a lock")
print("=" * 70)


class Temperature:
    def __init__(self, celsius: float) -> None:
        self._celsius = 0.0  # internal: may change without warning
        self.set_celsius(celsius)  # reuse the validation, do not duplicate it

    def set_celsius(self, celsius: float) -> None:
        if celsius < -273.15:
            raise ValueError(f"below absolute zero: {celsius}")
        self._celsius = celsius

    def get_celsius(self) -> float:
        return self._celsius

    def get_fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32


temperature = Temperature(21.0)
print("get_celsius()    ->", temperature.get_celsius())
print("get_fahrenheit() ->", temperature.get_fahrenheit())
try:
    temperature.set_celsius(-300)
except ValueError as error:
    print("set_celsius(-300)-> ValueError:", error)

print()
print("temperature._celsius ->", temperature._celsius, "<- nothing stopped us")
temperature._celsius = -500
print("after poking it      ->", temperature.get_celsius(), "(object now nonsense)")
print("The underscore documents SUPPORT, not access. Tomorrow's @property is how")
print("you add validation to a plain public attribute without changing callers.")


# ---------------------------------------------------------------------------
# 8. @dataclass
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. @dataclass writes the boring parts")
print("=" * 70)


class ManualBook:
    """The hand-written version: every field named four times."""

    def __init__(self, title: str, author: str, year: int) -> None:
        self.title = title
        self.author = author
        self.year = year

    def __repr__(self) -> str:
        return (f"ManualBook(title={self.title!r}, author={self.author!r}, "
                f"year={self.year!r})")


@dataclass
class Book:
    """The same thing, generated from the annotations."""

    title: str
    author: str
    year: int
    tags: list[str] = field(default_factory=list)  # NOT = []


book = Book("Structure and Interpretation", "Abelson", 1985)
print("a dataclass prints itself ->", book)
print("equality compares FIELDS  ->", book == Book("Structure and Interpretation", "Abelson", 1985))
print("different data, not equal ->", Book("A", "B", 1) == Book("A", "B", 2))
print("plain classes compare by identity ->",
      ManualBook("A", "B", 1) == ManualBook("A", "B", 1), "<- surprising, and why __eq__ matters")

print()
print("each instance gets its own list from default_factory:")
first, second = Book("A", "B", 1), Book("C", "D", 2)
first.tags.append("classic")
print("  first.tags  ->", first.tags)
print("  second.tags ->", second.tags)


@dataclass
class DataclassExpense:
    amount: float
    category: str
    date: str
    note: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Runs right after the generated __init__: the place for validation."""
        if self.amount <= 0:
            raise ValueError(f"amount must be positive, got {self.amount}")
        self.category = self.category.strip().lower()

    def formatted(self) -> str:
        return f"{self.date} {self.category:<10} {self.amount:>8.2f}"


print()
dataclass_expense = DataclassExpense(12.5, "  Food ", "2024-03-01")
print("__post_init__ normalised ->", dataclass_expense.category)
print("methods work as usual    ->", dataclass_expense.formatted())
try:
    DataclassExpense(-1, "food", "2024-03-01")
except ValueError as error:
    print("__post_init__ validated  -> ValueError:", error)

print("asdict(expense)          ->", asdict(dataclass_expense))
print("^ that dict is exactly what json.dump wants — see Day 14's project")

print()
print("Python refuses the mutable-default trap outright in a dataclass:")
print("  @dataclass")
print("  class Broken:")
print("      tags: list[str] = []")
print("  -> ValueError: mutable default <class 'list'> for field tags is not allowed")

print()
print("Done. Now open exercises.py in this folder.")
