#!/usr/bin/python3
"""Serialize and deserialize model instances using a JSON file."""

import json

from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


CLASSES = {
    "BaseModel": BaseModel,
    "User": User,
    "State": State,
    "City": City,
    "Amenity": Amenity,
    "Place": Place,
    "Review": Review,
}


class FileStorage:
    """Persist instances under keys of the form <class name>.<id>."""

    __file_path = "file.json"
    __objects = {}

    def all(self):
        """Return the live dictionary of stored instances."""
        return self.__objects

    def new(self, obj):
        """Register an instance using its class and ID."""
        key = "{}.{}".format(type(obj).__name__, obj.id)
        self.__objects[key] = obj

    def save(self):
        """Write all registered instances to the JSON file."""
        serialized = {key: obj.to_dict()
                      for key, obj in self.__objects.items()}
        with open(self.__file_path, "w", encoding="utf-8") as file:
            json.dump(serialized, file)

    def reload(self):
        """Load saved instances, ignoring a missing storage file."""
        try:
            with open(self.__file_path, encoding="utf-8") as file:
                serialized = json.load(file)
        except FileNotFoundError:
            return
        restored = {}
        for key, attributes in serialized.items():
            model_class = CLASSES[attributes["__class__"]]
            restored[key] = model_class(**attributes)
        self.__objects.update(restored)
