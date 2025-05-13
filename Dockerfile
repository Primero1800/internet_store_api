FROM python:3.12

RUN apt-get update -y && apt-get upgrade -y && pip install --no-cache-dir poetry

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./alembic.ini ./
COPY ./alembic ./alembic
COPY ./celery_home ./celery_home
COPY ./media ./media
COPY ./src ./src
COPY ./static ./static

RUN poetry config virtualenvs.create true && poetry install --no-root --no-interaction

EXPOSE 8000 5555

CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload" ]
