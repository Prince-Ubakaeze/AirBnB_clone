#!/usr/bin/python3
"""Regression checks for captured console output and compatible updates."""

import io
from uuid import UUID

from console import HBNBCommand
from models import storage
from models.base_model import BaseModel
from models.place import Place
from models.user import User
from tests.console_task_helpers import IsolatedStorageTestCase


class TestConsoleCompatibility(IsolatedStorageTestCase):
    """Exercise the output and update behavior used by existing tests."""

    def setUp(self):
        """Capture command output using cmd.Cmd's documented interface."""
        super().setUp()
        self.output = io.StringIO()
        self.console = HBNBCommand(stdout=self.output)

    def execute(self, command):
        """Return exactly the text written by one command."""
        self.output.seek(0)
        self.output.truncate(0)
        self.console.onecmd(command)
        return self.output.getvalue()

    def test_console_output_stream(self):
        """All output, errors, and help reach the configured stream."""
        cases = (
            ("all", "[]\n"),
            ("create", "** class name missing **\n"),
            ("show MissingClass", "** class doesn't exist **\n"),
            ("destroy BaseModel", "** instance id missing **\n"),
            ("update BaseModel absent", "** no instance found **\n"),
            ('all "BaseModel', "** invalid syntax **\n"),
        )
        for command, expected in cases:
            with self.subTest(command=command):
                self.assertEqual(self.execute(command), expected)
        self.assertIn("create BaseModel", self.execute("help create"))

    def test_captured_create_show_update_and_destroy(self):
        """Captured IDs can be used to complete an entire CRUD cycle."""
        identifier = self.execute("create User").strip()
        self.assertEqual(UUID(identifier).version, 4)
        self.assertIn(identifier, self.execute("show User " + identifier))
        self.execute('update User {} first_name "Ada Jane"'.format(
            identifier))
        self.assertIn("Ada Jane", self.execute("show User " + identifier))
        self.assertEqual(self.execute("destroy User " + identifier), "")
        self.assertNotIn("User." + identifier, storage.all())

    def test_class_registry_contains_every_model(self):
        """External consumers can inspect all supported model classes."""
        expected = {"BaseModel", "User", "State", "City", "Amenity",
                    "Place", "Review"}
        self.assertEqual(set(HBNBCommand.classes), expected)
        for name, model_class in HBNBCommand.classes.items():
            self.assertEqual(model_class.__name__, name)
            self.assertTrue(issubclass(model_class, BaseModel))

    def test_numeric_and_string_attribute_types(self):
        """New numeric fields are inferred and declared strings stay text."""
        obj = BaseModel()
        self.execute("update BaseModel {} my_number 89".format(obj.id))
        self.execute("update BaseModel {} rating 4.5".format(obj.id))
        self.assertIs(type(obj.my_number), int)
        self.assertEqual(obj.my_number, 89)
        self.assertIs(type(obj.rating), float)
        self.assertEqual(obj.rating, 4.5)
        user = User()
        self.execute('update User {} password "0123"'.format(user.id))
        self.assertEqual(user.password, "0123")

    def test_invalid_values_preserve_existing_attributes(self):
        """Invalid numbers and list updates cannot change stored defaults."""
        place = Place()
        original = place.__dict__.copy()
        for attribute in ("number_rooms", "latitude", "amenity_ids"):
            output = self.execute("update Place {} {} invalid".format(
                place.id, attribute))
            self.assertEqual(output, "** invalid attribute value **\n")
        self.assertEqual(place.__dict__, original)
        self.assertEqual(place.number_rooms, 0)
        self.assertEqual(place.latitude, 0.0)
        self.assertEqual(place.amenity_ids, [])

    def test_internal_attributes_cannot_be_overwritten(self):
        """Identity fields, timestamps, and model methods remain usable."""
        obj = BaseModel()
        original = obj.__dict__.copy()
        for attribute in ("id", "created_at", "updated_at", "__class__",
                          "save", "to_dict", "_hidden"):
            self.execute("update BaseModel {} {} changed".format(
                obj.id, attribute))
        self.assertEqual(obj.__dict__, original)
        self.assertTrue(callable(obj.save))
        self.assertTrue(callable(obj.to_dict))
