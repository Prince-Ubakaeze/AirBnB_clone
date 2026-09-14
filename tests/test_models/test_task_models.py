#!/usr/bin/python3
"""Verify model defaults, identity, serialization, and persistence."""

from datetime import datetime
import json
from uuid import UUID

from models import storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from tests.console_task_helpers import IsolatedStorageTestCase


class ModelChecks:
    """Apply the shared model contract to every concrete class."""

    def test_inherits_base_model(self):
        """All supported classes share BaseModel's behavior."""
        self.assertIsInstance(self.model_class(), BaseModel)

    def test_public_class_defaults(self):
        """Required defaults exist on the class with exact types."""
        obj = self.model_class()
        for name, expected in self.defaults.items():
            with self.subTest(attribute=name):
                self.assertIn(name, self.model_class.__dict__)
                self.assertEqual(getattr(obj, name), expected)
                self.assertIs(type(getattr(obj, name)), type(expected))

    def test_new_identity_and_timestamps(self):
        """New instances have unique UUID4 IDs and datetime fields."""
        first = self.model_class()
        second = self.model_class()
        self.assertIs(type(first.id), str)
        self.assertEqual(UUID(first.id).version, 4)
        self.assertNotEqual(first.id, second.id)
        self.assertIsInstance(first.created_at, datetime)
        self.assertIsInstance(first.updated_at, datetime)

    def test_new_instance_is_registered(self):
        """Construction registers exactly this object with storage."""
        obj = self.model_class()
        key = "{}.{}".format(self.model_class.__name__, obj.id)
        self.assertIs(storage.all()[key], obj)

    def test_to_dict_is_independent_and_json_compatible(self):
        """Serialization uses ISO dates without changing the instance."""
        obj = self.model_class()
        obj.custom_text = "A room in Lagos"
        result = obj.to_dict()
        self.assertEqual(result["__class__"], self.model_class.__name__)
        self.assertEqual(result["created_at"], obj.created_at.isoformat())
        self.assertEqual(result["updated_at"], obj.updated_at.isoformat())
        self.assertEqual(result["custom_text"], obj.custom_text)
        self.assertEqual(json.loads(json.dumps(result)), result)
        result["custom_text"] = "Changed dictionary"
        self.assertEqual(obj.custom_text, "A room in Lagos")
        self.assertNotIn("__class__", obj.__dict__)
        self.assertIsInstance(obj.created_at, datetime)

    def test_kwargs_restore_without_registering(self):
        """Dictionary construction restores dates and skips registration."""
        obj = self.model_class()
        obj.custom_number = 12
        data = obj.to_dict()
        storage.all().clear()
        restored = self.model_class(**data)
        self.assertEqual(restored.to_dict(), data)
        self.assertIsInstance(restored.created_at, datetime)
        self.assertIsInstance(restored.updated_at, datetime)
        self.assertEqual(storage.all(), {})
        self.assertNotIn("__class__", restored.__dict__)

    def test_string_format(self):
        """The display includes class, ID, and the instance dictionary."""
        obj = self.model_class()
        expected = "[{}] ({}) {}".format(
            self.model_class.__name__, obj.id, obj.__dict__)
        self.assertEqual(str(obj), expected)

    def test_save_updates_timestamp_and_persists(self):
        """Saving changes updated_at and writes current attributes."""
        obj = self.model_class()
        created_at = obj.created_at
        obj.updated_at = datetime(2000, 1, 1)
        obj.custom_text = "Saved value"
        obj.save()
        self.assertGreater(obj.updated_at, datetime(2000, 1, 1))
        self.assertEqual(obj.created_at, created_at)
        content = json.loads(self.file_path.read_text(encoding="utf-8"))
        key = "{}.{}".format(self.model_class.__name__, obj.id)
        self.assertEqual(content[key], obj.to_dict())


class TestBaseModel(ModelChecks, IsolatedStorageTestCase):
    """Test BaseModel's shared contract."""

    model_class = BaseModel
    defaults = {}

    def test_positional_arguments_are_ignored(self):
        """Unused positional arguments do not replace generated fields."""
        obj = BaseModel("unused", 42)
        self.assertEqual(UUID(obj.id).version, 4)

    def test_iso_dates_without_microseconds(self):
        """Reload exact-second timestamps produced by isoformat()."""
        obj = BaseModel(id="known-id", __class__="BaseModel",
                        created_at="2026-01-01T00:00:00",
                        updated_at="2026-01-01T00:00:00")
        self.assertEqual(obj.created_at, datetime(2026, 1, 1))


class TestUser(ModelChecks, IsolatedStorageTestCase):
    """Test User and its account fields."""

    model_class = User
    defaults = {"email": "", "password": "", "first_name": "",
                "last_name": ""}


class TestState(ModelChecks, IsolatedStorageTestCase):
    """Test State and its name field."""

    model_class = State
    defaults = {"name": ""}


class TestCity(ModelChecks, IsolatedStorageTestCase):
    """Test City and its state relationship."""

    model_class = City
    defaults = {"state_id": "", "name": ""}


class TestAmenity(ModelChecks, IsolatedStorageTestCase):
    """Test Amenity and its name field."""

    model_class = Amenity
    defaults = {"name": ""}


class TestPlace(ModelChecks, IsolatedStorageTestCase):
    """Test Place's string, integer, float, and list defaults."""

    model_class = Place
    defaults = {
        "city_id": "", "user_id": "", "name": "", "description": "",
        "number_rooms": 0, "number_bathrooms": 0, "max_guest": 0,
        "price_by_night": 0, "latitude": 0.0, "longitude": 0.0,
        "amenity_ids": [],
    }


class TestReview(ModelChecks, IsolatedStorageTestCase):
    """Test Review and its related user and place IDs."""

    model_class = Review
    defaults = {"place_id": "", "user_id": "", "text": ""}
