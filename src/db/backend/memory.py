from .error import DuplicateIDError, InvalidAgeError

type StudentRecord = tuple[int, str, str, int, str]


class StudentTable:
    def __init__(self) -> None:
        self._student: list[StudentRecord] = []

    def create_record(
        self,
        student_id: int,
        first_name: str,
        second_name: str,
        age: int,
        sex: str,
    ) -> StudentRecord:

        if age < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным.")

        if any(record[0] == student_id for record in self._student):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._student.append(new_record)
        return new_record

    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:

        if (
            student_id is None
            and first_name is None
            and second_name is None
            and age is None
            and sex is None
        ):
            return self._student.copy()

        result: list[StudentRecord] = []

        for record in self._student:
            if student_id is not None and record[0] != student_id:
                continue

            if first_name is not None and record[1] != first_name:
                continue

            if second_name is not None and record[2] != second_name:
                continue

            if age is not None and record[3] != age:
                continue

            if sex is not None and record[4] != sex:
                continue

            result.append(record)

        return result

    def update_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
        new_first_name: str | None = None,
        new_second_name: str | None = None,
        new_age: int | None = None,
        new_sex: str | None = None,
    ) -> list[StudentRecord]:
        """
        Обновляет записи, подходящие под фильтр.
        Возвращает список обновлённых записей.
        """
    
        updated_records = []

        if new_age is not None and new_age < 0:
            raise InvalidAgeError("Возраст не может быть отрицательным.")
    
        for i, record in enumerate(self._student):

            if student_id is not None and record[0] != student_id:
                continue

            if first_name is not None and record[1] != first_name:
                continue

            if second_name is not None and record[2] != second_name:
                continue

            if age is not None and record[3] != age:
                continue

            if sex is not None and record[4] != sex:
                continue

            # Новые значения (если None → оставить старое)
            new_record = (
                record[0],
                new_first_name.strip() if new_first_name is not None else record[1],
                new_second_name.strip() if new_second_name is not None else record[2],
                new_age if new_age is not None else record[3],
                new_sex.strip() if new_sex is not None else record[4],
            )
            
            # Замена записи
            self._student[i] = new_record
            updated_records.append(new_record)

        return updated_records

    def delete_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
    ) -> list[StudentRecord]:
        """
        Удаляет записи по фильтру.
        Возвращает список удалённых записей.
        """
        
        to_delete = []

        for record in self._student:
            if student_id is not None and record[0] != student_id:
                continue

            if first_name is not None and record[1] != first_name:
                continue

            if second_name is not None and record[2] != second_name:
                continue

            if age is not None and record[3] != age:
                continue

            if sex is not None and record[4] != sex:
                continue

            to_delete.append(record)

        # Удаляем найденные записи
        for record in to_delete:
            self._student.remove(record)

        return to_delete
