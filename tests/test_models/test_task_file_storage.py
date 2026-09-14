#!/usr/bin/python3
"""Verify JSON storage for every model class."""

from datetime import datetime
import json

from models import storage
from models.base_model import BaseModel
from models.engine.file_storage import CLASSES, FileStorage
from tests.console_task_helpers import IsolatedStorageTestCase


class TestFileStorage(IsolatedStorageTestCase):
    """Test registration, persistence, reload, and deletion."""

    def test_all_returns_live_dictionary(self):
        """Callers can inspect and modify the actual object dictionary."""
        objects = storage.all()
        obj = BaseModel()
        self.assertIs(objects["BaseModel." + obj.id], obj)
        self.assertIs(objects, storage.all())

    def test_all_classes_register_by_class_and_id(self):
        """Every supported class uses the required storage key."""
        for name, model_class in CLASSES.items():
            obj = model_class()
            self.assertIs(storage.all()[name + "." + obj.id], obj)
        self.assertEqual(len(storage.all()), 7)

    def test_new_registers_reconstructed_object(self):
        """new() also explicitly registers an object built from kwargs."""
        data = BaseModel().to_dict()
        storage.all().clear()
        obj = BaseModel(**data)
        storage.new(obj)
        self.assertIs(storage.all()["BaseModel." + obj.id], obj)

    def test_save_writes_all_classes(self):
        """Every serialized entry includes its class and ISO timestamps."""
        expected = {}
        for name, model_class in CLASSES.items():
            obj = model_class()
            obj.custom_text = name + " saved"
            expected[name + "." + obj.id] = obj.to_dict()
        storage.save()
        actual = json.loads(self.file_path.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_reload_restores_types_dates_and_values(self):
        """A fresh storage view reconstructs concrete classes correctly."""
        expected = {}
        originals = {}
        for name, model_class in CLASSES.items():
            obj = model_class()
            obj.custom_number = 42
            obj.custom_text = "A saved value"
            expected[name + "." + obj.id] = obj.to_dict()
            originals[name + "." + obj.id] = obj
        storage.save()
        storage.all().clear()
        FileStorage().reload()
        self.assertEqual(set(storage.all()), set(expected))
        for key, data in expected.items():
            with self.subTest(key=key):
                obj = storage.all()[key]
                self.assertIs(type(obj), CLASSES[data["__class__"]])
                self.assertEqual(obj.to_dict(), data)
                self.assertIsNot(obj, originals[key])
                self.assertIsInstance(obj.created_at, datetime)
                self.assertIsInstance(obj.updated_at, datetime)

    def test_missing_file_is_ignored(self):
        """A first run succeeds when the JSON file does not exist."""
        storage.reload()
        self.assertEqual(storage.all(), {})
        self.assertFalse(self.file_path.exists())

    def test_deletion_is_persisted(self):
        """Deleting and saving removes the instance after reloading."""
        obj = BaseModel()
        obj.save()
        del storage.all()["BaseModel." + obj.id]
        storage.save()
        storage.reload()
        self.assertEqual(storage.all(), {})
        self.assertEqual(json.loads(self.file_path.read_text()), {})

    def test_empty_collection_round_trip(self):
        """An empty dictionary is valid persistent storage."""
        storage.save()
        storage.reload()
        self.assertEqual(storage.all(), {})
