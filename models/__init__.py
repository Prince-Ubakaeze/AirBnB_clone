#!/usr/bin/python3
"""Create the shared storage engine and reload saved instances."""

from models.engine.file_storage import FileStorage

storage = FileStorage()
storage.reload()
