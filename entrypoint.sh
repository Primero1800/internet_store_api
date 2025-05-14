#!/bin/sh

# Установка PYTHONPATH для правильного поиска модулей
export PYTHONPATH=/app/src

# Выполняем миграции
poetry run alembic upgrade head

# Создаем суперпользователя
python src/scripts/create_default_superuser.py

# Запускаем uvicorn
poetry run uvicorn src.main:app --host 0.0.0.0 --reload