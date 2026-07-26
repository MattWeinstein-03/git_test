# Day 13 — OOP in Practice

> **Time:** ~4 hours  |  **Prerequisites:** Day 12

## What you'll be able to do after today
- Write a subclass that extends a base class, call the parent implementation with `super()`, and predict which method runs by reading the MRO.
- Choose between inheritance and composition with an argument, not a habit.
- Rely on duck typing, and explain why `isinstance` checks everywhere are a smell.
- Turn a plain attribute into a validated one with `@property` without changing a single caller.
- Add alternative constructors with `@classmethod` and namespaced helpers with `@staticmethod`.
- Implement `__eq__`, `__len__`, `__contains__` and `__iter__` so your objects work with `==`, `len()`, `in` and `for`.
- Recognise when a class is ceremony around a function, and write the module-of-functions version instead.

## Why this matters

Day 12 gave you classes. Today is about the decisions — and OOP is where inexperienced programmers most reliably over-engineer. A five-level inheritance hierarchy for three behaviours, an `AbstractBaseManagerFactory`, a class with one method and no state: all of it comes from learning the mechanics without the judgement.

The mechanics matter because the ecosystem is built on them: `@property` and `@classmethod` appear in every real codebase, and dunder methods are why `len(my_thing)` and `for item in my_thing` work at all. But the judgement matters more, and it compresses to one sentence: *use the smallest tool that models the problem honestly.* Sometimes that is a class hierarchy. Very often it is a function and a dict.

---

## 1. Inheritance: the mechanics

Inheritance says "this class is a specialised version of that class". The subclass gets the parent's attributes and methods for free, and can add or replace any of them.

```python
class Shape:
    def __init__(self, name: str) -> None:
        self.name = name

    def area(self) -> float:
        raise NotImplementedError("subclasses must implement area()")

    def describe(self) -> str:
        return f"{self.name} with area {self.area():.2f}"


class Square(Shape):
    def __init__(self, side: float) -> None:
        super().__init__("square")          # let Shape do its own initialising
        self.side = side

    def area(self) -> float:               # OVERRIDE: replaces Shape.area
        return self.side ** 2


class Circle(Shape):
    PI = 3.14159

    def __init__(self, radius: float) -> None:
        super().__init__("circle")
        self.radius = radius

    def area(self) -> float:
        return self.PI * self.radius ** 2
```

```python
shapes = [Square(3), Circle(1)]
for shape in shapes:
    print(shape.describe())
# square with area 9.00
# circle with area 3.14

print(isinstance(Square(3), Shape))     # True — a Square IS a Shape
print(issubclass(Circle, Shape))        # True
Shape("blob").area()                    # NotImplementedError: subclasses must implement area()
```

The interesting line is `describe()`. It was written once, in `Shape`, and it calls `self.area()` — which resolves to the *subclass's* implementation at runtime. That is **polymorphism**: shared code that adapts to the concrete type. It is the actual payoff of inheritance, and it is worth noticing that nothing in `describe` mentions `Square` or `Circle`.

`Shape.area` raising `NotImplementedError` is the plain-Python way of saying "abstract method: subclasses must supply this". (The `abc` module formalises it so instantiation itself fails; you do not need that yet.)

Vocabulary: `Shape` is the **base class**, **parent**, or **superclass**; `Square` is the **subclass** or **child**. Replacing a parent's method is **overriding**.

> **Gotcha:** inheritance is the tightest coupling in object-oriented programming. A subclass depends on its parent's internals, so a change in the parent can break every child silently. That is why the rest of this lesson keeps pushing you toward composition.

---

## 2. `super()`

`super()` gives you the parent's version of a method. Its two overwhelmingly common uses:

```python
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
        super().__init__(name, monthly_salary)      # 1. reuse the parent's setup
        self.reports = list(reports)

    def annual_pay(self) -> float:
        base = super().annual_pay()                  # 2. extend, do not re-implement
        return base + self.BONUS_PER_REPORT * len(self.reports)

    def describe(self) -> str:
        return super().describe() + f", managing {len(self.reports)}"
```

```python
manager = Manager("Grace", 5000.0, ["ada", "linus"])
print(manager.annual_pay())    # 62000.0   = 60000 + 2 * 1000
print(manager.describe())      # Grace earns 62000.00 a year, managing 2
```

Rules and reasons:

- **Always call `super().__init__(...)` in a subclass `__init__`** if the parent has one. Forget it and the parent's attributes never get set, producing an `AttributeError` far from the cause.
- Write `super()` with no arguments. The Python 2 form `super(Manager, self)` still works and adds nothing.
- `super()` follows the MRO (next section), not simply "my parent" — which is what makes it correct under multiple inheritance where hard-coding `Employee.__init__(self, ...)` is not.
- Position matters: call `super().__init__()` *before* using attributes it sets, and after any validation that must happen first.

> **Gotcha:** `super().method()` inside `__init__` calls the parent's method — but if the parent's method calls `self.something()` that the subclass overrides, the *subclass* version runs, possibly before the subclass has finished initialising. Calling overridable methods from `__init__` is a known trap.

---

## 3. MRO, at a practical level

The **method resolution order** is the ordered list of classes Python searches for an attribute. You can read it:

```python
print(Manager.__mro__)
# (<class 'Manager'>, <class 'Employee'>, <class 'object'>)

print([cls.__name__ for cls in Manager.mro()])
# ['Manager', 'Employee', 'object']
```

For single inheritance it is exactly what you expect: the class, then its parent, then its parent, ending at `object` (every class inherits from `object` — that is where the default `__repr__` comes from). First match wins.

Multiple inheritance is where an ordering rule becomes necessary:

```python
class Loggable:
    def describe(self) -> str:
        return "loggable"

class Serialisable:
    def describe(self) -> str:
        return "serialisable"

class Record(Loggable, Serialisable):
    pass

print(Record().describe())                          # loggable
print([c.__name__ for c in Record.mro()])
# ['Record', 'Loggable', 'Serialisable', 'object']
```

The practical rules, which is all you need:

1. **Left to right, depth-first, with a rule about shared ancestors** (C3 linearisation): a class always comes before its parents, and the order you listed the bases is respected.
2. **First match wins**, so `Loggable.describe` shadows `Serialisable.describe`.
3. `super()` means "the next class in the MRO **after me**", not "my parent". In a diamond, that can be a *sibling* branch — which is how cooperative multiple inheritance works, and why every class in such a hierarchy must call `super()`.

The famous diamond:

```
      A
     / \
    B   C
     \ /
      D          D.mro() -> [D, B, C, A, object]
```

Each of `B` and `C` calling `super().__init__()` means `A.__init__` runs exactly once, in the right order. Skip one `super()` call and part of the chain silently disappears.

Honest advice: **avoid multiple inheritance** for state-bearing classes. It is legitimate for **mixins** — small, stateless classes that add one behaviour (`class JsonMixin: def to_json(self): ...`) — and a maintenance burden for anything else. If you find yourself drawing the diamond, use composition.

> **Gotcha:** `TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y` means your base list contradicts an inherited ordering (e.g. `class D(A, B)` where `B` already inherits from `A`). Fix the base order — most specific first.

---

## 4. Composition, and why to prefer it

**Inheritance** is "is-a". **Composition** is "has-a": the object holds another object and delegates work to it.

```python
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


class Car:
    def __init__(self, model: str, horsepower: int) -> None:
        self.model = model
        self.engine = Engine(horsepower)      # HAS-A: composition

    def start(self) -> str:
        return f"{self.model}: {self.engine.start()}"    # delegate

    @property
    def running(self) -> bool:
        return self.engine.running                       # expose one detail
```

```python
car = Car("Mini", 90)
print(car.start())      # Mini: engine started
print(car.running)      # True
print(car.start())      # Mini: already running
```

Contrast with the tempting alternative, `class Car(Engine)`. It "works": `car.start()` exists, `car.horsepower` exists. It is also a lie — a car is not a kind of engine — and lies in your type model cost you later: every `Engine` method becomes part of `Car`'s public surface, `Car` cannot have two engines or swap to an electric motor, and any change to `Engine`'s internals can break `Car`.

Why composition is the default choice:

| | Inheritance | Composition |
|---|---|---|
| Coupling | Tight: you depend on the parent's internals | Loose: you depend only on the part's public API |
| Change at runtime | Impossible — the type is fixed | Easy: swap the part (`car.engine = ElectricMotor()`) |
| Multiple parts | One hierarchy, awkward | Natural: an engine *and* a gearbox *and* a radio |
| Testing | Must construct the whole hierarchy | Pass a simple fake part |
| Public surface | Everything the parent exposes | Exactly what you choose to delegate |

The test to apply, in order:

1. Is it genuinely an **is-a** relationship — is every instance of the child usable anywhere the parent is expected? (That is the Liskov Substitution Principle, and it is the only real justification for inheritance.)
2. Do you need shared *interface* rather than shared *code*? Duck typing (next section) gives you that with no hierarchy at all.
3. Otherwise: **has-a**. Hold the object and delegate.

`Square(Shape)` passes test 1: every square is a shape, and any code that asks for a shape's area works on a square. `Car(Engine)` fails it.

> **Gotcha:** delegation can get verbose — five one-line methods that just forward. That verbosity is a *feature*: it is you choosing the public surface explicitly. Reach for `__getattr__`-based auto-forwarding only when you can explain what it hides.

---

## 5. Duck typing

> "If it walks like a duck and quacks like a duck, treat it as a duck."

Python does not require a shared base class for polymorphism. It requires only that the object *has the method you call*.

```python
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
            output.append(item.render())          # EAFP: just try it
        except AttributeError:
            output.append(str(item))              # not a duck; be reasonable
    return output
```

```python
print(render_all([TextBlock("  hello  "), Divider(), 42]))
# ['hello', '--------------------', '42']
```

`TextBlock` and `Divider` share no base class. They share a *protocol*: "has a `render()` that returns a string". That is all `render_all` needs. This is why the standard library works on "anything with `read()`" and "anything iterable" rather than on specific classes — and it is why your code should accept any file-like object rather than demanding a real file.

The corresponding smell:

```python
# smell: a type switchboard
def render(item):
    if isinstance(item, TextBlock):
        return item.text.strip()
    elif isinstance(item, Divider):
        return "-" * 20
    elif isinstance(item, Image):
        return f"[image {item.name}]"
```

Every new kind of thing means editing this function — and every other function like it. The duck-typed version needs no edit at all: a new class with a `render()` method just works. The rule of thumb: **if you find yourself branching on type, the behaviour probably belongs on the objects.**

When `isinstance` *is* right:

- At a boundary, validating input from outside your program: `if not isinstance(amount, (int, float)): raise TypeError(...)`.
- Handling a genuine either/or in the data: `if isinstance(value, str): value = [value]`.
- Narrowing types for a static checker.

`hasattr(item, "render")` is the LBYL version of the duck test and is fine, though EAFP (`try/except AttributeError`) is more idiomatic and avoids a check-then-act gap.

> **Gotcha:** `except AttributeError` around a method *call* also catches an `AttributeError` raised *inside* that method — silently converting a bug into a fallback. If that worries you (it should), use `hasattr` or grab the method first: `renderer = getattr(item, "render", None)`.

---

## 6. `@property`: computed and validated attributes

Day 12 ended with getters and setters, and the observation that Python does not need them. `@property` is why.

Start with the simplest thing that works — a public attribute:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius
```

Now a requirement arrives: temperatures below absolute zero must be rejected. In a language with no properties, you would add `get_celsius()`/`set_celsius()` and edit every caller. In Python you change the class and **no caller changes at all**:

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius              # goes through the setter below

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
        """The same temperature in degrees Fahrenheit (computed, not stored)."""
        return round(self._celsius * 9 / 5 + 32, 2)

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = round((value - 32) * 5 / 9, 2)      # reuse the validation
```

```python
temperature = Temperature(21.0)
print(temperature.celsius)          # 21.0        — attribute syntax
print(temperature.fahrenheit)       # 69.8        — computed on demand
temperature.fahrenheit = 212
print(temperature.celsius)          # 100.0       — the setter converted it
temperature.celsius = -300          # ValueError: below absolute zero: -300
```

The mechanics:

- `@property` above a method makes it readable as an attribute: `obj.celsius`, no parentheses.
- `@celsius.setter` (the *property's* name, then `.setter`) defines what assignment does.
- The real value conventionally lives in `self._celsius`. The property is the public door.
- A property with no setter is **read-only**: assignment raises `AttributeError: property 'x' of 'Y' object has no setter`. That is an excellent way to expose derived state.

When to use one:

| Use `@property` | Use a method |
|---|---|
| Cheap to compute, feels like data (`area`, `full_name`, `fahrenheit`) | Expensive, does I/O, or can fail in interesting ways |
| Read-only derived state | Anything with parameters — properties take none |
| Adding validation to an existing public attribute | Actions: `save()`, `refresh()`, `send()` |

And the guidance that keeps this from becoming ceremony: **start with a plain public attribute.** Add the property when you actually need validation or computation. Writing speculative properties for every field is the Java habit that Python removed the need for.

> **Gotcha:** `self.celsius = celsius` inside `__init__` runs the setter — which is what you want, since the validation happens once, in one place. But if your setter reads another attribute that has not been assigned yet, you get an `AttributeError` during construction. Order your assignments deliberately.

---

## 7. `@classmethod` and `@staticmethod`

Three kinds of method, distinguished by their first parameter:

| Decorator | First parameter | Gets | Typical use |
|---|---|---|---|
| (none) | `self` | the instance | normal behaviour |
| `@classmethod` | `cls` | the class | alternative constructors |
| `@staticmethod` | — | nothing | a related helper with no state |

```python
class Duration:
    def __init__(self, hours: int, minutes: int) -> None:
        if hours < 0 or minutes < 0:
            raise ValueError("duration cannot be negative")
        if minutes > 59:
            raise ValueError(f"minutes must be 0-59, got {minutes}")
        self.hours = hours
        self.minutes = minutes

    @classmethod
    def from_string(cls, text: str) -> "Duration":
        """Build a Duration from "H:MM" — an ALTERNATIVE CONSTRUCTOR."""
        if not cls.is_valid(text):
            raise ValueError(f"cannot parse duration: {text!r}")
        hours_text, minutes_text = text.split(":")
        return cls(int(hours_text), int(minutes_text))       # cls, not Duration

    @classmethod
    def from_minutes(cls, total: int) -> "Duration":
        """Build a Duration from a total number of minutes."""
        return cls(total // 60, total % 60)

    @staticmethod
    def is_valid(text: str) -> bool:
        """Could `text` be an "H:MM" duration? No instance or class needed."""
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
```

```python
print(Duration.from_string("1:30"))      # 1h30m
print(Duration.from_minutes(150))        # 2h30m
print(Duration.is_valid("1:75"))         # False
print(Duration.from_string("1:30").total_minutes())    # 90
Duration.from_string("oops")             # ValueError: cannot parse duration: 'oops'
```

Why classmethods are the idiomatic way to offer several ways to build an object: `__init__` should have one clear signature, and stuffing four optional parameters into it to cover four input formats produces the worst constructor in the codebase. Named alternatives read better at the call site (`Duration.from_minutes(150)` says exactly what is happening), and you will meet them everywhere: `dict.fromkeys`, `datetime.fromisoformat`, `Path.cwd`.

**Use `cls(...)`, not `ClassName(...)`, inside a classmethod.** Then a subclass calling `from_string` gets an instance of the *subclass*, for free.

`@staticmethod` is the mildest of the three: a plain function that lives inside the class because it belongs to that concept. `Duration.is_valid` needs no instance and no class, but it is about durations, so it lives there. If you cannot justify the namespacing, a module-level function is better — which brings us to the last section.

> **Gotcha:** a `@classmethod` receives the class automatically, so calling `Duration.from_string("1:30")` passes only the string. Forgetting the decorator and writing `def from_string(text)` produces `TypeError: from_string() takes 1 positional argument but 2 were given` when called on an instance, or a confusing `self`-is-a-string bug.

---

## 8. Dunder methods: making your objects behave like Python's

Dunder ("double underscore") methods are Python's protocol hooks. Implement them and the built-in syntax works on your objects.

```python
class Bag:
    """A collection of items that behaves like a Python container."""

    def __init__(self, items: list[str] | None = None) -> None:
        self._items: list[str] = list(items) if items is not None else []

    def add(self, item: str) -> None:
        self._items.append(item)

    def __len__(self) -> int:                 # len(bag)
        return len(self._items)

    def __contains__(self, item: object) -> bool:      # item in bag
        return item in self._items

    def __iter__(self):                       # for x in bag, list(bag), max(bag)
        return iter(self._items)

    def __eq__(self, other: object) -> bool:  # bag == other
        if not isinstance(other, Bag):
            return NotImplemented             # "I don't know", not "unequal"
        return self._items == other._items

    def __repr__(self) -> str:
        return f"Bag(items={self._items!r})"
```

```python
bag = Bag(["apple", "pear"])
bag.add("fig")

print(len(bag))                 # 3
print("pear" in bag)            # True
print("plum" in bag)            # False
for item in bag:
    print(item)                 # apple / pear / fig
print(list(bag))                # ['apple', 'pear', 'fig']
print(sorted(bag))              # ['apple', 'fig', 'pear']
print(bag == Bag(["apple", "pear", "fig"]))    # True
print(bool(Bag()))              # False — empty, because __len__ returns 0
```

The four worth knowing now:

- **`__len__`** — `len(obj)`. Must return a non-negative int. Bonus: with no `__bool__`, truthiness falls back to `len(obj) != 0`, so `if not bag:` works exactly as it does for a list.
- **`__contains__`** — `x in obj`. Without it, `in` falls back to iterating, which still works but is O(n) even when you could answer instantly (e.g. by checking a dict).
- **`__iter__`** — `for x in obj`, `list(obj)`, `sorted(obj)`, `max(obj)`, unpacking. Returning `iter(self._items)` delegates to the list's iterator, which is the simplest correct implementation. (Writing an iterator from scratch, and `yield`, is Day 15.)
- **`__eq__`** — `==`. Two rules: return `NotImplemented` (the singleton, not an exception) for types you do not understand, so Python can try the other operand's `__eq__`; and remember that defining `__eq__` sets `__hash__` to None, making instances unhashable — add `__hash__` or use `@dataclass(frozen=True)` if you need them in a set or as dict keys.

Others you will meet: `__str__`/`__repr__` (Day 12), `__getitem__` (`obj[key]`), `__add__` (`+`), `__lt__` (`<`, and `sorted` uses it), `__call__` (makes an instance callable), `__enter__`/`__exit__` (the `with` protocol from Day 10).

The judgement: implement a dunder when your object genuinely *is* that kind of thing. A `Bag` is a container, so `len` and `in` are honest. Do not implement `__add__` on an `Employee` because it seemed cute — operator overloading that surprises the reader is worse than a plainly named method.

> **Gotcha:** `__eq__` returning `False` for unknown types (instead of `NotImplemented`) breaks symmetry: `bag == 5` would be `False` while `5 == bag` might be `True` via the other object's `__eq__`. Return `NotImplemented` and let Python arbitrate.

---

## 9. When NOT to use OOP

Here is the opinionated part, and it is the most valuable section of the day.

A class earns its place when it has **state plus behaviour over that state**, or when it must **enforce invariants**. Without those, a class is a namespace with extra steps. Four specific smells:

**Smell 1 — a class with one method and no state.**

```python
# ceremony
class PriceFormatter:
    def __init__(self, currency: str = "GBP") -> None:
        self.currency = currency

    def format(self, amount: float) -> str:
        return f"{amount:.2f} {self.currency}"

formatter = PriceFormatter()
print(formatter.format(12.5))
```

```python
# the honest version
def format_price(amount: float, currency: str = "GBP") -> str:
    return f"{amount:.2f} {currency}"

print(format_price(12.5))
```

Two lines instead of six, nothing to instantiate, trivially testable. If your class is `__init__` plus one method, it is a function whose arguments you split across two calls.

**Smell 2 — a class used as a namespace.**

```python
class MathHelpers:                 # a module already does this job
    @staticmethod
    def double(x): return x * 2
    @staticmethod
    def halve(x): return x / 2
```

Put those in `mathhelpers.py` and use `import mathhelpers`. Python has modules; it does not need classes-as-folders.

**Smell 3 — data with no rules.** A parsed JSON payload, a config mapping, a row from a CSV: a `dict` is the right type, and `dataclass` is the right upgrade when the shape is fixed. A hand-written class with five attributes and no validation is just a slower dict.

**Smell 4 — inheritance for code reuse.** "Both need this helper, so I'll make a base class" produces hierarchies that model nothing. Put the helper in a module and call it from both.

### Side by side: the same feature, two ways

A shopping cart with a subtotal, a coupon, and tax.

**As a module of functions** — data is plain, behaviour is separate:

```python
# cart_functions.py
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

def total(lines: list[dict], code: str | None = None, tax_rate: float = 0.2) -> float:
    """Subtotal, coupon, then tax."""
    return round(apply_coupon(subtotal(lines), code) * (1 + tax_rate), 2)
```

```python
lines = [{"name": "widget", "price": 10.0, "quantity": 2}]
print(subtotal(lines))                  # 20.0
print(total(lines, "SAVE10"))           # 21.6
```

**As a class** — state and behaviour bound together:

```python
class Cart:
    def __init__(self) -> None:
        self._lines: list[dict] = []

    def add(self, name: str, price: float, quantity: int) -> None:
        if price < 0 or quantity <= 0:
            raise ValueError("price must be >= 0 and quantity > 0")
        self._lines.append({"name": name, "price": price, "quantity": quantity})

    def subtotal(self) -> float:
        return subtotal(self._lines)                 # reuse the function

    def total(self, code: str | None = None, tax_rate: float = 0.2) -> float:
        return total(self._lines, code, tax_rate)

    def __len__(self) -> int:
        return len(self._lines)
```

```python
cart = Cart()
cart.add("widget", 10.0, 2)
print(len(cart), cart.subtotal(), cart.total("SAVE10"))    # 1 20.0 21.6
```

Which is better? **Neither — they answer different questions.**

| Choose functions when | Choose a class when |
|---|---|
| The data is already a list/dict from a file or an API | You must protect invariants (`add` validates; no invalid cart exists) |
| Each operation is independent | The thing has a lifecycle: add, remove, save, load |
| You want maximum testability with no setup | Callers should not care how the data is stored |
| The pipeline is transform-in, transform-out | You want `len(cart)`, `cart == other`, `for line in cart` |

Notice what the class did *not* do: reimplement the maths. It holds state, validates input, and delegates the calculating to the functions. That layering — **pure functions doing the work, a thin object holding the state** — is the shape most good Python takes, and it is exactly the Day 8 lesson about pure functions, one level up.

> **Gotcha:** "everything must be a class" is a habit imported from languages where it is mandatory. Python's standard library is full of plain functions (`sorted`, `json.dumps`, `os.path.join`) precisely because they are not about state. Write the function; promote it to a class when the state appears.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| Forgetting `super().__init__()` | `AttributeError` for an attribute the parent sets | Call it first in the subclass `__init__` |
| Re-implementing the parent's logic in the child | Divergent duplicate code | `super().method()` then extend |
| `Car(Engine)` — inheritance for has-a | Nonsense API, impossible to swap the part | Composition: hold an `Engine`, delegate |
| Deep hierarchies | Cannot tell where a method comes from | Flatten; prefer composition; read `Class.mro()` |
| `isinstance` chains for behaviour | Editing one function for every new type | Duck typing: put the behaviour on the objects |
| Calling a property with `()` | `TypeError: 'float' object is not callable` | Properties are accessed without parentheses |
| Property setter missing | `AttributeError: property 'x' has no setter` | Add `@x.setter`, or keep it read-only on purpose |
| Property that recurses | `RecursionError` | The property is `x`; store the value in `_x` |
| Forgetting `@classmethod` | `TypeError: ... takes 1 positional argument but 2 were given` | Add the decorator; first parameter is `cls` |
| Hard-coding the class inside a classmethod | Subclasses get the wrong type back | `return cls(...)` |
| `__eq__` returning `False` for unknown types | Asymmetric comparisons | `return NotImplemented` |
| Defining `__eq__` and then using a set | `TypeError: unhashable type` | Add `__hash__`, or `@dataclass(frozen=True)` |
| A class with one method and no state | Ceremony, `__init__` that stores one argument | Write the function |

---

## Mental model

```
   INHERITANCE                        COMPOSITION
   "is-a"                             "has-a"

     Shape                              Car
      |  \                               |
   Square Circle                     has-a Engine  (and a Gearbox, and a Radio)

   Shared code that adapts            Parts you choose, delegate to,
   (Shape.describe calls              and can swap at runtime.
    self.area())                      Public surface = what you forward.

   Coupling: tight                    Coupling: loose
   Use when: every child is           Use when: anything else.
   genuinely usable as the parent.


   DUCK TYPING                        A LADDER OF TOOLS, cheapest first

   No hierarchy at all -- the           1. a function
   object just has .render().           2. a function + a dict/dataclass
   The stdlib works this way:           3. a class (state + invariants)
   "anything with .read()".             4. a class + properties/dunders
                                        5. inheritance (rarely)
   Branching on isinstance is           6. multiple inheritance (almost never)
   the anti-pattern of this idea.
                                      Climb only when the rung below breaks.
```

One sentence to keep: *inheritance shares code down a hierarchy, composition assembles behaviour from parts, duck typing needs neither — and a function needs none of the three.*

---

## Practice

1. Run the demo. Section 9 prints the same cart computed both ways, so you can see that the class adds *structure*, not arithmetic:

   ```bash
   python course/week2/day13_oop_in_practice/examples.py
   ```

2. Open `exercises.py`. Exercise 8 asks you to write the same feature twice — as functions and as a class that reuses them. That is the point, not busywork: it is the layering you will use in tomorrow's project.

3. Grade from the course root:

   ```bash
   python check.py day13
   python check.py day13 -v
   ```

4. Then, on your Day 12 `Expense`/`Store` code: add a `@property` for something derived, an alternative constructor with `@classmethod` (say `Expense.from_csv_row`), and `__len__`/`__iter__` on the store. Tomorrow's project is that class at full size, so time spent here is time saved then.

---

## Recall check

1. What does `super()` actually mean — "my parent", or something more precise?
2. `class Manager(Employee)` with both defining `describe()`. Which runs for a `Manager`, and how do you check the search order in code?
3. Give the test that decides between inheritance and composition, and apply it to `Car`/`Engine`.
4. What is duck typing, and what is the anti-pattern it replaces?
5. You have a public attribute `celsius` used by twenty callers, and you now need to reject values below absolute zero. What do you change, and what do the callers change?
6. When would you use `@classmethod` rather than adding parameters to `__init__`? Why `cls(...)` instead of the class name?
7. Which four dunder methods make an object behave like a container, and what does each enable?
8. Name two of the four smells that mean "this should not be a class", and say what to write instead.

<details>
<summary>Answers</summary>

1. "The next class in the MRO after this one." For single inheritance that is the parent; under multiple inheritance it can be a sibling branch, which is what makes cooperative `super()` calls work.
2. `Manager.describe` — first match in the MRO wins. Check with `Manager.__mro__` or `[c.__name__ for c in Manager.mro()]`.
3. Ask whether every instance of the child is usable anywhere the parent is expected (is-a / Liskov). A `Square` is usable wherever a `Shape` is, so inheritance is fine; a `Car` is not a kind of `Engine`, so `Car` should *hold* an `Engine` and delegate.
4. Relying on the methods an object has rather than its type: if it has `render()`, call it. It replaces `isinstance` chains, which must be edited for every new type, whereas a duck-typed function needs no change at all.
5. Turn `celsius` into a `@property` with a `@celsius.setter` that validates and stores in `self._celsius`. The callers change nothing — that is the entire point of properties.
6. When there are several distinct ways to build the object (`from_string`, `from_minutes`): named alternative constructors keep `__init__` with one clear signature and read better at the call site. Use `cls(...)` so a subclass calling the classmethod gets an instance of the subclass.
7. `__len__` (`len(obj)`, plus truthiness), `__contains__` (`in`), `__iter__` (`for`, `list()`, `sorted()`, unpacking), `__eq__` (`==`, and `NotImplemented` for unknown types).
8. Any two of: a class with one method and no state (write the function); a class used as a namespace (use a module); data with no rules (use a dict or a dataclass); inheritance purely for code reuse (put the helper in a module and call it from both).

</details>
