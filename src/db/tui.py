# src/db/tui.py
from src.db.backend.file import FileDatabase
from src.db.backend.memory import MemoryDatabase
from src.db.backend.error import TableAlreadyExistsError, InvalidAgeError, DuplicateIDError, MissingColumnError, UnknownColumnError


class StudentUI:
    def __init__(self) -> None:
        print("Выберите тип базы данных:")
        print("1. In-memory")
        print("2. File database")

        choice = input("Введите номер: ").strip()
        if choice == "2":
            self.database = FileDatabase()
        else:
            self.database = MemoryDatabase()

        self.table_name = "students"
        self.columns = ("student_id", "first_name", "second_name", "age", "sex")

        try:
            self.database.create_table(self.table_name, self.columns)
        except TableAlreadyExistsError:
            pass

    def _print_menu(self) -> None:
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _print_records(self, records: list[dict]) -> None:
        if not records:
            print("Записи не найдены.")
            return

        for record in records:
            print(record)

    def _build_filters(self) -> dict:
        student_id = self._read_optional_int("id: ")
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        return filters

    def _add_student(self) -> None:
        """Добавление студента."""
        print("\nДобавление записи")

        try:
            student_id = self._read_int("id: ")
            first_name = input("first_name: ").strip()
            second_name = input("second_name: ").strip()
            age = self._read_int("age: ")
            sex = input("sex: ").strip()

            # Валидация
            if age < 0:
                raise InvalidAgeError("Возраст не может быть отрицательным.")

            # Проверка на дубликат ID
            existing = self.database.select_records(
                self.table_name,
                student_id=student_id
            )
            if existing:
                raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

            record = {
                "student_id": student_id,
                "first_name": first_name,
                "second_name": second_name,
                "age": age,
                "sex": sex,
            }
            self.database.insert_record(self.table_name, record)
            print(f"Запись добавлена: {record}")

        except (DuplicateIDError, InvalidAgeError, MissingColumnError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def _show_all_students(self) -> None:
        print("\nСписок записей")
        records = self.database.select_records(self.table_name)
        self._print_records(records)

    def _find_students_by_filter(self) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")
        filters = self._build_filters()
        records = self.database.select_records(self.table_name, **filters)
        self._print_records(records)

    def _update_student(self) -> None:
        print("\nОбновление записи (Enter = пропустить поле)")
        filters = self._build_filters()

        if not filters:
            print("Ошибка: необходимо указать хотя бы один критерий поиска.")
            return

        print("\nНовые значения (Enter = оставить без изменений)")
        new_first_name = input("new_first_name: ").strip() or None
        new_second_name = input("new_second_name: ").strip() or None
        new_age = self._read_optional_int("new_age: ")
        new_sex = input("new_sex: ").strip() or None

        updates = {}
        if new_first_name is not None:
            updates["first_name"] = new_first_name
        if new_second_name is not None:
            updates["second_name"] = new_second_name
        if new_age is not None:
            updates["age"] = new_age
        if new_sex is not None:
            updates["sex"] = new_sex

        if not updates:
            print("Новые значения не введены.")
            return

        try:
            updated = self.database.update_records(self.table_name, filters, updates)
            self._print_records(updated)
        except ValueError as exc:
            print(f"Ошибка: {exc}")

    def _delete_student(self) -> None:
        print("\nУдаление записи (Enter = пропустить поле)")
        filters = self._build_filters()

        if not filters:
            print("Ошибка: необходимо указать хотя бы один критерий поиска.")
            return

        confirm = input("\nВы уверены, что хотите удалить записи? (y/n): ").strip().lower()
        if confirm != "y":
            print("Удаление отменено.")
            return

        deleted = self.database.delete_records(self.table_name, filters)
        print("\nУдалённые записи:")
        self._print_records(deleted)

    def run(self) -> None:
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self._add_student()
            elif action == "2":
                self._show_all_students()
            elif action == "3":
                self._find_students_by_filter()
            elif action == "4":
                self._update_student()
            elif action == "5":
                self._delete_student()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")
