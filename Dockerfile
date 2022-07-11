FROM python:3.10.5

ENV PYTHONUNBUFFERED=1

EXPOSE 8000/tcp

RUN apt-get -y update --no-install-recommends \
    && apt-get install -yq --no-install-recommends \
    curl \
    git \
    && apt-get autoremove -y \
    && apt-get clean -y

# get poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

ENV APP_HOME=/app/lizaalert

WORKDIR ${APP_HOME}

COPY poetry.lock ${APP_HOME}/poetry.lock
COPY pyproject.toml ${APP_HOME}/pyproject.toml

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY lizaalert-backend ${APP_HOME}
COPY tests/tests/ ${APP_HOME}/tests
