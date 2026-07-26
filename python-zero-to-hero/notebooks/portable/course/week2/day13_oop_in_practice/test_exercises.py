"""Day 13 graded checks — OOP in practice."""

import pytest


# --- Exercise 1: Shape / Square / Circle ----------------------------------
def test_square_area_and_name(day):
    square = day.Square(3)
    assert square.area() == 9
    assert square.name == "square"


def test_circle_area_uses_the_pi_constant(day):
    assert day.Circle(1).area() == pytest.approx(3.14159)
    assert day.Circle(2).area() == pytest.approx(12.56636)


def test_describe_is_inherited_and_polymorphic(day):
    assert day.Square(3).describe() == "square with area 9.00"
    assert day.Circle(1).describe() == "circle with area 3.14"


def test_subclasses_are_shapes(day):
    assert isinstance(day.Square(3), day.Shape)
    assert issubclass(day.Circle, day.Shape)


def test_base_shape_area_is_abstract(day):
    shape = day.Shape("blob")
    with pytest.raises(NotImplementedError):
        shape.area()


# --- Exercise 2: Employee / Manager ---------------------------------------
def test_employee_pay_and_description(day):
    employee = day.Employee("Ada", 5000.0)
    assert employee.annual_pay() == 60000.0
    assert employee.describe() == "Ada earns 60000.00 a year"


def test_manager_calls_super_init(day):
    manager = day.Manager("Grace", 5000.0, ["ada", "linus"])
    assert manager.name == "Grace"
    assert manager.monthly_salary == 5000.0, "did you call super().__init__?"
    assert manager.reports == ["ada", "linus"]


def test_manager_extends_annual_pay(day):
    assert day.Manager("Grace", 5000.0, ["ada", "linus"]).annual_pay() == 62000.0
    assert day.Manager("Zoe", 1000.0, []).annual_pay() == 12000.0


def test_manager_extends_describe(day):
    got = day.Manager("Grace", 5000.0, ["ada", "linus"]).describe()
    assert got == "Grace earns 62000.00 a year, managing 2", f"got {got!r}"


def test_manager_copies_the_reports_list(day):
    reports = ["ada"]
    manager = day.Manager("Grace", 5000.0, reports)
    reports.append("linus")
    assert manager.reports == ["ada"], "store a copy so the caller cannot change you"


# --- Exercise 3: Temperature properties -----------------------------------
def test_temperature_celsius_is_a_property(day):
    temperature = day.Temperature(21.0)
    assert temperature.celsius == 21.0
    assert isinstance(type(temperature).celsius, property), (
        "celsius must be a @property, not a plain attribute or a method"
    )


def test_temperature_fahrenheit_and_kelvin(day):
    temperature = day.Temperature(21.0)
    assert temperature.fahrenheit == 69.8
    assert temperature.kelvin == 294.15


def test_temperature_celsius_setter_validates(day):
    temperature = day.Temperature(21.0)
    temperature.celsius = -273.15
    assert temperature.celsius == -273.15
    with pytest.raises(ValueError):
        temperature.celsius = -300
    assert temperature.celsius == -273.15


def test_temperature_constructor_uses_the_setter(day):
    with pytest.raises(ValueError):
        day.Temperature(-300)


def test_temperature_fahrenheit_setter_reuses_validation(day):
    temperature = day.Temperature(21.0)
    temperature.fahrenheit = 212
    assert temperature.celsius == 100.0
    with pytest.raises(ValueError):
        temperature.fahrenheit = -500


def test_temperature_kelvin_is_read_only(day):
    temperature = day.Temperature(21.0)
    with pytest.raises(AttributeError):
        temperature.kelvin = 0


# --- Exercise 4: Duration -------------------------------------------------
def test_duration_from_string(day):
    duration = day.Duration.from_string("1:30")
    assert (duration.hours, duration.minutes) == (1, 30)
    assert str(duration) == "1h30m"
    assert duration.total_minutes() == 90


def test_duration_from_minutes(day):
    assert str(day.Duration.from_minutes(150)) == "2h30m"
    assert str(day.Duration.from_minutes(5)) == "0h05m"


def test_duration_is_valid_is_a_static_check(day):
    assert day.Duration.is_valid("1:30") is True
    assert day.Duration.is_valid("1:75") is False
    assert day.Duration.is_valid("90") is False
    assert day.Duration.is_valid("a:bb") is False


def test_duration_from_string_rejects_junk(day):
    with pytest.raises(ValueError, match="cannot parse duration"):
        day.Duration.from_string("oops")


def test_duration_init_validates(day):
    with pytest.raises(ValueError):
        day.Duration(1, 60)
    with pytest.raises(ValueError):
        day.Duration(-1, 0)


def test_duration_repr(day):
    assert repr(day.Duration(1, 30)) == "Duration(hours=1, minutes=30)"


def test_duration_classmethods_respect_subclasses(day):
    class Precise(day.Duration):
        pass

    assert isinstance(Precise.from_minutes(90), Precise), (
        "build with cls(...) inside a classmethod, not the hard-coded class name"
    )


# --- Exercise 5: Playlist dunders -----------------------------------------
def test_playlist_len_and_bool(day):
    playlist = day.Playlist("road trip", ["Bad", "Thriller"])
    assert len(playlist) == 2
    assert bool(day.Playlist("empty")) is False


def test_playlist_contains_is_case_insensitive(day):
    playlist = day.Playlist("road trip", ["Bad", "Thriller"])
    assert "bad" in playlist
    assert "BAD" in playlist
    assert "nope" not in playlist


def test_playlist_is_iterable(day):
    playlist = day.Playlist("road trip", ["Bad", "Thriller"])
    assert list(playlist) == ["Bad", "Thriller"]
    assert sorted(playlist) == ["Bad", "Thriller"]


def test_playlist_add_strips_and_ignores_blanks(day):
    playlist = day.Playlist("road trip", ["Bad"])
    playlist.add("  Beat It ")
    playlist.add("   ")
    assert list(playlist) == ["Bad", "Beat It"]


def test_playlist_equality(day):
    assert day.Playlist("a", ["x"]) == day.Playlist("a", ["x"])
    assert day.Playlist("a", ["x"]) != day.Playlist("b", ["x"])
    assert day.Playlist("a", ["x"]) != day.Playlist("a", ["y"])
    assert (day.Playlist("a", ["x"]) == "a") is False


def test_playlist_copies_the_track_list(day):
    tracks = ["Bad"]
    playlist = day.Playlist("road trip", tracks)
    tracks.append("Thriller")
    assert len(playlist) == 1


def test_playlist_repr(day):
    assert repr(day.Playlist("a", ["x"])) == "Playlist(name='a', tracks=['x'])"


# --- Exercise 6: Engine / Car composition ---------------------------------
def test_engine_start_and_stop(day):
    engine = day.Engine(90)
    assert engine.running is False
    assert engine.start() == "engine started"
    assert engine.running is True
    assert engine.start() == "already running"
    assert engine.stop() == "engine stopped"
    assert engine.running is False


def test_car_delegates_to_its_engine(day):
    car = day.Car("Mini", 90)
    assert car.start() == "Mini: engine started"
    assert car.running is True
    assert car.start() == "Mini: already running"
    assert car.stop() == "Mini: engine stopped"
    assert car.running is False


def test_car_has_an_engine_rather_than_being_one(day):
    car = day.Car("Mini", 90)
    assert isinstance(car.engine, day.Engine)
    assert not isinstance(car, day.Engine), "a Car is not a kind of Engine — compose"


def test_car_engine_can_be_swapped_for_any_duck(day):
    class Motor:
        def __init__(self) -> None:
            self.running = False

        def start(self) -> str:
            self.running = True
            return "motor humming"

        def stop(self) -> str:
            self.running = False
            return "motor silent"

    car = day.Car("Leaf", 0)
    car.engine = Motor()
    assert car.start() == "Leaf: motor humming"
    assert car.running is True


# --- Exercise 7: render_all duck typing -----------------------------------
class Divider:
    def render(self) -> str:
        return "---"


class Shouty:
    def __init__(self, text: str) -> None:
        self.text = text

    def render(self) -> str:
        return self.text.upper()


def test_render_all_uses_render_when_present(day):
    assert day.render_all([Divider(), Shouty("hi")]) == ["---", "HI"]


def test_render_all_falls_back_to_str(day):
    assert day.render_all([42, "hi", None]) == ["42", "hi", "None"]


def test_render_all_mixes_freely(day):
    assert day.render_all([Divider(), 42, "hi"]) == ["---", "42", "hi"]


def test_render_all_empty(day):
    assert day.render_all([]) == []


def test_render_all_accepts_a_brand_new_class(day):
    class JustInvented:
        def render(self) -> str:
            return "new!"

    assert day.render_all([JustInvented()]) == ["new!"]


# --- Exercise 8: functions and the thin class -----------------------------
LINES = [{"name": "widget", "price": 10.0, "quantity": 2}]


def test_subtotal(day):
    assert day.subtotal(LINES) == 20.0
    assert day.subtotal([]) == 0.0
    assert day.subtotal(
        [
            {"name": "a", "price": 1.5, "quantity": 3},
            {"name": "b", "price": 0.5, "quantity": 1},
        ]
    ) == 5.0


def test_apply_coupon_rules(day):
    assert day.apply_coupon(20.0, None) == 20.0
    assert day.apply_coupon(20.0, "SAVE10") == 18.0
    assert day.apply_coupon(20.0, "FIVER") == 15.0
    assert day.apply_coupon(3.0, "FIVER") == 0.0


def test_apply_coupon_rejects_unknown_code(day):
    with pytest.raises(ValueError, match="unknown coupon"):
        day.apply_coupon(20.0, "NOPE")


def test_cart_total_applies_coupon_then_tax(day):
    assert day.cart_total(LINES) == 24.0
    assert day.cart_total(LINES, "SAVE10") == 21.6
    assert day.cart_total(LINES, None, 0.0) == 20.0
    assert day.cart_total([]) == 0.0


def test_cart_class_matches_the_functions(day):
    cart = day.Cart()
    assert len(cart) == 0
    cart.add("widget", 10.0, 2)
    assert len(cart) == 1
    assert cart.subtotal() == day.subtotal(LINES)
    assert cart.total() == day.cart_total(LINES)
    assert cart.total("SAVE10") == day.cart_total(LINES, "SAVE10")


def test_cart_validates_and_keeps_bad_lines_out(day):
    cart = day.Cart()
    with pytest.raises(ValueError):
        cart.add("bad", 1.0, 0)
    with pytest.raises(ValueError):
        cart.add("bad", -1.0, 1)
    assert len(cart) == 0, "a rejected line must not be stored"


def test_cart_totals_several_lines(day):
    cart = day.Cart()
    cart.add("a", 1.5, 3)
    cart.add("b", 0.5, 1)
    assert cart.subtotal() == 5.0
    assert cart.total(None, 0.0) == 5.0
