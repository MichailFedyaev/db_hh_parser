import json
from typing import Any


def read_json(json_file: str) -> Any:
    """Извлекает данные из JSON-файла и возвращает список словарей с соответствующей информацией."""

    with open(json_file, "r", encoding="UTF-8") as file:
        return json.load(file)