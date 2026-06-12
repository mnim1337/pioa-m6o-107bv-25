# src/db/backend/file.py
import json
import os
from pathlib import Path

from .database import Database
from .error import InvalidStorageDataError, TableNotFoundError
from .table import Table


class FileDatabase(Database):
    """База данных, которая хранит таблицы в JSON-файлах."""

    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                "Файл таблицы содержит некорректный JSON."
            ) from error
        except OSError as error:
            raise InvalidStorageDataError(
                f"Ошибка чтения файла: {error}"
            ) from error

        return self._deserialize_table(data)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)

        with table_path.open("w", encoding="utf-8") as file:
            json.dump(
                self._serialize_table(table),
                file,
                ensure_ascii=False,
                indent=2,
            )

    def _get_table_path(self, table_name: str) -> Path:
        safe_name = os.path.basename(table_name)
        if safe_name != table_name or not safe_name:
            raise InvalidStorageDataError(f"Недопустимое имя таблицы: {table_name}")
        return self.directory / f"{safe_name}.json"
    
    def _serialize_table(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
        }

    def _deserialize_table(self, data: dict) -> Table:
        if "columns" not in data or "records" not in data:
            raise InvalidStorageDataError(
                "Файл таблицы имеет некорректную структуру."
            )

        columns_data = data["columns"]
        records_data = data["records"]

        # Валидация типов
        if not isinstance(columns_data, list):
            raise InvalidStorageDataError("Поле 'columns' должно быть списком.")
        if not all(isinstance(col, str) for col in columns_data):
            raise InvalidStorageDataError("Имена колонок должны быть строками.")
        if not isinstance(records_data, list):
            raise InvalidStorageDataError("Поле 'records' должно быть списком.")

        columns = tuple(columns_data)
        # Каждая запись должна быть словарём
        validated_records = []
        for record in records_data:
            if not isinstance(record, dict):
                raise InvalidStorageDataError("Каждая запись должна быть словарём.")
            validated_records.append(record)

        return Table(columns, validated_records)
