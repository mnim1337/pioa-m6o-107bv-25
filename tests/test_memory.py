import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.error import (
    TableNotFoundError,
    MissingColumnError,
    UnknownColumnError,
    TableAlreadyExistsError,
)

class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        self.db.create_table("students", ("id", "name"))
        self.assertTrue(self.db._table_exists("students"))

    def test_create_duplicate_table(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))

    def test_insert_record(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "Ivan"})
        records = self.db.select_records("students")
        self.assertEqual(records, [{"id": 1, "name": "Ivan"}])

    def test_insert_missing_column(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", {"id": 1})

    def test_insert_extra_column(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("students", {"id": 1, "name": "Ivan", "age": 20})

    def test_select_with_filter(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "Ivan"})
        self.db.insert_record("students", {"id": 2, "name": "Maria"})
        records = self.db.select_records("students", name="Maria")
        self.assertEqual(records, [{"id": 2, "name": "Maria"}])

    def test_select_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("unknown")
