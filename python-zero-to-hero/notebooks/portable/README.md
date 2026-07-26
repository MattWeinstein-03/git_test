# Python Zero to Hero — portable notebooks

This one folder is the whole course as notebooks: 21 days of lesson text
with runnable code, plus the exercises, the reference solutions and the grader.
Copy it anywhere. Nothing outside it is needed.

Like everything under `notebooks/`, this folder is **generated** from
`course/weekN/dayNN_slug/LESSON.md` by `tools/build_notebooks.py`. Edit lessons,
not notebooks.

## What is in here

```
day01_getting_started.ipynb ... day21_project_capstone_pipeline.ipynb
course/weekN/dayNN_slug/      LESSON.md, examples.py, exercises.py,
                              solutions.py, test_exercises.py
reference/                    glossary, error messages, debugging playbook
check.py, conftest.py         the grader (pytest under the hood)
CHEATSHEET.md, SYLLABUS.md    lookup reference and the 21-day plan
requirements.txt              what to install
```

## Running it on a laptop

```bash
cd portable
python -m pip install -r requirements.txt
python -m jupyterlab           # or: python -m notebook
```

Open `day01_getting_started.ipynb` and work down the page. Shift+Enter runs a
cell. The last code cell of each notebook grades that day by running
`check.py dayNN` from this folder, so grading works here exactly as it does in
the full repository.

You can also grade from a terminal without Jupyter at all:

```bash
python check.py day01
python check.py            # progress across all 21 days
```

## Running it on an iPad

Any app that runs a real CPython kernel works — Juno, Carnets, a-Shell, or a
remote JupyterLab you reach through Safari. Copy this folder in (Files, iCloud
Drive, git clone in a-Shell), then open a notebook.

Two honest caveats on tablets:

- The **notebooks** run anywhere with a Python 3.10+ kernel.
- The **grading cell** additionally needs `pytest` and the ability to start a
  subprocess. Where an app forbids subprocesses, grade in a terminal app instead,
  or `import pytest; pytest.main(["course/week1/day01_getting_started"])` from a
  cell.

Blocks that need the network or the filesystem are already marked "not runnable
here" in the notebooks, so an offline tablet loses nothing.

## Editing your answers

`exercises.py` files in here are yours to fill in — this is a copy, so your work
stays in this folder. If you also work in the main repository, keep to one of the
two, because a rebuild of this bundle overwrites these copies with fresh stubs
from the course.
