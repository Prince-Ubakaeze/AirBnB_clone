# AirBnB clone: BaseModel and file storage

This Python project implements tasks 0–5 from the supplied AirBnB clone
assignment: project documentation, contributor information, style compliance,
unit tests, a shared base model, dictionary reconstruction and JSON file storage.
It is the initial backend milestone, not a booking website.

A small command interpreter is included so the model and persistence can be
used interactively. This version supports `BaseModel` only. Tasks after task 5
were not included in the supplied instructions.

## Quick start

Use Python 3; this package was verified with Python 3.12. Run the following
from the `AirBnB_clone` repository root:

```bash
python3 console.py
```

On systems where Python is named `python`, replace `python3` with `python`.
On Linux/macOS, `./console.py` also works when its executable permission is set.
If an archive tool dropped that permission, run `chmod +x console.py`.

The prompt is `(hbnb) `. Type `help` to list commands and `help create` for
help on one command. `quit` or end of input exits. Empty lines do nothing.

## Interpreter commands

| Command | Purpose |
| --- | --- |
| `create BaseModel` | Create and save an object; print its ID. |
| `show BaseModel <id>` | Display one object's attributes. |
| `all` or `all BaseModel` | Display the registered objects. |
| `update BaseModel <id> <attribute> <value>` | Change an attribute and save. |
| `destroy BaseModel <id>` | Delete an object and save the change. |
| `help` or `help <command>` | Show usage information. |
| `quit` or `EOF` | Exit the interpreter. |

Example session (replace `<id>` with the ID printed by `create`):

```text
(hbnb) create BaseModel
<new UUID printed here>
(hbnb) update BaseModel <id> name "My First Model"
(hbnb) update BaseModel <id> my_number 89
(hbnb) show BaseModel <id>
(hbnb) all
(hbnb) quit
```

Values containing spaces must be quoted. Whole-number values become integers,
decimal values become floats, and other values remain strings. Identity and
timestamp attributes cannot be edited through `update`; model methods and
private attribute names are also protected.

Non-interactive mode:

```bash
printf 'create BaseModel\nall\nquit\n' | python3 console.py
```

Each save writes to `file.json` in the current working directory. Starting
another Python process from the same directory reloads those objects. A
missing file is normal on first use. Invalid JSON and unsupported stored model
classes raise errors so a damaged or incompatible file is visible.

## Using the models directly

```python
from models import storage
from models.base_model import BaseModel

model = BaseModel()
model.name = "My First Model"
model.my_number = 89
model.save()

data = model.to_dict()
restored = BaseModel(**data)
assert restored.id == model.id
assert restored is not model
print(storage.all())
```

New instances register themselves with `storage`. Instances reconstructed from
keyword arguments do not register themselves; `FileStorage.reload()` inserts
them after reconstruction. `save()` refreshes `updated_at` and persists the
registered objects. `to_dict()` copies the instance dictionary, adds the class
name and converts timestamps to ISO strings without changing the instance.

## Tests and style

The tests use Python's `unittest` module, temporary storage files and fresh
processes to verify reconstruction and persistence without altering real data.

```bash
python3 -m unittest discover tests
echo "python3 -m unittest discover tests" | bash
```

Install the development tool in a virtual environment on Linux/macOS:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m pycodestyle console.py models tests
```

No third-party package is needed to run the application or its unit tests.

## Files

| Path | Role |
| --- | --- |
| `models/base_model.py` | IDs, timestamps, serialization and save behavior. |
| `models/__init__.py` | Shared `storage` instance and startup reload. |
| `models/engine/file_storage.py` | Object registry and JSON persistence. |
| `models/engine/__init__.py` | Storage package. |
| `console.py` | BaseModel command interpreter. |
| `tests/` | Unit and subprocess integration tests. |
| `AUTHORS` | Contributor names and email addresses; personalize this file. |
| `START_HERE.md` | Single-download setup and GitHub submission instructions. |

## Contributors and GitHub workflow

Replace the example in `AUTHORS` with your real name and email, and list every
teammate who contributed. The setup script can do this with its repeatable
`--author "Full Name <email@example.com>"` option.

Work on a branch and open a pull request. `START_HERE.md` explains how to add
all project files in one Git operation. Use repository name `AirBnB_clone`.

## References

- [Python datetime](https://docs.python.org/3/library/datetime.html)
- [Python cmd](https://docs.python.org/3/library/cmd.html)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
