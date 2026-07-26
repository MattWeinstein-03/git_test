"""Day 12 exercises — Classes.

Today you write classes, so each stub is a class whose methods raise
NotImplementedError. Replace the bodies with real code. Exercises 5 and 7 are
dataclasses: the stub is a plain class, and part of the exercise is turning it
into a dataclass with annotated fields.

Work top to bottom: they get harder.

Grade your work from the course root:

    python check.py day12
    python check.py day12 -v      # show full failure detail
"""

from __future__ import annotations

from dataclasses import dataclass, field  # noqa: F401 - you will need these


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
        # TODO: your code here
        raise NotImplementedError("exercise 1: Point.__init__")

    def distance_to(self, other: Point) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Point.distance_to")

    def moved_by(self, dx: float, dy: float) -> Point:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Point.moved_by")

    def __repr__(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Point.__repr__")


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
        # TODO: your code here
        raise NotImplementedError("exercise 2: BankAccount.__init__")

    def deposit(self, amount: float) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 2: BankAccount.deposit")

    def withdraw(self, amount: float) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 2: BankAccount.withdraw")

    def __repr__(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 2: BankAccount.__repr__")


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

    # TODO: your code here — the two class attributes go here
    species = "robot"
    population = 0

    def __init__(self, name: str) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 3: Robot.__init__")

    def introduce(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 3: Robot.introduce")

    def decommission(self) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 3: Robot.decommission")


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
        # TODO: your code here
        raise NotImplementedError("exercise 4: Temperature.__init__")

    def get_celsius(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 4: Temperature.get_celsius")

    def set_celsius(self, value: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 4: Temperature.set_celsius")

    def get_fahrenheit(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 4: Temperature.get_fahrenheit")

    def set_fahrenheit(self, value: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 4: Temperature.set_fahrenheit")

    def __repr__(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 4: Temperature.__repr__")


# ---------------------------------------------------------------------------
# Exercise 5 — your first dataclass
# ---------------------------------------------------------------------------
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

    # TODO: your code here — add the @dataclass decorator above this class and
    # replace this __init__ with annotated fields.
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError("exercise 5: Book")

    def citation(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 5: Book.citation")

    def add_tag(self, tag: str) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 5: Book.add_tag")


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
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.__init__")

    def add(self, name: str, quantity: int, unit_price: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.add")

    def remove(self, name: str, quantity: int) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.remove")

    def quantity_of(self, name: str) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.quantity_of")

    def total_value(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.total_value")

    def count(self) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.count")

    def __repr__(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Inventory.__repr__")


# ---------------------------------------------------------------------------
# Exercise 7 — a dataclass with validation and behaviour
# ---------------------------------------------------------------------------
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

    # TODO: your code here — add the @dataclass decorator and the two fields.
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError("exercise 7: Student")

    def add_score(self, value: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 7: Student.add_score")

    def average(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 7: Student.average")

    def best(self) -> float | None:
        # TODO: your code here
        raise NotImplementedError("exercise 7: Student.best")

    def grade(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 7: Student.grade")


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
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.__init__")

    def add_student(self, name: str) -> Student:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.add_student")

    def record(self, name: str, score: float) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.record")

    def student(self, name: str) -> Student | None:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.student")

    def class_average(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.class_average")

    def top_student(self) -> Student | None:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.top_student")

    def report(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Gradebook.report")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(Point(3, 4).distance_to(Point(0, 0)))
    # print(Book("Dune", "Herbert", 1965))
    print("Run `python check.py day12` from the course root to grade your work.")
