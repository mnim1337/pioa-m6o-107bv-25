# tests/test_memory.py
import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.error import InvalidAgeError, DuplicateIDError


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.student_table = StudentTable()
        self.assertIsInstance(self.student_table, StudentTable)

    def test_create_record(self):
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
            (11, "Jack", "Thomas", 18, "M"),
            (12, "Kathy", "Jackson", 23, "F"),
        ]

        for test_data in cases:
            # Используем subTest для изоляции каждого тестового случая и улучшения читаемости результатов тестирования.
            # Это позволяет нам видеть, какой именно набор данных вызвал ошибку, если тест не пройдет.
            with self.subTest(test_data=test_data):
                record = self.student_table.create_record(*test_data)
                self.assertEqual(record, test_data)

    def test_create_record_negative_age(self):
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
            (3, "Alice", "Johnson", -10, "F"),
        ]
        error_message = "Возраст не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidAgeError) as context:
                    self.student_table.create_record(*test_data)

        self.assertEqual(str(context.exception), error_message)

    def test_create_record_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.student_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

    def test_select_record(self):
        # Подготовка тестовых данных для проверки функции select_record.
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        # Формирование тестовых случаев для функции select_record.
        # Каждый случай включает в себя описание, набор фильтров и ожидаемый результат.
        cases = [
            {
                "name": "Выбор без фильтров",
                "filters": {},
                "expected": test_datas,
            },
            {
                "name": "Фильтр по ID",
                "filters": {"student_id": 1},
                "expected": [test_datas[0]],
            },
            {
                "name": "Фильтр по имени",
                "filters": {"first_name": "Jane"},
                "expected": [test_datas[1]],
            },
            {
                "name": "Фильтр по фамилии",
                "filters": {"second_name": "Johnson"},
                "expected": [test_datas[2]],
            },
            {
                "name": "Фильтр по возрасту",
                "filters": {"age": 20},
                "expected": [test_datas[0], test_datas[6]],
            },
            {
                "name": "Фильтр по полу",
                "filters": {"sex": "F"},
                "expected": [
                    test_datas[1],
                    test_datas[2],
                    test_datas[5],
                    test_datas[7],
                    test_datas[9],
                ],
            },
        ]

        for case in cases:
            with self.subTest(
                case=case["name"], filters=case["filters"], expected=case["expected"]
            ):
                records = self.student_table.select_record(**case["filters"])
                self.assertEqual(records, case["expected"])

    def test_update_record_id(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 21, "F"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        with self.subTest(name="Обновление одного студента по ID"):
            updated = self.student_table.update_record(student_id=1, new_first_name="Johnny", new_age=21)
            self.assertEqual(updated, [(1, "Johnny", "Doe", 21, "M")])
            
            # Проверяем, что изменения применились в базе
            self.assertEqual(self.student_table.select_record(student_id=1), [(1, "Johnny", "Doe", 21, "M")])

    def test_update_record_firstn(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 21, "F"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
 
        with self.subTest(name="Обновление одного студента по имени"):
            updated = self.student_table.update_record(first_name="John", new_age=28)
            self.assertEqual(updated, [(1, "John", "Doe", 28, "M")])
            
            # Проверяем, что изменения применились в базе
            self.assertEqual(self.student_table.select_record(first_name="John"), [(1, "John", "Doe", 28, "M")])

    def test_update_record_secondn(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 21, "F"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
 
        with self.subTest(name="Обновление одного студента по фамилии"):
            updated = self.student_table.update_record(second_name="Smith", new_first_name="The", new_sex="M")
            self.assertEqual(updated, [(2, "The", "Smith", 22, "M")])
            
            # Проверяем, что изменения применились в базе
            self.assertEqual(self.student_table.select_record(second_name="Smith"), [(2, "The", "Smith", 22, "M")])

    def test_update_record_age(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 21, "F"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
 
        with self.subTest(name="Обновление одного студента по имени"):
            updated = self.student_table.update_record(age=21, new_sex="M")
            self.assertEqual(updated, [(3, "Alice", "Johnson", 21, "M")])
            
            # Проверяем, что изменения применились в базе
            self.assertEqual(self.student_table.select_record(age=21), [(3, "Alice", "Johnson", 21, "M")])
    
    def test_update_record_sex(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
 
        with self.subTest(name="Обновление одного студента по полу"):
            updated = self.student_table.update_record(sex="M", new_age=28)
            self.assertEqual(updated, [(1, "John", "Doe", 28, "M")])
            
            # Проверяем, что изменения применились в базе
            self.assertEqual(self.student_table.select_record(sex="M"), [(1, "John", "Doe", 28, "M")])

    def test_update_record_negative_age(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        error_message = "Возраст не может быть отрицательным."

        with self.assertRaises(InvalidAgeError) as context:
            self.student_table.update_record(student_id=1, new_age=-5)
        
        self.assertEqual(str(context.exception), error_message)
        
    
    def test_delete_record(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Ivy", "Anderson", 23, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        # 1. Удаляем по ID
        res1 = self.student_table.delete_record(student_id=1)
        self.assertEqual(res1, [(1, "John", "Doe", 20, "M")])

        #2. Удаляем по имени
        res2 = self.student_table.delete_record(first_name="Jane")
        self.assertEqual(res2, [(2, "Jane", "Smith", 22, "F")])

        # 3. Удаляем по фамилии
        res3 = self.student_table.delete_record(second_name="Johnson")
        self.assertEqual(res3, [(3, "Alice", "Johnson", 19, "F")])

        # 4. Удаляем по возрасту
        res4 = self.student_table.delete_record(age=21)
        self.assertEqual(res4, [(4, "Bob", "Brown", 21, "M")])

        # 4. Удаляем по полу
        res5 = self.student_table.delete_record(sex="F")
        self.assertEqual(res5, [(6, "Ivy", "Anderson", 23, "F")])

        expected_remaining = [
        (5, "Charlie", "Davis", 18, "M")
        ]

        records = self.student_table.select_record()

        self.assertEqual(records, expected_remaining)
