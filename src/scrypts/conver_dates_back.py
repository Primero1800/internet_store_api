from datetime import datetime
from typing import Dict, Any


def convert_dates_operate(data: Dict[str, Any]) -> None:
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    convert_dates_operate(item)
        elif isinstance(value, dict):
            convert_dates_operate(value)
        elif isinstance(value, str):
            try:
                data[key] = datetime.fromisoformat(value)
            except ValueError:
                pass


def convert_dates(data: Dict[str, Any]) -> Dict[str, Any]:
    convert_dates_operate(data)
    return data
