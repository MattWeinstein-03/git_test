"""Day 14 graded checks — Project 2: Expense Tracker.

Tests are named test_m1_* … test_m5_* so partial credit is visible: finish
milestone 1 and the M1 checks go green while the rest still fail.

Every file operation uses pytest's `tmp_path`, so nothing is written into the
repository.
"""

import json

import pytest


def make_store(day, rows=None):
    """Helper: a store holding (amount, category, date) triples."""
    if rows is None:
        rows = [
            (12.5, "food", "2024-03-01"),
            (30.0, "transport", "2024-03-02"),
            (7.5, "food", "2024-04-05"),
        ]
    store = day.ExpenseStore()
    for amount, category, date in rows:
        store.add(day.Expense(amount, category, date))
    return store


# ===========================================================================
# M1 — the Expense dataclass
# ===========================================================================
def test_m1_expense_stores_and_normalises_fields(day):
    expense = day.Expense(12.5, "  Food ", "2024-03-01")
    assert expense.amount == 12.5
    assert expense.category == "food", "category is stripped and lowercased"
    assert expense.date == "2024-03-01"
    assert expense.note == ""


def test_m1_expense_note_is_optional_and_stripped(day):
    expense = day.Expense(1.0, "food", "2024-03-01", "  lunch  ")
    assert expense.note == "lunch"


def test_m1_expense_amount_becomes_a_float(day):
    expense = day.Expense(12, "food", "2024-03-01")
    assert isinstance(expense.amount, float)
    assert expense.amount == 12.0


def test_m1_expense_repr_is_dataclass_generated(day):
    got = repr(day.Expense(12.5, "food", "2024-03-01"))
    assert got == (
        "Expense(amount=12.5, category='food', date='2024-03-01', note='')"
    ), f"got {got!r} — is this a @dataclass?"


def test_m1_expense_equality_compares_values(day):
    assert day.Expense(1.0, "food", "2024-03-01") == day.Expense(
        1.0, "food", "2024-03-01"
    )
    assert day.Expense(1.0, "food", "2024-03-01") != day.Expense(
        2.0, "food", "2024-03-01"
    )


def test_m1_expense_rejects_bad_amounts(day):
    with pytest.raises(day.ValidationError, match="must be positive"):
        day.Expense(-5, "food", "2024-03-01")
    with pytest.raises(day.ValidationError, match="must be positive"):
        day.Expense(0, "food", "2024-03-01")


def test_m1_expense_rejects_non_numeric_amounts(day):
    with pytest.raises(day.ValidationError, match="must be a number, got str"):
        day.Expense("12", "food", "2024-03-01")
    with pytest.raises(day.ValidationError, match="must be a number, got bool"):
        day.Expense(True, "food", "2024-03-01")


def test_m1_expense_rejects_empty_category(day):
    with pytest.raises(day.ValidationError, match="category must not be empty"):
        day.Expense(5, "   ", "2024-03-01")


def test_m1_expense_rejects_bad_dates(day):
    for bad_date in ("1 March 2024", "2024-13-01", "24-3-1", "2024-03-32", ""):
        with pytest.raises(day.ValidationError, match="date must be YYYY-MM-DD"):
            day.Expense(5, "food", bad_date)


def test_m1_expense_month_property(day):
    expense = day.Expense(5, "food", "2024-03-01")
    assert expense.month == "2024-03"


def test_m1_expense_to_dict_is_json_ready(day):
    expense = day.Expense(12.5, "food", "2024-03-01", "lunch")
    data = expense.to_dict()
    assert data == {
        "amount": 12.5,
        "category": "food",
        "date": "2024-03-01",
        "note": "lunch",
    }
    json.dumps(data)  # must not raise


def test_m1_expense_from_dict_round_trips(day):
    expense = day.Expense(12.5, "food", "2024-03-01", "lunch")
    assert day.Expense.from_dict(expense.to_dict()) == expense


def test_m1_expense_from_dict_defaults_the_note(day):
    expense = day.Expense.from_dict(
        {"amount": 1.0, "category": "food", "date": "2024-03-01"}
    )
    assert expense.note == ""


def test_m1_expense_from_dict_reports_missing_fields(day):
    with pytest.raises(day.ValidationError, match="missing field: category"):
        day.Expense.from_dict({"amount": 5})
    with pytest.raises(day.ValidationError, match="missing field: amount"):
        day.Expense.from_dict({"category": "food", "date": "2024-03-01"})


# ===========================================================================
# M2 — the ExpenseStore container
# ===========================================================================
def test_m2_store_starts_empty(day):
    store = day.ExpenseStore()
    assert len(store) == 0
    assert store.all() == []
    assert bool(store) is False


def test_m2_store_add_and_len(day):
    store = day.ExpenseStore()
    store.add(day.Expense(12.5, "food", "2024-03-01"))
    store.add(day.Expense(30.0, "transport", "2024-03-02"))
    assert len(store) == 2
    assert store.all()[0].category == "food"


def test_m2_store_add_rejects_non_expenses(day):
    store = day.ExpenseStore()
    with pytest.raises(TypeError):
        store.add({"amount": 1.0})
    assert len(store) == 0, "a rejected value must not be stored"


def test_m2_store_remove_returns_the_expense(day):
    store = make_store(day)
    removed = store.remove(0)
    assert removed.category == "food"
    assert len(store) == 2


def test_m2_store_remove_bad_index(day):
    store = day.ExpenseStore()
    with pytest.raises(IndexError):
        store.remove(0)


def test_m2_store_all_returns_a_copy(day):
    store = make_store(day)
    stolen = store.all()
    stolen.clear()
    assert len(store) == 3, "all() must return a copy of the list"


def test_m2_store_copies_the_list_it_is_given(day):
    expenses = [day.Expense(1.0, "food", "2024-03-01")]
    store = day.ExpenseStore(expenses)
    expenses.append(day.Expense(2.0, "food", "2024-03-02"))
    assert len(store) == 1, "copy the list passed to __init__"


def test_m2_store_is_iterable(day):
    store = make_store(day)
    categories = []
    for expense in store:
        categories.append(expense.category)
    assert categories == ["food", "transport", "food"]


# ===========================================================================
# M3 — JSON persistence
# ===========================================================================
def test_m3_save_writes_a_json_array(day, tmp_path):
    store = make_store(day)
    path = tmp_path / "expenses.json"
    assert store.save(path) == 3
    records = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(records, list)
    assert records[0] == {
        "amount": 12.5,
        "category": "food",
        "date": "2024-03-01",
        "note": "",
    }


def test_m3_save_creates_missing_directories(day, tmp_path):
    store = make_store(day)
    path = tmp_path / "nested" / "deeper" / "expenses.json"
    assert store.save(path) == 3
    assert path.is_file()


def test_m3_round_trip_is_lossless(day, tmp_path):
    store = make_store(day)
    path = tmp_path / "expenses.json"
    store.save(path)
    reloaded = day.ExpenseStore.load(path)
    assert len(reloaded) == 3
    assert reloaded.all() == store.all()


def test_m3_load_tolerates_a_missing_file(day, tmp_path):
    store = day.ExpenseStore.load(tmp_path / "never_written.json")
    assert len(store) == 0


def test_m3_load_rejects_corrupt_json(day, tmp_path):
    path = tmp_path / "half.json"
    path.write_text('[{"amount": 1.0, ', encoding="utf-8")
    with pytest.raises(day.ValidationError, match="not valid JSON"):
        day.ExpenseStore.load(path)


def test_m3_load_rejects_json_that_is_not_a_list(day, tmp_path):
    path = tmp_path / "object.json"
    path.write_text('{"amount": 1.0}', encoding="utf-8")
    with pytest.raises(day.ValidationError, match="must contain a list"):
        day.ExpenseStore.load(path)


def test_m3_load_rejects_invalid_records(day, tmp_path):
    path = tmp_path / "bad_record.json"
    path.write_text(
        '[{"amount": -1.0, "category": "food", "date": "2024-03-01"}]',
        encoding="utf-8",
    )
    with pytest.raises(day.ValidationError):
        day.ExpenseStore.load(path)


def test_m3_save_then_load_empty_store(day, tmp_path):
    path = tmp_path / "expenses.json"
    assert day.ExpenseStore().save(path) == 0
    assert len(day.ExpenseStore.load(path)) == 0


# ===========================================================================
# M4 — reporting
# ===========================================================================
def test_m4_total(day):
    assert make_store(day).total() == 50.0
    assert day.ExpenseStore().total() == 0.0


def test_m4_total_by_category(day):
    got = make_store(day).total_by_category()
    assert got == {"food": 20.0, "transport": 30.0}
    assert list(got) == ["food", "transport"], "keys must be in alphabetical order"


def test_m4_total_by_category_empty(day):
    assert day.ExpenseStore().total_by_category() == {}


def test_m4_top_categories(day):
    store = make_store(day)
    assert store.top_categories(1) == [("transport", 30.0)]
    assert store.top_categories(2) == [("transport", 30.0), ("food", 20.0)]
    assert store.top_categories(9) == [("transport", 30.0), ("food", 20.0)]
    assert store.top_categories(0) == []
    assert store.top_categories(-1) == []


def test_m4_top_categories_breaks_ties_alphabetically(day):
    store = make_store(
        day,
        [
            (10.0, "zebra", "2024-03-01"),
            (10.0, "apple", "2024-03-02"),
        ],
    )
    assert store.top_categories(2) == [("apple", 10.0), ("zebra", 10.0)]


def test_m4_monthly_totals(day):
    got = make_store(day).monthly_totals()
    assert got == {"2024-03": 42.5, "2024-04": 7.5}
    assert list(got) == ["2024-03", "2024-04"], "keys must be in chronological order"


def test_m4_reports_agree_with_each_other(day):
    store = make_store(day)
    assert store.total() == round(sum(store.total_by_category().values()), 2)
    assert store.total() == round(sum(store.monthly_totals().values()), 2)


def test_m4_totals_are_rounded_to_two_places(day):
    store = make_store(
        day,
        [
            (0.1, "food", "2024-03-01"),
            (0.2, "food", "2024-03-02"),
        ],
    )
    assert store.total() == 0.3
    assert store.total_by_category() == {"food": 0.3}


# ===========================================================================
# M5 — CSV import
# ===========================================================================
GOOD_CSV = "amount,category,date,note\n12.50,food,2024-03-01,lunch\n30,transport,2024-03-02,\n"

DIRTY_CSV = (
    "amount,category,date,note\n"
    "12.50,food,2024-03-01,lunch\n"  # ok
    ",food,2024-03-02,\n"  # missing amount
    "abc,food,2024-03-03,\n"  # amount not a number
    "10,,2024-03-04,\n"  # missing category
    "10,food,1 March 2024,\n"  # bad date shape
    "-4,food,2024-03-05,\n"  # not positive
    "7.50,  Food ,2024-04-05,dinner\n"  # ok, and needs normalising
)


def test_m5_import_csv_adds_good_rows(day, tmp_path):
    path = tmp_path / "import.csv"
    path.write_text(GOOD_CSV, encoding="utf-8")
    store = day.ExpenseStore()
    added, problems = store.import_csv(path)
    assert added == 2
    assert problems == []
    assert len(store) == 2
    assert store.all()[0].note == "lunch"


def test_m5_import_csv_skips_and_reports_bad_rows(day, tmp_path):
    path = tmp_path / "dirty.csv"
    path.write_text(DIRTY_CSV, encoding="utf-8")
    store = day.ExpenseStore()
    added, problems = store.import_csv(path)

    assert added == 2, f"rows 1 and 7 are usable; got {added}"
    assert len(problems) == 5, f"expected 5 problems, got {problems!r}"
    assert problems[0].startswith("row 2: missing amount"), f"got {problems[0]!r}"
    assert problems[1].startswith("row 3: "), f"got {problems[1]!r}"
    assert problems[2].startswith("row 4: missing category"), f"got {problems[2]!r}"
    assert "date must be YYYY-MM-DD" in problems[3], f"got {problems[3]!r}"
    assert "must be positive" in problems[4], f"got {problems[4]!r}"


def test_m5_import_csv_normalises_imported_rows(day, tmp_path):
    path = tmp_path / "dirty.csv"
    path.write_text(DIRTY_CSV, encoding="utf-8")
    store = day.ExpenseStore()
    store.import_csv(path)
    assert store.all()[1].category == "food"
    assert store.all()[1].amount == 7.5


def test_m5_import_csv_keeps_existing_expenses(day, tmp_path):
    path = tmp_path / "import.csv"
    path.write_text(GOOD_CSV, encoding="utf-8")
    store = make_store(day)
    added, _problems = store.import_csv(path)
    assert added == 2
    assert len(store) == 5


def test_m5_import_csv_header_only(day, tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("amount,category,date\n", encoding="utf-8")
    store = day.ExpenseStore()
    assert store.import_csv(path) == (0, [])


def test_m5_import_csv_missing_file_raises(day, tmp_path):
    store = day.ExpenseStore()
    with pytest.raises(FileNotFoundError):
        store.import_csv(tmp_path / "nope.csv")


def test_m5_import_then_save_and_reload(day, tmp_path):
    csv_path = tmp_path / "dirty.csv"
    csv_path.write_text(DIRTY_CSV, encoding="utf-8")
    json_path = tmp_path / "expenses.json"

    store = day.ExpenseStore()
    store.import_csv(csv_path)
    store.save(json_path)
    reloaded = day.ExpenseStore.load(json_path)
    assert reloaded.all() == store.all()
    assert reloaded.total() == 20.0


# ===========================================================================
# The menu
# ===========================================================================
def test_main_prints_the_menu_and_quits(day, monkeypatch, capsys):
    answers = iter(["q"])

    def fake_input(prompt: str = "") -> str:
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    assert day.main(day.ExpenseStore()) == 0
    printed = capsys.readouterr().out
    assert "Expense Tracker" in printed
    assert "quit" in printed


def test_main_lists_expenses_then_quits(day, monkeypatch, capsys):
    answers = iter(["2", "q"])

    def fake_input(prompt: str = "") -> str:
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    assert day.main(make_store(day)) == 0
    printed = capsys.readouterr().out
    assert "transport" in printed


def test_main_reports_unknown_choices(day, monkeypatch, capsys):
    answers = iter(["zzz", "q"])

    def fake_input(prompt: str = "") -> str:
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    day.main(day.ExpenseStore())
    assert "unknown choice: zzz" in capsys.readouterr().out


def test_main_saves_to_the_path_it_is_given(day, monkeypatch, capsys, tmp_path):
    answers = iter(["4", "q"])

    def fake_input(prompt: str = "") -> str:
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    path = tmp_path / "expenses.json"
    day.main(make_store(day), path)
    capsys.readouterr()
    assert json.loads(path.read_text(encoding="utf-8"))[0]["category"] == "food"


def test_main_survives_a_closed_input_stream(day, monkeypatch, capsys):
    def fake_input(prompt: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)
    assert day.main(day.ExpenseStore()) == 0, (
        "EOFError must end the loop cleanly, not raise"
    )
