"""Day 12 solutions — Classes.

Reference implementations. Same class and method names as exercises.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ABSOLUTE_ZERO_C = -273.15


# ---------------------------------------------------------------------------
# Exercise 1 — __init__, a method, and __repr__
# ---------------------------------------------------------------------------
class Point:
    """A point in 2D space.

    Attributes:
        x: horizontal position.
        y: vertical position.

    Methods:
        distance_to(other): straight-line distance, rounded to 2 decimals.
        moved_by(dx, dy): a NEW Point shifted by dx and dy (this one is pure —
            it must not modify the point you called it on).

    __repr__ must look like a constructor call:
        f"Point(x={x!r}, y={y!r})"

    Examples:
        p = Point(3, 4)
        p.x -> 3
        repr(p) -> "Point(x=3, y=4)"
        p.distance_to(Point(0, 0)) -> 5.0
        Point(0, 0).distance_to(Point(1, 1)) -> 1.41
        q = p.moved_by(1, -1)
        q -> Point(x=4, y=3)      and p is still Point(x=3, y=4)
    """

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance_to(self, other: Point) -> float:
        across = self.x - other.x
        up = self.y - other.y
        # why: ** 0.5 is a square root without needing an import.
        return round((across * across + up * up) ** 0.5, 2)

    def moved_by(self, dx: float, dy: float) -> Point:
        # why: return a NEW Point instead of mutating self — callers keep their data.
        return Point(self.x + dx, self.y + dy)

    def __repr__(self) -> str:
        return f"Point(x={self.x!r}, y={self.y!r})"


# ---------------------------------------------------------------------------
# Exercise 2 — methods that guard an invariant
# ---------------------------------------------------------------------------
class BankAccount:
    """A bank account that can never go negative.

    Attributes:
        owner: the account holder's name.
        balance: current balance. Starts at `balance`, which defaults to 0.0.
        history: a list of strings, one per successful operation, in order:
            f"deposit {amount:.2f}" or f"withdraw {amount:.2f}"

    Methods:
        deposit(amount): add money, return the new balance.
        withdraw(amount): remove money, return the new balance.

    Rules — every one of these raises ValueError, and a failed operation must
    NOT be recorded in history and must NOT change the balance:
        * an opening balance below 0
        * a deposit of 0 or less
        * a withdrawal of 0 or less
        * a withdrawal larger than the balance

    __repr__ must be f"BankAccount(owner={owner!r}, balance={balance!r})".

    Examples:
        account = BankAccount("Ada", 100.0)
        account.deposit(50) -> 150.0
        account.withdraw(30) -> 120.0
        account.history -> ["deposit 50.00", "withdraw 30.00"]
        account.withdraw(1000) -> raises ValueError
        BankAccount("Ada").balance -> 0.0
        BankAccount("Ada", -1) -> raises ValueError
    """

    def __init__(self, owner: str, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError(f"balance must not be negative, got {balance}")
        self.owner = owner
        self.balance = balance
        # why: a fresh list per account. A class attribute here would be shared.
        self.history: list[str] = []

    def deposit(self, amount: float) -> float:
        # why: validate BEFORE touching state, so a rejected operation leaves
        # the object exactly as it was.
        if amount <= 0:
            raise ValueError(f"deposit must be positive, got {amount}")
        self.balance += amount
        self.history.append(f"deposit {amount:.2f}")
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError(f"withdrawal must be positive, got {amount}")
        if amount > self.balance:
            raise ValueError(f"cannot withdraw {amount} from {self.balance}")
        self.balance -= amount
        self.history.append(f"withdraw {amount:.2f}")
        return self.balance

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self.balance!r})"


# ---------------------------------------------------------------------------
# Exercise 3 — class attributes vs instance attributes
# ---------------------------------------------------------------------------
class Robot:
    """A robot that keeps a count of how many robots exist.

    Class attributes (shared by every robot):
        species: the string "robot".
        population: how many robots currently exist. Starts at 0.

    Instance attributes:
        name: this robot's name.

    Methods:
        introduce(): f"I am {name}, a {species}."
        decommission(): reduce the shared population by 1 and return the new
            population. Never let it go below 0.

    Remember: inside a method, `Robot.population += 1` updates the shared
    counter, while `self.population += 1` would quietly create an instance
    attribute and leave the shared one alone.

    Examples:
        Robot.population   # 0 before any robot exists
        r2 = Robot("R2-D2")
        Robot.population -> 1
        r2.introduce() -> "I am R2-D2, a robot."
        c3 = Robot("C-3PO")
        Robot.population -> 2
        r2.decommission() -> 1
        Robot.species -> "robot"
    """

    species = "robot"  # shared constant
    population = 0  # shared counter

    def __init__(self, name: str) -> None:
        self.name = name
        # why: naming the CLASS updates the one shared counter. `self.population
        # += 1` would create an instance attribute and leave the class at 0.
        Robot.population += 1

    def introduce(self) -> str:
        # why: self.species reads through to the class attribute, so a subclass
        # could override it without changing this method.
        return f"I am {self.name}, a {self.species}."

    def decommission(self) -> int:
        if Robot.population > 0:
            Robot.population -= 1
        return Robot.population


# ---------------------------------------------------------------------------
# Exercise 4 — encapsulation with the _private convention
# ---------------------------------------------------------------------------
class Temperature:
    """A temperature that refuses to be colder than absolute zero.

    Store the value in a single internal attribute named `_celsius`, and let
    every path in go through the validation. Absolute zero is -273.15 C.

    Methods:
        get_celsius(): the stored value.
        set_celsius(value): validate and store. ValueError below -273.15.
        get_fahrenheit(): the value converted, celsius * 9 / 5 + 32,
            rounded to 2 decimals.
        set_fahrenheit(value): convert (value - 32) * 5 / 9 to celsius and
            store it through the same validation, rounded to 2 decimals.

    __repr__ must be f"Temperature(celsius={celsius!r})".

    Examples:
        t = Temperature(21.0)
        t.get_celsius() -> 21.0
        t.get_fahrenheit() -> 69.8
        t.set_celsius(-273.15) -> None, and get_celsius() -> -273.15
        t.set_celsius(-300) -> raises ValueError
        t.set_fahrenheit(212) -> None, and get_celsius() -> 100.0
        t.set_fahrenheit(-500) -> raises ValueError
        Temperature(-300) -> raises ValueError
        repr(Temperature(21.0)) -> "Temperature(celsius=21.0)"
    """

    def __init__(self, celsius: float) -> None:
        self._celsius = 0.0
        # why: go through the setter so the rule lives in exactly one place.
        self.set_celsius(celsius)

    def get_celsius(self) -> float:
        return self._celsius

    def set_celsius(self, value: float) -> None:
        if value < ABSOLUTE_ZERO_C:
            raise ValueError(f"below absolute zero: {value}")
        self._celsius = value

    def get_fahrenheit(self) -> float:
        return round(self._celsius * 9 / 5 + 32, 2)

    def set_fahrenheit(self, value: float) -> None:
        self.set_celsius(round((value - 32) * 5 / 9, 2))

    def __repr__(self) -> str:
        return f"Temperature(celsius={self._celsius!r})"


# ---------------------------------------------------------------------------
# Exercise 5 — your first dataclass
# ---------------------------------------------------------------------------
@dataclass
class Book:
    """A book record. Make this a @dataclass.

    Fields, in this order:
        title: str
        author: str
        year: int
        tags: list[str], defaulting to an empty list — use
            field(default_factory=list), because `= []` is both the Day 8
            mutable-default trap and an outright error in a dataclass.

    Methods:
        citation(): f"{author} ({year}). {title}."
        add_tag(tag): add `tag` lowercased and stripped, unless it is already
            present. Ignore a tag that is empty after stripping. Returns None.

    You get __init__, __repr__ and __eq__ for free from the decorator, so two
    books holding the same data must compare equal.

    Examples:
        book = Book("Dune", "Herbert", 1965)
        book.title -> "Dune"
        book.tags -> []
        book.citation() -> "Herbert (1965). Dune."
        book.add_tag("  SciFi ")
        book.tags -> ["scifi"]
        book.add_tag("scifi")     # already there
        book.tags -> ["scifi"]
        Book("Dune", "Herbert", 1965) == Book("Dune", "Herbert", 1965) -> True
        Book("Dune", "Herbert", 1965) == Book("Dune", "Herbert", 1966) -> False
        repr(Book("Dune", "Herbert", 1965)) ->
            "Book(title='Dune', author='Herbert', year=1965, tags=[])"
    """

    title: str
    author: str
    year: int
    # why: default_factory calls list() per instance. `= []` is refused outright.
    tags: list[str] = field(default_factory=list)

    def citation(self) -> str:
        return f"{self.author} ({self.year}). {self.title}."

    def add_tag(self, tag: str) -> None:
        cleaned = tag.strip().lower()
        if not cleaned:
            return
        if cleaned not in self.tags:
            self.tags.append(cleaned)


# ---------------------------------------------------------------------------
# Exercise 6 — a class that owns a dict
# ---------------------------------------------------------------------------
class Inventory:
    """Stock levels for a small shop.

    Keep the data in one internal dict named `_items`, mapping an item name to
    its quantity and unit price. Nothing outside the class should need to know
    the shape of that dict — that is the point of the underscore.

    Methods:
        add(name, quantity, unit_price): add stock. Adding a name that is
            already present increases its quantity and adopts the new unit
            price. ValueError if quantity <= 0 or unit_price < 0.
        remove(name, quantity): take stock away, returning the quantity left.
            KeyError if the name is unknown. ValueError if quantity <= 0 or
            more than is held. Removing the last of an item deletes it
            entirely, so count() drops.
        quantity_of(name): how many are held, 0 for an unknown name.
        total_value(): sum of quantity * unit_price over everything, rounded
            to 2 decimals.
        count(): how many DISTINCT item names are stocked.

    __repr__ must be f"Inventory({count} items, total {total_value:.2f})".

    Examples:
        stock = Inventory()
        stock.count() -> 0
        stock.add("widget", 2, 9.99)
        stock.add("bolt", 10, 0.5)
        stock.count() -> 2
        stock.quantity_of("widget") -> 2
        stock.quantity_of("nothing") -> 0
        stock.total_value() -> 24.98
        stock.add("widget", 1, 10.0)      # same name: now 3 at 10.00
        stock.quantity_of("widget") -> 3
        stock.total_value() -> 35.0
        stock.remove("bolt", 10) -> 0
        stock.count() -> 1
        stock.remove("bolt", 1) -> raises KeyError
        stock.remove("widget", 99) -> raises ValueError
        repr(stock) -> "Inventory(1 items, total 30.00)"
    """

    def __init__(self) -> None:
        # why: one internal dict, private by convention. Callers use the methods.
        self._items: dict[str, dict[str, float]] = {}

    def add(self, name: str, quantity: int, unit_price: float) -> None:
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")
        if unit_price < 0:
            raise ValueError(f"unit_price must not be negative, got {unit_price}")
        held = self._items.get(name)
        if held is None:
            self._items[name] = {"quantity": quantity, "unit_price": unit_price}
        else:
            held["quantity"] += quantity
            held["unit_price"] = unit_price

    def remove(self, name: str, quantity: int) -> int:
        if name not in self._items:
            raise KeyError(name)
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")
        held = self._items[name]
        if quantity > held["quantity"]:
            raise ValueError(
                f"cannot remove {quantity} of {name!r}: only {held['quantity']} held"
            )
        held["quantity"] -= quantity
        if held["quantity"] == 0:
            del self._items[name]
            return 0
        return int(held["quantity"])

    def quantity_of(self, name: str) -> int:
        held = self._items.get(name)
        if held is None:
            return 0
        return int(held["quantity"])

    def total_value(self) -> float:
        total = 0.0
        for held in self._items.values():
            total += held["quantity"] * held["unit_price"]
        return round(total, 2)

    def count(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Inventory({self.count()} items, total {self.total_value():.2f})"


# ---------------------------------------------------------------------------
# Exercise 7 — a dataclass with validation and behaviour
# ---------------------------------------------------------------------------
@dataclass
class Student:
    """A student and their scores. Make this a @dataclass.

    Fields, in this order:
        name: str
        scores: list[float], defaulting to an empty list via field(default_factory=list)

    Methods:
        add_score(value): append a score. ValueError if it is below 0 or above
            100. Returns None.
        average(): mean of the scores rounded to 1 decimal; 0.0 when there are
            no scores.
        best(): the highest score, or None when there are no scores.
        grade(): letter for the average — "A" for 90 or more, "B" for 80+,
            "C" for 70+, "D" for 60+, otherwise "F". With no scores at all,
            return "N/A".

    Examples:
        student = Student("Ada")
        student.scores -> []
        student.average() -> 0.0
        student.grade() -> "N/A"
        student.best() -> None
        student.add_score(90)
        student.add_score(95)
        student.average() -> 92.5
        student.best() -> 95
        student.grade() -> "A"
        Student("Ada", [70.0]).grade() -> "C"
        student.add_score(101) -> raises ValueError
        Student("Ada", [1.0]) == Student("Ada", [1.0]) -> True
    """

    name: str
    scores: list[float] = field(default_factory=list)

    def add_score(self, value: float) -> None:
        if value < 0 or value > 100:
            raise ValueError(f"score must be between 0 and 100, got {value}")
        self.scores.append(value)

    def average(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(self.scores) / len(self.scores), 1)

    def best(self) -> float | None:
        if not self.scores:
            return None
        return max(self.scores)

    def grade(self) -> str:
        # why: the "no data" case is not an F — it is unknown. Say so.
        if not self.scores:
            return "N/A"
        average = self.average()
        if average >= 90:
            return "A"
        if average >= 80:
            return "B"
        if average >= 70:
            return "C"
        if average >= 60:
            return "D"
        return "F"


# ---------------------------------------------------------------------------
# Exercise 8 — the hard one: one class managing many objects
# ---------------------------------------------------------------------------
class Gradebook:
    """A collection of Students, keyed by name.

    This is the shape you will use again in Day 14's project: a small class
    that owns a collection of smaller objects and answers questions about them.
    Store the students in one internal dict named `_students`.

    Methods:
        add_student(name): create a Student, store it, and return it.
            ValueError if that name is already in the book.
        record(name, score): add a score to that student, returning the
            student's new average. KeyError if the name is unknown; the
            Student's own validation handles a bad score.
        student(name): the Student object, or None if there is no such student.
        class_average(): the mean of every student's average(), rounded to 1
            decimal. 0.0 for an empty gradebook.
        top_student(): the Student with the highest average, or None when the
            book is empty. Break ties alphabetically by name.
        report(): a multi-line string, "\\n" between lines, no trailing newline:
            one line per student, sorted by name:
                f"{name:<10}{average:>6.1f}  {grade}"
            then a final line:
                f"{'CLASS':<10}{class_average:>6.1f}"
            An empty gradebook reports the single line "(no students)".

    Examples:
        book = Gradebook()
        book.report() -> "(no students)"
        book.class_average() -> 0.0
        book.top_student() -> None

        ada = book.add_student("Ada")
        book.add_student("Grace")
        book.record("Ada", 90) -> 90.0
        book.record("Ada", 100) -> 95.0
        book.record("Grace", 80) -> 80.0
        book.class_average() -> 87.5
        book.top_student().name -> "Ada"
        book.student("Ada") is ada -> True
        book.student("nobody") -> None
        book.add_student("Ada") -> raises ValueError
        book.record("nobody", 50) -> raises KeyError

        book.report() ->
            'Ada         95.0  A\\n'
            'Grace       80.0  B\\n'
            'CLASS       87.5'
    """

    def __init__(self) -> None:
        self._students: dict[str, Student] = {}

    def add_student(self, name: str) -> Student:
        if name in self._students:
            raise ValueError(f"{name!r} is already in the gradebook")
        student = Student(name)
        self._students[name] = student
        return student

    def record(self, name: str, score: float) -> float:
        if name not in self._students:
            raise KeyError(name)
        student = self._students[name]
        # why: let Student validate the score. One rule, one home.
        student.add_score(score)
        return student.average()

    def student(self, name: str) -> Student | None:
        return self._students.get(name)

    def class_average(self) -> float:
        if not self._students:
            return 0.0
        total = 0.0
        for student in self._students.values():
            total += student.average()
        return round(total / len(self._students), 1)

    def top_student(self) -> Student | None:
        best: Student | None = None
        # why: iterate names in sorted order, so a tie keeps the alphabetically
        # first student without needing a custom sort key.
        for name in sorted(self._students):
            student = self._students[name]
            if best is None or student.average() > best.average():
                best = student
        return best

    def report(self) -> str:
        if not self._students:
            return "(no students)"
        lines: list[str] = []
        for name in sorted(self._students):
            student = self._students[name]
            lines.append(f"{name:<10}{student.average():>6.1f}  {student.grade()}")
        lines.append(f"{'CLASS':<10}{self.class_average():>6.1f}")
        return "\n".join(lines)


if __name__ == "__main__":
    book = Gradebook()
    book.add_student("Ada")
    book.add_student("Grace")
    book.record("Ada", 90)
    book.record("Ada", 100)
    book.record("Grace", 80)
    print(book.report())
