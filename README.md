# namePicker

A terminal tool for teachers that calls on students fairly and keeps track of
how many times each student has been called, per task. Students who have been
called the fewest times come up first, with ties shuffled so the order is never
predictable.

## Features

- **Fair call order** - least-called students go first, random within ties
- **Per-task tracking** - separate counters for questions, books, pointer,
  brooms/volunteers, and Jeopardy
- **Last-called date** - see when a student was last called ("3 days ago", "never")
- **In-session controls** - mark absent, skip to the next student, choose a
  specific student, drumroll
- **Group maker** - divide the class by gender, odd/even, sections, random,
  every Nth student, or reload previously saved groups, then edit them
- **Jeopardy mode** - round-robin questions across teams
- **Spinner** - random picker
- **Fun countdowns** - "Eenie meenie miney moe" and an ASCII-art countdown
- **Safe saving** - writes go to a temp file first, so a crash mid-save can't
  corrupt your roster

## Requirements

- Python 3.8 or newer
- No third-party packages (standard library only)

## Quick start

```bash
# 1. Get the code
git clone https://github.com/<your-username>/namePicker.git
cd namePicker

# 2. Add a class file. To try it out with the fake sample class:
#    Windows:      copy sample_data\G2-1.csv classes\G2-1.csv
#    macOS/Linux:  cp sample_data/G2-1.csv classes/G2-1.csv

# 3. Run it
python main.py            # Windows (or double-click NamePicker.bat)
python3 main.py           # macOS / Linux
```

When it asks for a class, type `1` to load `classes/G2-1.csv`.

### Optional: use a virtual environment

Not required, since there are no dependencies, but it is good practice and
keeps your Python setup tidy:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Class files

Each class is one CSV in `classes/`, named `G2-<number>.csv` (typing `4` at the
prompt loads `classes/G2-4.csv`). The columns are:

| Column | Meaning |
|---|---|
| `room` | Class name, e.g. `G2-1` |
| `id` | Unique ID for each student |
| `#` | Class number |
| `Name` | Student name |
| `Gender` | `boy` or `girl` (used by the gender grouping) |
| `qCount`, `bCount`, `jCount`, `pCount` | Times called for questions, tasks, Jeopardy, and pointer |
| `qLast`, `bLast`, `jLast`, `pLast` | Date of the last call (`YYYY-MM-DD`), blank if never |
| `group` | Saved group name, blank if none |

See [`sample_data/G2-1.csv`](sample_data/G2-1.csv) for a complete example.

> **Privacy:** `classes/*.csv` is listed in `.gitignore` so real student names
> never get committed. Only the made-up sample in `sample_data/` is tracked.

## During a calling session

| Input | Effect |
|---|---|
| *(Enter)* | Call the next student |
| `A` | Mark the last student absent |
| `N` | Call the next person instead |
| `C <name>` | Choose a specific student (partial names work if unique) |
| `D` | Drumroll |
| `S` | Stop and go to the save prompt |

## Project layout

```
namePicker/
|-- main.py             Entry point: loads a class, shows the main menu
|-- activities.py       The menu modes (questions, Jeopardy, spinner, groups)
|-- call_queue.py       Fair call-order logic
|-- grouping.py         Ways to divide the class into groups
|-- models.py           Student / Group / Roster data classes
|-- storage.py          All CSV reading and writing
|-- ui.py               Terminal boxes, menus, and prompts
|-- fun.py              Countdowns and ASCII art (safe to delete)
|-- console_window.py   Windows-only window size / font tweaks
|-- config.py           Settings: sizes, pacing, CSV columns, categories
|-- NamePicker.bat      Double-click launcher for Windows
|-- classes/            Your real class CSVs (git-ignored)
|-- sample_data/        Fake example class for trying the app
|-- requirements.txt    Dependencies (none right now)
```

Each layer only depends on the ones beneath it: `models` knows nothing, `storage`,
`call_queue`, and `grouping` know only `models`, `ui` knows nothing about the
data, and `activities` ties them together.

## Configuration

Everything tweakable is in [`config.py`](config.py): box width and border style,
pacing of the ". . ." transitions, window size and font (Windows), and the CSV
columns.

**Windows window styling:** `console_window.py` tries to center the window and set
the font size. It only works in the classic console (`cmd.exe`), not Windows
Terminal. If it has no effect, set the size and font in Windows Terminal's own
settings, or set `ENABLE_WINDOW_STYLING = False` in `config.py`.

## Adding a new call category

1. Add the count and last-called columns to `FIELDS` in `config.py`
2. Add entries to `CATEGORIES` and `LAST_CALLED_FIELD` in `config.py`
3. Add a menu entry in `main.py`

`models.py`, `storage.py`, and `call_queue.py` don't need to change.
