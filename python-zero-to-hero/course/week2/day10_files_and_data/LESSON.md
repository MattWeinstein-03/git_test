# Day 10 — Files and Data

> **Time:** ~4 hours  |  **Prerequisites:** Day 09

## What you'll be able to do after today
- Build, inspect, and join filesystem paths with `pathlib.Path`, and explain why it beats string concatenation and `os.path`.
- Read and write text files with `with open(...)`, always specifying an encoding, and explain what a context manager guarantees.
- Choose between reading a whole file and streaming it line by line, and justify the choice by memory.
- Read and write CSV with both `csv.reader`/`csv.writer` and `csv.DictReader`/`csv.DictWriter`, including the `newline=""` rule.
- Round-trip Python data through JSON with `json.dump`/`load`/`dumps`/`loads`, and state exactly which types survive the trip and which change.
- Validate incoming rows: detect missing fields, coerce types, and report bad rows instead of crashing.

## Why this matters

Until today your programs forgot everything the moment they ended. A program that cannot persist data is a toy. Files are also how programs talk to each other: your bank exports CSV, an API answers in JSON, a config file holds your settings, a log file records what happened at 3am.

This is also where beginners lose data for real. Open a file with the wrong mode and you silently erase it. Forget to close it and your writes vanish. Ignore encoding and your program works on your laptop and crashes on the server with `UnicodeDecodeError`. Trust a CSV column to be a number and your total becomes `"12" + "7" = "127"`. Today is about doing all of this correctly and defensively, because the data you receive will always be dirtier than you were promised.

---

## 1. Paths are objects, not strings: `pathlib.Path`

A path is a location in the filesystem. The naive way to build one is string concatenation, and it is wrong in three ways at once:

```python
folder = "data"
name = "sales.csv"
path = folder + "/" + name            # "data/sales.csv" — works, until it doesn't
```

Problems: you hand-code the separator (`\` on Windows), you get double slashes when `folder` already ends in one, and a string knows nothing about itself — it cannot tell you its extension, whether it exists, or what its parent folder is.

`pathlib` gives you a `Path` object that does know:

```python
from pathlib import Path

path = Path("data") / "sales.csv"       # the / operator joins path parts
print(path)                             # data/sales.csv
print(type(path))                       # <class 'pathlib.PosixPath'>
```

That `/` is the headline feature. It picks the right separator for the operating system, never doubles up, and reads like a path.

The properties you will use constantly:

```python
path = Path("/home/you/reports/sales_2024.csv")

print(path.name)        # sales_2024.csv   — file name with extension
print(path.stem)        # sales_2024       — file name without extension
print(path.suffix)      # .csv             — extension, dot included
print(path.parent)      # /home/you/reports
print(path.parts)       # ('/', 'home', 'you', 'reports', 'sales_2024.csv')
print(path.is_absolute())  # True
```

Questions and actions:

```python
path.exists()          # True/False — is there anything at this path?
path.is_file()         # True if it exists AND is a regular file
path.is_dir()          # True if it exists AND is a directory
path.stat().st_size    # size in bytes
path.mkdir(parents=True, exist_ok=True)   # create a directory (and parents), no error if present
path.unlink(missing_ok=True)              # delete a file, no error if absent
path.rename(other)     # move/rename
path.resolve()         # absolute, symlinks resolved
Path.cwd()             # current working directory
Path.home()            # your home directory
```

Reading and writing in one line, for small files:

```python
path.write_text("hello\n", encoding="utf-8")   # creates or OVERWRITES
content = path.read_text(encoding="utf-8")
```

Finding files:

```python
for csv_file in Path("data").glob("*.csv"):        # this directory only
    print(csv_file.name)

for py_file in Path("course").rglob("*.py"):       # recursive
    print(py_file)
```

### 1.1 Why prefer `pathlib` over `os.path`

You will meet the older API in every codebase written before ~2018, and it still works:

```python
import os.path
full = os.path.join("data", "sales.csv")
base = os.path.basename(full)
stem = os.path.splitext(base)[0]
if os.path.exists(full) and os.path.isfile(full):
    ...
```

versus

```python
from pathlib import Path
full = Path("data") / "sales.csv"
base = full.name
stem = full.stem
if full.is_file():
    ...
```

Concretely, `pathlib` wins because:

1. **One object, all the operations.** `os.path` is a bag of functions plus `os.remove`, `os.rename`, `os.mkdir`, `open`, `glob.glob` — five modules for one concept. `Path` gathers them as methods you can discover by typing `path.` in your editor.
2. **No stringly-typed mistakes.** `os.path.splitext(base)[0]` is a puzzle; `path.stem` is a noun.
3. **Composability.** `Path("data") / user_input / "out.csv"` handles separators for you.
4. **`is_file()` says what you mean.** `os.path.exists` is True for directories too — a real source of bugs.

Read `os.path` fluently; write `pathlib`. If a stubborn old library demands a string, pass `str(path)`.

> **Gotcha:** `Path("data/out.txt").write_text(...)` fails with `FileNotFoundError: [Errno 2] No such file or directory` if `data/` does not exist. Directories are never created implicitly. `path.parent.mkdir(parents=True, exist_ok=True)` first.

---

## 2. Opening files, and what `with` guarantees

The general-purpose tool is `open()`:

```python
with open("notes.txt", "r", encoding="utf-8") as file:
    content = file.read()
print(content)
```

Three arguments you should always think about: the path, the **mode**, and the **encoding**.

| Mode | Meaning | If the file exists | If it does not |
|---|---|---|---|
| `"r"` | read text (default) | reads it | `FileNotFoundError` |
| `"w"` | write text | **truncates it to zero bytes** | creates it |
| `"a"` | append text | writes at the end | creates it |
| `"x"` | exclusive create | `FileExistsError` | creates it |
| `"r+"` | read and write | opens at the start | `FileNotFoundError` |
| add `"b"` | binary (`"rb"`, `"wb"`) | gives you `bytes`, not `str` | — |

The `"w"` row is the one that eats homework. Opening for writing destroys the previous contents *immediately*, before you write a single byte. When you mean "add to the end", the mode is `"a"`. When a file must not be clobbered, `"x"` makes the filesystem enforce it.

### 2.1 `with` and context managers

Without `with`, you must close the file yourself:

```python
file = open("notes.txt", "w", encoding="utf-8")
file.write("hello")
file.close()               # if an exception happens above, this never runs
```

Why closing matters: writes are **buffered**. Your text sits in memory until the buffer fills or the file is closed. If the program crashes first, the file on disk is empty or truncated — you get a mysteriously half-written file. Also, every open file consumes an operating-system handle, and there is a hard limit (`OSError: Too many open files`).

`with` fixes this by using a **context manager**: an object that knows how to set something up and — crucially — how to tear it down no matter what happens.

```python
with open("notes.txt", "w", encoding="utf-8") as file:
    file.write("hello")
    raise ValueError("boom")     # the file is STILL closed properly
```

`with` is `try/finally` with the cleanup written once, inside the object, instead of at every call site:

```python
# what `with` does for you
file = open("notes.txt", "w", encoding="utf-8")
try:
    file.write("hello")
finally:
    file.close()
```

Rules of thumb:
- Any function whose docs mention "closes" or "releases" probably wants `with`.
- Keep the `with` block **short**: open, read or write, get out. Do not do your analysis inside it while the file is held open.
- Several at once: `with open(a) as src, open(b, "w") as dst:`.
- You will meet the same pattern for database connections, locks, and network sessions. Same word, same guarantee. (Writing your own context manager is Day 16 territory.)

```python
with open("notes.txt", encoding="utf-8") as file:
    print(file.closed)      # False
print(file.closed)          # True — closed on the way out, even on exceptions
```

> **Gotcha:** after the `with` block the file object is closed, and `file.read()` then raises `ValueError: I/O operation on closed file`. Copy the *data* out of the block, not the file object.

---

## 3. Encoding, and newline pitfalls

A text file on disk is bytes. An **encoding** is the agreed table that maps bytes to characters. `"café"` is 4 characters, but 5 bytes in UTF-8 (é takes two).

```python
text = "café"
print(len(text))                       # 4 characters
print(len(text.encode("utf-8")))       # 5 bytes
print(text.encode("utf-8"))            # b'caf\xc3\xa9'
```

If you write a file as UTF-8 and read it as something else, you get either mojibake or a crash:

```python
Path("x.txt").write_text("café", encoding="utf-8")
Path("x.txt").read_text(encoding="ascii")
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 3
```

The rule: **always pass `encoding="utf-8"` explicitly, for reading and writing.** If you leave it out, Python uses a platform default which is UTF-8 on modern Linux and macOS but was historically `cp1252` on Windows — the classic "works on my machine" bug. Explicit is one keyword argument; implicit is a support ticket.

When you cannot control the input and it may be dirty, you can choose a failure policy:

```python
path.read_text(encoding="utf-8", errors="strict")   # default: raise (usually right)
path.read_text(encoding="utf-8", errors="replace")  # bad bytes become U+FFFD "replacement char"
path.read_text(encoding="utf-8", errors="ignore")   # bad bytes silently dropped (lossy!)
```

Use `strict` unless you have a documented reason. `ignore` deletes data.

### 3.1 Newlines

Line endings differ by platform: `"\n"` (LF) on Linux/macOS, `"\r\n"` (CRLF) on Windows. Python's text mode hides this with **universal newlines**: on reading, `\r\n` and `\r` are translated to `\n`; on writing, `\n` is translated to `os.linesep` if the platform wants that.

```python
with open("out.txt", "w", encoding="utf-8") as file:
    file.write("a\nb\n")            # on Windows, lands on disk as a\r\nb\r\n
```

Three consequences:

1. **Reading text gives you `\n` endings whatever the source**, which is why `line.rstrip("\n")` is usually enough. Use `line.rstrip()` if you also want to drop trailing spaces, or `line.strip()` if you want both ends.
2. **`print(file.read())` shows blank lines between entries** if you `print` lines that still end with `\n` — `print` adds one of its own. Strip first, or use `end=""`.
3. **`csv` needs `newline=""`.** The `csv` module handles line endings itself; letting Python translate too produces stray blank rows on Windows. Every `open()` you hand to `csv` gets `newline=""`. Non-negotiable, and it is in the stdlib docs for exactly this reason.

```python
with open("out.csv", "w", encoding="utf-8", newline="") as file:   # <- newline=""
    ...
```

> **Gotcha:** if a text file has a "byte order mark" (Excel loves adding one), the first field name arrives as `"\ufeffid"` and your `row["id"]` raises `KeyError`. The fix is the encoding `"utf-8-sig"`, which strips the BOM.

---

## 4. Whole file vs line by line

Four ways to read, and the choice is about memory:

```python
# 1. Everything, as one string. Simple. Uses RAM equal to the file size.
with open(path, encoding="utf-8") as file:
    content = file.read()

# 2. Everything, as a list of lines (each still ending in "\n").
with open(path, encoding="utf-8") as file:
    lines = file.readlines()

# 3. One line at a time. Constant memory, whatever the file size.
with open(path, encoding="utf-8") as file:
    for line in file:                       # the file object iterates by line
        print(line.rstrip("\n"))

# 4. The one-liner for small files.
content = Path(path).read_text(encoding="utf-8")
```

Guidance:

- Config file, small CSV, JSON document (up to a few MB): read it whole. Simplicity wins.
- Log file, data export, anything unbounded or user-supplied: **iterate**. A 4 GB log file will not fit in an 8 GB laptop once Python's per-string overhead is counted, and `MemoryError` at 2am is avoidable.
- Iterating a file object is lazy: it reads a buffer at a time and hands you one line. This is the same laziness that Day 15 formalises with generators.

Counting without loading:

```python
line_count = 0
with open(path, encoding="utf-8") as file:
    for _line in file:
        line_count += 1
```

Writing is symmetric — one string, many strings, or line by line:

```python
with open(path, "w", encoding="utf-8") as file:
    file.write("first\n")                    # write does NOT add a newline for you
    file.writelines(["second\n", "third\n"])  # nor does writelines
```

> **Gotcha:** `file.write("a")` twice gives `aa`, not two lines. Unlike `print`, `write` adds nothing. Include `"\n"` yourself.

---

## 5. CSV

CSV is "comma-separated values": one line per record, fields separated by commas, an optional header row. It looks trivial, which is why people parse it with `line.split(",")` and get burned by a field that legitimately contains a comma:

```
name,note,amount
Ada,"Owes me 3, maybe 4",12.50
```

`split(",")` gives you five wrong fields. The `csv` module gets quoting, escaping, and embedded newlines right. Use it.

### 5.1 `csv.writer` and `csv.reader` (positional rows)

```python
import csv

rows = [
    ["name", "amount"],
    ["Ada", "12.50"],
    ["Grace", "7.00"],
]

with open("out.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(rows[0])       # one row
    writer.writerows(rows[1:])     # many rows

with open("out.csv", encoding="utf-8", newline="") as file:
    reader = csv.reader(file)
    header = next(reader)          # pull the header off first
    print(header)                  # ['name', 'amount']
    for row in reader:
        print(row)                 # ['Ada', '12.50'] then ['Grace', '7.00']
```

Everything read from a CSV is a **string**. There are no numbers in a CSV file, only text that looks like numbers. `row[1] * 2` gives `'12.5012.50'`. Convert deliberately: `float(row[1])`.

### 5.2 `DictReader` and `DictWriter` (fields by name)

Positional access (`row[3]`) breaks the moment someone reorders columns. Name-based access does not:

```python
with open("out.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "amount"])
    writer.writeheader()                                  # you must ask for the header
    writer.writerow({"name": "Ada", "amount": "12.50"})
    writer.writerows([{"name": "Grace", "amount": "7.00"}])

with open("out.csv", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)          # first row becomes the field names
    print(reader.fieldnames)               # ['name', 'amount']
    for row in reader:
        print(row["name"], row["amount"])  # Ada 12.50 / Grace 7.00
```

`DictReader` details that matter:
- `row` is a plain `dict` (in Python 3.8+; older versions gave an `OrderedDict`).
- A row with **fewer** fields than the header fills the missing ones with `None`.
- A row with **more** fields puts the extras in a list under the key `None` — or under `restkey` if you name one.
- Blank lines are skipped for you.

`DictWriter` details:
- `fieldnames` decides the column order; keys not listed raise `ValueError`.
- A dict missing a listed key writes an empty cell (change with `restval=`).
- Pass `extrasaction="ignore"` to tolerate extra keys instead of raising.

Other useful arguments: `delimiter="\t"` for TSV, `delimiter=";"` for European exports, `quoting=csv.QUOTE_MINIMAL` (the default) versus `csv.QUOTE_ALL`.

> **Gotcha:** `csv.DictWriter(file, fieldnames=[...])` writes no header until you call `writeheader()`. A CSV whose first row is data is a CSV whose first record gets eaten by the next `DictReader`.

---

## 6. JSON

JSON is the interchange format of the internet: nested objects and arrays, defined types, human-readable. Python's `json` module maps it onto built-in types.

Four functions, and the naming is the only thing to learn — **`s` means string**:

| Function | Direction | Works with |
|---|---|---|
| `json.dump(obj, file)` | Python -> JSON | an open file |
| `json.dumps(obj)` | Python -> JSON | a string |
| `json.load(file)` | JSON -> Python | an open file |
| `json.loads(text)` | JSON -> Python | a string |

```python
import json

data = {"name": "Ada", "scores": [90, 95], "active": True, "note": None}

text = json.dumps(data)
print(text)         # {"name": "Ada", "scores": [90, 95], "active": true, "note": null}

back = json.loads(text)
print(back == data)  # True

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2)      # indent=2 for a file humans will read

with open("data.json", encoding="utf-8") as file:
    loaded = json.load(file)
print(loaded["scores"][1])               # 95
```

Useful arguments: `indent=2` (pretty-print), `sort_keys=True` (stable output — friendlier diffs), `ensure_ascii=False` (write "café" as itself rather than `caf\u00e9`).

### 6.1 What survives a round trip

This table is the whole reason to read this section:

| Python in | JSON | Python back out |
|---|---|---|
| `dict` | object | `dict` |
| `list` | array | `list` |
| **`tuple`** | array | **`list`** — changed! |
| `str` | string | `str` |
| `int` | number | `int` |
| `float` | number | `float` |
| `True` / `False` | `true` / `false` | `True` / `False` |
| `None` | `null` | `None` |
| **`set`** | — | **`TypeError: Object of type set is not JSON serializable`** |
| **dict with int keys** | object (keys stringified) | **keys are now `str`** |

```python
original = {"tags": ("a", "b"), "counts": {1: "one"}}
round_tripped = json.loads(json.dumps(original))
print(round_tripped)          # {'tags': ['a', 'b'], 'counts': {'1': 'one'}}
print(original == round_tripped)   # False
```

So: JSON is lossy for tuples, sets, and non-string dict keys. Convert deliberately before saving (`list(my_set)`) and convert back after loading if you need the original type. Dates are not a JSON type either; store them as ISO strings like `"2024-03-14"` — which is exactly why the Day 14 project uses ISO date strings.

### 6.2 Failure modes

```python
json.loads("{oops}")
# json.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

`JSONDecodeError` is a subclass of `ValueError`, so `except ValueError:` catches it, and it carries `.lineno`, `.colno`, `.pos` to point at the damage. A truncated file (program killed mid-write) is the usual cause.

The standard "load, tolerating a missing or corrupt file" shape:

```python
def load_data(path: Path) -> dict:
    """Return saved data, or an empty dict when there is nothing usable."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}                    # first run: perfectly normal
    except json.JSONDecodeError as error:
        print(f"{path} is corrupt ({error}); starting fresh")
        return {}
```

JSON is also strict in ways people trip over: no trailing commas, no comments, keys must be double-quoted strings, `NaN`/`Infinity` are Python extensions that other languages will reject.

> **Gotcha:** `json.dump(data, path)` — passing a *path* instead of an open *file* — fails with `AttributeError: 'PosixPath' object has no attribute 'write'`. `dump` needs a file object; `dumps` gives you a string you can `path.write_text(...)`.

---

## 7. Data hygiene

Every real data file is dirty. Your job is to decide *at the boundary* what "valid" means, and to keep bad records out of your calculations. Three principles:

**1. Validate at the edge, once.** Convert and check as data enters the program, then trust it internally. Sprinkling `if value is None` through your maths is how a codebase rots.

**2. Never crash on one bad row.** A 50,000-row import that dies at row 3 is worthless. Skip the row, record *why*, and report a summary.

**3. Report, do not swallow.** "Imported 4,998 rows, skipped 2: row 17 missing 'amount', row 402 amount 'n/a' is not a number" is professional. Silently importing 4,998 rows is a data-corruption incident.

The shape that does all three:

```python
def clean(rows: list[dict], required: list[str]) -> tuple[list[dict], list[str]]:
    """Return (good rows, problem messages). Never raises."""
    good: list[dict] = []
    problems: list[str] = []

    for index, row in enumerate(rows):
        number = index + 1                       # humans count from 1

        missing = []
        for field in required:
            value = row.get(field)
            if value is None or str(value).strip() == "":
                missing.append(field)
        if missing:
            problems.append(f"row {number}: missing {', '.join(missing)}")
            continue                             # skip, keep going

        try:
            amount = float(row["amount"])
        except ValueError:
            problems.append(f"row {number}: amount {row['amount']!r} is not a number")
            continue

        if amount <= 0:
            problems.append(f"row {number}: amount must be positive, got {amount}")
            continue

        good.append({"name": row["name"].strip(), "amount": amount})

    return good, problems
```

The specific checks worth having in your reflexes:

| Problem | Check |
|---|---|
| Missing column | `row.get(field) is None` |
| Present but empty | `str(value).strip() == ""` |
| Whitespace round values | `value.strip()` before comparing or storing |
| Number as text | `try: float(value) except ValueError` |
| Out-of-range number | explicit `if amount <= 0` after conversion |
| Inconsistent case | `value.strip().lower()` for categories and keys |
| Duplicate identity | keep a `set` of seen ids |
| Extra unexpected column | `DictReader`'s `restkey`, or ignore it |
| Excel BOM on the first header | `encoding="utf-8-sig"` |

One more habit: **write to a temporary file, then replace.** If your program dies halfway through writing `data.json`, you have destroyed the old copy and not finished the new one.

```python
temp = path.with_suffix(".json.tmp")
temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
temp.replace(path)          # atomic on the same filesystem: either old or new, never half
```

> **Gotcha:** in this course, every exercise writes only into a pytest `tmp_path` or a `tmp/` folder. Real habit, same reason: a program that scatters files into whatever directory it happened to be launched from is a program nobody wants to run.

---

## Common mistakes

| Mistake | What you'll see | Fix |
|---|---|---|
| `open(path, "w")` when you meant append | The file is empty; old data gone | Use `"a"`, or `"x"` to refuse to overwrite |
| No `with`, no `close()` | File on disk is empty or truncated | Always `with open(...) as file:` |
| Using the file object after the block | `ValueError: I/O operation on closed file` | Copy the data out inside the block |
| Omitting `encoding` | `UnicodeDecodeError` on another machine | `encoding="utf-8"` every time |
| Missing `newline=""` for csv | Blank row between every record on Windows | `open(..., newline="")` for csv |
| Writing into a directory that does not exist | `FileNotFoundError` on write | `path.parent.mkdir(parents=True, exist_ok=True)` |
| Treating CSV fields as numbers | `'12' * 2` -> `'1212'`; `TypeError` on `+` | Convert explicitly with `int()`/`float()` |
| Forgetting `writeheader()` | First record read back as the header | Call `writeheader()` after creating `DictWriter` |
| `json.dump(data, path)` | `AttributeError: ... has no attribute 'write'` | Pass an open file, or use `dumps` + `write_text` |
| Expecting tuples/sets back from JSON | Tuples come back as lists; sets raise `TypeError` | Convert before dumping and after loading |
| Assuming a file exists | `FileNotFoundError` on first run | `except FileNotFoundError:` and return a default |
| Crashing the import on one bad row | 49,999 good rows lost | Skip, collect messages, report a summary |
| `path.unlink()` on a missing file | `FileNotFoundError` | `path.unlink(missing_ok=True)` |

---

## Mental model

A file is a **filing cabinet drawer** in a building you do not own.

```
   Path("data/sales.csv")        the LABEL on the drawer.
                                 Cheap to hold, means nothing on its own.
                                 A Path is not a file; it is an address.

   with open(path) as file:      you OPEN the drawer and the building's
       ...                       keeper hands you a handle. Limited number
                                 available. `with` promises you give it back
                                 even if you faint (an exception).

   encoding="utf-8"              the LANGUAGE the papers are written in.
                                 Guess wrong and you read gibberish.

   mode="w" / "a" / "x"          what you intend to do:
                                   "w" shred everything first
                                   "a" add to the back
                                   "x" refuse if the drawer is occupied

   csv / json                    the FORM the papers are laid out in.
                                 csv = one row per line, everything text.
                                 json = nested boxes with typed contents.

   validation at the boundary    the CLERK at the drawer who rejects
                                 unreadable forms and writes down why,
                                 instead of letting them into the ledger.
```

Two sentences to keep: *a `Path` is an address, an open file is a borrowed resource, and `with` is the promise to return it.* And: *everything that comes out of a CSV is a string; everything that goes into JSON must be a JSON type.*

---

## Practice

1. Run the demo. It creates a `tmp/` folder next to itself, writes into it, prints what it did, and deletes it again:

   ```bash
   python course/week2/day10_files_and_data/examples.py
   ```

   Read the output next to the code. Note the sections on encoding and on the JSON round trip particularly — those two print things people find surprising.

2. Open `exercises.py`. Every function takes the path it should work on, so nothing is hard-coded. **Write only into paths you are given** — the tests pass in pytest's `tmp_path`, a fresh empty directory per test, which is why they never pollute the repository. Adopt the habit.

3. Grade from the course root:

   ```bash
   python check.py day10
   python check.py day10 -v
   ```

4. Then do this by hand, because file bugs are muscle memory: create `tmp/scratch.txt`, write to it with mode `"w"` twice, and confirm the first content is gone. Then do it with `"a"`. Then open it with `encoding="ascii"` after writing a `£` sign and read the exact exception text.

---

## Recall check

1. Why is `Path("data") / "sales.csv"` better than `"data" + "/" + "sales.csv"`?
2. What exactly does `with` guarantee, and what goes wrong without it?
3. What happens to an existing file when you `open(path, "w")` — and when does it happen?
4. Why should you pass `encoding="utf-8"` explicitly even though it usually works without?
5. When must you read a file line by line rather than all at once, and why?
6. Why does every `open()` handed to the `csv` module need `newline=""`?
7. Which Python types do not survive a JSON round trip, and what do they become?
8. A CSV import hits a row with an empty `amount`. What should your code do, and what should it definitely not do?

<details>
<summary>Answers</summary>

1. `Path` picks the correct separator for the platform, never produces doubled slashes, and the result is an object that knows its own `.name`, `.stem`, `.suffix`, `.parent`, and whether it exists — a string knows none of that.
2. `with` guarantees the resource is released (the file closed) when the block exits, whether it exits normally, via `return`, or via an exception. Without it, a crash before `close()` leaves buffered writes unflushed (an empty or truncated file) and leaks an OS file handle.
3. It is truncated to zero bytes — immediately, at `open()`, before you write anything. Use `"a"` to append or `"x"` to fail rather than overwrite.
4. Because the default depends on the machine's locale: UTF-8 on modern Linux/macOS, historically `cp1252` on Windows. Being explicit makes the program behave identically everywhere, instead of failing with `UnicodeDecodeError` on someone else's computer.
5. When the file could be large or is not under your control. Reading whole costs RAM equal to the file's size (plus overhead); iterating uses a constant, small amount whatever the size.
6. The `csv` module manages line endings itself. Leaving Python's universal-newline translation on as well produces an extra blank row between records on Windows.
7. `tuple` comes back as `list`; `set` cannot be serialised at all (`TypeError`); non-string dict keys (e.g. ints) come back as strings. Dates have no JSON type — store them as ISO strings.
8. Skip that row, record a specific message naming the row number and the problem, keep processing the rest, and report a summary at the end (`imported N, skipped M: ...`). It must not crash the whole import, and it must not silently drop the row without telling anyone.

</details>
