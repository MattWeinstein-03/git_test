"""Day 13 exercises — OOP in practice.

Fill in each class or function. Delete the `raise NotImplementedError(...)`
lines and write real code. Work top to bottom: they get harder, and exercise 8
asks you to write the same feature twice on purpose.

Grade your work from the course root:

    python check.py day13
    python check.py day13 -v      # show full failure detail
"""

from __future__ import annotations

# Use this instead of importing math, so everybody's numbers match exactly.
PI = 3.14159
ABSOLUTE_ZERO_C = -273.15
COUPONS = {"SAVE10": 0.10, "FIVER": 5.00}


# ---------------------------------------------------------------------------
# Exercise 1 — inheritance, overriding, and polymorphism
# ---------------------------------------------------------------------------
class Shape:
    """Base class for shapes.

    Attributes:
        name: what kind of shape this is.

    Methods:
        area(): must be overridden by subclasses. In THIS class, raise
            NotImplementedError("subclasses must implement area()").
        describe(): f"{name} with area {area:.2f}" — write this ONCE here and
            let it call self.area(), so it works for every subclass.
    """

    def __init__(self, name: str) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Shape.__init__")

    def area(self) -> float:
        # TODO: your code here — this one really does stay NotImplementedError,
        # with the message "subclasses must implement area()".
        raise NotImplementedError("subclasses must implement area()")

    def describe(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Shape.describe")


class Square(Shape):
    """A square. Pass the name "square" up to Shape with super().__init__.

    Attributes:
        side: the length of one side.

    Examples:
        Square(3).area() -> 9
        Square(3).describe() -> "square with area 9.00"
        Square(3).name -> "square"
        isinstance(Square(3), Shape) -> True
    """

    def __init__(self, side: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Square.__init__")

    def area(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Square.area")


class Circle(Shape):
    """A circle, named "circle". Use the module-level PI constant.

    Attributes:
        radius: the radius.

    Examples:
        Circle(1).area() -> 3.14159
        Circle(2).area() -> 12.56636
        Circle(1).describe() -> "circle with area 3.14"
    """

    def __init__(self, radius: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Circle.__init__")

    def area(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 1: Circle.area")


# ---------------------------------------------------------------------------
# Exercise 2 — super() to extend, not replace
# ---------------------------------------------------------------------------
class Employee:
    """Somebody on the payroll.

    Attributes:
        name: their name.
        monthly_salary: what they are paid each month.

    Methods:
        annual_pay(): monthly_salary * 12.
        describe(): f"{name} earns {annual_pay:.2f} a year"

    Examples:
        Employee("Ada", 5000.0).annual_pay() -> 60000.0
        Employee("Ada", 5000.0).describe() -> "Ada earns 60000.00 a year"
    """

    def __init__(self, name: str, monthly_salary: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 2: Employee.__init__")

    def annual_pay(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 2: Employee.annual_pay")

    def describe(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 2: Employee.describe")


class Manager(Employee):
    """An employee who also gets BONUS_PER_REPORT for each direct report.

    Call super().__init__ for the shared setup, and use super() inside both
    methods rather than repeating the parent's logic. Store `reports` as a NEW
    list, so the caller's list cannot change your object later.

    Attributes:
        reports: the names of the people who report to them.

    Methods:
        annual_pay(): the parent's answer plus BONUS_PER_REPORT per report.
        describe(): the parent's sentence plus f", managing {len(reports)}"

    Examples:
        m = Manager("Grace", 5000.0, ["ada", "linus"])
        m.annual_pay() -> 62000.0
        m.describe() -> "Grace earns 62000.00 a year, managing 2"
        Manager("Zoe", 1000.0, []).annual_pay() -> 12000.0
    """

    BONUS_PER_REPORT = 1000.0

    def __init__(self, name: str, monthly_salary: float, reports: list[str]) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 2: Manager.__init__")

    def annual_pay(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 2: Manager.annual_pay")

    def describe(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 2: Manager.describe")


# ---------------------------------------------------------------------------
# Exercise 3 — @property with validation
# ---------------------------------------------------------------------------
class Temperature:
    """A temperature exposed as plain attributes, protected by properties.

    Store the number once, in `self._celsius`. Then:
        celsius     — property with a setter that raises ValueError below
                      ABSOLUTE_ZERO_C. __init__ must go through this setter.
        fahrenheit  — property computing celsius * 9 / 5 + 32, rounded to 2
                      decimals, with a setter that converts
                      (value - 32) * 5 / 9, rounds to 2 decimals, and stores it
                      through the celsius setter so the validation is reused.
        kelvin      — read-only property: celsius + 273.15, rounded to 2.
                      Do NOT give it a setter; assigning to it must fail.

    Examples:
        t = Temperature(21.0)
        t.celsius -> 21.0            (no parentheses — it is a property)
        t.fahrenheit -> 69.8
        t.kelvin -> 294.15
        t.fahrenheit = 212           then t.celsius -> 100.0
        t.celsius = -300             raises ValueError
        Temperature(-300)            raises ValueError
        t.kelvin = 0                 raises AttributeError
    """

    def __init__(self, celsius: float) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 3: Temperature.__init__")

    # TODO: your code here — the three properties (and two setters) go below.
    @property
    def celsius(self) -> float:
        raise NotImplementedError("exercise 3: Temperature.celsius")


# ---------------------------------------------------------------------------
# Exercise 4 — @classmethod alternative constructors, @staticmethod helper
# ---------------------------------------------------------------------------
class Duration:
    """A length of time in whole hours and minutes.

    __init__(hours, minutes) validates: ValueError if either is negative, or if
    minutes is greater than 59.

    Methods:
        from_string(text): CLASSMETHOD. Parse "H:MM". Reject anything
            is_valid() rejects, with ValueError(f"cannot parse duration: {text!r}").
            Build the result with cls(...), not Duration(...), so subclasses work.
        from_minutes(total): CLASSMETHOD. Build from a total minute count.
        is_valid(text): STATICMETHOD. True when `text` is two digit-only parts
            separated by exactly one ":" and the minutes part is below 60.
        total_minutes(): hours * 60 + minutes.

    __repr__: f"Duration(hours={hours!r}, minutes={minutes!r})"
    __str__:  f"{hours}h{minutes:02d}m"  ->  "1h30m", "2h05m"

    Examples:
        str(Duration.from_string("1:30")) -> "1h30m"
        Duration.from_string("1:30").total_minutes() -> 90
        str(Duration.from_minutes(150)) -> "2h30m"
        str(Duration.from_minutes(5)) -> "0h05m"
        Duration.is_valid("1:30") -> True
        Duration.is_valid("1:75") -> False
        Duration.is_valid("90") -> False
        Duration.is_valid("a:bb") -> False
        Duration.from_string("oops") -> raises ValueError
        Duration(1, 60) -> raises ValueError
        Duration(-1, 0) -> raises ValueError
        repr(Duration(1, 30)) -> "Duration(hours=1, minutes=30)"
    """

    def __init__(self, hours: int, minutes: int) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 4: Duration.__init__")

    # TODO: your code here — from_string and from_minutes are @classmethod,
    # is_valid is @staticmethod. Do not forget the decorators.
    @classmethod
    def from_string(cls, text: str) -> Duration:
        raise NotImplementedError("exercise 4: Duration.from_string")

    @classmethod
    def from_minutes(cls, total: int) -> Duration:
        raise NotImplementedError("exercise 4: Duration.from_minutes")

    @staticmethod
    def is_valid(text: str) -> bool:
        raise NotImplementedError("exercise 4: Duration.is_valid")

    def total_minutes(self) -> int:
        raise NotImplementedError("exercise 4: Duration.total_minutes")

    def __repr__(self) -> str:
        raise NotImplementedError("exercise 4: Duration.__repr__")

    def __str__(self) -> str:
        raise NotImplementedError("exercise 4: Duration.__str__")


# ---------------------------------------------------------------------------
# Exercise 5 — dunder methods
# ---------------------------------------------------------------------------
class Playlist:
    """A named list of tracks that behaves like a Python container.

    Keep the tracks in `self._tracks`. Copy the list you are given, so the
    caller cannot mutate your playlist behind your back.

    Attributes:
        name: the playlist's name.

    Methods:
        add(track): append a track. Ignore a track that is empty after
            stripping. Store tracks stripped.

    Dunders to implement:
        __len__      -> how many tracks (so bool(playlist) is False when empty)
        __contains__ -> case-insensitive membership: "Bad" in playlist finds "bad"
        __iter__     -> iterating yields the tracks in order (return iter(...))
        __eq__       -> equal when the name AND the tracks match. Return
                        NotImplemented for anything that is not a Playlist.
        __repr__     -> f"Playlist(name={name!r}, tracks={tracks!r})"

    Examples:
        p = Playlist("road trip", ["Bad", "Thriller"])
        len(p) -> 2
        "bad" in p -> True
        "BAD" in p -> True
        "nope" in p -> False
        list(p) -> ["Bad", "Thriller"]
        sorted(p) -> ["Bad", "Thriller"]
        p.add("  Beat It ")
        list(p) -> ["Bad", "Thriller", "Beat It"]
        bool(Playlist("empty")) -> False
        Playlist("a", ["x"]) == Playlist("a", ["x"]) -> True
        Playlist("a", ["x"]) == Playlist("b", ["x"]) -> False
        Playlist("a", ["x"]) == "a" -> False
        repr(Playlist("a", ["x"])) -> "Playlist(name='a', tracks=['x'])"
    """

    def __init__(self, name: str, tracks: list[str] | None = None) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 5: Playlist.__init__")

    def add(self, track: str) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 5: Playlist.add")

    # TODO: your code here — __len__, __contains__, __iter__, __eq__, __repr__
    def __len__(self) -> int:
        raise NotImplementedError("exercise 5: Playlist.__len__")


# ---------------------------------------------------------------------------
# Exercise 6 — composition and delegation
# ---------------------------------------------------------------------------
class Engine:
    """A part. Knows nothing about cars.

    Attributes:
        horsepower: how strong it is.
        running: whether it is currently on. Starts False.

    Methods:
        start(): "engine started", or "already running" if it was already on.
            Sets running to True either way.
        stop(): "engine stopped", and sets running to False.

    Examples:
        e = Engine(90)
        e.running -> False
        e.start() -> "engine started"
        e.running -> True
        e.start() -> "already running"
        e.stop() -> "engine stopped"
        e.running -> False
    """

    def __init__(self, horsepower: int) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Engine.__init__")

    def start(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Engine.start")

    def stop(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Engine.stop")


class Car:
    """A car that HAS an engine (composition), rather than IS one.

    __init__(model, horsepower) must build its own Engine and store it as
    `self.engine`, so it can be swapped later.

    Methods:
        start(): f"{model}: {engine.start()}"  — delegate to the part.
        stop(): f"{model}: {engine.stop()}"
        running: a read-only @property reporting self.engine.running.

    Because this is composition, `car.engine = something_else` must keep
    working as long as the replacement has start(), stop() and running — that
    is duck typing, and the tests check it.

    Examples:
        car = Car("Mini", 90)
        car.start() -> "Mini: engine started"
        car.running -> True
        car.start() -> "Mini: already running"
        car.stop() -> "Mini: engine stopped"
        car.running -> False
    """

    def __init__(self, model: str, horsepower: int) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Car.__init__")

    def start(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Car.start")

    def stop(self) -> str:
        # TODO: your code here
        raise NotImplementedError("exercise 6: Car.stop")

    # TODO: your code here — `running` as a read-only property
    @property
    def running(self) -> bool:
        raise NotImplementedError("exercise 6: Car.running")


# ---------------------------------------------------------------------------
# Exercise 7 — duck typing
# ---------------------------------------------------------------------------
def render_all(items: list) -> list[str]:
    """Render every item, using its own render() when it has one.

    For each item in order:
      * if calling item.render() works, use whatever it returns;
      * if the item has no render at all, use str(item) instead.

    Do it with duck typing — try the call and handle the AttributeError, or
    check with hasattr. Do NOT write a chain of isinstance() checks: the whole
    point is that a brand-new class with a render() method works with no
    changes to this function.

    Args:
        items: anything at all, mixed types welcome.

    Returns:
        One string per item, in the same order.

    Examples:
        class Divider:
            def render(self): return "---"
        render_all([Divider(), 42, "hi"]) -> ["---", "42", "hi"]
        render_all([]) -> []
    """
    # TODO: your code here
    raise NotImplementedError("exercise 7: render_all")


# ---------------------------------------------------------------------------
# Exercise 8 — the hard one: functions first, then a thin class on top
# ---------------------------------------------------------------------------
def subtotal(lines: list[dict]) -> float:
    """Return the sum of price * quantity over `lines`, rounded to 2 decimals.

    Each line is a dict with "name", "price" and "quantity".

    Examples:
        subtotal([{"name": "widget", "price": 10.0, "quantity": 2}]) -> 20.0
        subtotal([{"name": "a", "price": 1.5, "quantity": 3},
                  {"name": "b", "price": 0.5, "quantity": 1}]) -> 5.0
        subtotal([]) -> 0.0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: subtotal")


def apply_coupon(amount: float, code: str | None) -> float:
    """Return `amount` with the coupon `code` applied, rounded to 2 decimals.

    Rules, using the COUPONS dict at the top of this file:
        None      -> unchanged (return `amount` as it came in)
        "SAVE10"  -> 10% off
        "FIVER"   -> 5.00 off, but never below 0.0
        anything else -> raise ValueError(f"unknown coupon: {code}")

    Examples:
        apply_coupon(20.0, None) -> 20.0
        apply_coupon(20.0, "SAVE10") -> 18.0
        apply_coupon(20.0, "FIVER") -> 15.0
        apply_coupon(3.0, "FIVER") -> 0.0
        apply_coupon(20.0, "NOPE") -> raises ValueError
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: apply_coupon")


def cart_total(
    lines: list[dict], code: str | None = None, tax_rate: float = 0.2
) -> float:
    """Return the final total: subtotal, then coupon, then tax.

    Rounded to 2 decimals. Build this from the two functions above rather than
    repeating their logic.

    Examples:
        lines = [{"name": "widget", "price": 10.0, "quantity": 2}]
        cart_total(lines) -> 24.0
        cart_total(lines, "SAVE10") -> 21.6
        cart_total(lines, None, 0.0) -> 20.0
        cart_total([]) -> 0.0
    """
    # TODO: your code here
    raise NotImplementedError("exercise 8: cart_total")


class Cart:
    """The object version: it holds the state and guards it. The maths is reused.

    Keep the lines in `self._lines`. Every method below must call the functions
    above rather than re-implementing the arithmetic — that layering (pure
    functions doing the work, a thin object holding the state) is the point of
    this exercise.

    Methods:
        add(name, price, quantity): append a line dict with those three keys.
            ValueError if price < 0 or quantity <= 0, and a rejected line must
            not be stored.
        subtotal(): the subtotal of its own lines.
        total(code=None, tax_rate=0.2): the final total of its own lines.
        __len__: how many lines it holds.

    Examples:
        cart = Cart()
        len(cart) -> 0
        cart.add("widget", 10.0, 2)
        len(cart) -> 1
        cart.subtotal() -> 20.0
        cart.total() -> 24.0
        cart.total("SAVE10") -> 21.6
        cart.add("bad", 1.0, 0) -> raises ValueError
        cart.add("bad", -1.0, 1) -> raises ValueError
    """

    def __init__(self) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Cart.__init__")

    def add(self, name: str, price: float, quantity: int) -> None:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Cart.add")

    def subtotal(self) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Cart.subtotal")

    def total(self, code: str | None = None, tax_rate: float = 0.2) -> float:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Cart.total")

    def __len__(self) -> int:
        # TODO: your code here
        raise NotImplementedError("exercise 8: Cart.__len__")


if __name__ == "__main__":
    # Quick manual poking ground. Uncomment as you implement each exercise.
    # print(Square(3).describe())
    # print(Duration.from_string("1:30"))
    print("Run `python check.py day13` from the course root to grade your work.")
