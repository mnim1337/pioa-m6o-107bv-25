import unittest
from unittest.mock import MagicMock, patch

from src.db.tui import StudentUI
from src.db.backend.error import TableAlreadyExistsError


class TestStudentUIInit(unittest.TestCase):
    def test_init_uses_memory_database_by_default(self):
        with patch("builtins.input", return_value="1"), patch("src.db.tui.MemoryDatabase") as MockMemory, patch(
            "src.db.tui.FileDatabase"
        ) as MockFile:
            mock_db = MockMemory.return_value

            ui = StudentUI()

            MockMemory.assert_called_once()
            MockFile.assert_not_called()
            self.assertIs(ui.database, mock_db)
            mock_db.create_table.assert_called_once_with(
                "students",
                ("student_id", "first_name", "second_name", "age", "sex"),
            )

    def test_init_uses_file_database_when_choice_is_2(self):
        with patch("builtins.input", return_value="2"), patch("src.db.tui.MemoryDatabase") as MockMemory, patch(
            "src.db.tui.FileDatabase"
        ) as MockFile:
            mock_db = MockFile.return_value

            ui = StudentUI()

            MockFile.assert_called_once()
            MockMemory.assert_not_called()
            self.assertIs(ui.database, mock_db)
            mock_db.create_table.assert_called_once_with(
                "students",
                ("student_id", "first_name", "second_name", "age", "sex"),
            )

    def test_init_ignores_table_already_exists_error(self):
        with patch("builtins.input", return_value="1"), patch("src.db.tui.MemoryDatabase") as MockMemory:
            mock_db = MockMemory.return_value
            mock_db.create_table.side_effect = TableAlreadyExistsError("already exists")

            ui = StudentUI()

            self.assertIs(ui.database, mock_db)
            mock_db.create_table.assert_called_once()


class TestStudentUIHelpers(unittest.TestCase):
    def setUp(self):
        self.ui = StudentUI.__new__(StudentUI)
        self.ui.table_name = "students"
        self.ui.columns = ("student_id", "first_name", "second_name", "age", "sex")
        self.ui.database = MagicMock()

    def test_read_int_retries_until_valid(self):
        with patch("builtins.input", side_effect=["abc", "5"]), patch("builtins.print") as mock_print:
            result = self.ui._read_int("id: ")

        self.assertEqual(result, 5)
        mock_print.assert_called_once_with("Ошибка: введите целое число.")

    def test_read_optional_int_returns_none_for_empty_input(self):
        with patch("builtins.input", return_value=""):
            result = self.ui._read_optional_int("age: ")

        self.assertIsNone(result)

    def test_read_optional_int_retries_until_valid(self):
        with patch("builtins.input", side_effect=["qwe", "12"]), patch("builtins.print") as mock_print:
            result = self.ui._read_optional_int("age: ")

        self.assertEqual(result, 12)
        mock_print.assert_called_once_with("Ошибка: введите целое число или оставьте поле пустым.")

    def test_build_filters_ignores_empty_fields(self):
        with patch.object(self.ui, "_read_optional_int", side_effect=[10, None]), patch(
            "builtins.input",
            side_effect=["John", "", "M"],
        ):
            filters = self.ui._build_filters()

        self.assertEqual(
            filters,
            {
                "student_id": 10,
                "first_name": "John",
                "sex": "M",
            },
        )


class TestStudentUIActions(unittest.TestCase):
    def setUp(self):
        self.ui = StudentUI.__new__(StudentUI)
        self.ui.table_name = "students"
        self.ui.columns = ("student_id", "first_name", "second_name", "age", "sex")
        self.ui.database = MagicMock()

    def test_add_student_success(self):
        self.ui.database.select_records.return_value = []

        with patch.object(self.ui, "_read_int", side_effect=[1, 20]), patch(
            "builtins.input",
            side_effect=["Ivan", "Petrov", "M"],
        ), patch("builtins.print") as mock_print:
            self.ui._add_student()

        self.ui.database.select_records.assert_called_once_with("students", student_id=1)
        self.ui.database.insert_record.assert_called_once_with(
            "students",
            {
                "student_id": 1,
                "first_name": "Ivan",
                "second_name": "Petrov",
                "age": 20,
                "sex": "M",
            },
        )
        mock_print.assert_any_call(
            "Запись добавлена: {'student_id': 1, 'first_name': 'Ivan', 'second_name': 'Petrov', 'age': 20, 'sex': 'M'}"
        )

    def test_add_student_negative_age(self):
        self.ui.database.select_records.return_value = []

        with patch.object(self.ui, "_read_int", side_effect=[1, -5]), patch(
            "builtins.input",
            side_effect=["Ivan", "Petrov", "M"],
        ), patch("builtins.print") as mock_print:
            self.ui._add_student()

        self.ui.database.insert_record.assert_not_called()
        self.assertTrue(
            any("Ошибка: Возраст не может быть отрицательным." in str(args[0]) for args, _ in mock_print.call_args_list)
        )

    def test_add_student_duplicate_id(self):
        self.ui.database.select_records.return_value = [{"student_id": 1}]

        with patch.object(self.ui, "_read_int", side_effect=[1, 20]), patch(
            "builtins.input",
            side_effect=["Ivan", "Petrov", "M"],
        ), patch("builtins.print") as mock_print:
            self.ui._add_student()

        self.ui.database.insert_record.assert_not_called()
        self.assertTrue(
            any("Ошибка: Запись с id=1 уже существует." in str(args[0]) for args, _ in mock_print.call_args_list)
        )

    def test_show_all_students(self):
        self.ui.database.select_records.return_value = [
            {"student_id": 1, "first_name": "Ivan"},
            {"student_id": 2, "first_name": "Anna"},
        ]

        with patch("builtins.print") as mock_print:
            self.ui._show_all_students()

        self.ui.database.select_records.assert_called_once_with("students")
        mock_print.assert_any_call("\nСписок записей")
        mock_print.assert_any_call({"student_id": 1, "first_name": "Ivan"})
        mock_print.assert_any_call({"student_id": 2, "first_name": "Anna"})

    def test_find_students_by_filter(self):
        self.ui.database.select_records.return_value = [{"student_id": 1}]

        with patch.object(self.ui, "_build_filters", return_value={"student_id": 1}), patch(
            "builtins.print"
        ) as mock_print:
            self.ui._find_students_by_filter()

        self.ui.database.select_records.assert_called_once_with("students", student_id=1)
        mock_print.assert_any_call("\nПоиск по фильтру (Enter = пропустить поле)")
        mock_print.assert_any_call({"student_id": 1})

    def test_update_student_without_filters(self):
        with patch.object(self.ui, "_build_filters", return_value={}), patch("builtins.print") as mock_print:
            self.ui._update_student()

        self.ui.database.update_records.assert_not_called()
        mock_print.assert_any_call("Ошибка: необходимо указать хотя бы один критерий поиска.")

    def test_update_student_success(self):
        self.ui.database.update_records.return_value = [{"student_id": 1, "first_name": "Updated"}]

        with patch.object(self.ui, "_build_filters", return_value={"student_id": 1}), patch(
            "builtins.input",
            side_effect=["Updated", "", "M"],
        ), patch.object(self.ui, "_read_optional_int", return_value=21), patch("builtins.print") as mock_print:
            self.ui._update_student()

        self.ui.database.update_records.assert_called_once_with(
            "students",
            {"student_id": 1},
            {"first_name": "Updated", "age": 21, "sex": "M"},
        )
        mock_print.assert_any_call({"student_id": 1, "first_name": "Updated"})

    def test_delete_student_cancelled(self):
        with patch.object(self.ui, "_build_filters", return_value={"student_id": 1}), patch(
            "builtins.input",
            return_value="n",
        ), patch("builtins.print") as mock_print:
            self.ui._delete_student()

        self.ui.database.delete_records.assert_not_called()
        mock_print.assert_any_call("Удаление отменено.")

    def test_delete_student_success(self):
        self.ui.database.delete_records.return_value = [{"student_id": 1}]

        with patch.object(self.ui, "_build_filters", return_value={"student_id": 1}), patch(
            "builtins.input",
            return_value="y",
        ), patch("builtins.print") as mock_print:
            self.ui._delete_student()

        self.ui.database.delete_records.assert_called_once_with("students", {"student_id": 1})
        mock_print.assert_any_call("\nУдалённые записи:")
        mock_print.assert_any_call({"student_id": 1})


class TestStudentUIRun(unittest.TestCase):
    def test_run_exits_on_zero(self):
        ui = StudentUI.__new__(StudentUI)
        ui._print_menu = MagicMock()
        ui._add_student = MagicMock()
        ui._show_all_students = MagicMock()
        ui._find_students_by_filter = MagicMock()
        ui._update_student = MagicMock()
        ui._delete_student = MagicMock()

        with patch("builtins.input", side_effect=["0"]), patch("builtins.print") as mock_print:
            ui.run()

        mock_print.assert_any_call("Выход из программы.")
        ui._print_menu.assert_called_once()
        ui._add_student.assert_not_called()

    def test_run_handles_unknown_command(self):
        ui = StudentUI.__new__(StudentUI)
        ui._print_menu = MagicMock()
        ui._add_student = MagicMock()
        ui._show_all_students = MagicMock()
        ui._find_students_by_filter = MagicMock()
        ui._update_student = MagicMock()
        ui._delete_student = MagicMock()

        with patch("builtins.input", side_effect=["9", "0"]), patch("builtins.print") as mock_print:
            ui.run()

        mock_print.assert_any_call("Неизвестная команда. Повторите ввод.")
