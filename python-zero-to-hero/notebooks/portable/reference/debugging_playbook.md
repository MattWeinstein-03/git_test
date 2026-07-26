# Debugging playbook

Debugging is not a talent. It is a procedure, and the procedure below is the one
professionals actually use. Beginners debug by staring at code and changing things
that look suspicious; that is guessing, and it is slow. What follows replaces
guessing with a loop that converges.

The core discipline: **stop trying to fix the bug and start trying to locate it.**
You cannot fix what you cannot see, and almost every stubborn bug turns out to be a
place where the code does exactly what you told it to and you were wrong about what
you told it.

---

## The loop

1. **Read the error.** All of it, bottom-up.
2. **Reproduce it.** Reliably, in as few lines as possible.
3. **Localise it.** Bisect until you know the exact line and the exact values.
4. **Check your assumptions.** Print or assert what you *believe* is true.
5. **Form one hypothesis. Change one thing.** Re-run.
6. **Confirm the fix, then keep it fixed** with a test.

Steps 1-4 are where the work is. If you find yourself on step 5 repeatedly with no
progress, you skipped step 3.

---

## 1. Read the traceback bottom-up

A traceback is printed outermost call first, innermost last, which is the opposite
of the order you want to read it in.

```
Traceback (most recent call last):
  File "report.py", line 20, in <module>
    main()
  File "report.py", line 15, in main
    print(summarise(rows))
  File "report.py", line 9, in summarise
    return total / len(rows)
ZeroDivisionError: division by zero
```

Read in this order:

1. **The last line.** The exception type and message. This is *what* went wrong.
   `ZeroDivisionError: division by zero`.
2. **The frame directly above it.** The file, line number and source line that
   raised. This is *where*. `report.py` line 9, `return total / len(rows)`.
3. **Upwards through the frames, to find the first one you wrote.** If the deepest
   frames are inside library code (`site-packages/...`), the bug is nearly always
   in the last frame that belongs to *you* — you called a library function with
   something it did not expect. This is *how you got there*.
4. **Now ask the only question that matters:** what value would make that line
   raise that error? Here: `len(rows) == 0`. So `rows` is empty. The real bug is
   wherever `rows` was supposed to be filled.

Notes that save time:

- The error is a *symptom*. The line that raised is where the bad value was
  *used*; the bug is usually where it was *produced*. Walk backwards.
- `During handling of the above exception, another exception occurred` — read the
  *lower* traceback first; it is the failure you have now, and the upper one is
  what you were trying to handle.
- `The above exception was the direct cause of the following exception` — the upper
  one is the root cause, the lower one is the wrapper.
- For SyntaxError and IndentationError, no code ran at all, and the reported line
  is where Python *noticed*, often one line after the real mistake. Look at the
  line above.

Message-by-message meanings are in [error_messages.md](error_messages.md).

---

## 2. Reproduce it minimally

A bug you cannot reproduce on demand cannot be debugged; you can only wait for it.
A bug reproducible in three lines is nearly solved.

Work in this order:

1. Make it happen reliably. Note the exact command and input you used.
2. Copy the failing code into a new scratch file.
3. Delete everything not needed to produce the failure. Halve it, run, and if it
   still fails, halve again. If it stops failing, put back the last thing you
   removed — that thing is involved.
4. Replace inputs with the smallest literal values that still fail. Not a
   10,000-row CSV; two rows. Not the real API; a hard-coded dict of the shape the
   API returns.

```python
# Before: fails somewhere inside a 200-line pipeline
# After: the whole bug
rows = [{"amount": "12.50"}, {"amount": ""}]
print(sum(float(r["amount"]) for r in rows))
# ValueError: could not convert string to float: ''
```

Now the bug is not "my report script is broken" but "empty amount fields", which
you can decide about: skip them, treat them as zero, or reject the file.

For anything involving `input()` or files, replace it with a hard-coded value
first. Interactive input makes iteration slow and hides which value caused the
problem.

---

## 3. Bisect

When you do not know *where* the problem is, do not read the whole program. Cut the
search space in half repeatedly. Ten halvings cover a thousand lines.

**Bisect in space.** Put one probe at the middle of the suspect region:

```python
print(f"HALFWAY {rows=}")
```

Is the data correct at that point? If yes, the bug is after it; if no, before it.
Move the probe into the failing half and repeat. Four or five probes localise
almost anything.

**Bisect in time.** If it worked earlier today, what did you change? Comment out
the most recent change and re-run. Small commits make this trivial (`git stash`,
`git diff`, `git bisect`); this is one of the practical reasons to commit often.

**Bisect in data.** If it fails on a 5,000-line file, try the first 2,500 lines,
then 1,250. You will usually land on one malformed row, and looking at that row
explains everything.

**Bisect in configuration.** Fails in your project but not in a fresh scratch file?
The difference is the bug: a shadowed module name, a stale `__pycache__`, the wrong
interpreter, an inactive virtualenv.

---

## 4. Check your assumptions

Almost every bug is a false belief about a value: its content, its type, or whether
that line runs at all. Make the beliefs visible.

```python
print(f"{rows=}")                    # content — the = form prints the expression too
print(f"{type(amount)=} {amount=!r}") # type and exact repr; !r shows quotes
print(f"{len(rows)=} {bool(rows)=}")  # size and truthiness
print("reached the else branch")      # did this line run at all?
```

Rules for good probes:

- Print **types** as well as values. `"5"` and `5` look identical when printed
  plainly; `!r` and `type()` distinguish them. A huge share of beginner bugs are
  string-versus-number.
- Label every probe. Ten unlabelled numbers in the output teach you nothing.
- Print **inside** loops and branches, not only before and after. "It printed once
  when I expected three times" is a solved bug.
- Use `!r` for anything text-shaped. It reveals trailing whitespace, `None`, empty
  strings and unexpected quotes, all of which are invisible otherwise.
- Delete probes when done, or convert the useful ones to tests.

Assertions are probes that check themselves and get louder:

```python
assert isinstance(rows, list), f"expected list, got {type(rows)}"
assert rows, "rows should never be empty here"
assert 0 <= pct <= 100, f"percentage out of range: {pct}"
```

An assert states an invariant. When it fires you learn both *what* is wrong and
*where* the wrongness starts, which is more information than a print gives you.
Keep the cheap ones permanently; they are documentation that executes.

---

## 5. Use `breakpoint()`

Prints are fine for one or two values. When you need to look around at a moment in
time, stop the program there instead.

```python
def summarise(rows):
    total = sum(r["amount"] for r in rows)
    breakpoint()          # execution pauses here, you get a (Pdb) prompt
    return total / len(rows)
```

Run the program normally. At the prompt, every name in scope is available and you
can evaluate any expression.

| Command | Effect |
|---|---|
| `l` | list source around the current line (`ll` for the whole function) |
| `p expr` | print an expression; `pp` pretty-prints structures |
| `n` | next line, stepping *over* function calls |
| `s` | step *into* the call on this line |
| `r` | run until the current function returns |
| `c` | continue until the next breakpoint or the end |
| `w` | where: the call stack |
| `u` / `d` | move up / down a stack frame to inspect a caller's variables |
| `a` | show the current function's arguments |
| `q` | quit the program |
| `h` | help; `h <cmd>` for one command |

Two practical notes: any name that collides with a pdb command needs `p` in front
(`p n` prints your variable `n`, while `n` steps). And with pytest, use
`python -m pytest path::test_name -s` — without `-s` pytest captures stdin and the
prompt does not work.

To inspect a crash rather than a chosen line, run the whole thing under post-mortem
and you land at the failing frame with everything still alive:

```bash
python -m pdb -c continue myscript.py
```

---

## 6. Rubber-duck it

Explain the code out loud, line by line, to something that cannot help you — a
duck, a wall, a text file. Say what each line is *supposed* to do and what value
you *expect*.

This works because it forces sequential, honest articulation. Reading code
silently, your brain smooths over the gap; saying "and then this returns the sorted
list" out loud while looking at `xs.sort()` is usually the moment you notice it
returns `None`. Bugs live precisely in the places where your explanation goes vague
— "and then it sort of handles the rest" is a location, not a filler phrase.

Do it in writing if you prefer. Writing a question for someone else is the same
mechanism, which is why so many questions get answered by the person asking them.

---

## Reading documentation effectively

Being able to answer your own questions from primary sources is the single skill
that outlives this course.

**Search like this:** `python <module> <thing>` — `python pathlib glob recursive`,
`python csv DictReader` — and prefer `docs.python.org` results. Add the version if
it matters. Do not paste your variable names into the search; strip the query down
to the concept.

**Search an error like this:** remove your specific names and quote the invariant
part: search `python "object is not subscriptable"`, not `python 'Order' object is
not subscriptable at line 41`.

**In the terminal, faster than a browser:**

```python
help(str.split)                  # signature and docstring
help(pathlib.Path)               # everything on the class
dir(obj)                         # what attributes does this have
[m for m in dir(str) if "split" in m]
import inspect; print(inspect.signature(fn))
print(fn.__doc__)
```

**How to read a stdlib doc page:** find the function, read its *signature* (which
arguments are required, which are keyword-only, what the defaults are), read the
first sentence and the return value, then skip to the examples at the bottom. Then
try it in the REPL with two-item toy data before wiring it into your program.

**Source reliability, in order:** the official docs at docs.python.org and the
library's own documentation; the library's source code (often the fastest answer
for "what does this actually do"); recent, highly-voted Q&A answers; blog posts,
with the date checked; AI answers, which you verify by running them. Any snippet
you cannot run and explain does not count as an answer yet.

---

## Stuck for 20 minutes: escalation checklist

Timebox it. When 20 minutes pass with no forward movement, stop poking the code and
run this list in order. It is deliberately mechanical, because your judgement is
the thing that is currently failing.

1. **Say the failure out loud in one sentence.** "When I pass an empty list,
   `average` raises ZeroDivisionError." If you cannot, you do not yet know what is
   wrong — go back to reproducing it.
2. **Re-read the error message.** All of it. Then look it up in
   [error_messages.md](error_messages.md).
3. **Re-read the exercise docstring.** Word by word. Check the return *type*, the
   edge cases named, and the worked examples. A large share of "wrong answer" bugs
   are correct code answering a different question.
4. **Re-read the relevant numbered section of today's `LESSON.md`.** Not the whole
   file — the section that covers the thing you are using.
5. **Run the day's `examples.py`.** It contains a working version of the technique.
   Compare it with yours line by line.
6. **Print the inputs and the output** of the failing function, with `!r` and
   `type()`. Confirm the input is what you think it is. Very often it is not.
7. **Check the four usual suspects:**
   - a string where a number belongs, or the reverse
   - `None` from a function that forgot to `return`, or from a mutating method
   - an off-by-one in a range, index or slice
   - a mutable object shared by two names
8. **Reproduce it in five lines** in a scratch file, as in section 2.
9. **Prove the test is passable:** `PZH_SOLUTIONS=1 python -m pytest
   course/weekN/dayNN_*/test_exercises.py -q`. Green means the tests are fine and
   the problem is in your code — that certainty is worth the ten seconds.
10. **Read the failing test.** `test_exercises.py` is plain Python and it is the
    precise specification. It tells you the exact input and the exact expected
    output.
11. **`breakpoint()` at the failing line.** Look at everything in scope.
12. **Take a five-minute walk.** Not a euphemism for giving up. Fixation is a real
    failure mode, and stepping away for five minutes is a faster fix for it than
    another twenty minutes of staring.
13. **Write the question** as described below. If you still have it after writing,
    ask it.
14. **Only now, if the day's tests are still red after all of the above:** read
    `solutions.py`, but read it as a diff against your own attempt — find the one
    line where your logic diverges, understand *why*, then close it and retype your
    own version from scratch. Never copy the file wholesale; you will not have
    learned the thing the day existed to teach.

---

## Asking a good question

Whether you ask a person, a forum or an AI, the quality of the answer is set by the
quality of the question. A good question has five parts and takes ten minutes to
write. Writing it frequently answers it.

1. **What you are trying to do.** One sentence about the goal, not the code.
   "I am counting how many times each word appears in a file."
2. **The minimal reproducible example.** Code someone else can run unchanged,
   complete but as short as possible, with hard-coded input instead of a file or
   API. No unrelated functions, no imports you do not use.
3. **What you expected.** Concretely: `{"a": 2, "b": 1}`.
4. **What happened instead.** The *full* traceback, copied as text, not a
   screenshot and not paraphrased. If there is no error, the actual wrong output.
5. **What you already tried,** and what it ruled out. This stops people repeating
   your work and shows where your model is wrong.

Also state your Python version (`python --version`) and operating system if
anything platform-specific is involved.

A complete example:

> **Goal:** count word frequencies from a string.
>
> **Code:**
> ```python
> text = "a b a"
> counts = {}
> for word in text.split():
>     counts[word] += 1
> print(counts)
> ```
>
> **Expected:** `{'a': 2, 'b': 1}`
>
> **Got:**
> ```
> Traceback (most recent call last):
>   File "wc.py", line 4, in <module>
>     counts[word] += 1
> KeyError: 'a'
> ```
>
> **Tried:** printing `counts` before the loop — it is `{}`. I think the problem is
> that I am adding to a key that does not exist yet, but I do not know the idiomatic
> way to handle the first occurrence.
>
> **Python 3.11 on macOS.**

That question is answerable in one line (`counts[word] = counts.get(word, 0) + 1`,
or `collections.Counter`), and — this is the point — the person who wrote it
understood their own bug by sentence four.

What makes a question unanswerable: "my code doesn't work", a screenshot of a
terminal, a paraphrased error, 300 lines with the relevant 5 unmarked, or no
statement of expected output. If you would not be able to help someone from the
information you provided, do not send it yet.

---

Related: [error_messages.md](error_messages.md) · [glossary.md](glossary.md) ·
[../CHEATSHEET.md](../CHEATSHEET.md) · [../README.md](../README.md)
