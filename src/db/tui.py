# Импортируем из модуля backend.memory функции, реализующие операции
# создания записи и выборки записей из таблицы.
from .backend.memory import StudentTable

t = StudentTable()

class StudentUI:
    def __init__(self) -> None:
        pass

    def _print_menu(self) -> None:
        # Символ \n обозначает перевод строки.
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("0. Выход")

    # Функция чтения целочисленного значения из консоли.
    def _read_int(self, prompt: str) -> int:
        # Используется цикл с повторением до получения корректного ввода.
        while True:
            # Получение строки из консоли с удалением пробельных символов
            # в начале и в конце строки.
            raw = input(prompt).strip()
            try:
                # Преобразование строки к целому числу.
                return int(raw)
            except ValueError:
                # Исключение возникает при невозможности преобразования.
                # Пользователю выводится сообщение об ошибке,
                # после чего ввод повторяется.
                print("Ошибка: введите целое число.")

    # Функция добавления новой записи в базу данных.
    def _add_student(self) -> None:
        print("\nДобавление записи")

        student_id = self._read_int("id: ")
        first_name = input("first_name: ").strip()
        second_name = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()

        try:
            record = t.create_record(student_id, first_name, second_name, age, sex)

            # В случае успешного добавления запись выводится в консоль.
            print(f"Запись добавлена: {record}")

        except ValueError as exc:
            # Обработка ошибок валидации.
            print(f"Ошибка: {exc}")

    # Вспомогательная функция вывода списка записей.
    def _print_records(self, records: list[tuple[int, str, str, int, str]]) -> None:
        # Проверка на пустой список.
        if not records:
            print("Записи не найдены.")
            return

        # Последовательный вывод записей.
        for record in records:
            print(record)

    # Функция вывода всех записей из базы данных.
    def _show_all_students(self) -> None:
        print("\nСписок записей")
        self._print_records(t.select_record())

    # Функция чтения необязательного целочисленного значения.
    # Пустой ввод интерпретируется как отсутствие фильтра (None).
    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()

            if raw == "":
                return None

            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    # Функция поиска записей по заданным фильтрам.
    def _find_students_by_filter(self) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")

        student_id = self._read_optional_int("id: ")

        # Оператор `or` возвращает первое истинное значение.
        # Если строка после strip() пуста, будет возвращено None.
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None

        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        records = t.select_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )

        self._print_records(records)

    def _update_student(self) -> None:
        print("\nОбновление записи (Enter = пропустить поле)")

        student_id = self._read_optional_int("id: ")
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        filters = [student_id, first_name, second_name, age, sex]
        if not any(f is not None for f in filters):
            print("Ошибка: Необходимо указать хотя бы один критерий поиска.")
            return

        print("\nНовые значения (Enter = оставить без изменений)")

        new_first_name = input("new_first_name: ").strip() or None
        new_second_name = input("new_second_name: ").strip() or None
        new_age = self._read_optional_int("new_age: ")
        new_sex = input("new_sex: ").strip() or None

        # Доп. проверка: указаны ли новые данные для обновления
        new_values = [new_first_name, new_second_name, new_age, new_sex]
        if not any(v is not None for v in new_values):
            print("Новые значения не введены. Не обновлю")
            return

        try:
            updated = t.update_record(
                student_id=student_id,
                first_name=first_name,
                second_name=second_name,
                age=age,
                    sex=sex,
                new_first_name=new_first_name,
                new_second_name=new_second_name,
                new_age=new_age,
                new_sex=new_sex,
            )

            self._print_records(updated)

        except ValueError as exc:
            print(f"Ошибка: {exc}")

    def _delete_student(self) -> None:
        print("\nУдаление записи (Enter = пропустить поле)")

        student_id = self._read_optional_int("id: ")
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        filters = [student_id, first_name, second_name, age, sex]
        if not any(f is not None for f in filters):
            print("Ошибка: Необходимо указать хотя бы один критерий поиска")
            return
    
        confirm = input("\nВы уверены, что хотите удалить записи? (y/n): ")
        if confirm != 'y':
            print("Удаление отменено.")
            return

        deleted = t.delete_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )

        print("\nУдалённые записи:")
        self._print_records(deleted)

    def run(self) -> None:
        while True:
            # Отображение меню доступных действий.
            self._print_menu()

            # Получение команды пользователя.
            # Метод strip() удаляет пробельные символы
            # в начале и в конце строки.
            action = input("Выберите действие: ").strip()

            # Диспетчеризация пользовательской команды.
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
                # Завершение работы программы.
                print("Выход из программы.")
                break

            else:
                # Обработка некорректного ввода команды.
                print("Неизвестная команда. Повторите ввод.")
