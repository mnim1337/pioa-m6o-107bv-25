import json
import tempfile
import unittest
from pathlib import Path

from src.db.backend.error import (
    InvalidStorageDataError,
    MissingColumnError,
    TableAlreadyExistsError,
    TableNotFoundError,
    UnknownColumnError,
)
from src.db.backend.file import FileDatabase


class TestFileDatabase(unittest.TestCase):
    def test_create_table_creates_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))

            table_path = Path(directory) / "students.json"
            self.assertTrue(table_path.exists())

            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            self.assertEqual(data, {"columns": ["student_id", "name"], "records": []})

    def test_create_table_twice_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))

            with self.assertRaises(TableAlreadyExistsError):
                db.create_table("students", ("student_id", "name"))

    def test_insert_record_saves_data_between_instances(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first_db = FileDatabase(directory)
            first_db.create_table("students", ("student_id", "name"))
            first_db.insert_record("students", {"student_id": 1, "name": "Иван"})

            second_db = FileDatabase(directory)
            records = second_db.select_records("students")

            self.assertEqual(records, [{"student_id": 1, "name": "Иван"}])

    def test_insert_record_with_missing_column_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))

            with self.assertRaises(MissingColumnError):
                db.insert_record("students", {"student_id": 1})

    def test_insert_record_with_unknown_column_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))

            with self.assertRaises(UnknownColumnError):
                db.insert_record(
                    "students",
                    {"student_id": 1, "name": "Иван", "age": 20},
                )

    def test_select_with_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})
            db.insert_record("students", {"student_id": 2, "name": "Мария"})

            records = db.select_records("students", name="Мария")

            self.assertEqual(records, [{"student_id": 2, "name": "Мария"}])

    def test_select_with_unknown_filter_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})

            with self.assertRaises(UnknownColumnError):
                db.select_records("students", age=20)

    def test_update_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})

            updated = db.update_records(
                "students",
                filters={"student_id": 1},
                updates={"name": "Иван Петров"},
            )

            self.assertEqual(updated, [{"student_id": 1, "name": "Иван Петров"}])
            self.assertEqual(
                db.select_records("students"),
                [{"student_id": 1, "name": "Иван Петров"}],
            )

    def test_update_with_unknown_filter_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))

            with self.assertRaises(UnknownColumnError):
                db.update_records(
                    "students",
                    filters={"age": 20},
                    updates={"name": "Иван"},
                )

    def test_update_with_unknown_column_in_updates_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})

            with self.assertRaises(UnknownColumnError):
                db.update_records(
                    "students",
                    filters={"student_id": 1},
                    updates={"age": 20},
                )

    def test_delete_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})
            db.insert_record("students", {"student_id": 2, "name": "Мария"})

            deleted = db.delete_records("students", filters={"student_id": 1})

            self.assertEqual(deleted, [{"student_id": 1, "name": "Иван"}])
            self.assertEqual(
                db.select_records("students"),
                [{"student_id": 2, "name": "Мария"}],
            )

    def test_delete_with_unknown_filter_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)
            db.create_table("students", ("student_id", "name"))

            with self.assertRaises(UnknownColumnError):
                db.delete_records("students", filters={"age": 20})

    def test_select_from_missing_table_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = FileDatabase(directory)

            with self.assertRaises(TableNotFoundError):
                db.select_records("students")

    def test_invalid_json_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table_path = Path(directory) / "students.json"
            table_path.write_text("{invalid json}", encoding="utf-8")

            db = FileDatabase(directory)

            with self.assertRaises(InvalidStorageDataError):
                db.select_records("students")

    def test_invalid_file_structure_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table_path = Path(directory) / "students.json"
            table_path.write_text(
                json.dumps({"wrong_key": []}, ensure_ascii=False),
                encoding="utf-8",
            )

            db = FileDatabase(directory)

            with self.assertRaises(InvalidStorageDataError):
                db.select_records("students")
