# Console assignment: Tasks 0 through 4

## One-file setup

Download the updated `airbnb_tasks.py` into your existing `AirBnB_clone`
folder, replacing the older copy. In Windows Git Bash, run:

```bash
cd ~/developer/AirBnB_clone
python airbnb_tasks.py .
```

The setup script contains every generated file. It needs Python 3.8 or later
and does not require downloads, external packages, or a ZIP archive. It can
also be run from another location with an explicit destination:

```bash
python /path/to/airbnb_tasks.py /path/to/AirBnB_clone
```

## What is included

- `console.py`: `HBNBCommand(cmd.Cmd)`, `(hbnb) ` prompt, help, quit, EOF,
  empty-line handling, and all five required model commands.
- `models/base_model.py`: IDs, timestamps, registration, serialization,
  reconstruction, display, and save behavior needed by the console.
- `models/user.py`, `state.py`, `city.py`, `amenity.py`, `place.py`,
  and `review.py`: all public class attributes specified in the task.
- `models/engine/file_storage.py`: JSON storage and reconstruction of all
  seven concrete classes without using `eval`.
- Package initializers, model/storage and console regression tests, and
  `check_project.py`.
- A README for a new project, this guide, and added `.gitignore` entries.

The supplied suite contains 72 test cases, including 66 model/storage tests
and six regression tests for console compatibility. Console smoke
checks additionally cover all classes, error messages in argument order,
quoted and empty strings, ignored extra arguments, integer/float conversion,
JSON persistence across independent processes, help, exits, and empty lines.
Existing console and integration tests are included in discovery. The
console writes to its configured output stream, exposes its class registry,
infers numeric values for new attributes, and protects internal attributes.

The setup changes only files it manages. Before replacing a changed file,
it copies the original into a timestamped backup directory beside the
project and prints that directory. An existing README and test package
initializers are kept. New test filenames avoid replacing conventional
existing test modules. Existing `.gitignore` entries are kept and extended.
Existing `file.json`, unrelated files, and Git configuration are preserved.
Re-running an unchanged setup does not create another backup.

For manual recovery, copy the desired original files from the printed backup
directory to the same relative paths in your project.

## Verify and run

Setup automatically runs the checker. You can run it again at any time:

| System | Check again | Start console |
| --- | --- | --- |
| Windows / Git Bash | `python check_project.py` | `python console.py` |
| Linux / macOS | `python3 check_project.py` | `python3 console.py` |

For Linux assignment compatibility, `console.py` keeps the required
`#!/usr/bin/python3` header. Windows Git Bash should launch it with
`python console.py`; this does not depend on that Linux interpreter path.

Use `quit` to leave the console. To check style as well, install the optional
checker in a local virtual environment. On Windows Git Bash:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install pycodestyle
.venv/Scripts/python.exe check_project.py
```

On Linux or macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pycodestyle
.venv/bin/python check_project.py
```

If Ubuntu reports that `venv` or `ensurepip` is unavailable, install Ubuntu's
`python3-venv` package with your normal package manager, then retry.

All required functional checks use only the standard library. A skipped
style check is reported explicitly. Any failed functional or installed style
check makes the setup return a nonzero exit status; generated files remain
available for inspection and correction. Existing tests are also discovered,
so a failure in a previous test file will be shown rather than hidden.

## Commit and push

From the project folder, check where Git's root is located:

```bash
git rev-parse --show-toplevel
git status --short
```

The first command should print the path to `AirBnB_clone`. If it prints your
home directory or another parent directory, fix the repository location
before committing. The setup does not create or move `.git` directories.

Once the checks pass and Git's root is correct:

```bash
git add console.py models tests README.md CONSOLE_TASK.md check_project.py
git add .gitignore
git diff --cached --stat
git commit -m "Complete console commands and all model classes"
git push
```

`file.json`, bytecode, virtual environments, and the downloaded setup script
are ignored. The setup itself does not stage, commit, or push anything.
