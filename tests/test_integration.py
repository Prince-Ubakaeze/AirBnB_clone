#!/usr/bin/python3
"""Verify imports and persistence across separate Python processes."""

import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

from tests.helpers import StorageTestCase


class TestIntegration(StorageTestCase):
    """Run real Python and console processes in a temporary directory."""

    def run_process(self, code=None, input_text=None):
        """Run Python with the project on its module search path."""
        root = str(Path(__file__).resolve().parents[1])
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(
            filter(None, (root, environment.get("PYTHONPATH", ""))))
        command = [sys.executable]
        if code is not None:
            command.extend(["-c", code])
        else:
            command.append(os.path.join(root, "console.py"))
        result = subprocess.run(command, input=input_text,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                cwd=os.path.dirname(self.path),
                                env=environment, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def test_new_process_reloads_saved_object_automatically(self):
        """Importing models in a fresh process restores saved state."""
        identifier = self.run_process(
            "from models.base_model import BaseModel\n"
            "model = BaseModel()\n"
            "model.name = 'Saved across processes'\n"
            "model.my_number = 89\n"
            "model.save()\n"
            "print(model.id)\n").strip()
        output = self.run_process(
            "import json\n"
            "from models import storage\n"
            "print(json.dumps({key: value.to_dict() "
            "for key, value in storage.all().items()}))\n")
        restored = json.loads(output)["BaseModel." + identifier]
        self.assertEqual(restored["name"], "Saved across processes")
        self.assertEqual(restored["my_number"], 89)
        self.assertEqual(restored["id"], identifier)

    def test_alternate_import_order(self):
        """Importing storage and BaseModel in either order succeeds."""
        for imports in (
                "from models.base_model import BaseModel\n"
                "from models import storage\n",
                "from models.engine.file_storage import FileStorage\n"
                "from models.base_model import BaseModel\n"
                "from models import storage\n"):
            with self.subTest(imports=imports):
                self.assertEqual(self.run_process(
                    imports + "print(len(storage.all()))\n"), "0\n")

    def test_console_pipeline_persists_across_sessions(self):
        """Piped console input creates data that a later session sees."""
        output = self.run_process(input_text="create BaseModel\nquit\n")
        with open(self.path, encoding="utf-8") as stream:
            saved = json.load(stream)
        key = next(iter(saved))
        identifier = saved[key]["id"]
        self.assertEqual(UUID(identifier).version, 4)
        self.assertIn(identifier, output)
        self.assertIn(identifier,
                      self.run_process(input_text="all\nquit\n"))

    def test_console_exits_on_empty_input(self):
        """End of piped input exits without hanging or raising."""
        self.assertIn("(hbnb)", self.run_process(input_text=""))

    def test_console_blank_line_does_not_repeat_in_pipeline(self):
        """A blank line after creation does not duplicate the object."""
        self.run_process(input_text="create BaseModel\n\nquit\n")
        with open(self.path, encoding="utf-8") as stream:
            self.assertEqual(len(json.load(stream)), 1)
