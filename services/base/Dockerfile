FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

# get poetry
RUN pip install poetry gunicorn

WORKDIR /app/

COPY src/pyproject.toml .
COPY src/poetry.lock .

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY src/pytest.ini .
COPY src/setup.cfg .
