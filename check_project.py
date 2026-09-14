#!/usr/bin/python3
"""Check syntax, project tests, and the console without changing real data."""

import ast
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from uuid import UUID


CLASS_FIELDS = {
    "BaseModel": "name",
    "User": "first_name",
    "State": "name",
    "City": "name",
    "Amenity": "name",
    "Place": "description",
    "Review": "text",
}


def require(condition, message):
    """Stop with a useful explanation when a behavior is incorrect."""
    if not condition:
        raise RuntimeError(message)


def project_environment(root):
    """Make project imports work from an isolated working directory."""
    environment = os.environ.copy()
    previous = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = str(root)
    if previous:
        environment["PYTHONPATH"] += os.pathsep + previous
    return environment


def run_console(root, directory, commands):
    """Run a fresh console process and remove its prompts from output."""
    result = subprocess.run(
        [sys.executable, str(root / "console.py")],
        input=commands, text=True, capture_output=True,
        cwd=directory, env=project_environment(root), timeout=15)
    require(result.returncode == 0,
            "Console failed: " + result.stdout + result.stderr)
    require(not result.stderr, "Console error: " + result.stderr)
    return result.stdout.replace("(hbnb) ", "").strip()


def saved_objects(directory):
    """Read the isolated JSON data written by a console process."""
    path = Path(directory) / "file.json"
    return json.loads(path.read_text(encoding="utf-8"))


def check_console(root, directory):
    """Exercise the assignment's command behavior and persistence."""
    result = subprocess.run(
        [sys.executable, "-c", "import console; print('import-safe')"],
        input="create User\nquit\n", text=True, capture_output=True,
        cwd=directory, env=project_environment(root), timeout=15)
    require(result.returncode == 0 and result.stdout == "import-safe\n"
            and not result.stderr, "Importing console must not run it")
    require(not (Path(directory) / "file.json").exists(),
            "Importing console unexpectedly created a storage file")

    for command in ("create", "show", "destroy", "update"):
        output = run_console(root, directory, command + "\nquit\n")
        require(output == "** class name missing **", command + " class")
        output = run_console(root, directory,
                             command + " MissingModel\nquit\n")
        require(output == "** class doesn't exist **", command + " type")
    for command in ("show", "destroy", "update"):
        output = run_console(root, directory,
                             command + " BaseModel\nquit\n")
        require(output == "** instance id missing **", command + " id")
        output = run_console(root, directory,
                             command + " BaseModel absent\nquit\n")
        require(output == "** no instance found **", command + " object")
    output = run_console(root, directory, "all MissingModel\nquit\n")
    require(output == "** class doesn't exist **", "all class validation")

    ids = {}
    for name, field in CLASS_FIELDS.items():
        obj_id = run_console(root, directory, "create " + name + "\n")
        require(str(UUID(obj_id)) == obj_id, "create must print a UUID")
        ids[name] = obj_id
        key = name + "." + obj_id
        original = saved_objects(directory)[key]
        require(original["__class__"] == name, "Saved model class")

        prefix = name + " " + obj_id
        output = run_console(root, directory, "show " + prefix + "\n")
        require(output.startswith("[{}] ({})".format(name, obj_id)),
                "show after reload: " + name)
        command = 'update {} {} "A room in Lagos" ignored "unused"\n'
        output = run_console(root, directory, command.format(prefix, field))
        require(output == "", "Successful update should be silent")
        updated = saved_objects(directory)[key]
        require(updated[field] == "A room in Lagos", "Quoted string value")
        require("ignored" not in updated, "Only one attribute per update")
        require(updated["created_at"] == original["created_at"],
                "An update must preserve the creation timestamp")
        require(updated["updated_at"] != original["updated_at"],
                "An update must refresh the modification timestamp")
        output = run_console(root, directory, "show " + prefix + "\n")
        require("A room in Lagos" in output, "show updated attributes")
        output = run_console(root, directory, "all " + name + "\n")
        listed = ast.literal_eval(output)
        require(len(listed) == 1 and isinstance(listed[0], str),
                "all must return a filtered list of strings")
        require(listed[0].startswith("[" + name + "]"), "all class filter")

    output = run_console(root, directory, "all\n")
    listed = ast.literal_eval(output)
    require(len(listed) == 7 and all(isinstance(x, str) for x in listed),
            "all without a class must list every instance")

    prefix = "BaseModel " + ids["BaseModel"]
    cases = (
        ("update " + prefix, "** attribute name missing **"),
        ("update " + prefix + " name", "** value missing **"),
    )
    for command, expected in cases:
        require(run_console(root, directory, command + "\n") == expected,
                "Missing update argument: " + command)
    run_console(root, directory, 'update ' + prefix + ' name ""\n')
    require(saved_objects(directory)["BaseModel." + ids["BaseModel"]]
            ["name"] == "", "An explicitly quoted empty string is valid")

    numeric_fields = {
        "number_rooms": 3, "number_bathrooms": 2, "max_guest": 4,
        "price_by_night": 150, "latitude": 6.45, "longitude": 3.40,
    }
    for field, value in numeric_fields.items():
        command = 'update Place {} {} "{}"\n'.format(
            ids["Place"], field, value)
        run_console(root, directory, command)
        actual = saved_objects(directory)["Place." + ids["Place"]][field]
        require(actual == value and type(actual) is type(value),
                "Numeric attribute type: " + field)

    blank_id = run_console(root, directory, "create BaseModel\n\n\nquit\n")
    require(str(UUID(blank_id)) == blank_id, "Empty lines repeated create")
    require(len(saved_objects(directory)) == 8,
            "Empty lines must not repeat the preceding command")
    run_console(root, directory, "destroy BaseModel " + blank_id + "\n")

    for command in ("quit\n", "EOF\n", ""):
        require(run_console(root, directory, command) == "", "Exit behavior")
    help_output = run_console(root, directory, "help\nhelp quit\nquit\n")
    for command in ("EOF", "help", "quit", "create", "show", "destroy",
                    "all", "update"):
        require(command in help_output, "Missing documented command")
    require("Quit command to exit the program" in help_output,
            "Missing quit help documentation")

    for name, obj_id in ids.items():
        prefix = name + " " + obj_id
        output = run_console(root, directory, "destroy " + prefix + "\n")
        require(output == "", "Successful destroy should be silent")
        output = run_console(root, directory, "show " + prefix + "\n")
        require(output == "** no instance found **", "Persistent deletion")
    require(saved_objects(directory) == {}, "Deleted data remains on disk")
    require(run_console(root, directory, "all\n") == "[]", "Empty all")


def main():
    """Run checks and return a nonzero status if any required check fails."""
    root = Path(__file__).resolve().parent
    sources = [root / "console.py", root / "check_project.py"]
    for folder in ("models", "tests"):
        sources.extend(sorted((root / folder).rglob("*.py")))
    for path in sources:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print("Python syntax: PASS", flush=True)

    with TemporaryDirectory(prefix="airbnb-model-check-") as directory:
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s",
             str(root / "tests"), "-t", str(root)],
            cwd=directory, env=project_environment(root), timeout=60)
        require(result.returncode == 0, "Project unit tests failed")
    print("Project unit tests: PASS", flush=True)

    with TemporaryDirectory(prefix="airbnb-console-check-") as directory:
        check_console(root, directory)
    print("Console commands and fresh-process persistence: PASS", flush=True)

    if importlib.util.find_spec("pycodestyle") is not None:
        result = subprocess.run(
            [sys.executable, "-m", "pycodestyle", "console.py", "models",
             "tests", "check_project.py"], cwd=root, timeout=60)
        require(result.returncode == 0, "pycodestyle reported style errors")
        print("pycodestyle: PASS", flush=True)
    else:
        print("pycodestyle: SKIPPED (optional tool is not installed)")
        print("To install it in a project environment:")
        python_name = "python" if os.name == "nt" else "python3"
        venv_python = (".venv/Scripts/python.exe" if os.name == "nt"
                       else ".venv/bin/python")
        print("  " + python_name + " -m venv .venv")
        print("  " + venv_python + " -m pip install pycodestyle")
        print("  " + venv_python + " check_project.py")
    print("All required functional checks passed.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError,
            subprocess.TimeoutExpired) as error:
        print("CHECK FAILED: " + str(error), file=sys.stderr)
        sys.exit(1)
