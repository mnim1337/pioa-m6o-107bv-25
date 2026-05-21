# tests/test_ui.py

import unittest
from unittest.mock import patch
from io import StringIO

from src.db.tui import StudentUI
from src.db.tui import t


class TestStudentUI(unittest.TestCase):

    def setUp(self):
        self.ui = StudentUI()

        # очищаем память перед каждым тестом
        t._student = []

    # -------------------------------------------------
    # Тест добавления записи
    # -------------------------------------------------
    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_add_student(self, mock_stdout, mock_input):

        mock_input.side_effect = [
            "1",        # id
            "John",     # first_name
            "Doe",      # second_name
            "20",       # age
            "M",        # sex
        ]

        self.ui._add_student()

        records = t.select_record()

        expected = [(1, "John", "Doe", 20, "M")]

        self.assertEqual(records, expected)

        output = mock_stdout.getvalue()
        self.assertIn("Запись добавлена", output)

    # -------------------------------------------------
    # Тест отображения всех записей
    # -------------------------------------------------
    @patch("sys.stdout", new_callable=StringIO)
    def test_show_all_students(self, mock_stdout):

        test_data = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]

        for record in test_data:
            t.create_record(*record)

        self.ui._show_all_students()

        output = mock_stdout.getvalue()

        self.assertIn("John", output)
        self.assertIn("Jane", output)

    # -------------------------------------------------
    # Тест поиска по фильтру
    # -------------------------------------------------
    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_find_students_by_filter(self, mock_stdout, mock_input):

        test_data = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]

        for record in test_data:
            t.create_record(*record)

        mock_input.side_effect = [
            "2",        # id
            "",         # first_name
            "",         # second_name
            "",         # age
            "",         # sex
        ]

        self.ui._find_students_by_filter()

        output = mock_stdout.getvalue()

        self.assertIn("Jane", output)
        self.assertNotIn("John", output)

    # -------------------------------------------------
    # Тест обновления записи
    # -------------------------------------------------
    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_update_student(self, mock_stdout, mock_input):

        t.create_record(1, "John", "Doe", 20, "M")

        mock_input.side_effect = [
            "1",        # id
            "",         # first_name
            "",         # second_name
            "",         # age
            "",         # sex

            "Johnny",   # new_first_name
            "",         # new_second_name
            "",         # new_age
            "",         # new_sex
        ]

        self.ui._update_student()

        records = t.select_record(student_id=1)

        expected = [(1, "Johnny", "Doe", 20, "M")]

        self.assertEqual(records, expected)

    # -------------------------------------------------
    # Тест удаления записи
    # -------------------------------------------------
    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_delete_student(self, mock_stdout, mock_input):

        t.create_record(1, "John", "Doe", 20, "M")

        mock_input.side_effect = [
            "1",    # id
            "",     # first_name
            "",     # second_name
            "",     # age
            "",     # sex
            "y",    # подтверждение
        ]

        self.ui._delete_student()

        records = t.select_record()

        self.assertEqual(records, [])

        output = mock_stdout.getvalue()
        self.assertIn("Удалённые записи", output)

    # -------------------------------------------------
    # Тест отмены удаления
    # -------------------------------------------------
    @patch("builtins.input")
    @patch("sys.stdout", new_callable=StringIO)
    def test_delete_student_cancel(self, mock_stdout, mock_input):

        t.create_record(1, "John", "Doe", 20, "M")

        mock_input.side_effect = [
            "1",    # id
            "",     # first_name
            "",     # second_name
            "",     # age
            "",     # sex
            "n",    # отмена
        ]

        self.ui._delete_student()

        records = t.select_record()

        expected = [(1, "John", "Doe", 20, "M")]

        self.assertEqual(records, expected)

        output = mock_stdout.getvalue()
        self.assertIn("Удаление отменено", output)
