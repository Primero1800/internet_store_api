FROM python:3.12

RUN apt-get update -y && apt-get upgrade -y

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY ./pyproject.toml /poetry.lock ./

RUN poetry config virtualenvs.create true && poetry install --no-root --no-interaction

COPY ./alembic ./alembic
COPY ./celery_home ./celery_home
COPY ./media ./media
COPY ./src ./src
COPY ./static ./static
COPY ./alembic.ini ./alembic.ini

CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload" ]
