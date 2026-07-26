# What's next

You finished 21 days. Here is an accurate assessment of where that puts you, and
what to do about it.

**What you can now do:** read most Python you encounter, write programs of a few
hundred lines that are organised into functions, modules and classes, handle errors
deliberately, move data through files, JSON, CSV, HTTP APIs and SQLite, test your
own code, and — most importantly — learn the next library from its documentation
without a course.

**What you cannot yet do:** design a system that five people work on for two years,
estimate work reliably, review someone else's architecture, or reach for the right
tool without looking it up. Those come from volume: shipping things, reading other
people's code, and being wrong in public. There is no shortcut, but there is a
straight road, and it starts with picking one direction instead of four.

**The one decision that matters now:** stop taking courses and start building. Pick
one track below, learn its first two items, and build the portfolio project with
them. Depth in one direction beats a shallow tour of all four, and the fundamentals
you have are transferable — nothing here is wasted if you later switch.

---

## Track 1: Backend and web APIs

Build the services other programs talk to. The largest job market for Python, and
the most direct continuation of Days 19 and 21.

**Learn in this order:**

1. **HTTP and REST properly.** Methods, status codes, headers, idempotency,
   authentication, pagination. You touched this on Day 19; go deeper before picking
   a framework, because every framework assumes it.
2. **FastAPI.** Routing, request and response models with Pydantic, dependency
   injection, automatic OpenAPI docs, async endpoints. Your Day 8 type hints and
   Day 12 classes become load-bearing here.
3. **SQL and an ORM.** Real schema design, joins, indexes, and transactions in raw
   SQL first, then SQLAlchemy 2.x (or SQLModel) plus Alembic for migrations. Do not
   skip raw SQL; an ORM you cannot debug is a liability.
4. **Deployment.** Docker, environment-based configuration, a managed Postgres,
   and one platform (Fly.io, Railway, or AWS). "It works on my machine" is not a
   finished project.
5. **Production concerns.** Structured logging, error tracking (Sentry), health
   checks, rate limiting, and background jobs with Celery or RQ.

**Canonical libraries:** FastAPI, Pydantic, SQLAlchemy, Alembic, httpx, uvicorn,
pytest + httpx's test client, Docker. Django is the alternative to FastAPI when you
want batteries, an admin UI and server-rendered pages; Flask is the minimal
middle ground.

**First portfolio project:** a JSON API for something you personally want — a
reading list, a workout log, a bookmark archive. Requirements: user accounts with
hashed passwords and token auth, full CRUD on the main resource, Postgres via
migrations, input validation, pagination and filtering on list endpoints, 80%+ test
coverage, a Dockerfile, and a deployed URL a stranger can hit. That project answers
more interview questions than any certificate.

---

## Track 2: Data analysis

Turn data into answers. The fastest track to visible results, and the one where
your Day 10 and Day 15 skills pay off immediately.

**Learn in this order:**

1. **pandas.** DataFrames, indexing with `.loc`/`.iloc`, `groupby`, `merge`,
   reshaping with pivot/melt, missing data, and time series. Budget two weeks; it
   is a genuinely large API with its own idioms.
2. **Jupyter and a plotting library.** Notebooks for exploration, matplotlib for
   control, seaborn or plotly for speed and interactivity. Learn what makes a chart
   readable, not just how to emit one.
3. **Statistics you will actually use.** Distributions, sampling, confidence
   intervals, correlation versus causation, and why an average is often the wrong
   summary. Without this you will produce confident nonsense.
4. **SQL at analyst depth.** Joins, window functions, CTEs. Most real data lives in
   a warehouse, and SQL is how you get it out.
5. **Reproducible pipelines.** Turning a notebook into a script, `duckdb` or
   `polars` for data too big for pandas but too small for Spark, and versioning
   your inputs.

**Canonical libraries:** pandas, NumPy, Jupyter, matplotlib, seaborn, scipy,
statsmodels, polars, duckdb.

**First portfolio project:** an end-to-end analysis of a dataset you care about —
your bank statements, a public transport dataset, city open data. Requirements: a
documented question stated up front, a cleaning stage that handles the real mess
(the interesting part), three or four charts that each make one point, an honest
limitations section, and a written conclusion someone non-technical can read.
Publish the notebook and the code separately.

---

## Track 3: Automation and scripting

Delete your own repetitive work, then other people's. The highest immediate return
on effort, and the easiest track to practise daily.

**Learn in this order:**

1. **Robust CLI tools.** `argparse` (Day 17) then Typer or Click, `pathlib` for
   filesystem work, `logging` instead of print, exit codes, and `--dry-run` as a
   habit. A script that can destroy data should be able to tell you what it would
   do.
2. **Scheduling and packaging.** cron or systemd timers on Unix, Task Scheduler on
   Windows; `pipx` for installing tools, `pyproject.toml` for entry points so your
   tool has a real command name.
3. **Working with the messy formats you will meet.** Excel via openpyxl, PDFs via
   pypdf, HTML scraping with httpx plus BeautifulSoup or selectolax (and reading
   `robots.txt` and terms of service before you scrape), images via Pillow.
4. **APIs of tools you already use.** Your calendar, GitHub, a spreadsheet, a
   ticket system. Automating a service you use daily is where this track becomes
   genuinely valuable.
5. **Reliability.** Retries with backoff, idempotency so a re-run is safe,
   notifications on failure, and never writing over your only copy of the input.

**Canonical libraries:** Typer or Click, rich (readable terminal output), httpx,
BeautifulSoup, openpyxl, Pillow, pypdf, `subprocess`, watchdog, APScheduler.

**First portfolio project:** automate something you currently do by hand every
week. Requirements: a real command-line interface with `--help`, a `--dry-run`
mode, logging to a file, safe handling of partial failure, a config file rather
than hard-coded values, tests for the transformation logic, and a README a
colleague could follow. Bonus if it runs on a schedule and emails you when it
breaks.

---

## Track 4: Machine learning

The longest road of the four, with the most prerequisites and the most hype. Do it
because the problems interest you, not because of the job titles.

**Learn in this order:**

1. **pandas and NumPy first.** Non-negotiable. Most of a real ML project is data
   wrangling, and if you cannot reshape data you cannot do ML. Track 2's first item
   is this track's first item.
2. **The maths you cannot skip.** Linear algebra (vectors, matrices, dot products),
   calculus to the level of gradients and the chain rule, probability and
   statistics. Aim for working intuition, not exam performance.
3. **Classical ML with scikit-learn.** Train/validation/test splits, cross
   validation, overfitting, regularisation, feature engineering, pipelines, and the
   metrics that suit your problem — accuracy is usually the wrong one. Most
   real-world problems are solved here, not with deep learning.
4. **Deep learning with PyTorch.** Tensors, autograd, `nn.Module`, training loops,
   then transfer learning. Learn to fine-tune an existing model before trying to
   train from scratch.
5. **Getting a model into use.** Serving with FastAPI, versioning data and models,
   monitoring for drift, and the ethics and failure modes of deployed models. A
   model in a notebook has produced no value yet.

**Canonical libraries:** NumPy, pandas, scikit-learn, matplotlib, PyTorch, Hugging
Face transformers and datasets, MLflow or Weights & Biases.

**First portfolio project:** a supervised learning problem on data you obtained and
cleaned yourself, not a tidy Kaggle CSV. Requirements: a baseline model to beat
(even "always predict the mean"), honest evaluation on a held-out set, an error
analysis section describing what the model gets wrong and why, a discussion of
where it should not be used, and a small deployed demo. Reviewers care far more
about the error analysis than about your final score.

---

## Practice sources

Skill comes from reps on problems slightly beyond your reach.

- **Your own annoyances.** The best source, by a wide margin. Something you
  actually want to exist keeps you working through the boring middle of a project.
- **Advent of Code** (adventofcode.com) — 25 puzzles per year, increasing
  difficulty, past years always available. Excellent for the core language and data
  structures. Solve, then read other people's solutions to the same problem.
- **Exercism** (exercism.org) — Python track with human mentor feedback on your
  submissions. The feedback is the value; few sources will tell you *why* your
  working code is not idiomatic.
- **Codewars / LeetCode** — useful in moderation for algorithmic fluency and
  interview preparation. Not a substitute for building things; the skills only
  partially overlap.
- **Real bugs in real projects.** Search GitHub for `label:"good first issue"` in
  Python repositories you use. Fixing a small bug in someone else's codebase
  teaches you reading, testing and collaboration at once.
- **Rebuild a tool you use.** A tiny `grep`, a static site generator, a URL
  shortener, a JSON formatter. You learn what design decisions the real tool made
  and why.

---

## Reading other people's code

This is the fastest way to grow after the basics, and almost nobody does it
deliberately. The gap between competent and good is largely a gap in how much code
you have read.

**Where to start:** the Python standard library. It is on your machine and it is
well written. `pathlib`, `dataclasses`, `csv`, `textwrap`, `collections` are all
readable in an afternoon. Find any of them with:

```python
import csv; print(csv.__file__)
```

**Then:** a small, well-maintained third-party library you already use — `requests`,
`httpx`, `click`, `rich`. Read the tests first; they show intended usage more
honestly than the README does.

**How to read a codebase you did not write:**

1. Read the README and the tests before any source.
2. Find the entry point — `__main__.py`, `cli.py`, `app.py`, `__init__.py`.
3. Pick one feature and trace it end to end. Do not read files top to bottom, and
   do not try to understand everything.
4. Run it under `breakpoint()` or `python -m pdb` and step through. Watching real
   values move is worth an hour of reading.
5. Write down one pattern you want to steal. Then use it in your own code that
   week, or you will forget it.

**Also read diffs.** Pull requests in an active project show you how experienced
developers argue about code, what reviewers catch, and what "done" means to them.
That is knowledge you cannot get from any tutorial.

---

## Building a habit that sticks

Three weeks of intensity got you here. Intensity is not what keeps you here.

- **Consistency beats volume.** An hour a day, five days a week, beats a nine-hour
  Saturday. Every time. Skills built and skills lost both compound.
- **Always have exactly one project running.** Zero projects means no reason to
  learn; three means none finishes, and finishing is where the hard parts live.
- **Finish and ship.** Deployed, published, or in someone else's hands. The last
  10% of a project contains most of what employers care about and most of what you
  have not done before.
- **Write it down.** A short note per session: what you did, what confused you, what
  you will do next. It removes the restart cost of the next session and becomes
  evidence of progress on days when you feel stuck.
- **Keep reading the docs.** The habit of reading primary sources instead of the
  first search result is the professional differentiator. Protect it.
- **Get your code read.** A code review from someone better than you is worth ten
  tutorials. Contribute to a project, join a Python community, find one person to
  swap reviews with.
- **Take the boring parts seriously.** Tests, error handling, logging, naming,
  documentation. Everyone can write the happy path. The rest is the job.
- **Expect a slump around week five.** Beyond the basics, progress stops feeling
  fast because the problems get bigger. It is not a plateau in ability; it is a
  change in the unit of measurement. Keep shipping.

Re-read Day 18 in a month. Testing and tooling is the day whose value grows the
most once you have code worth protecting.

---

Related: [../README.md](../README.md) · [../SYLLABUS.md](../SYLLABUS.md) ·
[../CHEATSHEET.md](../CHEATSHEET.md) · [glossary.md](glossary.md)
