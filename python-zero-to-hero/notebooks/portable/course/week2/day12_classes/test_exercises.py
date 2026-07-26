"""Day 12 graded checks — Classes."""

import pytest


# --- Exercise 1: Point ----------------------------------------------------
def test_point_stores_coordinates(day):
    point = day.Point(3, 4)
    assert point.x == 3
    assert point.y == 4


def test_point_repr_looks_like_a_constructor_call(day):
    assert repr(day.Point(3, 4)) == "Point(x=3, y=4)"


def test_point_distance_to(day):
    assert day.Point(3, 4).distance_to(day.Point(0, 0)) == 5.0
    assert day.Point(0, 0).distance_to(day.Point(1, 1)) == 1.41


def test_point_distance_to_itself_is_zero(day):
    point = day.Point(2.5, -3)
    assert point.distance_to(point) == 0.0


def test_point_moved_by_returns_a_new_point(day):
    point = day.Point(3, 4)
    moved = point.moved_by(1, -1)
    assert (moved.x, moved.y) == (4, 3)
    assert (point.x, point.y) == (3, 4), "moved_by must not modify the original"
    assert moved is not point


# --- Exercise 2: BankAccount ----------------------------------------------
def test_bank_account_defaults_to_zero(day):
    account = day.BankAccount("Ada")
    assert account.owner == "Ada"
    assert account.balance == 0.0
    assert account.history == []


def test_bank_account_deposit_and_withdraw(day):
    account = day.BankAccount("Ada", 100.0)
    assert account.deposit(50) == 150.0
    assert account.withdraw(30) == 120.0
    assert account.balance == 120.0


def test_bank_account_records_history(day):
    account = day.BankAccount("Ada", 100.0)
    account.deposit(50)
    account.withdraw(30)
    assert account.history == ["deposit 50.00", "withdraw 30.00"]


def test_bank_account_refuses_overdraft_without_side_effects(day):
    account = day.BankAccount("Ada", 100.0)
    with pytest.raises(ValueError):
        account.withdraw(1000)
    assert account.balance == 100.0
    assert account.history == [], "a rejected operation must not be recorded"


def test_bank_account_rejects_bad_amounts(day):
    account = day.BankAccount("Ada", 10.0)
    with pytest.raises(ValueError):
        account.deposit(0)
    with pytest.raises(ValueError):
        account.withdraw(-5)
    with pytest.raises(ValueError):
        day.BankAccount("Ada", -1)


def test_bank_account_histories_are_independent(day):
    first = day.BankAccount("Ada", 10.0)
    second = day.BankAccount("Grace", 10.0)
    first.deposit(1)
    assert second.history == [], "each account needs its own history list"


def test_bank_account_repr(day):
    assert repr(day.BankAccount("Ada", 100.0)) == (
        "BankAccount(owner='Ada', balance=100.0)"
    )


# --- Exercise 3: Robot ----------------------------------------------------
def test_robot_population_counts_instances(day):
    assert day.Robot.population == 0
    day.Robot("R2-D2")
    assert day.Robot.population == 1
    day.Robot("C-3PO")
    assert day.Robot.population == 2, (
        "use `Robot.population += 1`; `self.population += 1` creates an "
        "instance attribute and leaves the shared counter alone"
    )


def test_robot_introduce_uses_the_shared_species(day):
    assert day.Robot("R2-D2").introduce() == "I am R2-D2, a robot."
    assert day.Robot.species == "robot"


def test_robot_instances_have_their_own_names(day):
    r2 = day.Robot("R2-D2")
    c3 = day.Robot("C-3PO")
    assert r2.name == "R2-D2"
    assert c3.name == "C-3PO"


def test_robot_decommission_reduces_population(day):
    r2 = day.Robot("R2-D2")
    day.Robot("C-3PO")
    assert r2.decommission() == 1
    assert day.Robot.population == 1


def test_robot_population_never_goes_negative(day):
    robot = day.Robot("R2-D2")
    robot.decommission()
    assert robot.decommission() == 0


# --- Exercise 4: Temperature ---------------------------------------------
def test_temperature_stores_and_reads_celsius(day):
    temperature = day.Temperature(21.0)
    assert temperature.get_celsius() == 21.0


def test_temperature_converts_to_fahrenheit(day):
    assert day.Temperature(21.0).get_fahrenheit() == 69.8
    assert day.Temperature(100.0).get_fahrenheit() == 212.0


def test_temperature_set_celsius_validates(day):
    temperature = day.Temperature(21.0)
    temperature.set_celsius(-273.15)
    assert temperature.get_celsius() == -273.15
    with pytest.raises(ValueError):
        temperature.set_celsius(-300)
    assert temperature.get_celsius() == -273.15, "a rejected value must not be stored"


def test_temperature_constructor_validates_too(day):
    with pytest.raises(ValueError):
        day.Temperature(-300)


def test_temperature_set_fahrenheit_goes_through_the_same_check(day):
    temperature = day.Temperature(21.0)
    temperature.set_fahrenheit(212)
    assert temperature.get_celsius() == 100.0
    with pytest.raises(ValueError):
        temperature.set_fahrenheit(-500)


def test_temperature_repr(day):
    assert repr(day.Temperature(21.0)) == "Temperature(celsius=21.0)"


def test_temperature_uses_a_private_attribute(day):
    temperature = day.Temperature(21.0)
    assert hasattr(temperature, "_celsius"), (
        "store the value in a single internal attribute named _celsius"
    )


# --- Exercise 5: Book -----------------------------------------------------
def test_book_fields_and_default_tags(day):
    book = day.Book("Dune", "Herbert", 1965)
    assert book.title == "Dune"
    assert book.author == "Herbert"
    assert book.year == 1965
    assert book.tags == []


def test_book_repr_is_generated_by_dataclass(day):
    assert repr(day.Book("Dune", "Herbert", 1965)) == (
        "Book(title='Dune', author='Herbert', year=1965, tags=[])"
    )


def test_book_equality_compares_values(day):
    assert day.Book("Dune", "Herbert", 1965) == day.Book("Dune", "Herbert", 1965)
    assert day.Book("Dune", "Herbert", 1965) != day.Book("Dune", "Herbert", 1966)


def test_book_citation(day):
    assert day.Book("Dune", "Herbert", 1965).citation() == "Herbert (1965). Dune."


def test_book_add_tag_normalises_and_deduplicates(day):
    book = day.Book("Dune", "Herbert", 1965)
    book.add_tag("  SciFi ")
    book.add_tag("scifi")
    book.add_tag("   ")
    assert book.tags == ["scifi"]


def test_book_tags_are_not_shared_between_instances(day):
    first = day.Book("Dune", "Herbert", 1965)
    second = day.Book("Emma", "Austen", 1815)
    first.add_tag("classic")
    assert second.tags == [], "use field(default_factory=list)"


# --- Exercise 6: Inventory -----------------------------------------------
def test_inventory_starts_empty(day):
    stock = day.Inventory()
    assert stock.count() == 0
    assert stock.total_value() == 0.0
    assert stock.quantity_of("widget") == 0


def test_inventory_add_and_value(day):
    stock = day.Inventory()
    stock.add("widget", 2, 9.99)
    stock.add("bolt", 10, 0.5)
    assert stock.count() == 2
    assert stock.quantity_of("widget") == 2
    assert stock.total_value() == 24.98


def test_inventory_add_existing_name_accumulates(day):
    stock = day.Inventory()
    stock.add("widget", 2, 9.99)
    stock.add("widget", 1, 10.0)
    assert stock.quantity_of("widget") == 3
    assert stock.total_value() == 30.0
    assert stock.count() == 1


def test_inventory_remove_returns_remaining_and_deletes_empties(day):
    stock = day.Inventory()
    stock.add("bolt", 10, 0.5)
    assert stock.remove("bolt", 4) == 6
    assert stock.remove("bolt", 6) == 0
    assert stock.count() == 0


def test_inventory_remove_errors(day):
    stock = day.Inventory()
    stock.add("widget", 2, 9.99)
    with pytest.raises(KeyError):
        stock.remove("bolt", 1)
    with pytest.raises(ValueError):
        stock.remove("widget", 99)
    with pytest.raises(ValueError):
        stock.remove("widget", 0)
    assert stock.quantity_of("widget") == 2


def test_inventory_add_validates(day):
    stock = day.Inventory()
    with pytest.raises(ValueError):
        stock.add("widget", 0, 1.0)
    with pytest.raises(ValueError):
        stock.add("widget", 1, -1.0)


def test_inventory_repr(day):
    stock = day.Inventory()
    stock.add("widget", 3, 10.0)
    assert repr(stock) == "Inventory(1 items, total 30.00)"


# --- Exercise 7: Student -------------------------------------------------
def test_student_defaults(day):
    student = day.Student("Ada")
    assert student.name == "Ada"
    assert student.scores == []
    assert student.average() == 0.0
    assert student.best() is None
    assert student.grade() == "N/A"


def test_student_add_score_and_average(day):
    student = day.Student("Ada")
    student.add_score(90)
    student.add_score(95)
    assert student.average() == 92.5
    assert student.best() == 95
    assert student.grade() == "A"


def test_student_grade_boundaries(day):
    assert day.Student("x", [90.0]).grade() == "A"
    assert day.Student("x", [80.0]).grade() == "B"
    assert day.Student("x", [70.0]).grade() == "C"
    assert day.Student("x", [60.0]).grade() == "D"
    assert day.Student("x", [59.9]).grade() == "F"


def test_student_rejects_impossible_scores(day):
    student = day.Student("Ada")
    with pytest.raises(ValueError):
        student.add_score(101)
    with pytest.raises(ValueError):
        student.add_score(-1)
    assert student.scores == []


def test_student_equality_and_independent_score_lists(day):
    assert day.Student("Ada", [1.0]) == day.Student("Ada", [1.0])
    first, second = day.Student("Ada"), day.Student("Grace")
    first.add_score(50)
    assert second.scores == []


# --- Exercise 8: Gradebook -----------------------------------------------
def test_gradebook_starts_empty(day):
    book = day.Gradebook()
    assert book.class_average() == 0.0
    assert book.top_student() is None
    assert book.report() == "(no students)"


def test_gradebook_add_student_returns_the_student(day):
    book = day.Gradebook()
    ada = book.add_student("Ada")
    assert ada.name == "Ada"
    assert book.student("Ada") is ada
    assert book.student("nobody") is None


def test_gradebook_rejects_duplicate_names(day):
    book = day.Gradebook()
    book.add_student("Ada")
    with pytest.raises(ValueError):
        book.add_student("Ada")


def test_gradebook_record_returns_new_average(day):
    book = day.Gradebook()
    book.add_student("Ada")
    assert book.record("Ada", 90) == 90.0
    assert book.record("Ada", 100) == 95.0


def test_gradebook_record_errors(day):
    book = day.Gradebook()
    book.add_student("Ada")
    with pytest.raises(KeyError):
        book.record("nobody", 50)
    with pytest.raises(ValueError):
        book.record("Ada", 101)


def test_gradebook_class_average_and_top_student(day):
    book = day.Gradebook()
    book.add_student("Ada")
    book.add_student("Grace")
    book.record("Ada", 90)
    book.record("Ada", 100)
    book.record("Grace", 80)
    assert book.class_average() == 87.5
    top = book.top_student()
    assert top is not None and top.name == "Ada"


def test_gradebook_breaks_ties_alphabetically(day):
    book = day.Gradebook()
    book.add_student("Zoe")
    book.add_student("Ada")
    book.record("Zoe", 70)
    book.record("Ada", 70)
    top = book.top_student()
    assert top is not None and top.name == "Ada"


def test_gradebook_report_layout(day):
    book = day.Gradebook()
    book.add_student("Ada")
    book.add_student("Grace")
    book.record("Ada", 90)
    book.record("Ada", 100)
    book.record("Grace", 80)
    want = "\n".join(
        [
            "Ada         95.0  A",
            "Grace       80.0  B",
            "CLASS       87.5",
        ]
    )
    got = book.report()
    assert got == want, f"got:\n{got}\n\nwant:\n{want}"
