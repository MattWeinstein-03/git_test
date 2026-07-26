"""Day 13 — OOP in practice: runnable demonstrations.

Run me from the course root:

    python course/week2/day13_oop_in_practice/examples.py

No files are written. Section numbers match LESSON.md.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. Inheritance and polymorphism
# ---------------------------------------------------------------------------
print("=" * 70)
print("1. Inheritance: shared code that adapts to the subclass")
print("=" * 70)


class Shape:
    def __init__(self, name: str) -> None:
        self.name = name

    def area(self) -> float:
        # The plain-Python way to say "abstract: subclasses must supply this".
        raise NotImplementedError("subclasses must implement area()")

    def describe(self) -> str:
        # Written ONCE. self.area() resolves to the subclass's version.
        return f"{self.name} with area {self.area():.2f}"


class Square(Shape):
    def __init__(self, side: float) -> None:
        super().__init__("square")  # let Shape initialise its own part
        self.side = side

    def area(self) -> float:  # override
        return self.side ** 2


class Circle(Shape):
    PI = 3.14159  # class attribute: a shared constant

    def __init__(self, radius: float) -> None:
        super().__init__("circle")
        self.radius = radius

    def area(self) -> float:
        return self.PI * self.radius ** 2


for shape in (Square(3), Circle(1)):
    print(f"  {shape.describe()}")
print("describe() never mentions Square or Circle — that is polymorphism")
print("isinstance(Square(3), Shape) ->", isinstance(Square(3), Shape))
print("issubclass(Circle, Shape)    ->", issubclass(Circle, Shape))
try:
    Shape("blob").area()
except NotImplementedError as error:
    print("Shape('blob').area()         -> NotImplementedError:", error)


# ---------------------------------------------------------------------------
# 2. super()
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. super(): reuse the parent, then extend")
print("=" * 70)


class Employee:
    def __init__(self, name: str, monthly_salary: float) -> None:
        self.name = name
        self.monthly_salary = monthly_salary

    def annual_pay(self) -> float:
        return self.monthly_salary * 12

    def describe(self) -> str:
        return f"{self.name} earns {self.annual_pay():.2f} a year"


class Manager(Employee):
    BONUS_PER_REPORT = 1000.0

    def __init__(self, name: str, monthly_salary: float, reports: list[str]) -> None:
        super().__init__(name, monthly_salary)  # 1. parent's setup
        self.reports = list(reports)  # why: copy, so the caller's list is ours alone

    def annual_pay(self) -> float:
        base = super().annual_pay()  # 2. extend rather than re-implement
        return base + self.BONUS_PER_REPORT * len(self.reports)

    def describe(self) -> str:
        return super().describe() + f", managing {len(self.reports)}"


employee = Employee("Ada", 5000.0)
manager = Manager("Grace", 5000.0, ["ada", "linus"])
print("  employee.annual_pay() ->", employee.annual_pay())
print("  manager.annual_pay()  ->", manager.annual_pay(), "(60000 + 2 * 1000)")
print("  manager.describe()    ->", manager.describe())


class ForgotSuper(Employee):
    def __init__(self, name: str) -> None:
        self.name = name  # never calls super().__init__, so no monthly_salary


try:
    ForgotSuper("Linus").annual_pay()
except AttributeError as error:
    print()
    print("forgetting super().__init__() -> AttributeError:", error)
    print("  the failure appears far from the cause: the parent never ran")


# ---------------------------------------------------------------------------
# 3. MRO
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. Method resolution order")
print("=" * 70)

def mro_names(cls: type) -> list[str]:
    """The method resolution order as readable names."""
    names = []
    for entry in cls.mro():
        names.append(entry.__name__)
    return names


print("Manager.mro() ->", mro_names(Manager))
print("every class ends at `object`, which is where the default __repr__ lives")


class Loggable:
    def describe(self) -> str:
        return "loggable"


class Serialisable:
    def describe(self) -> str:
        return "serialisable"


class Record(Loggable, Serialisable):
    pass


print()
print("class Record(Loggable, Serialisable)")
print("  Record.mro()      ->", mro_names(Record))
print("  Record().describe()->", Record().describe(), "(left to right, first match wins)")
print("Avoid multiple inheritance for state-bearing classes; mixins only.")


# ---------------------------------------------------------------------------
# 4. Composition
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("4. Composition: has-a, and swappable")
print("=" * 70)


class Engine:
    def __init__(self, horsepower: int) -> None:
        self.horsepower = horsepower
        self.running = False

    def start(self) -> str:
        if self.running:
            return "already running"
        self.running = True
        return "engine started"

    def stop(self) -> str:
        self.running = False
        return "engine stopped"


class ElectricMotor:
    """A different part with the same protocol — duck typing again."""

    def __init__(self, kilowatts: int) -> None:
        self.kilowatts = kilowatts
        self.running = False

    def start(self) -> str:
        self.running = True
        return "motor humming"

    def stop(self) -> str:
        self.running = False
        return "motor silent"


class Car:
    def __init__(self, model: str, horsepower: int) -> None:
        self.model = model
        self.engine = Engine(horsepower)  # HAS-A

    def start(self) -> str:
        return f"{self.model}: {self.engine.start()}"  # delegate

    @property
    def running(self) -> bool:
        return self.engine.running  # expose exactly one detail


car = Car("Mini", 90)
print("  car.start()   ->", car.start())
print("  car.running   ->", car.running)
print("  car.start()   ->", car.start(), "(the engine knows it is already going)")
car.engine = ElectricMotor(80)  # swap the part at RUNTIME — impossible with inheritance
print("  after swapping the engine for a motor:")
print("  car.start()   ->", car.start())
print()
print("`class Car(Engine)` would also 'work', and would be a lie: every Engine")
print("method would become part of Car's API, and you could never swap the part.")


# ---------------------------------------------------------------------------
# 5. Duck typing
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. Duck typing: no shared base class needed")
print("=" * 70)


class TextBlock:
    def __init__(self, text: str) -> None:
        self.text = text

    def render(self) -> str:
        return self.text.strip()


class Divider:
    def render(self) -> str:
        return "-" * 20


def render_all(items: list) -> list[str]:
    """Render everything that can render itself; fall back to str() otherwise."""
    output = []
    for item in items:
        try:
            output.append(item.render())  # EAFP: just try it
        except AttributeError:
            output.append(str(item))  # not a duck; be reasonable
    return output


print("  render_all([TextBlock, Divider, 42]) ->")
for line in render_all([TextBlock("  hello  "), Divider(), 42]):
    print("   ", repr(line))
print("TextBlock and Divider share no base class, only a protocol: .render()")
print("A new class with .render() works with zero changes to render_all.")
print()
print("The anti-pattern this replaces:")
print("  if isinstance(item, TextBlock): ...")
print("  elif isinstance(item, Divider): ...   <- edited for every new type")


# ---------------------------------------------------------------------------
# 6. @property
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("6. @property: validation and computed values, attribute syntax")
print("=" * 70)


class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius  # goes through the setter, so validation is not skipped

    @property
    def celsius(self) -> float:
        """The temperature in degrees Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"below absolute zero: {value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """The same temperature in Fahrenheit — computed, never stored."""
        return round(self._celsius * 9 / 5 + 32, 2)

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = round((value - 32) * 5 / 9, 2)  # reuse the validation

    @property
    def kelvin(self) -> float:
        """Read-only on purpose: there is no setter."""
        return round(self._celsius + 273.15, 2)


temperature = Temperature(21.0)
print("  temperature.celsius     ->", temperature.celsius, "(no parentheses)")
print("  temperature.fahrenheit  ->", temperature.fahrenheit)
print("  temperature.kelvin      ->", temperature.kelvin)
temperature.fahrenheit = 212
print("  after .fahrenheit = 212 -> celsius is", temperature.celsius)
try:
    temperature.celsius = -300
except ValueError as error:
    print("  .celsius = -300         -> ValueError:", error)
try:
    temperature.kelvin = 0
except AttributeError as error:
    print("  .kelvin = 0             -> AttributeError:", error)
print("Twenty callers writing `t.celsius` needed NO changes when validation")
print("arrived. That is why Python does not need speculative getters/setters.")


# ---------------------------------------------------------------------------
# 7. @classmethod and @staticmethod
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("7. Alternative constructors and namespaced helpers")
print("=" * 70)


class Duration:
    def __init__(self, hours: int, minutes: int) -> None:
        if hours < 0 or minutes < 0:
            raise ValueError("duration cannot be negative")
        if minutes > 59:
            raise ValueError(f"minutes must be 0-59, got {minutes}")
        self.hours = hours
        self.minutes = minutes

    @classmethod
    def from_string(cls, text: str) -> Duration:
        """Build from "H:MM". An ALTERNATIVE CONSTRUCTOR."""
        if not cls.is_valid(text):
            raise ValueError(f"cannot parse duration: {text!r}")
        hours_text, minutes_text = text.split(":")
        return cls(int(hours_text), int(minutes_text))  # cls, so subclasses work

    @classmethod
    def from_minutes(cls, total: int) -> Duration:
        """Build from a total number of minutes."""
        return cls(total // 60, total % 60)

    @staticmethod
    def is_valid(text: str) -> bool:
        """Could `text` be an "H:MM" duration? Needs no instance and no class."""
        parts = text.split(":")
        if len(parts) != 2:
            return False
        return parts[0].isdigit() and parts[1].isdigit() and int(parts[1]) < 60

    def total_minutes(self) -> int:
        return self.hours * 60 + self.minutes

    def __repr__(self) -> str:
        return f"Duration(hours={self.hours!r}, minutes={self.minutes!r})"

    def __str__(self) -> str:
        return f"{self.hours}h{self.minutes:02d}m"


print("  Duration.from_string('1:30') ->", Duration.from_string("1:30"),
      "| repr:", repr(Duration.from_string("1:30")))
print("  Duration.from_minutes(150)   ->", Duration.from_minutes(150))
print("  .total_minutes()             ->", Duration.from_string("1:30").total_minutes())
print("  Duration.is_valid('1:75')    ->", Duration.is_valid("1:75"), "(static: no instance)")
try:
    Duration.from_string("oops")
except ValueError as error:
    print("  Duration.from_string('oops') -> ValueError:", error)


class PreciseDuration(Duration):
    """A subclass gets the alternative constructors for free, thanks to cls()."""


print("  PreciseDuration.from_minutes(90) is a",
      type(PreciseDuration.from_minutes(90)).__name__, "<- because from_minutes used cls()")


# ---------------------------------------------------------------------------
# 8. Dunder methods
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("8. Dunders: make your object behave like a Python container")
print("=" * 70)


class Bag:
    """A collection of items that behaves like a Python container."""

    def __init__(self, items: list[str] | None = None) -> None:
        self._items: list[str] = list(items) if items is not None else []

    def add(self, item: str) -> None:
        self._items.append(item)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __iter__(self):
        # why: delegate to the list's own iterator. Writing one from scratch
        # (and `yield`) is Day 15.
        return iter(self._items)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bag):
            return NotImplemented  # "I don't know", not "unequal"
        return self._items == other._items

    def __repr__(self) -> str:
        return f"Bag(items={self._items!r})"


bag = Bag(["apple", "pear"])
bag.add("fig")
print("  repr(bag)          ->", repr(bag))
print("  len(bag)           ->", len(bag), "        (__len__)")
print("  'pear' in bag      ->", "pear" in bag, "     (__contains__)")
print("  'plum' in bag      ->", "plum" in bag)
print("  list(bag)          ->", list(bag), "  (__iter__)")
print("  sorted(bag)        ->", sorted(bag))
print("  max(bag)           ->", max(bag))
print("  bag == Bag([...])  ->", bag == Bag(["apple", "pear", "fig"]), "     (__eq__)")
print("  bool(Bag())        ->", bool(Bag()), "    (falsy: __len__ is 0)")
print("  bag == 5           ->", bag == 5, "    (NotImplemented -> Python says False)")
print("  hash(bag)?         -> defining __eq__ makes instances unhashable:")
try:
    {bag}
except TypeError as error:
    print("     ", type(error).__name__ + ":", error)


# ---------------------------------------------------------------------------
# 9. When NOT to use OOP
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("9. The same feature, two ways")
print("=" * 70)


class PriceFormatter:
    """Smell 1: a class with one method and no real state."""

    def __init__(self, currency: str = "GBP") -> None:
        self.currency = currency

    def format(self, amount: float) -> str:
        return f"{amount:.2f} {self.currency}"


def format_price(amount: float, currency: str = "GBP") -> str:
    """The honest version: two lines, nothing to instantiate."""
    return f"{amount:.2f} {currency}"


print("  PriceFormatter().format(12.5) ->", PriceFormatter().format(12.5))
print("  format_price(12.5)            ->", format_price(12.5), "<- prefer this")

COUPONS = {"SAVE10": 0.10, "FIVER": 5.00}


def subtotal(lines: list[dict]) -> float:
    """Sum price * quantity over `lines`."""
    total = 0.0
    for line in lines:
        total += line["price"] * line["quantity"]
    return round(total, 2)


def apply_coupon(amount: float, code: str | None) -> float:
    """Return `amount` with the coupon applied. Unknown code -> ValueError."""
    if code is None:
        return amount
    if code == "SAVE10":
        return round(amount * (1 - COUPONS["SAVE10"]), 2)
    if code == "FIVER":
        return round(max(amount - COUPONS["FIVER"], 0.0), 2)
    raise ValueError(f"unknown coupon: {code}")


def cart_total(lines: list[dict], code: str | None = None, tax_rate: float = 0.2) -> float:
    """Subtotal, then coupon, then tax."""
    return round(apply_coupon(subtotal(lines), code) * (1 + tax_rate), 2)


class Cart:
    """The class version: it holds state and validates. The MATHS is reused."""

    def __init__(self) -> None:
        self._lines: list[dict] = []

    def add(self, name: str, price: float, quantity: int) -> None:
        if price < 0 or quantity <= 0:
            raise ValueError("price must be >= 0 and quantity > 0")
        self._lines.append({"name": name, "price": price, "quantity": quantity})

    def subtotal(self) -> float:
        return subtotal(self._lines)

    def total(self, code: str | None = None, tax_rate: float = 0.2) -> float:
        return cart_total(self._lines, code, tax_rate)

    def __len__(self) -> int:
        return len(self._lines)


lines = [{"name": "widget", "price": 10.0, "quantity": 2}]
cart = Cart()
cart.add("widget", 10.0, 2)

print()
print("  functions: subtotal(lines)          ->", subtotal(lines))
print("  functions: cart_total(lines,'SAVE10')->", cart_total(lines, "SAVE10"))
print("  class:     cart.subtotal()          ->", cart.subtotal())
print("  class:     cart.total('SAVE10')     ->", cart.total("SAVE10"))
print("  class:     len(cart)                ->", len(cart))
print("  identical numbers — the class adds STRUCTURE, not arithmetic")
try:
    cart.add("bad", 1.0, 0)
except ValueError as error:
    print("  class:     cart.add(..., 0)         -> ValueError:", error)
print("  ^ that guarantee (no invalid line can enter) is what the class bought.")

print()
print("Choose functions when the data is already a list/dict and each operation")
print("is independent. Choose a class when you must protect invariants or the")
print("thing has a lifecycle. Pure functions doing the work, a thin object")
print("holding the state, is the shape most good Python takes.")

print()
print("Done. Now open exercises.py in this folder.")
