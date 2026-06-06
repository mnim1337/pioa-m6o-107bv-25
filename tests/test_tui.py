# tests/test_ui.py

import unittest
from unittest.mock import patch

from src.db.tui import StudentUI, t


class TestStudentUI(unittest.TestCase):

    def setUp(self):
        self.ui = StudentUI()

        # очищаем таблицу перед каждым тестом
        try:
            t.delete_record(student_id=None)
        except Exception:
            pass
    
    @patch("builtins.print")
    def test_print_menu(self, mock_print):
        self.ui._print_menu()

        mock_print.assert_any_call("\n=== База студентов ===")
        mock_print.assert_any_call("1. Добавить запись")
        mock_print.assert_any_call("2. Показать все записи")
        mock_print.assert_any_call("3. Найти записи по фильтру")
        mock_print.assert_any_call("4. Обновить запись")
        mock_print.assert_any_call("5. Удалить запись")
        mock_print.assert_any_call("0. Выход")

        self.assertEqual(mock_print.call_count, 7)

    @patch("builtins.input", side_effect=[
        "1",         # id
        "John",      # first_name
        "Doe",       # second_name
        "20",        # age
        "M"          # sex
    ])
    def test_add_student(self, mock_input):
        self.ui._add_student()

        result = t.select_record(student_id=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (1, "John", "Doe", 20, "M"))

    @patch("builtins.input", side_effect=[
        "1",         # id фильтр
        "",          # first_name
        "",          # second_name
        "",          # age
        ""           # sex
    ])
    def test_find_student_by_id(self, mock_input):
        t.create_record(1, "John", "Doe", 20, "M")

        with patch.object(self.ui, "_print_records") as mock_print:
            self.ui._find_students_by_filter()

            mock_print.assert_called_once_with(
                [(1, "John", "Doe", 20, "M")]
            )

    @patch("builtins.input", side_effect=[
        "1",         # id
        "",          # first_name
        "",          # second_name
        "",          # age
        "",          # sex

        "Jack",      # new_first_name
        "",          # new_second_name
        "",          # new_age
        ""           # new_sex
    ])
    def test_update_student(self, mock_input):
        t.create_record(1, "John", "Doe", 20, "M")

        self.ui._update_student()

        result = t.select_record(student_id=1)

        self.assertEqual(
            result[0],
            (1, "Jack", "Doe", 20, "M")
        )

    @patch("builtins.input", side_effect=[
        "1",     # id
        "",      # first_name
        "",      # second_name
        "",      # age
        "",      # sex
        "y"      # подтверждение
    ])
    def test_delete_student(self, mock_input):
        t.create_record(1, "John", "Doe", 20, "M")

        self.ui._delete_student()

        result = t.select_record(student_id=1)

        self.assertEqual(result, [])

    @patch("builtins.input", side_effect=[
        "", "", "", "", ""
    ])
    @patch("builtins.print")
    def test_delete_without_filters(self, mock_print, mock_input):
        self.ui._delete_student()

        mock_print.assert_any_call(
            "Ошибка: Необходимо указать хотя бы один критерий поиска"
        )

    @patch("builtins.input", side_effect=[
        "", "", "", "", "",

        "Jack", "", "", ""
    ])
    @patch("builtins.print")
    def test_update_without_filters(self, mock_print, mock_input):
        self.ui._update_student()

        mock_print.assert_any_call(
            "Ошибка: Необходимо указать хотя бы один критерий поиска."
        )

    @patch("builtins.input", side_effect=["0"])
    @patch("builtins.print")
    def test_run_exit(self, mock_print, mock_input):
        self.ui.run()

        mock_print.assert_any_call("Выход из программы.")

    @patch.object(StudentUI, "_add_student")
    @patch("builtins.input", side_effect=["1", "0"])
    def test_run_add_student(self, mock_input, mock_add_student):
        self.ui.run()

        mock_add_student.assert_called_once()

    @patch.object(StudentUI, "_show_all_students")
    @patch("builtins.input", side_effect=["2", "0"])
    def test_run_show_all_students(self, mock_input, mock_show):
        self.ui.run()

        mock_show.assert_called_once()

    @patch.object(StudentUI, "_find_students_by_filter")
    @patch("builtins.input", side_effect=["3", "0"])
    def test_run_find_students(self, mock_input, mock_find):
        self.ui.run()

        mock_find.assert_called_once()

    @patch.object(StudentUI, "_update_student")
    @patch("builtins.input", side_effect=["4", "0"])
    def test_run_update_student(self, mock_input, mock_update):
        self.ui.run()

        mock_update.assert_called_once()
    
    @patch.object(StudentUI, "_delete_student")
    @patch("builtins.input", side_effect=["5", "0"])
    def test_run_delete_student(self, mock_input, mock_delete):
        self.ui.run()

        mock_delete.assert_called_once()
    
    @patch("builtins.input", side_effect=["6", "0"])
    @patch("builtins.print")
    def test_run_unknown_command(self, mock_print, mock_input):
        self.ui.run()

        mock_print.assert_any_call(
            "Неизвестная команда. Повторите ввод."
        )
    