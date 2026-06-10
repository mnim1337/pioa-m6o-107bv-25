from typing import Any

from .error import MissingColumnError, UnknownColumnError


class Table:
    """Таблица с фиксированным набором колонок."""

    def __init__(self, columns: tuple[str, ...], records: list[dict[str, Any]] | None = None) -> None:
        self.columns = columns
        self.records: list[dict[str, Any]] = []

        if records is not None:
            for record in records:
                self.insert_record(record)

    def insert_record(self, record: dict[str, Any]) -> None:
        """Добавляет запись, если она соответствует схеме таблицы."""
        # Проверяем, что все обязательные поля присутствуют
        missing_columns = [column for column in self.columns if column not in record]
        if missing_columns:
            raise MissingColumnError(
                f"Отсутствует поле '{missing_columns[0]}' в записи."
            )

        # Проверяем, что нет лишних полей
        extra_columns = [column for column in record if column not in self.columns]
        if extra_columns:
            raise UnknownColumnError(
                f"Поле '{extra_columns[0]}' не определено в структуре таблицы."
            )

        self.records.append(record.copy())

    def select_records(self, **filters: Any) -> list[dict[str, Any]]:
        """Возвращает записи, удовлетворяющие всем переданным фильтрам."""
        # Проверяем, что поля фильтров существуют
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        # Если фильтров нет, возвращаем все записи
        if not filters:
            return [record.copy() for record in self.records]

        # Фильтруем записи
        result: list[dict[str, Any]] = []
        for record in self.records:
            if all(record.get(key) == value for key, value in filters.items()):
                result.append(record.copy())

        return result

    def update_records(self, filters: dict[str, Any], updates: dict[str, Any]) -> list[dict[str, Any]]:
        """Обновляет записи, соответствующие фильтрам."""
        # Проверяем поля фильтров
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        # Проверяем поля обновлений
        unknown_updates = [key for key in updates if key not in self.columns]
        if unknown_updates:
            raise UnknownColumnError(
                f"Поле '{unknown_updates[0]}' не определено в структуре таблицы."
            )

        updated_records = []
        for i, record in enumerate(self.records):
            # Проверяем, соответствует ли запись фильтрам
            if all(record.get(key) == value for key, value in filters.items()):
                # Обновляем запись
                for key, value in updates.items():
                    self.records[i][key] = value
                updated_records.append(self.records[i].copy())

        return updated_records

    def delete_records(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Удаляет записи, соответствующие фильтрам."""
        # Проверяем поля фильтров
        unknown_filters = [key for key in filters if key not in self.columns]
        if unknown_filters:
            raise UnknownColumnError(
                f"Поле '{unknown_filters[0]}' не определено в структуре таблицы."
            )

        deleted_records = []
        i = 0
        while i < len(self.records):
            record = self.records[i]
            if all(record.get(key) == value for key, value in filters.items()):
                deleted_records.append(self.records.pop(i).copy())
            else:
                i += 1

        return deleted_records
