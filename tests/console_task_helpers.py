#!/usr/bin/python3
"""Shared test fixtures that keep the real JSON file untouched."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from models.engine.file_storage import FileStorage


class IsolatedStorageTestCase(unittest.TestCase):
    """Run each test with an independent object map and JSON file."""

    def setUp(self):
        """Patch the storage destination and restore it after each test."""
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.file_path = Path(directory.name) / "file.json"
        patches = (
            patch.object(FileStorage, "_FileStorage__objects", {}),
            patch.object(FileStorage, "_FileStorage__file_path",
                         str(self.file_path)),
        )
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
