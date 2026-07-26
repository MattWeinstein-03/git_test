# Setup

Goal: a terminal where `python --version` (or `python3 --version`) prints 3.10 or
newer, and `python -m pytest --version` prints a version instead of an error. That
is the entire requirement for Days 1-18. Budget 20-40 minutes if you have never
installed a developer tool. Nothing here is hard; it is just unfamiliar.

Two words you need before you start:

- **Terminal** (also: shell, command line, console): a program where you type
  commands and read text output. On macOS it is Terminal.app. On Windows it is
  PowerShell or Windows Terminal. On Linux it is GNOME Terminal, Konsole, or
  whatever your distribution ships.
- **Prompt**: the text the terminal shows before your cursor, like `$` or `PS>`.
  In this document, code blocks show the command only. Do not type the `$`.

---

## 1. Check whether you already have Python

Most machines already have some Python. Open a terminal and run:

```bash
python3 --version
```

Expected: something like `Python 3.11.9`. If the number after `3.` is 10 or higher,
you are done with this step — skip to [step 3](#3-install-pytest).

If you see `Python 3.9.x` or lower, you need a newer one. This course uses syntax
introduced in 3.10 (notably `list[int]` style type hints and `X | Y` unions), and
`check.py doctor` will refuse to pass you.

If you see `command not found`, `not recognized`, or Windows opens the Microsoft
Store, you do not have a usable Python on your PATH. Go to step 2.

Try all three names before concluding you have nothing:

```bash
python3 --version
python --version
py --version
```

---

## 2. Install Python

### macOS

macOS ships an old, Apple-managed Python you should not use for development.
Install your own.

Option A, the installer (simplest):

1. Go to <https://www.python.org/downloads/macos/>.
2. Download the latest **macOS 64-bit universal2 installer** for Python 3.12 or
   3.11.
3. Run it and accept the defaults.
4. Close and reopen your terminal, then run `python3 --version`.

Option B, Homebrew (if you already have it):

```bash
brew install python@3.12
python3 --version
```

Reopening the terminal matters: the installer edits your shell configuration, and
an already-open terminal will not see the change.

### Windows

Option A, the installer:

1. Go to <https://www.python.org/downloads/windows/>.
2. Download the latest **Windows installer (64-bit)**.
3. Run it. On the first screen, tick **"Add python.exe to PATH"** before clicking
   Install. This is the single most important checkbox in this document. If you
   miss it, you will get `'python' is not recognized...` and have to re-run the
   installer and choose Modify.
4. Choose "Install Now".
5. Open a **new** PowerShell window and run `py --version`.

Option B, winget:

```powershell
winget install Python.Python.3.12
```

On Windows, `py` (the Python launcher) is the most reliable way to invoke Python,
because it works regardless of PATH ordering. Use `py` in place of `python` in
every command in this course if `python` misbehaves.

If typing `python` opens the Microsoft Store, Windows is showing you a stub
because no real Python is on your PATH. Install properly with the option above,
or disable the stub under Settings > Apps > Advanced app settings > App execution
aliases by turning off the `python.exe` and `python3.exe` entries.

### Linux

Debian, Ubuntu, and derivatives:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

`python3-venv` is a separate package on Debian-family systems and you will need it
for virtual environments. Installing it now saves you a confusing error later.

Fedora, RHEL:

```bash
sudo dnf install python3 python3-pip
```

Arch:

```bash
sudo pacman -S python python-pip
```

If your distribution's Python is older than 3.10, install a newer one with
[pyenv](https://github.com/pyenv/pyenv) rather than replacing the system Python —
your operating system depends on its own copy.

---

## `python` vs `python3` vs `py`

This trips up everyone. There is no single correct name; it depends on your
platform and how Python was installed.

| Command | Where it usually works | Notes |
|---|---|---|
| `python3` | macOS, Linux | Always Python 3. The safest name on Unix-like systems. |
| `python` | Windows, and inside an activated virtualenv anywhere | On old Linux systems it might be Python 2, which will fail loudly. |
| `py` | Windows only | The Python launcher. Finds your installs regardless of PATH. Use `py -3.12` to pick a version. |

Practical rule:

- Figure out once which of the three prints 3.10+, and use that name for
  everything.
- Once you create and activate a virtualenv (below), `python` works everywhere and
  the confusion disappears. That is one of the reasons to use one.
- When installing packages, always use `python -m pip install X` rather than bare
  `pip install X`. The `-m` form guarantees the package lands in the same Python
  that will run your code. Bare `pip` may belong to a different installation.

The course documentation writes `python`. If that does not work for you, mentally
substitute `python3` or `py`.

---

## PATH problems, and how to recognise them

PATH is a list of folders your terminal searches when you type a command name. If
Python is installed but its folder is not on PATH, the terminal reports that the
command does not exist — the file is there, but nobody looked in that folder.

Symptoms that mean "PATH problem":

- `python: command not found` / `'python' is not recognized as an internal or
  external command`
- `pip: command not found` even though Python works
- Typing `python` on Windows opens the Microsoft Store
- `python --version` shows an older version than the one you just installed

Diagnose which Python you are actually running:

```bash
# macOS / Linux
which -a python3 python
python3 -c "import sys; print(sys.executable)"

# Windows PowerShell
where.exe python
py -c "import sys; print(sys.executable)"
```

`sys.executable` is the ground truth: it prints the full path of the interpreter
that just ran. If it is not the Python you expected, you have found your bug.

Fixes:

- **Windows:** re-run the installer, choose Modify, tick "Add python.exe to PATH".
  Or just use `py` and stop worrying about it.
- **macOS/Linux:** the python.org installer and Homebrew both add the right folder
  to your shell profile (`~/.zshrc` on modern macOS, `~/.bashrc` on most Linux).
  If it did not take effect, close and reopen the terminal. A new terminal reads
  the profile; the old one does not.
- **Any platform:** use a virtualenv. Activating one puts the correct interpreter
  first on PATH for that terminal session, which sidesteps the whole problem.

---

## 3. Install pytest

Every day of this course is graded by pytest. Install it:

```bash
python -m pip install pytest
```

Verify:

```bash
python -m pytest --version
```

If pip itself is missing (`No module named pip`), install it with
`python -m ensurepip --upgrade`, or on Debian/Ubuntu with
`sudo apt install python3-pip`.

If you get a `permission denied` error, do **not** reach for `sudo`. Either use a
virtualenv (next section) or add `--user`:

```bash
python -m pip install --user pytest
```

If pip refuses with `error: externally-managed-environment` — common on recent
Debian, Ubuntu and Homebrew installs — that is your operating system telling you
to use a virtualenv. Do that; it is the right answer anyway.

---

## 4. Virtual environments

A virtualenv is a private folder holding its own copy of Python and its own
installed packages. Two projects can then depend on different versions of the same
library without fighting. Day 11 covers the concept properly; this section is just
the mechanics so you can create one now.

Create it once, from the course root (the folder containing `check.py`):

```bash
# macOS / Linux
python3 -m venv .venv

# Windows
py -m venv .venv
```

That makes a `.venv/` folder. It is disposable — if it ever gets into a weird
state, delete the folder and make a new one. It is already in `.gitignore`.

Activate it. You must do this in every new terminal session:

| Shell / OS | Activate command |
|---|---|
| macOS / Linux (bash, zsh) | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd.exe | `.venv\Scripts\activate.bat` |
| Git Bash on Windows | `source .venv/Scripts/activate` |
| fish | `source .venv/bin/activate.fish` |

When it is active your prompt gets a `(.venv)` prefix, `python` means the venv's
Python, and `python -m pip install` installs into the venv. Confirm with:

```bash
python -c "import sys; print(sys.prefix != sys.base_prefix)"   # prints True
```

Then install the dependency:

```bash
python -m pip install pytest
```

Deactivate with `deactivate` when you are finished.

If PowerShell refuses with `cannot be loaded because running scripts is disabled
on this system`, allow local scripts for your user once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then activate again.

A virtualenv is optional for this course — `check.py doctor` only warns about it —
but recommended. It makes `python` and `pip` unambiguous, which removes an entire
category of beginner confusion.

---

## 5. Verify the whole setup

From the course root:

```bash
python check.py doctor
```

You want output along these lines:

```
  Setup check
  ok   Python 3.11.9
  ok   pytest 8.3.2
  ok   found all 21 day folders
  ok   virtualenv active: True

  You're ready. Start with course/week1/day01_*/LESSON.md
```

Two expected imperfections:

- `warn   virtualenv active: False` is fine. It is a warning, not a failure, and
  `doctor` still exits 0.
- `bad  found N day folders, expected 21` while the course content is still being
  written. `doctor` will exit 1. Ignore it; nothing is wrong with your setup.
- If `course/` does not exist at all yet, every `check.py` command prints
  `No day folders found under .../course. Is the course installed?` and exits 1.
  Same story: not your setup.

---

## 6. Choosing an editor

You need something that shows you line numbers, keeps indentation consistent, and
highlights Python syntax. Any of these is fine. Do not spend an hour on this
decision; you can switch later.

- **VS Code** — <https://code.visualstudio.com/>. The default choice. Install the
  Microsoft "Python" extension, then use the command palette
  (`Ctrl/Cmd+Shift+P`) > "Python: Select Interpreter" and pick your `.venv`. It
  has an integrated terminal, so you can edit and run in one window.
- **PyCharm Community Edition** — heavier, more opinionated, excellent debugger
  and refactoring tools. Free.
- **A browser-based environment** — if you are working in one already, you have an
  editor and a terminal, and steps 1-5 are all you need.
- **Vim / Neovim / Emacs** — fine if you already know one. Do not learn a modal
  editor and Python in the same three weeks.

Two settings worth turning on whatever you pick:

- Insert spaces instead of tabs, 4 spaces per indent. Python cares about
  indentation, and mixing tabs with spaces produces `TabError`.
- Show whitespace or at least the indent guides.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `python: command not found` | Python not installed, or not on PATH | Try `python3` and `py`. If none work, install (step 2). On Windows, re-run the installer with "Add python.exe to PATH" ticked. |
| `'python' is not recognized as an internal or external command` | Windows PATH does not include Python | Use `py` instead, or re-run the installer and choose Modify > Add to PATH. |
| Typing `python` opens the Microsoft Store | Windows app-execution-alias stub, no real Python installed | Install Python properly, or disable the alias in Settings > Apps > Advanced app settings > App execution aliases. |
| `ModuleNotFoundError: No module named 'pytest'` | pytest installed into a different Python than the one running | Run `python -m pip install pytest` with the *same* command name you use to run code. If a venv is active, install inside it. |
| `ModuleNotFoundError` for something you definitely installed | You installed it before activating the venv, or into another interpreter | Activate the venv, then `python -m pip install X`. Compare `python -c "import sys; print(sys.executable)"` with `python -m pip -V`. |
| `pip: command not found` but `python` works | pip's script folder is not on PATH | Always use `python -m pip ...` instead of bare `pip`. |
| `No module named pip` | pip missing from that install | `python -m ensurepip --upgrade`, or `sudo apt install python3-pip`. |
| `permission denied` during `pip install` | Installing into a system folder your user cannot write | Use a venv, or `python -m pip install --user X`. Do not use `sudo pip`. |
| `error: externally-managed-environment` | Distro-managed Python blocking global installs | Create and activate a venv (step 4), then install there. |
| `Python 3.9.x` when you installed 3.12 | An older Python is earlier on PATH | Check `python3 -c "import sys; print(sys.executable)"`. Use the full path, use `py -3.12` on Windows, or create the venv from the newer interpreter. |
| `cannot be loaded because running scripts is disabled` (PowerShell) | Execution policy blocks the activate script | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then activate again. |
| `source: not found` when activating | Running the bash activate script in cmd.exe, or the wrong path | Use the row for your exact shell in the activation table above. |
| `The system cannot find the path specified` after activating | `.venv` was created by a Python that has since moved or been uninstalled | Delete `.venv` and recreate it. |
| `python check.py doctor` prints `No day folders found ...` | `course/` is missing or empty | Expected while content is being written. Not a setup problem. |
| `bad  found 7 day folders, expected 21` | Only part of the course content is present | Expected during authoring. Not a setup problem. |
| `check.py` runs but every day says `No tests ran.` | `test_exercises.py` not present in that day folder yet | Expected during authoring. Confirm with `ls course/week1/day01_getting_started`. |
| `TabError: inconsistent use of tabs and spaces in indentation` | Editor inserted a tab into space-indented code | Set the editor to spaces-only, 4 per indent, and retype the offending line. |
| `SyntaxError` on a line that looks fine | The real problem is usually the line *above* (unclosed bracket or quote) | Check the previous line for a missing `)`, `]`, `}` or quote. See reference/error_messages.md. |
| `No such file or directory: 'data.txt'` | You are running from a different folder than you think | `pwd` (or `cd` on Windows) to see where you are. Run course commands from the course root. |
| Editor shows no errors but `check.py` fails | The editor is checking with a different interpreter | Point the editor at your `.venv` interpreter. |

Still stuck after 20 minutes? Work through
[reference/debugging_playbook.md](reference/debugging_playbook.md) — it has an
escalation checklist and a section on writing a question that gets a useful
answer.

## Next

- Front door and daily loop: [README.md](README.md)
- The 21-day plan: [SYLLABUS.md](SYLLABUS.md)
- First lesson: [course/week1/day01_getting_started/LESSON.md](course/week1/day01_getting_started/LESSON.md)
