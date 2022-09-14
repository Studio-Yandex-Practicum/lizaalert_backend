FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

# get poetry
RUN pip install poetry

WORKDIR /app/

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false \ 
    && poetry install --no-interaction --no-ansi

COPY pytest.ini .
COPY setup.cfg .
