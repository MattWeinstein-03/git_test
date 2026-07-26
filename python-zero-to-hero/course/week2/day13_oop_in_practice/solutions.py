"""Day 13 solutions — OOP in practice.

Reference implementations. Same names and signatures as exercises.py.
"""

from __future__ import annotations

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
        self.name = name

    def area(self) -> float:
        # why: the plain-Python way to declare an abstract method.
        raise NotImplementedError("subclasses must implement area()")

    def describe(self) -> str:
        # why: self.area() resolves to the SUBCLASS's version at runtime, so
        # this one line serves every shape that will ever exist.
        return f"{self.name} with area {self.area():.2f}"


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
        super().__init__("square")
        self.side = side

    def area(self) -> float:
        return self.side ** 2


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
        super().__init__("circle")
        self.radius = radius

    def area(self) -> float:
        return PI * self.radius ** 2


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
        self.name = name
        self.monthly_salary = monthly_salary

    def annual_pay(self) -> float:
        return self.monthly_salary * 12

    def describe(self) -> str:
        return f"{self.name} earns {self.annual_pay():.2f} a year"


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
        super().__init__(name, monthly_salary)
        # why: list(...) copies, so later changes to the caller's list cannot
        # reach inside this object.
        self.reports = list(reports)

    def annual_pay(self) -> float:
        base = super().annual_pay()
        return base + self.BONUS_PER_REPORT * len(self.reports)

    def describe(self) -> str:
        return super().describe() + f", managing {len(self.reports)}"


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
        # why: assigning to the PROPERTY runs the setter, so construction and
        # later assignment share one validation rule.
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        """The temperature in degrees Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < ABSOLUTE_ZERO_C:
            raise ValueError(f"below absolute zero: {value}")
        # why: the stored attribute is _celsius. Assigning to self.celsius here
        # would call this setter again, forever (RecursionError).
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """The same temperature in degrees Fahrenheit (computed, not stored)."""
        return round(self._celsius * 9 / 5 + 32, 2)

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = round((value - 32) * 5 / 9, 2)

    @property
    def kelvin(self) -> float:
        """Read-only: there is deliberately no setter."""
        return round(self._celsius + 273.15, 2)


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
        if hours < 0 or minutes < 0:
            raise ValueError("duration cannot be negative")
        if minutes > 59:
            raise ValueError(f"minutes must be 0-59, got {minutes}")
        self.hours = hours
        self.minutes = minutes

    @classmethod
    def from_string(cls, text: str) -> Duration:
        if not cls.is_valid(text):
            raise ValueError(f"cannot parse duration: {text!r}")
        hours_text, minutes_text = text.split(":")
        # why: cls(...) means a subclass calling this gets a subclass instance.
        return cls(int(hours_text), int(minutes_text))

    @classmethod
    def from_minutes(cls, total: int) -> Duration:
        return cls(total // 60, total % 60)

    @staticmethod
    def is_valid(text: str) -> bool:
        # why: no instance and no class is needed, but the question is about
        # durations — so it lives here rather than at module level.
        parts = text.split(":")
        if len(parts) != 2:
            return False
        if not parts[0].isdigit() or not parts[1].isdigit():
            return False
        return int(parts[1]) < 60

    def total_minutes(self) -> int:
        return self.hours * 60 + self.minutes

    def __repr__(self) -> str:
        return f"Duration(hours={self.hours!r}, minutes={self.minutes!r})"

    def __str__(self) -> str:
        return f"{self.hours}h{self.minutes:02d}m"


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
        self.name = name
        self._tracks: list[str] = list(tracks) if tracks is not None else []

    def add(self, track: str) -> None:
        cleaned = track.strip()
        if not cleaned:
            return
        self._tracks.append(cleaned)

    def __len__(self) -> int:
        # why: with no __bool__, truthiness falls back to len() != 0, so an
        # empty playlist is falsy for free.
        return len(self._tracks)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, str):
            return False
        wanted = item.lower()
        for track in self._tracks:
            if track.lower() == wanted:
                return True
        return False

    def __iter__(self):
        # why: delegate to the list's iterator — the simplest correct answer.
        return iter(self._tracks)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Playlist):
            # why: NotImplemented means "I don't know", letting Python ask the
            # other object. Returning False here would break symmetry.
            return NotImplemented
        return self.name == other.name and self._tracks == other._tracks

    def __repr__(self) -> str:
        return f"Playlist(name={self.name!r}, tracks={self._tracks!r})"


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
        self.model = model
        # why: HAS-A. Inheriting from Engine would make every Engine method
        # part of Car's API and make swapping the part impossible.
        self.engine = Engine(horsepower)

    def start(self) -> str:
        return f"{self.model}: {self.engine.start()}"

    def stop(self) -> str:
        return f"{self.model}: {self.engine.stop()}"

    @property
    def running(self) -> bool:
        # why: expose exactly one detail of the part, read-only.
        return self.engine.running


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
    output: list[str] = []
    for item in items:
        # why: getattr with a default keeps an AttributeError raised INSIDE
        # render() from being mistaken for "this object cannot render".
        renderer = getattr(item, "render", None)
        if callable(renderer):
            output.append(renderer())
        else:
            output.append(str(item))
    return output


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
    total = 0.0
    for line in lines:
        total += line["price"] * line["quantity"]
    return round(total, 2)


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
    if code is None:
        return amount
    if code == "SAVE10":
        return round(amount * (1 - COUPONS["SAVE10"]), 2)
    if code == "FIVER":
        return round(max(amount - COUPONS["FIVER"], 0.0), 2)
    raise ValueError(f"unknown coupon: {code}")


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
    # why: composed from the smaller pure functions, so each rule has one home.
    discounted = apply_coupon(subtotal(lines), code)
    return round(discounted * (1 + tax_rate), 2)


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
        self._lines: list[dict] = []

    def add(self, name: str, price: float, quantity: int) -> None:
        # why: validate first, so a rejected line is never stored.
        if price < 0:
            raise ValueError(f"price must not be negative, got {price}")
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")
        self._lines.append({"name": name, "price": price, "quantity": quantity})

    def subtotal(self) -> float:
        return subtotal(self._lines)

    def total(self, code: str | None = None, tax_rate: float = 0.2) -> float:
        return cart_total(self._lines, code, tax_rate)

    def __len__(self) -> int:
        return len(self._lines)


if __name__ == "__main__":
    print(Square(3).describe())
    print(Duration.from_string("1:30"))
    cart = Cart()
    cart.add("widget", 10.0, 2)
    print(len(cart), cart.subtotal(), cart.total("SAVE10"))
