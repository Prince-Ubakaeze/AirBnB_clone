#!/usr/bin/python3
"""Common attributes and persistence methods for every model."""

from datetime import datetime
from uuid import uuid4

import models


class BaseModel:
    """Provide identity, timestamps, and JSON-compatible serialization."""

    def __init__(self, *args, **kwargs):
        """Create a new instance or reconstruct one from a dictionary."""
        if kwargs:
            for key, value in kwargs.items():
                if key == "__class__":
                    continue
                if key in ("created_at", "updated_at"):
                    value = datetime.fromisoformat(value)
                setattr(self, key, value)
        else:
            self.id = str(uuid4())
            self.created_at = datetime.now()
            self.updated_at = self.created_at
            models.storage.new(self)

    def __str__(self):
        """Return the class, ID, and instance attribute dictionary."""
        return "[{}] ({}) {}".format(
            type(self).__name__, self.id, self.__dict__)

    def save(self):
        """Update the modification time and persist all instances."""
        self.updated_at = datetime.now()
        models.storage.save()

    def to_dict(self):
        """Return a new dictionary containing JSON-compatible values."""
        result = self.__dict__.copy()
        result["__class__"] = type(self).__name__
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        return result
